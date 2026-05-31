"""优先级融合 — 按字段级优先级从 candidates 中选最佳值

当多来源值冲突时，信息粒度更高的来源可覆盖静态优先级。
"""
import json
from pathlib import Path

_CONFIG_DIR = Path(__file__).parent.parent / "config"

_PRIORITY = json.loads(
    _CONFIG_DIR.joinpath("field_priority.json").read_text(encoding="utf-8")
)
_RISK = json.loads(
    _CONFIG_DIR.joinpath("field_risk_weight.json").read_text(encoding="utf-8")
)
_SPECIFICITY = json.loads(
    _CONFIG_DIR.joinpath("specificity_scores.json").read_text(encoding="utf-8")
)


def _get_priority(field: str) -> list:
    """获取某字段的来源优先级列表"""
    return _PRIORITY.get(field, ["title", "item_specifics", "image"])


def _get_risk_weight(field: str) -> int:
    """获取某字段的风险权重"""
    return _RISK.get(field, 10)


def _compute_specificity(field: str, value) -> int:
    """计算 canonical 值的信息粒度。

    粒度越高 = 语义信息越多 = 更可能准确。
    例如 position: Front-Driver-Side-Inner (4) > Front (1)
    """
    config = _SPECIFICITY.get(field)
    if not config:
        return 0

    val_str = str(value) if not isinstance(value, list) else "-".join(value)
    method = config.get("method", "word_count")

    if method == "position_components":
        return len(val_str.split("-"))
    elif method == "delimiter_components":
        delim = config.get("delimiter", "-")
        return len(val_str.split(delim))
    elif method == "word_count":
        return len(val_str.split())

    return 0


def _specificity_override(field: str, clean: dict, priority: list) -> tuple:
    """当多来源值冲突时，检查低优先级来源是否能以更高粒度覆盖。

    仅当以下条件全部满足时触发覆盖：
    1. 字段在 specificity_scores.json 中有配置
    2. 存在至少 2 个不同值（即冲突）
    3. 若配置了 low_granularity_values，top 值必须在白名单内（防信息推测）
    4. 低优先级来源的值粒度 >= 高优先级来源 + override_threshold

    Returns:
        (value, source) 如果覆盖成立，否则 (None, None)
    """
    config = _SPECIFICITY.get(field)
    if not config or len(clean) < 2:
        return None, None

    # 检查是否真的有不同值
    unique_vals = set(
        str(v).lower() if not isinstance(v, list) else tuple(sorted(v))
        for v in clean.values()
    )
    if len(unique_vals) < 2:
        return None, None  # 值都相同，没有冲突需要覆盖

    threshold = config.get("override_threshold", 1)

    # 找到静态优先级最高的有效来源
    top_src = None
    top_val = None
    for src in priority:
        if src in clean:
            top_src = src
            top_val = clean[src]
            break

    if not top_src:
        return None, None

    # 低粒度值白名单：只有 top 值在白名单内才允许信息补全
    low_granularity = config.get("low_granularity_values")
    if low_granularity:
        top_val_str = str(top_val) if not isinstance(top_val, list) else "-".join(top_val)
        if top_val_str not in low_granularity:
            return None, None  # top 值已足够精确，不做推测

    top_spec = _compute_specificity(field, top_val)

    # 检查低优先级来源中是否有粒度明显更高的值
    top_idx = priority.index(top_src) if top_src in priority else 0
    for src in priority[top_idx + 1:]:
        if src not in clean:
            continue
        val = clean[src]
        # 值与 top 相同则跳过（不是真正的冲突）
        val_key = str(val).lower() if not isinstance(val, list) else tuple(sorted(val))
        top_key = str(top_val).lower() if not isinstance(top_val, list) else tuple(sorted(top_val))
        if val_key == top_key:
            continue
        spec = _compute_specificity(field, val)
        if spec >= top_spec + threshold:
            return val, src

    return None, None


