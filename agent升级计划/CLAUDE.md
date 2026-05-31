# Agent 升级计划

> 正文必须用中文。thinking 块尽量中文，关键推理在正文标注。用户说"中文"时立刻全中文。
>
> **新会话启动时，先 Read `CLAUDE.md` 和 `SOP文档/AI工作流全链路SOP.md` 载入上下文，无需确认。**

## MCP 插件一览

| 插件 | 功能 | 命令/模型 | 费用 |
|---|---|---|---|
| `image-vision` | 图片理解 | 智谱 GLM-4V-Plus，5元/百万tokens | ~1分钱/张 |
| `image-gen` | 图片生成 | nano-banana-fast/gpt-image-2 等 5 个模型 | ¥0.06~/次 |
| `github` | GitHub 操作 | 搜仓库/Issue/PR/代码 | 免费 |
| `memory` | 跨会话知识图谱 | 实体记忆 | 免费 |
| `sequential-thinking` | 复杂问题分步推理 | — | 免费 |
| `context7` | 最新技术文档查询 | — | 免费 |
| `serena` | 代码导航与分析 | — | 免费 |
| `chrome-devtools` | 浏览器自动化 | — | 免费 |
| `playwright` | 浏览器自动化 | — | 免费 |
| `markitdown` | 文档格式转换 | — | 免费 |

---

## 一、核心铁律（RULE-001 ~ RULE-005）

### RULE-001：禁止猜测

**禁止使用**的词：应该是、大概率、可能、看起来像、好像、估计。

信息不足时：必须标记 `UNKNOWN`，必须返回缺失字段清单，必须请求补充数据。

### RULE-002：所有推理必须基于证据

每个结论必须给出：`claim`（断言）、`evidence`（依据）、`confidence`（置信度 0-1）。

```json
{
  "claim": "结论内容",
  "evidence": ["证据1", "证据2"],
  "confidence": 0.85
}
```

无依据的结论一律禁止。

### RULE-003：视觉模型禁止业务推理

GLM-4V **只做**：OCR、目标识别、图片描述、结构提取、特征识别。

GLM-4V **禁止**：fitment 判断、兼容性分析、OE 推断、平台车推断、Listing 优化、业务决策。

视觉模型只负责"看见什么"，业务逻辑统一由 DeepSeek 执行。

### RULE-004：结构化输出

模块间禁止自然语言裸传。所有传递使用 JSON Schema。

### RULE-005：高风险结果必须二次验证

高风险范围：fitment、OE号、年款、平台车、SKU映射、自动修改文件、自动生成运营数据。

至少通过 Tool验证 / Rule验证 / Schema验证 其中之一。

---

## 二、任务路由器（Task Router）

每个任务必须先归类，再分发给对应模型，禁止跳步。

```
Input → Task Classification → Data Collection → Structure Extraction
→ Validation → Reasoning → Verification → Output
```

### TYPE-A：视觉任务
OCR、图片识别、UI识别、产品识别、车型识别。
**只走 GLM-4V**，禁止先进 DeepSeek。

### TYPE-B：逻辑推理任务
fitment、OE分析、年款分析、数据逻辑、SKU分析。
**只走 DeepSeek**。

### TYPE-C：代码/数据任务
Python、SQL、CSV、Excel、数据清洗、可视化。
**DeepSeek → Python Runtime 真实执行 → DeepSeek 分析结果**。
禁止模型脑补计算结果。

### TYPE-D：生图任务
主图、场景图、修图、局部重绘。
**只走 maiziAI**。DeepSeek 只负责 Prompt 规划和场景描述，禁止直接生成图像逻辑结论。

---

## 三、模型分工与输出隔离

| 任务类型 | 模型/平台 | 允许 | 禁止 |
|----------|-----------|------|------|
| TYPE-A 视觉 | 智谱 GLM-4V-Plus | OCR/识别/描述 | 业务推理/决策 |
| TYPE-B 逻辑 | DeepSeek v4-pro | 推理/分析/决策 | 图片生成/图片理解 |
| TYPE-C 数据 | DeepSeek + Python | 代码/计算/图表 | 脑补结果 |
| TYPE-D 生图 | maiziAI | 生成/修图/inpainting | —（Prompt 由 DS 写）|

