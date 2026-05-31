"""链接归类 → 母文件 → 队列调度"""
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime

# 产品归档根目录
ARCHIVE_ROOT = Path(r"C:\Users\Administrator\Desktop\AI项目\产品卖点主图和信息生成")
QUEUE_DIR = Path(__file__).parent
PENDING_FILE = QUEUE_DIR / "pending.json"
DONE_FILE = QUEUE_DIR / "done.json"
FAILED_FILE = QUEUE_DIR / "failed.json"

# ── 车型识别词典 ──
MAKE_PATTERNS = [
    "Chevy|Chevrolet", "Ford", "Toyota", "Honda", "BMW", "Mercedes",
    "Audi", "Nissan", "Dodge", "Jeep", "GMC", "Ram", "Subaru", "Mazda",
    "Hyundai", "Kia", "Volkswagen|VW", "Volvo", "Porsche", "Lexus",
    "Acura", "Infiniti", "Cadillac", "Lincoln", "Buick", "Chrysler",
    "Pontiac", "Oldsmobile", "Plymouth", "Saturn", "Mercury", "Scion",
    "Suzuki", "Mitsubishi", "Land Rover", "Jaguar", "Ferrari", "Tesla",
    "Rivian", "Mini", "Fiat", "Alfa Romeo", "Maserati", "Bentley",
]

MODEL_PATTERNS = {
    # Chevy
    "Nova": ["Chevy", "Chevrolet"],
    "Camaro": ["Chevy", "Chevrolet"],
    "Corvette": ["Chevy", "Chevrolet"],
    "Silverado": ["Chevy", "Chevrolet"],
    "Tahoe": ["Chevy", "Chevrolet"],
    "Suburban": ["Chevy", "Chevrolet"],
    "Impala": ["Chevy", "Chevrolet"],
    "Malibu": ["Chevy", "Chevrolet"],
    "Chevelle": ["Chevy", "Chevrolet"],
    "Blazer": ["Chevy", "Chevrolet"],
    "C10": ["Chevy", "Chevrolet"],
    "K10": ["Chevy", "Chevrolet"],
    "C20": ["Chevy", "Chevrolet"],
    # Ford
    "Mustang": ["Ford"],
    "F-150": ["Ford"],
    "F150": ["Ford"],
    "F-250": ["Ford"],
    "F250": ["Ford"],
    "F-350": ["Ford"],
    "F350": ["Ford"],
    "Bronco": ["Ford"],
    "Explorer": ["Ford"],
    "Ranger": ["Ford"],
    "Focus": ["Ford"],
    "Fusion": ["Ford"],
    "Escape": ["Ford"],
    # Toyota
    "Camry": ["Toyota"],
    "Corolla": ["Toyota"],
    "Tacoma": ["Toyota"],
    "Tundra": ["Toyota"],
    "RAV4": ["Toyota"],
    "4Runner": ["Toyota"],
    "Highlander": ["Toyota"],
    # Honda
    "Civic": ["Honda"],
    "Accord": ["Honda"],
    "CR-V": ["Honda"],
    "Pilot": ["Honda"],
    "Odyssey": ["Honda"],
    # BMW
    "3 Series": ["BMW"],
    "5 Series": ["BMW"],
    "X3": ["BMW"],
    "X5": ["BMW"],
    # Dodge/Ram
    "Ram 1500": ["Ram", "Dodge"],
    "Ram 2500": ["Ram", "Dodge"],
    "Ram 3500": ["Ram", "Dodge"],
    "Charger": ["Dodge"],
    "Challenger": ["Dodge"],
    "Durango": ["Dodge"],
    # Jeep
    "Wrangler": ["Jeep"],
    "Silverado": ["Chevy", "Chevrolet"],
    "Sierra": ["GMC"],
    "Tahoe": ["Chevy", "Chevrolet"],
    "Suburban": ["Chevy", "Chevrolet"],
    "Yukon": ["GMC"],
    "Denali": ["GMC"],
    "Escalade": ["Cadillac"],
    "Avalanche": ["Chevy", "Chevrolet"],
    "Colorado": ["Chevy", "Chevrolet"],
    "Canyon": ["GMC"],
    "Express": ["Chevy", "Chevrolet"],
    "Savana": ["GMC"],
    "Super Duty": ["Ford"],
    "Excursion": ["Ford"],
    "Grand Cherokee": ["Jeep"],
    "Durango": ["Dodge"],
    "Altima": ["Nissan"],
    "Sentra": ["Nissan"],
    "Maxima": ["Nissan"],
    # GMC
    "Sierra": ["GMC"],
    "Yukon": ["GMC"],
    # Subaru
    "Outback": ["Subaru"],
    "Forester": ["Subaru"],
    "WRX": ["Subaru"],
    # Pontiac
    "Firebird": ["Pontiac"],
    "GTO": ["Pontiac"],
    "Trans Am": ["Pontiac"],
    # Others
    "Wrangler": ["Jeep"],
    "Cherokee": ["Jeep"],
    "Grand Cherokee": ["Jeep"],
}

