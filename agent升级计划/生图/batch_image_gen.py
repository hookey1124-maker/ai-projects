"""批量生图 — 母文件下生成6张套图（主图/场景/细节/多角度/安装/套装）

自动从 market_intel.json 读取产品特征，动态构建 prompt。
"""
import sys
import json
import time
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from image_gen import generate as gen_one

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def _load_product_info(mother_dir: Path) -> dict:
    """从 market_intel.json 提取产品特征"""
    intel_file = mother_dir / "market_intel.json"
    if not intel_file.exists():
        raise FileNotFoundError(f"market_intel.json 不存在: {intel_file}")

    intel = json.loads(intel_file.read_text(encoding="utf-8"))

    # 分析产品特征
    specs = intel.get("key_specs", {})
    color = specs.get("Color", {}).get("value", "").lower()
    material = specs.get("Material", {}).get("value", "").lower()
    prod_type = specs.get("Type", {}).get("value", "").lower()
    count_raw = specs.get("Number of Pieces", {}).get("value", "1")
    placement = specs.get("Placement on Vehicle", {}).get("value", "")

    # 解析数量
    try:
        count = int(count_raw)
    except ValueError:
        count = 1

    # 判断特征
    is_chrome = "chrome" in color or "chrome" in " ".join(
        kw[0].lower() for kw in intel.get("common_keywords", [])[:20]
    )
    is_black = "black" in color
    is_textured = "textured" in color or "texture" in material

    # 材质描述
    if is_chrome:
        finish_desc = "chrome-plated finish over durable ABS construction"
        finish_short = "chrome"
    elif is_black and is_textured:
        finish_desc = "black textured finish over durable plastic construction"
        finish_short = "black textured"
    elif is_black:
        finish_desc = "black finish over durable plastic construction"
        finish_short = "black"
    else:
        finish_desc = "durable automotive-grade construction"
        finish_short = "standard"

    # 产品类型描述
    if "cover" in prod_type or "trim" in prod_type or "shell" in prod_type:
        product_name = "door handle cover trim"
    elif "door handle" in prod_type:
        product_name = "exterior door handle"
    elif "window" in prod_type or "glass" in prod_type:
        product_name = "door window glass"
    elif "body side" in prod_type:
        # Dodge Durango: "Body Side" = handle covers
        product_name = "door handle cover trim"
    else:
        product_name = prod_type or "auto part"

    # 适配车型（从标题样本提取）
    titles = intel.get("title_samples", [])
    vehicle_desc = ""
    if titles:
        # 提取年份-品牌-车型
        first_title = titles[0]
        # 尝试提取 "For YYYY-YYYY Brand Model" 模式
        import re
        m = re.search(r"(?:For|for)\s+(\d{2,4})\s*[-–]\s*(\d{2,4})\s+(.+?)(?:\s+(?:Door|Exterior|Front|Rear|Driver|Passenger|Left|Right|LH|RH|Outside|New|Textured|Chrome|Black|Set|Handle))", first_title)
        if m:
            vehicle_desc = f"{m.group(1)}-{m.group(2)} {m.group(3).strip()}"

    return {
        "product_name": product_name,
        "product_type": prod_type,
        "count": count,
        "finish_desc": finish_desc,
        "finish_short": finish_short,
        "is_chrome": is_chrome,
        "is_black": is_black,
        "is_textured": is_textured,
        "vehicle_desc": vehicle_desc,
        "specs": specs,
        "intel": intel,
    }


def _load_image_prompts(prompts_file: str) -> dict:
    """从 JSON 文件加载 6 张套图 Prompt（由 prompt_builder.py 生成）"""
    pf = Path(prompts_file)
    if not pf.exists():
        raise FileNotFoundError(
            f"Prompt 文件不存在: {pf}\n"
            f"请先运行 prompt_builder.py 生成 Prompt: python 生图/prompt_builder.py <mother_dir>"
        )
    prompts = json.loads(pf.read_text(encoding="utf-8"))
    required = {"main", "fitment", "install", "selling_points", "detail", "shipping"}
    actual = set(prompts.keys())
    missing = required - actual
    if missing:
        raise RuntimeError(f"Prompt 文件缺少字段: {missing}，实际字段: {actual}")
    return prompts


def _download_ref_image(mother_dir: Path) -> str | None:
    """从 market_intel.json 下载第一张参考图到本地，返回本地路径"""
    intel_file = mother_dir / "market_intel.json"
    if not intel_file.exists():
        return None

    intel = json.loads(intel_file.read_text(encoding="utf-8"))
    ref_urls = intel.get("reference_images", [])
    if not ref_urls:
        return None

    # 下载第一张参考图
    import requests
    ref_path = mother_dir / "ref_ebay.webp"
    if ref_path.exists():
        return str(ref_path)

    for url in ref_urls[:3]:
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"
            })
            resp.raise_for_status()
            ref_path.write_bytes(resp.content)
            print(f"参考图已下载: {ref_path} ({len(resp.content)} bytes)")
            return str(ref_path)
        except Exception as e:
            print(f"  下载参考图失败 ({url[:60]}): {e}")
            continue
    return None


