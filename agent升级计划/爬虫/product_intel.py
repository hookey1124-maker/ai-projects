"""市场情报汇总 — 批量爬取母文件下所有竞品链接，交叉分析输出 market_intel.json

用法:
  python product_intel.py <mother_dir>                     # 分析单个母文件
  python product_intel.py <mother_dir> --max 8             # 最多爬取 8 个链接
  python product_intel.py <mother_dir> --dry-run           # 仅分析已有 JSON，不爬取
  python product_intel.py <mother_dir> --dry-run --vision  # 启用 GLM-4V 视觉分类
"""
import sys
import json
import re
import base64
import asyncio
import random
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

# Fix Windows GBK encoding
_AGENT_DIR = Path(__file__).parent.parent
if str(_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_DIR))
from engine.canonicalize import classify_product, classify_product_legacy
from engine.conflict import detect_conflicts
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from playwright_stealth import Stealth
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False
    Stealth = None

# ── Config ─────────────────────────────────────────────
PROXY_SERVER = "http://127.0.0.1:7897"
USER_DATA_DIR = Path(r"c:\Users\Hardy\ai-projects\agent升级计划\browser_profile")
OUTPUT_ROOT = Path(r"c:\Users\Hardy\ai-projects\产品卖点主图和信息生成")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

# ── eBay 页面解析 JS（完整版，含适配表+卖家+物流）──────────
EXTRACT_JS = r"""() => {
    const get = (sel) => {
        const el = document.querySelector(sel);
        return el?.innerText?.trim() || '';
    };

    // ── Item Specifics：先展开 "See all" 再提取 ──
    const expandSpecs = () => {
        // eBay 常见的折叠按钮：See all / Show more / See full description
        const btns = document.querySelectorAll('button');
        for (const btn of btns) {
            const txt = btn.innerText?.trim() || '';
            if (/(?:see\s*all|show\s*more|see\s*full|view\s*more|expand|more\s*about)/i.test(txt)) {
                btn.click();
                return true;
            }
        }
        // 也尝试点击展开图标（有的版本用非标准按钮）
        const expandIcons = document.querySelectorAll(
            '.ux-labels-values--expand, [data-testid="x-specs-expand"], '
            + '.vim-expand-more, [aria-label*="more"], [aria-label*="expand"], '
            + '.ux-expand-icon, svg.ux-chevron-down, [data-testid="x-see-all"]'
        );
        for (const el of expandIcons) {
            el.click();
            return true;
        }
        return false;
    };
    expandSpecs();

    // 等待展开渲染（最多 1 秒）
    const start = Date.now();
    let oldLen = 0;
    while (Date.now() - start < 1000) {
        const current = document.querySelectorAll('.ux-labels-values__labels').length;
        if (current > oldLen) { oldLen = current; } else if (current > 0) { break; }
    }

    let specs = {};
    document.querySelectorAll('.ux-labels-values__labels').forEach(el => {
        const label = el.innerText.trim().replace(/:$/, '');
        const val = el.nextElementSibling?.innerText?.trim();
        if (label && val) specs[label] = val;
    });

    if (Object.keys(specs).length === 0) {
        document.querySelectorAll('.ux-labels-values--inline .ux-labels-values__labels, .item-conditions tr').forEach(el => {
            const label = el.innerText.trim().replace(/:$/, '');
            const val = el.nextElementSibling?.innerText?.trim();
            if (label && val) specs[label] = val;
        });
    }

    let images = [];
    document.querySelectorAll('.ux-image-carousel-item img, .ux-image-carousel img').forEach(img => {
        const src = img.src || img.dataset?.src || '';
        if (src && !images.includes(src)) images.push(src);
    });

    // 卖家信息
    let sellerUsername = '';
    const descIframe = document.querySelector('#desc_ifr');
    if (descIframe?.src) {
        const um = descIframe.src.match(new RegExp('[?&]seller=([^&]+)'));
        if (um) sellerUsername = um[1];
    }

    const sellerSection = document.querySelector('[data-testid="x-seller-name"]')
        || document.querySelector('.x-seller-name')
        || document.querySelector('.vim-seller')
        || document.querySelector('.ux-seller-section');

    let sellerName = '';
    let sellerUrl = '';
    if (sellerSection) {
        const sellerLink = sellerSection.querySelector('a[href*="/str/"]')
            || sellerSection.querySelector('a[href*="/sch/"]')
            || sellerSection.querySelector('a');
        if (sellerLink) {
            sellerName = sellerLink.innerText?.trim() || '';
            sellerUrl = sellerLink.href || '';
        }
    }
    if (!sellerName) sellerName = sellerUsername;
    if (!sellerUrl && sellerUsername) sellerUrl = 'https://www.ebay.com/str/' + sellerUsername;

    // 卖家反馈
    let sellerFeedback = '';
    let sellerFeedbackPct = '';
    const feedbackEl = document.querySelector('[data-testid="x-seller-feedback"], .x-seller-feedback');
    if (feedbackEl) {
        const txt = feedbackEl.innerText || '';
        const fbMatch = txt.match(/([\\d,.]+)\\s*([\\d,.]+)%/);
        if (fbMatch) { sellerFeedback = fbMatch[1]; sellerFeedbackPct = fbMatch[2]; }
    }

    // 卖家其他商品链接
    let sellerItemsUrl = '';
    const seeAllLink = document.querySelector('a[href*="_ssn="]')
        || document.querySelector('[data-testid="x-seller-other-items"] a')
        || (sellerSection && sellerSection.querySelector('a[href*="_ssn="]'));
    if (seeAllLink?.href) sellerItemsUrl = seeAllLink.href;

    // 兼容适配表
    let compatibility = [];
    const compatTable = document.querySelector('.ux-layout-section--compatibility table')
        || document.querySelector('[data-testid="x-compatibility"] table');
    if (compatTable) {
        const headers = [];
        compatTable.querySelectorAll('thead th, thead td').forEach(th => headers.push(th.innerText.trim()));
        compatTable.querySelectorAll('tbody tr').forEach(tr => {
            const row = {};
            tr.querySelectorAll('td').forEach((td, i) => {
                row[headers[i] || 'col' + i] = td.innerText.trim();
            });
            if (Object.keys(row).length > 0) compatibility.push(row);
        });
    }
    if (compatibility.length === 0) {
        const compatSection = document.querySelector('.ux-layout-section--compatibility')
            || document.querySelector('[data-testid="x-compatibility"]');
        if (compatSection) {
            compatSection.querySelectorAll('.ux-labels-values__labels, .ux-labels-values--inline .ux-labels-values__labels').forEach(el => {
                const label = el.innerText.trim().replace(/:$/, '');
                const val = el.nextElementSibling?.innerText?.trim();
                if (label && val) compatibility.push({ [label]: val });
            });
        }
    }

    // 配送/退货/支付
    let shipping = get('[data-testid="x-shipping-cost"]') || get('.x-shipping-cost') || get('.ux-labels-values--shipping');
    let returns = get('[data-testid="x-return-policy"]') || get('.x-return-policy');
    let payment = get('[data-testid="x-payment-methods"]') || get('.x-payment-methods');

    // 库存/销量
    let quantity = get('[data-testid="x-quantity-primary-text"]') || get('.x-quantity-primary-text') || '';
    let sold = get('[data-testid="x-quantity-secondary-text"]') || '';

    // categoryId
    let categoryId = '';
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
        try {
            const ld = JSON.parse(s.textContent);
            if (ld['@type'] === 'BreadcrumbList' && ld.itemListElement) {
                const items = ld.itemListElement;
                for (let j = items.length - 1; j >= 0; j--) {
                    const it = items[j];
                    const itemUrl = typeof it.item === 'string' ? it.item : it.item?.['@id'];
                    if (itemUrl) {
                        const m = itemUrl.match(/\/b\/[^/]+\/(\d+)/);
                        if (m) { categoryId = m[1]; break; }
                    }
                }
            }
        } catch(e) {}
    });

    return {
        title: get('h1'),
        price: get('[data-testid="x-price-primary"]') || get('.x-price-primary span') || get('.x-price-primary'),
        condition: get('.x-item-condition-text'),
        seller: sellerName || sellerUsername,
        sellerUsername: sellerUsername,
        sellerUrl: sellerUrl,
        sellerFeedback: sellerFeedback,
        sellerFeedbackPct: sellerFeedbackPct,
        sellerItemsUrl: sellerItemsUrl,
        quantity: quantity,
        sold: sold,
        imageCount: document.querySelectorAll('.ux-image-carousel-item').length || images.length,
        specs: specs,
        images: images.slice(0, 8),
        compatibility: compatibility,
        shipping: shipping,
        returns: returns,
        payment: payment,
        categoryId: categoryId,
        descriptionIframeSrc: (document.querySelector('#desc_ifr') || {}).src || '',
    };
}"""


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# ── 爬虫部分 ──────────────────────────────────────────

