"""快速提取单个 eBay 产品标题和关键词"""
import sys, json, asyncio, re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")


async def quick_fetch(url: str):
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

        # Warmup
        try:
            await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1)
        except:
            pass

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)

        data = await page.evaluate("""() => {
            const get = (sel) => {
                const el = document.querySelector(sel);
                return el?.innerText?.trim() || '';
            };
            const getAll = (sel) => {
                return Array.from(document.querySelectorAll(sel)).map(el => el.innerText?.trim() || '');
            };

            // Expand specs
            const btns = document.querySelectorAll('button');
            for (const btn of btns) {
                const txt = btn.innerText?.trim() || '';
                if (/(?:see\\s*all|show\\s*more)/i.test(txt)) {
                    btn.click();
                }
            }

            // Title
            const title = get('h1.x-item-title') || get('h1.it-ttl') || get('[data-testid="x-item-title"]') || document.title;

            // Price
            const price = get('.x-price-primary span') || get('.ux-textspans--BOLD') || '';

            // Item specifics
            const specs = {};
            const labels = document.querySelectorAll('.ux-labels-values__labels .ux-textspans, .ux-layout-section__row .ux-labels-values__labels-content .ux-textspans');
            const values = document.querySelectorAll('.ux-labels-values__values .ux-textspans, .ux-layout-section__row .ux-labels-values__values-content .ux-textspans');

            // Try structured approach
            const rows = document.querySelectorAll('.ux-layout-section-evo__row, .ux-labels-values__row');
            rows.forEach(row => {
                const label = row.querySelector('.ux-labels-values__labels .ux-textspans');
                const value = row.querySelector('.ux-labels-values__values .ux-textspans');
                if (label && value) {
                    const k = label.innerText.replace(/:/g, '').trim();
                    const v = value.innerText.trim();
                    if (k && v) specs[k] = v;
                }
            });

            // Images
            const images = [];
            const imgs = document.querySelectorAll('.ux-image-carousel-item img, [data-testid="ux-img-carousel"] img, .img img[src*="ebayimg"]');
            imgs.forEach(img => {
                const src = img.src || img.getAttribute('data-src') || '';
                if (src && src.includes('ebayimg') && !images.includes(src)) {
                    images.push(src.replace(/\\/s-l\\d+\\./, '/s-l500.'));
                }
            });

            return { title, price, specs, images: [...new Set(images)].slice(0, 10) };
        }""")

        await ctx.close()
        return data


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.ebay.com/itm/355448970865"
    data = asyncio.run(quick_fetch(url))
    print(json.dumps(data, ensure_ascii=False, indent=2))
