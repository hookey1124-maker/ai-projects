"""搜索 eBay 竞品链接 — LYAP-X1001-1 Rear Bumper Diffuser Shark Fins"""
import sys, re, json, asyncio
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"c:\Users\Hardy\ai-projects\agent升级计划\browser_profile")
MOTHER_DIR = Path(r"c:\Users\Hardy\ai-projects\产品卖点主图和信息生成\Universal_Rear_Glossy-Black_4pcs_Bumper-Diffuser")

ANCHOR_IDS = {"116781928287", "188299528230", "196020510372", "227141995383"}

QUERIES = [
    'Rear Bumper Diffuser Shark Fins Spoiler Lip Splitter Glossy Black Universal 4PCS',
    'Universal Rear Bumper Lip Diffuser Shark Fin Spoiler Splitter Gloss Black 4pc',
    'Rear Diffuser Shark Fins Bumper Spoiler Lip Splitter Glossy Black Car Truck 4pcs',
    '4 PCS Rear Bumper Diffuser Shark Fin Spoiler Canard Lip Splitter Universal Black',
    'Universal Rear Diffuser Shark Fin Bumper Lip Splitter Spoiler Glossy Black 4x',
    'Rear Bumper Lower Diffuser Shark Fins Spoiler Lip Body Kit Universal Gloss Black',
    'Car Rear Bumper Diffuser Shark Fin Lip Splitter Spoiler Universal 4 Pieces Black',
    'Glossy Black Rear Bumper Diffuser Shark Fin Spoiler Splitter Universal Auto 4pc',
    'Universal Car SUV Rear Diffuser Shark Fin Bumper Lip Spoiler Splitter 4PCS Black',
    'Rear Bumper Shark Fin Diffuser Splitter Lip Spoiler Canards Universal Gloss Black',
    '4 Pieces Universal Rear Bumper Diffuser Shark Fin Spoiler Lip Glossy Black Auto',
    'Universal Rear Bumper Shark Fin Diffuser Trim Spoiler Lip Splitter Gloss Black',
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
                    seen[id] = text.substring(0, 200);
                }
            });
        });
        return Object.entries(seen).map(([id, snippet]) => ({id, snippet}));
    }""")


async def search_all():
    source_file = MOTHER_DIR / "source_links.json"
    source = json.loads(source_file.read_text(encoding="utf-8"))
    existing = {re.search(r'/itm/(\d+)', l["url"]).group(1)
                for l in source["links"] if re.search(r'/itm/(\d+)', l["url"])}
    anchor_ids = {re.search(r'/itm/(\d+)', l["url"]).group(1)
                  for l in source["links"] if l.get("anchor")}

    all_found = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            str(USER_DATA),
            headless=False,
            proxy={"server": PROXY},
            channel="chrome",
            viewport={"width": 1280, "height": 800},
        )

        for q in QUERIES:
            print(f"\n=== Searching: {q[:80]}... ===")
            page = await browser.new_page()
            try:
                search_url = f"https://www.ebay.com/sch/i.html?_dmd=1&_nkw={q.replace(' ', '+')}&LH_BIN=1&_ipg=240"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                results = await extract_results(page)
                print(f"  Found {len(results)} results")

                for r in results:
                    rid = r["id"]
                    if rid not in anchor_ids and rid not in all_found:
                        all_found[rid] = r["snippet"][:200]
            except Exception as e:
                print(f"  Error: {e}")
            finally:
                await page.close()

        await browser.close()

    keep_keywords = ['diffuser', 'shark', 'fin', 'splitter', 'bumper lip', 'canard', 'spoiler']
    exclude_keywords = ['front', 'side skirt', 'door', 'handle', 'mirror', 'headlight', 'tail light', 'grille', 'hood']

    filtered = {}
    for rid, snippet in all_found.items():
        s_lower = snippet.lower()
        has_keep = any(kw in s_lower for kw in keep_keywords)
        has_exclude = any(kw in s_lower for kw in exclude_keywords)
        if has_keep and not has_exclude:
            filtered[rid] = snippet

    print(f"\n=== After filtering: {len(filtered)} of {len(all_found)} ===")

    new_count = 0
    for rid in filtered:
        if rid not in existing:
            source["links"].append({"url": f"https://www.ebay.com/itm/{rid}", "anchor": False})
            existing.add(rid)
            new_count += 1

    source_file.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Added {new_count} new links. Total: {len(source['links'])}")
    return source


if __name__ == "__main__":
    asyncio.run(search_all())
