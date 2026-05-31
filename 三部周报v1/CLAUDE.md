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
  | newProductStatus | ⚠️ 部分完成（3895行，硬编码数据） |
  | adsStatus | 🚫 空壳 |
  | pricingStatus | 🚫 空壳 |
  | accountTrafficStatus | 🚫 空壳 |
  | salesForecast | 🚫 空壳 |
- 每个模块按契约：`Page.tsx` + `Adapter.ts` + `Summary.ts` + `Rules.ts` + `index.ts` + `README.md`

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