async def scrape_batch(urls: list, chunk_size: int = 5, save_dir=None) -> list:
    """批量抓取 eBay 商品，分批执行避免长时间占用浏览器。每批完成即保存。"""
    all_results = []
    from pathlib import Path

    for chunk_start in range(0, len(urls), chunk_size):
        chunk = urls[chunk_start:chunk_start + chunk_size]
        log(f"启动浏览器批次 [{chunk_start+1}-{min(chunk_start+chunk_size, len(urls))}/{len(urls)}]")

        async with async_playwright() as p:
            context_kwargs = {
                'user_data_dir': str(USER_DATA_DIR),
                'headless': True,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-first-run', '--no-default-browser-check',
                    f'--window-size=1920,1080',
                ],
                'user_agent': random.choice(USER_AGENTS),
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'en-US',
                'timezone_id': 'America/New_York',
                'proxy': {'server': PROXY_SERVER},
            }

            if HAS_STEALTH:
                async with Stealth().use_async(p) as playwright:
                    context = await playwright.chromium.launch_persistent_context(**context_kwargs)
                    chunk_results = await _do_scrape(context, chunk)
            else:
                context = await p.chromium.launch_persistent_context(**context_kwargs)
                chunk_results = await _do_scrape(context, chunk)

        all_results.extend(chunk_results)
        log(f"批次完成: {len(chunk_results)} 条")

        # 每批完成立即保存，防止中间崩溃丢失数据
        if save_dir:
            for data in chunk_results:
                if 'item_id' in data and 'error' not in data:
                    out_file = Path(save_dir) / f"product_{data['item_id']}.json"
                    out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                    log(f"  saved: {out_file.name}")

        # 批次间隔
        if chunk_start + chunk_size < len(urls):
            await asyncio.sleep(5)

    return all_results


