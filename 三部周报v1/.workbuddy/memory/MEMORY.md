# 长期记忆 - 三部周报系统

## 项目概览

**项目路径**：`c:\Users\Hardy\ai-projects\三部周报v1\New project 2`
**技术栈**：Vite + React + TypeScript + xlsx + Recharts

**项目定性**：多模块周报自动生成看板，支持上传 Excel 解析真实业务数据。

---

## 模块体系

### 已完成（成熟样板）
- **总销售状态** (`salesStatus`)：销量、销售额、市占比、在售价、出单均价等总销售分析，含 KPI、趋势图、维度拆解、异常排行、汇报文本

### 待开发（空壳）
- **新品状态** (`newProductStatus`)：跟踪新品上市、动销、爬坡、异常
- **广告状态** (`adsStatus`)：跟踪广告投放、ACOS、CPC等
- **价格状态** (`pricingStatus`)：跟踪价格变化、风险
- **账号流量状态** (`accountTrafficStatus`)：跟踪流量、访问、转化
- **销量预估** (`salesForecast`)：基于历史趋势预测销量

---

## 核心规则与约束（必须遵守）

### 周期类型
| 模块 | 周期类型 | 说明 |
|------|----------|------|
| 总销售状态 | `SALES_THU_TO_WED` | 周四至周三 |
| 新品状态 | `SALES_THU_TO_WED` | 周四至周三 |
| 广告状态 | `NATURAL_WEEK_MON_TO_SUN` | 自然周 |
| 价格状态 | `DATE_SNAPSHOT` | 日期快照 |
| 账号流量状态 | `NATURAL_WEEK_MON_TO_SUN` | 自然周 |
| 销量预估 | `FORECAST_WEEK` | 预测周 |

### 数据口径冻结
- **市占比** = 汇总销量 / (汇总销量 + 汇总直接对手出单)，不做行级平均
- **出单均价** = 销售额 / 销量，销量为0时 null
- **在售均价** = 有效在售价简单平均（过滤空值、0、负数、>=10000）
- **环比**：只能在同周期类型内计算，禁止跨周期类型比较
- **销售额**：USD 原值，严禁货币转换

### 辅助字段匹配规则（总销售表）
- 周期结束日、+1、+2、+3 四个候选日期
- 市占比/直接对手出单：`M/D` 格式，如 `4/23市占比`
- 在售价：`YYYY/M/D` 格式，如 `2026/4/23在售价`

### 禁止修改的文件
- `src/dataCenter/` 核心文件（periodTypes.ts, periodConfig.ts, periodParser.ts, reportContext.ts, moduleRegistry.ts, DataCenterProvider.tsx）
- `src/components/Sidebar.tsx`
- `src/styles/global.css`
- `src/utils/excelParser.ts`
- 其他模块目录

---

## 模块开发规范

### 每个模块交付结构
```
modules/<moduleName>/
  <ModuleName>Page.tsx   - 页面展示
  <moduleName>Adapter.ts - 数据转换
  <moduleName>Summary.ts - 周报文案
  <moduleName>Rules.ts   - 异常判断
  index.ts               - 统一导出
  README.md
```

### 页面必须包含
1. 模块标题、简介
2. 数据周期（来自 `weeklyReportContext`）
3. 周期口径（来自 `modulePeriodConfig`）
4. 数据来源状态
5. 空数据状态（`EmptyState` 组件）

### 公共组件（可复用）
- `ModulePageLayout` - 页面壳子
- `EmptyState` - 空状态
- `SectionCard` - 卡片
- `KpiCard` - KPI 指标卡
- `StatusTag` - 状态标签（颜色：低风险=绿，中=琥珀，高=红，未知=灰）
- `FilterBar` - 筛选器
- `ModulePeriodInfo` - 周期信息展示

### 周期信息获取方式
```typescript
const { dataPeriod, periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo('newProductStatus');
```

---

