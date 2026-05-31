"""Playwright 通用抓取模板 — URL → DOM → 结构化 JSON

前置依赖（已安装）：
  playwright          — 浏览器自动化
  playwright_stealth  — 反检测

用法：
  python playwright_template.py <url>
  python playwright_template.py <url> --wait 5000
  python playwright_template.py <url> -o result.json
"""
import sys
import json
import asyncio
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

try:
    from playwright_stealth import Stealth
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False
    Stealth = None

# ── 配置 ─────────────────────────────────────────────
PROXY = "http://127.0.0.1:7897"
BROWSER_PROFILE = Path(r"C:\Users\Administrator\Desktop\AI项目\agent升级计划\browser_profile")


# ═══════════════════════════════════════════════════════════
# 1. JS 提取 — 在浏览器里直接读 DOM（改成你自己的选择器）
# ═══════════════════════════════════════════════════════════
EXTRACT_JS = """() => {
    const text = (sel) => document.querySelector(sel)?.innerText?.trim() || '';

    let images = [];
    document.querySelectorAll('.ux-image-carousel-item img, .ux-image-carousel img')
        .forEach(img => { const s = img.src || img.dataset?.src; if (s) images.push(s); });

    let specs = {};
    document.querySelectorAll('.ux-labels-values--inline .ux-labels-values__labels, .ux-labels-values__labels')
        .forEach(el => {
            const label = el.innerText.trim().replace(/:$/, '');
            const val = el.nextElementSibling?.innerText?.trim();
            if (label && val) specs[label] = val;
        });

    return {
        title: text('h1'),
        price: text('[data-testid="x-price-primary"] span') || text('.x-price-primary'),
        condition: text('.x-item-condition-text'),
        quantity: text('[data-testid="x-quantity"]'),
        sold: text('.x-quantity__availability'),
        images: images.slice(0, 10),
        specs: specs,
        url: location.href,
    };
}"""


async def scrape(url: str, wait_ms: int = 3000) -> dict:
    """URL → Playwright → DOM → JSON"""
    async with async_playwright() as p:
        # 反检测 + 持久化浏览器（复用 cookie / localStorage，防风控）
        context_kwargs = {
            'user_data_dir': str(BROWSER_PROFILE),
            'headless': True,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--no-first-run', '--no-default-browser-check',
                '--window-size=1920,1080',
            ],
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36",
        }
        if PROXY:
            context_kwargs['proxy'] = {"server": PROXY}

        # Stealth 注入（屏蔽 webdriver 痕迹）
        if HAS_STEALTH:
            async with Stealth().use_async(p) as playwright:
                context = await playwright.chromium.launch_persistent_context(**context_kwargs)
        else:
            context = await p.chromium.launch_persistent_context(**context_kwargs)

        page = await context.new_page()

        # eBay 地域 cookie
        await page.context.add_cookies([
            {"name": "shs", "value": "US", "domain": ".ebay.com", "path": "/"},
            {"name": "shss", "value": "NC", "domain": ".ebay.com", "path": "/"},
            {"name": "shzip", "value": "27513", "domain": ".ebay.com", "path": "/"},
        ])

        # 2. 打开网页
        print(f"打开: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(wait_ms)

        # 3. 执行 JS 抓 DOM
        data = await page.evaluate(EXTRACT_JS)

        result = {
            "url": data.get("url", url),
            "title": data.get("title", ""),
            "price": data.get("price", ""),
            "condition": data.get("condition", ""),
            "quantity": data.get("quantity", ""),
            "sold": data.get("sold", ""),
            "images": data.get("images", []),
            "specs": data.get("specs", {}),
            "scraped_at": await page.evaluate("() => new Date().toISOString()"),
        }

        await context.close()
        return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Playwright 通用抓取模板")
    parser.add_argument("url", help="目标 URL")
    parser.add_argument("--wait", type=int, default=3000, help="额外等待毫秒（默认 3000）")
    parser.add_argument("-o", "--output", default=None, help="保存 JSON 文件路径")
    args = parser.parse_args()

    result = asyncio.run(scrape(args.url, args.wait))
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n已保存: {out}")
