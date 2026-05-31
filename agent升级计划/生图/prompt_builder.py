"""DeepSeek 动态 Prompt 生成器 — 根据产品信息和卖点文案生成6张套图 Prompt

用法:
  python 生图/prompt_builder.py <mother_dir>                    # 从 market_intel.json + listing_output.json 生成
  python 生图/prompt_builder.py <mother_dir> --api-key sk-xxx   # 指定 API Key
"""
import sys
import json
import base64
from pathlib import Path
from openai import OpenAI

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# DeepSeek API 配置（优先级：命令行 > 环境变量 > 脚本常量）
DEEPSEEK_API_KEY = "sk-2bd057df46a34ed68aedb037eecd7131"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

SYSTEM_PROMPT = """You are an expert eBay product photographer and prompt engineer. Your job is to write 6 English image generation prompts for an AI image generator (like DALL-E / Stable Diffusion).

Each prompt must be around 150-300 words, highly detailed, describing exact camera angles, lighting, composition, materials, and spatial relationships.

## CRITICAL RULES (apply to ALL prompts):
- ALL prompts MUST be in English (the image generator only understands English)
- NO car brand logos, NO OEM emblems, NO brand names, NO trademarks, NO text/watermarks on products
- Products must sit naturally in the scene — NOT floating. Describe where they rest (on a surface, installed on door, etc.)
- Describe shadows: direction, softness, contact shadows where product meets surface
- Product structure must NOT be altered — no added parts, no deformed shapes
- Consistent lighting style across all 6 images (same color temperature, similar light direction)
- EXACT PRODUCT COUNT must be respected: every prompt must explicitly state the exact number of items. If the product is "1 piece", say "a single" or "one". If "2 pieces", say "a pair of". If "4 pieces", say "a set of 4" or "four individual". NEVER generate the wrong count. This is the single most important rule — count mismatch = rejected image.

## THE 6 IMAGE TYPES:

### 1. main — Product Main Image
- Full product display showing the complete item clearly
- NOT limited to white background — choose the best setting for this product type:
  - Studio photography with professional lighting setup
  - Outdoor scenes (field, desert, garage, workshop, industrial)
  - Natural environment that fits the product category
- Commercial photography quality, high resolution
- Best angle to show the product's key features (usually 45-degree elevated)

### 2. fitment — Vehicle Compatibility Infographic
- Clean infographic-style image showing compatible vehicles
- Display the Year + Brand + Model information in an elegant layout
- Can be designed as a clean specification card / compatibility chart style
- The product itself may appear as a small reference in the corner
- Professional, clean, readable — like a high-end catalog spec page

### 3. install — Installation Effect
- Product installed on the correct vehicle position, showing exact fitment
- The vehicle door/body panel should be a neutral color (dark gray, silver, or white)
- MUST clearly indicate the installation position (visual highlighting, subtle glow, or arrow)
- Factory-installation look, flush fit, OEM-quality appearance
- Shallow depth of field keeps focus on the installed product
- NO car brand logos or emblems visible on the vehicle

### 4. selling_points — Key Selling Points Visualization
- Visual representation of the product's key selling points from the listing bullets
- Examples of selling point visualizations:
  - UV/sun protection → product shown in bright sunlight, emphasizing weather resistance
  - Rust-proof → water beading on surface, corrosion resistance implied
  - Shatter-proof / durable → impact resistance, solid construction shown
  - Texture grip → close-up of anti-slip pattern with water droplets
- Choose the most visually compelling 1-2 selling points and create a scene around them
- The scene should tell a story about the product's quality

### 5. detail — Macro Detail Shot
- Extreme close-up macro photography showing surface texture and color
- Shallow depth of field with blurred background
- Show material quality: chrome reflections, matte grain, textured patterns, gloss finish
- Studio macro lighting, no glare on reflective surfaces
- The fine details should be sharply in focus

### 6. shipping — Logistics & After-Sale Service
- Clean commercial graphic style showing shipping/service advantages
- Default elements to visualize: Free Shipping badge, Fast Delivery, 30-Day Returns
- Professional packaging暗示 / ready-to-ship appearance
- Can show the product packaged or alongside shipping/service icons
- Trust-building visual: organized, professional, reliable

## OUTPUT FORMAT:
Return a JSON object with exactly 6 keys. Each value is an object with "label" and "prompt" fields.
The prompts must be complete, detailed, and ready to send to an image generator.

```json
{
  "main": {"label": "Product Main Image", "prompt": "..."},
  "fitment": {"label": "Vehicle Compatibility Infographic", "prompt": "..."},
  "install": {"label": "Installation Effect", "prompt": "..."},
  "selling_points": {"label": "Selling Points Visualization", "prompt": "..."},
  "detail": {"label": "Macro Detail Shot", "prompt": "..."},
  "shipping": {"label": "Logistics & After-Sale Service", "prompt": "..."}
}
```

Reply with ONLY the JSON object, no other text."""


