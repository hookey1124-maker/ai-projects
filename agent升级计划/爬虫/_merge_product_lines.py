"""合并碎片目录到统一品线目录"""
import json
import shutil
from pathlib import Path

BASE = Path(r"c:\Users\Hardy\ai-projects\产品卖点主图和信息生成")

# 品线定义: (保留目录, [碎片目录列表])
MERGES = [
    (
        "Chevy-Silverado_1999-2014_Door-Handle",
        [
            "Chevy-Silverado_1999-2006_Door-Handle",
            "Chevy-Silverado_1999-2007_Door-Handle",
            "Chevy-Silverado_2007-2013_Door-Handle",
            "Chevy-Silverado_2007-2014_Door-Handle",
            "Chevy-Pickup_2007-2013_Door-Handle",
            "Chevy-UNKNOWN_2007-2013_Door-Handle",
            "Chevy-UNKNOWN_2007-2014_Door-Handle",
            "Chevrolet-UNKNOWN_2007-2014_Door-Handle",
        ],
    ),
    (
        "Chevy-Colorado_2004-2012_Door-Handle",
        [
            "Chevy-Colorado_2004-2012_Door",
            "Chevy-Colorado_Unknown-Year_Door-Handle",
        ],
    ),
    (
        "Chevy-Express_1996-2022_Door-Handle",
        [
            "Chevy-Express_1996-2009_Door-Handle",
            "Chevy-Express_2003-2021_Door-Handle",
        ],
    ),
    (
        "Ford-F-Super-Duty_1999-2016_Door-Handle",
        [
            "Ford-F-250_1999-2007_Door-Handle",
            "Ford-F-250_1999-2016_Door-Handle",
            "Ford-F250_1999-2016_Door-Handle",
            "Ford-Super Duty_1999-2016_Door-Handle",
        ],
    ),
    (
        "Ford-F-150_2015-2022_Door-Window-Glass",
        [
            "Ford-F150_2015-2022_Door-Window-Glass",
        ],
    ),
    (
        "Ram-1500_2009-2022_Door-Window-Glass",
        [
            "Ram-1500_2009-2018_Door-Window-Glass",
            "Ram-Ram 1500_2009-2018_Door-Window-Glass",
            "Ram-UNKNOWN_2019-2022_Door-Window-Glass",
            "Chevy-Pickup_2019-2022_Door-Window-Glass",  # 实际是Ram 1500
        ],
    ),
]

# 待删除的目录（处理完后清除）
TO_DELETE = set()

for keep_name, fragments in MERGES:
    keep_dir = BASE / keep_name
    if not keep_dir.exists():
        print(f"[ERROR] 保留目录不存在: {keep_dir}")
        continue

    print(f"\n{'='*60}")
    print(f"合并 → {keep_name}")
    print(f"{'='*60}")

    # 读取保留目录的 source_links
    keep_sources = json.loads((keep_dir / "source_links.json").read_text(encoding="utf-8"))
    keep_links = keep_sources.get("links", [])
    keep_urls = {l["url"] for l in keep_links}
    new_links_added = 0
    products_copied = 0

    for frag_name in fragments:
        frag_dir = BASE / frag_name
        if not frag_dir.exists():
            print(f"  [SKIP] 碎片目录不存在: {frag_name}")
            continue

        TO_DELETE.add(frag_name)
        print(f"  处理: {frag_name}")

        # 1. 复制 product_*.json（不覆盖同名文件）
        for json_file in sorted(frag_dir.glob("product_*.json")):
            dest = keep_dir / json_file.name
            if dest.exists():
                print(f"    [SKIP] 已存在: {json_file.name}")
                continue
            shutil.copy2(str(json_file), str(dest))
            products_copied += 1
            print(f"    [COPY] {json_file.name}")

        # 也复制 xlsx 文件
        for xlsx_file in sorted(frag_dir.glob("product_*.xlsx")):
            dest = keep_dir / xlsx_file.name
            if dest.exists():
                continue
            shutil.copy2(str(xlsx_file), str(dest))

        # 2. 合并 source_links（去重）
        frag_sf = frag_dir / "source_links.json"
        if frag_sf.exists():
            frag_sources = json.loads(frag_sf.read_text(encoding="utf-8"))
            for link in frag_sources.get("links", []):
                url = link.get("url", "")
                if url and url not in keep_urls:
                    keep_links.append(link)
                    keep_urls.add(url)
                    new_links_added += 1

    # 更新 source_links.json
    keep_sources["links"] = keep_links
    keep_sources["total_links"] = len(keep_links)
    (keep_dir / "source_links.json").write_text(
        json.dumps(keep_sources, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  结果: +{new_links_added} 新链接, +{products_copied} 产品JSON")
    print(f"  合并后总链接数: {len(keep_links)}")

# 额外：处理 Tahoe, Jeep, Durango, Escalade（无碎片，但需要确认）
NO_MERGE = [
    "Chevy-Tahoe_2007-2013_Door-Handle",
    "Jeep-Grand Cherokee_2011_Door-Handle",
    "Dodge-Durango_2011-2020_Door-Handle",
    "Cadillac-Escalade_2007-2014_Door-Handle",
]
print(f"\n无需合并的独立品线: {len(NO_MERGE)} 个")

print(f"\n{'='*60}")
print(f"待删除目录 ({len(TO_DELETE)} 个):")
for d in sorted(TO_DELETE):
    print(f"  - {d}")

# 加上旧规则目录
TO_DELETE.add("304052751324")

print(f"\n下一步: 确认后执行删除，然后重新生成 market_intel.json 和 xlsx")
print(f"删除命令: 手动确认后执行")
