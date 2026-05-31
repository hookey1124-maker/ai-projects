"""maiziAI 图片生成 — 提交 + 轮询 + 自动降级"""
import requests
import time
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MAIZI_API_KEY = "sk-mz-tKqUFcs_REIXU85RUXEpAvNQovkV6r-sOVnD6-qynBcDBWfx"
BASE_URL = "https://www.maizitech.cn/v1"
POLL_INTERVAL = 2
MAX_POLL = 150  # 150 * 2s = 5min，降级阈值

MODEL_IDS = {
    "fast": "nano-banana-fast",
    "quality": "gpt-image-2",
    "pro": "nano-banana-pro",
    "banana2": "nano-banana-2",
    "official": "gpt-image-2-official",
}

# 降级链：[(model_key, size, description)]
FALLBACK_CHAIN = [
    ("quality",    "4k", "gpt-image-2 4K ¥0.06~0.105 — 主力"),
    ("banana2",    "4k", "nano-banana-2 4K ¥0.12 — 降级1"),
    ("pro",        "4k", "nano-banana-pro 4K ¥0.18 — 降级2"),
    ("official",   "4k", "gpt-image-2-official 4K ¥0.053~11.43 — 降级3（贵）"),
    ("fast",       "4k", "nano-banana-fast 4K ¥0.06 — 兜底"),
]


def _try_one(prompt: str, model_key: str, size: str,
             reference_image: str = None, strength: float = 0.5,
             output_dir: str = ".",
             max_poll: int = MAX_POLL) -> str:
    """尝试用指定模型生成一张图片，成功返回路径，失败抛异常"""
    model_id = MODEL_IDS.get(model_key, model_key)
    body = {"model": model_id, "prompt": prompt, "n": 1, "size": size}

    if reference_image:
        import base64
        ext = Path(reference_image).suffix.lstrip(".") or "png"
        b64 = base64.b64encode(Path(reference_image).read_bytes()).decode()
        body["image"] = f"data:image/{ext};base64,{b64}"
        body["strength"] = strength

    headers = {"Authorization": f"Bearer {MAIZI_API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(f"{BASE_URL}/images/generations", json=body, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if data.get("error"):
        raise RuntimeError(f"API错误: {data['error']}")

    task_id = data.get("data", [{}])[0].get("task_id")
    if not task_id:
        raise RuntimeError(f"未获取到 task_id: {data}")

    print(f"  task_id={task_id} model={model_id} size={size}")

    for i in range(max_poll):
        time.sleep(POLL_INTERVAL)
        r = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers, timeout=30)
        r.raise_for_status()
        j = r.json()
        status = j.get("status", "")
        print(f"  [{i+1}] status={status}")

        if status == "completed":
            result_url = j.get("result_urls", [None])[0]
            if not result_url:
                raise RuntimeError(f"任务完成但无图片: {j}")
            img_url = result_url if result_url.startswith("http") else f"https://www.maizitech.cn{result_url}"
            img_resp = requests.get(img_url, timeout=60)
            img_resp.raise_for_status()

            ts = int(time.time())
            out_path = Path(output_dir) / f"gen_{model_key}_{ts}.png"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(img_resp.content)
            cost = j.get("cost", "?")
            print(f"  费用: ¥{cost}  saved: {out_path}")
            return str(out_path)

        if status == "failed":
            err = j.get("error_msg", str(j))
            raise RuntimeError(f"生成失败: {err}")

    raise TimeoutError(f"任务超时: task_id={task_id} ({max_poll * POLL_INTERVAL}s)")


def generate(prompt: str, model: str = "quality", size: str = "4k",
             reference_image: str = None, strength: float = 0.5,
             output_dir: str = ".") -> dict:
    """生成一张图片，自动降级。返回 {path, model_used, size_used, fallback_level}"""
    # 如果用户指定了非默认模型，只用那个
    if model != "quality":
        path = _try_one(prompt, model, size, reference_image, strength, output_dir)
        return {"path": path, "model_used": model, "size_used": size, "fallback_level": 0}

    # 否则走降级链
    last_error = None
    for level, (mkey, fsize, desc) in enumerate(FALLBACK_CHAIN):
        print(f"\n{'='*50}")
        print(f"[降级 {level}] {desc}")
        print(f"{'='*50}")
        try:
            path = _try_one(prompt, mkey, fsize, reference_image, strength, output_dir)
            return {"path": path, "model_used": mkey, "size_used": fsize, "fallback_level": level}
        except (TimeoutError, RuntimeError, requests.RequestException) as e:
            last_error = e
            print(f"  失败: {e}")
            if level < len(FALLBACK_CHAIN) - 1:
                print(f"  → 降级到下一级...")
            continue

    raise RuntimeError(f"所有模型均失败，最后错误: {last_error}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default="quality", choices=["fast", "quality", "pro", "banana2", "official"])
    parser.add_argument("--size", default="4k")
    parser.add_argument("--ref", default=None, help="参考图路径（可选）")
    parser.add_argument("--strength", type=float, default=0.5)
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    result = generate(args.prompt, args.model, args.size, args.ref, args.strength, args.out_dir)
    print(f"\n最终: {result['path']} (模型={result['model_used']}, 降级={result['fallback_level']})")