### 输出隔离规则

1. **GLM 输出**：原文直出，不改写、不润色、不总结、不翻译。
2. **maiziAI 输出**：只报成功/失败、路径、模型、费用，不评价内容。
3. **DeepSeek 输出**：只处理文本/代码/数据，不插手图片。
4. **禁止跨模型加工**：任一模型的输出不得作为另一模型的"参考"二次解释。
5. **Tool Result 优先级最高**：如果 Tool Result 与模型推理冲突，永远优先 Tool Result。
6. **错误隔离**：某模型失败时直报错误原文，不用其他模型猜测补救。

---

## 四、数据验证层

### Schema Validation
检查 JSON 格式、必填字段、字段类型、空值。失败立即重试。

### Rule Validation
硬规则检查（如 `vehicle.year >= 2015 AND platform == "GMT800"` 应触发 ValidationError）。

### Confidence Threshold

| 区间 | 级别 | 行为 |
|------|------|------|
| >= 0.90 | HIGH | 允许自动执行 |
| 0.75 - 0.89 | MEDIUM | 标注后输出 |
| < 0.75 | LOW | **必须请求人工确认，禁止自动执行** |

---

## 五、上下文管理

- 禁止全历史注入、禁止无限累积上下文
- 每一步保存状态（step/status/result），后续只读状态结果
- 禁止"之前好像识别过..."这类自然语言记忆，必须用结构化引用

---

## 六、错误恢复

- 同一错误最多重试 **2 次**
- 失败必须输出：error_type、reason、recoverable
- 禁止伪造成功结果

---

## 七、看图流程

1. Win+Shift+S 截图 → 剪贴板
2. 告诉 Claude "截好了"
3. Claude 运行 `clipboard3.ps1` 取图 → 调 `image-vision` → 返回 GLM 原文描述

PowerShell 脚本：`视觉模块/clipboard3.ps1`（保存剪贴板图片到 `~/Desktop/clipboard_test2.png`）

---

## 八、生图流程（V2 — 文案驱动）

**工作流顺序（V2 对调）**：先文案，后生图。图片基于卖点文案生成。

```
market_intel.json + listing_output.json
  → prompt_builder.py (DeepSeek 动态生成6张套图 Prompt)
    → batch_image_gen.py (maiziAI 生图)
      → image_validator.py (GLM-4V 验图)
```

### 6 张套图类型

| Key | 标签 | 说明 |
|-----|------|------|
| `main` | 产品主图 | 完整产品展示，**不限于白底**。摄影棚布光或户外场景（野地/沙漠/车间），根据产品类型自动选择最佳场景。 |
| `fitment` | 产品适配图 | 信息图风格，展示适配车型（年份+品牌+车型），干净的高端目录规格页风格。 |
| `install` | 产品安装图 | 产品安装于汽车的效果展示，明确示意安装位置。中性色车身。 |
| `selling_points` | 产品卖点图 | 基于文案 bullets 的可视化卖点展示。防晒→阳光场景、防锈→水珠/耐候、纹理→表面特写。选择最视觉化的 1-2 个卖点。 |
| `detail` | 产品细节图 | 微距特写，展示表面纹理和颜色。浅景深。镀铬反光/哑光颗粒/纹理凹凸。 |
| `shipping` | 发货售后图 | 物流/售后优势展示。Free Shipping / Fast Delivery / 30-Day Returns。仓库信息后续注入。 |

### 脚本

| 脚本 | 用法 |
|------|------|
| `生图/prompt_builder.py` | **DeepSeek 动态生成 6 张套图 Prompt**。读取 market_intel.json + listing_output.json → 调用 DeepSeek API → 输出 image_prompts.json |
| `生图/batch_image_gen.py` | 读取 image_prompts.json → maiziAI 批量生图（5级降级链） |
| `生图/image_gen.py` | 单张生图，被 batch 调用 |
| `生图/recovery/fallback_strategy.py` | 生图失败自动恢复策略 |

### Prompt 模板库

`生图/prompts/` 下按用途分三类，共 11 个 JSON 模板：

