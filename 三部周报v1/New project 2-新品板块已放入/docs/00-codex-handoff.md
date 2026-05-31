# 周报自动生成看板 Codex 续接说明

## 当前项目状态

项目路径：
/Users/kun/Documents/New project 2

技术栈：
- Vite 4.x
- React
- TypeScript
- xlsx
- Recharts

当前已实现：
1. 页面默认进入上传 Excel 状态，真实业务数据不放入 public 目录
2. 支持上传 Excel
3. 读取 sheet：数据源
4. 自动识别固定字段：
   - 销售编码
   - 在售SKU
   - 分类
   - 三级类目
   - 分析人
   - 产品等级
   - 是否亏本
   - 库存
   - 可售周
5. 自动识别动态周期字段：
   - 周销量
   - 周销售额
   - 市占比
   - 直接对手出单
   - 在售价
6. 支持历史周期选择
7. 支持 6 个 KPI：
   - 销量
   - 销售额
   - 市占比
   - 直接对手出单
   - 在售均价
   - 售出均价
8. 支持 4 张趋势图
9. 支持按总体 / 分析人 / 产品分类 / 产品等级拆解
10. 支持点击表格行下钻
11. 支持异常标签、建议动作和中文自动总结

## 当前验证结果

- npm run build：通过
- dev server：http://localhost:5173/
- 默认状态：无内置真实 Excel，需上传本地数据源
- 识别结果：8 个周周期，1100 条 SKU 数据
- 最新周期：4/16-4/22
- 分析人字段：4月分析人
- 产品等级字段：4月等级

## 当前阶段目标

现在不要重写项目，不要重新搭建项目。

下一步目标是做只读审核和二轮优化：
1. 检查市占比口径
2. 检查售出均价口径
3. 检查周期映射
4. 检查历史周期切换
5. 检查细分趋势下钻
6. 检查自动总结是否有业务判断
7. 检查 UI 可读性和构建稳定性

## 重要业务口径

市占比：
市占比 = 汇总销量 / (汇总销量 + 汇总直接对手出单)

售出均价：
售出均价 = 汇总销售额 / 汇总销量

在售均价：
使用有效在售价平均值，空值、错误值、非数字不参与计算。

周期映射：
例如 4/16-4/22 周期应该对应：
- 4/16-4/22销量
- 4/16-4/22销售额
- 4/23市占比
- 4/23直接对手出单
- 2026/4/23在售价

注意：
不要写死列字母。
不要写死日期。
不要重构整个项目。

## 2026-04-28 第三批优化记录

本轮目标：
- 周会汇报观感优化
- 业务使用闭环

已完成：
1. 新增“本周核心结论”区，基于总盘、分类、等级、分析人聚合结果生成：
   - 总盘表现
   - 主要增长来源
   - 主要拖累来源
   - 重点异常对象
   - 下周建议动作
2. 新增“重点异常排行榜”：
   - 销售额拖累 TOP 10
   - 销量拖累 TOP 10
   - 市占下滑 TOP 10
   - 支持产品分类 / 产品等级 / 分析人切换
   - 点击榜单项可下钻到趋势对象
3. 新增“复制周报总结”按钮，使用 navigator.clipboard 复制结构化周报文本。
4. 新增“分析模式 / 汇报模式”切换：
   - 分析模式保留完整操作与字段状态
   - 汇报模式隐藏表格和字段详情，保留 KPI、核心结论、风险榜、趋势图和自动总结
5. 优化汇报观感：
   - KPI 数字更突出
   - 核心结论卡片化
   - 风险榜更适合周会扫描
   - warning 在汇报模式以简洁提示保留

新增文件：
- src/utils/reportGenerator.ts
- src/components/SummaryConclusion.tsx
- src/components/RiskRankingPanel.tsx

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过
- 默认 Excel 仍识别 8 个周期、1100 条 SKU，最新周期 4/16-4/22
- 复制周报文本生成逻辑已验证，包含标题、周期、对比周期和 warning 提示

注意：
- 本轮没有新增广告数据、价格数据、其他模块。
- 未改动第一批核心口径：周期辅助字段 fallback、市占缺失返回 null、在售价过滤、多标签异常规则仍保留。

## 2026-04-28 重点异常排行榜专项记录

本轮目标：
- 在总销售数据页面优先完善“重点异常排行榜”
- 不新增广告 / 价格 / 其他模块
- 不改动 Excel 解析、周期识别和核心数据口径

已完成：
1. `RiskRankingPanel` 保持接入总销售数据页面，展示：
   - 销售额拖累 TOP 10
   - 销量拖累 TOP 10
   - 市占下滑 TOP 10
2. 榜单维度支持切换：
   - 产品分类
   - 产品等级
   - 分析人
3. 每个榜单项明确展示：
   - 维度名称
   - 本期值
   - 变化值
   - 环比
   - 异常标签
   - 建议动作
4. 点击榜单项后调用现有下钻逻辑，联动趋势对象。
5. 市占下滑榜过滤 `marketShare === null` 或 `marketShareBpChange === null` 的对象，缺失市占数据不会进入榜单。

