"""cab 字段提取 — Crew Cab / Extended Cab / Regular Cab"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["cab"]

_HALF_CAB_RE = re.compile(
    r'\bsuper\s*cab\b|\bextended\s*cab\b|\bquad\s*cab\b'
    r'|\bdouble\s*cab\b|\baccess\s*cab\b|\bking\s*cab\b',
    re.IGNORECASE
)
_FULL_CAB_RE = re.compile(
    r'\bcrew\s*cab\b|\bsuper\s*crew\b|\bcrew\s*max\b|\bmega\s*cab\b',
    re.IGNORECASE
)
_TWO_CAB_RE = re.compile(
    r'\bregular\s*cab\b|\bsingle\s*cab\b|\bstandard\s*cab\b',
    re.IGNORECASE
)


def from_compat(compat_rows: list) -> str | None:
    """从 compatibility API 的 Trim 字段提取 cab 类型"""
    if not compat_rows:
        return None
    trims = []
    for row in compat_rows:
        trim = row.get("Trim", "")
        if trim:
            trims.append(trim.lower())
    combined = " ".join(trims)
    if not combined:
        return None

    if _FULL_CAB_RE.search(combined):
        return "Crew Cab"
    if _HALF_CAB_RE.search(combined):
        return "Extended Cab"
    if _TWO_CAB_RE.search(combined):
        return "Regular Cab"

    # 从 Model 名推断
    for row in compat_rows:
        model = row.get("Model", "").lower()
        if "crew cab" in model:
            return "Crew Cab"
        if "extended cab" in model or "double cab" in model:
            return "Extended Cab"
        if "regular cab" in model:
            return "Regular Cab"
    return None


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 提取 cab（eBay 通常没有此字段）"""
    return None


def from_title(title: str) -> str | None:
    """从标题正则提取 cab 类型"""
    if _FULL_CAB_RE.search(title):
        return "Crew Cab"
    if _HALF_CAB_RE.search(title):
        return "Extended Cab"
    if _TWO_CAB_RE.search(title):
        return "Regular Cab"
    return None


def from_image(image_path: str) -> str | None:
    """预留：从图片提取 cab（暂不实现）"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 cab 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
