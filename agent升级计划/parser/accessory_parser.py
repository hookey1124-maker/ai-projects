"""accessory 字段提取 — 附带配件列表"""
import re

_ACCESSORY_PATTERNS = {
    "screws": [r"\bscrew(s)?\b", r"\bbolt(s)?\b", r"\bnut(s)?\b", r"\bwasher(s)?\b"],
    "gaskets": [r"\bgasket(s)?\b", r"\bseal(s)?\b", r"\bo-ring(s)?\b"],
    "clips": [r"\bclip(s)?\b", r"\bretainer(s)?\b", r"\bfastener(s)?\b"],
    "mounting_hardware": [r"\bmount(ing)?\s*(?:kit|hardware)\b", r"\bhardware\s*kit\b"],
    "installation_tool": [r"\btool(s)?\b", r"\bwrench\b", r"\bkey\b"],
    "wiring": [r"\bwiring\b", r"\bharness\b", r"\bconnector(s)?\b", r"\bplug(s)?\b"],
    "brackets": [r"\bbracket(s)?\b", r"\bmounting\s*plate\b", r"\badaptor(s)?\b"],
    "springs": [r"\bspring(s)?\b"],
    "rods": [r"\brod(s)?\b", r"\blinkage\b", r"\bactuator\b"],
}


def from_compat(compat_rows: list) -> list | None:
    """compatibility API 不提供配件信息"""
    return None


def from_specs(specs: dict) -> list | None:
    """从 Item Specifics 提取配件（Items Included / Package Includes）"""
    items = specs.get("Items Included", "") or specs.get("Package Includes", "") or specs.get("Package Note", "")
    if not items:
        return None

    items_lower = items.lower()
    found = []
    for category, patterns in _ACCESSORY_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, items_lower):
                found.append(category)
                break
    return found if found else None


def from_title(title: str) -> list | None:
    """从标题正则提取配件列表"""
    text_lower = title.lower()
    found = []
    for category, patterns in _ACCESSORY_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                found.append(category)
                break
    return found if found else None


def from_image(image_path: str) -> list | None:
    """预留：GLM-4V 视觉配件识别"""
    return None