async def _do_scrape(context, urls):
    page = context.pages[0] if context.pages else await context.new_page()

    # 预热：设置美国 cookie（最多重试 3 次）
    for attempt in range(3):
        try:
            await page.goto("https://www.ebay.com", wait_until="domcontentloaded", timeout=30000)
            await page.evaluate("""() => {
                const expires = new Date(Date.now() + 365 * 86400000).toUTCString();
                document.cookie = 'shs=US;expires=' + expires + ';path=/;domain=.ebay.com';
                document.cookie = 'shss=NC;expires=' + expires + ';path=/;domain=.ebay.com';
                document.cookie = 'shzip=27513;expires=' + expires + ';path=/;domain=.ebay.com';
            }""")
            await asyncio.sleep(1.5)
            break
        except Exception as e:
            log(f"  预热失败 (attempt {attempt+1}): {e}")
            if attempt == 2:
                raise
            await asyncio.sleep(3)

    results = []
    for i, url in enumerate(urls):
        log(f"[{i+1}/{len(urls)}] {url}")
        for retry in range(2):
            try:
                await page.goto(url, wait_until="load", timeout=60000)
                await asyncio.sleep(random.uniform(2, 4))
                data = await page.evaluate(EXTRACT_JS)
                item_id = re.search(r'/itm/(\d+)', url)
                data['item_id'] = item_id.group(1) if item_id else ''
                data['url'] = url
                data['scraped_at'] = datetime.now().isoformat()

                # 提取 description 文本（从 #desc_ifr iframe）
                desc_iframe_src = data.pop('descriptionIframeSrc', '')
                if desc_iframe_src:
                    try:
                        desc_page = await context.new_page()
                        await desc_page.goto(desc_iframe_src, wait_until="domcontentloaded", timeout=15000)
                        desc_text = await desc_page.evaluate(
                            "() => document.body?.innerText?.replace(/\\s+/g, ' ').trim() || ''"
                        )
                        data['description_text'] = desc_text[:5000]
                        await desc_page.close()
                    except Exception:
                        data['description_text'] = ''
                else:
                    data['description_text'] = ''

                # 通过 finders API 获取完整兼容适配表
                category_id = data.get('categoryId', '')
                if data['item_id'] and category_id:
                    try:
                        all_rows = []
                        offset = 0
                        while offset < 500:
                            api_url = f"https://www.ebay.com/g/api/finders?module_groups=PART_FINDER&referrer=VIEWITEM&offset={offset}&module=COMPATIBILITY_TABLE"
                            payload = {
                                "scopedContext": {
                                    "catalogDetails": {
                                        "itemId": data['item_id'],
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
                    except Exception:
                        pass  # API失败时保留页面DOM提取的compatibility

                results.append(data)
                break
            except Exception as e:
                if retry == 0:
                    log(f"  [RETRY] {e}")
                    await asyncio.sleep(3)
                else:
                    log(f"  [ERROR] {e}")
                    results.append({"url": url, "error": str(e)})

        if i < len(urls) - 1:
            await asyncio.sleep(random.uniform(2, 4))

    await context.close()
    return results


# ── 产品分类提取 ──────────────────────────────────────

def _extract_structure_type(title: str, specs: dict) -> dict:
    """检测一体式/分体式，返回 {type, source}"""
    text = (title + " " + " ".join(specs.values())).lower()
    if re.search(r"\bone[\s-]piece\b|\bsingle[\s-]piece\b|\b1pc\s*design\b", text):
        return {"structure": "One-Piece", "structure_source": "text"}
    if re.search(r"\bmulti[\s-]piece\b|\bassembly\b|\bassemble\b|\bseparate\b", text):
        return {"structure": "Multi-Piece", "structure_source": "text"}
    return {"structure": "Unknown", "structure_source": "unknown"}


def _classify_product(product: dict) -> dict:
    """完整产品分类 — 使用 engine 多来源融合"""
    return classify_product_legacy(product)


def _is_valid_competitor(anchor_class: dict, other_class: dict,
                         anchor_specs: dict | None = None,
                         other_specs: dict | None = None) -> tuple:
    """规则0：检查是否为有效竞品。返回 (is_valid, exclude_reason)"""

    # ── 安装方式：adhesive vs bolt-on（在方位之前判断，优先级更高）──
    _ATTACHMENT_KEYS = ["Attachment Type", "Mounting Type", "Installation Type", "Fitment Type"]
    _ADHESIVE_TERMS = ["adhesive", "stick-on", "stick on", "tape", "3m", "self-adhesive",
                       "glue", "double-sided", "peel and stick"]

    def _is_adhesive(specs: dict | None) -> bool:
        if not specs:
            return False
        for key in _ATTACHMENT_KEYS:
            val = str(specs.get(key, "")).lower()
            for term in _ADHESIVE_TERMS:
                if term in val:
                    return True
        return False

    anchor_adhesive = _is_adhesive(anchor_specs)
    other_adhesive = _is_adhesive(other_specs)
    if other_adhesive and not anchor_adhesive:
        return False, {"field": "attachment_type", "reason": "安装方式不同",
                       "anchor_value": "Bolt-on/Clip-on", "competitor_value": "Adhesive"}

    # ── 方位兼容性 ──
    # "Rear" 和 "Rear-Driver-Side" 兼容（后者是前者的子集）
    # "Front" 和 "Front-Driver-Side" 兼容
    def _pos_compatible(a: str, b: str) -> bool:
        if a == b:
            return True
        if a == "Unknown" or b == "Unknown":
            return True
        # 把精确方位归一化
        broader = {"Rear-Driver-Side": ["Rear", "Left", "Driver-Side"],
                   "Rear-Passenger-Side": ["Rear", "Right", "Passenger-Side"],
                   "Front-Driver-Side": ["Front", "Left", "Driver-Side"],
                   "Front-Passenger-Side": ["Front", "Right", "Passenger-Side"]}
        for precise, broad_list in broader.items():
            if a == precise and b in broad_list:
                return True
            if b == precise and a in broad_list:
                return True
        # 通用：拆分组件，若一方是另一方的子集则兼容
        # 如 "Rear-Both-Sides-Lower" vs "Rear" → Rear 是子集，兼容
        # 如 "Front-Rear" vs "Front" → Front 是子集，兼容
        a_parts = set(a.split("-"))
        b_parts = set(b.split("-"))
        if a_parts.issubset(b_parts) or b_parts.issubset(a_parts):
            return True
        return False

    # ── 表面处理等价 ──
    def _finish_compatible(a: str, b: str) -> bool:
        if a == b:
            return True
        if a == "Unknown" or b == "Unknown":
            return True
        equivalents = [
            {"Dark", "Black", "Matte-Black", "Gloss-Black", "Textured-Black", "Glossy", "Glossy-Black", "Gloss-Black", "Piano-Black"},
            {"Chrome", "Polished"},
        ]
        for eq_set in equivalents:
            if a in eq_set and b in eq_set:
                return True
        return False

    # ── 严格字段：锚点已知但竞品 Unknown → 排除 ──
    strict_checks = [
        ("count", "关键字段未识别"),
        ("finish", "关键字段未识别"),
    ]
    for field, reason in strict_checks:
        a_val = anchor_class.get(field, "Unknown")
        o_val = other_class.get(field, "Unknown")
        if a_val != "Unknown" and o_val == "Unknown":
            return False, {"field": field, "reason": reason,
                           "anchor_value": a_val, "competitor_value": "Unknown"}

    # sub_type: 只在 specs 的 Type 字段也为空时才排除
    # 很多 listing 有 Type=Curved/Flat/Rear Diffuser 但没填 Fitment Type
    a_sub = anchor_class.get("sub_type", "Unknown")
    o_sub = other_class.get("sub_type", "Unknown")
    if a_sub != "Unknown" and o_sub == "Unknown":
        o_type = (other_specs or {}).get("Type", "")
        if not o_type:
            return False, {"field": "sub_type", "reason": "关键字段未识别",
                           "anchor_value": a_sub, "competitor_value": "Unknown"}

    # ── 关键 Specs 字段比对 ──
    # Material: 泛称/子类兼容（Plastic ≈ ABS Plastic ≈ Premium ABS）
    _MATERIAL_GENERICS = {
        "plastic": ["abs", "polycarbonate", "pc", "nylon", "pp", "pu", "tpe", "pvc"],
        "metal": ["aluminum", "steel", "stainless steel", "zinc", "zinc alloy"],
    }
    a_mat = (anchor_specs or {}).get("Material", "")
    o_mat = (other_specs or {}).get("Material", "")
    if a_mat and o_mat:
        a_norm = str(a_mat).lower().strip()
        o_norm = str(o_mat).lower().strip()
        if a_norm != o_norm:
            compatible = False
            for generic, subtypes in _MATERIAL_GENERICS.items():
                a_is_gen = (a_norm == generic or any(s in a_norm for s in subtypes))
                o_is_gen = (o_norm == generic or any(s in o_norm for s in subtypes))
                if a_is_gen and o_is_gen:
                    compatible = True
                    break
            if not compatible:
                return False, {"field": "material", "reason": "材质不同",
                               "anchor_value": a_mat, "competitor_value": o_mat}

    # Size: 直接比对
    a_size = (anchor_specs or {}).get("Size", "")
    o_size = (other_specs or {}).get("Size", "")
    if a_size and o_size:
        if str(a_size).lower().strip() != str(o_size).lower().strip():
            return False, {"field": "size", "reason": "尺寸不同",
                           "anchor_value": a_size, "competitor_value": o_size}

    # ── 宽松字段：双方都已知才比较，Unknown 放行 ──
    lenient_checks = [
        ("position", "方位不同", _pos_compatible),
        ("count", "件数不同", None),
        ("finish", "表面处理/颜色不同", _finish_compatible),
        ("sub_type", "产品子类型不同", None),
        ("door_config", "车门配置不同（2-door / 4-door-half / 4-door-full）", None),
    ]
    for field, reason, compat_fn in lenient_checks:
        a_val = anchor_class.get(field, "Unknown")
        o_val = other_class.get(field, "Unknown")
        if a_val != "Unknown" and o_val != "Unknown":
            if compat_fn:
                if not compat_fn(a_val, o_val):
                    return False, {"field": field, "reason": reason,
                                   "anchor_value": a_val, "competitor_value": o_val}
            elif a_val != o_val:
                return False, {"field": field, "reason": reason,
                               "anchor_value": a_val, "competitor_value": o_val}
    return True, None

def _extract_year_range(title: str) -> tuple:
    """从标题提取适配年份区间，返回 (start, end) 或 None"""
    patterns = [
        r'(?:For|Fit(?:s)?|Compatible\s+(?:with\s+)?)\s*(\d{2,4})\s*[-–]\s*(\d{2,4})',
        r'\b(\d{2})\s*[-–]\s*(\d{2})\b',
        r'\b(\d{4})\s*[-–]\s*(\d{2,4})\b',
    ]
    for pat in patterns:
        m = re.search(pat, title, re.IGNORECASE)
        if m:
            y1 = int(m.group(1))
            y2 = int(m.group(2))
            if y2 < 100:
                y2 += 2000 if y2 < 50 else 1900
            if y1 < 100:
                y1 += 2000 if y1 < 50 else 1900
            return (min(y1, y2), max(y1, y2))
    return None


def _extract_vehicle_makes(title: str) -> set:
    """从标题提取适配车型品牌+型号，返回 set of (make, model)"""
    makes = [
        "Ford", "Chevy", "Chevrolet", "GMC", "Dodge", "Ram", "Jeep", "Cadillac",
        "Toyota", "Honda", "Nissan", "Mazda", "BMW", "Mercedes", "Audi", "Volkswagen",
        "Subaru", "Hyundai", "Kia", "Volvo", "Tesla", "Rivian", "Chrysler", "Buick",
        "Lincoln", "Lexus", "Acura", "Infiniti", "Porsche", "Land Rover", "Jaguar",
    ]
    found = set()
    title_lower = title.lower()
    for make in makes:
        if make.lower() in title_lower:
            # 尝试提取紧跟在品牌后的车型名
            pat = rf'\b{re.escape(make)}\s+([A-Z][a-zA-Z0-9\-\.]+(?:\s+[A-Z][a-zA-Z0-9\-\.]+)?)'
            m = re.search(pat, title, re.IGNORECASE)
            if m:
                model = m.group(1).strip()
                # 排除年份数字
                if not re.match(r'^\d{2,4}$', model):
                    found.add((make, model))
                    continue
            found.add((make, "UNKNOWN"))
    return found


def _extract_structure_signature(product: dict) -> dict:
    """从产品信息中提取结构特征签名"""
    specs = product.get("specs", {})
    title = product.get("title", "").lower()
    sig = {}
    # 材质
    material = specs.get("Material", specs.get("材质", ""))
    if material:
        sig["material"] = material.lower()
    # 颜色/电镀
    color = specs.get("Color", specs.get("颜色", ""))
    if color:
        sig["color"] = color.lower()
    elif "chrome" in title:
        sig["color"] = "chrome"
    # 安装方式
    fitment = specs.get("Fitment Type", specs.get("安装方式", ""))
    if fitment:
        sig["fitment"] = fitment.lower()
    # 数量
    pieces = specs.get("Number of Pieces", specs.get("数量", ""))
    if pieces:
        sig["pieces"] = pieces
    # 类型
    ptype = specs.get("Type", specs.get("类型", ""))
    if ptype:
        sig["type"] = ptype.lower()
    return sig


# ── GLM-4V 视觉分类 ────────────────────────────────────

# 智谱 API 配置（复用 image_validator）
ZHIPU_API_KEY = "61ffd79cb5394e0284550b88ff3c0eda.hai1zorE9yumVzsd"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
VISION_MODEL = "GLM-4V-Plus"

VISION_COMPARE_PROMPT = """左边是锚定产品（标准品），右边是竞品（待验证）。

请分两步完成：

第一步 — 分别描述左右两图：
- anchor_desc: 左图的属性。逐项填写 position（方位: Front/Rear/Driver-Side/Passenger-Side/Front-Rear/Both-Sides/Unknown）、structure（结构: One-Piece/Multi-Piece/Unknown）、finish（表面处理: Chrome/Gloss-Black/Matte-Black/Textured-Black/Painted/Primered/Polished/Brushed/Carbon-Fiber/Black/White/Silver/Red/Blue/Green/Red-Black/Blue-Black/Unknown）、shape（轮廓形状描述）、count（图中可见的产品主体数量）
- candidate_desc: 右图的属性。逐项填写同样的字段

第二步 — 对比两组描述：
- 两段描述在 position + structure + finish + shape + count 五个维度都一致 → match=true
- 任一维度存在本质差异 → match=false
- 拍摄角度/光照造成的差异不算本质差异

注意：即使两图完全相同、找不出任何差异，也必须输出match=true的JSON，禁止只输出文字说明。

只输出 JSON：

{
  "anchor_desc": {"position": "...", "structure": "...", "finish": "...", "shape": "...", "count": 数字},
  "candidate_desc": {"position": "...", "structure": "...", "finish": "...", "shape": "...", "count": 数字},
  "match": true/false,
  "diff_type": "shape|structure|finish|size|none",
  "confidence": 0.0-1.0
}"""

VISION_CLASSIFY_PROMPT = """请分析这张汽车零配件产品图片，按以下每一项输出 JSON：

1. position: 产品安装的方位。从以下选一个：Front-Driver-Side / Front-Passenger-Side / Rear-Driver-Side / Rear-Passenger-Side / Front / Rear / Unknown。
   - 前玻璃比后玻璃面积大、形状略方
   - 司机侧和乘客侧玻璃/把手互相对称（镜像）
   - 如果无法从图中判断，填 Unknown

2. structure: 产品是一体式还是分体式。选：One-Piece / Multi-Piece / Unknown。
   - 一体式：整个产品是一个完整件，没有可分离的部件
   - 分体式：产品由多个独立部件组装而成（如把手+底座分离、灯罩+灯座分离）
   - 如果无法从图中判断，填 Unknown

3. finish: 产品的表面处理/颜色。选一个：Chrome / Gloss-Black / Matte-Black / Textured-Black / Painted / Primered / Polished / Brushed / Black / White / Silver / Red / Blue / Green / Unknown。
   - Chrome = 镜面反光
   - Gloss-Black = 亮面黑
   - Matte-Black = 哑面黑/不发亮
   - Textured-Black = 有颗粒纹理的黑
   - Painted = 彩色喷漆（非电镀、非黑色）
   - 优先选最精确的，不够精确则选大类（如亮黑和哑黑分不清→Black）

4. accessories: 图中可见的附带配件。从以下选多个，用数组返回：screws / bolts / gaskets / clips / mounting_hardware / installation_tool / wiring / brackets / springs / rods / none。
   - 如果看不到任何配件，返回 ["none"]

5. count: 图中清晰可见的产品主体数量（不是配件数量）。数字。

只输出 JSON，不要任何其他文字。格式：{"position": "...", "structure": "...", "finish": "...", "accessories": [...], "count": N}"""


def _call_glm4v(image_path: str, question: str, timeout: int = 60) -> str:
    """调用 GLM-4V 分析图片，返回原始文本"""
    from openai import OpenAI
    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    img_buffer = Path(image_path).read_bytes()
    b64 = base64.b64encode(img_buffer).decode()
    ext = Path(image_path).suffix.lower().lstrip(".") or "png"
    data_url = f"data:image/{ext};base64,{b64}"
    resp = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data_url}},
            {"type": "text", "text": question},
        ]}],
        max_tokens=500,
        temperature=0.1,
        timeout=timeout,
    )
    time.sleep(1)  # QPS 限流保护（默认 1-2 QPS）
    return resp.choices[0].message.content.strip()


