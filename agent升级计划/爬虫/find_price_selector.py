"""Quick: find the correct price CSS selector on current eBay page"""
import sys, json, asyncio, random
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
from pathlib import Path

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"c:\Users\Hardy\ai-projects\agent升级计划\browser_profile")

async def find_price():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA),
            headless=True, channel="chrome",
            proxy={"server": PROXY},
            viewport={'width': 1920, 'height': 1080},
            locale='en-US', timezone_id='America/New_York',
        )
        page = context.pages[0] if context.pages else await context.new_page()
        try:
            await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
            await page.evaluate("""() => {
                const e = new Date(Date.now() + 365*86400000).toUTCString();
                document.cookie = 'shs=US;expires='+e+';path=/;domain=.ebay.com';
            }""")
        except: pass

        await page.goto("https://www.ebay.com/itm/355448970865", wait_until="load", timeout=45000)
        await asyncio.sleep(3)

        result = await page.evaluate("""() => {
            const findings = [];

            // Check all common price selectors
            const selectors = [
                '[data-testid="x-price-primary"]',
                '.x-price-primary',
                '[itemprop="price"]',
                '.vim-price-display',
                '.mainPrice',
                '.display-price',
                '[class*="x-price"]',
                '[class*="price"]',
            ];

            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    findings.push({
                        selector: sel,
                        text: el.innerText?.trim().substring(0, 100),
                        tag: el.tagName,
                        className: el.className,
                        outerHTML: el.outerHTML?.substring(0, 200)
                    });
                }
            }

            // Also find any element whose text looks like a price
            const allElements = document.querySelectorAll('span, div');
            for (const el of allElements) {
                const txt = el.innerText?.trim() || '';
                if (/^US\\s*\\$\\s*\\d+[\\.,]\\d{2}$/.test(txt)) {
                    findings.push({
                        selector: 'FOUND_BY_TEXT',
                        text: txt,
                        tag: el.tagName,
                        className: el.className,
                        outerHTML: el.outerHTML?.substring(0, 200)
                    });
                }
            }

            return findings;
        }""")

        print("Price element findings:")
        for f in result:
            print(f"  [{f['selector']}] {f['tag']}.{f['className']}")
            print(f"    text: [{f['text']}]")
            print(f"    html: {f.get('outerHTML','')[:150]}")
            print()

        await context.close()

if __name__ == '__main__':
    asyncio.run(find_price())