PRODUCT_CATEGORIES = {
    "Door-Handle": ["door handle", "exterior door", "outside door", "outer door", "door exterior", "door outside"],
    "Door-Hinge": ["door hinge", "hinge"],
    "Door-Window-Glass": ["door window glass", "door glass", "window glass"],
    "Door-Handle-Cover": ["door handle cover", "handle cover trim"],
    "Mirror-Cover": ["mirror cover", "mirror shell", "rearview mirror shell"],
    "Brake-Pad": ["brake pad", "brake pads", "brake shoe"],
    "Brake-Rotor": ["brake rotor", "brake disc", "rotor"],
    "Control-Arm": ["control arm", "suspension arm"],
    "Shock": ["shock", "strut"],
    "Bumper": ["bumper", "bumper cover"],
    "Fender": ["fender", "quarter panel"],
    "Headlight": ["headlight", "head light", "headlamp"],
    "Tail-Light": ["tail light", "taillight", "rear light"],
    "Mirror": ["mirror", "side mirror"],
    "Radiator": ["radiator"],
    "Alternator": ["alternator"],
    "Starter": ["starter"],
    "Fuel Pump": ["fuel pump"],
    "Water Pump": ["water pump"],
    "Window Regulator": ["window regulator"],
    "Wheel Bearing": ["wheel bearing", "hub bearing"],
    "Ball Joint": ["ball joint"],
    "Tie Rod": ["tie rod"],
    "Sway Bar": ["sway bar"],
    "Grille": ["grille", "grill"],
    "Hood": ["hood"],
    "Door": ["door", "door panel", "door shell"],
    "Trunk": ["trunk", "trunk lid"],
    "Exhaust": ["exhaust", "muffler"],
    "Catalytic Converter": ["catalytic converter"],
    "Ignition Coil": ["ignition coil"],
    "Spark Plug": ["spark plug"],
    "Air Filter": ["air filter", "cold air intake"],
    "Oil Filter": ["oil filter"],
    "Sensor": ["sensor", "o2 sensor", "oxygen sensor"],
    "CV Axle": ["cv axle", "axle shaft"],
    "Drive Shaft": ["drive shaft"],
    "Transfer Case": ["transfer case"],
    "Differential": ["differential"],
    "Timing Chain": ["timing chain", "timing belt"],
}

# 匹配年份：1968-1979、68-79、2015-2020、15-20 等
YEAR_PATTERN = re.compile(
    r'(19\d{2}|20\d{2}|\b\d{2}\b)\s*[-–—to]*\s*(19\d{2}|20\d{2}|\b\d{2}\b)?',
    re.IGNORECASE
)

def _normalize_year(y: str) -> int:
    """将 2 位或 4 位年份统一为 4 位"""
    y = y.strip()
    if len(y) == 2:
        return 1900 + int(y) if int(y) > 50 else 2000 + int(y)
    return int(y)