def _classify_via_vision(image_path: str, fields_to_check: list) -> dict:
    """用 GLM-4V 对图片进行独立分类，返回分类结果"""
    if not Path(image_path).exists():
        return {}

    try:
        raw = _call_glm4v(image_path, VISION_CLASSIFY_PROMPT)
        # 清理 markdown 包裹
        raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
        raw = re.sub(r'\s*```$', '', raw)
        result = json.loads(raw)
        log(f"  [GLM-4V] {image_path[:50]}... → {json.dumps(result, ensure_ascii=False)}")
        return result
    except Exception as e:
        log(f"  [GLM-4V ERROR] {e}")
        return {}


def _compare_via_vision(anchor_img: str, candidate_img: str, timeout: int = 45) -> dict:
    """用 GLM-4V 并排对比锚点图和竞品图（对比模式，准确率更高）"""
    from openai import OpenAI

    if not Path(anchor_img).exists() or not Path(candidate_img).exists():
        return {}

    # 编码两张图
    a_buf = Path(anchor_img).read_bytes()
    c_buf = Path(candidate_img).read_bytes()
    a_b64 = base64.b64encode(a_buf).decode()
    c_b64 = base64.b64encode(c_buf).decode()
    a_ext = Path(anchor_img).suffix.lower().lstrip(".") or "png"
    c_ext = Path(candidate_img).suffix.lower().lstrip(".") or "png"

    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    try:
        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/{a_ext};base64,{a_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/{c_ext};base64,{c_b64}"}},
                {"type": "text", "text": VISION_COMPARE_PROMPT},
            ]}],
            max_tokens=600,
            temperature=0.1,
            timeout=timeout,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw).rstrip('`').strip()
        # 模型偶尔输出 "# 示例" 等非JSON前缀，提取第一个完整JSON对象
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            raw = m.group(0)
        result = json.loads(raw)
        # 将 candidate_desc 字段提升到顶层，保持与 _enhance_classification 兼容
        if "candidate_desc" in result:
            cd = result["candidate_desc"]
            for field in ["position", "structure", "finish", "count"]:
                if field in cd and field not in result:
                    result[field] = cd[field]
        log(f"  [GLM-4V COMPARE] → {json.dumps(result, ensure_ascii=False)}")
        time.sleep(1)  # QPS 限流保护（默认 1-2 QPS）
        return result
    except Exception as e:
        log(f"  [GLM-4V COMPARE ERROR] {e}")
        return {}


