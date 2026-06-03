"""Competitor Search — Stage 1-2: Query Generation + eBay Search

从 anchor canonical 数据构建 eBay 搜索查询 → 执行搜索 → 返回候选列表
"""
import sys
import json
import asyncio
import random
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

_DIR = Path(__file__).parent
_CONFIG = _DIR.parent / "config"

PROXY_SERVER = "http://127.0.0.1:7897"
USER_DATA_DIR = Path(r"c:\Users\Hardy\ai-projects\agent升级计划\browser_profile")
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

_QUERY_TEMPLATES = json.loads((_CONFIG / "query_templates.json").read_text(encoding="utf-8"))

_EXTRACT_JS = """() => {
    const results = [];
    const seen = new Set();

    document.querySelectorAll('a[href*="/itm/"]').forEach(a => {
        const href = a.href || '';
        const m = href.match(/\\/itm\\/(\\d+)/);
        if (!m || seen.has(m[1])) return;
        if (href.includes('/sch/') || href.includes('/usr/') || href.includes('/help/')) return;

        const itemId = m[1];
        let container = a;
        for (let i = 0; i < 10; i++) {
            container = container.parentElement;
            if (!container) break;

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
                        results.push({item_id: itemId, title: t.substring(0, 150),
                                      url: 'https://www.ebay.com/itm/' + itemId});
                        return;
                    }
                }
            }
        }

        let c2 = a.closest('li') || a.closest('[class*="result"]') || a.closest('[class*="card"]');
        if (!c2) c2 = a.parentElement?.parentElement;
        if (c2) {
            const allText = (c2.innerText || '').replace(/\\s+/g, ' ').trim();
            const lines = allText.split(/\\n|Sponsored|\\|/).filter(l => l.trim().length > 20 && l.trim().length < 200);
            const bestLine = lines.find(l =>
                /door|handle|window|glass|mirror|hinge|lock|latch|panel|trim|bumper|fender|running|step|rail/i.test(l) &&
                !/delivery|shipping|located|positive|returns|buy it now|best offer|free/i.test(l)
            );
            if (bestLine && !seen.has(itemId)) {
                seen.add(itemId);
                results.push({item_id: itemId, title: bestLine.trim().substring(0, 150),
                              url: 'https://www.ebay.com/itm/' + itemId});
            }
        }
    });
    return results;
}"""


def build_queries(anchor_canonical: dict) -> list[str]:
    """从 anchor canonical 数据构建 1-2 条 eBay 搜索查询字符串"""
    cls = anchor_canonical.get("classification", {})
    vehicle = cls.get("vehicle", {}).get("value", {}) or {}
    makes = vehicle.get("makes", [])
    models = vehicle.get("models", [])
    years = vehicle.get("years", []) or vehicle.get("year_range", [])

    product_type = cls.get("product_type", {}).get("value") or ""
    cab = cls.get("cab", {}).get("value") or ""
    position = cls.get("position", {}).get("value") or ""
    finish = cls.get("finish", {}).get("value") or ""

    if not makes or not models:
        return []

    # 取第一个 make/model + 第一个年份
    make = makes[0]
    model = models[0]
    year = years[0] if years else ""
    year_str = str(year) if year else ""

    # 匹配查询模板
    template = _QUERY_TEMPLATES.get(product_type, _QUERY_TEMPLATES.get("default", {}))
    variables = template.get("variables", [])

    def _fill(tmpl: str) -> str:
        s = tmpl
        for var in variables:
            val = {
                "year": year_str,
                "make": make,
                "model": model,
                "cab": cab or "",
                "position": position or "",
                "finish": finish or "",
                "product_type": product_type or "",
            }.get(var, "")
            s = s.replace(f"{{{var}}}", str(val))
        # 清理多余空格
        return " ".join(s.split())

    queries = []
    primary = template.get("primary", "")
    fallback = template.get("fallback", "")

    # 只有变量齐全时才用 primary
    primary_missing = any(
        v in variables and not {"year": year_str, "make": make, "model": model,
                                "cab": cab, "position": position, "finish": finish,
                                "product_type": product_type}.get(v, "")
        for v in variables
    )

    if primary and not primary_missing:
        queries.append(_fill(primary))
    if fallback:
        queries.append(_fill(fallback))

    # 去重
    seen = set()
    unique = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique.append(q)
    return unique


async def search_ebay(query: str, max_results: int = 60) -> list[dict]:
    """执行单条 eBay 搜索，返回 {item_id, title, url} 列表"""
    encoded = query.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={encoded}&_sop=15&LH_BIN=1&_dmd=1&LH_PrefLoc=1"

    results = []
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            str(USER_DATA_DIR),
            headless=True,
            channel="chrome",
            proxy={"server": PROXY_SERVER},
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        # Cookie 预热（美国市场）
        await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
        await page.evaluate("""() => {
            const expires = new Date(Date.now() + 365 * 86400000).toUTCString();
            document.cookie = 'shs=US;expires=' + expires + ';path=/;domain=.ebay.com';
            document.cookie = 'shss=NC;expires=' + expires + ';path=/;domain=.ebay.com';
            document.cookie = 'shzip=27513;expires=' + expires + ';path=/;domain=.ebay.com';
        }""")
        await asyncio.sleep(1.5)

        await page.goto(url, wait_until="load", timeout=60000)
        await asyncio.sleep(random.uniform(2, 3))

        items = await page.evaluate(_EXTRACT_JS)
        await ctx.close()
        results = items

    return results[:max_results]


async def discover_candidates(anchor_canonical: dict, max_results: int = 60) -> list[dict]:
    """主入口：构建查询 → eBay 搜索 → 合并去重 → 返回 {item_id, title, url} 列表"""
    queries = build_queries(anchor_canonical)
    if not queries:
        return []

    all_results = {}
    for qi, q in enumerate(queries):
        items = await search_ebay(q, max_results=max_results)
        for item in items:
            iid = item["item_id"]
            if iid not in all_results:
                all_results[iid] = item

        if len(all_results) >= max_results:
            break
        if qi < len(queries) - 1:
            await asyncio.sleep(random.uniform(1, 2))

    result_list = list(all_results.values())
    return result_list[:max_results]
