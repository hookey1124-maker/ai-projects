"""冲突检测 — 跨来源一致性分析"""
import json
from pathlib import Path

_RISK = json.loads(
    Path(__file__).parent.parent.joinpath("config", "field_risk_weight.json").read_text(encoding="utf-8")
)


def detect_conflicts(resolved_fields: dict) -> dict:
    """对全部字段做全局冲突汇总

    Args:
        resolved_fields: canonicalize() 输出的完整字段 dict

    Returns:
        {"total_conflicts": 2, "critical": [...], "minor": [...], ...}
    """
    critical = []
    minor = []
    informational = []

    for field_name, result in resolved_fields.items():
        if not result.get("conflict"):
            continue
        ctype = result.get("conflict_type", "")
        entry = {
            "field": field_name,
            "conflict_type": ctype,
            "conflict_score": result.get("conflict_score", 0),
            "candidates": result.get("candidates", {}),
            "selected_value": result.get("value"),
            "selected_source": result.get("source"),
        }
        if ctype == "critical_fitment_conflict":
            critical.append(entry)
        elif ctype == "minor_attribute_conflict":
            minor.append(entry)
        else:
            informational.append(entry)

    total = len(critical) + len(minor) + len(informational)

    return {
        "total_conflicts": total,
        "has_critical": len(critical) > 0,
        "critical": critical,
        "minor": minor,
        "informational": informational,
        "overall_risk_score": _calc_overall_risk(critical, minor),
    }


def compute_agreement_ratio(candidates: dict) -> float:
    """计算候选值之间的一致性比例"""
    non_none = {k: v for k, v in candidates.items() if v is not None and v != []}
    if not non_none:
        return 0.0

    from collections import Counter
    str_values = [str(v).lower() for v in non_none.values()]
    counts = Counter(str_values)
    majority_count = counts.most_common(1)[0][1]
    return round(majority_count / len(non_none), 2)


def _calc_overall_risk(critical: list, minor: list) -> int:
    """计算全局风险评分"""
    score = 0
    for c in critical:
        score += c.get("conflict_score", 0)
    for m in minor:
        score += m.get("conflict_score", 0)
    return min(score, 100)