涉及文件：
- src/components/RiskRankingPanel.tsx
- src/styles/global.css
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动第一批核心数据口径。
- 构建仍有 Vite chunk size warning，仅为包体积提示，不影响运行。

## 2026-04-28 总销售数据页信息架构调整记录

本轮目标：
- 只调整“总销售数据”页面的信息架构、隐藏交互和自动总结层级
- 不改动 Excel 解析、周期识别、市占口径、价格过滤和多标签规则
- 不新增广告 / 价格 / 其他模块

已完成：
1. 页面主内容调整为四个区域：
   - 总盘概览区：KPI、总盘趋势、warning 简要提示、本周核心结论折叠入口
   - 细分诊断区：当前分析对象、趋势筛选器、返回总盘、细分趋势图、重点异常排行榜
   - 明细拆解区：多维表格，保留全量横向对比，不随下钻对象过滤
   - 汇报输出区：维度对比总结、当前对象总结、一键复制周报
2. 本周核心结论支持折叠：
   - 分析模式默认收起
   - 汇报模式默认展开
   - 用户可手动展开 / 收起
   - 切换周期不会强制重置，仅切换分析 / 汇报模式会按模式默认状态更新
3. 自动总结层级调整：
   - 总盘总结从“自动总结”中移出，合并到“本周核心结论”
   - 汇报输出区聚焦“维度对比总结”和“当前对象总结”
4. 维度对比总结增强：
   - 支持产品等级 A/B/C/D 横向比较
   - 支持产品分类增长 / 拖累对比
   - 支持分析人负责范围增长 / 拖累对比
   - 产品等级总结先整体比较 A/B/C/D，再分别解释具体等级问题
5. 重点异常排行榜移动到“细分诊断区”内部，继续支持点击下钻。

涉及文件：
- src/App.tsx
- src/components/SummaryConclusion.tsx
- src/components/SummaryPanel.tsx
- src/utils/summaryGenerator.ts
- src/utils/reportGenerator.ts
- src/styles/global.css
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动核心数据口径。
- 构建仍有 Vite chunk size warning，仅为包体积提示，不影响运行。

## 2026-04-28 趋势图近 8 周范围记录

本轮目标：
- 所有趋势图默认只展示“以当前选择周期为终点的近 8 周”
- 不改动 Excel 解析、周期识别、指标计算口径、KPI、表格、总结和排行榜逻辑

已完成：
1. 在 `App.tsx` 中新增图表专用周期数组：
   - `chartPeriods = periods.slice(Math.max(0, selectedPeriodIndex - 7), selectedPeriodIndex + 1)`
   - 仅用于趋势图
2. 保留完整 `periods`：
   - 周期选择器仍展示所有历史周期
   - KPI、表格、总结、重点异常排行榜仍按当前周期和上一周期计算
3. 总盘概览趋势图和细分诊断趋势图均改用基于 `chartPeriods` 生成的图表序列。
4. 趋势图区域新增轻量提示：
   - `趋势范围：起始周期 至 当前周期`
5. `TrendCharts` 新增 `rangeLabel` 展示能力，不影响图表计算。

涉及文件：
- src/App.tsx
- src/components/TrendCharts.tsx
- src/styles/global.css
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过
- 默认 Excel 仍识别 8 个周期、1100 条 SKU，最新周期 4/16-4/22

注意：
- 当前默认 Excel 正好 8 周，因此趋势图显示 8 周。
- 后续新增第 9 周后，趋势图会自动只显示当前选择周期往前最多 8 周。

## 2026-04-28 Vercel 部署前数据安全整理记录

本轮目标：
- 部署前检查真实业务 Excel 是否位于 public 目录
- 避免 Vercel 静态发布真实业务数据
- 页面默认进入上传 Excel 状态

已完成：
1. 检查 `public/data/weekly-sales.xlsx`：
   - 包含 `数据源` sheet
   - 包含 1100 行 SKU 级数据
   - 包含销售编码、在售 SKU、分析人、销售额、市占比、直接对手出单、在售价等业务字段
   - 判断为真实业务数据
2. 已将真实 Excel 从 `public/data/weekly-sales.xlsx` 移到：
   - `private-data/weekly-sales.xlsx`
3. 页面默认不再自动读取 public 默认文件，进入上传 Excel 引导状态。
4. `.gitignore` 已加入：
   - `node_modules/`
   - `dist/`
   - `.DS_Store`
   - `private-data/`
   - `public/data/weekly-sales.xlsx`
   - `public/data/*.xlsx`
   - 允许未来保留脱敏示例：`!public/data/demo-weekly-sales.xlsx`
5. README 已更新：
   - 说明线上部署不内置真实 Excel
   - 说明真实数据应放在 `private-data/`
   - 说明如需示例数据，只能使用脱敏 `public/data/demo-weekly-sales.xlsx`

涉及文件：
- src/App.tsx
- src/utils/excelParser.ts
- .gitignore
- README.md
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动核心业务计算逻辑。
- `private-data/weekly-sales.xlsx` 仅保留在本地并被 git 忽略，不会进入 Vercel 静态部署。

## 2026-04-28 总盘销售趋势补充均价趋势记录

