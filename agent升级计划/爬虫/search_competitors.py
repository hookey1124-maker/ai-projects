"""搜索 eBay 竞品链接 — LYAP-280-2 补充搜索（追加30个valid竞品）"""
import sys, re, json, asyncio
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")
MOTHER_DIR = Path(r"C:\Users\Administrator\Desktop\AI项目\产品卖点主图和信息生成\Chevy-Silverado_2007-2014_Front-Rear_Chrome_4pcs_Door-Handle")

ANCHOR_IDS = {
    "176994107624", "355545628474", "285758239190", "116036305188",
    "304281020944", "193917125260", "373474559121",
}

# 新搜索词 — 覆盖不同表述和车型变体
QUERIES = [
    'Chrome Door Handles 4pc Set Chevy GMC 2007 2008 2009 2010 2011 2012 2013 2014 Exterior',
    '4pc Chrome Exterior Door Handle Silverado Sierra Tahoe Yukon Suburban 07-14',
    'Outside Door Handle Chrome 4pcs Chevy Silverado GMC Sierra 2007-2014',
    'Chrome Door Handle Replacement Set 4 Front Rear Silverado Tahoe Yukon 07-13',
    'Exterior Chrome Door Handle Kit For 07-14 Escalade Tahoe Yukon Silverado Sierra 4pc',
    '4X Outside Chrome Door Handle Chevy GMC Truck SUV 2007 2008 2009 2010 2011 2012 2013',
    'Chrome Exterior Handle Set 4-Door Silverado Sierra 1500 2500 07-14',
    'Chrome Outer Door Handle 4PCS Tahoe Yukon Suburban Avalanche 2007-2014',
    # 第二轮补充 — 更细粒度搜索
    'Chrome Handle Set 4pc 07-14 Chevy GMC Exterior Door Replacement',
    'Outside Door Handle 4 Piece Chrome Silverado 1500 2500 3500 2007-2014',
    'Chrome Exterior Door Handle 4 PCS For 07-14 Chevy GMC Full Set',
    'Set of 4 Chrome Door Handle Outside Chevy GMC 07 08 09 10 11 12 13 14',
]


async def extract_results(page):
    return await page.evaluate("""() => {
        const seen = {};
        document.querySelectorAll('.srp-results li').forEach(function(li) {
            li.querySelectorAll('a[href]').forEach(function(a) {
                const href = a.href;
                const idx = href.indexOf('/itm/');
                if (idx === -1) return;
                const after = href.substring(idx + 5);
                const slash = after.indexOf('/');
                const id = slash > -1 ? after.substring(0, slash) : after.split('?')[0];
                if (id && /^\\d+$/.test(id) && !seen[id]) {
                    const text = (li.innerText || '').replace(/\\s+/g, ' ').trim();
                    seen[id] = {id: id, url: 'https://www.ebay.com/itm/' + id, title: text.substring(0, 200)};
                }
            });
        });
        return Object.values(seen);
    }""")


async def search(existing_ids: set):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA), headless=True, channel="chrome",
            args=['--disable-blink-features=AutomationControlled', '--window-size=1920,1080'],
            viewport={'width': 1920, 'height': 1080},
            locale='en-US', timezone_id='America/New_York',
            proxy={'server': PROXY},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        print("Warming up...")
        await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        all_links = {}

        for qi, query in enumerate(QUERIES):
            filtered_count = len(filter_competitors(all_links))
            if filtered_count >= 60:
                break
            print(f"\n[{qi+1}/{len(QUERIES)}] {query} (filtered so far: {filtered_count})")
            try:
                search_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=12&LH_ItemCondition=1000"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)

                if 'captcha' in page.url.lower():
                    print("  *** CAPTCHA ***")
                    continue

                results = await extract_results(page)
                added = 0
                for r in results:
                    if r['id'] not in ANCHOR_IDS and r['id'] not in existing_ids and r['id'] not in all_links:
                        all_links[r['id']] = r
                        added += 1
                print(f"  Page 1: {len(results)} raw, +{added} new, total: {len(all_links)}")

                for pn in range(2, 5):
                    if len(filter_competitors(all_links)) >= 60:
                        break
                    try:
                        paged = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=12&_pgn={pn}&LH_ItemCondition=1000"
                        await page.goto(paged, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(2)
                        results = await extract_results(page)
                        p_added = 0
                        for r in results:
                            if r['id'] not in ANCHOR_IDS and r['id'] not in existing_ids and r['id'] not in all_links:
                                all_links[r['id']] = r
                                p_added += 1
                        print(f"  Page {pn}: +{p_added} new, total: {len(all_links)}")
                    except Exception as e:
                        print(f"  Page {pn} error: {e}")
                        break
            except Exception as e:
                print(f"  Error: {e}")

        await context.close()
        return all_links


def filter_competitors(links: dict) -> dict:
    """标题级过滤 — Chrome Exterior Door Handle 4pcs"""
    filtered = {}
    for item_id, item in links.items():
        t = item['title'].lower()
        if len(t) < 15:
            continue
        has_truck = any(m in t for m in ['silverado', 'sierra', 'tahoe', 'yukon', 'suburban', 'escalade', 'avalanche'])
        has_year = bool(re.search(r'(?:2007|2008|2009|2010|2011|2012|2013|2014|07.14|07-14|07.13|07-13)', t))
        has_handle = 'handle' in t and ('door' in t or 'exterior' in t or 'outside' in t or 'outer' in t)
        has_set = bool(re.search(r'\b(?:4|four)\s*(?:pc|pcs|piece|pack|set)\b', t)) or '4x' in t or 'front rear' in t or 'left right' in t
        is_interior = 'interior' in t and 'exterior' not in t and 'outside' not in t and 'outer' not in t

        if has_truck and has_year and has_handle and has_set and not is_interior:
            filtered[item_id] = item
    return filtered


async def main():
    # 加载已有竞品ID（排除）
    source_file = MOTHER_DIR / "source_links.json"
    existing_source = json.loads(source_file.read_text(encoding="utf-8"))
    existing_ids = {l['item_id'] for l in existing_source['links']}

    print(f"Existing links: {len(existing_ids)} ({len([l for l in existing_source['links'] if l['anchor']])} anchors + {len([l for l in existing_source['links'] if not l['anchor']])} competitors)")

    # 搜索新竞品
    links = await search(existing_ids)
    print(f"\n{'='*50}")
    print(f"New raw collected: {len(links)}")

    if not links:
        print("NO NEW RESULTS")
        return

    filtered = filter_competitors(links)
    print(f"After title filter: {len(filtered)}")

    # 合并到现有 source_links.json
    new_competitors = []
    for cid, cinfo in filtered.items():
        new_competitors.append({"url": cinfo['url'], "item_id": cid, "anchor": False})

    merged_links = existing_source['links'] + new_competitors
    existing_source['links'] = merged_links
    existing_source['generated_at'] = datetime.now().isoformat()

    source_file.write_text(json.dumps(existing_source, ensure_ascii=False, indent=2), encoding="utf-8")
    anchors = [l for l in merged_links if l['anchor']]
    comps = [l for l in merged_links if not l['anchor']]
    print(f"\nSaved: {source_file}")
    print(f"Total: {len(merged_links)} links ({len(anchors)} anchor + {len(comps)} competitor)")
    print(f"New added: {len(new_competitors)}")

    print(f"\n=== 新增竞品标题抽查 ===")
    for i, (cid, cinfo) in enumerate(list(filtered.items())[:10]):
        print(f"  {i+1}. [{cid}] {cinfo['title'][:120]}")


if __name__ == '__main__':
    asyncio.run(main())
