"""Competitor Filter — Stage 6: Hard/Soft Rule Engine + OE Fast Pass

对已抓取详情的 candidate 执行硬规则(reject)和软规则(penalty)过滤。
区分 mismatch（明确冲突→reject）vs absent（未提及→soft penalty）。
"""
import re
import json
from pathlib import Path

_DIR = Path(__file__).parent
_CONFIG = _DIR.parent / "config"

_FILTER_RULES = json.loads((_CONFIG / "filter_rules.json").read_text(encoding="utf-8"))

# 从 light_ranker 导入共用函数
from crawler.light_ranker import _find_vehicle_families, FAMILIES, _UNIVERSAL_RE

# OE 号可能的 spec key 名称
_OE_KEYS = [
    "OE/OEM Part Number", "OEM Part Number", "OE Part Number",
    "OEPartNumber", "OE/OEM Part Numbers",
]
_INTERCHANGE_KEYS = [
    "Interchange Part Number", "Cross Reference Part Number",
    "InterchangePartNumber", "Cross Reference Number",
]
_MPN_KEYS = [
    "Manufacturer Part Number", "MPN", "Mfr Part Number",
    "ManufacturerPartNumber", "Part Number",
]


def extract_oe_numbers(specs: dict) -> set[str]:
    """从 Item Specifics 中提取所有 OE/Interchange/MPN 号，返回标准化 set"""
    result = set()
    if not specs:
        return result

    for key in _OE_KEYS + _INTERCHANGE_KEYS + _MPN_KEYS:
        val = specs.get(key, "")
        if not val:
            continue
        # 拆分多重编号（逗号、分号、空格分隔）
        parts = re.split(r'[,;，；\s]+', str(val))
        for p in parts:
            p = p.strip().upper()
            # 过滤无效 token：太短、纯数字（可能是年份）、描述性文本
            if len(p) >= 4 and re.search(r'[A-Z0-9]', p):
                result.add(p)
    return result


def oe_fast_pass(anchor_specs: dict, candidate_specs: dict) -> bool:
    """检查 anchor 和 candidate 是否有共同 OE 号"""
    if not _FILTER_RULES.get("oe_fast_pass", {}).get("enabled", True):
        return False
    anchor_oe = extract_oe_numbers(anchor_specs)
    candidate_oe = extract_oe_numbers(candidate_specs)
    if not anchor_oe or not candidate_oe:
        return False
    return bool(anchor_oe & candidate_oe)


def _get_vehicle_years(cls: dict) -> set[int]:
    """从 classification 中提取年份集合"""
    vehicle = cls.get("vehicle", {}).get("value", {}) or {}
    years = vehicle.get("years", [])
    if not years:
        yr = vehicle.get("year_range", [])
        if isinstance(yr, list) and len(yr) >= 2:
            years = list(range(yr[0], yr[1] + 1))
    return set(int(y) for y in years if y)


def _get_vehicle_makes_models(cls: dict) -> tuple[set, set]:
    """返回 (makes_set, models_set)，均小写"""
    vehicle = cls.get("vehicle", {}).get("value", {}) or {}
    makes = set(m.lower() for m in (vehicle.get("makes", []) or []))
    models = set(m.lower() for m in (vehicle.get("models", []) or []))
    return makes, models


def _get_field_value(cls: dict, field: str) -> str | None:
    """安全获取 classification 字段的 value"""
    v = cls.get(field, {}).get("value")
    if v and v != "Unknown":
        return v
    return None