def extract_product_identity(title: str, url: str = "") -> dict:
    """从 eBay 标题提取产品身份：车型、年份、产品类型

    Returns:
        {
            "make": "Chevy",
            "model": "Nova",
            "year_start": 1968,
            "year_end": 1979,
            "product_type": "Door-Hinges",
            "product_category": "Door Hinge",
            "raw_title": "...",
            "url": "..."
        }
    """
    result = {
        "make": "UNKNOWN",
        "model": "UNKNOWN",
        "year_start": None,
        "year_end": None,
        "product_type": "UNKNOWN",
        "product_category": "UNKNOWN",
        "raw_title": title,
        "url": url
    }

    # 1. 提取年份
    years = YEAR_PATTERN.findall(title)
    if years:
        all_years = []
        for y in years:
            if y[0]:
                all_years.append(_normalize_year(y[0]))
            if y[1]:
                all_years.append(_normalize_year(y[1]))
        if all_years:
            result["year_start"] = min(all_years)
            result["year_end"] = max(all_years)

    # 2. 识别车型（Model）
    title_lower = title.lower()
    for model, makes in MODEL_PATTERNS.items():
        if model.lower() in title_lower:
            result["model"] = model
            result["make"] = makes[0]  # 首选 make
            break

    # 3. 如果没匹配到 Model，尝试直接匹配 Make
    if result["make"] == "UNKNOWN":
        for pattern in MAKE_PATTERNS:
            for variant in pattern.split("|"):
                if variant.lower() in title_lower:
                    result["make"] = variant
                    break
            if result["make"] != "UNKNOWN":
                break

    # 2b/3b. 模型名称标准化（放在 make 检测之后，确保 Pickup 推断能工作）
    _normalize_model(result)

    # 4. 识别产品类型
    for category, keywords in PRODUCT_CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                result["product_category"] = category
                result["product_type"] = _slugify(category)
                break
        if result["product_type"] != "UNKNOWN":
            break

    # 如果产品类型未识别，尝试从标题提取名词短语
    if result["product_type"] == "UNKNOWN":
        # 使用标题中的关键词作为产品类型
        result["product_type"] = _slugify(title[:60])
        result["product_category"] = title[:60]

    return result


def _normalize_model(identity: dict):
    """标准化模型名称：F150→F-150, Super Duty/F-250/F-350→F-Super-Duty"""
    model = identity.get("model", "")
    make = identity.get("make", "")

    # 制造商名称标准化
    if make == "Chevrolet":
        identity["make"] = "Chevy"

    # F150/F250/F350 → F-150/F-Super-Duty
    for naked in ["F150"]:
        if model == naked:
            identity["model"] = "F-150"
    # F-250/F-350/F250/F350/Super Duty → F-Super-Duty (统一)
    if make == "Ford" and model in ("F-250", "F-350", "F250", "F350", "Super Duty", "F-450", "F450", "F-550", "F550"):
        identity["model"] = "F-Super-Duty"

    # Ram 1500/2500/3500 → make=Ram, model=1500/2500/3500
    if model in ("Ram 1500", "Ram 2500", "Ram 3500"):
        identity["make"] = "Ram"
        identity["model"] = model.replace("Ram ", "")

    # 如果标题含 "Pickup" 或 "Truck" 且 model=UNKNOWN，推断默认皮卡车型
    if model == "UNKNOWN" and make != "UNKNOWN":
        title_lower = identity.get("raw_title", "").lower()
        # 检查是否有 Pickup/Truck 参考
        if any(w in title_lower for w in ["pickup", "truck", "pick up"]):
            # 尝试从标题提取数字型号（如 "1500", "2500"），排除年份
            nums = re.findall(r'\b(1[5-9]\d{2}|2[0-4]\d{2})\b', title_lower)
            # 排除年份（19xx, 20xx）
            non_year_nums = [n for n in nums if not (1900 <= int(n) <= 2029)]
            if non_year_nums:
                identity["model"] = non_year_nums[0]
            else:
                # 默认映射
                default_pickups = {
                    "Chevy": "Silverado", "Chevrolet": "Silverado",
                    "Ford": "F-150", "GMC": "Sierra",
                    "Ram": "1500", "Dodge": "Ram",
                }
                current_make = identity.get("make", make)
                identity["model"] = default_pickups.get(current_make, default_pickups.get(make, "UNKNOWN"))
        else:
            # 无 Pickup/Truck 提示，使用该品牌最通用型号
            default_models = {
                "Chevy": "Silverado", "Chevrolet": "Silverado",
                "GMC": "Sierra", "Ford": "F-150",
                "Ram": "1500", "Dodge": "Ram",
                "Jeep": "Grand Cherokee", "Cadillac": "Escalade",
            }
            # 使用 identity 里的 make（可能已被标准化）而非局部变量
            current_make = identity.get("make", make)
            identity["model"] = default_models.get(current_make, default_models.get(make, "UNKNOWN"))