本轮目标：
- 在总盘概览区的“总盘销售趋势”卡片中补充在售均价和出单均价趋势
- 不恢复总盘概览区 4 张完整趋势图
- 不改动 Excel 解析、周期识别、指标计算口径、市占、价格过滤和多标签规则

已完成：
1. `TrendCharts` 新增 `showPriceInSalesCard`：
   - 开启后会在销售趋势卡片内部追加“均价趋势”小图
   - 小图展示在售均价与出单均价两条线
2. 仅总盘概览区开启 `showPriceInSalesCard`：
   - 总盘概览仍只有 sales、market 两张核心趋势卡片
   - 均价趋势作为 sales 卡片内部子图展示
3. 均价趋势使用同一份图表序列，因此继续遵守近 8 周展示规则。
4. UI 文案统一：
   - 展示“在售均价”
   - 展示“出单均价”
   - 内部变量仍复用 `soldAvgPrice`
5. 细分诊断区逻辑保持不变：
   - 总盘 / 全部仍显示轻量提示
   - 选择细分对象后继续展示完整细分趋势

涉及文件：
- src/App.tsx
- src/components/TrendCharts.tsx
- src/components/KpiCards.tsx
- src/components/DimensionTable.tsx
- src/components/SummaryConclusion.tsx
- src/components/SummaryPanel.tsx
- src/utils/reportGenerator.ts
- src/utils/summaryGenerator.ts
- src/styles/global.css
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动核心数据口径。
- 构建仍有 Vite chunk size warning，仅为包体积提示，不影响运行。

## 2026-04-28 重点数据高亮细化记录

本轮目标：
- 继续优化总结文本、核心结论、维度总结、当前对象总结中的关键数据展示
- 不改动 Excel 解析、周期识别、指标计算口径、市占口径、价格过滤和多标签规则
- 不调整页面四段结构和布局顺序

已完成：
1. 保留并强化 `MetricChip` 展示：
   - 本周核心结论中销量、销售额、市占比、直接对手出单、售出均价以 chip 展示
   - 正向变化绿色，负向变化红色，中性灰色
2. 核心判断标签化：
   - 风险类使用红 / 橙色标签
   - 增长类使用绿色标签
   - 观察类使用蓝 / 灰色标签
   - warning 使用黄色标签
3. 主要增长来源和主要拖累来源 chip 化，避免长段落埋没关键对象。
4. 产品等级 A/B/C/D 对比进一步业务化：
   - A 档可识别“高货值均价压力”
   - B 档可识别“主力盘小幅下滑”
   - C 档可识别“成交结构改善”
   - D 档可识别“尾部动销改善”
5. 当前对象总结保留高亮卡片：
   - 当前对象
   - 销量、销售额、市占比、售出均价
   - 贡献占比变化
   - 异常标签与建议动作
6. 一键复制周报仍保持纯文本，并将分区标题改为【总盘表现】等更适合粘贴周报的格式。

涉及文件：
- src/components/SummaryPanel.tsx
- src/utils/reportGenerator.ts
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动核心数据口径。
- 构建仍有 Vite chunk size warning，仅为包体积提示，不影响运行。

## 2026-04-28 去重减重与汇报模式收敛记录

本轮目标：
- 根据 UI 只读审核结果做“去重减重 + 汇报模式收敛”
- 不改动 Excel 解析、周期识别、指标计算、市占口径、价格过滤和多标签规则
- 不新增广告 / 价格 / 其他模块

已完成：
1. `TrendCharts` 新增 `showCharts` 控制能力：
   - `sales`：销量 & 销售额趋势
   - `market`：市占比 & 直接对手出单趋势
   - `price`：在售均价 vs 售出均价趋势
   - `share`：销量占比 / 销售额占比趋势
2. 总盘概览区减重：
   - 顺序调整为 KPI → 本周核心结论 → 总盘核心趋势
   - 总盘概览只展示 sales、market 两张核心趋势图
   - 不再展示价格趋势和总盘占比趋势
3. 细分诊断区去重：
   - 总盘 / 全部状态不再重复展示总盘趋势图
   - 改为轻量提示卡，引导用户选择产品分类、产品等级或分析人
   - 选择细分对象后仍展示完整细分趋势图
4. 移除 TrendFilterBar 内重复的“当前分析对象”文案，保留细分诊断区标题右侧状态。
5. 汇报输出标题去重：
   - SummaryPanel 内部标题由“汇报输出”调整为“周报文本”
6. 汇报模式收敛：
   - 汇报模式保留 KPI、核心结论、2 张核心趋势、简化风险榜、汇报输出文本和复制按钮
   - 汇报模式隐藏趋势筛选器、重复总盘趋势、明细拆解表格、字段识别详情和总盘占比图
7. 细分诊断区视觉减重：
   - 降低内部图表和风险榜阴影
   - 增加总盘视角轻量提示卡
   - 风险榜 compact 模式隐藏建议动作长文本，仅保留核心风险扫描信息

