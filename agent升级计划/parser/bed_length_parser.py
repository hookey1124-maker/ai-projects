"""bed_length 字段提取 — Short Bed / Standard Bed / Long Bed"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["bed_length"]

_SHORT_BED_RE = re.compile(
    r'\bshort\s*bed\b|\b5\.5\s*ft\b|\b5\.8\s*ft\b|\b5\.5\s*foot\b',
    re.IGNORECASE
)
_STANDARD_BED_RE = re.compile(
    r'\bstandard\s*bed\b|\b6\.5\s*ft\b|\b6\.4\s*ft\b|\b6\.5\s*foot\b',
    re.IGNORECASE
)
_LONG_BED_RE = re.compile(
    r'\blong\s*bed\b|\b8\s*ft\b|\b8\.1\s*ft\b|\b8\s*foot\b',
    re.IGNORECASE
)


def from_compat(compat_rows: list) -> str | None:
    """从 compatibility Trim/Model 推断 bed length"""
    if not compat_rows:
        return None
    combined = " ".join(
        row.get("Trim", "") + " " + row.get("Model", "")
        for row in compat_rows
    ).lower()
    if not combined.strip():
        return None

    if _SHORT_BED_RE.search(combined):
        return "Short Bed"
    if _LONG_BED_RE.search(combined):
        return "Long Bed"
    if _STANDARD_BED_RE.search(combined):
        return "Standard Bed"
    return None


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 提取 bed length（eBay 通常无此字段）"""
    for key in ["Bed Length", "Bed Size", "Bed Type"]:
        val = specs.get(key, "")
        if val:
            return canonicalize(val)
    return None


def from_title(title: str) -> str | None:
    """从标题正则提取 bed length"""
    if _SHORT_BED_RE.search(title):
        return "Short Bed"
    if _LONG_BED_RE.search(title):
        return "Long Bed"
    if _STANDARD_BED_RE.search(title):
        return "Standard Bed"
    return None


def from_image(image_path: str) -> str | None:
    """预留：视觉识别 bed length"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 bed_length 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
