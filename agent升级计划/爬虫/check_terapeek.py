"""Check Terapeek / eBay Product Research access for sales data"""
import sys, json, asyncio, random
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")


async def check():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA),
            headless=True,
            channel="chrome",
            args=['--disable-blink-features=AutomationControlled', '--window-size=1920,1080'],
            viewport={'width': 1920, 'height': 1080},
            locale='en-US', timezone_id='America/New_York',
            proxy={'server': PROXY},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Warmup + login check
        print("Checking eBay login state...")
        await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Check if logged in
        logged_in = await page.evaluate("""() => {
            const signIn = document.querySelector('[href*="signin"], a[href*="SignIn"]');
            const userName = document.querySelector('#gh-ug, [data-testid="x-header-user"], .gh-ug');
            return {
                hasSignInLink: !!signIn,
                userName: userName?.innerText?.trim() || 'not found'
            };
        }""")
        print(f"  Login: {json.dumps(logged_in)}")

        # Try Product Research
        print("\nNavigating to Product Research...")
        await page.goto("https://www.ebay.com/sh/research", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        current_url = page.url
        title = await page.title()
        print(f"  URL: {current_url}")
        print(f"  Title: {title}")

        if 'signin' in current_url.lower():
            print("\n*** NOT LOGGED IN - Terapeek requires eBay login ***")
            print("Please log in to eBay first in the browser profile.")
            await context.close()
            return

        if '/sh/research' in current_url:
            print("\n*** Product Research is ACCESSIBLE! ***")

            # Try to search for a product
            try:
                search_box = await page.query_selector('input[type="text"]')
                if not search_box:
                    search_box = await page.query_selector('input')
                if search_box:
                    await search_box.fill("355448970865")
                    await search_box.press("Enter")
                    await asyncio.sleep(5)

                    # Check what we see
                    page_text = await page.evaluate("document.body.innerText.substring(0, 2000)")
                    print(f"  Page text: {page_text[:500]}...")

                    # Look for sales data
                    sales = await page.evaluate("""() => {
                        const body = document.body.innerText;
                        const patterns = [
                            /sold\\s+\\d+/i, /(\\d+)\\s+sold/i,
                            /sales.*\\d+/i, /revenue/i,
                            /sell\\s*through/i, /(\\d+)\\s*units/i
                        ];
                        const matches = [];
                        for (const p of patterns) {
                            const m = body.match(p);
                            if (m) matches.push(m[0]);
                        }
                        return matches;
                    }""")
                    print(f"  Sales patterns: {sales}")
                else:
                    print("  No search box found")
            except Exception as e:
                print(f"  Error searching: {e}")

            # Save page
            html = await page.content()
            html_path = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\爬虫\terapeek_page.html")
            html_path.write_text(html[:200000], encoding='utf-8')
            print(f"  Saved to {html_path}")

        await context.close()


if __name__ == '__main__':
    asyncio.run(check())
