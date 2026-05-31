# 数据契约

## DataCenter 目标

DataCenter 负责统一读取主数据源、解析动态日期字段、输出周期信息，并提供各模块共享的 SKU 级基础字段。业务模块不应重复解析主销售 Excel。

## 通用周期字段

周报批次和业务周期是两个概念：

- `WeeklyReportContext` / `ReportPeriod` 表示同一份周报，例如 `reportId`、`reportDate`、`reportLabel`。
- `UnifiedPeriod` / `BusinessPeriod` 表示某个模块自己的业务统计周期。

同一份周报可以包含不同业务周期，最终通过 `reportId` 归并到同一份周报里，不能强行把所有模块对齐到同一个日期范围。

`PeriodType`：

- `SALES_THU_TO_WED`：销售周，周四至周三。
- `NATURAL_WEEK_MON_TO_SUN`：自然周，周一至周日。
- `DATE_SNAPSHOT`：日期快照，例如价格快照。
- `MONTHLY`：自然月。
- `FORECAST_WEEK`：预测周。

`UnifiedPeriod`：

- `id`：周期唯一 ID。
- `type`：周期类型，来自模块周期配置。
- `label`：原始周周期标签，例如 `4/16-4/22`。
- `startDate`：ISO 日期格式的周期开始日期。
- `endDate`：ISO 日期格式的周期结束日期。
- `reportDate`：可选，报表日期。
- `sourceModule`：可选，周期来源模块。

周期解析由 `dataCenter/periodParser.ts` 统一导出，周期配置由 `dataCenter/periodConfig.ts` 维护。

## 模块周期配置

每个模块必须声明自己的周期类型，当前配置如下：

- 总销售状态：`SALES_THU_TO_WED`
- 新品状态：`SALES_THU_TO_WED`
- 广告状态：`NATURAL_WEEK_MON_TO_SUN`
- 价格状态：`DATE_SNAPSHOT`
- 账号流量状态：`NATURAL_WEEK_MON_TO_SUN`
- 销量预估：`FORECAST_WEEK`

页面顶部必须展示模块自己的：

- 数据周期
- 周期口径

例如总销售状态展示 `4/30-5/6` 和 `周四至周三`；广告状态展示 `4/27-5/3` 和 `自然周，周一至周日`。

## SKU 基础字段

`BaseSkuRecord`：

- `sku`：SKU 或可识别的销售编码。
- `productName`：产品名称；当前主数据未稳定识别时为空字符串。
- `analyst`：分析人，缺失时使用 `未分组`。
- `category`：产品分类，缺失时使用 `未分组`。
- `productGrade`：产品等级，缺失时使用 `未分组`。
- `sales`：本周期销量，对应现有周销量口径。
- `revenue`：本周期销售额，对应现有周销售额口径。
- `marketShare`：市占比，由销量和直接对手出单推导；缺失时为 `null`。
- `currentPrice`：在售价；异常或缺失时为 `null`。
- `avgOrderPrice`：出单均价，销售额 / 销量；销量为 0 时为 `null`。
- `periodId`：所属 `UnifiedPeriod.id`。

## 动态日期字段解析规则

业务表存在随周期变化的动态列，例如：

- `4/30-5/6销量`
- `4/30-5/6销售额`
- `5/6市占比`
- `2026/5/6在售价`
- `4/27-5/3广告花费`
- `4/27-5/3ACoS`

字段名用于识别日期范围和指标，但不能只靠字段名判断周期类型。周期类型必须优先来自 `modulePeriodConfig`：

- 销售数据源里的 `4/30-5/6销量` 归属 `SALES_THU_TO_WED`。
- 广告数据源里的 `4/27-5/3ACoS` 归属 `NATURAL_WEEK_MON_TO_SUN`。
- 价格数据源里的 `2026/5/6在售价` 归属 `DATE_SNAPSHOT`。

主销售表动态列仍保留现有核心口径：

- 周销量列：按销售周期识别。
- 周销售额列：跟随销售周期匹配。
- 直接对手出单列：用于市占比推导。
- 在售价列：常带有日期前缀，例如 `2026/4/22在售价`。

解析规则统一保留在现有 Excel parser 和 DataCenter period parser 中。模块开发者不能在页面里重新用字符串规则扫描表头。

## 环比计算

环比只能在同周期类型内计算。

允许：

- 销售本期 `4/30-5/6` 对比销售上期 `4/23-4/29`。
- 广告本期 `4/27-5/3` 对比广告上期 `4/20-4/26`。

禁止：

- 用销售周期对比广告周期。
- 用自然周广告数据对比周四至周三销售数据。
- 在页面里临时拼接不同周期类型的数据做环比。

代码层可使用 `periodParser.ts` 中的 `getPreviousBusinessPeriod`、`canComparePeriods`、`assertComparablePeriods` 保持同周期类型比较。

## 模块状态摘要

`ModuleStatusSummary` 用于各模块统一输出状态：

- `moduleKey`
- `moduleName`
- `currentStatus`
- `riskLevel`
- `coreMetrics`
- `mainFindings`
- `nextActions`

后续模块的 Summary 文件可复用该结构，也可以按模块目标定义更合适的文案结构。Page 如何展示由模块负责人自行设计，但不能绕过周期和数据契约。

## 独立数据源

广告、账号流量、价格调整、新品清单、销量预测表等独立数据源，必须通过对应模块 adapter 接入：

- `adsStatusAdapter.ts`
- `accountTrafficStatusAdapter.ts`
- `pricingStatusAdapter.ts`
- `newProductStatusAdapter.ts`
- `salesForecastAdapter.ts`

adapter 可以合并 DataCenter 的 `BaseSkuRecord`，但不能改变主销售口径。
