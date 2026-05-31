"""文案后自动验证 — 标题/卖点/规则检查"""
import json
import re
from pathlib import Path

# ── 品牌分类 ─────────────────────────────────────────
# 汽车品牌：允许出现在 fits/for 等适配声明中
AUTO_BRANDS = [
    "Ford", "BMW", "Toyota", "Honda", "Chevrolet", "Mercedes", "Audi", "Volkswagen",
    "Nissan", "Porsche", "Ferrari", "Lamborghini", "Maserati", "Jaguar", "Land Rover",
    "Lexus", "Acura", "Infiniti", "Cadillac", "Lincoln", "Buick", "GMC", "Dodge",
    "Chrysler", "Jeep", "Ram", "Subaru", "Mazda", "Hyundai", "Kia", "Volvo",
    "Bentley", "Rolls Royce", "Aston Martin", "McLaren", "Tesla", "Rivian",
    "Chevy", "VW", "Benz", "Mini", "Smart", "Scion", "Saturn", "Pontiac",
    "Oldsmobile", "Mercury", "Plymouth", "Eagle", "Hummer", "Saab", "Suzuki",
    "Isuzu", "Daewoo", "Fiat", "Alfa Romeo", "Lancia", "Peugeot", "Citroen",
    "Renault", "Opel", "Seat", "Skoda", "Dacia",
]

# OEM 厂商集团名／零部件品牌：高风险，无条件拒绝（含上下文豁免也不行）
HIGH_RISK_OEM = [
    # ── 厂商集团 ──
    "GM",           # General Motors 集团
    "FCA",          # Fiat Chrysler Automobiles 集团
    "Daimler",      # Daimler AG
    "Stellantis",   # Stellantis 集团
    # ── 原厂件品牌 ──
    "MOPAR",        # Chrysler 原厂件
    "ACDelco",      # GM 原厂件
    "Motorcraft",   # Ford 原厂件
    "FoMoCo",       # Ford Motor Company 内部标识
    # ── OE 供应商 ──
    "Denso",        # 丰田系 OE 供应商
    "Bosch",        # 德国 OE 供应商
    "Valeo",        # 法国 OE 供应商
    "Hella",        # 德国车灯/电子
    "Delphi",       # 原 GM 子公司/OE 供应商
    "NGK",          # 日本火花塞/OE 供应商
    "Brembo",       # 意大利刹车
    "Bilstein",     # 德国避震
    "KYB",          # 日本避震
    "Moog",         # 美国底盘件
    "Timken",       # 美国轴承
    "SKF",          # 瑞典轴承
    "Mahle",        # 德国滤清器/活塞
    "Gates",        # 美国皮带/软管
    "Dayco",        # 美国皮带
    "Fel-Pro",      # 美国密封垫
    "TRW",          # 美国底盘/刹车
    "Cardone",      # 美国再制造件
]

# 适配声明前缀
COMPAT_PREFIX = r"(?:fits?\s+|for\s+|compatible\s+with\s+|replaces?\s+|replacement\s+for\s+|designed\s+for\s+|engineered\s+for\s+)"


def _check_brands(text: str) -> tuple[list, list]:
    """检查文本中的品牌词，返回 (auto_brand_hits, high_risk_hits)"""
    auto_hits = []
    high_risk_hits = []

    # 高风险词：无条件拒绝
    for word in HIGH_RISK_OEM:
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            high_risk_hits.append(word)

    # 汽车品牌：需要适配声明前缀
    for brand in AUTO_BRANDS:
        for match in re.finditer(rf"\b{re.escape(brand)}\b", text, re.IGNORECASE):
            prefix = text[:match.start()]
            if not re.search(COMPAT_PREFIX, prefix, re.IGNORECASE):
                auto_hits.append(brand)

    return auto_hits, high_risk_hits


