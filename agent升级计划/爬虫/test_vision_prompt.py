"""测试新版 VISION_COMPARE_PROMPT — 对8个误判产品重新对比"""
import sys
import json
import base64
import time
from pathlib import Path

from openai import OpenAI

# 复用 product_intel 的配置
ZHIPU_API_KEY = "61ffd79cb5394e0284550b88ff3c0eda.hai1zorE9yumVzsd"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
VISION_MODEL = "glm-4v"

SKU_DIR = Path(r"C:\Users\Administrator\Desktop\AI项目\产品卖点主图和信息生成\Universal_Rear_Glossy-Black_4pcs_Bumper-Diffuser")
ANCHOR_IMG = SKU_DIR / "ebay_images" / "vision_116781928287.webp"

MISCLASSIFIED = [
    "406455835498",
    "305010922814",
    "225342546563",
    "184954131023",
    "177800760694",
    "175100629761",
    "165251322971",
    "125204891385",
]

VISION_COMPARE_PROMPT = """左边是锚定产品（标准品），右边是竞品（待验证）。

请分两步完成：

第一步 — 分别描述左右两图：
- anchor_desc: 左图的属性。逐项填写 position（方位: Front/Rear/Driver-Side/Passenger-Side/Front-Rear/Both-Sides/Unknown）、structure（结构: One-Piece/Multi-Piece/Unknown）、finish（表面处理: Chrome/Gloss-Black/Matte-Black/Textured-Black/Painted/Primered/Polished/Brushed/Carbon-Fiber/Black/White/Silver/Red/Blue/Green/Red-Black/Blue-Black/Unknown）、shape（轮廓形状描述）、count（图中可见的产品主体数量）
- candidate_desc: 右图的属性。逐项填写同样的字段

第二步 — 对比两组描述：
- 两段描述在 position + structure + finish + shape + count 五个维度都一致 → match=true
- 任一维度存在本质差异 → match=false
- 拍摄角度/光照造成的差异不算本质差异

注意：即使两图完全相同、找不出任何差异，也必须输出match=true的JSON，禁止只输出文字说明。

只输出 JSON：

{
  "anchor_desc": {"position": "...", "structure": "...", "finish": "...", "shape": "...", "count": 数字},
  "candidate_desc": {"position": "...", "structure": "...", "finish": "...", "shape": "...", "count": 数字},
  "match": true/false,
  "diff_type": "shape|structure|finish|size|none",
  "confidence": 0.0-1.0
}"""


def main():
    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)

    a_buf = ANCHOR_IMG.read_bytes()
    a_b64 = base64.b64encode(a_buf).decode()
    a_ext = ANCHOR_IMG.suffix.lstrip(".") or "png"

    results = []
    for pid in MISCLASSIFIED:
        c_img = SKU_DIR / "ebay_images" / f"vision_{pid}.webp"
        if not c_img.exists():
            print(f"  [SKIP] {pid} — 图片不存在")
            continue

        c_buf = c_img.read_bytes()
        c_b64 = base64.b64encode(c_buf).decode()
        c_ext = c_img.suffix.lstrip(".") or "png"

        try:
            resp = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/{a_ext};base64,{a_b64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/{c_ext};base64,{c_b64}"}},
                    {"type": "text", "text": VISION_COMPARE_PROMPT},
                ]}],
                max_tokens=600,
                temperature=0.1,
                timeout=45,
            )
            raw = resp.choices[0].message.content.strip()
            print(f"  RAW({pid}): {raw[:300]}")
            import re
            raw_clean = re.sub(r'^```(?:json)?\s*', '', raw).rstrip('`').strip()
            # try to find JSON block
            json_match = re.search(r'\{[\s\S]*\}', raw_clean)
            if json_match:
                raw_clean = json_match.group(0)
            result = json.loads(raw_clean)
            match = result.get("match", "?")
            anchor_desc = result.get("anchor_desc", {})
            cand_desc = result.get("candidate_desc", {})
            diff = result.get("diff_type", "?")
            conf = result.get("confidence", "?")
            print(f"  {pid}: match={match} diff={diff} conf={conf}")
            print(f"    anchor: pos={anchor_desc.get('position')} struct={anchor_desc.get('structure')} finish={anchor_desc.get('finish')} shape={anchor_desc.get('shape')} count={anchor_desc.get('count')}")
            print(f"    cand:   pos={cand_desc.get('position')} struct={cand_desc.get('structure')} finish={cand_desc.get('finish')} shape={cand_desc.get('shape')} count={cand_desc.get('count')}")
            results.append({"id": pid, "match": match, "diff_type": diff, "confidence": conf})
        except Exception as e:
            print(f"  {pid}: ERROR — {e}")
            results.append({"id": pid, "error": str(e)})

        time.sleep(1)

    # 汇总
    matches = [r for r in results if r.get("match") is True]
    non_matches = [r for r in results if r.get("match") is False]
    print(f"\n=== 汇总: {len(matches)}/8 match=true, {len(non_matches)}/8 match=false ===")
    if non_matches:
        print(f"仍误判: {[r['id'] for r in non_matches]}")


if __name__ == "__main__":
    main()