def _canonical_key(identity: dict) -> str:
    """生成归并键：make + model + product_type"""
    return f"{identity.get('make','')}|{identity.get('model','')}|{identity.get('product_type','')}"


def _overlap_year_range(y1s, y1e, y2s, y2e) -> bool:
    """判断两个年份范围是否重叠或相邻（差距≤3年视为同一产品）"""
    if None in (y1s, y1e, y2s, y2e):
        return True  # 未知年份默认合并
    # 范围重叠或差距≤3年
    gap = max(y2s - y1e, y1s - y2e, 0)
    return gap <= 3


def _merge_groups(groups: dict[str, list]) -> dict[str, list]:
    """合并相似分组：同 make+model+product_type 且年份范围重叠 → 合并"""
    canonical = {}  # canonical_key → list of (mother_name, items, year_start, year_end)

    for mother_name, items in groups.items():
        if not items:
            continue
        key = _canonical_key(items[0]["identity"])
        ys = items[0]["identity"].get("year_start")
        ye = items[0]["identity"].get("year_end")

        merged = False
        for existing_key in list(canonical.keys()):
            if existing_key == key:
                for entry in canonical[existing_key]:
                    e_name, e_items, e_ys, e_ye = entry
                    if _overlap_year_range(ys, ye, e_ys, e_ye):
                        # 合并！
                        e_items.extend(items)
                        # 扩展年份范围
                        all_ys = [x for x in [e_ys, ys] if x is not None]
                        all_ye = [x for x in [e_ye, ye] if x is not None]
                        new_ys = min(all_ys) if all_ys else None
                        new_ye = max(all_ye) if all_ye else None
                        entry[1] = e_items
                        entry[2] = new_ys
                        entry[3] = new_ye
                        merged = True
                        break
                if merged:
                    break

        if not merged:
            if key not in canonical:
                canonical[key] = []
            canonical[key].append([mother_name, items.copy(), ys, ye])

    # 重新生成合并后的 groups
    result = {}
    for key, entries in canonical.items():
        for entry in entries:
            name, items_list, ys, ye = entry
            # 重建 identity 和 mother_name
            identity = items_list[0]["identity"].copy()
            identity["year_start"] = ys
            identity["year_end"] = ye
            new_name = generate_mother_name(identity)
            result[new_name] = items_list

    return result


def _slugify(text: str) -> str:
    """将文本转为文件安全的 slug"""
    return re.sub(r'[\s/&]+', '-', text.strip()).strip('-')[:50]


