"""position 字段提取 — Front-Driver-Side / Rear-Passenger-Side 等"""
import re
from pathlib import Path
import json

_CANONICAL = json.loads(
    Path(__file__).parent.parent.joinpath("config", "canonical_maps.json").read_text(encoding="utf-8")
)["position"]

_DIRECTION_RE = re.compile(
    r'\b(?:left|driver(?:\s*side)?|lh)\b', re.IGNORECASE
)
_RIGHT_RE = re.compile(
    r'\b(?:right|passenger(?:\s*side)?|rh)\b', re.IGNORECASE
)
_FRONT_RE = re.compile(r'\bfront\b', re.IGNORECASE)
_REAR_RE = re.compile(r'\b(?:rear|back)\b', re.IGNORECASE)
_INNER_RE = re.compile(r'\b(?:inner|inside|interior)\b', re.IGNORECASE)
_OUTER_RE = re.compile(r'\b(?:outer|outside)\b', re.IGNORECASE)
_UPPER_RE = re.compile(r'\b(?:upper|top)\b', re.IGNORECASE)
_LOWER_RE = re.compile(r'\b(?:lower|bottom)\b', re.IGNORECASE)

_DOOR_KEYWORDS = [
    r'\bdoor\s*(?:window|glass|handle|hinge|lock|latch|panel|trim|seal|weatherstrip|check|stop|step)\b',
    r'\bdoor\s*handle\b', r'\bdoor\s*hinge\b', r'\bdoor\s*lock\b', r'\bdoor\s*latch\b',
    r'\bdoor\s*panel\b', r'\bdoor\s*trim\b', r'\bdoor\s*mirror\b',
    r'\bwindow\s*(?:glass|regulator|motor|lift|switch)\b',
    r'\bquarter\s*glass\b', r'\bvent\s*glass\b',
]


def _is_door_part(title: str) -> bool:
    """检测是否为车门安装件（受 2-door 规则影响）"""
    for pat in _DOOR_KEYWORDS:
        if re.search(pat, title.lower()):
            return True
    return False


def _has_two_door(title: str) -> bool:
    """检测标题中是否指示 2-door 车型"""
    two_door_re = re.compile(
        r'\b2\s*-?\s*(?:door|dr)\b|\bcoupe\b'
        r'|\bregular\s*cab\b|\bsingle\s*cab\b|\bstandard\s*cab\b',
        re.IGNORECASE
    )
    return bool(two_door_re.search(title))


def from_compat(compat_rows: list) -> str | None:
    """compatibility API 通常不直接提供方位信息"""
    return None


_POSITION_SPEC_KEYS = ["Placement on Vehicle", "Position", "Location", "Side"]


def from_specs(specs: dict) -> str | None:
    """从 Item Specifics 多 key 解析方位（含 Inner/Outer/Upper/Lower）"""
    for key in _POSITION_SPEC_KEYS:
        placement = specs.get(key, "")
        if not placement:
            continue
        result = _combine_position(placement)
        if result:
            return result
    return None


def _combine_position(text: str, strip_front_rear: bool = False) -> str | None:
    """组合方位检测。
    Front+Rear 同时出现 → 'Front-Rear'（全车套件）；
    Left+Right 同时出现 → 'Both-Sides'（双侧）；
    strip_front_rear 为 True 时简化 Front/Rear 为单侧（2-door 车型）。
    """
    has_left = bool(_DIRECTION_RE.search(text))
    has_right = bool(_RIGHT_RE.search(text))
    has_front = bool(_FRONT_RE.search(text))
    has_rear = bool(_REAR_RE.search(text))
    has_inner = bool(_INNER_RE.search(text))
    has_outer = bool(_OUTER_RE.search(text))
    has_upper = bool(_UPPER_RE.search(text))
    has_lower = bool(_LOWER_RE.search(text))

    # 2-door 简化：Front/Rear → 单侧
    if strip_front_rear and (has_front or has_rear):
        if has_left:
            return "Driver-Side"
        if has_right:
            return "Passenger-Side"

    # Full set: Front+Rear → 'Front-Rear' (implies all doors, skip side detail)
    if has_front and has_rear:
        result = "Front-Rear"
        if has_inner:
            result += "-Inner"
        elif has_outer:
            result += "-Outer"
        return result

    parts = []
    if has_front:
        parts.append("Front")
    elif has_rear:
        parts.append("Rear")

    # Left + Right 同时 → 双侧
    if has_left and has_right:
        parts.append("Both-Sides")
    elif has_left:
        parts.append("Driver-Side")
    elif has_right:
        parts.append("Passenger-Side")

    if has_inner:
        parts.append("Inner")
    elif has_outer:
        parts.append("Outer")
    if has_upper:
        parts.append("Upper")
    elif has_lower:
        parts.append("Lower")

    return "-".join(parts) if parts else None


def from_title(title: str) -> str | None:
    """从标题正则提取方位（含 Inner/Outer/Upper/Lower）

    当标题仅含 Left+Right (Both-Sides) 但产品是 4pc 套件时，
    推断为 Front-Rear（四角全套）。
    """
    is_two_door = _has_two_door(title)
    strip_front_rear = is_two_door and _is_door_part(title)
    result = _combine_position(title, strip_front_rear)

    if result == "Both-Sides":
        # Left+Right 同时出现但没有 Front/Rear → 可能是 4pc 套件
        if re.search(r'\b(?:4\s*pc|4\s*piece|set\s*of\s*4|all\s*four|full\s*set|4x)\b',
                     title, re.IGNORECASE):
            return "Front-Rear"

    return result


def from_image(image_path: str) -> str | None:
    """预留：GLM-4V 视觉方位识别"""
    return None


def canonicalize(value: str) -> str | None:
    """标准化 position 值"""
    if not value:
        return None
    return _CANONICAL.get(value.lower().strip(), value)
