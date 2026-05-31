# 总销售状态模块

## 模块目标

总销售状态是当前系统的样板模块，承接已有成熟销售周报能力：上传主销售 Excel、识别动态周字段、展示销量、销售额、市占比、在售价、出单均价、维度拆解、异常排行和汇报文本。

## 当前开发状态

已接入真实主销售数据源和现有业务口径。本模块作为后续其他模块的参考样板，保留当前页面功能，不重写 UI，不改变 Excel 解析逻辑。

## 允许修改文件

- `SalesStatusPage.tsx`
- `salesStatusAdapter.ts`
- `salesStatusSummary.ts`
- `salesStatusRules.ts`
- `index.ts`
- `README.md`

## 禁止修改文件

- `src/utils/excelParser.ts`
- `src/dataCenter/periodTypes.ts`
- `src/dataCenter/periodConfig.ts`
- `src/dataCenter/reportContext.ts`
- `src/dataCenter/moduleRegistry.ts`
- `src/components/Sidebar.tsx`
- 其他模块目录

## 数据来源

主销售 Excel 先由现有 parser 解析，再通过 DataCenter 和 `salesStatusAdapter.ts` 转换为模块数据。页面不直接解析原始 Excel。

## 周期口径

`SALES_THU_TO_WED`，周四至周三。环比只能和同为 `SALES_THU_TO_WED` 的上期销售周期比较。

## 页面结构

- 数据周期、周期口径、数据来源状态
- 总盘概览
- 细分诊断
- 明细拆解
- 汇报输出
- 字段识别信息

## Adapter 输入输出

输入为 DataCenter 或主销售 ParseResult 转换后的结构化数据，输出销售事实、SKU 基础记录、周期、warnings。不得改变现有销售口径。

## Rules 规则要求

规则文件用于沉淀销量、销售额、市占比、均价等异常判断 ID 和阈值。新增规则要保持和现有 insight 口径一致。

## Summary 文案要求

汇报文案应围绕总盘表现、增长来源、拖累项、重点异常和下周动作输出，不暴露技术实现细节。

## 验收标准

- 原总销售页面功能正常。
- 上传 Excel、周期切换、维度拆解、汇报复制可用。
- 页面顶部展示数据周期、周期口径、数据来源状态。
- `npm run build` 通过。
