"""Fix price extraction — eBay page DOM has changed"""
import sys, json, asyncio, random, re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"c:\Users\Hardy\ai-projects\agent升级计划\browser_profile")
MOTHER = Path(r"c:\Users\Hardy\ai-projects\产品卖点主图和信息生成\Chevy-Silverado_2007-2013_Driver-Side_Black_1pc_Interior-Door-Handle")


async def fix_prices():
    # Get all product JSONs
    jsons = sorted(MOTHER.glob("product_*.json"))
    print(f"Found {len(jsons)} product JSONs")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA),
            headless=True,
            channel="chrome",
            args=['--disable-blink-features=AutomationControlled', '--no-first-run',
                  '--no-default-browser-check', '--window-size=1920,1080'],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            proxy={'server': PROXY},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Warmup
        try:
            await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1)
            await page.evaluate("""() => {
                const expires = new Date(Date.now() + 365 * 86400000).toUTCString();
                document.cookie = 'shs=US;expires=' + expires + ';path=/;domain=.ebay.com';
            }""")
        except: pass

        fixed = 0
        for i, jf in enumerate(jsons):
            data = json.loads(jf.read_text(encoding="utf-8"))
            old_price = data.get('price', '')

            # Skip if price already looks valid
            try:
                p_str = str(old_price).replace('US $', '').replace('$', '').replace(',', '').strip()
                if p_str and float(p_str) > 0 and float(p_str) < 100000:
                    continue
            except: pass

            url = data.get('url', '')
            if not url:
                continue

            print(f"[{i+1}/{len(jsons)}] {data.get('item_id','?')} old=[{str(old_price)[:50]}]")

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)

                # Try multiple price selectors (eBay changes these frequently)
                price = await page.evaluate("""() => {
                    const selectors = [
                        '[data-testid="x-price-primary"] .ux-textspans',
                        '.x-price-primary .ux-textspans',
                        '[itemprop="price"]',
                        '.x-price-primary span',
                        '.vim-price-display .ux-textspans',
                        '[class*="price"] .ux-textspans--BOLD',
                        '.ux-textspans--BOLD',
                        '[data-testid="x-price-primary"]',
                        '.x-price-primary',
                        '.mainPrice .ux-textspans',
                        '.mainPrice span',
                        '[class*="x-price"] span',
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        const txt = el?.innerText?.trim() || el?.getAttribute('content') || '';
                        if (txt && /^[US\$\\s]*\\d+[\\.,]\\d{2}/.test(txt)) {
                            return txt;
                        }
                    }
                    // Fallback: look for any element containing "$XX.XX"
                    const allText = document.body.innerText;
                    const pm = allText.match(/US\\s*\\$\\s*([\\d,]+\\.\\d{2})/);
                    if (pm) return 'US $' + pm[1];
                    const pm2 = allText.match(/\$([\\d,]+\\.\\d{2})/);
                    if (pm2) return '$' + pm2[1];
                    return '';
                }""")

                if price and price.strip():
                    data['price'] = price.strip()
                    jf.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                    fixed += 1
                    print(f"  -> [{price.strip()}]")
                else:
                    print(f"  -> NO PRICE FOUND")

            except Exception as e:
                print(f"  ERROR: {e}")

            if i < len(jsons) - 1:
                await asyncio.sleep(random.uniform(1.5, 2.5))

        await context.close()
        print(f"\nFixed {fixed}/{len(jsons)} prices")


if __name__ == '__main__':
    asyncio.run(fix_prices())