def generate_mother_name(identity: dict) -> str:
    """生成母文件目录名：{车型}_{年份}_{产品类型}

    Example: Chevy-Nova_1968-1979_Door-Hinge-Kit
    """
    make_model = f"{identity['make']}-{identity['model']}"
    if identity['make'] == "UNKNOWN" and identity['model'] == "UNKNOWN":
        make_model = "Unknown-Vehicle"

    year_range = "Unknown-Year"
    if identity['year_start'] and identity['year_end']:
        if identity['year_start'] == identity['year_end']:
            year_range = str(identity['year_start'])
        else:
            year_range = f"{identity['year_start']}-{identity['year_end']}"
    elif identity['year_start']:
        year_range = str(identity['year_start'])

    product = identity.get('product_type', 'Unknown-Product')

    return f"{make_model}_{year_range}_{product}"


def classify_links(links: list[dict]) -> dict[str, list[dict]]:
    """将链接列表归类到母文件

    Args:
        links: [{"url": "...", "title": "..."}, ...]  或直接是 URL 字符串列表

    Returns:
        {mother_name: [links, ...], ...}
    """
    groups = {}

    for i, item in enumerate(links):
        if isinstance(item, str):
            item = {"url": item, "title": ""}

        url = item.get("url", "")
        title = item.get("title", "")

        # 如果没有 title，从 URL 提取 item ID 做标识
        if not title:
            # 尝试从 URL 提取
            m = re.search(r'/itm/(\d+)', url)
            item_id = m.group(1) if m else f"link_{i}"
            title = f"ITEM_{item_id}"

        identity = extract_product_identity(title, url)
        mother = generate_mother_name(identity)

        if mother not in groups:
            groups[mother] = []
        groups[mother].append({
            "url": url,
            "title": title,
            "identity": identity
        })

    # 合并相似分组
    return _merge_groups(groups)


