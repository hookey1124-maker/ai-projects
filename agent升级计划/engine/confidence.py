"""置信度计算 — Phase 1 启发式版本（Phase 3 用历史正确率校准）"""

SOURCE_BASE_CONFIDENCE = {
    "compatibility_api": 0.90,
    "item_specifics": 0.80,
    "title": 0.55,
    "image": 0.35,
    "ai_inference": 0.25,
}


def compute_field_confidence(
    candidates: dict,
    selected_source: str | None,
    agreement_ratio: float,
    has_conflict: bool,
) -> float:
    """计算单个字段的置信度

    规则:
    - 多来源一致 (>=2) → 0.95
    - 单来源 → 按来源可靠性
    - compatibility 优先但 specifics 冲突 → 0.72
    - title 优先但有冲突 → 0.50
    """
    non_none = {k: v for k, v in candidates.items() if v is not None and v != []}
    num_sources = len(non_none)

    if num_sources == 0:
        return 0.0

    if agreement_ratio == 1.0 and num_sources >= 2:
        return 0.95

    if agreement_ratio == 1.0 and num_sources == 1:
        return SOURCE_BASE_CONFIDENCE.get(selected_source, 0.40)

    if has_conflict and selected_source == "compatibility_api":
        return 0.72

    if has_conflict:
        return max(0.30, SOURCE_BASE_CONFIDENCE.get(selected_source, 0.40) - 0.20)

    return 0.60


def compute_overall_confidence(resolved_fields: dict) -> float:
    """计算全局置信度（所有字段置信度的加权平均）"""
    total_weight = 0
    weighted_sum = 0.0

    for field_name, result in resolved_fields.items():
        conf = result.get("confidence", 0.0)
        risk = result.get("risk_weight", 10)
        weighted_sum += conf * risk
        total_weight += risk

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 2)