涉及文件：
- src/App.tsx
- src/components/TrendCharts.tsx
- src/components/TrendFilterBar.tsx
- src/components/RiskRankingPanel.tsx
- src/components/SummaryPanel.tsx
- src/styles/global.css
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动核心数据口径。
- 构建仍有 Vite chunk size warning，仅为包体积提示，不影响运行。

## 2026-04-28 总结文本重点数据高亮记录

本轮目标：
- 优化“本周核心结论”“维度对比总结”“当前对象总结”的重点数据展示
- 不改动 Excel 解析、周期识别、指标计算、市占口径、价格过滤和多标签规则
- 不新增广告 / 价格 / 其他模块

已完成：
1. 新增轻量展示组件 `MetricChip`，用于突出指标名、本期值、环比变化和方向。
2. 本周核心结论展开态改为结构化展示：
   - 总盘表现使用销量、销售额、市占比、直接对手出单、售出均价 metric chips
   - 核心判断使用风险 / 增长 / warning 标签
   - 主要增长来源和主要拖累来源使用对象 chip
   - 下周建议动作使用 action card
3. 维度对比总结新增产品等级 A/B/C/D 对比卡片：
   - 展示销量环比、销售额环比、市占变化、主要标签
   - 下方保留解释文字
4. 当前对象总结在下钻时新增高亮卡片：
   - 当前对象名称
   - 销量、销售额、市占比、售出均价
   - 贡献占比变化
   - 异常标签和建议动作
5. 一键复制周报仍保持纯文本，并补充总盘核心指标结构化文本。

涉及文件：
- src/components/MetricChip.tsx
- src/components/SummaryConclusion.tsx
- src/components/SummaryPanel.tsx
- src/utils/reportGenerator.ts
- src/styles/global.css
- src/App.tsx
- docs/00-codex-handoff.md

验证：
- ./node_modules/.bin/tsc --noEmit：通过
- tsc --noEmit && vite build：通过

注意：
- 本轮未改动核心数据口径。
- 构建仍有 Vite chunk size warning，仅为包体积提示，不影响运行。

## 2026-04-28 DataCenter 骨架记录

本轮目标：
- 建立轻量 DataCenter 骨架，为后续总销售数据、广告数据、价格数据、新品共用周期和基础数据层做准备
- 不重构总销售数据模块
- 不改动 Excel 解析、周期映射和指标计算口径
- 不新增广告 / 价格 / 新品真实计算逻辑

已完成：
1. 新增 `src/dataCenter/types.ts`：
   - 定义 `ModuleKey`
   - 定义 `DataSourceStatus`
   - 定义 `DataSourceKind`
   - 定义 `UnifiedPeriod`
   - 定义 `ProductDimension`
   - 定义 `DataCenterState`
2. 新增 `src/dataCenter/periodEngine.ts`：
   - `convertWeeklyPeriodsToUnifiedPeriods`
   - `getCurrentPeriod`
   - `getPreviousPeriod`
   - `getVisiblePeriods`
   - `getVisiblePeriods` 保持“以当前选择周期为终点，往前最多 8 周”的规则
3. 新增 `src/dataCenter/selectors.ts`：
   - `selectCurrentPeriod`
   - `selectPreviousPeriod`
   - `selectVisiblePeriods`
   - `selectSourceStatus`
   - `selectWarningsBySource`
4. 新增 `src/dataCenter/DataCenterProvider.tsx`：
   - 提供 `periods`
   - 提供 `selectedPeriodId` / `setSelectedPeriodId`
   - 提供 `currentPeriod`
   - 提供 `previousPeriod`
   - 提供 `visiblePeriods`
   - 当前只从现有 sales `ParseResult` 初始化
   - ads / pricing / newProducts 暂时保持 `notUploaded`
5. `App.tsx` 仅包裹 `DataCenterProvider`：
   - 总销售模块仍使用旧的 `selectedPeriodIndex`
   - DataCenter 通过 `selectedSourcePeriodIndex` 跟随现有周期选择
   - `PeriodSelector` 仍使用旧 `WeeklyPeriod`
   - KPI、趋势图、表格、总结仍走原有 `metrics.ts`

注意：
- 当前 DataCenter 只接入 sales source。
- 总销售模块仍使用旧计算逻辑。
- 后续可以逐步迁移 `PeriodSelector`、模块 adapter 和跨模块 selector。

## 2026-04-29 静态快照导出记录

本轮目标：
- 生成可直接发给同事或会议展示的静态周报看板
- 复用当前 React 组件、CSS、Excel 解析逻辑和指标计算逻辑
- 使用真实 Excel 数据，不使用假数据、不手写 KPI / 趋势 / 排行榜 / 表格结果

已完成：
1. 新增 `scripts/exportStaticSnapshot.mjs`：
   - 优先查找 `public/data/weekly-sales.xlsx`
   - 当前实际使用 `private-data/weekly-sales.xlsx`
   - 通过 Vite SSR loader 加载当前项目的 `parseWorkbook` 和 `buildKpiMetric`
   - 将真实 Excel 解析后的 `ParseResult` 内嵌进静态 HTML
   - 将构建后的 CSS / JS 内联到单文件 HTML
