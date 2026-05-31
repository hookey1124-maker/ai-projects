# Agent 升级计划

> 正文必须用中文。thinking 块尽量中文，关键推理在正文标注。用户说"中文"时立刻全中文。

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

## 八、生图流程

1. 告诉 Claude 要生成什么 + 提供参考图（产品图/风格图，至少一种）
2. Claude 用 DeepSeek 写好 Prompt（禁止 DS 生成图像逻辑结论）
3. `/image-gen` → 选模型和尺寸 → maiziAI 生成 → 保存到 `~/Desktop/ai-images/`

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
  ├── 生成图片/           # AI生成套图 + image_batch.json + image_validation.json
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

**四个维度任一不同 = 不同 SKU，不可混在同一目录：**

| 维度 | 示例 | 区分项 |
|------|------|--------|
| 方位 | Front / Rear / Driver Side / Passenger Side | 前玻璃 ≠ 后玻璃 |
| 件数 | 1pc / 2pcs / 4pcs | 单只把手 ≠ 4件套 |
| 表面处理 | Chrome / Gloss Black / Matte Black / Textured | 镀铬 ≠ 亮黑 |
| 子类型 | Replacement / Cover / Trim / Shell | 替换件 ≠ 覆盖件 |

目录命名格式：`{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}`

爬虫提取时从标题 + Item Specifics 获取这四个维度。缺失填 `Unknown`。详见 [产品归类规则](product-classification-rules.md)。

---

---
## 九、批量爬虫策略

### 爬虫工具

**脚本位置**: `爬虫/product_intel.py`
- Playwright + stealth 反检测 + 持久化浏览器 profile
- 完整 JS 提取（20+字段）：标题/价格/规格/兼容表/卖家/反馈/物流/支付/库存
- 通过 eBay finders API 分页获取完整兼容表（每商品 300-500 条车型记录）
- 用法：`python 爬虫/product_intel.py <mother_dir>` 或 `python 爬虫/product_intel.py <mother_dir> --vision`
- 输出：每个商品保存为 `采集数据/product_{item_id}.json`

**xlsx 导出**: `爬虫/batch_xlsx.py`（独立）× `爬虫/summary_xlsx.py`（汇总）
- `python 爬虫/summary_xlsx.py <mother_dir> <SKU>` — 生成汇总表

### 图片生成

**脚本位置**: `生图/image_gen.py`（单张）+ `生图/batch_image_gen.py`（6张套图）

- `生图/batch_image_gen.py` 启动前自动清理前次失败残留的孤儿 `gen_*.png`，避免重复花钱
- 生图/image_gen.py 内置5级降级链：gpt-image-2 → nano-banana-2 → nano-banana-pro → gpt-image-2-official → nano-banana-fast
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
| 生图（6张, gpt-image-2 4K） | ~50s 并行 | ¥0.36 |
| GLM-4V 验图 | ~20s | ~¥0.03 |
| DeepSeek 文案 | ~20s | ~¥0.01 |
| 导出 xlsx + docx | ~5s | 免费 |
| **合计** | **~2 分钟** | **~¥0.40** |

### 去重与聚类

- **爬虫不去重**，同一产品多条链接 = 市场情报
- 抓取完成后，DeepSeek 按车型/品类/规格聚类
- 每组基于头部 listing 做竞品分析（价格/标题策略/卖点角度）

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
