"""批量生图 — 处理所有待处理产品线"""
import subprocess
import sys
from pathlib import Path

PRODUCT_DIR = Path(r"c:\Users\Hardy\ai-projects\产品卖点主图和信息生成")

LINES = [
    "Ford-F-150_2015-2022_Door-Window-Glass",
    "Chevy-Express_1996-2022_Door-Handle",
    "Chevy-Tahoe_2007-2013_Door-Handle",
    "Ford-F-Super-Duty_1999-2016_Door-Handle",
    "Jeep-Grand Cherokee_2011_Door-Handle",
    "Ram-1500_2009-2022_Door-Window-Glass",
    "Dodge-Durango_2011-2020_Door-Handle",
    "Cadillac-Escalade_2007-2014_Door-Handle",
]

for line in LINES:
    d = PRODUCT_DIR / line
    if not d.exists():
        print(f"[SKIP] 目录不存在: {d}")
        continue

    # Check if already has images
    existing = list(d.glob("gen_main_fast_*.png"))
    if len(existing) >= 6:
        print(f"[SKIP] {line} - 已有 {len(existing)} 张图片")
        continue

    print(f"\n{'='*60}")
    print(f"Processing: {line}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, "batch_image_gen.py", str(d)],
        capture_output=True, text=True, timeout=300,
        encoding='utf-8', errors='replace'
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")

print("\n全部完成!")
