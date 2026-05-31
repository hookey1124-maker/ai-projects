"""material 字段提取 — ABS / Plastic / Tempered Glass 等"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["material"]

_MATERIAL_PATTERNS = [
    (r'\bzinc\s*alloy\b', 'Zinc Alloy'),
    (r'\bzinc\b', 'Zinc'),
    (r'\bpolycarbonate\b', 'Polycarbonate'),
    (r'\bnylon\b', 'Nylon'),
    (r'\babs\b', 'ABS'),
    (r'\bpp\b', 'PP'),
    (r'\bpu\b', 'PU'),
    (r'\btpe\b', 'TPE'),
    (r'\bplastic\b', 'Plastic'),
    (r'\btempered\s*glass\b', 'Tempered Glass'),
    (r'\bglass\b', 'Glass'),
    (r'\bstainless\s*steel\b', 'Stainless Steel'),
    (r'\bsteel\b', 'Steel'),
    (r'\baluminum\b', 'Aluminum'),
    (r'\bcarbon\s*fiber\b', 'Carbon Fiber'),
    (r'\brubber\b', 'Rubber'),
    (r'\bleather\b', 'Leather'),
    (r'\bvinyl\b', 'Vinyl'),
    (r'\bmetal\b', 'Metal'),
]


def from_compat(compat_rows: list) -> str | None:
    """compatibility API 不提供材质"""
    return None


_MATERIAL_SPEC_KEYS = ["Material", "Primary Material", "Material Type", "Construction Material"]


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 多 key 提取材质"""
    for key in _MATERIAL_SPEC_KEYS:
        material = specs.get(key, "")
        if material:
            return canonicalize(material)
    return None


def from_title(title: str) -> str | None:
    """从标题正则提取材质"""
    title_lower = title.lower()
    for pattern, value in _MATERIAL_PATTERNS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return value
    return None


def from_image(image_path: str) -> str | None:
    """预留：视觉材质识别"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 material 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