def _read_inputs(mother_dir: Path) -> dict:
    """读取产品信息和文案"""
    intel_file = mother_dir / "market_intel.json"
    listing_file = mother_dir / "listing_output.json"
    ref_image = mother_dir / "ref_ebay.webp"
    if not ref_image.exists():
        ref_image = None

    if not intel_file.exists():
        raise FileNotFoundError(f"market_intel.json 不存在: {intel_file}")
    if not listing_file.exists():
        raise FileNotFoundError(f"listing_output.json 不存在: {listing_file}")

    return {
        "market_intel": json.loads(intel_file.read_text(encoding="utf-8")),
        "listing": json.loads(listing_file.read_text(encoding="utf-8")),
        "ref_image": ref_image,
    }


def _build_user_message(inputs: dict) -> str:
    """构建发给 DeepSeek 的用户消息"""
    intel = inputs["market_intel"]
    listing = inputs["listing"]

    # 提取关键产品信息
    specs = intel.get("key_specs", {})
    prod_type = specs.get("Type", {}).get("value", "Auto Part")
    color = specs.get("Color", {}).get("value", "N/A")
    material = specs.get("Material", {}).get("value", "N/A")
    count = specs.get("Number of Pieces", {}).get("value", "1")
    placement = specs.get("Placement on Vehicle", {}).get("value", "N/A")

    # 适配车型（从标题样本提取，复用 batch_image_gen 的逻辑）
    import re
    titles = intel.get("title_samples", [])
    vehicle_desc = "N/A"
    if titles:
        m = re.search(
            r"(?:For|for)\s+(\d{2,4})\s*[-–]\s*(\d{2,4})\s+(.+?)(?:\s+(?:Door|Exterior|Front|Rear|Driver|Passenger|Left|Right|LH|RH|Outside|New|Textured|Chrome|Black|Set|Handle))",
            titles[0]
        )
        if m:
            vehicle_desc = f"{m.group(1)}-{m.group(2)} {m.group(3).strip()}"

    # 标题
    title = listing.get("title", "N/A")
    bullets = listing.get("bullets", [])
    bullets_text = "\n".join(f"  - {b}" for b in bullets) if bullets else "  N/A"

    return f"""## Product Information

- **Product Type**: {prod_type}
- **Color**: {color}
- **Material**: {material}
- **Number of Pieces**: {count}
- **Placement on Vehicle**: {placement}
- **Compatible Vehicles**: {vehicle_desc}

## eBay Listing

- **Title**: {title}

- **Selling Points (bullets)**:
{bullets_text}

## Task

Generate 6 image prompts for the 6 types (main / fitment / install / selling_points / detail / shipping).

IMPORTANT CONTEXT for each type:

1. **main**: Product type is "{prod_type}" — choose the most appropriate background/scene for this product category.
2. **fitment**: Compatible vehicles are "{vehicle_desc}" — use this exact information in the infographic.
3. **install**: Placement is "{placement}" — show the product installed in this position on a vehicle door.
4. **selling_points**: Use the bullets above to choose 1-2 most visually compelling selling points. Create a scene that VISUALLY demonstrates these benefits.
5. **detail**: Color is "{color}", material is "{material}" — highlight the surface texture and finish quality.
6. **shipping**: Reference "Free Shipping", "Fast Delivery", "30-Day Returns" as standard benefits. The product is shipped from a professional warehouse.

CRITICAL COUNT RULE: This product contains exactly {count} piece(s). EVERY prompt must visually show exactly this number — no more, no less. Use specific quantity language: "a single product" for 1, "a pair of products" for 2, "a set of 4 products arranged in a grid" for 4. If you get the count wrong, the entire batch is rejected. Double-check each prompt before output.

For the fitment infographic, the compatible vehicles information "{vehicle_desc}" should be the hero element — design it like a clean spec card.

Reply with ONLY the JSON object."""