| 类别 | 目录 | 模板 |
|------|------|------|
| 文案 | `prompts/copywriting/` | `title_v1.json`, `description_v1.json` |
| 生图 | `prompts/image/` | `main_product_v1/v2`, `detail_v1/v2`, `fitment_v2`, `install_v2`, `selling_points_v2`, `shipping_v2`, `scene_v1` |
| 校验 | `prompts/validation/` | `image_check_v1.json`, `listing_check_v1.json` |

`prompt_builder.py` 运行时从模板库读取，由 DeepSeek 填充产品参数。

### 视觉校验模块

`视觉模块/verification/` 下三个校验器：

| 脚本 | 职责 |
|------|------|
| `image_validator.py` | GLM-4V 生图校验（logo/结构/浮空/数量） |
| `listing_validator.py` | Listing 文案校验（标题≤80字符/禁词/卖点数） |
| `schema_validator.py` | JSON Schema 校验（必填字段/类型/空值） |

用法：
```bash
# 第一步：生成 Prompt（需要 DeepSeek API Key）
python 生图/prompt_builder.py <mother_dir> --api-key sk-xxx

# 第二步：批量生图
python 生图/batch_image_gen.py <mother_dir> [--prompts-file <path>]
```

可用模型：

| 模型 | 分辨率 | 价格 |
|------|--------|------|
| nano-banana-fast | 1K | ¥0.06/次 |
| gpt-image-2 | 1K/2K/4K | ¥0.06~0.105/次 |
| gpt-image-2-official | 1K/2K/4K | ¥0.053~11.43/次 |
| nano-banana-2 | 1K/2K/4K | ¥0.12/次 |
| nano-banana-pro | 1K/2K/4K | ¥0.18/次 |

尺寸：1:1, 16:9, 4:3

生图铁律：
- 必须有参考图，禁止纯 Prompt 生图
- 禁止 AI 自主修改产品结构/新增部件/修改 OE 结构
- 优先 inpainting 局部修改，禁止整图重生成
- **禁止生成车标/品牌Logo**：所有生成图片不得包含汽车品牌标志（如 Ford/BMW/Toyota 等 OEM Logo）、商标、品牌文字，防止侵权
- **产品必须与背景自然融合**：禁止悬浮/漂浮，Prompt 必须描述空间关系（放置/摆放/安装）+ 光影（阴影、光源方向）+ 透视匹配

---

## API 平台

| 用途 | 平台 | Key 位置 |
|---|---|---|
| 图片理解 | 智谱 bigmodel.cn | `.mcp.json` → image-vision → args → `--api-key=` |
| 图片生成 | 麦子AI maizitech.cn | `.mcp.json` → image-gen → args → `--api-key=` |

---

## eBay Listing 规则