def apply_hard_rules(anchor_cls: dict, candidate_cls: dict,
                     skip_vehicle: bool = False,
                     anchor_text: str = "",
                     candidate_text: str = "",
                     anchor_specs: dict | None = None,
                     candidate_specs: dict | None = None) -> tuple[bool, list[str]]:
    """执行硬规则检查。

    Args:
        skip_vehicle: 为 True 时跳过 vehicle_make_model 和 year_range 检查
                      （用于 universal-fit 产品）
        anchor_text: anchor 的 title + description_text（用于语义检测）
        candidate_text: candidate 的 title + description_text（用于语义检测）
        anchor_specs: anchor 的 Item Specifics（用于 attachment_type 等检测）
        candidate_specs: candidate 的 Item Specifics（用于 attachment_type 等检测）

    Returns:
        (reject: bool, reasons: list[str])
    """
    reject = False
    reasons = []

    hard_rules = _FILTER_RULES.get("hard_rules", {})

    # 1. vehicle_make_model — universal 产品跳过
    if "vehicle_make_model" in hard_rules and not skip_vehicle:
        a_makes, a_models = _get_vehicle_makes_models(anchor_cls)
        c_makes, c_models = _get_vehicle_makes_models(candidate_cls)
        make_overlap = a_makes & c_makes
        model_overlap = a_models & c_models
        if not make_overlap or not model_overlap:
            reject = True
            reasons.append("vehicle_make_model: anchor={}/{} candidate={}/{} — no overlap".format(
                a_makes, a_models, c_makes, c_models))

    # 2. product_type
    if "product_type" in hard_rules:
        a_pt = _get_field_value(anchor_cls, "product_type")
        c_pt = _get_field_value(candidate_cls, "product_type")
        if a_pt and c_pt and a_pt.lower() != c_pt.lower():
            reject = True
            reasons.append(f"product_type mismatch: anchor={a_pt} candidate={c_pt}")

    # 3. cab — mismatch only, absent → skip
    if "cab" in hard_rules:
        a_cab = _get_field_value(anchor_cls, "cab")
        c_cab = _get_field_value(candidate_cls, "cab")
        # candidate 有 cab 且与 anchor 不同 → reject
        if a_cab and c_cab and a_cab.lower() != c_cab.lower():
            reject = True
            reasons.append(f"cab mismatch: anchor={a_cab} candidate={c_cab}")

    # 4. bed_length — mismatch only, absent → skip
    if "bed_length" in hard_rules:
        a_bl = _get_field_value(anchor_cls, "bed_length")
        c_bl = _get_field_value(candidate_cls, "bed_length")
        if a_bl and c_bl and a_bl.lower() != c_bl.lower():
            reject = True
            reasons.append(f"bed_length mismatch: anchor={a_bl} candidate={c_bl}")

    # 5. year_range — reject on zero overlap; universal 产品跳过
    if "year_range" in hard_rules and not skip_vehicle:
        a_years = _get_vehicle_years(anchor_cls)
        c_years = _get_vehicle_years(candidate_cls)
        if a_years and c_years and not (a_years & c_years):
            reject = True
            reasons.append(f"year_range zero overlap: anchor={sorted(a_years)} candidate={sorted(c_years)}")

    # 6. product_semantics — cover/overlay vs replacement → hard reject
    if "product_semantics" in hard_rules and anchor_text and candidate_text:
        a_type = _detect_semantic_type(anchor_text)
        c_type = _detect_semantic_type(candidate_text)
        if a_type and c_type and a_type != c_type:
            reject = True
            reasons.append(f"product_semantics: anchor={a_type} candidate={c_type} — fundamentally different product")

    # 7. attachment_type — adhesive vs bolt-on → hard reject
    if "attachment_type" in hard_rules:
        a_att = _get_attachment_type(anchor_specs or {})
        c_att = _get_attachment_type(candidate_specs or {})
        if c_att and not a_att:
            reject = True
            reasons.append(f"attachment_type: candidate={c_att} (anchor has no adhesive attachment)")
        elif a_att and c_att and a_att != c_att:
            reject = True
            reasons.append(f"attachment_type: anchor={a_att} candidate={c_att}")

    return reject, reasons