2. `App.tsx` 新增静态快照入口：
   - 读取 `window.__STATIC_PARSE_RESULT__`
   - 静态模式走与正常模式相同的 `parseResult` 输入边界
   - 静态模式隐藏 Excel 上传入口
   - 静态模式仍进入 `DataCenterProvider`
3. `package.json` 新增脚本：
   - `npm run export:static`
4. 已生成输出目录：
   - `static-export/weekly-report-static.html`
   - `static-export/README-如何打开.md`
   - `static-export/verification-report.md`

数据校验结果：
- Excel 数据源：`private-data/weekly-sales.xlsx`
- SKU 行数：1100
- 周周期数量：8
- 最新周期：`4/16-4/22`
- 分析人字段：`4月分析人`
- 产品等级字段：`4月等级`
- 最新周期 KPI：
  - 销量：4,792
  - 销售额：331,484.75
  - 市占比：45.4%
  - 直接对手出单：5,771
  - 在售均价：94.35
  - 出单均价：69.17

周期映射校验：
- `2/26-3/4` → `3/4市占比`、`3/4直接对手出单`、`2026/3/4在售价`
- `3/12-3/18` → `3/20市占比`、`3/20直接对手出单`、`2026/3/19在售价`
- `4/16-4/22` → `4/23市占比`、`4/23直接对手出单`、`2026/4/23在售价`

打开方式：
- 可直接打开 `static-export/weekly-report-static.html`
- 如浏览器限制 file 打开，可运行：
  - `cd "/Users/kun/Documents/New project 2/static-export"`
  - `python3 -m http.server 8000`
  - 访问 `http://localhost:8000/weekly-report-static.html`

验证：
- `npx tsc --noEmit`：通过
- `npm run build`：通过
- `npm run export:static`：通过
- 使用 in-app browser 打开 `file:///Users/kun/Documents/New%20project%202/static-export/weekly-report-static.html`，页面可渲染总盘概览、核心结论、异常榜、明细拆解、汇报输出和复制按钮。

注意：
- 静态页与正式页面差异仅在于隐藏上传入口，并显示“静态快照展示模式”提示。
- 静态 HTML 内嵌真实业务数据，外发前请确认接收范围。

## 2026-04-29 第一批安全与冗余风险处理记录

本轮目标：
- 只处理 `static-export`、demo 数据风险、README 安全说明和 `.gitignore`
- 不改动 Excel 解析
- 不改动指标计算口径
- 不改动页面 UI
- 不开发新品模块

已完成：
1. `.gitignore` 增加提交保护：
   - `static-export/`
   - `*.xlsx`
   - `*.xls`
   - `*.xlsm`
   - `*.csv`
   - `*.tsv`
   - 保留已有 `dist/`、`private-data/`、`.DS_Store`、`*.tsbuildinfo`
   - 保留 `!public/data/demo-weekly-sales.xlsx` 和 `!src/demo/demoParseResult.ts` 例外
2. README 增加“提交与部署安全边界”：
   - 真实 Excel 不放入 `public/data`
   - 不提交真实业务数据文件
   - 不提交 `static-export/`
   - 真实静态快照只允许本地临时会议展示
   - 对外部署必须使用脱敏 demo 数据或上传模式
3. 确认 `static-export/weekly-report-static.html` 风险：
   - 文件可能内联真实 Excel 解析快照
   - `static-export/` 仅应作为本地临时产物
   - 当前已通过 `.gitignore` 忽略，避免误提交
4. 确认 `src/demo/demoParseResult.ts` 风险：
   - 仍被 `App.tsx` 静态导入
   - 会进入生产 bundle
   - 文件约 1.7 MB / 57380 行
   - 包含 demo SKU、销售编码、分析人、价格、市占、直接对手出单等字段
   - 当前字段值表现为 `DEMO-*` 编码和演示人员姓名，但是否完全脱敏仍需业务确认

待后续处理：
- 将 demo 数据改为动态导入或更小的脱敏样例，降低生产 bundle 体积
- 若继续保留静态导出脚本，应增加更强的安全提示或显式数据源参数
- `static-export/weekly-report-static.html` 本轮按要求未删除

## 2026-04-29 总销售数据业务口径冻结记录

本轮目标：
- 新增总销售数据业务口径冻结说明
- 不大改现有指标计算
- 不重构 `metrics.ts`
- 不开发新品模块
- 补充必要 warning，降低误判风险

已完成：
1. 新增 `docs/10-sales-metrics-definition.md`：
   - 冻结周期口径、当前周期、对比周期、近 8 周趋势范围
   - 明确辅助字段匹配规则为周期结束日、+1、+2、+3
   - 明确销量、销售额、市占、在售均价、出单均价和趋势窗口口径
2. 明确市占冻结公式：
   - `市占比 = 汇总销量 / (汇总销量 + 汇总直接对手出单)`
   - 不直接平均 Excel 行级市占比
   - 整列直接对手出单缺失时，市占为 `null`
3. `src/utils/excelParser.ts` 新增最小 warning：
   - 周期缺失销售额列时，提示销售额、出单均价和销售额趋势需谨慎
   - 周期存在直接对手出单字段，但动销 SKU 行中空值数量不少于 5 行且空值比例不低于 20% 时，提示市占判断需谨慎