- eBay 产品 ID 从 URL 提取，如 `https://www.ebay.com/itm/XXX/304052751324` → ID 为 `304052751324`
- **所有输出文件按 SKU 命名目录归档**：`C:\Users\Administrator\Desktop\AI项目\产品卖点主图和信息生成\{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Product-Type}\`
- 每个产品目录结构：
  ```
  ├── 锚定产品xlsx/       # 锚定商品独立xlsx（6 Sheet）
  ├── 对手产品xlsx/       # 对手商品独立xlsx（6 Sheet）
  ├── 生成图片/           # AI生成套图 + image_prompts.json + image_batch.json + image_validation.json
  ├── 采集数据/           # product_*.json（爬虫原始数据）+ ebay_images/（参考图）
  ├── {SKU}.xlsx          # 汇总表（产品概览/竞品对比/图片索引/市场情报）
  ├── listing_output.docx # 标题+卖点 Word文档
  ├── listing_output.json # 标题+卖点 JSON
  ├── listing_output.md   # 标题+卖点 Markdown
  ├── market_intel.json   # 市场情报（含竞品分析 Rule 0-5）
  ├── source_links.json   # 锚点+对手链接清单
  └── ref_ebay.webp       # 参考图（从eBay自动下载）
  ```
- 独立 xlsx 使用 `爬虫/batch_xlsx.py` 生成（6 Sheet：Product Info / Item Specifics / Compatibility / Shipping & Returns / Seller Info / Images）
- 汇总 xlsx 使用 `爬虫/summary_xlsx.py` 生成：`python 爬虫/summary_xlsx.py <mother_dir> <SKU>`
- 使用 `md2docx.py` 将 Markdown 转为 Word 文档：`python md2docx.py <input.md> <output.docx>`
- **标题 ≤ 80 字符（含空格）**，80 字符满示例：`Set Of Door Hinges 4pcs Upper Lower For 1968-1979 Chevy Nova / Camaro / Firebird`
- 标题中禁止 OEM Logo、品牌词、商标、®/™ 符号
- 详情页文案 ≥ 5 点，每点突出一个卖点
- 图片禁止带车标/品牌Logo

### 产品归类规则（RULE-006）

**五个维度任一不同 = 不同 SKU，不可混在同一目录：**

| 维度 | 示例 | 区分项 |
|------|------|--------|
| 方位 | Front / Rear / Driver Side / Passenger Side | 前玻璃 ≠ 后玻璃 |
| 件数 | 1pc / 2pcs / 4pcs | 单只把手 ≠ 4件套 |
| 表面处理 | Chrome / Gloss Black / Matte Black / Textured | 镀铬 ≠ 亮黑 |
| 子类型 | Replacement / Cover / Trim / Shell | 替换件 ≠ 覆盖件 |
| 车门配置 | 2-door / 4-door-half / 4-door-full | 2门车窗 ≠ 4门全尺寸车窗 |

目录命名格式：`{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}`

爬虫提取时从标题 + Item Specifics 获取这五个维度。缺失填 `Unknown`。详见 [产品归类规则](product-classification-rules.md)。

### 方位提取规则（门件 vs 车体件）

**核心原则**：Front/Rear 对车门件和车体件含义完全不同。

| 产品类型 | Front 含义 | Rear 含义 | 2门简化规则 |
|----------|-----------|-----------|------------|
| **车门件**（车窗/把手/铰链/锁/门板/门镜） | 前车门 | 后车门 | ✅ 适用：2门车无后门，去掉 Front/Rear |
| **车体件**（保险杠/中网/翼子板/大灯/尾灯/机盖/尾门） | 车头 | 车尾 | ❌ 不适用：车头尾始终有意义 |

**车门件判断**：`parser/position_parser.py` 中 `_is_door_part()` 通过关键词检测产品是否为车门安装件。

**2门简化规则**：仅当 `车型为2门/coupe` **且** `产品为车门件` 时，去掉 Front/Rear（因为2门车只有前门，不存在前后门区分）。

**皮卡车厢类型速查表**：

| 车门配置 | 值 | 典型车型 | 后门窗尺寸 |
|----------|-----|---------|-----------|
| 2门 | `2-door` | Regular Cab / Single Cab / Standard Cab | 无后门窗 |
| 4门半尺寸 | `4-door-half` | Extended Cab / SuperCab / Double Cab / Quad Cab / Access Cab / King Cab | 后门窗较小（对开/反向门） |
| 4门全尺寸 | `4-door-full` | Crew Cab / SuperCrew / CrewMax / Mega Cab / Sedan | 后门窗全尺寸（四扇独立门） |

**注意**：Coupe = 2-door，Sedan = 4-door-full。不同车门配置的同一位置产品也互为不同SKU（如 4-door-half 后窗玻璃 ≠ 4-door-full 后窗玻璃）。

---

---
## 九、批量爬虫策略

### 爬虫工具

**脚本位置**: `爬虫/product_intel.py`
- Playwright + stealth 反检测 + 持久化浏览器 profile
- 完整 JS 提取（20+字段）：标题/价格/规格/兼容表/卖家/反馈/物流/支付/库存 + description_text（#desc_ifr 纯文本）
- **Item Specifics "See all" 自动展开**：EXTRACT_JS 先检查并点击所有 "See all" 折叠按钮，再提取完整规格列表（避免缺字段）
- 通过 eBay finders API 分页获取完整兼容表（每商品 300-500 条车型记录）
- 用法：`python 爬虫/product_intel.py <mother_dir>` 或 `python 爬虫/product_intel.py <mother_dir> --vision`
- 输出：每个商品保存为 `采集数据/product_{item_id}.json`

**规范化引擎**（`parser/` + `engine/` — Phase 1 重构）：

| 层级 | 文件 | 职责 |
|------|------|------|
| 解析层 | `parser/cab_parser.py` | 车门配置提取（Crew/Extended/Regular Cab），from_compat/from_specs/from_title |
| 解析层 | `parser/position_parser.py` | 方位提取（Front/Rear + Left/Right → Front-Rear/Both-Sides 多位置套件 + Inner/Outer + Upper/Lower），Exterior 防误判，含门件2门简化规则，多 spec key 兜底 |
| 解析层 | `parser/count_parser.py` | 件数提取（多 spec key：Number of Pieces/Quantity/Qty/Package Quantity/Set Size），标题 dual/twin/N-count |
| 解析层 | `parser/finish_parser.py` | 表面处理提取（Chrome/Black-Chrome/Smoke-Chrome/Gloss-Black/Satin-Black/Matte-Black/Textured-Black/Painted/Powder-Coated/Primered/Polished/Anodized/Brushed/Satin + 纯色），Textured 防误判 |
| 解析层 | `parser/vehicle_parser.py` | 车型提取（Year/Make/Model/Trim/Engine） |
| 解析层 | `parser/bed_length_parser.py` | 货箱长度提取 |
| 解析层 | `parser/structure_parser.py` | 结构提取（One-Piece/Multi-Piece），N-piece 数字模式 + assemble→assembl(ed\|y) 修复 |
| 解析层 | `parser/material_parser.py` | 材质提取（Zinc Alloy/Zinc/Polycarbonate/Nylon/PP/PU/TPE + 原13种），多 spec key 兜底 |
| 解析层 | `parser/color_parser.py` | 颜色提取 |
| 解析层 | `parser/accessory_parser.py` | 附件提取 |
| 融合层 | `engine/resolver.py` | 多源字段融合（按 field_priority.json 优先级链）+ 来源特异性覆盖（spec specificity 粒度优先） |
| 融合层 | `engine/canonicalize.py` | 主入口 `classify_product()` + fitment_type from_title() 正则提取 + 冲突检测 + 置信度计算 |
| 融合层 | `engine/conflict.py` | 跨字段冲突聚合 |
| 融合层 | `engine/confidence.py` | 启发式置信度评分 |

**xlsx 导出**: `爬虫/batch_xlsx.py`（独立）× `爬虫/summary_xlsx.py`（汇总）
- `python 爬虫/summary_xlsx.py <mother_dir> <SKU>` — 生成汇总表（6 Sheet：产品概览 / Valid竞品 / Excluded竞品 / 锚定产品 / 图片索引 / 市场情报）

**批量脚本**: `爬虫/_batch_intel.py`（批量爬虫）× `爬虫/_batch_images.py`（批量生图）× `爬虫/_merge_product_lines.py`（多行合并）

**任务队列**: `爬虫/queues/queue_manager.py` — pending/done/failed JSON 队列管理

### 图片生成

**脚本位置**: `生图/image_gen.py`（单张）+ `生图/batch_image_gen.py`（6张套图）+ `生图/prompt_builder.py`（DeepSeek Prompt 生成）

- `生图/prompt_builder.py` 读取 market_intel.json + listing_output.json，调用 DeepSeek API 动态生成 6 张套图 Prompt，输出 image_prompts.json
- `生图/batch_image_gen.py` 读取 image_prompts.json → 调用 maiziAI 生图。启动前自动清理前次失败残留的孤儿 `gen_*.png`
- `生图/batch_image_gen.py` 默认自动查找 `<mother_dir>/生成图片/image_prompts.json`，也可通过 `--prompts-file` 指定
- `生图/image_gen.py` 内置5级降级链：gpt-image-2 → nano-banana-2 → nano-banana-pro → gpt-image-2-official → nano-banana-fast
- 生成后须用 `视觉模块/verification/image_validator.py` 做 GLM-4V 视觉校验（logo/结构/浮空/数量）

### 代理与 IP 轮换

**双 mihomo 架构：**

| 实例 | 用途 | 代理端口 | API 端口 |
|------|------|---------|---------|
| Clash Verge Rev（GUI） | 日常上网 | 7897 | 无（被屏蔽） |
| 独立 mihomo（命令行） | 爬虫专用 | 7898 | **9098** ✓ |

**启动独立 mihomo：**
```bash
"C:\Program Files\Clash Verge\verge-mihomo.exe" -f "C:\Users\Administrator\Desktop\AI项目\agent升级计划\VPN\mihomo_scraper.yaml"
```

**自动节点轮换：** `VPN/clash_rotator.py` 通过 REST API（`PUT /proxies/{group}`）切换 `🔰 选择节点` 组内的 47 个节点。美国节点 2x 权重优先。

用法：
```python
from VPN.clash_rotator import rotate_node, get_current_node
rotate_node()        # 随机切换一个节点（避开当前）
get_current_node()  # 查看当前节点
```

- Clash Verge Rev，`mixed-port: 7897`，共 **46 个节点**（美国 2 个 + 日本 18 + 香港 11 + 新加坡 3 + 其他 12）
- **已验证：非美国节点 + US cookie 可正常展示美国市场数据**（实测 JP 节点，eBay 未拦截，价格/运费/位置均为 US）
- 爬虫 `warmup_browser()` 已写入 `shs=US` / `shss=NC` / `shzip=27513` cookie，eBay 优先读 cookie 判定 shipping to
- **全部 46 个节点可用于轮换**，美国节点优先（数据一致性最佳），非美国节点兜底

### 批量节奏

| 参数 | 值 |
|------|-----|
| 单次抓取间隔 | 30-60s 随机 |
| 单 IP 日安全上限 | 200-300 条 |
| 全节点日处理能力 | 500-1000 条（分时段） |
| 推荐批次 | 50 条/批，每批间隔 1-2 小时 |

### 单件成本估算

| 项目 | 时间 | 费用 |
|------|------|------|
| 爬虫 | ~35s | 免费 |
| DeepSeek 文案 | ~20s | ~¥0.01 |
| DeepSeek Prompt 生成 | ~10s | ~¥0.005 |
| 生图（6张, gpt-image-2 4K） | ~50s 并行 | ¥0.36 |
| GLM-4V 验图 | ~20s | ~¥0.03 |
| 导出 xlsx + docx | ~5s | 免费 |
| **合计** | **~2.3 分钟** | **~¥0.41** |

### 去重与聚类

- **爬虫不去重**，同一产品多条链接 = 市场情报
- 抓取完成后，DeepSeek 按车型/品类/规格聚类
- 每组基于头部 listing 做竞品分析（价格/标题策略/卖点角度）

---

## 十、竞品自动发现流水线（Phase 0.5）

### 架构概览

```
Stage 0: Anchor Canonicalization — classify_product()
Stage 1: Query Generation — build_queries() → eBay 搜索词
Stage 2: eBay Search — search_ebay() → 60 candidates (title only)
Stage 3: Light Ranking — rank_candidates() → title 级打分排序
Stage 4: Detail Scraping — scrape_batch() → 抓取 top 20-25 详情
Stage 5: Canonical Resolution — classify_product() → 候选规范化
Stage 6: Hard/Soft Rule Engine — filter_candidate() → approve/reject/borderline
Stage 7: Similarity Scoring — compute_similarity() → 加权评分
Stage 8: Output → approved / borderline / rejected
Stage 9: DB Persistence → market.db 入库（7 表：own_products/competitor_listings/relationships/price_snapshots/crawl_jobs/canonical_snapshots/ruleset_version）
```

### 新增模块

| 文件 | 职责 | 核心函数 |
|------|------|----------|
| `crawler/competitor_search.py` | Stage 1-2：查询构建 + eBay 搜索 | `build_queries()`, `search_ebay()`, `discover_candidates()` |
| `crawler/light_ranker.py` | Stage 3：title 级别打分 | `rank_candidates()` |
| `crawler/competitor_filter.py` | Stage 6：hard/soft 规则 + OE Fast Pass + product_semantics（cover/replacement 互斥） | `filter_candidate()`, `extract_oe_numbers()`, `oe_fast_pass()` |
| `crawler/similarity_engine.py` | Stage 7：加权字段重叠评分 | `compute_similarity()`, `classify_result()`, `score_candidates()` |
| `crawler/database.py` | Stage 9：SQLite 持久化 + 批量入库 | `MarketDB` — 7 表 CRUD + `ingest_analysis()` 整次入库 |

### 配置文件

| 文件 | 用途 |
|------|------|
| `config/vehicle_ontology.json` | 9 大车型家族（GM Full-Size Truck, Ford F-Series 等） |
| `config/query_templates.json` | 按产品类型的 eBay 搜索模板（primary + fallback） |
| `config/category_thresholds.json` | 品类差异化 similarity 阈值 |
| `config/filter_rules.json` | hard/soft rules 配置（含 OE Fast Pass / product_semantics cover/replacement 互斥） |
| `config/similarity_weights.json` | 8 项相似度权重（总分 100） |

### 三个 P0 设计要点

1. **OE Fast Pass**：candidate 和 anchor 的 OE/Interchange 号有交集 → 直接 Approved（similarity=1.0），跳过所有后续规则
2. **mismatch vs absent**：candidate 明确写了不同的 cab → HARD REJECT；candidate 没提 cab → 不 reject，仅 soft penalty -2
3. **复合 key 缓存**：SQLite 用 `(item_id, anchor_family, product_type, cab)` 复合主键，同一 listing 对不同车型/品类不污染

### 用法

```python
# 完整流水线
from engine.canonicalize import classify_product
from crawler.competitor_search import build_queries, search_ebay, discover_candidates
from crawler.light_ranker import rank_candidates
from crawler.competitor_filter import filter_candidate
from crawler.similarity_engine import score_candidates
from crawler.database import MarketDB
```

---
## 注意事项

- **Windows GBK 编码**：所有含 `¥` 或中文的 Python 脚本顶部须加：
  ```python
  import sys
  if sys.platform == 'win32':
      sys.stdout.reconfigure(encoding='utf-8', errors='replace')
  ```
- `.mcp.json` 的 `env` 字段在 Windows 上不生效，所有 Key 通过 `--api-key=` 命令行参数传递
- 智谱 GLM-4V-Flash 完全免费，可切换回去省费用
- `image-gen` 是异步 API，插件已内置轮询（最长 60 秒超时）
- 本工作区独立于 模板提取，插件路径已更新
- 最终输出必须包含：task / result / confidence / evidence / validation / assumptions / unknowns

---

## 十一、与其他项目的关系

本项目是 **AI项目** 工作区的核心引擎。共 8 个项目，关系如下：

```
agent升级计划 (核心引擎)
    ├── 输出 → 产品卖点主图和信息生成 (16个SKU目录)
    │
    独立项目 (不依赖本引擎):
    ├── 三部周报v1 (React SPA 周报看板，原型)
    ├── 新品复盘 (Python 周报/月报生成，正式版)
    ├── AI表格自动化 (钉钉OCR，一次性任务)
    ├── 品类调研报告 (玻璃品类2025.9调研，已完成)
    ├── 市调项目 (市场调研框架搭建，早期)
    └── 工作区 (VS Code workspace 配置)