def _build_vision_message(user_text: str, image_path: Path) -> list:
    """构建带图片的 vision 消息（如果参考图存在）"""
    if not image_path or not image_path.exists():
        return [{"type": "text", "text": user_text}]

    img_buffer = image_path.read_bytes()
    b64 = base64.b64encode(img_buffer).decode()
    ext = image_path.suffix.lower().lstrip(".")
    mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
    mime = mime_map.get(ext, "image/webp")

    return [
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        {"type": "text", "text": "This is the reference product image from eBay. Use it to understand the product's appearance, shape, and details. The AI-generated images should match this product's structure.\n\n" + user_text},
    ]


def build_prompts(mother_dir: str, api_key: str = None) -> dict:
    """根据产品信息生成6张套图 Prompt，返回 {key: {label, prompt}}"""
    mother_dir = Path(mother_dir)
    inputs = _read_inputs(mother_dir)

    key = api_key or DEEPSEEK_API_KEY or None
    if not key:
        raise ValueError(
            "DeepSeek API Key 未配置。请通过以下方式之一提供：\n"
            "  1. 命令行: --api-key sk-xxx\n"
            "  2. 环境变量: DEEPSEEK_API_KEY\n"
            "  3. 编辑脚本顶部的 DEEPSEEK_API_KEY 常量"
        )

    client = OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL)

    user_text = _build_user_message(inputs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_vision_message(user_text, inputs["ref_image"])},
    ]

    print(f"调用 DeepSeek API ({DEEPSEEK_MODEL}) 生成 6 张套图 Prompt...")
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        stream=False,
        timeout=120,
    )

    raw = response.choices[0].message.content.strip()

    # 去除可能的 markdown 代码块
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]

    try:
        prompts = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"DeepSeek 返回内容（前500字符）:\n{raw[:500]}")
        raise RuntimeError(f"解析 DeepSeek 返回的 JSON 失败: {e}")

    # 验证必需字段
    required_keys = {"main", "fitment", "install", "selling_points", "detail", "shipping"}
    actual_keys = set(prompts.keys())
    missing = required_keys - actual_keys
    if missing:
        raise RuntimeError(f"返回的 JSON 缺少字段: {missing}")

    for k in required_keys:
        if not isinstance(prompts[k], dict) or "prompt" not in prompts[k]:
            raise RuntimeError(f"字段 '{k}' 格式不正确，需要 {{label, prompt}}")

    return prompts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DeepSeek 动态 Prompt 生成器")
    parser.add_argument("mother_dir", help="母文件目录（含 market_intel.json + listing_output.json）")
    parser.add_argument("--api-key", default=None, help="DeepSeek API Key")
    parser.add_argument("--model", default=DEEPSEEK_MODEL, help="DeepSeek 模型名")
    args = parser.parse_args()

    DEEPSEEK_MODEL = args.model

    prompts = build_prompts(args.mother_dir, args.api_key)

    out_file = Path(args.mother_dir) / "生成图片" / "image_prompts.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prompt 已保存到: {out_file}")

    for k, v in prompts.items():
        print(f"  [{v['label']}] {len(v['prompt'])} chars")
