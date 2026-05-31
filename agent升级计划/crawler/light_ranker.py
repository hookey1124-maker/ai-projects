"""Light Ranker — Stage 3 title 级别打分（不抓详情页）

纯 title 级别 scoring：
  vehicle match → +30
  product_type keyword → +25
  cab hint → +15
  position hint → +10
  seo_spam (cross-family) → -10, flag
  universal → flag

只 ranking，不做 reject。所有 reject 决策推迟到 Stage 6（有完整 canonical 后）。
"""
import re
import json
from pathlib import Path

_ONTOLOGY = json.loads(
    Path(__file__).parent.parent.joinpath("config", "vehicle_ontology.json").read_text(encoding="utf-8")
)
_UNIVERSAL_PATTERNS = [
    r'\buniversal\b', r'\bfits\s*most\b', r'\bfits\s*all\b',
    r'\buniversal\s*fit\b', r'\bmulti[\s-]fit\b',
]
_UNIVERSAL_RE = re.compile('|'.join(_UNIVERSAL_PATTERNS), re.IGNORECASE)


def _get_ontology_families() -> dict:
    """展开 ontology 为 {family_name: [(make, model), ...]}"""
    families = {}
    for family_name, data in _ONTOLOGY.get("families", {}).items():
        entries = []
        for make in data.get("makes", []):
            for model in data.get("models", []):
                entries.append((make.lower(), model.lower()))
        families[family_name] = entries
    return families


FAMILIES = _get_ontology_families()


def _find_vehicle_families(title_lower: str) -> set:
    """找出标题属于哪些 ontology family"""
    found = set()
    for fam_name, entries in FAMILIES.items():
        for make, model in entries:
            if make in title_lower and model in title_lower:
                found.add(fam_name)
                break
    return found


def _product_type_keyword_match(title_lower: str, product_type: str) -> bool:
    """标题是否包含产品类型关键词"""
    if not product_type:
        return False
    keywords = product_type.lower().split()
    # 至少有一个关键词在标题中
    return any(kw in title_lower for kw in keywords)


def _cab_hint_match(title_lower: str, cab: str) -> bool:
    """标题中是否有 cab 类型的暗示"""
    if not cab or cab == "Unknown":
        return False
    cab_keywords = {
        "Crew Cab": ["crew cab", "crewcab", "crew max", "crewmax", "supercrew"],
        "Extended Cab": ["extended cab", "ext cab", "double cab", "quad cab",
                         "super cab", "supercab", "access cab", "king cab"],
        "Regular Cab": ["regular cab", "single cab", "standard cab"],
    }
    for kw in cab_keywords.get(cab, []):
        if kw in title_lower:
            return True
    return False


def _position_hint_match(title_lower: str, position: str) -> bool:
    """标题中是否有方位的暗示"""
    if not position or position == "Unknown":
        return False
    pos_keywords = {
        "Front-Driver-Side": ["front left", "front driver", "lh", "front lh"],
        "Front-Passenger-Side": ["front right", "front passenger", "rh", "front rh"],
        "Rear-Driver-Side": ["rear left", "rear driver", "rear lh"],
        "Rear-Passenger-Side": ["rear right", "rear passenger", "rear rh"],
        "Front": ["front"],
        "Rear": ["rear", "back"],
        "Driver-Side": ["driver side", "left", "lh"],
        "Passenger-Side": ["passenger side", "right", "rh"],
    }
    for kw in pos_keywords.get(position, []):
        if kw in title_lower:
            return True
    return False


def rank_candidates(candidates: list[dict], anchor_canonical: dict) -> list[dict]:
    """对候选列表做 title 级别打分 + 排序

    Args:
        candidates: [{item_id, title, url}, ...]
        anchor_canonical: classify_product() 的输出

    Returns:
        带 score 和 flags 的排序后列表
    """
    vehicle_info = anchor_canonical.get("classification", {}).get("vehicle", {})
    vehicle_value = vehicle_info.get("value") or {}
    anchor_makes = [m.lower() for m in vehicle_value.get("makes", [])]
    anchor_models = [m.lower() for m in vehicle_value.get("models", [])]

    cab_info = anchor_canonical.get("classification", {}).get("cab", {})
    anchor_cab = cab_info.get("value") if cab_info else None

    pos_info = anchor_canonical.get("classification", {}).get("position", {})
    anchor_position = pos_info.get("value") if pos_info else None

    pt_info = anchor_canonical.get("classification", {}).get("product_type", {})
    anchor_product_type = pt_info.get("value") if pt_info else None

    ranked = []
    for c in candidates:
        title_lower = c.get("title", "").lower()
        score = 0
        flags = []

        # vehicle family match
        candidate_families = _find_vehicle_families(title_lower)
        anchor_family_set = set()
        for fam_name, entries in FAMILIES.items():
            for make, model in entries:
                if make in anchor_makes and model in anchor_models:
                    anchor_family_set.add(fam_name)

        if candidate_families & anchor_family_set:
            score += 30
        elif any(make in title_lower for make in anchor_makes):
            score += 15  # make 匹配但 model 不匹配

        # product_type keyword
        if anchor_product_type and _product_type_keyword_match(title_lower, anchor_product_type):
            score += 25

        # cab hint
        if anchor_cab and _cab_hint_match(title_lower, anchor_cab):
            score += 15

        # position hint
        if anchor_position and _position_hint_match(title_lower, anchor_position):
            score += 10

        # universal detect
        if _UNIVERSAL_RE.search(title_lower):
            flags.append("universal")

        # seo spam detect (cross-family)
        if len(candidate_families) >= 2:
            score -= 10
            flags.append("seo_spam_cross_family")

        c["light_score"] = score
        c["light_flags"] = flags
        c["light_families"] = list(candidate_families)
        ranked.append(c)

    ranked.sort(key=lambda x: x["light_score"], reverse=True)
    return ranked