def apply_soft_rules(anchor_cls: dict, candidate_cls: dict) -> list[dict]:
    """执行软规则检查。
    Returns:
        [{field, penalty, reason}, ...]
    """
    soft_rules = _FILTER_RULES.get("soft_rules", {})
    penalties = []

    # position: mismatch → penalty, absent → skip (no penalty for absent position)
    if "position" in soft_rules:
        a_pos = _get_field_value(anchor_cls, "position")
        c_pos = _get_field_value(candidate_cls, "position")
        if a_pos and c_pos and a_pos.lower() != c_pos.lower():
            penalties.append({
                "field": "position",
                "penalty": soft_rules["position"].get("penalty", 15),
                "reason": f"position mismatch: anchor={a_pos} candidate={c_pos}"
            })

    # finish: mismatch → penalty
    if "finish" in soft_rules:
        a_f = _get_field_value(anchor_cls, "finish")
        c_f = _get_field_value(candidate_cls, "finish")
        if a_f and c_f and a_f.lower() != c_f.lower():
            penalties.append({
                "field": "finish",
                "penalty": soft_rules["finish"].get("penalty", 5),
                "reason": f"finish mismatch: anchor={a_f} candidate={c_f}"
            })

    # count: mismatch → penalty
    if "count" in soft_rules:
        a_cnt = _get_field_value(anchor_cls, "count")
        c_cnt = _get_field_value(candidate_cls, "count")
        if a_cnt and c_cnt and str(a_cnt).lower() != str(c_cnt).lower():
            penalties.append({
                "field": "count",
                "penalty": soft_rules["count"].get("penalty", 5),
                "reason": f"count mismatch: anchor={a_cnt} candidate={c_cnt}"
            })

    # year_partial: 年份有交集但不完全一致 → penalty
    if "year_partial" in soft_rules:
        a_years = _get_vehicle_years(anchor_cls)
        c_years = _get_vehicle_years(candidate_cls)
        if a_years and c_years and (a_years & c_years) and (a_years != c_years):
            penalties.append({
                "field": "year_partial",
                "penalty": soft_rules["year_partial"].get("penalty", 8),
                "reason": f"year partial overlap: anchor={sorted(a_years)} candidate={sorted(c_years)}"
            })

    # cab_absent: candidate 未提及 cab → tiny penalty
    if "cab_absent" in soft_rules:
        a_cab = _get_field_value(anchor_cls, "cab")
        c_cab = _get_field_value(candidate_cls, "cab")
        if a_cab and not c_cab:
            penalties.append({
                "field": "cab",
                "penalty": soft_rules["cab_absent"].get("penalty", 2),
                "reason": "cab absent in candidate"
            })

    # bed_length_absent: candidate 未提及 bed_length → tiny penalty
    if "bed_length_absent" in soft_rules:
        a_bl = _get_field_value(anchor_cls, "bed_length")
        c_bl = _get_field_value(candidate_cls, "bed_length")
        if a_bl and not c_bl:
            penalties.append({
                "field": "bed_length",
                "penalty": soft_rules["bed_length_absent"].get("penalty", 2),
                "reason": "bed_length absent in candidate"
            })

    return penalties


def seo_spam_check(title_lower: str) -> bool:
    """检测跨车型家族 SEO 刷词"""
    families = _find_vehicle_families(title_lower)
    threshold = _FILTER_RULES.get("seo_spam", {}).get("cross_family_threshold", 2)
    return len(families) >= threshold


def universal_detect(title_lower: str) -> bool:
    """检测 universal 关键词"""
    return bool(_UNIVERSAL_RE.search(title_lower))


def _get_attachment_type(specs: dict) -> str | None:
    """从 Item Specifics 提取安装方式。返回 'adhesive' / None。"""
    config = _FILTER_RULES.get("hard_rules", {}).get("attachment_type", {})
    if not config:
        return None

    for key in config.get("spec_keys", []):
        val = specs.get(key, "")
        if not val:
            continue
        val_lower = str(val).lower()
        for term in config.get("adhesive_terms", []):
            if term in val_lower:
                return "adhesive"
    return None