def create_mother_files(classified: dict[str, list[dict]]) -> list[dict]:
    """为每个母文件创建目录和 source_links.json

    Returns:
        [{"mother_name": ..., "dir": ..., "link_count": ...}, ...]
    """
    results = []
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)

    for mother_name, items in classified.items():
        mother_dir = ARCHIVE_ROOT / mother_name
        mother_dir.mkdir(parents=True, exist_ok=True)

        # 取第一条链接的最多图片数作为"标杆链接"
        benchmark_url = items[0]["url"]
        benchmark_title = items[0]["title"]

        # 生成 source_links.json
        source_links = {
            "mother_name": mother_name,
            "created_at": datetime.now().isoformat(),
            "total_links": len(items),
            "benchmark": {
                "url": benchmark_url,
                "title": benchmark_title,
                "reason": "图片最多的 listing（待爬虫确认）"
            },
            "links": []
        }

        for item in items:
            source_links["links"].append({
                "url": item["url"],
                "title": item["title"],
                "identity": item["identity"],
                "status": "pending"
            })

        (mother_dir / "source_links.json").write_text(
            json.dumps(source_links, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # 生成空的 market_intel.json（待 DeepSeek 填充）
        market_intel = {
            "mother_name": mother_name,
            "generated_at": None,
            "price_range": None,
            "avg_price": None,
            "title_strategies": [],
            "selling_points": [],
            "image_count_distribution": {},
            "top_sellers": [],
            "notes": "待 DeepSeek 分析所有链接后填充"
        }
        (mother_dir / "market_intel.json").write_text(
            json.dumps(market_intel, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        results.append({
            "mother_name": mother_name,
            "dir": str(mother_dir),
            "link_count": len(items)
        })

    return results


def process_link_list(links: list, save_queue: bool = True) -> dict:
    """主入口：链接列表 → 归类 → 创建母文件 → 写入队列

    Args:
        links: URL 字符串列表 或 [{"url": "...", "title": "..."}] 列表
        save_queue: 是否保存到 pending.json

    Returns:
        {
            "total_links": int,
            "total_mothers": int,
            "mothers": [{"mother_name": ..., "dir": ..., "link_count": ...}],
            "groups": {mother_name: [links, ...]}
        }
    """
    classified = classify_links(links)
    mother_results = create_mother_files(classified)

    # 写入队列文件
    if save_queue:
        pending = []
        for mother_name, items in classified.items():
            pending.append({
                "mother_name": mother_name,
                "link_count": len(items),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "benchmark_url": items[0]["url"] if items else ""
            })

        _write_json(PENDING_FILE, pending)
        _write_json(DONE_FILE, [])
        _write_json(FAILED_FILE, [])

    return {
        "total_links": len(links),
        "total_mothers": len(classified),
        "mothers": mother_results,
        "groups": {
            name: [{"url": it["url"], "title": it["title"][:80]} for it in items]
            for name, items in classified.items()
        }
    }


def _write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_queue() -> dict:
    """加载当前队列状态"""
    result = {"pending": [], "done": [], "failed": []}
    for key, path in [("pending", PENDING_FILE), ("done", DONE_FILE), ("failed", FAILED_FILE)]:
        if path.exists():
            result[key] = json.loads(path.read_text(encoding="utf-8"))
    return result


def mark_completed(mother_name: str):
    """标记母文件完成"""
    _move_entry(mother_name, PENDING_FILE, DONE_FILE)


def mark_failed(mother_name: str, error: str):
    """标记母文件失败"""
    _move_entry(mother_name, PENDING_FILE, FAILED_FILE, extra={"error": error, "failed_at": datetime.now().isoformat()})


def _move_entry(name, from_file, to_file, extra=None):
    from_data = json.loads(from_file.read_text(encoding="utf-8")) if from_file.exists() else []
    to_data = json.loads(to_file.read_text(encoding="utf-8")) if to_file.exists() else []

    entry = None
    new_from = []
    for item in from_data:
        if item.get("mother_name") == name:
            entry = item
        else:
            new_from.append(item)

    if entry:
        entry["status"] = "done" if to_file == DONE_FILE else "failed"
        if extra:
            entry.update(extra)
        to_data.append(entry)

    _write_json(from_file, new_from)
    _write_json(to_file, to_data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python queue_manager.py classify <links.txt>       # 从文本文件读链接列表并归类")
        print("  python queue_manager.py classify --stdin           # 从 stdin 读链接列表")
        print("  python queue_manager.py list                        # 查看队列状态")
        print("  python queue_manager.py done <mother_name>          # 标记完成")
        print("  python queue_manager.py fail <mother_name> <error>  # 标记失败")
        print()
        print("链接文件格式：每行一个 URL，或 JSON 数组 [{\"url\":\"...\",\"title\":\"...\"}]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "classify":
        if len(sys.argv) > 2:
            if sys.argv[2] == "--stdin":
                raw = sys.stdin.read()
            else:
                raw = Path(sys.argv[2]).read_text(encoding="utf-8")

            # 尝试 JSON 格式
            try:
                links = json.loads(raw)
            except json.JSONDecodeError:
                # 纯文本，每行一个 URL
                links = [line.strip() for line in raw.splitlines() if line.strip() and 'http' in line]

            result = process_link_list(links)
            print(json.dumps({
                "total_links": result["total_links"],
                "total_mothers": result["total_mothers"],
                "mothers": result["mothers"],
                "groups": result["groups"]
            }, ensure_ascii=False, indent=2))

    elif cmd == "list":
        q = load_queue()
        print(f"待处理: {len(q['pending'])}")
        for item in q['pending']:
            print(f"  - {item['mother_name']} ({item.get('link_count', '?')} 条链接)")
        print(f"已完成: {len(q['done'])}")
        for item in q['done']:
            print(f"  - {item['mother_name']}")
        print(f"失败: {len(q['failed'])}")
        for item in q['failed']:
            print(f"  - {item['mother_name']}: {item.get('error', '?')}")

    elif cmd == "done" and len(sys.argv) > 2:
        mark_completed(sys.argv[2])
        print(f"已标记完成: {sys.argv[2]}")

    elif cmd == "fail" and len(sys.argv) > 3:
        mark_failed(sys.argv[2], sys.argv[3])
        print(f"已标记失败: {sys.argv[2]}")
