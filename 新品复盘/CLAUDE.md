# 新品复盘 — 三部新品周报/月报自动生成系统

> 正文必须用中文。本文件是项目迁移记忆文件。

## 项目定位

跨境电商汽配（Amazon）新品表现复盘系统。从 Excel 源数据自动生成 HTML 看板 + XLSX 报表。**本项目是 三部周报v1 的后身/重构版，更成熟。**

## 目录结构

```
新品复盘/
├── 新品板块_4.30-5.27_4weeks_drill.html   # ⭐ 正式周报看板（旧管线，6Tab+下钻+4周，静态数据）
├── 新品板块_drill_upload.html             # ⭐ 上传版下钻看板（新管线，拖入Excel+下钻+广告结构）
├── 新品板块_4.30-5.27_4weeks_drill_v3.html # 正式看板v3（部门占比+PW市占→Tab1，广告构成明细）
├── 新品板块.html                          # 新管线通用模板（CDN版，拖入Excel即用）
├── 新品板块_离线版.html                   # 离线版模板（内嵌SheetJS+Chart.js，双击即用）
├── compute_engine.js                      # ⭐ JS计算引擎（~1314行，替代Python）
├── render_dashboard.js                    # ⭐ JS渲染引擎（~1075行）
├── build_offline.py                       # 离线构建（下载CDN→内嵌）
├── build_html_clean.py                    # 在线版构建（组装模板+引擎+渲染）
├── inject_drill_upload.py                 # 向上传版注入下钻+广告结构（输出drill_upload.html）
├── rebuild_ad_tab.py                      # 重构广告Tab（旧管线，openpyxl计算→drill_v2.html）
├── fix_drill_upload.py                    # 修复drill_upload版（部门+PW→Tab1，广告构成明细）
├── fix_drill_v2.py                        # 同步修复正式版（drill→v3，同fix_drill逻辑）
├── 周报/                              # 数据源+验证截图
├── 月报/                              # 月报子项目（独立）
├── screenshots/                       # 看板截图
├── .venv/                             # Python 3.14 (uv)
└── _archive/                          # 📦 历史文件归档
    ├── 4.30-5.6/                      # 第一期（5版HTML+5版XLSX+JSON）
    ├── 5.7-5.13/                      # 第二期
    ├── 5.14-5.20/                     # 第三期
    ├── 5.21-5.27/                     # 第四期
    └── 工具脚本/                      # 一次性验证/压缩/检查脚本
```

## 数据管道

### 旧管线（gen_html_*.py，已归档保留）
```
周报/新品检查周源数据和PLP数据.xlsx
    ├── Sheet "四三数据累计"：~137列/SKU
    ├── Sheet "PLP明细"：广告投放数据
    └── Sheet "自然周销售数据"：SKU级自然周销售
              │
              ├─→ gen_xlsx_*.py ──→ 新品周报数据表_X.X-X.X.xlsx
              │
              └─→ gen_html_*.py ──→ 新品板块_X.X-X.X.html
                    (内嵌 Chart.js CDN + 37个JS数据块)
```

### 新管线（上传接口，⭐ 推荐使用）
```
新品检查周源数据和PLP数据.xlsx
    ↓ 拖入浏览器（SheetJS 解析表头名匹配列）
新品板块.html  ← 通用模板，无内嵌数据
    ├── JS计算引擎 computeEngine() — 替代 Python ~1063 行
    ├── Chart.js 渲染 — 14 个图表
    ├── 6 Tab 表格渲染
    └── XLSX 导出（SheetJS 写，替代 openpyxl）
```

### 新管线核心优势
- **列自动定位**：表头名正则匹配（`/销量.*5\.21/`），Excel 加列/调序不受影响
- **单一计算源**：所有计算在浏览器 JS 中完成，消除 Python→JS 变量映射不一致
- **即拖即用**：每周期只需拖入新 Excel，无需修改任何代码
- **零依赖**：离线版内置 SheetJS + Chart.js，双击 HTML 即可使用

### 文件说明