4. 本轮未改变核心 KPI 计算公式：
   - 空值参与计算的现有方式未调整
   - `metrics.ts` 未重构
   - 页面 UI 未调整

验证：
- `./node_modules/.bin/tsc --noEmit`：通过
- `./node_modules/.bin/vite build`：通过
- Vite 仍有主 chunk 超过 500 kB 的提示，主要来自现有依赖和 demo 快照体积，不影响本轮口径冻结

## 2026-04-29 DataCenter 第二阶段记录

本轮目标：
- 继续统一框架和统一数据源
- 完成 DataCenter 第二阶段：salesAdapter、数据源注册、warning 标准化和口径文档补充
- 不新增新品 / 广告 / 价格模块页面
- 不改动总销售数据页面 UI
- 不改动 Excel 解析口径、周期映射逻辑和 `metrics.ts` 指标计算口径
- 不替换现有 `selectedPeriodIndex`
- 不把 `PeriodSelector` 切到 DataCenter

已完成：
1. 新增 `src/dataCenter/adapters/salesAdapter.ts`：
   - `adaptSalesParseResult(parseResult)` 输出统一 DataCenter 结果
   - 输出 `periods`
   - 输出 `productDimensions`
   - 输出 `salesFacts`
   - 输出标准化 `warnings`
2. `src/dataCenter/types.ts` 补充：
   - `SalesFact`
   - `SalesAdapterResult`
   - `DataCenterWarning`
   - `DataSourceRegistry`
   - 保留并扩展 `DataSourceKind`、`DataSourceStatus`、`DataSourceState`
3. `SalesFact` 生成规则：
   - 对 `parseResult.rows` 每一行、每一个 period 生成一条事实数据
   - `salesQty` 来自 `period.salesQtyColumn`
   - `salesAmount` 来自 `period.salesAmountColumn`，缺失时为 0
   - `competitorOrders` 来自 `period.competitorColumn`，整列缺失时为 `null`
   - `marketShare = salesQty / (salesQty + competitorOrders)`，整列对手出单缺失时为 `null`
   - `listingPrice` 继续使用有效在售价规则：`> 0 && < 10000`
   - `soldAvgPrice = salesAmount / salesQty`，销量为 0 时为 `null`
4. `DataCenterProvider` 改为调用 `adaptSalesParseResult`：
   - `periods`、`productDimensions`、`salesFacts`、`warnings` 来自 sales adapter
   - `sources.sales` 在有 `salesParseResult` 时为 `loaded`
   - `ads`、`pricing`、`newProducts` 仍为 `notUploaded`
5. `docs/10-sales-metrics-definition.md` 补充“当前待确认项”：
   - 明确 DataCenter 第二阶段不接管现有页面计算
   - 明确后续迁移前需要校验 adapter 聚合结果与 `metrics.ts` 完全一致

注意：
- 本轮没有改动 `src/App.tsx`。
- 本轮没有改动 `src/utils/excelParser.ts`。
- 本轮没有改动 `src/utils/periodParser.ts`。
- 本轮没有改动 `src/utils/metrics.ts`。
- 当前总销售页面 UI 和计算链路仍走原有 `parseResult` + `metrics.ts`。

## 2026-04-29 DataCenter 第三阶段校验层记录

本轮目标：
- 新增 DataCenter 只读校验工具
- 基于 `salesFacts` 重新聚合总盘 KPI
- 与当前 `metrics.ts` 的总盘聚合结果做对比
- 不改动现有总销售页面 UI
- 不替换 `metrics.ts`
- 不替换 `PeriodSelector`
- 不改动 Excel 解析、周期映射和指标计算口径
- 不新增广告 / 价格 / 新品模块

已完成：
1. 新增 `src/dataCenter/validation/salesFactsValidation.ts`：
   - `buildSalesFactsOverview(salesFacts, periodId, previousPeriodId)`
   - `compareSalesOverview(legacyOverview, factsOverview)`
2. `buildSalesFactsOverview` 聚合口径：
   - 销量按 period 汇总 `salesQty`
   - 销售额按 period 汇总 `salesAmount`
   - 对手出单整期全缺失时为 `null`，否则对有效数字求和
   - 市占为 `salesQty / (salesQty + competitorOrders)`，对手出单缺失时为 `null`
   - 在售均价对有效 `listingPrice` 做简单平均，有效值为 `> 0 && < 10000`
   - 出单均价为 `salesAmount / salesQty`，销量为 0 时为 `null`
   - 环比避免 `Infinity`，上期为 0 且本期增长时返回 `null`
3. `compareSalesOverview` 对比当前 `metrics.ts` 总盘输出：
   - 整数类容忍度：`0.01`
   - 金额 / 均价容忍度：`0.01`
   - 比率类容忍度：`0.0001`
   - 输出 `passed` 和差异列表
4. 新增 `src/dataCenter/validation/DataCenterValidationProbe.tsx`：
   - 组件返回 `null`，不渲染页面 UI
   - 仅在 dev 环境执行
   - 复用 `aggregateByDimension(..., '总体')` 生成 legacy overview
   - 默认检查最新周期、上一周期、再上一历史周期
   - 通过 `console.info('[DataCenter 校验] salesFacts vs metrics.ts 总盘 KPI', ...)` 查看结果
