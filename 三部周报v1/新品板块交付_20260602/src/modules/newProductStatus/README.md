# 新品状态模块 (newProductStatus)

> 跟踪新品上市、动销、爬坡、异常情况

## 模块概述

新品状态模块用于追踪和分析新品的销售表现、市场占有情况、广告投放效果等，为新品研发和运营决策提供数据支持。

## 周期口径

- **周期类型**: `SALES_THU_TO_WED` (周四至周三)
- **本期周期**: 4.30-5.6
- **上期周期**: 4.23-4.29

## 数据来源

数据来源于 `新品周报数据_{周期}.xlsx` 汇总文件，包含以下 10 个 Sheet：

| # | Sheet 名 | 核心内容 |
|---|----------|---------|
| 1 | 总体数据 | KPI 汇总（SKU/销量/销售额/出单率/分析及时率） |
| 2 | 品线维度 | 各品线 SKU/销量/销售额/有对手数 |
| 3 | 分析人维度 | 各分析人 SKU/销量/销售额 |
| 4 | 拓展类型 | 原开品/拓展品/组合件 出单率/销量/销售额 |
| 5 | 分析及时率 | 各分析人及时率/8日内无分析/超7日未分析 |
| 6 | 低占比新品 | 低占比 SKU 明细（25列） |
| 7 | 新品PLP | 广告总览+分析人/品线/拓展类型维度 |
| 8 | 新品出单情况 | Y/N/未出单分布 按分析人/品线维度 |
| 9 | 新品未出单原因 | A/B 双板块：原因分布/按分析人/按品线 |
| 10 | 新品PLG维度 | PLG 明细表 |

## 核心规则

### 8日出单情况规则

| 列值 | 含义 | 统计处理 |
|------|------|---------|
| **Y** | 8日内出单 | ✅ 计入已出单 |
| **N** | 8日外出单 | ✅ 计入已出单（出单较晚） |
| **未出单** | 真正从未出单 | ❌ 计入未出单 |
| **未上架** | 未来日期 | ❌ 不计入统计 |

### 低占比新品定义

同时满足：
1. 本期末市占比 < 75%
2. 有对手（对手销量 > 0）

### 分析及时率规则

- 8日内新品无分析：7日新品频次标签 = "异常"
- 超7日低占比未分析：7日频次标签 = "异常"

## 完整数据来源（v2.html）

本模块于 2026-05-13 整合了 `新品周报板块_4.30-5.6_v2.html` 的完整数据，包含：

- **cum43Data**：101 条完整新品追踪数据（93 条周期内 + 8 条周期外上架）
- **lowShareData**：40 条低占比新品明细（5.6 市占 < 75% 且有对手销量）
- **unorderAnData**：6 位分析人的未出单统计
- **unorderCatData**：6 条品线的未出单统计
- **orderTotalData**：6 条出单情况汇总
- **orderAnData**：6 位分析人的出单分布
- **orderCatData**：7 条品线的出单分布
- **mainFindings**：6 条主要发现
- **nextActions**：6 条下周动作

参考文件：`src/modules/newProductStatus/新品板块_4.30-5.6_v2.html`

## 交付结构

```
modules/newProductStatus/
├── NewProductStatusPage.tsx      # 主页面（4-Tab + 新增板块）
├── newProductStatusAdapter.ts    # 数据适配器（含完整 mock 数据）
├── newProductStatusRules.ts      # 异常规则
├── newProductStatusSummary.ts    # 周报文案
├── index.ts                      # 统一导出
├── README.md                     # 本文档
└── 新品板块_4.30-5.6_v2.html    # 原始参考文件（独立 HTML）
```

## 页面结构

### Tab 1: 总盘概览

- KPI 卡片（累计SKU/总销量/出单率/分析及时率）
- 新品出单情况分布
- 品线维度表（含本周销量/上周销量/环比）
- 分析人维度表（含本周销量/上周销量/环比）
- 拓展类型维度表
- 分析及时率表
- **新品出单情况**（新增：有对手口径 Y/N/未出单 + 按分析人/品线维度表）

### Tab 2: 低占比分析

- 低占比新品概览
- A. 有对手未出单新品（橙色主题）
- B. 无对手未出单新品（绿色主题）
- **新品未出单原因分析**（新增：按分析人/品线维度，含竞争无优势/无市场双口径）

### Tab 3: 广告追踪（PLP复盘）

- PLP 广告总览（42个SKU/119686曝光/$272.56花费/ROAS 6.44/ACOS 15.54%）
- PLP 核心指标（ROAS/CVR/CTR/CPC/CPA/ACOS/ACOAS）
- 分析人维度 PLP 表（含俞东旭/张潇/朱培源/王偲涵/章鹏/胡煜星）
- 品线维度 PLP 表（车门系统/挡泥板/机盖及附件/牌照板支架/其他/饰条）
- PLG 费率统计

### Tab 4: 汇报输出

- 本周期主要发现
- 下周重点动作
- 风险预警
- 可复制周报文案

## 异常规则

| 规则ID | 描述 | 严重级别 |
|--------|------|---------|
| new_product_low_share_high_risk | 低占比高风险新品 | 高 |
| new_product_no_sales | 新品未出单 | 中 |
| new_product_ramp_slow | 爬坡缓慢 | 低 |
| new_product_analysis_delay | 分析延迟 | 中 |
| new_product_competitor_pressure | 竞品压力 | 低 |

## 接入真实数据

后续需接入 DataCenter 数据源：

1. 在 `newProductStatusAdapter.ts` 中调用数据服务获取 JSON 数据
2. 使用 `parseNewProductStatusData()` 解析数据
3. 传入页面组件 `NewProductStatusPage.tsx`

```typescript
// 示例
import { parseNewProductStatusData } from './newProductStatusAdapter';

const jsonData = await dataService.getNewProductData('4.30-5.6');
const data = parseNewProductStatusData(jsonData);
```

## UI 设计规范

### 美化版本（2026-05-14）

本期对 UI 进行了全面美化，主要改进包括：

#### 视觉层次优化
- **Section 分组**：每个功能区块使用 `module-section` 包装，带有图标标题
- **卡片阴影**：统一使用项目级 CSS 变量 `var(--shadow)` 和 `var(--line)`
- **间距规范**：遵循 `18px` 基础间距，使用 `section-heading` 组件

#### Tab 导航增强
- 使用 `segmented` CSS 组件实现标签页样式
- 添加 Emoji 图标区分不同模块
- 悬停和激活状态自动应用 CSS 样式

#### 图表美化
- **饼图**：圆环图（innerRadius: 65）更现代
- **柱状图**：圆角顶部（radius），渐变色系区分本周/上周
- **折线图**：用于时序数据（及时率对比）
- **配色**：使用项目级 CSS 变量（`--blue`、`--green`、`--amber`、`--red`）

#### 表格优化
- 使用 `dimension-table` CSS 组件统一表格样式
- 固定表头（sticky）支持大数据量滚动
- 高亮行背景色区分重要数据
- 数字列右对齐，颜色编码变化趋势

#### 组件复用
- **KpiCard**：用于核心指标展示
- **StatusTag**：风险等级标签（低/中/高）
- **metric-chip**：小型指标卡片
- **action-card**：行动项卡片

#### 色彩语义化
| 颜色 | 含义 |
|------|------|
| 绿色 (#059669) | 正常、正向增长、达标 |
| 蓝色 (#2563eb) | 核心数据、关键指标 |
| 琥珀色 (#d97706) | 警示、需关注 |
| 红色 (#dc2626) | 风险、异常、未达标 |

---

*更新于 2026-05-14（UI 全面美化）*