| 文件 | 说明 |
|------|------|
| `新品板块_4.30-5.27_4weeks_drill.html` | ⭐ **正式周报看板**，6Tab+16图表+7下钻表+4周趋势 |
| `新品板块.html` | 新管线通用模板（CDN版，拖入Excel即用） |
| `新品板块_离线版.html` | 离线版模板，内嵌SheetJS+Chart.js |
| `compute_engine.js` | JS 计算引擎源码（~1314行） |
| `render_dashboard.js` | JS 渲染引擎源码（~1075行） |
| `build_offline.py` | 离线构建脚本，下载CDN内嵌 |
| `新品板块_drill_upload.html` | 上传版+下钻+广告结构合体（`inject_drill_upload.py` 输出） |
| `新品板块_4.30-5.27_4weeks_drill_v3.html` | 正式看板v3：部门占比+PW→Tab1，广告构成明细 |
| `inject_drill_upload.py` | 向上传版注入下钻+广告结构+`computeAdExtras()` |
| `rebuild_ad_tab.py` | Python端计算广告结构数据→重构drill v1→v2 |
| `fix_drill_upload.py` | 修复drill_upload版（7个fix，部门+PW移到Tab1） |
| `fix_drill_v2.py` | 同步修复正式版（6个fix，输出drill_v3） |
| `build_html_clean.py` | 组装模板+compute_engine.js+render_dashboard.js→clean.html |
| `add_drilldown.py` | 下钻图表注入（旧管线增量脚本） |
| `upgrade_4weeks.py` | 4周数据升级（旧管线增量脚本） |

## 三个数据周期

| 周期 | HTML 脚本 | XLSX 脚本 | 特点 |
|------|-----------|-----------|------|
| 4.30-5.6 | gen_html_506_v4.py | gen_xlsx_4_30_5_6_v4.py | 迭代最多（5版HTML+5版XLSX） |
| 5.7-5.13 | gen_html_5_7_5_13.py | gen_xlsx_5_7_5_13.py | 改用直接读xlsx，21个JS数据块 |
| 5.14-5.20 | gen_html_5_14_5_20.py | gen_xlsx_5_14_5_20.py | **最新**，7标签，24数据块，品效分析 |

## 关键业务规则（⚠️ 必须遵守）

### 百分比处理
源数据中市占比和PLG费率存储为 **0-1 小数**。所有输出必须 **×100** 显示。
筛选阈值：`>= 75`（不是 `>= 0.75`）。

### ACOAS 去重
计算 ACOAS 总额时，totalRevenue 必须按 SKU 去重（同一 SKU 可能出现在多个广告系列中）。

### 核心指标
- **市占比** = 汇总销量 / (汇总销量 + 汇总对手出单)，不做行级平均
- **出单均价** = 销售额 / 销量，销量=0时 null
- **8日出单**：Y=8日内, N=8日外, Y和N都算"已出单"
- **低占比新品**：市占比 < 75% 且对手销量 > 0
- **销售额**：USD原值，禁止货币转换

## HTML 看板结构（6 Tab）

1. **总盘概览** — KPI卡片 + 4周趋势折线图 + 部门占比&PW市占（v3新增）
2. **低占比分析** — 市占<75%且对手>0的SKU明细
3. **广告结构** — 广告构成分布（PLP+PLG/单PLP/仅PLG/无广告）+ PLG费率四档 + 部门占比 + PW市占对比
4. **四三累计** — SKU级累计数据汇总+筛选
5. **品效分析** — 按上架月的队列分析
6. **汇报输出** — 一键复制汇报文案（含部门占比、广告构成、PLG费率）

## 环境

- Python 3.14 via uv（venv 在 `.venv/`）
- 核心依赖：openpyxl 3.1.5, pandas 3.0.3, numpy 2.3.5
- HTML 输出需联网：Chart.js 4.4.0 CDN（离线=仅显示表格）
- **无** requirements.txt / pyproject.toml

## 临时文件已清理

2026-05-31 清理了月报/下 28 个临时文件（21个 .txt 调试输出 + 4个 temp JS + 1个 tmp HTML + test.js）。如需历史调试记录，查看 git log。

## 与三部周报v1的关系