def validate_title(title: str) -> dict:
    """验证 eBay 标题规则"""
    issues = []

    length = len(title)
    length_ok = length <= 80
    if not length_ok:
        issues.append(f"标题 {length} 字符，超过 80 字符限制（超出 {length - 80}）")

    auto_hits, high_risk_hits = _check_brands(title)
    found_logos = auto_hits + high_risk_hits
    no_oem_logo = len(found_logos) == 0
    if not no_oem_logo:
        parts = []
        if auto_hits:
            parts.append(f"品牌缺少适配前缀: {auto_hits}")
        if high_risk_hits:
            parts.append(f"禁止的 OEM 厂商名: {high_risk_hits}")
        issues.append("; ".join(parts))

    # 商标符号检查
    trademark_chars = ["®", "™", "©"]
    found_tm = [c for c in trademark_chars if c in title]
    no_trademark = len(found_tm) == 0
    if not no_trademark:
        issues.append(f"标题含商标符号: {found_tm}")

    return {
        "length": length,
        "length_ok": length_ok,
        "no_oem_logo": no_oem_logo,
        "no_trademark": no_trademark,
        "passed": length_ok and no_oem_logo and no_trademark,
        "issues": issues,
    }


def validate_bullet_points(bullets: list) -> dict:
    """验证卖点列表"""
    issues = []
    count = len(bullets)
    count_ok = count >= 5
    if not count_ok:
        issues.append(f"卖点仅 {count} 条，要求 >= 5")

    short_bullets = [i for i, b in enumerate(bullets, 1) if len(b) < 10]
    min_length_ok = len(short_bullets) == 0
    if not min_length_ok:
        issues.append(f"卖点 #{short_bullets} 过短（< 10 字符）")

    # 禁止词
    forbidden = ["100%", "perfect", "guaranteed fit", "no issues", "never used"]
    has_forbidden = False
    for b in bullets:
        for fw in forbidden:
            if fw.lower() in b.lower():
                issues.append(f"卖点含禁止词: '{fw}'")
                has_forbidden = True

    # 品牌检查（逐条，汇总所有命中）
    all_auto = set()
    all_high_risk = set()
    for b in bullets:
        auto_hits, high_risk_hits = _check_brands(b)
        all_auto.update(auto_hits)
        all_high_risk.update(high_risk_hits)

    no_oem_brand = len(all_auto) == 0 and len(all_high_risk) == 0
    if not no_oem_brand:
        parts = []
        if all_auto:
            parts.append(f"品牌缺少适配前缀: {list(all_auto)}")
        if all_high_risk:
            parts.append(f"禁止的 OEM 厂商名: {list(all_high_risk)}")
        issues.append("; ".join(parts))

    return {
        "count": count,
        "count_ok": count_ok,
        "min_length_ok": min_length_ok,
        "no_forbidden_words": not has_forbidden,
        "no_oem_brand": no_oem_brand,
        "passed": count_ok and min_length_ok and not has_forbidden and no_oem_brand,
        "issues": issues,
    }


def validate_listing(title: str, bullets: list) -> dict:
    """完整文案验证"""
    title_result = validate_title(title)
    bullets_result = validate_bullet_points(bullets)

    all_passed = title_result["passed"] and bullets_result["passed"]

    if all_passed:
        action, reason = "accept", "文案验证通过"
    elif not title_result["passed"] and bullets_result["passed"]:
        if not title_result["length_ok"]:
            action, reason = "reject", f"标题过长({title_result['length']}字符)，需精简后重写"
        else:
            action, reason = "reject", f"标题含禁止内容: {title_result['issues']}"
    elif not bullets_result["passed"]:
        action, reason = "retry", f"卖点不足: {bullets_result['issues']}"
    else:
        action, reason = "reject", f"多项不通过: title={title_result['issues']}, bullets={bullets_result['issues']}"

    return {
        "title": title_result,
        "bullets": bullets_result,
        "passed": all_passed,
        "action": action,
        "reason": reason,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python listing_validator.py <listing.json>")
        print("  listing.json 格式: {\"title\": \"...\", \"bullets\": [\"...\", ...]}")
        sys.exit(1)

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = validate_listing(data.get("title", ""), data.get("bullets", []))
    print(json.dumps(result, ensure_ascii=False, indent=2))