def _download_product_image(product: dict, mother_dir: Path) -> str:
    """下载产品的第一张图片到母文件目录，返回本地路径"""
    images = product.get("images", [])
    if not images:
        return ""

    img_dir = mother_dir / "ebay_images"
    img_dir.mkdir(parents=True, exist_ok=True)

    # 取第一张大图（偏好 s-l1600）
    pref_order = [img for img in images if "s-l1600" in img]
    url = pref_order[0] if pref_order else images[0]

    item_id = product.get("item_id", "unknown")
    ext = ".webp" if "webp" in url else ".png" if "png" in url else ".jpg"
    local_path = img_dir / f"vision_{item_id}{ext}"

    if local_path.exists():
        return str(local_path)

    for attempt in range(2):
        try:
            import requests
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"
            })
            resp.raise_for_status()
            local_path.write_bytes(resp.content)
            return str(local_path)
        except Exception as e:
            if attempt == 0:
                time.sleep(1)
                continue
            log(f"  [IMG DOWNLOAD ERROR] {item_id}: {e}")
            return ""


def _enhance_classification(product: dict, mother_dir: Path,
                            force_vision: bool = False,
                            anchor_img: str = None) -> dict:
    """增强产品分类：文本提取 → 标记 needs_vision → GLM-4V 补充/纠错

    当提供 anchor_img 时使用对比模式（更准确），否则用独立判断。
    """
    text_cls = _classify_product(product)

    # 确定哪些字段需要视觉识别（不仅是 Unknown，也包括低置信度场景）
    needs_vision = []
    if text_cls["position"] == "Unknown":
        needs_vision.append("position")
    if text_cls["structure"] == "Unknown":
        needs_vision.append("structure")
    if text_cls["sub_type"] == "Unknown":
        needs_vision.append("sub_type")
    # 裸色 finish 可能漏了双色组合（如 Red Black → 只抓到 Black）
    if text_cls["finish"] in ["Black", "Silver", "White", "Gray", "Red", "Blue", "Green"]:
        needs_vision.append("finish")
    # 件数未知 → 视觉补
    if text_cls["count"] is None or text_cls["count"] == "Unknown":
        needs_vision.append("count")

    text_cls["needs_vision"] = needs_vision

    if not needs_vision and not force_vision:
        text_cls["vision_result"] = None
        return text_cls

    # 下载图片 + 调用 GLM-4V
    img_path = _download_product_image(product, mother_dir)
    if not img_path:
        text_cls["vision_result"] = None
        return text_cls

    # 对比模式（有锚点图）vs 独立判断
    if anchor_img and Path(anchor_img).exists():
        vision = _compare_via_vision(anchor_img, img_path)
    else:
        vision = _classify_via_vision(img_path, needs_vision)

    text_cls["vision_result"] = vision

    if not vision:
        return text_cls

    # ── 用视觉结果回填/纠错 ──
    if vision.get("position") and vision["position"] != "Unknown":
        if text_cls["position"] == "Unknown":
            text_cls["position"] = vision["position"]
            text_cls["position_source"] = "vision"
    if vision.get("structure") and vision["structure"] != "Unknown":
        if text_cls["structure"] == "Unknown":
            text_cls["structure"] = vision["structure"]
            text_cls["structure_source"] = "vision"
    vision_finish = vision.get("finish", "")
    if vision_finish and vision_finish != "Unknown":
        if text_cls["finish"] == "Unknown" or (
            text_cls["finish"] in ["Black", "Silver", "White", "Gray", "Red", "Blue", "Green"]
            and vision_finish not in ["Black", "Silver", "White", "Gray", "Red", "Blue", "Green", "Unknown"]
        ):
            text_cls["finish"] = vision_finish
            text_cls["finish_source"] = "vision"
    vision_acc = vision.get("accessories", [])
    if vision_acc and vision_acc != ["none"]:
        existing = set(text_cls.get("accessories", []))
        for a in vision_acc:
            if a != "none" and a not in existing:
                existing.add(a)
        text_cls["accessories"] = list(existing)
    if text_cls["sub_type"] == "Unknown" and vision.get("sub_type"):
        text_cls["sub_type"] = vision["sub_type"]
        text_cls["sub_type_source"] = "vision"
    # 视觉 count 覆盖文本 count（文本的 N-pc/N-fin 可能误判）
    vision_count = vision.get("count")
    if isinstance(vision_count, int) and vision_count > 0:
        if text_cls["count"] is None or text_cls["count"] != vision_count:
            text_cls["count"] = vision_count
            text_cls["count_source"] = "vision"

    return text_cls