def _detect_semantic_type(title: str, description_text: str = "") -> str | None:
    """从标题和 description 文本检测产品语义类型。

    返回 'cover' / 'replacement' / None。
    优先检测 cover 类（更强地定义了产品类型差异）。
    """
    config = _FILTER_RULES.get("hard_rules", {}).get("product_semantics", {})
    if not config:
        return None

    text = f"{title} {description_text}".lower()

    for term in config.get("cover_terms", []):
        if term in text:
            return "cover"

    for term in config.get("replacement_terms", []):
        if term in text:
            return "replacement"

    return None


def filter_candidate(anchor_canonical: dict, candidate_product: dict,
                     candidate_canonical: dict | None = None) -> dict:
    """对单个 candidate 执行完整过滤流程。

    Args:
        anchor_canonical: classify_product(anchor) 的输出
        candidate_product: scrape_batch() 返回的原始产品数据（含 specs）
        candidate_canonical: classify_product(candidate) 的输出（可选，如未提供则跳过部分检查）

    Returns:
        {item_id, status, oe_match, hard_reject_reasons, soft_penalties,
         total_penalty, flags}
    """
    anchor_cls = anchor_canonical.get("classification", {})
    candidate_cls = (candidate_canonical or {}).get("classification", {})
    title = candidate_product.get("title", "")
    title_lower = title.lower()

    item_id = candidate_product.get("item_id", "")

    # 0. Flags — 提前检测，影响后续规则
    flags = []
    is_universal = universal_detect(title_lower)
    if is_universal:
        flags.append("universal")
    if seo_spam_check(title_lower):
        flags.append("seo_spam_cross_family")

    # 1. OE Fast Pass — 优先检查
    candidate_specs = candidate_product.get("specs", {})

    # OE fast pass 需要 anchor 的 specs（不是 classification），由调用方传入
    anchor_oe_set = extract_oe_numbers(candidate_product.get("_anchor_specs", {}))
    candidate_oe_set = extract_oe_numbers(candidate_specs)
    oe_match = bool(anchor_oe_set and candidate_oe_set and (anchor_oe_set & candidate_oe_set))

    if oe_match and _FILTER_RULES.get("oe_fast_pass", {}).get("enabled", True):
        return {
            "item_id": item_id, "status": "approved", "oe_match": True,
            "hard_reject_reasons": [], "soft_penalties": [], "total_penalty": 0,
            "flags": flags,
        }

    # 2. Hard rules — universal 产品跳过 vehicle 比对
    anchor_text = anchor_canonical.get("_title", "") + " " + anchor_canonical.get("_description_text", "")
    candidate_text = title + " " + candidate_product.get("description_text", "")
    reject, hard_reasons = apply_hard_rules(anchor_cls, candidate_cls,
                                             skip_vehicle=is_universal,
                                             anchor_text=anchor_text,
                                             candidate_text=candidate_text,
                                             anchor_specs=candidate_product.get("_anchor_specs"),
                                             candidate_specs=candidate_specs)
    if reject:
        return {
            "item_id": item_id, "status": "rejected", "oe_match": False,
            "hard_reject_reasons": hard_reasons, "soft_penalties": [], "total_penalty": 0,
            "flags": flags,
        }

    # 3. Soft rules
    soft_penalties = apply_soft_rules(anchor_cls, candidate_cls)
    total_penalty = sum(p["penalty"] for p in soft_penalties)

    # 4. 判定最终状态
    border_threshold = 15  # penalty > 15 → borderline
    if total_penalty > border_threshold:
        status = "borderline"
    else:
        status = "approved"

    return {
        "item_id": item_id,
        "status": status,
        "oe_match": False,
        "hard_reject_reasons": [],
        "soft_penalties": soft_penalties,
        "total_penalty": total_penalty,
        "flags": flags,
    }