5. `src/App.tsx` 仅在 `DataCenterProvider` 内挂载校验探针：
   - 不改变 Sidebar、KPI、趋势图、表格、总结和页面布局
   - 正式 UI 仍走旧的 `parseResult` + `metrics.ts`

验证：
- `./node_modules/.bin/tsc --noEmit`：通过
- `./node_modules/.bin/vite build`：通过
- 使用 `private-data/weekly-sales.xlsx` 做内存校验：
  - SKU 行数：1100
  - 周周期数量：8
  - 校验周期：`4/16-4/22`、`4/9-4/15`、`4/2-4/8`
  - 三个周期 `salesFacts` 聚合结果与 `metrics.ts` 总盘输出均无差异
- Vite 仍有主 chunk 超过 500 kB 的提示，主要来自现有依赖和 demo 快照体积，不影响本轮校验层

注意：
- 当前校验层只做对比，不驱动 UI。
- 如果控制台出现差异，应先判断是事实层行级口径、汇总口径还是 legacy 字段映射差异，再决定是否进入迁移。

## 2026-04-29 DataCenter 第四阶段维度聚合校验记录

本轮目标：
- 扩展 DataCenter 校验层
- 基于 `salesFacts` 和 `productDimensions` 重新聚合维度表
- 与当前 `metrics.ts` 的维度表输出做对比
- 覆盖产品分类、产品等级、分析人
- 不改动现有页面 UI
- 不替换 `metrics.ts`
- 不替换 `PeriodSelector`
- 不改动 Excel 解析、周期映射和指标计算口径
- 不新增广告 / 价格 / 新品模块

已完成：
1. 扩展 `src/dataCenter/validation/salesFactsValidation.ts`：
   - 新增 `SalesFactsDimension`
   - 新增 `SalesFactsDimensionRow`
   - 新增 `buildSalesFactsDimensionRows(...)`
   - 新增 `compareSalesDimensionRows(...)`
2. `buildSalesFactsDimensionRows` 聚合口径：
   - `salesFacts` 与 `productDimensions` 优先通过 `sku` 关联
   - `sku` 无法关联时 fallback 到 `salesCode`
   - 无法关联时归入 `未分组`
   - 为贴合当前维度表输出，最终过滤 `未分组`、`无在售`
   - 按产品分类 / 产品等级 / 分析人生成维度行
   - 每个维度行计算 `skuCount`、`activeSkuCount`、销量、销售额、市占、在售均价、出单均价和环比指标
3. `compareSalesDimensionRows` 对比口径：
   - 按 `dimensionName` 对齐 legacy 行和 facts 行
   - 整数类容忍度：`0.01`
   - 金额 / 均价容忍度：`0.01`
   - 比率类容忍度：`0.0001`
   - legacy 有但 facts 没有输出 `error`
   - facts 有但 legacy 没有输出 `warning`
   - 最多输出前 20 条差异，避免 console 过长
4. 扩展 `DataCenterValidationProbe`：
   - 继续返回 `null`，不渲染页面 UI
   - 仅在 dev 环境 console 输出
   - 分别输出总盘、产品分类、产品等级、分析人的校验结果
   - 默认校验最新周期、上一周期、再上一历史周期
5. 修正 `salesAdapter` 的 `productDimensions` 生成：
   - 缺 `sku` 但有 `salesCode` 的行现在会保留
   - 这样维度校验可以通过 `salesCode` fallback 对齐
   - 本次修正仅影响 DataCenter 事实层关联，不影响现有页面计算

验证：
- 使用 `private-data/weekly-sales.xlsx` 做内存校验：
  - SKU 行数：1100
  - 周周期数量：8
  - `productDimensions` 行数：1100
  - 校验周期：`4/16-4/22`、`4/9-4/15`、`4/2-4/8`
  - 总盘校验：通过，差异 0
  - 产品分类校验：通过，差异 0
  - 产品等级校验：通过，差异 0
  - 分析人校验：通过，差异 0

注意：
- 本轮初次校验发现产品分类“挡泥板” `skuCount` 少 2，原因是 DataCenter adapter 曾跳过缺 SKU 但有销售编码的行。
- 已通过保留这类行并使用 `salesCode` fallback 修正，复验后全部通过。
- 当前校验层仍只做对比，不驱动 UI。

## 2026-04-29 DataCenter 第五阶段趋势序列校验记录

本轮目标：
- 扩展 DataCenter 校验层
- 基于 `salesFacts` 生成近 8 周趋势序列
- 与当前 `metrics.ts` 的 `buildTrendSeries` 输出做对比
- 不改动现有页面 UI
- 不替换 `metrics.ts`
- 不替换 `PeriodSelector`
- 不改动 Excel 解析、周期映射和指标计算口径
- 不新增广告 / 价格 / 新品模块