def _compare_anchors(anchor_data: list, all_data: list, source_links: list,
                     all_classifications: list = None) -> dict:
    """以锚点为基准，对比所有竞品，输出差异告警

    规则0: 方位/件数/表面处理/子类型 → 不匹配直接排除
    规则1: 年份范围 > 锚点 → 高亮
    规则2: 额外适配车型 → 标红
    规则3: 结构特征差异 ≥7条 + 5店铺 → 标红
    规则4: 一体式/分体式差异 → 标红
    """
    if not anchor_data:
        return {}

    # ── 锚点基准 ──
    anchor_years = set()
    anchor_vehicles = set()
    anchor_structures = []
    anchor_classifications = []
    for ad in anchor_data:
        yr = _extract_year_range(ad.get("title", ""))
        if yr:
            anchor_years.add(yr)
        anchor_vehicles |= _extract_vehicle_makes(ad.get("title", ""))
        anchor_structures.append(_extract_structure_signature(ad))
        anchor_classifications.append(_classify_product(ad))

    # 锚点年份范围（取最宽的）
    anchor_year_min = min(y[0] for y in anchor_years) if anchor_years else None
    anchor_year_max = max(y[1] for y in anchor_years) if anchor_years else None

    # 锚点分类（取第一个锚点的分类作为基准；多个锚点有冲突时取 Confidence 最高的）
    anchor_class = anchor_classifications[0] if anchor_classifications else {}
    # 如果有多个锚点，合并信息（取最常见的值）
    if len(anchor_classifications) > 1:
        for field in ["position", "count", "finish", "sub_type", "door_config"]:
            vals = [c[field] for c in anchor_classifications if c[field] != "Unknown"]
            if vals:
                anchor_class[field] = max(set(vals), key=vals.count)

    # 锚点结构类型
    anchor_structure = _extract_structure_type(
        anchor_data[0].get("title", ""), anchor_data[0].get("specs", {})
    )

    # ── 规则0: 竞品入池筛选 ──
    # 使用预计算的 vision 增强分类结果（如果有）
    cls_lookup = {}
    if all_classifications:
        for c in all_classifications:
            cls_lookup[c["item_id"]] = c["classification"]

    anchor_ids = {a.get("item_id", "") for a in anchor_data}
    valid_competitors = []
    excluded = []
    for p in all_data:
        if p.get("item_id", "") in anchor_ids:
            continue  # 锚点自身不参与对比
        pid = p.get("item_id", "")
        cls = cls_lookup.get(pid) or _classify_product(p)
        is_valid, reason = _is_valid_competitor(anchor_class, cls,
                                                     anchor_specs=anchor_data[0].get("specs", {}),
                                                     other_specs=p.get("specs", {}))
        if is_valid:
            p["_classification"] = cls
            valid_competitors.append(p)
        else:
            excluded.append({
                "competitor_url": p.get("url", ""),
                "competitor_title": p.get("title", ""),
                **reason,
            })

    # ── 规则1: 年份扩展检测（仅对有效竞品）──
    year_alerts = []
    for p in valid_competitors:
        title = p.get("title", "")
        yr = _extract_year_range(title)
        if not yr or not anchor_year_min:
            continue
        # 年份范围大于锚点 → 高亮
        if yr[0] < anchor_year_min or yr[1] > anchor_year_max:
            year_alerts.append({
                "competitor_url": p.get("url", ""),
                "competitor_title": title,
                "competitor_year": f"{yr[0]}-{yr[1]}",
                "anchor_year": f"{anchor_year_min}-{anchor_year_max}",
                "flag": "highlight",
                "note": "竞品适配年份超出锚点范围，可能是扩展适配机会",
            })

    # ── 规则2: 车型扩展检测（仅对有效竞品）──
    vehicle_alerts = []
    for p in valid_competitors:
        title = p.get("title", "")
        p_vehicles = _extract_vehicle_makes(title)
        extra = p_vehicles - anchor_vehicles
        if extra:
            vehicle_alerts.append({
                "competitor_url": p.get("url", ""),
                "competitor_title": title,
                "anchor_vehicles": [f"{m} {md}" for m, md in sorted(anchor_vehicles)],
                "extra_vehicles": [f"{m} {md}" for m, md in sorted(extra)],
                "flag": "red",
                "note": "竞品额外适配车型，需人工确认（同平台车可能共享零件）",
            })

    # ── 规则3: 结构特征差异检测（≥7条不同店铺）──
    structure_warnings = []
    competitor_structures = Counter()
    competitor_shops = {}
    for p in valid_competitors:
        sig = _extract_structure_signature(p)
        seller = p.get("seller", "")
        for key, val in sig.items():
            full_sig = f"{key}={val}"
            competitor_structures[full_sig] += 1
            if full_sig not in competitor_shops:
                competitor_shops[full_sig] = set()
            competitor_shops[full_sig].add(seller)

    anchor_sig_all = {}
    for ans in anchor_structures:
        anchor_sig_all.update(ans)

    for sig_str, count in competitor_structures.items():
        key, val = sig_str.split("=", 1)
        anchor_val = anchor_sig_all.get(key, "")
        if anchor_val and anchor_val != val and count >= 7:
            shops = competitor_shops.get(sig_str, set())
            if len(shops) >= 5:
                structure_warnings.append({
                    "field": key,
                    "anchor_value": anchor_val,
                    "competitor_value": val,
                    "count": count,
                    "different_shops": len(shops),
                    "flag": "red",
                    "note": f"≥7条竞品（{len(shops)}家店铺）的 {key} 与锚点不同，可能产品已迭代，需人工判断",
                })

    # ── 规则4: 一体式/分体式结构检测 ──
    structure_alerts = []
    # 检查有效竞品中一体式/分体式的分布
    struct_votes = Counter()
    struct_details = []
    for p in valid_competitors:
        st = p.get("_classification", {}).get("structure", "Unknown")
        src = p.get("_classification", {}).get("structure_source", "unknown")
        struct_votes[st] += 1
        if st != "Unknown":
            struct_details.append({
                "competitor_url": p.get("url", ""),
                "competitor_title": p.get("title", ""),
                "structure": st,
                "source": src,
            })

    # 锚点结构未知 vs 竞品有明确结构
    anchor_struct = anchor_structure.get("structure", "Unknown")
    anchor_struct_src = anchor_structure.get("structure_source", "unknown")

    if anchor_struct == "Unknown" and len(struct_details) > 0:
        # 锚点一体式/分体式未确认，需要视觉识别
        structure_alerts.append({
            "type": "structure_unknown",
            "anchor_structure": "Unknown",
            "competitor_dominant": struct_votes.most_common(1)[0][0] if struct_votes else "Unknown",
            "competitor_details": struct_details[:5],
            "flag": "warning",
            "note": "⚠️ 一体式/分体式未确认，请调用 GLM-4V 查看参考图判断",
        })
    elif anchor_struct != "Unknown" and struct_votes:
        majority = struct_votes.most_common(1)[0]
        if majority[0] != "Unknown" and majority[0] != anchor_struct and majority[1] >= 3:
            structure_alerts.append({
                "type": "structure_mismatch",
                "anchor_structure": anchor_struct,
                "anchor_structure_source": anchor_struct_src,
                "competitor_dominant": majority[0],
                "competitor_count": majority[1],
                "competitor_details": struct_details[:5],
                "flag": "red",
                "note": f"锚点为{anchor_struct}，但{majority[1]}条竞品为{majority[0]}，产品结构可能不同",
            })

    # ── 规则5: 多配件检测 ──
    accessory_alerts = []
    anchor_accessories = set(anchor_class.get("accessories", []))
    comp_accessory_count = Counter()
    comp_accessory_shops = {}
    for p in valid_competitors:
        accs = p.get("_classification", {}).get("accessories", [])
        seller = p.get("seller", "")
        for a in accs:
            if a not in anchor_accessories:
                comp_accessory_count[a] += 1
                if a not in comp_accessory_shops:
                    comp_accessory_shops[a] = set()
                comp_accessory_shops[a].add(seller)

    for acc, count in comp_accessory_count.most_common():
        shops = comp_accessory_shops.get(acc, set())
        if count >= 3:
            flag = "red" if count >= 7 and len(shops) >= 5 else "highlight"
            accessory_alerts.append({
                "accessory": acc,
                "count": count,
                "different_shops": len(shops),
                "flag": flag,
                "note": f"竞品附带{acc}（{count}条/{len(shops)}店铺），锚点不含此配件" + (
                    " — 市场主流配置包含此配件，锚点可能需要补配" if flag == "red" else ""
                ),
            })

    return {
        "anchor_classification": anchor_class,
        "anchor_structure": anchor_structure,
        "anchor_accessories": list(anchor_accessories) if anchor_accessories else [],
        "anchor_years": f"{anchor_year_min}-{anchor_year_max}" if anchor_year_min else None,
        "anchor_vehicles": [f"{m} {md}" for m, md in sorted(anchor_vehicles)],
        "rule0_excluded": excluded,
        "rule0_excluded_count": len(excluded),
        "valid_competitors_count": len(valid_competitors),
        "year_expanded_alerts": year_alerts,
        "vehicle_compatibility_alerts": vehicle_alerts,
        "structure_warnings": structure_warnings,
        "structure_alerts": structure_alerts,
        "accessory_alerts": accessory_alerts,
    }


