"""Similarity Engine — Stage 7: 加权字段重叠评分

对通过 hard/soft filter 的 candidate 做加权字段重叠评分，
按品类差异化阈值分 approved / borderline。
"""
import json
from pathlib import Path

_DIR = Path(__file__).parent
_CONFIG = _DIR.parent / "config"

_WEIGHTS = json.loads((_CONFIG / "similarity_weights.json").read_text(encoding="utf-8"))
_THRESHOLDS = json.loads((_CONFIG / "category_thresholds.json").read_text(encoding="utf-8"))


def _get_field_value(cls: dict, field: str) -> str | None:
    v = cls.get(field, {}).get("value")
    if v and v != "Unknown":
        return v
    return None


def _compute_field_coverage(cls: dict) -> float:
    """候选产品的字段覆盖率：8 个加权字段中有值的比例。

    Unknown 过多 → coverage 低 → similarity 降权，防止虚高。
    """
    weighted_fields = ["product_type", "cab", "position", "count", "finish", "bed_length"]
    known = 0
    for f in weighted_fields:
        if _get_field_value(cls, f):
            known += 1
    # vehicle 拆为 make_model + year_overlap 两项
    vehicle = cls.get("vehicle", {}).get("value", {}) or {}
    if vehicle.get("makes") or vehicle.get("models"):
        known += 1
    if vehicle.get("years") or vehicle.get("year_range"):
        known += 1
    return known / 8


def _get_vehicle_sets(cls: dict) -> tuple[set, set, set]:
    """返回 (makes_set, models_set, years_set)，均小写归一化"""
    vehicle = cls.get("vehicle", {}).get("value", {}) or {}
    makes = set(m.lower() for m in (vehicle.get("makes", []) or []))
    models = set(m.lower() for m in (vehicle.get("models", []) or []))
    years_raw = vehicle.get("years", [])
    if not years_raw:
        yr = vehicle.get("year_range", [])
        if isinstance(yr, list) and len(yr) >= 2:
            years_raw = list(range(yr[0], yr[1] + 1))
    years = set(int(y) for y in years_raw if y)
    return makes, models, years


def compute_similarity(anchor_cls: dict, candidate_cls: dict,
                       soft_penalties: list[dict] = None) -> dict:
    """计算锚点与候选产品的加权字段重叠相似度。

    Returns:
        {similarity: float, raw_score: float, max_score: 100, breakdown: dict}
    """
    breakdown = {}
    a_makes, a_models, a_years = _get_vehicle_sets(anchor_cls)
    c_makes, c_models, c_years = _get_vehicle_sets(candidate_cls)

    # 1. vehicle_make_model (weight from config)
    w_mm = _WEIGHTS.get("vehicle_make_model", 25)
    if a_makes & c_makes and a_models & c_models:
        breakdown["vehicle_make_model"] = w_mm
    elif a_makes & c_makes:
        breakdown["vehicle_make_model"] = int(w_mm * 0.6)  # make only
    else:
        breakdown["vehicle_make_model"] = 0

    # 2. vehicle_year_overlap (Jaccard)
    w_year = _WEIGHTS.get("vehicle_year_overlap", 15)
    if a_years and c_years:
        intersection = a_years & c_years
        union = a_years | c_years
        jaccard = len(intersection) / len(union) if union else 1.0
        breakdown["vehicle_year_overlap"] = round(w_year * jaccard, 1)
    else:
        breakdown["vehicle_year_overlap"] = int(w_year * 0.5)  # 一方缺失

    # 3. product_type
    w_pt = _WEIGHTS.get("product_type", 25)
    a_pt = _get_field_value(anchor_cls, "product_type")
    c_pt = _get_field_value(candidate_cls, "product_type")
    if a_pt and c_pt and a_pt.lower() == c_pt.lower():
        breakdown["product_type"] = w_pt
    else:
        breakdown["product_type"] = 0

    # 4. cab
    w_cab = _WEIGHTS.get("cab", 15)
    a_cab = _get_field_value(anchor_cls, "cab")
    c_cab = _get_field_value(candidate_cls, "cab")
    if a_cab and c_cab and a_cab.lower() == c_cab.lower():
        breakdown["cab"] = w_cab
    elif a_cab and not c_cab:
        breakdown["cab"] = int(w_cab * 0.67)  # absent
    else:
        breakdown["cab"] = 0

    # 5. position
    w_pos = _WEIGHTS.get("position", 10)
    a_pos = _get_field_value(anchor_cls, "position")
    c_pos = _get_field_value(candidate_cls, "position")
    if a_pos and c_pos and a_pos.lower() == c_pos.lower():
        breakdown["position"] = w_pos
    elif a_pos and not c_pos:
        breakdown["position"] = int(w_pos * 0.5)  # absent
    else:
        breakdown["position"] = 0

    # 6. count
    w_cnt = _WEIGHTS.get("count", 5)
    a_cnt = _get_field_value(anchor_cls, "count")
    c_cnt = _get_field_value(candidate_cls, "count")
    if a_cnt and c_cnt and str(a_cnt) == str(c_cnt):
        breakdown["count"] = w_cnt
    else:
        breakdown["count"] = 0

    # 7. finish
    w_fin = _WEIGHTS.get("finish", 3)
    a_f = _get_field_value(anchor_cls, "finish")
    c_f = _get_field_value(candidate_cls, "finish")
    if a_f and c_f and a_f.lower() == c_f.lower():
        breakdown["finish"] = w_fin
    elif a_f and not c_f:
        breakdown["finish"] = int(w_fin * 0.33)  # absent
    else:
        breakdown["finish"] = 0

    # 8. bed_length
    w_bl = _WEIGHTS.get("bed_length", 2)
    a_bl = _get_field_value(anchor_cls, "bed_length")
    c_bl = _get_field_value(candidate_cls, "bed_length")
    if a_bl and c_bl and a_bl.lower() == c_bl.lower():
        breakdown["bed_length"] = w_bl
    elif a_bl and not c_bl:
        breakdown["bed_length"] = int(w_bl * 0.5)  # absent
    else:
        breakdown["bed_length"] = 0

    raw_score = sum(breakdown.values())
    max_score = sum(_WEIGHTS.values())

    # 减去 soft penalties
    penalty_total = sum(p.get("penalty", 0) for p in (soft_penalties or []))
    raw_score = max(0, raw_score - penalty_total)

    similarity = raw_score / max_score if max_score > 0 else 0.0

    # 字段覆盖率降权：candidate Unknown 过多 → similarity 虚高 → 降权
    coverage = _compute_field_coverage(candidate_cls)
    adjusted = similarity * (0.7 + 0.3 * coverage)
    if coverage < 0.45:
        adjusted = min(adjusted, 0.72)

    return {
        "similarity": round(adjusted, 3),
        "raw_similarity": round(similarity, 3),
        "raw_score": round(raw_score, 1),
        "max_score": max_score,
        "coverage": round(coverage, 2),
        "breakdown": breakdown,
        "penalties": soft_penalties or [],
    }


