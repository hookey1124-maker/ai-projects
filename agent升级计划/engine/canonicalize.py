"""编排层 — 调所有 parser → resolver → 输出完整 canonical 分类"""
import json
import re
from pathlib import Path

from engine.resolver import resolve_field
from engine.conflict import detect_conflicts
from engine.confidence import compute_overall_confidence

from parser import cab_parser, position_parser, count_parser, finish_parser
from parser import vehicle_parser, bed_length_parser, structure_parser
from parser import material_parser, color_parser, accessory_parser

_CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_noise_keys() -> set:
    keys = json.loads(_CONFIG_DIR.joinpath("noise_keys.json").read_text(encoding="utf-8"))
    return set(k.lower() for k in keys)


NOISE_KEYS = _load_noise_keys()


def clean_specs(specs: dict) -> str:
    """过滤噪音 key，返回纯文本用于 title regex 兜底"""
    parts = []
    for k, v in specs.items():
        if k.lower().strip() not in NOISE_KEYS:
            parts.append(str(v))
    return " ".join(parts).lower()


def classify_product(product: dict) -> dict:
    """完整产品分类 — 多来源提取 + 字段级优先级融合

    Args:
        product: {"title": str, "specs": dict, "compatibility": list, "image_path": str(可选)}

    Returns:
        12 个 canonical 字段，每个含 {value, confidence, source, candidates, conflict, ...}
    """
    title = product.get("title", "")
    specs = product.get("specs", {})
    compat = product.get("compatibility", [])
    image_path = product.get("image_path", "")

    # ── 逐字段提取 multi-source candidates ──
    fields = {}

    # cab
    fields["cab"] = resolve_field("cab", {
        "compatibility_api": cab_parser.canonicalize(cab_parser.from_compat(compat)),
        "item_specifics": cab_parser.canonicalize(cab_parser.from_specs(specs)),
        "title": cab_parser.canonicalize(cab_parser.from_title(title)),
        "image": cab_parser.canonicalize(cab_parser.from_image(image_path)),
        "ai_inference": None,
    })

    # position
    fields["position"] = resolve_field("position", {
        "compatibility_api": None,
        "item_specifics": position_parser.canonicalize(position_parser.from_specs(specs)),
        "title": position_parser.canonicalize(position_parser.from_title(title)),
        "image": position_parser.canonicalize(position_parser.from_image(image_path)),
        "ai_inference": None,
    })

    # count
    fields["count"] = resolve_field("count", {
        "compatibility_api": None,
        "item_specifics": count_parser.from_specs(specs),
        "title": count_parser.from_title(title),
        "image": count_parser.from_image(image_path),
        "ai_inference": None,
    })

    # finish
    fields["finish"] = resolve_field("finish", {
        "compatibility_api": None,
        "item_specifics": finish_parser.from_specs(specs),
        "title": finish_parser.from_title(title),
        "image": finish_parser.from_image(image_path),
        "ai_inference": None,
    })

    # color
    fields["color"] = resolve_field("color", {
        "compatibility_api": None,
        "item_specifics": color_parser.from_specs(specs),
        "title": color_parser.from_title(title),
        "image": color_parser.from_image(image_path),
        "ai_inference": None,
    })

    # material
    fields["material"] = resolve_field("material", {
        "compatibility_api": None,
        "item_specifics": material_parser.from_specs(specs),
        "title": material_parser.from_title(title),
        "image": material_parser.from_image(image_path),
        "ai_inference": None,
    })

    # vehicle
    fields["vehicle"] = resolve_field("vehicle", {
        "compatibility_api": vehicle_parser.from_compat(compat),
        "item_specifics": vehicle_parser.from_specs(specs),
        "title": vehicle_parser.from_title(title),
        "image": vehicle_parser.from_image(image_path),
        "ai_inference": None,
    })

    # bed_length
    fields["bed_length"] = resolve_field("bed_length", {
        "compatibility_api": bed_length_parser.from_compat(compat),
        "item_specifics": bed_length_parser.from_specs(specs),
        "title": bed_length_parser.from_title(title),
        "image": bed_length_parser.from_image(image_path),
        "ai_inference": None,
    })

    # structure
    fields["structure"] = resolve_field("structure", {
        "compatibility_api": None,
        "item_specifics": structure_parser.from_specs(specs),
        "title": structure_parser.from_title(title),
        "image": structure_parser.from_image(image_path),
        "ai_inference": None,
    })

    # product_type (from Item Specifics "Type")
    fields["product_type"] = resolve_field("product_type", {
        "compatibility_api": None,
        "item_specifics": _extract_product_type_from_specs(specs),
        "title": None,
        "image": None,
        "ai_inference": None,
    })

    # fitment_type (from Item Specifics "Fitment Type" + title regex)
    fields["fitment_type"] = resolve_field("fitment_type", {
        "compatibility_api": None,
        "item_specifics": _extract_fitment_type_from_specs(specs),
        "title": _extract_fitment_type_from_title(title),
        "image": None,
        "ai_inference": None,
    })

    # ── 全局冲突检测 ──
    conflict_summary = detect_conflicts(fields)

    # ── 全局置信度 ──
    overall_confidence = compute_overall_confidence(fields)

    return {
        "classification": fields,
        "conflict_summary": conflict_summary,
        "overall_confidence": overall_confidence,
        "_title": title,
        "_description_text": product.get("description_text", ""),
    }


