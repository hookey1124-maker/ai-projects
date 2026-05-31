"""Check Terapeek / eBay Product Research access"""
import sys, json, asyncio, random
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

PROXY = "http://127.0.0.1:7897"
USER_DATA = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")


async def check():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            str(USER_DATA),
            headless=False,  # Need visible to check login state
            channel="chrome",
            proxy={"server": PROXY} if PROXY else None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        # Try to access Product Research
        print("Navigating to eBay Product Research...")
        try:
            await page.goto("https://www.ebay.com/sh/research", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            current_url = page.url
            print(f"Final URL: {current_url}")
            title = await page.title()
            print(f"Title: {title}")

            # Check if we can access the tool
            html = await page.content()
            if 'signin' in current_url.lower() or 'login' in current_url.lower():
                print("STATUS: NOT LOGGED IN - need to log in to eBay first")
            elif 'research' in current_url.lower() or 'product' in current_url.lower():
                print("STATUS: ACCESSIBLE - Product Research available")

                # Try searching for a product
                # The product research page has a search bar
                search_input = await page.query_selector('input[type="text"], input[placeholder*="search"], input[placeholder*="Search"]')
                if search_input:
                    print("Found search input!")
                    await search_input.fill("355448970865")
                    await asyncio.sleep(0.5)
                    # Press Enter or click search
                    await search_input.press("Enter")
                    await asyncio.sleep(5)

                    # Check results
                    page_title = await page.title()
                    print(f"After search - title: {page_title}")

                    # Save the results page
                    html2 = await page.content()
                    html_path = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\爬虫\terapeek_result.html")
                    html_path.write_text(html2[:200000], encoding='utf-8')
                    print(f"Saved to {html_path} ({len(html2)} chars)")
                else:
                    # Try direct API
                    print("Trying direct item lookup...")
                    await page.goto(f"https://www.ebay.com/sh/research/product/355448970865", wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(3)
                    current_url2 = page.url
                    print(f"Direct URL result: {current_url2}")
            else:
                print("STATUS: UNKNOWN - unexpected redirect")

            # Save for debugging
            html_path = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\爬虫\terapeek_page.html")
            html_path.write_text(html[:100000], encoding='utf-8')
            print(f"Saved page to {html_path}")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

        await asyncio.sleep(10)  # Keep browser open to review
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(check())