# ── 分析部分 ──────────────────────────────────────────

def analyze(mother_dir: Path, product_data: list, source_links: list = None,
             use_vision: bool = False) -> dict:
    """交叉分析所有竞品数据，输出 market_intel"""
    valid = [p for p in product_data if 'title' in p and p['title']]
    if not valid:
        return {"error": "无有效数据", "generated_at": datetime.now().isoformat()}

    # ── 标题分析 ──
    titles = [p['title'] for p in valid]
    # 提取产品数量表述
    count_patterns = re.findall(
        r'\b(set\s+of\s+\d+|\d+\s*pc|\d+\s*piece|\d+\s*pack|\d+x|\d+\s*set)',
        ' '.join(titles), re.IGNORECASE
    )
    # 高频词（排除车型名和通用词）
    word_freq = Counter()
    for t in titles:
        words = re.findall(r'[A-Z][a-z]+|\d+', t)
        for w in words:
            word_freq[w.lower()] += 1

    # ── 图片分析 ──
    image_counts = [p.get('imageCount', 0) for p in valid]
    best_image_listing = max(
        valid, key=lambda p: p.get('imageCount', 0)
    )
    # 汇总所有图片（去重，取最佳质量）
    all_images = []
    for p in sorted(valid, key=lambda x: x.get('imageCount', 0), reverse=True):
        for img in p.get('images', []):
            # 偏好 s-l1600 大图 → s-l500 → 其他
            if img not in all_images:
                all_images.append(img)

    # ── 规格交叉验证 ──
    spec_consensus = {}
    for p in valid:
        for k, v in p.get('specs', {}).items():
            if k not in spec_consensus:
                spec_consensus[k] = Counter()
            spec_consensus[k][v] += 1

    # 找出高共识规格（≥50% listing 一致）
    key_specs = {}
    for k, counter in spec_consensus.items():
        total = sum(counter.values())
        top_val, top_count = counter.most_common(1)[0]
        if top_count >= len(valid) * 0.5:
            key_specs[k] = {"value": top_val, "consensus": round(top_count / len(valid), 2)}

    # ── 价格分析 ──
    prices = []
    for p in valid:
        price_str = p.get('price', '')
        m = re.search(r'\d+\.?\d*', str(price_str))
        if m:
            prices.append(float(m.group()))
    price_range = f"${min(prices):.2f} - ${max(prices):.2f}" if prices else "N/A"
    avg_price = round(sum(prices) / len(prices), 2) if prices else None

    # ── 标题策略提取 ──
    strategies = []
    for t in titles[:10]:
        # 提取关键词序列
        keywords = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', t)
        strategies.append({
            "title": t,
            "keywords": keywords[:8],
            "has_count": bool(re.search(r'\b(\d+)\s*(pc|piece|pack|x|set)', t, re.IGNORECASE)),
            "has_chrome": 'chrome' in t.lower(),
            "has_exterior": 'exterior' in t.lower() or 'outer' in t.lower(),
        })

    # ── 锚点数据（提前提取，供视觉对比模式使用）──
    anchor_links = [l for l in (source_links or []) if l.get("anchor")]
    anchor_ids = set()
    for al in anchor_links:
        m = re.search(r'/itm/(\d+)', al.get("url", ""))
        if m:
            anchor_ids.add(m.group(1))
    anchor_data = [p for p in valid if p.get("item_id", "") in anchor_ids]

    # ── 产品分类 ──
    anchor_img = None
    if use_vision and anchor_data:
        anchor_img = _download_product_image(anchor_data[0], mother_dir)

    all_classifications = []
    for p in valid:
        cls = _enhance_classification(p, mother_dir,
                                       anchor_img=anchor_img) if use_vision else _classify_product(p)
        all_classifications.append({
            "item_id": p.get("item_id", ""),
            "title": p.get("title", ""),
            "classification": cls,
        })
    if use_vision:
        needs_v = sum(1 for c in all_classifications if c["classification"].get("needs_vision"))
        log(f"视觉分类完成: {needs_v} 条仍待视觉确认（无图/API失败）")

    # ── 锚点对比分析 ──
    comparison = _compare_anchors(anchor_data, valid, source_links or [],
                                     all_classifications if use_vision else None) if anchor_data else {}

    return {
        "mother_name": mother_dir.name,
        "generated_at": datetime.now().isoformat(),
        "total_links_analyzed": len(product_data),
        "valid_listings": len(valid),
        "anchor_count": len(anchor_data),
        "price_range": price_range,
        "avg_price": avg_price,
        "product_count_mentions": list(set(count_patterns)),
        "image_counts": {"min": min(image_counts), "max": max(image_counts), "avg": round(sum(image_counts)/len(image_counts), 1)},
        "best_image_listing": {"title": best_image_listing['title'], "images": best_image_listing.get('images', [])[:5], "item_id": best_image_listing.get('item_id', '')},
        "reference_images": all_images[:6],
        "key_specs": key_specs,
        "title_samples": titles[:5],
        "title_strategies": strategies[:3],
        "common_keywords": word_freq.most_common(20),
        # 产品分类（每个 listing 的方位/件数/表面处理/子类型/结构）
        "product_classifications": all_classifications,
        # 锚点对比结果
        "anchor_analysis": comparison,
    }


