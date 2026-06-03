# 三部周报v1 — 三部新品周报自动化系统

> 正文必须用中文。本文件是项目迁移记忆文件。

## 项目定位

跨境电商汽配业务（eBay）的周报自动生成系统。上传 Excel 源数据 → 浏览器端解析 → KPI/趋势图/多维拆解/中文汇报文案。

## 核心子项目（3个）

### 1. New project 2-新品板块已放入（主项目，React SPA）
- **技术栈**: Vite 4 + React 19 + TypeScript 5.9 + Recharts 3.2 + xlsx 0.18 + lucide-react
- **运行**: `npm run dev` → localhost:5173，demo 模式 `?demo=1`
- **路由**: Hash-based（`#/sales-status`, `#/new-product-status` 等）
- **数据流**: Excel 上传 → SheetJS 解析 → DataCenter → 各模块 Page 渲染
- **6 个模块**:
  | 模块 | 状态 |
  |------|------|
  | salesStatus | ✅ 完成（253行，props驱动） |
  | newProductStatus | ✅ 完成（~610行TSX + ~210行Adapter，JSON数据驱动） |
  | adsStatus | 🚫 空壳 |
  | pricingStatus | 🚫 空壳 |
  | accountTrafficStatus | 🚫 空壳 |
  | salesForecast | 🚫 空壳 |
- 每个模块按契约：`Page.tsx` + `Adapter.ts` + `Summary.ts` + `Rules.ts` + `index.ts` + `README.md`

### newProductStatus 模块架构（2026-06-01 重写完成）

```
src/modules/newProductStatus/
├── corrected_data.json          # 53个数据块，从新品复盘HTML提取（409KB）
├── newProductStatusAdapter.ts   # 薄数据访问层（~210行），导出getData/getOverviewKpi等
├── NewProductStatusPage.tsx     # 6 Tab页面（~610行），Recharts图表+表格+下钻弹窗
├── newProductStatusRules.ts     # 异常规则引擎
├── Summary.ts                   # 摘要组件
└── index.ts                     # 模块导出
```

**数据流**: Python管线(新品复盘) → HTML(内嵌JS数据块) → JSON提取 → Adapter → Page渲染
React层纯展示，不做数据处理。所有聚合/百分比计算在Python端完成。

**6个Tab**: 总盘概览 | 市场分布 | 低占比分析 | 广告追踪 | 四三累计 | 汇报输出
**图表库**: Recharts (PieChart/BarChart/LineChart/ComposedChart)，非Chart.js
**下钻**: ComposedChart双Y轴弹窗（品线/分析人/及时率/PLP/PLG维度）

### 2. 新品周报全流程（独立项目）
- **技术栈**: Vite 5 + 原生 JavaScript + Chart.js 4.4 (CDN)
- 数据管道: Excel → XLSX (10 Sheet) → JSON → HTML (9面板)
- 完整 SOP 见 SKILL.md

### 3. 新品周报-单模块（交付包）
- newProductStatus 模块的独立交付版

## 关键数据规则

- **市占比** = 汇总销量 / (汇总销量 + 汇总对手出单)，不做行级平均
- **出单均价** = 销售额 / 销量，销量为0时 null
- **8日出单**：Y=8日内出单, N=8日外出单, Y和N都算"已出单"
- **低占比新品**：市占比 < 0.75 且对手销量 > 0
- **销售额**：USD原值，禁止货币转换
- **环比**：只能在同周期类型内计算
- **周期类型**：销售 Thu-Wed / 广告 Mon-Sun / 价格日期快照 / 预测周

## ⚠️ 易错点 & 易生Bug点（每次开发前必读）

### 1. Adapter 字段名必须与 JSON 数据一致
**错误模式**: 凭想象写字段名（如 `stats.totalSales`），JSON中实际是 `stats.sales4w[0]`
**正确做法**: 每次写Adapter前，先用 Python 打印 JSON 的 `keys()`，逐字段核对
```python
python -c "import json; d=json.load(open('corrected_data.json','r',encoding='utf-8')); print(list(d['cum43Stats'].keys()))"
```

