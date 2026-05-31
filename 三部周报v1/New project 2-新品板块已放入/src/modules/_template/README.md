# 标准模块开发模板

## 用途

`src/modules/_template/` 是后续业务模块开发的参考模板，不参与实际页面路由。模板只提供最小开发壳子，不预设 KPI、趋势图、异常清单、汇报输出或表格结构。

## 职责边界

- `TemplateStatusPage.tsx`：只负责基础页面壳子、周期信息和空状态。
- `templateStatusAdapter.ts`：负责把 DataCenter 或模块独立数据源转换成模块页面需要的数据结构。
- `templateStatusRules.ts`：负责异常规则、阈值、规则 ID 和规则结果。
- `templateStatusSummary.ts`：负责生成模块负责人自定义的汇报文案结构。
- `index.ts`：统一导出模块能力。

## 禁止事项

- 不允许 Page 直接解析 Excel、CSV 或原始报表。
- 不允许模块自己定义周期类型。
- 不允许绕过 `weeklyReportContext` 和 `modulePeriodConfig` 获取周期口径。
- 不允许私自修改 DataCenter 核心文件、Sidebar、全局 CSS 或其他模块目录。

## 页面要求

模块负责人自行设计页面内容、指标展示、图表表格、异常规则和汇报输出方式。页面必须保留模块标题、简介、数据周期、周期口径、数据来源状态和空数据状态。

## 周期要求

周期必须通过 `useModulePeriodInfo(moduleKey)` 读取，该 hook 内部来自 `weeklyReportContext` 和 `modulePeriodConfig`。

## 验收

模块交付前必须执行：

```bash
npm run build
```
