"""color 字段提取 — Black / White / Silver 等"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["color"]

_COLOR_PATTERNS = [
    (r'\bblack\b', 'Black'),
    (r'\bwhite\b', 'White'),
    (r'\bsilver\b', 'Silver'),
    (r'\bgrey\b|\bgray\b', 'Gray'),
    (r'\bred\b', 'Red'),
    (r'\bblue\b', 'Blue'),
    (r'\bgreen\b', 'Green'),
]


def from_compat(compat_rows: list) -> str | None:
    """compatibility API 不提供颜色"""
    return None


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 'Color' 提取颜色"""
    color = specs.get("Color", "") or specs.get("Primary Color", "")
    if color:
        return canonicalize(color)
    return None


def from_title(title: str) -> str | None:
    """从标题正则提取颜色"""
    title_lower = title.lower()
    for pattern, value in _COLOR_PATTERNS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return value
    return None


def from_image(image_path: str) -> str | None:
    """预留：视觉颜色识别"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 color 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