### 2. 百分比 ×100 规则：分三种情况，不能一刀切
| 数据来源 | 格式 | 示例 | 是否需要×100 |
|----------|------|------|-------------|
| `cum43Stats.share4w` / `totalShare4w` / `catShare4w` / `anShare4w` | 已是百分数 | `52.6`=52.6% | ❌ 不要 |
| `categoryRevenueData[].curMarketShare` | 已是百分数 | `48.2`=48.2% | ❌ 不要 |
| `plpAn4w[].acos4w` / `plgAn4w[].acos4w` | 已是百分数 | `14.3`=14.3% | ❌ 不要 |
| `plpDetailData[].acos` / `acoas` | 0-1 小数 | `0.0381`=3.81% | ✅ 需要 |
| `plpDetailData[].cvr` / `ctr` | 0-1 小数 | `0.1111`=11.11% | ✅ 需要 |
| `plpAnalysts[].acos` / `cvr` 等汇总表 | 已是格式化字符串 | `"11.31%"` | ❌ 直接透传 |

### 3. 数据结构行列方向不一致
**错误案例**: `priceOverview.byAnalyst` — 代码假设 `byAnalyst[range][analyst]`，实际是 `[{analyst, "$0-10":0, "$10-20":1}]`（按分析人行，非按区间列）
**正确做法**: 遇到嵌套数据先 `python -c` 打印结构，确认是列表还是字典

### 4. 下钻弹窗 Y轴量级冲突
**错误案例**: 品线/分析人下钻用单Y轴，销售额($万级)压扁销量(十位级)和市占比(0-100)
**正确做法**: 量级差10倍以上必须双Y轴 ComposedChart，大量级放左轴，小量级放右轴

### 5. drillLink 忘记接线
**错误案例**: drillMap 有数据，但表格渲染用 `r.analyst` 纯文本而非 `drillLink('plg:an:' + r.analyst, r.analyst)`
**检查清单**: 每个含下钻的表格，确认 `<td>` 内容是 `drillLink(...)` 而非纯文本

### 6. 表格列与 HTML 源不一致
**错误案例**: PLP维度表缺"链接数"和"CPA"列；四三累计多了"运营判断"和"PLP"列
**正确做法**: 对照 HTML 源的 `<th>` 逐列比对，列名、列数、列序必须一致

### 7. 筛选器数量与 HTML 不同
**错误案例**: 四三累计只有4个筛选器，HTML有7个（缺拓展类型/市占比/广告条件）
**正确做法**: 找到 HTML 中的 `<select id="f-xxx">` 逐一核对

### 8. renderTable total 行字段名匹配
**错误案例**: total 对象字段名与 getRow 函数解构不一致，导致合计行显示空白
**正确做法**: total 对象的 key 必须与表格数据行字段名完全一致

## 禁止修改的文件

- `src/dataCenter/`（核心数据层）
- `src/components/Sidebar.tsx`
- `src/styles/global.css`
- `src/utils/excelParser.ts`
- 其他模块目录

## Root Python 脚本

| 脚本 | 功能 |
|------|------|
| `generate_report_v3.py` | 从 JSON 生成独立 HTML 报告 |
| `generate_xlsx.py` | 从 JSON 生成 12-Sheet Excel (openpyxl) |
| `fix_html.py` | 修复 HTML 中多行模板字符串 |
| `check_quotes.py` | 检测 HTML 中多余引号 |
| `parse_rtf.py` | RTF 文件解码 |

## 分析维度

- **分析人(6)**：俞东旭, 张潇, 朱培源, 王偲涵, 章鹏, 胡煜星
- **品类(7)**：车门系统, 车身外扩件, 挡泥板, 机盖及附件, 牌照板支架, 其他, 饰条
- **拓展类型(3)**：原开品, 拓展品, 组合件

## 与新品复盘的关系

- **新品复盘** 是本项目的后身/重构版（更成熟，三周期完整脚本）
- 本项目的 Python 脚本（generate_report_v3.py/generate_xlsx.py）为早期版本
- 数据源可能相同（新品检查周源数据和PLP数据.xlsx）