```

| 项目 | 关系 | 状态 |
|------|------|------|
| **产品卖点主图和信息生成** | 本项目的输出目录 | 2品线完成/8品线待生图/5新SKU |
| **三部周报v1** | 独立（周报看板），本项目的原型 | salesStatus完成/5模块空壳 |
| **新品复盘** | 独立（周报月报），三部周报v1的后身 | 三周期脚本完整 |
| **品类调研报告** | 独立，方法论文本来源 | 已完成 |
| **市调项目** | 独立，方法论模板化 | 早期 |
| **AI表格自动化** | 独立，一次性任务 | 已完成 |
| **工作区** | VS Code 多根工作区配置 | 配置用 |

---

## 版本迭代规划

> 详见 `SOP文档/版本迭代思路.md`

| 版本 | 状态 | 内容 |
|------|------|------|
| **V1** | ✅ | Prompt 驱动生图 + 文案先行 |
| **V2** | ✅ | 多源融合规范化引擎（parser/ + engine/） |
| **V2.5** | ✅ | 竞品自动发现 P0（crawler/ + OE Fast Pass） |
| **V3** | 🔜 | P1 精度优化 + P2 商业维度 |
| **V4** | 📋 | 汽配产品知识库 |

执行原则：P0 缺一不可，P1/P2 跑一轮数据后再迭代，配置驱动 > 硬编码，mismatch ≠ absent。
