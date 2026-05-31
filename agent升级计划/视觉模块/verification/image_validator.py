"""生图后自动验证 — 调用 GLM-4V 检查生成图片是否符合规则"""
import json
import base64
import time
from pathlib import Path
from openai import OpenAI

# 智谱 GLM-4V API 配置
ZHIPU_API_KEY = "61ffd79cb5394e0284550b88ff3c0eda.hai1zorE9yumVzsd"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "GLM-4V-Plus"

CHECKLIST_PROMPT = """请严格检查这张产品图片，按以下每一项输出 JSON：

1. product_count_match: 图中可见产品数量是否与描述一致？（true/false）
2. structure_changed: 产品结构是否被修改/变形/新增部件？（true/false）
3. missing_parts: 产品是否有缺失部件？（true/false）
4. floating_issue: 产品是否悬浮/漂浮，没有与背景自然结合？（true/false）
5. logo_detected: 图中是否有汽车品牌Logo/商标/品牌文字（如 Ford/BMW/Toyota 等）？（true/false）
6. perspective_ok: 透视是否合理一致？（true/false）
7. lighting_ok: 光影是否合理？（true/false）
8. confidence: 你对整体判断的置信度（0-1）
9. issues: 如果发现问题，用中文描述具体是什么问题。如果没有问题，写"无"
10. passed: 根据规则判定是否通过（image_validator.py 规定的判定条件：structure_changed=true 或 logo_detected=true → 不通过；其他问题可重试）

只输出 JSON，不要任何其他文字。"""

# true=bad（出现即为问题）
REJECT_CONDITIONS = ["structure_changed", "logo_detected"]
RETRY_CONDITIONS = ["floating_issue", "missing_parts"]
# true=good（不出现即为问题）— 检查时为 false 触发
POSITIVE_CONDITIONS = ["product_count_match", "perspective_ok", "lighting_ok"]


def _call_glm4v(image_path: str, question: str, timeout: int = 60) -> str:
    """调用 GLM-4V 分析图片，返回原始文本"""
    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    img_buffer = Path(image_path).read_bytes()
    b64 = base64.b64encode(img_buffer).decode()
    ext = Path(image_path).suffix.lower().lstrip(".")
    mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
    mime = mime_map.get(ext, "image/png")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": question}
            ]
        }],
        stream=False,
        timeout=timeout
    )
    return response.choices[0].message.content


def _parse_response(raw: str) -> dict:
    """从 GLM-4V 返回中提取 JSON"""
    text = raw.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def _count_products(image_path: str, expected_count: int) -> dict:
    """第一轮验证：只数数量（独立调用，确保不被其他问题分散注意力）"""
    question = (
        f"How many separate individual products/items are visible in this image? "
        f"Expected count: {expected_count}. "
        f"Count carefully, one by one. "
        f"Reply with ONLY a number, nothing else."
    )
    try:
        raw = _call_glm4v(image_path, question)
        count = int(raw.strip())
        match = (count == expected_count)
        return {"count": count, "expected": expected_count, "match": match}
    except Exception as e:
        return {"count": -1, "expected": expected_count, "match": None, "error": str(e)}


def validate_image(image_path: str, expected_product_count: int = None) -> dict:
    """验证单张生成图片（两轮 GLM-4V 调用）

    Args:
        image_path: 生成图片的绝对路径
        expected_product_count: 预期的产品数量

    Returns:
        {
            "product_count_match": bool,
            "structure_changed": bool,
            "missing_parts": bool,
            "floating_issue": bool,
            "logo_detected": bool,
            "perspective_ok": bool,
            "lighting_ok": bool,
            "confidence": float,
            "issues": str,
            "passed": bool,
            "action": "accept" | "reject" | "retry" | "human_review",
            "reason": str
        }
    """
    start_time = time.time()

    # ── 第一轮：数量检查（独立调用）──
    if expected_product_count is not None:
        count_result = _count_products(image_path, expected_product_count)
        if not count_result.get("match"):
            return {
                "product_count_match": False,
                "expected_count": expected_product_count,
                "actual_count": count_result.get("count", -1),
                "passed": False,
                "action": "retry",
                "reason": f"数量不符：期望 {expected_product_count}，实际 {count_result.get('count', '?')}",
                "elapsed": round(time.time() - start_time, 2)
            }

    # ── 第二轮：质量检查 ──
    try:
        raw = _call_glm4v(image_path, CHECKLIST_PROMPT)
        result = _parse_response(raw)
    except Exception as e:
        return {
            "error": str(e),
            "passed": False,
            "action": "retry",
            "reason": f"GLM-4V 调用失败: {e}",
            "elapsed": round(time.time() - start_time, 2)
        }

    # 决定处理方式
    result["elapsed"] = round(time.time() - start_time, 2)

    # 自动拒绝（true=bad）
    for cond in REJECT_CONDITIONS:
        if result.get(cond, False):
            result["action"] = "reject"
            result["reason"] = f"触发自动拒绝条件: {cond}=true，图片不可用，需重新生成"
            result["passed"] = False
            return result

    # 自动重试（true=bad）
    for cond in RETRY_CONDITIONS:
        if result.get(cond, False):
            result["action"] = "retry"
            result["reason"] = f"触发自动重试条件: {cond}=true"
            result["passed"] = False
            return result

    # 正向条件检查（true=good，false=bad → 重试）
    for cond in POSITIVE_CONDITIONS:
        if not result.get(cond, True):
            result["action"] = "retry"
            result["reason"] = f"触发自动重试条件: {cond}=false"
            result["passed"] = False
            return result

    # 人工审核（置信度低）
    if result.get("confidence", 0) < 0.85:
        result["action"] = "human_review"
        result["reason"] = f"置信度 {result['confidence']} < 0.85，需人工确认"
        result["passed"] = False
        return result

    result["action"] = "accept"
    result["reason"] = "所有检查通过"
    result["passed"] = True
    return result


def batch_validate(image_paths: list, expected_product_count: int = None) -> list:
    """批量验证多张图片"""
    results = []
    for path in image_paths:
        result = validate_image(path, expected_product_count)
        result["image_path"] = path
        results.append(result)
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python image_validator.py <image_path> [expected_product_count]")
        sys.exit(1)
    count = int(sys.argv[2]) if len(sys.argv) > 2 else None
    result = validate_image(sys.argv[1], count)
    print(json.dumps(result, ensure_ascii=False, indent=2))