# ── 主入口 ────────────────────────────────────────────

async def run_intel(mother_dir: str, max_links: int = None, dry_run: bool = False,
                    use_vision: bool = False):
    mother = Path(mother_dir)
    if not mother.is_dir():
        print(f"目录不存在: {mother}")
        sys.exit(1)

    source_file = mother / "source_links.json"
    if not source_file.exists():
        print(f"source_links.json 不存在: {source_file}")
        sys.exit(1)

    source = json.loads(source_file.read_text(encoding="utf-8"))
    links = source.get("links", [])

    # 去重
    seen = set()
    unique_links = []
    for link in links:
        url = link.get("url", "")
        if url not in seen:
            seen.add(url)
            unique_links.append(url)
    if max_links:
        unique_links = unique_links[:max_links]

    log(f"母文件: {mother.name}")
    log(f"链接数: {len(links)} (去重后 {len(unique_links)})")

    # 检查已有 product JSON
    existing = list(mother.glob("product_*.json"))
    log(f"已有 product JSON: {len(existing)} 个")

    product_data = []
    for f in existing:
        try:
            product_data.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass

    # 爬取缺的
    existing_ids = {p.get('item_id', '') for p in product_data}
    need_scrape = []
    for u in unique_links:
        m = re.search(r'/itm/(\d+)', u)
        if m and m.group(1) not in existing_ids:
            need_scrape.append(u)
        elif not m:
            log(f"  [SKIP] 无法解析 item_id: {u}")

    if dry_run:
        log(f"DRY RUN: 将爬取 {len(need_scrape)} 个新链接（跳过）")
    elif need_scrape:
        log(f"开始爬取 {len(need_scrape)} 个新链接...")
        scraped = await scrape_batch(need_scrape, save_dir=str(mother))
        for data in scraped:
            if 'item_id' in data and 'error' not in data:
                out_file = mother / f"product_{data['item_id']}.json"
                out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                log(f"  saved: {out_file.name}")
                product_data.append(data)
            else:
                log(f"  [FAIL] {data.get('url', '?')}: {data.get('error', 'unknown')}")
    else:
        log("所有链接已爬取，仅做分析")

    # 分析（传入 source_links 用于锚点对比）
    intel = analyze(mother, product_data, source.get("links", []), use_vision=use_vision)
    intel_file = mother / "market_intel.json"
    intel_file.write_text(json.dumps(intel, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"market_intel.json 已更新 ({len(product_data)} 条数据)")

    # ── SQLite 入库 ──
    try:
        from crawler.database import MarketDB
        sku = mother.name
        db = MarketDB()
        db.init_tables()
        job_id = db.ingest_analysis(
            mother_dir=str(mother), sku=sku,
            product_data=product_data,
            source_links=source.get("links", []),
            market_intel=intel,
            vision_enabled=use_vision,
        )
        log(f"market.db 已更新 (job: {job_id})")
    except Exception as e:
        log(f"market.db 写入失败（不影响主流程）: {e}")

    # 简要输出
    print(f"\n{'='*50}")
    print(f"  价格区间: {intel.get('price_range', 'N/A')}")
    print(f"  平均价格: ${intel.get('avg_price', 'N/A')}")
    print(f"  产品数量表述: {intel.get('product_count_mentions', [])}")
    print(f"  图片数范围: {intel.get('image_counts', {})}")
    print(f"  高共识规格: {list(intel.get('key_specs', {}).keys())}")
    print(f"  参考图: {len(intel.get('reference_images', []))} 张")
    print(f"  标题样例: {intel.get('title_samples', [])[:2]}")
    print(f"{'='*50}")

    return intel


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mother_dir", help="母文件目录路径")
    parser.add_argument("--max", type=int, default=50, help="最大爬取链接数")
    parser.add_argument("--dry-run", action="store_true", help="仅分析已有 JSON，不爬取")
    parser.add_argument("--vision", action="store_true", help="启用 GLM-4V 视觉分类（下载图片+GLM打标）")
    args = parser.parse_args()

    asyncio.run(run_intel(args.mother_dir, args.max, args.dry_run, args.vision))