- **三部周报v1** 是原型（React SPA + generate_report_v3.py）
- **新品复盘** 是正式版（直接读xlsx，单文件HTML输出）
- **React重写(2026-06-01)**: 新品复盘HTML → 提取53个JS数据块 → `corrected_data.json`(409KB) → 三部周报v1 React的 `newProductStatusAdapter.ts` → `NewProductStatusPage.tsx`(6 Tab)
- `copy_to_template.py` 仍引用 `三部周报v1/胡煜星-周报统一Workbook表头模板.xlsx`
- `gen_xlsx_506_acoas.py` 曾从 `三部周报v1/周报/` 读取源数据

## JSON 提取协议（供 React 消费）

当 HTML 更新后，需重新提取 JSON 给 React：
```python
# 从 HTML 提取 JS 数据块到 corrected_data.json
# HTML 中的 const xxx = {...}; 会被解析为 JSON key-value
# 确保 encoding='utf-8'，HTML 的 <meta charset="UTF-8"> 保证中文正确
```

## ⚠️ 易错点 & 易生Bug点

### 百分比输出一致性
Python 端所有百分比输出必须统一为**百分数格式**（×100后的值），React 端不再做 ×100：
- `share4w`: `[52.6, 49.1]` ← Python: `round(share*100, 1)`，不是 `0.526`
- `curMarketShare`: `48.2`，不是 `0.482`
- PLP/PLG 4周 `acos4w/acoas4w`: `[14.3, 10.2]`，不是 `[0.143, 0.102]`
- **例外**: `plpDetailData[].acos` 保持 0-1 小数 `0.0381`（明细表React端自行×100）

### 数据块命名必须稳定
React Adapter 按固定 key 名读取 JSON，Python 端生成 JS 数据块时命名不能变：
- `cum43Stats`, `prevWeekKpi`, `categoryRevenueData`, `analystRevenueData`
- `totalSales4w`, `totalShare4w`, `catShare4w`, `anShare4w`
- `plpAnalysts`, `plpCategories`, `plpExpandTypes`, `plpDetailData`
- `plgStats`（含 `byAnalyst` 数组，字段: `analyst/total/plpAndPlgBoth/singleLinkPlpPlg/plgOnly/plpOnly/noAd/plpDisabledNoSale/plgSpend/plgAdRev/plgNatRev/acos/acoas`）
- `adDeptPct`（部门占比: `salesPct/revPct/newSales/newRevenue/deptSales/deptRevenue`）
- `adPwVsNew`（PW爬虫 vs 新品市占: `pwShare/newShare/pwTotalLinks/newSkuCount/newTotalSales/newRivalSales`）
- `adCompDist`（广告构成: `{'PLP+PLG':N, '单PLP':N, '仅PLG':N, '无广告':N}`）
- `adPlgTierDist`（PLG费率四档: `{'无广告':N, '低费率':N, '中费率':N, '高费率':N}`，阈值 ≤2%, 2-4%, >4%）
- `adPlpPlgLink`（PLP→PLG链接统计: `totalSku/plgY/plgN`）
- `adAnDetail/adCatDetail`（广告构成按分析人/品线明细表）
- `plgAn4w`, `plpAn4w`, `plpCat4w`, `plpExp4w`
- `timelinessData`（含 `analysts` 数组 + `total`，每个分析人有 `prevTimelyRate`/`change`）
- `priceOverview`（`byAnalyst` 是 `[{analyst, "$0-10":0, ...}]` 结构，非字典嵌套）

### 数据结构方向
- `priceOverview.byAnalyst`: **按分析人行** → `[{analyst: "俞东旭", "$0-10": 0}]`
- `mktDistOverall.distribution`: **按状态行** → `[{status: "正常", curCount: 52}]`
- `shareTierOverview.byCategory`: **按品线行** → `[{category: "车门系统", high: 10, mid: 5, low: 3}]`

## 分析维度

- **分析人(6)**：俞东旭, 张潇, 朱培源, 王偲涵, 章鹏, 胡煜星
- **品类(7)**：车门系统, 车身外扩件, 挡泥板, 机盖及附件, 牌照板支架, 其他, 饰条
- **拓展类型(3)**：原开品, 拓展品, 组合件
- **上架月份**：1月/2月/3月（月报队列分析）

## 与其他项目关系

- **上游**：三部周报v1（原型/模板来源）
- **独立**：不依赖 agent升级计划 或 产品卖点主图
- **数据源**：共享 `新品检查周源数据和PLP数据.xlsx`（位置在 `周报/` 下）
