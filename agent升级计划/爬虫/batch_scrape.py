"""一体化批量爬取：单个浏览器会话，顺序爬取所有产品"""
import sys, json, asyncio, re, random
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")
MOTHER = Path(r"C:\Users\Administrator\Desktop\AI项目\产品卖点主图和信息生成\Chevy-Silverado_2007-2013_Driver-Side_Black_1pc_Interior-Door-Handle")
OUTPUT_DIR = MOTHER  # save directly to mother dir

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

EXTRACT_JS = r"""() => {
    const get = (sel) => {
        const el = document.querySelector(sel);
        return el?.innerText?.trim() || '';
    };
    const getAllText = (sel) => {
        return Array.from(document.querySelectorAll(sel)).map(el => el.innerText?.trim() || '');
    };

    // Expand "See all" in Item Specifics
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
        const txt = btn.innerText?.trim() || '';
        if (/(?:see\s*all|show\s*more|see\s*full)/i.test(txt)) {
            btn.click();
        }
    }

    // Title
    const title = get('h1.x-item-title') || get('h1.it-ttl') || get('[data-testid="x-item-title"]') || '';

    // Price
    const priceEl = document.querySelector('.x-price-primary span, .ux-textspans--BOLD, [itemprop="price"]');
    const price = priceEl?.innerText?.trim() || priceEl?.getAttribute('content') || '';

    // Item Specifics
    const specs = {};
    const rows = document.querySelectorAll('.ux-layout-section-evo__row, .ux-labels-values__row');
    rows.forEach(row => {
        const label = row.querySelector('.ux-labels-values__labels .ux-textspans');
        const value = row.querySelector('.ux-labels-values__values .ux-textspans');
        if (label && value) {
            const k = label.innerText.replace(/:/g, '').trim();
            const v = value.innerText.trim();
            if (k && v && !specs[k]) specs[k] = v;
        }
    });

    // Images
    const images = [];
    document.querySelectorAll('img[src*="ebayimg"]').forEach(img => {
        const src = img.src || img.getAttribute('data-src') || '';
        if (src && !src.includes('thumbs') && !images.includes(src)) {
            images.push(src.replace(/\/s-l\d+\./, '/s-l500.'));
        }
    });

    // Seller info
    const seller = get('.ux-seller-section__item--seller a') || get('[data-testid="x-seller-name"]') || '';
    const sellerUrl = document.querySelector('.ux-seller-section__item--seller a')?.href || '';
    const sellerFeedback = get('.ux-seller-section__item--seller .ux-textspans--SECONDARY') || '';
    const sellerFeedbackPct = '';

    // Item ID from URL
    const itemId = (window.location.href.match(/\/itm\/(\d+)/) || [])[1] || '';

    // Category ID
    const categoryId = '';
    const catEl = document.querySelector('[data-testid="x-category"] a, .ux-breadcrumb a:last-child');
    if (catEl) {
        const catHref = catEl.href || '';
        const cm = catHref.match(/\/b\/.+\/(\d+)/);
        if (cm) categoryId = cm[1];
    }

    // Bullet points / description
    const bullets = [];
    document.querySelectorAll('.x-about-this-item .ux-textspans, [data-testid="x-about-this-item"] span').forEach(el => {
        const t = el.innerText?.trim();
        if (t && t.length > 10 && t.length < 500) bullets.push(t);
    });

    // Compatibility from DOM
    const compatibility = [];
    document.querySelectorAll('[data-testid="x-compatibility"] table tr, .ux-layout-section-evo__row table tr').forEach(row => {
        const cells = row.querySelectorAll('td, th');
        if (cells.length >= 3) {
            compatibility.push({
                Year: cells[0]?.innerText?.trim() || '',
                Make: cells[1]?.innerText?.trim() || '',
                Model: cells[2]?.innerText?.trim() || '',
                Trim: cells[3]?.innerText?.trim() || '',
                Engine: cells[4]?.innerText?.trim() || ''
            });
        }
    });

    return {
        title, price, specs, images: images.slice(0, 15),
        seller, sellerUrl, sellerFeedback, sellerFeedbackPct,
        itemId, categoryId, bullets, compatibility,
        imageCount: images.length
    };
}"""