def classify_result(similarity: float, product_type: str) -> str:
    """按品类阈值判定最终状态"""
    threshold = _THRESHOLDS.get(product_type, _THRESHOLDS.get("default", 0.75))
    if similarity >= threshold:
        return "approved"
    return "borderline"


def score_candidates(anchor_canonical: dict, candidates: list[dict],
                     filter_results: list[dict],
                     anchor_img: str = None, **kwargs) -> list[dict]:
    """批量入口：对通过 filter 的 candidates 逐一评分并排序。

    Args:
        anchor_canonical: classify_product(anchor) 输出
        candidates: [{item_id, title, url, ...}, ...] 候选产品列表（须含 classification）
        filter_results: filter_candidate() 的结果列表（按 item_id 匹配）
        anchor_img: 锚定产品主图路径（用于 borderline 视觉兜底验证）

    Returns:
        带 similarity/breakdown/final_status 的排序后列表
    """
    anchor_cls = anchor_canonical.get("classification", {})
    product_type = _get_field_value(anchor_cls, "product_type") or ""

    # 建立 filter_results 索引
    filter_map = {fr["item_id"]: fr for fr in filter_results}

    results = []
    for c in candidates:
        item_id = c.get("item_id", "")
        fr = filter_map.get(item_id, {})

        # 已被 reject 的跳过评分
        if fr.get("status") == "rejected":
            c["similarity"] = 0.0
            c["breakdown"] = {}
            c["final_status"] = "rejected"
            c["filter_result"] = fr
            results.append(c)
            continue

        # OE fast pass 的给满分
        if fr.get("oe_match"):
            c["similarity"] = 1.0
            c["breakdown"] = {"oe_fast_pass": 100}
            c["final_status"] = "approved"
            c["filter_result"] = fr
            results.append(c)
            continue

        candidate_cls = c.get("classification", {})
        soft_penalties = fr.get("soft_penalties", [])

        score_result = compute_similarity(anchor_cls, candidate_cls, soft_penalties)
        final_status = classify_result(score_result["similarity"], product_type)

        c["similarity"] = score_result["similarity"]
        c["breakdown"] = score_result["breakdown"]
        c["final_status"] = final_status
        c["filter_result"] = fr
        c["_product"] = c  # 保留原始产品数据给 vision diff 用
        results.append(c)

    results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

    # ── Vision Diff 兜底：borderline 候选视觉对比 ──
    if anchor_img:
        try:
            from vision.compare import vision_filter
            results = vision_filter(anchor_img, results, threshold=0.78)
        except ImportError:
            pass

    # ── SQLite 入库（如果提供了 db 实例）──
    db = kwargs.get("db")
    if db and anchor_canonical.get("_own_product_id"):
        _flush_to_db(db, anchor_canonical["_own_product_id"], results)

    return results


def _flush_to_db(db, own_product_id: str, results: list[dict]) -> None:
    """将 score_candidates 结果批量写入 market.db。"""
    for c in results:
        item_id = c.get("item_id", "")
        if not item_id:
            continue
        prod = c.get("_product", {})
        if prod:
            from crawler.database import _parse_price
            db.upsert_competitor(
                item_id=item_id,
                title=prod.get("title", ""),
                url=prod.get("url", ""),
                price=_parse_price(prod.get("price", "")),
                seller=prod.get("seller", ""),
                classification=c.get("classification"),
                image_path=prod.get("image_path", ""),
            )
        db.link_competitor(
            own_product_id=own_product_id,
            competitor_id=item_id,
            similarity=c.get("similarity"),
            final_status=c.get("final_status", "pending"),
            raw_score=c.get("raw_score") if isinstance(c.get("raw_score"), (int, float)) else None,
            max_score=100,
            coverage=c.get("coverage"),
            breakdown=c.get("breakdown"),
            filter_result=c.get("filter_result"),
            vision_diff=c.get("_vision_diff"),
            hard_reject_reason=c.get("filter_result", {}).get("reason"),
        )
