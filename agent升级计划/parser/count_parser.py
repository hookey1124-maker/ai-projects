"""count 字段提取 — 产品件数（返回 int）"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["count"]

# 排除 "4 Door Crew Cab" 中的 "4 door" 误判为件数
_DOOR_CONTEXT_RE = re.compile(
    r'\b(\d+)\s*door\s+(?:crew|cab|extended|king|super|mega|club|quad|double|access)\b',
    re.IGNORECASE
)
_DR_CLEAN_RE = re.compile(
    r'\b(\d+)\s*dr\b(?!\s*(?:pc|piece|x))',
    re.IGNORECASE
)

_COUNT_PATTERNS = [
    (re.compile(r"\bset\s*of\s*(\d+)\b", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*pc", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*piece", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*pack\b", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*x\b(?!\d)", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*[-]?\s*count\b", re.IGNORECASE), lambda n: n),
    # N-fin / N-wing / N-blade（鲨鱼鳍/尾翼/叶片类产品）
    (re.compile(r"\b(\d+)\s*[-]?\s*fin\b", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*[-]?\s*wing\b", re.IGNORECASE), lambda n: n),
    (re.compile(r"\b(\d+)\s*[-]?\s*blade\b", re.IGNORECASE), lambda n: n),
    (re.compile(r"\bsingle\b", re.IGNORECASE), lambda _: 1),
    (re.compile(r"\bpair\b", re.IGNORECASE), lambda _: 2),
    (re.compile(r"\bdual\b", re.IGNORECASE), lambda _: 2),
    (re.compile(r"\btwin\b(?!\s*(?:turbo|scroll|cam|cab))", re.IGNORECASE), lambda _: 2),
]


def _clean_title(title: str) -> str:
    """移除车门配置噪音，避免 '4 door' 被误判为 4 件"""
    text = _DOOR_CONTEXT_RE.sub("", title)
    text = _DR_CLEAN_RE.sub("", text)
    return text


def from_compat(compat_rows: list) -> int | None:
    """compatibility API 不提供件数"""
    return None


_COUNT_SPEC_KEYS = ["Number of Pieces", "Quantity", "Qty", "Package Quantity", "Set Size"]


def from_specs(specs: dict) -> int | None:
    """从 Item Specifics 多 key 提取件数。
    兼容 "(2) Interior Door Handle"、 "2 pcs"、 "2 - Interior" 等混合文本。
    """
    for key in _COUNT_SPEC_KEYS:
        pieces = specs.get(key, "")
        if not pieces:
            continue
        val = str(pieces).strip()
        if val.isdigit():
            return int(val)
        m = re.search(r'\b(\d+)\b', val)
        if m:
            return int(m.group(1))
    return None


def from_title(title: str) -> int | None:
    """从标题正则提取件数（修复 bug：不再有重复 re.search 覆盖 text_clean）"""
    text = _clean_title(title)
    for pattern, transform in _COUNT_PATTERNS:
        m = pattern.search(text)
        if m:
            if m.lastindex and m.group(1).isdigit():
                return transform(int(m.group(1)))
            return transform(0)  # single/pair 不需要 group(1)
    return None


def from_image(image_path: str) -> int | None:
    """预留：GLM-4V 视觉计件"""
    return None


def canonicalize(value: int | str) -> int | None:
    """标准化 count 为 int"""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    val_str = str(value).lower().strip()
    mapped = _CANONICAL.get(val_str)
    if mapped is not None:
        return mapped
    try:
        return int(val_str)
    except (ValueError, TypeError):
        return None
