# 模块交付指南

## 开发流程

1. 阅读本指南、`docs/03-data-contract.md` 和目标模块 README。
2. 只在目标模块目录内开发。
3. 先定义 Adapter 输入输出类型。
4. 再定义 Rules 异常规则。
5. 再定义 Summary 汇报文案生成方式。
6. 最后在 Page 中设计并展示模块内容。
7. 执行 `npm run build`，确认不影响其他模块。

## 允许修改目录

接手哪个模块，就只修改哪个目录：

- `src/modules/newProductStatus/`
- `src/modules/adsStatus/`
- `src/modules/pricingStatus/`
- `src/modules/accountTrafficStatus/`
- `src/modules/salesForecast/`

总销售状态 `src/modules/salesStatus/` 是成熟样板模块，非销售任务不要修改。

## 禁止修改文件

- `src/dataCenter/periodTypes.ts`
- `src/dataCenter/periodConfig.ts`
- `src/dataCenter/periodParser.ts`
- `src/dataCenter/reportContext.ts`
- `src/dataCenter/moduleRegistry.ts`
- `src/dataCenter/DataCenterProvider.tsx`
- `src/components/Sidebar.tsx`
- `src/styles/global.css`
- `src/utils/excelParser.ts`
- 其他模块目录

## 必须交付文件

每个模块交付必须包含：

- `Page.tsx`
- `Adapter.ts`
- `Summary.ts`
- `Rules.ts`
- `index.ts`
- `README.md`

## Adapter 要求

Adapter 负责数据转换。输入可以是 DataCenter 输出、模块独立数据源或两者合并结果；输出必须是明确 TypeScript 类型。页面不能直接解析 Excel、CSV 或原始报表。

## Rules 要求

Rules 负责异常判断。规则方向、阈值、严重程度和展示方式由模块负责人自行设计。环比规则只能比较相同 `PeriodType` 的周期。

## Summary 要求

Summary 负责周报文案。模块负责人自行设计汇报结构和输出方式，但文案必须面向业务汇报，不暴露技术实现细节。

## Page 要求

Page 只负责展示。模块负责人自行设计页面内容、指标展示、图表表格、异常规则和汇报输出方式。页面必须保留主项目框架中的模块标题、简介、数据周期、周期口径、数据来源状态和空数据状态。

公共组件可以按需要使用，例如 `ModulePageLayout`、`EmptyState`、`SectionCard`、`KpiCard`、`StatusTag`、`FilterBar`，但除基础壳子外不强制固定页面区域。

## 周期要求

模块不能自己定义周期。周期必须从 `weeklyReportContext` 和 `modulePeriodConfig` 获取。字段名只用于识别日期和指标，不能用来决定周期类型。

## Build 验收

交付前必须执行：

```bash
npm run build
```

构建失败必须修复。Vite chunk size warning 可以记录，但不等于失败。

## 整合方式

1. 将交付模块目录覆盖或合并到对应 `src/modules/<module>/`。
2. 检查没有修改禁止文件。
3. 检查模块 `index.ts` 导出完整。
4. 打开对应 Sidebar 入口验收页面。
5. 执行 `npm run build`。
6. 对比其他模块入口是否仍可进入。
