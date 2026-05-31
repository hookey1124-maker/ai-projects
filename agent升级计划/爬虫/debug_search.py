"""Search eBay — force classic view + better title extraction"""
import sys, json, asyncio, random
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")

async def search(query: str):
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            str(USER_DATA),
            headless=True,
            channel="chrome",
            proxy={"server": PROXY} if PROXY else None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        encoded = query.replace(' ', '+')
        # Use _dmd=1 to force classic list view (more predictable HTML)
        url = f"https://www.ebay.com/sch/i.html?_nkw={encoded}&_sop=15&LH_BIN=1&_dmd=1&LH_PrefLoc=1"
        print(f"  URL: {url[:150]}...")

        await page.goto(url, wait_until="load", timeout=60000)
        await asyncio.sleep(random.uniform(2, 3))

        items = await page.evaluate("""() => {
            const results = [];
            const seen = new Set();

            // Extract all /itm/ links
            document.querySelectorAll('a[href*="/itm/"]').forEach(a => {
                const href = a.href || '';
                const m = href.match(/\\/itm\\/(\\d+)/);
                if (!m || seen.has(m[1])) return;
                if (href.includes('/sch/') || href.includes('/usr/') || href.includes('/help/')) return;

                const itemId = m[1];

                // Find the best title by walking up the DOM
                let container = a;
                for (let i = 0; i < 10; i++) {
                    container = container.parentElement;
                    if (!container) break;

                    // Look for title-like elements
                    const titleSelectors = [
                        'h3', '.s-item__title', '[class*="title"]',
                        'span[role="text"]', '.s-item__title span',
                        'a[class*="title"]', '.textual-display',
                        '[data-testid="list-view-item-title"]'
                    ];

                    for (const sel of titleSelectors) {
                        const titleEl = container.querySelector(sel);
                        if (titleEl) {
                            const t = (titleEl.innerText || titleEl.textContent || '').replace(/\\s+/g, ' ').trim();
                            if (t.length > 20 && t.length < 200 && !t.includes('Shop on eBay')) {
                                seen.add(itemId);
                                results.push({
                                    item_id: itemId,
                                    title: t.substring(0, 150),
                                    url: 'https://www.ebay.com/itm/' + itemId
                                });
                                return;
                            }
                        }
                    }
                }

                // Fallback: use the innerText of the nearest meaningful container
                let c2 = a.closest('li') || a.closest('[class*="result"]') || a.closest('[class*="card"]');
                if (!c2) c2 = a.parentElement?.parentElement;
                if (c2) {
                    const allText = (c2.innerText || '').replace(/\\s+/g, ' ').trim();
                    const lines = allText.split(/\\n|Sponsored|\\|/).filter(l => l.trim().length > 20 && l.trim().length < 200);
                    const bestLine = lines.find(l =>
                        /door|handle|window|glass|mirror|hinge|lock|latch|panel|trim/i.test(l) &&
                        !/delivery|shipping|located|positive|returns|buy it now|best offer|free/i.test(l)
                    );
                    if (bestLine && !seen.has(itemId)) {
                        seen.add(itemId);
                        results.push({
                            item_id: itemId,
                            title: bestLine.trim().substring(0, 150),
                            url: 'https://www.ebay.com/itm/' + itemId
                        });
                    }
                }
            });

            return results;
        }""")

        await ctx.close()
        return items


async def main():
    queries = [
        "Silverado Sierra interior door handle driver side 2007-2013",
        "Chevrolet Silverado inside door handle left driver 2007 2008 2009 2010 2011 2012 2013",
        "GMC Sierra interior door handle driver side inside 2007-2013",
        "Silverado Sierra door handle interior left driver side replacement",
    ]

    all_results = {}
    anchor_id = "355448970865"

    for qi, q in enumerate(queries):
        print(f"\n[{qi+1}/{len(queries)}] {q[:80]}...")
        try:
            items = await search(q)
            print(f"  Found: {len(items)} items")
            for item in items:
                if item['item_id'] != anchor_id and item['item_id'] not in all_results:
                    # Filter: must be a door handle product
                    t = (item.get('title', '') or '').lower()
                    if 'door' in t and ('handle' in t or 'interior' in t or 'inside' in t):
                        all_results[item['item_id']] = item

            print(f"  After filter: {len(items)} → cumulative: {len(all_results)}")
        except Exception as e:
            print(f"  ERROR: {e}")

        if len(all_results) >= 55:
            break
        await asyncio.sleep(random.uniform(1, 2))

    result_list = list(all_results.values())
    result_list.sort(key=lambda x: x.get('title', ''))

    print(f"\n=== TOTAL: {len(result_list)} competitors ===")
    for i, r in enumerate(result_list[:55]):
        print(f"  [{i+1}] {r['item_id']}: {r.get('title','')[:120]}")

    final = result_list[:50]
    out = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\爬虫\search_results.json")
    out.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nSaved {len(final)} results to {out}")

if __name__ == '__main__':
    asyncio.run(main())
