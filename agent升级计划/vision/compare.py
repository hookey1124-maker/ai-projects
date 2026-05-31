"""Vision Diff — GLM-4V 并排对比验证

对 borderline 候选进行视觉兜底验证。
输入锚点图 + 竞品图，AI 并排对比，识别文本规则漏掉的结构差异。
"""
import re
import json
import base64
import time
from pathlib import Path
from openai import OpenAI

ZHIPU_API_KEY = "61ffd79cb5394e0284550b88ff3c0eda.hai1zorE9yumVzsd"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
VISION_MODEL = "GLM-4V-Plus"

COMPARE_PROMPT = """你是一个汽车零配件质检专家。左边是锚定产品图（标准品），右边是竞品图（待验证）。

请分两步完成：

第一步 — 分别描述左右两图：
- anchor_desc: 左图（锚定产品）的属性。逐项填写 position（方位）/ structure（一体式还是多片式）/ finish（表面处理：Chrome/Gloss-Black/Matte-Black/Black/Carbon-Fiber/Painted/...）/ shape（轮廓形状）/ count（件数）
- candidate_desc: 右图（竞品）的属性。逐项填写同样的字段

第二步 — 对比两组描述，判断是否同一款产品：
- 两段描述在 position + structure + finish + shape + count 五个维度都一致 → match=true
- 任一维度存在本质差异 → match=false。拍摄角度/光照造成的差异不算

按以下 JSON 输出（只输出 JSON，不要任何其他文字）：

{
  "anchor_desc": {"position": "...", "structure": "...", "finish": "...", "shape": "...", "count": 数字},
  "candidate_desc": {"position": "...", "structure": "...", "finish": "...", "shape": "...", "count": 数字},
  "match": true/false,
  "diff_type": "shape|structure|finish|size|none",
  "shape_detail": "...",
  "structure_detail": "...",
  "finish_detail": "...",
  "size_detail": "...",
  "confidence": 0.0-1.0
}"""


def _encode_image(image_path: str) -> str:
    """将图片编码为 base64 data URL（支持本地路径和 HTTP URL）"""
    if image_path.startswith("http"):
        try:
            import requests
            resp = requests.get(image_path, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"
            })
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            ext = "jpg"
            if "png" in ct:
                ext = "png"
            elif "webp" in ct:
                ext = "webp"
            b64 = base64.b64encode(resp.content).decode()
            return f"data:image/{ext};base64,{b64}"
        except Exception:
            return ""
    buf = Path(image_path).read_bytes()
    b64 = base64.b64encode(buf).decode()
    ext = Path(image_path).suffix.lower().lstrip(".") or "png"
    return f"data:image/{ext};base64,{b64}"


def compare_images(anchor_img: str, candidate_img: str, timeout: int = 45) -> dict:
    """并排对比锚点图和竞品图。

    Args:
        anchor_img: 锚定产品主图路径
        candidate_img: 竞品主图路径

    Returns:
        {match, diff_type, details, confidence}
    """
    if not Path(anchor_img).exists():
        return {"match": True, "diff_type": "none", "error": "anchor image not found"}
    if not Path(candidate_img).exists():
        return {"match": True, "diff_type": "none", "error": "candidate image not found"}

    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)

    try:
        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": _encode_image(anchor_img)}},
                {"type": "image_url", "image_url": {"url": _encode_image(candidate_img)}},
                {"type": "text", "text": COMPARE_PROMPT},
            ]}],
            max_tokens=600,
            temperature=0.1,
            timeout=timeout,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw).rstrip('`').strip()

        result = json.loads(raw)
        # 将 candidate_desc 字段提升到顶层（兼容 vision_filter 等调用方）
        if "candidate_desc" in result:
            cd = result["candidate_desc"]
            for field in ["position", "structure", "finish", "count"]:
                if field in cd and field not in result:
                    result[field] = cd[field]
        result["_raw"] = raw
        return result

    except json.JSONDecodeError:
        return {"match": True, "diff_type": "none", "error": "parse_failed", "_raw": raw if 'raw' in dir() else ""}
    except Exception as e:
        return {"match": True, "diff_type": "none", "error": str(e)}


def vision_filter(anchor_img: str, candidates: list[dict],
                  threshold: float = 0.78, delay: float = 0.5) -> list[dict]:
    """对 borderline 候选进行视觉兜底验证。

    仅对 similarity < threshold 且 >= threshold - 0.15 的候选运行。
    结构差异(match=false, diff_type=structure) → final_status 降为 "rejected"
    其他差异 → final_status 降为 "borderline"

    Args:
        anchor_img: 锚定产品主图路径
        candidates: score_candidates() 输出列表（含 similarity/final_status/_product数据）
        threshold: borderline 触发阈值

    Returns:
        更新了 final_status 的 candidates 列表
    """
    for c in candidates:
        if c.get("final_status") == "rejected":
            continue
        sim = c.get("similarity", 0)
        if sim >= threshold:
            continue
        if sim < threshold - 0.15:
            continue

        candidate_img = _get_first_image(c)
        if not candidate_img:
            continue

        result = compare_images(anchor_img, candidate_img)
        c["_vision_diff"] = result

        if result.get("error"):
            continue

        if not result.get("match", True):
            if result.get("diff_type") == "structure":
                c["final_status"] = "rejected"
                c["_vision_reject_reason"] = result.get("structure_detail", "视觉结构差异")
            else:
                c["final_status"] = "borderline"
                c["_vision_borderline_reason"] = (
                    result.get("shape_detail") or
                    result.get("finish_detail") or
                    result.get("size_detail") or
                    "视觉差异"
                )

        time.sleep(delay)

    return candidates


def _get_first_image(candidate: dict) -> str | None:
    """从 candidate 数据中获取第一张图片路径"""
    images = candidate.get("images") or candidate.get("_product", {}).get("images", [])
    if images:
        img = images[0]
        if isinstance(img, str) and not img.startswith("http"):
            return img
    product = candidate.get("_product", {})
    image_path = product.get("image_path", "")
    if image_path and Path(image_path).exists():
        return image_path
    return None