已完成：
1. 扩展 `src/dataCenter/validation/salesFactsValidation.ts`：
   - 新增 `SalesFactsTrendDimension`
   - 新增 `SalesFactsTrendPoint`
   - 新增 `buildSalesFactsTrendSeries(...)`
   - 新增 `compareSalesTrendSeries(...)`
2. `buildSalesFactsTrendSeries` 口径：
   - 趋势范围为以 `selectedPeriodId` 为终点，往前最多 8 周
   - `total` 使用全部 `salesFacts`
   - 产品分类 / 产品等级 / 分析人通过 `productDimensions` 过滤
   - `salesFacts` 与 `productDimensions` 优先通过 `sku` 关联，fallback 到 `salesCode`
   - 无法关联时归入 `未分组`
   - 每个趋势点计算销量、销售额、对手出单、市占、在售均价、出单均价、SKU 数、动销 SKU 数、销量占比和销售额占比
3. `compareSalesTrendSeries` 对比口径：
   - 按 `periodLabel` 对齐 legacy 趋势点和 facts 趋势点
   - 比较 `salesQty`、`salesAmount`、`competitorOrders`、`marketShare`、`listingAvgPrice`、`soldAvgPrice`、`skuCount`、`activeSkuCount`、`salesQtyShare`、`salesAmountShare`
   - 整数类容忍度：`0.01`
   - 金额 / 均价容忍度：`0.01`
   - 比率类容忍度：`0.0001`
   - legacy 有但 facts 没有输出 `error`
   - facts 有但 legacy 没有输出 `warning`
   - 最多输出前 20 条差异
4. 扩展 `DataCenterValidationProbe`：
   - 继续返回 `null`，不渲染页面 UI
   - 仅在 dev 环境 console 输出趋势校验结果
   - 验证 selectedPeriod 为 `4/16-4/22` 和 `4/9-4/15` 两种近 8 周窗口

验证范围：
- 总盘
- 产品分类：`车身外扩件`、`挡泥板`、`车门系统`
- 产品等级：`A`、`B`、`C`、`D`
- 分析人：`张潇`、`王偲涵`、`俞东旭`
- selectedPeriod：`4/16-4/22`、`4/9-4/15`

验证结果：
- 使用 `private-data/weekly-sales.xlsx` 做内存校验：
  - SKU 行数：1100
  - 周周期数量：8
  - 总盘 KPI 校验：仍通过
  - 产品分类 / 产品等级 / 分析人维度聚合校验：仍通过
  - 趋势序列校验：全部通过，差异 0
- 所有指定趋势样本均存在，未发生跳过。

注意：
- 当前趋势校验只做对比，不驱动 UI。
- 现有趋势图仍使用 `buildTrendSeries` 和 `App.tsx` 中的 `chartPeriods`。
- 后续如迁移趋势图到 DataCenter，应先保留该校验层作为回归保护。

## 2026-04-29 DataCenter 第六阶段 sales selectors 记录

本轮目标：
- 封装正式 DataCenter sales selectors
- 复用已经通过校验的 `salesFacts` 聚合逻辑
- 不改动现有页面 UI
- 不替换 `metrics.ts`
- 不替换 `PeriodSelector`
- 不改动 Excel 解析、周期映射和指标计算口径
- 不新增广告 / 价格 / 新品模块

已完成：
1. 新增共享计算层 `src/dataCenter/metrics/salesFactsMetrics.ts`：
   - `buildSalesFactsOverview`
   - `buildSalesFactsDimensionRows`
   - `buildSalesFactsTrendSeries`
   - `SalesFactsOverview`
   - `SalesFactsDimensionRow`
   - `SalesFactsTrendPoint`
   - `SalesFactsDimension`
   - `SalesFactsTrendDimension`
2. `src/dataCenter/validation/salesFactsValidation.ts` 调整为复用共享计算层：
   - 保留原有 validation 导出路径
   - compare 函数继续存在于 validation 中
   - 不改变已通过校验的聚合口径
3. 新增 `src/dataCenter/salesSelectors.ts`：
   - `selectSalesOverviewFromFacts`
   - `selectSalesOverview`
   - `selectSalesDimensionRowsFromFacts`
   - `selectSalesDimensionRows`
   - `selectSalesTrendSeriesFromFacts`
   - `selectSalesTrendSeries`
   - `selectSalesSourceStatus`
4. `selectSalesSourceStatus` 返回：
   - `status`
   - `rowCount`
   - `periodCount`
   - `warningCount`
   - `sourceName`
   - 原始标准化 `warnings`

验证：
- 使用 `private-data/weekly-sales.xlsx` 做内存校验：
  - SKU 行数：1100
  - 周周期数量：8
  - sales source：`loaded`
  - `rowCount`：1100
  - `periodCount`：8
  - `warningCount`：1
  - selector smoke test：通过
  - 总盘 KPI 校验：仍通过，差异 0
  - 产品分类 / 产品等级 / 分析人维度聚合校验：仍通过，差异 0
  - 趋势序列校验：仍通过，差异 0

注意：
- 当前 UI 仍未迁移到 sales selectors。
- 现有总销售页面仍使用旧的 `parseResult` + `metrics.ts` 链路。
- sales selectors 只是为后续只读调试面板或逐步迁移准备正式入口。
