# 产品卖点主图和信息生成

> 本目录是 `agent升级计划` 的输出目录。所有脚本和工具位于 `../agent升级计划/`。
> 新会话启动时，先 Read `../agent升级计划/CLAUDE.md` 获取完整工作流上下文。

## 项目定位

汽车后市场 eBay listing 的输出目录。承接 agent升级计划流水线产出的：竞品爬虫数据、AI 文案、AI 生成图。不包含独立脚本。

## 目录命名规范

每个 SKU 按 5 维度命名：`{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}`

## 标准产品目录结构

```
{SKU}/
├── 锚定产品xlsx/       # 锚定商品独立xlsx（6 Sheet）
├── 对手产品xlsx/       # 对手商品独立xlsx（6 Sheet）
├── 生成图片/           # AI生成套图 + image_prompts.json + image_batch.json
├── 采集数据/           # product_*.json + ebay_images/
├── {SKU}.xlsx          # 汇总表（产品概览/竞品对比/图片索引/市场情报）
├── listing_output.json # 标题+卖点 JSON
├── listing_output.md   # 标题+卖点 Markdown
├── listing_output.docx # 标题+卖点 Word
├── market_intel.json   # 市场情报
├── source_links.json   # 锚点+对手链接清单
└── ref_ebay.webp       # eBay参考图
```

## 品线状态（2026-05-31）

### ✅ 已完成（6图+文案+xlsx）
- Chevy-Silverado_1999-2014_Door-Handle (38 links)
- Chevy-Colorado_2004-2012_Door-Handle (10 links)

### ⏳ 待生图（爬取+文案done，缺图片）
- Chevy-Express_1996-2022_Door-Handle (8 links)
- Chevy-Tahoe_2007-2013_Door-Handle (5 links)
- Ford-F-Super-Duty_1999-2016_Door-Handle (9 links)
- Ford-F-150_2015-2022_Door-Window-Glass (8 links)
- Jeep-Grand Cherokee_2011_Door-Handle (3 links)
- Ram-1500_2009-2022_Door-Window-Glass (5 links)
- Dodge-Durango_2011-2020_Door-Handle (1 link)
- Cadillac-Escalade_2007-2014_Door-Handle (1 link)

### 🔧 新SKU（5维度命名，进度不一）
- Chevy-Silverado_2007-2013_Driver-Side_Black_1pc_Interior-Door-Handle (47 links)
- Chevy-Silverado_2007-2014_Front-Rear_Chrome_4pcs_Door-Handle (80 links)
- Ford-F-150_2015-2022_Rear-Driver-Side_Dark_Door-Window-Glass (organized)
- Ford-Mustang_1994-2004_Driver-Side_Tempered-Green_1pc_Door-Window-Glass (缺 listing)
- Universal_Rear_Glossy-Black_4pcs_Bumper-Diffuser (296 links)

## 生图流水线（任一 SKU 目录）

```bash
cd ../agent升级计划

# 步骤1: 生成生图 Prompt（需 DeepSeek API Key）
python 生图/prompt_builder.py "../产品卖点主图和信息生成/{SKU_DIR}" --api-key sk-xxx

# 步骤2: 批量生图（maiziAI，5级降级）
python 生图/batch_image_gen.py "../产品卖点主图和信息生成/{SKU_DIR}"

# 步骤3: 视觉校验（GLM-4V）
python 视觉模块/verification/image_validator.py "../产品卖点主图和信息生成/{SKU_DIR}"

# 步骤4: 导出汇总 xlsx
python 爬虫/summary_xlsx.py "../产品卖点主图和信息生成/{SKU_DIR}" {SKU}

# 步骤5: Markdown 转 Word
python md2docx.py "../产品卖点主图和信息生成/{SKU_DIR}/listing_output.md" "../产品卖点主图和信息生成/{SKU_DIR}/listing_output.docx"
```

## 关键依赖（全部在 ../agent升级计划/）

| 脚本 | 功能 |
|------|------|
| `爬虫/product_intel.py` | Playwright eBay 爬虫 |
| `生图/prompt_builder.py` | DeepSeek 生图 Prompt 生成 |
| `生图/batch_image_gen.py` | maiziAI 批量生图 |
| `视觉模块/verification/image_validator.py` | GLM-4V 验图 |
| `md2docx.py` | Markdown → Word |
| `爬虫/summary_xlsx.py` | 汇总 xlsx 生成 |
| `爬虫/batch_xlsx.py` | 独立产品 xlsx 生成 |

## 杂项说明

- `_vision_test/`：Universal 产品的测试副本（25/296 product JSON），测试用
- `品线归类建议.md`：10条品线归类和状态汇总
- `爬虫上传源数据.xlsx`：爬虫上传的源数据

## 与其他项目关系

- **上游**：agent升级计划（所有脚本和工具）
- **独立**：不依赖其他项目运行
