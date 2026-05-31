# 模块开发契约

## 必须遵守

1. 不要修改 DataCenter 核心逻辑，除非本次任务明确要求调整统一数据口径。
2. 不要私自改 Sidebar 的总结构和一级模块顺序。
3. 不要直接在页面组件里解析 Excel、CSV 或其他原始报表。
4. 不要私自写全局 CSS 覆盖已有页面。模块样式优先复用 `components/common` 和已有 class。
5. 不要重写现有总销售页面和 Excel 解析核心口径。
6. 不要把模块私有字段塞进通用类型，除非其他模块也会复用。

## 每个模块的交付结构

每个业务模块必须按以下文件交付：

```text
modules/<moduleName>/
  <ModuleName>Page.tsx
  <moduleName>Adapter.ts
  <moduleName>Summary.ts
  <moduleName>Rules.ts
  index.ts
```

职责边界：

- Page：只负责页面展示、交互状态和调用模块级数据。
- Adapter：负责把 DataCenter 或独立数据源转换成本模块数据结构。
- Summary：负责生成周报文字、结论、行动建议。
- Rules：负责异常判断规则、阈值和规则 ID。
- index.ts：统一导出模块能力，方便整合。

## 数据接入规则

总销售主数据必须通过 DataCenter 读取。广告关键词报告、账号流量报告、价格调整表等独立数据源，可以由模块自己的 adapter 接入，但不能在 Page 里直接处理原始文件。

Adapter 输出必须是明确的 TypeScript 类型，避免返回 `any` 或页面临时对象。

## UI 接入规则

模块负责人自行设计页面内容、指标展示、图表表格、异常规则和汇报输出方式。页面必须保留主项目框架中的模块标题、简介、数据周期、周期口径、数据来源状态和空数据状态。

公共组件按需复用，例如 `ModulePageLayout`、`EmptyState`、`SectionCard`、`KpiCard`、`StatusTag`、`FilterBar`。除基础壳子外，不强制固定页面区域。

## 提交前检查

模块开发完成后至少执行：

```bash
npm run build
```

如果新增了关键口径或复杂规则，应补充模块级说明文档或注释，并在交付说明中写清楚数据来源和字段依赖。