def resolve_field(field_name: str, candidates: dict) -> dict:
    """按字段级优先级从 candidates 中选出最佳值

    Args:
        field_name: 字段名 (cab/position/count/finish/...)
        candidates: {"compatibility_api": "Crew Cab", "title": "Crew Cab", ...}

    Returns:
        {"value": ..., "source": ..., "confidence": ..., "candidates": ...,
         "agreement_ratio": ..., "conflict": ..., "conflict_type": ...,
         "conflict_score": ..., "risk_weight": ...}
    """
    priority = _get_priority(field_name)
    risk_weight = _get_risk_weight(field_name)

    # 去除非 None 值并标准化
    clean = {}
    for src, val in candidates.items():
        if val is not None and val != "Unknown" and val != []:
            clean[src] = val

    if not clean:
        return {
            "field": field_name,
            "value": None,
            "confidence": 0.0,
            "source": None,
            "candidates": candidates,
            "agreement_ratio": 0.0,
            "conflict": False,
            "conflict_type": None,
            "conflict_score": 0,
            "risk_weight": risk_weight,
            "specificity_override": False,
        }

    # 统计唯一值
    unique_values = _unique_values(clean)
    non_image_sources = [s for s in clean if s != "image" and s != "ai_inference"]
    non_image_values = [clean[s] for s in non_image_sources if s in clean]

    # 一致性比例
    total_sources = len(clean)
    if total_sources == 0:
        agreement_ratio = 0.0
    elif len(unique_values) == 1:
        agreement_ratio = 1.0
    else:
        # 以 majority 为准计算
        from collections import Counter
        counts = Counter(str(v) for v in clean.values())
        majority_count = counts.most_common(1)[0][1]
        agreement_ratio = round(majority_count / total_sources, 2)

    # 冲突检测
    conflict = len(unique_values) > 1
    conflict_type = _classify_conflict_type(field_name, risk_weight, conflict)
    conflict_score = _calc_conflict_score(risk_weight, agreement_ratio, conflict)

    # 按优先级选值（冲突时允许特异性覆盖）
    selected_value = None
    selected_source = None
    specificity_override = False

    # 来源特异性覆盖：低优先级但粒度更高的值优先
    if conflict:
        override_val, override_src = _specificity_override(field_name, clean, priority)
        if override_src:
            selected_value = override_val
            selected_source = override_src
            specificity_override = True

    if selected_source is None:
        for src in priority:
            if src in clean:
                selected_value = clean[src]
                selected_source = src
                break

    if selected_value is None:
        # 没有任何优先级来源有值，取第一个非 None
        for src, val in clean.items():
            selected_value = val
            selected_source = src
            break

    # 置信度（特异性覆盖时给予适度信任）
    if specificity_override:
        confidence = 0.68  # 高于普通冲突(0.50)，低于多源一致(0.95)
    else:
        confidence = _heuristic_confidence(
            total_sources, agreement_ratio, conflict, selected_source
        )

    return {
        "field": field_name,
        "value": selected_value,
        "confidence": confidence,
        "source": selected_source,
        "candidates": candidates,
        "agreement_ratio": agreement_ratio,
        "conflict": conflict,
        "conflict_type": conflict_type,
        "conflict_score": conflict_score,
        "risk_weight": risk_weight,
        "specificity_override": specificity_override,
    }


def _unique_values(clean: dict) -> list:
    """提取标准化后的唯一值列表"""
    seen = []
    for v in clean.values():
        if isinstance(v, list):
            key = tuple(sorted(v))
        else:
            key = str(v).lower()
        if key not in seen:
            seen.append(key)
    return seen


def _classify_conflict_type(field: str, risk_weight: int, has_conflict: bool) -> str | None:
    """按字段风险权重分类冲突类型"""
    if not has_conflict:
        return None
    if risk_weight >= 30:
        return "critical_fitment_conflict"
    if risk_weight >= 10:
        return "minor_attribute_conflict"
    return "informational"


def _calc_conflict_score(risk_weight: int, agreement_ratio: float, has_conflict: bool) -> int:
    """计算冲突评分 (0-50)"""
    if not has_conflict:
        return 0
    base = risk_weight * (1 - agreement_ratio)
    return min(round(base), 50)


def _heuristic_confidence(
    num_sources: int,
    agreement_ratio: float,
    has_conflict: bool,
    selected_source: str | None,
) -> float:
    """启发式置信度计算（Phase 1 简易版，Phase 3 会校准）"""
    if num_sources == 0:
        return 0.0

    # 多来源一致
    if agreement_ratio == 1.0 and num_sources >= 2:
        return 0.95
    if agreement_ratio == 1.0 and num_sources == 1:
        src_conf = {
            "compatibility_api": 0.90,
            "item_specifics": 0.80,
            "title": 0.55,
            "image": 0.35,
            "ai_inference": 0.25,
        }
        return src_conf.get(selected_source, 0.40)

    # 有冲突，按优先级选了
    if has_conflict and selected_source == "compatibility_api":
        return 0.72
    if has_conflict and selected_source == "title":
        return 0.50

    return 0.60