def _cleanup_orphans(out_dir: Path) -> int:
    """清理前次失败残留的孤儿图片，避免重复花钱"""
    existing = list(out_dir.glob("gen_*.png"))
    if not existing:
        return 0

    # 如果有旧 image_batch.json，只保留其中标记为 ok 的
    old_batch = out_dir / "image_batch.json"
    keep = set()
    if old_batch.exists():
        try:
            old = json.loads(old_batch.read_text(encoding="utf-8"))
            for v in old.values():
                if v.get("status") == "ok" and v.get("path"):
                    keep.add(Path(v["path"]).name)
        except Exception:
            pass

    deleted = 0
    for f in existing:
        if f.name not in keep:
            f.unlink()
            deleted += 1
            print(f"  [清理孤儿图] {f.name}")

    # 旧 batch 也归档
    if old_batch.exists():
        bak = out_dir / "image_batch.bak.json"
        if bak.exists():
            bak.unlink()
        old_batch.rename(bak)

    return deleted


def batch_generate(mother_dir: str, model: str = "quality", ref_image: str = None,
                   prompts_file: str = None) -> dict:
    """生成6张套图并保存到母文件目录

    prompts_file: image_prompts.json 路径（由 prompt_builder.py 生成）。
                  不提供时自动查找 <mother_dir>/生成图片/image_prompts.json。
    """
    out_dir = Path(mother_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 预清理：删除前次失败残留，不浪费钱重复生成
    orphan_count = _cleanup_orphans(out_dir)
    if orphan_count:
        print(f"已清理 {orphan_count} 张孤儿图，开始全新生成\n")

    # 如果没有指定参考图，自动从 market_intel 下载
    if not ref_image:
        ref_image = _download_ref_image(out_dir)
        if ref_image:
            print(f"自动加载参考图: {ref_image}")
        else:
            print("警告: 无参考图，纯文本生图质量可能较差")

    # 加载 Prompt（优先使用指定的文件，否则自动查找）
    if prompts_file:
        pf = Path(prompts_file)
    else:
        pf = out_dir / "生成图片" / "image_prompts.json"
    print(f"加载 Prompt: {pf}")
    shots = _load_image_prompts(str(pf))

    # 读取产品信息（用于打印）
    try:
        info = _load_product_info(out_dir)
        print(f"产品: {info['product_name']} | 数量: {info['count']} | 材质: {info['finish_short']}")
        print(f"适配: {info.get('vehicle_desc', 'N/A')}")
    except Exception:
        pass  # _load_product_info 可能失败，不影响主流程

    out_dir = out_dir / "生成图片"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for i, (shot_key, shot_info) in enumerate(shots.items(), 1):
        label = shot_info["label"]
        prompt = shot_info["prompt"]
        print(f"\n{'='*50}")
        print(f"[{i}/6] {label}")
        print(f"  Prompt 长度: {len(prompt)} chars")
        print(f"{'='*50}")

        try:
            result = gen_one(
                prompt=prompt,
                model=model,
                size="4k",
                reference_image=ref_image,
                strength=0.5,
                output_dir=str(out_dir),
            )
            path = result["path"]
            print(f"  模型: {result.get('model_used', '?')} | 降级级: {result.get('fallback_level', '?')}")
            results[shot_key] = {"label": label, "path": path, "status": "ok"}
        except Exception as e:
            print(f"  FAILED: {e}")
            results[shot_key] = {"label": label, "path": None, "status": "error", "error": str(e)}

        if i < 6:
            time.sleep(2)

    # 保存结果索引
    index_file = out_dir / "image_batch.json"
    index_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n索引文件: {index_file}")

    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"完成: {ok}/6 张成功")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="批量生图 — 生成6张套图（从 image_prompts.json 读取 Prompt）")
    parser.add_argument("mother_dir", help="母文件目录")
    parser.add_argument("--model", default="quality", choices=["fast", "quality", "pro", "banana2", "official"])
    parser.add_argument("--ref", default=None, help="参考图路径（可选）")
    parser.add_argument("--prompts-file", default=None, help="image_prompts.json 路径（默认自动查找 mother_dir/生成图片/image_prompts.json）")
    args = parser.parse_args()
    batch_generate(args.mother_dir, args.model, args.ref, args.prompts_file)
