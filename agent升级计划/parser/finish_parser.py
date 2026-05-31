"""finish 字段提取 — Chrome / Gloss-Black / Matte-Black 等"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["finish"]

_FINISH_PATTERNS = [
    ("Black-Chrome", [r"\bblack\s*chrome\b"]),
    ("Smoke-Chrome", [r"\bsmoke\s*chrome\b", r"\bsmoked\s*chrome\b"]),
    ("Gloss-Black", [r"\bgloss\s*(?:y)?\s*black\b", r"\bpiano\s*black\b"]),
    ("Satin-Black", [r"\bsatin\s*black\b"]),
    ("Matte-Black", [r"\bmatte?\s*black\b", r"\bflat\s*black\b"]),
    ("Textured-Black", [r"\btextured\s*black\b"]),
    ("Carbon-Fiber", [r"\bcarbon\s*fiber\b"]),
    ("Painted", [r"\bpaint(?:ed|able)?[-\s]*to[-\s]*match\b", r"\bpainted\b"]),
    ("Powder-Coated", [r"\bpowder\s*coat(?:ed)?\b"]),
    ("Primered", [r"\bprimer(?:ed)?\b"]),
    ("Polished", [r"\bpolished\b"]),
    ("Anodized", [r"\banodized?\b"]),
    ("Brushed", [r"\bbrushed\b"]),
    ("Satin", [r"\bsatin\b"]),
    ("Black", [r"\bblack\b"]),
    ("Chrome", [r"\bchrome\b"]),
    ("White", [r"\bwhite\b"]),
    ("Silver", [r"\bsilver\b"]),
    ("Gray", [r"\bgrey\b", r"\bgray\b"]),
    ("Red", [r"\bred\b"]),
    ("Blue", [r"\bblue\b"]),
    ("Green", [r"\bgreen\b"]),
]


def from_compat(compat_rows: list) -> str | None:
    """compatibility API 不提供表面处理信息"""
    return None


_FINISH_SPEC_KEYS = ["Finish", "Primary Color", "Exterior Finish", "Surface Finish", "Color"]


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 提取表面处理（遍历多个可能的 key）"""
    for key in _FINISH_SPEC_KEYS:
        finish = specs.get(key, "")
        if finish:
            val = finish.strip()
            result = canonicalize(val)
            if result:
                return result
    return None


def from_title(title: str) -> str | None:
    """从标题正则提取表面处理。匹配到裸色时检查是否含 Black（双色组合）。"""
    result = None
    for name, patterns in _FINISH_PATTERNS:
        for pat in patterns:
            if re.search(pat, title, re.IGNORECASE):
                result = name
                break
        if result:
            break

    if not result:
        if re.search(r"\btextured\b", title, re.IGNORECASE):
            return "Textured"
        return None

    # 双色检测：匹配到裸色时检查标题是否含其他颜色
    _BARE_COLORS = {"Red", "Blue", "Green", "White", "Silver", "Gray"}
    has_black = re.search(r"\bblack\b", title, re.IGNORECASE)
    if result in _BARE_COLORS and has_black:
        return f"{result}-Black"
    if result == "Black":
        for color in _BARE_COLORS:
            if re.search(rf'\b{re.escape(color.lower())}\b', title, re.IGNORECASE):
                return f"{color}-Black"

    return result


def from_image(image_path: str) -> str | None:
    """预留：GLM-4V 视觉表面处理识别"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 finish 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
