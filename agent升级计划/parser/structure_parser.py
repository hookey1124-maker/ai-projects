"""structure 字段提取 — One-Piece / Multi-Piece"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["structure"]

_ONE_PIECE_RE = re.compile(
    r'\bone[\s-]piece\b|\bsingle[\s-]piece\b|\b1pc\s*design\b',
    re.IGNORECASE
)
_MULTI_PIECE_RE = re.compile(
    r'\bmulti[\s-]piece\b|\bassembl(?:ed|y)\b|\bseparate\b',
    re.IGNORECASE
)
_N_PIECE_RE = re.compile(
    r'\b(\d+|two|three|four)\s*[-]?\s*piece(?:s)?\b',
    re.IGNORECASE
)


def from_compat(compat_rows: list) -> str | None:
    """compatibility API 不提供结构信息"""
    return None


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 提取结构（部分卖家填写）"""
    for key in ["Structure", "Construction", "Piece Type", "Design"]:
        val = specs.get(key, "")
        if val:
            return canonicalize(val)
    return None


def from_title(title: str) -> str | None:
    """从标题正则提取一体/分体结构"""
    m = _N_PIECE_RE.search(title)
    if m:
        n = m.group(1).lower()
        return "One-Piece" if n in ("1", "one") else "Multi-Piece"
    if _ONE_PIECE_RE.search(title):
        return "One-Piece"
    if _MULTI_PIECE_RE.search(title):
        return "Multi-Piece"
    return None


def from_image(image_path: str) -> str | None:
    """预留：GLM-4V 视觉结构识别"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 structure 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