_FITMENT_TYPE_TITLE_PATTERNS = [
    (re.compile(r"\breplacements?\b.*\bcovers?\b|\bcovers?\b.*\breplacements?\b", re.IGNORECASE), "Replacement/Cover"),
    (re.compile(r"\breplacements?\b", re.IGNORECASE), "Replacement"),
    (re.compile(r"\bcovers?\b", re.IGNORECASE), "Cover"),
    (re.compile(r"\btrims?\b", re.IGNORECASE), "Trim"),
    (re.compile(r"\bpanels?\b", re.IGNORECASE), "Panel"),
    (re.compile(r"\bshells?\b", re.IGNORECASE), "Trim"),
    (re.compile(r"\boverlays?\b", re.IGNORECASE), "Cover"),
]


def _extract_fitment_type_from_title(title: str) -> str | None:
    """从标题正则提取子类型（trim / cover / replacement / panel）"""
    if not title:
        return None
    for pattern, mapped in _FITMENT_TYPE_TITLE_PATTERNS:
        if pattern.search(title):
            return mapped
    return None


def _extract_product_type_from_specs(specs: dict) -> str | None:
    """从 Item Specifics 'Type' 提取产品类型"""
    ptype = specs.get("Type", "")
    if not ptype:
        return None
    maps = json.loads(
        _CONFIG_DIR.joinpath("canonical_maps.json").read_text(encoding="utf-8")
    ).get("product_type", {})
    return maps.get(ptype.lower().strip(), ptype)


def _extract_fitment_type_from_specs(specs: dict) -> str | None:
    """从 Item Specifics 'Fitment Type' / 'Part Name' / 'Part Type' 提取子类型"""
    ft = specs.get("Fitment Type", "") or specs.get("Part Name", "") or specs.get("Part Type", "")
    if not ft:
        return None
    maps = json.loads(
        _CONFIG_DIR.joinpath("canonical_maps.json").read_text(encoding="utf-8")
    ).get("fitment_type", {})
    # 先精确匹配
    result = maps.get(ft.lower().strip(), "")
    if result:
        return result
    # 再模糊匹配：值中出现 map key 的任一词
    val_lower = ft.lower().strip()
    for key, mapped in maps.items():
        if key in val_lower:
            return mapped
    return ft


# ── 向后兼容：导出原 product_intel.py 使用的字段名 ──

def _to_legacy(full_result: dict) -> dict:
    """将完整 canonical 输出转为 product_intel.py 兼容的扁平格式"""
    cls = full_result["classification"]

    def _v(key):
        r = cls.get(key, {})
        return r.get("value") if r else None

    def _src(key):
        r = cls.get(key, {})
        return r.get("source") if r else None

    return {
        "position": _v("position") or "Unknown",
        "position_source": _src("position"),
        "count": _v("count") or "Unknown",
        "count_source": _src("count"),
        "finish": _v("finish") or "Unknown",
        "finish_source": _src("finish"),
        "color": _v("color") or "Unknown",
        "material": _v("material") or "Unknown",
        "sub_type": _v("fitment_type") or "Unknown",
        "door_config": _to_door_config(_v("cab")),
        "structure": _v("structure") or "Unknown",
        "structure_source": _src("structure") or "unknown",
        "accessories": _get_accessories_flat(cls),
        "vehicle": _v("vehicle"),
        "bed_length": _v("bed_length"),
        # 向后兼容 needs_vision
        "needs_vision": _get_needs_vision(cls),
        "vision_result": None,
    }


def _to_door_config(cab: str) -> str:
    """cab → 旧 door_config 格式"""
    if not cab:
        return "Unknown"
    mapping = {
        "Crew Cab": "4-door-full",
        "Extended Cab": "4-door-half",
        "Regular Cab": "2-door",
    }
    return mapping.get(cab, "Unknown")


def _get_accessories_flat(cls: dict) -> list:
    r = cls.get("accessories", {})
    val = r.get("value") if r else None
    return val if isinstance(val, list) else []


def _get_needs_vision(cls: dict) -> list:
    """判断哪些字段需要视觉辅助"""
    needs = []
    for field in ["position", "structure", "finish"]:
        r = cls.get(field, {})
        if r and r.get("value") is None:
            needs.append(field)
    return needs


def classify_product_legacy(product: dict) -> dict:
    """向后兼容原 _classify_product() 的调用方式"""
    return _to_legacy(classify_product(product))
