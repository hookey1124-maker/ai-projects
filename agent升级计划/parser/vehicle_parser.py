"""vehicle 字段提取 — Year / Make / Model 从 compatibility API + 标题"""
import re

_VEHICLE_MAKES = [
    "Ford", "Chevy", "Chevrolet", "GMC", "Dodge", "Ram", "Jeep", "Cadillac",
    "Toyota", "Honda", "Nissan", "Mazda", "BMW", "Mercedes", "Audi", "Volkswagen",
    "Subaru", "Hyundai", "Kia", "Volvo", "Tesla", "Rivian", "Chrysler", "Buick",
    "Lincoln", "Lexus", "Acura", "Infiniti", "Porsche", "Land Rover", "Jaguar",
]

_YEAR_PATTERNS = [
    re.compile(r'(?:For|Fit(?:s)?|Compatible\s+(?:with\s+)?)\s*(\d{2,4})\s*[-–]\s*(\d{2,4})', re.IGNORECASE),
    re.compile(r'\b(\d{4})\s*[-–]\s*(\d{2,4})\b'),
]


def _fix_year(y: int) -> int:
    """修正两位数年份"""
    if y < 100:
        return y + 2000 if y < 50 else y + 1900
    return y


def from_compat(compat_rows: list) -> dict | None:
    """从 compatibility API 提取车型信息"""
    if not compat_rows:
        return None

    years = set()
    makes = set()
    models = set()
    trims = set()
    engines = set()

    for row in compat_rows:
        year_str = row.get("Year", "")
        if year_str:
            for part in re.split(r'[,;\s]+', str(year_str)):
                part = part.strip()
                if part.isdigit():
                    years.add(int(part))

        make = row.get("Make", "")
        if make:
            makes.add(make.strip())

        model = row.get("Model", "")
        if model:
            models.add(model.strip())

        trim = row.get("Trim", "")
        if trim:
            trims.add(trim.strip())

        engine = row.get("Engine", "")
        if engine:
            engines.add(engine.strip())

    if not makes:
        return None

    year_min = min(years) if years else None
    year_max = max(years) if years else None

    return {
        "year_start": year_min,
        "year_end": year_max,
        "year_range": f"{year_min}-{year_max}" if year_min else None,
        "makes": sorted(makes),
        "models": sorted(models),
        "trims": sorted(trims),
        "engines": sorted(engines),
    }


def from_specs(specs: dict) -> dict | None:
    """从 Item Specifics 提取车型（部分卖家填写 Compatible Make/Model）"""
    make = specs.get("Compatible Make", "") or specs.get("Make", "")
    model = specs.get("Model", "")
    year = specs.get("Compatible Year", "")

    if not make:
        return None

    return {
        "year_range": year if year else None,
        "makes": [m.strip() for m in make.split(",") if m.strip()],
        "models": [m.strip() for m in model.split(",") if m.strip()] if model else [],
        "trims": [],
        "engines": [],
    }


def from_title(title: str) -> dict | None:
    """从标题提取车型品牌+型号"""
    found = []
    title_lower = title.lower()
    for make in _VEHICLE_MAKES:
        if make.lower() in title_lower:
            pat = rf'\b{re.escape(make)}\s+([A-Z][a-zA-Z0-9\-\.]+(?:\s+[A-Z][a-zA-Z0-9\-\.]+)?)'
            m = re.search(pat, title, re.IGNORECASE)
            if m and not re.match(r'^\d{2,4}$', m.group(1)):
                found.append({"make": make, "model": m.group(1).strip()})
            else:
                found.append({"make": make, "model": None})

    if not found:
        return None

    # 提取年份
    year_start, year_end = None, None
    for pat in _YEAR_PATTERNS:
        m = pat.search(title)
        if m:
            y1 = _fix_year(int(m.group(1)))
            y2 = _fix_year(int(m.group(2)))
            year_start = min(y1, y2)
            year_end = max(y1, y2)
            break

    makes = sorted(set(f["make"] for f in found))
    models = sorted(set(f["model"] for f in found if f["model"]))

    return {
        "year_start": year_start,
        "year_end": year_end,
        "year_range": f"{year_start}-{year_end}" if year_start else None,
        "makes": makes,
        "models": models,
        "trims": [],
        "engines": [],
    }


def from_image(image_path: str) -> dict | None:
    """预留：GLM-4V 视觉车型识别"""
    return None
