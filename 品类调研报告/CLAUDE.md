# 品类调研报告 — 汽车玻璃品类市场调研

> 正文必须用中文。本文件是项目迁移记忆文件，用于新 Claude Code 环境快速理解项目。

## 项目定位

美区亚马逊汽车玻璃品类市场调研。从 69.9 MB 源数据 Excel 中提取销售/竞争/定价数据，生成可视化分析报告。

## 目录结构

```
品类调研报告/
├── 玻璃品类调研2025.9.xlsx              # 源数据 (16 Sheet, 69.9 MB)
├── extract_data.js                       # Excel→JSON 数据提取脚本
├── corrected_visual_data.js              # 人工修正后的数据（修正了单位换算Bug）
├── read_excel.js                         # 读取并列出所有Sheet名
├── visualization_data.json               # 提取的原始JSON（有Bug）
├── glass_analysis_report.html            # 静态分析报告（科幻暗色主题）
├── glass_visualization_dashboard.html    # 交互式Chart.js仪表盘
├── product_research_template.html        # 通用化模板（无玻璃数据）
├── package.json / package-lock.json      # Node依赖（xlsx ^0.18.5）
├── node_modules/
├── temp_excel/                           # 临时目录（空）
└── temp_analysis/
    ├── analyze.js                        # Sheet结构分析脚本
    ├── read_excel.js                     # Excel读取脚本
    ├── analysis.json                     # 分析结果
    ├── package.json
    └── node_modules/
```

## 源数据 16 个 Sheet

| Sheet | 内容 |
|-------|------|
| 自身 | 自身产品销售/定价 |
| 市场 | 关键词、竞争（总量869万 listing，37.9万玻璃 listing，市占4.36%） |
| 信息 | 产品类别、材质 |
| 各维度均价 | 按车型/品牌/材质/尺寸的均价分析 |
| 销售数据 | 详细销售记录 |
| 其他 | 各维度销售拆分 |

## 关键指标（修正后）

| 指标 | 值 |
|------|-----|
| 月销量 | 1,012 件 (2025年8月) |
| 月收入 | $89,316.89 |
| 均价 | $88.26 |
| 价格区间 | $58 - $98 |
| 市占率 | 4.36% |
| Top品类 | Windshield 40%, Side/Front 25%, Side/Rear 20%, Back Glass 15% |
| 材质 | Tempered Glass 70%, Laminated 30% |

## 数据质量注意事项

`extract_data.js` 有单位换算 Bug：`monthlySales` 被解析为 8（实际应为1012），`averagePrice` 被解析为 89316.89（实际应为 $88.26）。**请使用 `corrected_visual_data.js` 作为权威数据源。**

## 外部CDN依赖（HTML仪表盘）

- chart.js + chartjs-plugin-datalabels
- Font Awesome 6.4.0
- Google Fonts: Orbitron, Exo 2

## 与其他项目关系

- 与"市调项目"有血缘关系：本项目的分析方法论后续被提炼为"市调项目"的通用模板框架
- 独立项目，不依赖其他项目运行