async def scrape_all():
    # Load source links
    source = json.loads((MOTHER / "source_links.json").read_text(encoding="utf-8"))
    links = source.get("links", [])
    urls = [l["url"] for l in links]
    print(f"Total URLs: {len(urls)}")

    # Check existing
    existing = {p.stem.replace("product_", ""): p for p in MOTHER.glob("product_*.json")}
    pending = [u for u in urls if re.search(r'/itm/(\d+)', u).group(1) not in existing]
    print(f"Already scraped: {len(existing)}, Pending: {len(pending)}")

    if not pending:
        print("All products already scraped!")
        return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA),
            headless=True,
            channel="chrome",
            args=['--disable-blink-features=AutomationControlled', '--no-first-run',
                  '--no-default-browser-check', '--window-size=1920,1080'],
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            proxy={'server': PROXY},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Warmup
        print("Warming up...")
        try:
            await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            await page.evaluate("""() => {
                const expires = new Date(Date.now() + 365 * 86400000).toUTCString();
                document.cookie = 'shs=US;expires=' + expires + ';path=/;domain=.ebay.com';
                document.cookie = 'shss=NC;expires=' + expires + ';path=/;domain=.ebay.com';
                document.cookie = 'shzip=27513;expires=' + expires + ';path=/;domain=.ebay.com';
            }""")
            print("Warmup OK")
        except Exception as e:
            print(f"Warmup warning: {e}")

        # Scrape each product
        for i, url in enumerate(pending):
            item_id = re.search(r'/itm/(\d+)', url).group(1)
            anchor = any(l["url"] == url and l.get("anchor") for l in links)
            tag = "[ANCHOR]" if anchor else "[COMP]"
            print(f"[{i+1}/{len(pending)}] {tag} {item_id}")

            for retry in range(2):
                try:
                    await page.goto(url, wait_until="load", timeout=45000)
                    await asyncio.sleep(random.uniform(2.0, 3.5))
                    data = await page.evaluate(EXTRACT_JS)
                    data['item_id'] = item_id
                    data['url'] = url
                    data['anchor'] = anchor
                    data['scraped_at'] = datetime.now().isoformat()

                    # Fetch compatibility via finders API
                    category_id = data.get('categoryId', '')
                    if item_id and category_id:
                        try:
                            all_rows = []
                            offset = 0
                            while offset < 500:
                                api_url = f"https://www.ebay.com/g/api/finders?module_groups=PART_FINDER&referrer=VIEWITEM&offset={offset}&module=COMPATIBILITY_TABLE"
                                payload = {
                                    "scopedContext": {
                                        "catalogDetails": {
                                            "itemId": item_id,
                                            "sellerName": data.get('sellerUsername', ''),
                                            "categoryId": category_id,
                                            "marketplaceId": "EBAY-US"
                                        }
                                    }
                                }
                                resp = await page.request.post(api_url, headers={
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json',
                                    'Referer': url,
                                }, data=json.dumps(payload))
                                if resp.status != 200:
                                    break
                                result = await resp.json()
                                table = result.get('modules', {}).get('COMPATIBILITY_TABLE', {}).get('paginatedTable', {})
                                rows = table.get('rows', [])
                                if not rows:
                                    break
                                for row in rows:
                                    cells = row.get('cells', [])
                                    all_rows.append({
                                        'Year': cells[0].get('textSpans', [{}])[0].get('text', '') if len(cells) > 0 else '',
                                        'Make': cells[1].get('textSpans', [{}])[0].get('text', '') if len(cells) > 1 else '',
                                        'Model': cells[2].get('textSpans', [{}])[0].get('text', '') if len(cells) > 2 else '',
                                        'Trim': cells[3].get('textSpans', [{}])[0].get('text', '') if len(cells) > 3 else '',
                                        'Engine': cells[4].get('textSpans', [{}])[0].get('text', '') if len(cells) > 4 else '',
                                    })
                                offset += len(rows)
                                if len(rows) < 20:
                                    break
                            if all_rows:
                                data['compatibility'] = all_rows
                                print(f"    Compat: {len(all_rows)} rows")
                        except Exception as e:
                            print(f"    Compat API error: {e}")

                    # Save
                    out_file = OUTPUT_DIR / f"product_{item_id}.json"
                    out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"    OK: {data.get('title', '?')[:80]}")
                    break
                except Exception as e:
                    if retry == 0:
                        print(f"    Retry: {e}")
                        await asyncio.sleep(3)
                    else:
                        print(f"    FAIL: {e}")

            # Rate limiting
            if i < len(pending) - 1:
                delay = random.uniform(2, 4)
                await asyncio.sleep(delay)

        await context.close()

    print(f"\nDone! Checked {len(existing) + len(pending)} products")
    final_count = len(list(MOTHER.glob("product_*.json")))
    print(f"Total product JSONs: {final_count}")


if __name__ == '__main__':
    asyncio.run(scrape_all())