## UI 风格规范
- 整体：浅灰背景、白色卡片、深色侧边栏、**蓝色主强调色**
- 卡片：白底、浅色边框、8px 圆角、轻阴影，不用大面积装饰渐变
- 状态标签：胶囊样式，低风险绿/中风险琥珀/高风险红/未知灰
- 表格：表头清晰、数字右对齐、异常标签醒目
- 空数据用 EmptyState，不写成错误状态

---

## DataCenter 数据层

### 关键类型
- `BaseSkuRecord`：sku、productName、analyst、category、productGrade、sales、revenue、marketShare、currentPrice、avgOrderPrice、periodId
- `SalesFact`：行级事实数据（periodId、sku、salesQty、salesAmount、competitorOrders、marketShare、listingPrice、soldAvgPrice）
- `ProductDimension`：sku维度信息（category、analyst、productGrade等）
- `ModuleStatusSummary`：模块状态汇总（moduleKey、currentStatus、riskLevel、coreMetrics、mainFindings、nextActions）

### 低占比新品判定标准
市场份额 < 0.75 **且** 存在竞品订单

---

## 近期动态记录

- **2026-05-15**：修复新品板块数据问题（任务 #19）

### 修复内容

1. **四三累计数据过滤（关键修复）**
   - `corrected_data.json` 的 `cum43Data`：从109条过滤至**101条**（移除8条 05-09 周四至周三周期外上架新品）
   - 5.9日上架SKU：LYAM-X3058, LYAP-X1957, LYAP-X2025, LYAP-X2210-BK, LYAP-X2470, LYAP-X2471, LYAP-X2472, LYAP-X2473

2. **newProductStatusAdapter.ts 数据源对齐**
   - 导入 `expandTypeData`、`timelinessData`、`plpExpandTypes`、`plpPrevTotal`、`hasCompetitorUnsold`、`prevWeekKpi`、`plgStats`
   - 所有从空值/零值改为从 `corrected_data.json` 真实读取

3. **上周环比数据补充**
   - `corrected_data.json` 新增 `prevWeekKpi`：prevTotalSku=90, prevTotalSalesQty=151, prevTotalRevenue=$17,688.39
   - KPI 环比：SKU +12.2%、销量 +29.1%、销售额 +15.9%、及时率 +9.2%
   - 品类/分析人维度的上周明细不在原始数据中，显示 "--"

4. **PLG 费率统计补充**
   - `corrected_data.json` 新增 `plgStats`：plgEnabledCount=24, plpDisabledNoSaleCount=8, plpDisabledPlgActiveCount=23, plpEnabledCount=15

5. **数据周期显示修复**
   - 页面周期从自动计算 `5/14-5/20` 覆盖为 `4/30 - 5/6`
   - 原因：`buildWeeklyReportContext` 基于 `todayIso()` 自动计算

6. **验证**：构建通过

---

- **2026-05-14**：完成新品板块_4.30-5.6_v2.html 的全面数据更新

### 更新内容摘要
1. **KPI总览行**：在售SKU 101→109；8日Y 27→57；8日N 13→22；未出单 22→30（有对手3+无对手27）；已出单40→79；低占比新品40→39

2. **品类数据(catData)**：更新为正确的7个品类分布（车门系统36、其他33、机盖及附件9、饰条9、挡泥板9、车身外扩件12、牌照板支架1）

3. **分析人数据(anData)**：更新为正确的6位分析人汇总（张潇29、胡煜星25、俞东旭25、朱培源16、王偲涵10、章鹏4）

4. **新品出单情况**：更新按分析人和品类维度的出单情况数据

5. **新品未出单**：更新为30个未出单SKU（有对手3+无对手27），更新按分析人和品类维度的分布

6. **低占比新品(lowShareData)**：更新为完整的39条记录

7. **四三累计(cum43Data)**：更新为完整的101条记录

8. **各模块标题和说明文字**：同步更新为正确的统计数据

### 技术说明
- PowerShell替换操作会导致UTF-8编码损坏，**禁止使用PowerShell直接操作包含中文的HTML文件**
- 应使用Python脚本进行文件操作，确保正确的UTF-8编码处理
- 重新生成了完整的HTML文件（约100KB），包含所有正确的聚合数据和可视化
