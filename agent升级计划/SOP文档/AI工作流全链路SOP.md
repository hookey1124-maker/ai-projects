# AI 半自动化 eBay Listing 工作流 — 全链路 SOP

> 版本：v2.4
> 日期：2026-05-27
> 适用范围：eBay 汽车配件 Listing 半自动化生成（爬虫 → 竞品分析 → 文案 → Prompt构建 → 生图 → 验图 → 导出）

---

## 目录

1. [概述与架构](#1-概述与架构)
2. [环境搭建](#2-环境搭建)
3. [AI 模型与 MCP 插件](#3-ai-模型与-mcp-插件)
4. [任务路由（Task Router）](#4-任务路由task-router)
5. [网络环境搭建](#5-网络环境搭建)
6. [爬虫系统](#6-爬虫系统)
7. [图片理解（GLM-4V）](#7-图片理解glm-4v)
8. [图片生成（maiziAI）](#8-图片生成maiziai)
9. [文案生成与导出](#9-文案生成与导出)
10. [产品归档结构](#10-产品归档结构)
11. [批量化方案与成本](#11-批量化方案与成本)
12. [核心铁律速查](#12-核心铁律速查)
13. [故障排查](#13-故障排查)
14. [版本记录](#14-版本记录)

---

## 1. 概述与架构

### 1.1 工作流全景

```
Phase 0.5 竞品自动发现（NEW）：
  锚点 eBay URL → classify_product() → build_queries() → eBay 搜索
    → Light Rank → 详情抓取 → Canonicalize → Hard/Soft Filter
    → Similarity Scoring → Approved 竞品列表 → SQLite Memory

Phase 1 竞品分析 + 内容生成（已有）：
  竞品列表 → DeepSeek 竞品分析 → market_intel.json
                    ↓
        参考图 ← GLM-4V 图片理解（产品特征提取）
                    ↓
          DeepSeek 文案（标题+卖点）→ listing_output.json
                    ↓
          DeepSeek Prompt 构建（prompt_builder.py）
                    ↓
        maiziAI 生图（6张/产品，基于卖点文案）
                    ↓
        GLM-4V 视觉校验（image_validator.py）
                    ↓
        导出（.docx + .xlsx）→ SKU 目录
```

### 1.2 模型分工

| 角色 | 模型/平台 | 职责 | 禁止 |
|------|----------|------|------|
| 文本推理 | DeepSeek v4-pro | 数据分析、文案生成、竞品分析、聚类 | 图片理解、图片生成 |
| 图片理解 | 智谱 GLM-4V-Plus | OCR、目标识别、特征提取、构图验证 | 业务推理、fitment 判断 |
| 图片生成 | maiziAI（麦子AI） | 产品主图、场景图、局部重绘 | — |
| 代码执行 | Python Runtime | 数据处理、文件导出、格式转换 | 脑补计算结果 |

### 1.3 目录结构

```
c:\Users\Hardy\ai-projects\
└── agent升级计划/                  # 主工作区
    ├── CLAUDE.md                   #   核心规则文件（必须保留在根目录）
    ├── .mcp.json                   #   MCP 服务器注册
    ├── .claude/                    #   项目级配置
    │   ├── settings.json           #     权限白名单
    │   └── skills/                 #     Skill 定义
    ├── MCP/                        #   MCP 插件
    │   ├── mcp-image-gen/          #     生图 MCP 插件
    │   └── mcp-image-vision/       #     看图 MCP 插件
    ├── 视觉模块/                    #   图片理解与校验
    │   ├── clipboard3.ps1          #     截图取图脚本
    │   └── verification/           #     视觉校验
    │       ├── image_validator.py  #       GLM-4V 生图校验
    │       ├── listing_validator.py#       Listing 文案校验
    │       └── schema_validator.py #       JSON Schema 校验
    ├── 生图/                       #   图片生成
    │   ├── prompt_builder.py       #     DeepSeek 动态 Prompt 生成（NEW V2）
    │   ├── image_gen.py            #     单张生图（5级降级链）
    │   ├── batch_image_gen.py      #     批量6张套图（读取 image_prompts.json）
    │   ├── recovery/               #     生图故障恢复
    │   │   └── fallback_strategy.py#       自动降级恢复策略
    │   └── prompts/                #     Prompt 模板库（11+ 模板）
    ├── 爬虫/                       #   数据采集与导出
    │   ├── product_intel.py        #     eBay 爬虫（Playwright + stealth + finders API）
    │   ├── batch_xlsx.py           #     独立商品 JSON → xlsx（6 Sheet）
    │   ├── summary_xlsx.py         #     SKU 汇总 xlsx（4 Sheet）
    │   ├── _batch_intel.py         #     批量爬虫调度
    │   ├── _batch_images.py        #     批量生图调度
    │   ├── debug_search.py         #     eBay 搜索调试
    │   ├── playwright_template.py  #     Playwright 通用模板
    │   ├── search_competitors.py   #     竞品搜索（旧版）
    │   └── queues/                 #     任务队列
    │       └── queue_manager.py    #       pending/done/failed 管理
    ├── crawler/                    #   竞品自动发现（Phase 0.5 NEW）
    │   ├── competitor_search.py    #     Stage 1-2：查询构建 + eBay 搜索
    │   ├── light_ranker.py         #     Stage 3：title 级别打分
    │   ├── competitor_filter.py    #     Stage 6：hard/soft 规则 + OE Fast Pass
    │   ├── similarity_engine.py    #     Stage 7：加权字段重叠评分
    │   └── database.py              #     Stage 9：SQLite 持久化（market.db 7表 + MarketDB CRUD）
    ├── engine/                     #   规范化引擎（Phase 1）
    │   ├── canonicalize.py         #     多源融合 classify_product()
    │   ├── resolver.py             #     字段优先级融合 + 来源特异性覆盖
    │   ├── conflict.py             #     冲突检测
    │   └── confidence.py           #     置信度计算
    ├── parser/                     #   字段解析器（Phase 1）
    │   ├── vehicle_parser.py       #     车型（Year/Make/Model/Trim/Engine）
    │   ├── cab_parser.py           #     车门配置
    │   ├── position_parser.py      #     方位
    │   ├── count_parser.py         #     件数
    │   ├── finish_parser.py        #     表面处理
    │   ├── material_parser.py      #     材质
    │   ├── color_parser.py         #     颜色
    │   ├── structure_parser.py     #     结构（One-Piece/Multi-Piece）
    │   ├── bed_length_parser.py    #     货箱长度
    │   └── accessory_parser.py     #     附件
    ├── config/                     #   配置文件
    │   ├── field_priority.json     #     字段优先级链
    │   ├── field_risk_weight.json  #     风险权重
    │   ├── canonical_maps.json     #     别名→canonical 映射
    │   ├── noise_keys.json         #     噪音键过滤
    │   ├── vehicle_ontology.json   #     车型家族（Phase 0.5）
    │   ├── query_templates.json    #     eBay 搜索模板（Phase 0.5）
    │   ├── category_thresholds.json#     品类差异化阈值（Phase 0.5）
    │   ├── filter_rules.json       #     hard/soft 规则（Phase 0.5）
    │   ├── similarity_weights.json #     相似度权重（Phase 0.5）
    │   └── specificity_scores.json #     来源特异性粒度（Phase 0.5.1）
    ├── VPN/                        #   代理与网络
    │   ├── clash_rotator.py        #     Clash 节点自动轮换
    │   └── mihomo_scraper.yaml     #     独立 mihomo 配置（47节点）
    ├── SOP文档/                    #   文档
    │   ├── AI工作流全链路SOP.md     #     本文件
    ├── md2docx.py                  #   Markdown → Word 转换
    └── browser_profile/            #   浏览器持久化 Profile

c:\Users\Hardy\ai-projects\
└── 产品卖点主图和信息生成/         # 输出归档（按 SKU 命名目录）
    └── {Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}/
        ├── 锚定产品xlsx/           #   锚定商品独立 xlsx（6 Sheet）
        ├── 对手产品xlsx/           #   对手商品独立 xlsx（6 Sheet）
        ├── 生成图片/               #   AI 生成套图 + image_prompts.json + image_batch.json + image_validation.json
        ├── 采集数据/               #   product_*.json（爬虫原始数据）+ ebay_images/（参考图）
        ├── {SKU}.xlsx              #   汇总表（产品概览/竞品对比/图片索引/市场情报）
        ├── listing_output.docx     #   标题+卖点 Word 文档
        ├── listing_output.json     #   标题+卖点 JSON
        ├── listing_output.md       #   标题+卖点 Markdown
        ├── market_intel.json       #   市场情报（含竞品分析）
        ├── source_links.json       #   锚点+对手链接清单
        └── ref_ebay.webp           #   参考图（从 eBay 自动下载）
```

---

## 2. 环境搭建

### 2.1 前置软件

| 软件 | 版本要求 | 安装方式 |
|------|---------|---------|
| Node.js | ≥18.x | `winget install OpenJS.NodeJS.LTS` |
| Python | ≥3.12 | `winget install Python.Python.3.12` |
| Git | 最新 | `winget install Git.Git` |
| Clash Verge Rev | 最新 | GitHub Release |

### 2.2 Claude Code 安装

```bash
npm install -g @anthropic-ai/claude-code
```

### 2.3 创建工作区

```bash
mkdir "c:\Users\Hardy\ai-projects\agent升级计划"
cd "c:\Users\Hardy\ai-projects\agent升级计划"
```

在 Claude Code 中注册工作区（通过 VSCode 扩展或 CLI）。

### 2.4 权限配置（关键）

#### 全局配置 `~/.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)",
      "Skill(*)", "WebFetch(*)", "WebSearch(*)", "Agent(*)",
      "Bash(git *)", "Bash(ls *)", "Bash(cd *)", "Bash(mkdir *)",
      "Bash(rm *)", "Bash(cp *)", "Bash(mv *)", "Bash(cat *)",
      "Bash(curl *)", "Bash(wget *)", "Bash(python *)", "Bash(python3 *)",
      "Bash(pip *)", "Bash(npm *)", "Bash(npx *)", "Bash(node *)",
      "Bash(find *)", "Bash(netstat *)", "Bash(tasklist *)",
      "Bash(powershell *)"
    ]
  }
}
```

#### 项目级配置 `{工作区}/.claude/settings.json`

**关键陷阱：项目级 `permissions.allow` 会完全覆盖全局，不是合并！**

因此项目级配置必须**完整复制全局 allow 列表**，并添加 MCP 工具白名单：

```json
{
  "model": "deepseek-v4-pro",
  "permissions": {
    "allow": [
      "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)",
      "Skill(*)", "WebFetch(*)", "WebSearch(*)", "Agent(*)",
      "Bash(git *)", "Bash(ls *)", "Bash(cd *)", "Bash(mkdir *)",
      "Bash(rm *)", "Bash(cp *)", "Bash(mv *)", "Bash(cat *)",
      "Bash(curl *)", "Bash(wget *)", "Bash(python *)", "Bash(python3 *)",
      "Bash(pip *)", "Bash(npm *)", "Bash(npx *)", "Bash(node *)",
      "Bash(find *)", "Bash(netstat *)", "Bash(tasklist *)",
      "Bash(powershell *)",
      "mcp__image-vision__*",
      "mcp__image-gen__*",
      "mcp__serena__*",
      "mcp__memory__*",
      "mcp__sequential-thinking__*",
      "mcp__context7__*",
      "mcp__markitdown__*",
      "mcp__chrome-devtools__*",
      "mcp__playwright__*",
      "mcp__github__*",
      "mcp__github-mcp__*"
    ]
  }
}
```

### 2.5 CLAUDE.md 创建

CLAUDE.md 是本工作流的核心配置文件，包含所有规则。详见本 SOP 第 12 节核心铁律速查。完整内容参考：
`c:\Users\Hardy\ai-projects\agent升级计划\CLAUDE.md`

---

## 3. AI 模型与 MCP 插件

### 3.1 模型清单

| 模型 | 用途 | API 平台 | 费用 |
|------|------|---------|------|
| deepseek-v4-pro | 文本推理/文案/聚类 | DeepSeek API | ~¥0.01/次 |
| GLM-4V-Plus | 图片理解/OCR | 智谱 bigmodel.cn | ¥5/百万tokens (~¥0.005/张) |
| GLM-4V-Flash | 图片理解（免费版） | 智谱 bigmodel.cn | 免费 |
| nano-banana-fast | 快速生图 1K | maiziAI | ¥0.06/张 |
| gpt-image-2 | 高质量生图 1K/2K/4K | maiziAI | ¥0.06~0.105/张 |
| gpt-image-2-official | 高端生图 1K/2K/4K | maiziAI | ¥0.053~11.43/张 |
| nano-banana-2 | 生图 1K/2K/4K | maiziAI | ¥0.12/张 |
| nano-banana-pro | 生图 1K/2K/4K | maiziAI | ¥0.18/张 |

### 3.2 MCP 插件注册 `.mcp.json`

```json
{
  "mcpServers": {
    "image-vision": {
      "transport": "stdio",
      "command": "node",
      "args": [
        "c:/Users/Hardy/ai-projects/agent升级计划/MCP/mcp-image-vision/index.js",
        "--api-key=你的智谱API-KEY",
        "--model=GLM-4V-Plus"
      ]
    },
    "image-gen": {
      "transport": "stdio",
      "command": "node",
      "args": [
        "c:/Users/Hardy/ai-projects/agent升级计划/MCP/mcp-image-gen/index.js",
        "--api-key=你的麦子AI-KEY"
      ]
    },
    "memory": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "markitdown": {
      "transport": "stdio",
      "command": "uvx",
      "args": ["markitdown-mcp@0.0.1a4"]
    },
    "playwright": {
      "transport": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "chrome-devtools": {
      "transport": "stdio",
      "command": "npx",
      "args": ["--registry", "https://registry.npmjs.org", "chrome-devtools-mcp@1.0.1"]
    },
    "serena": {
      "transport": "stdio",
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/oraios/serena",
        "serena", "start-mcp-server", "serena@latest",
        "--context", "claude-code"
      ]
    },
    "github": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@fre4x/github@latest"],
      "env": { "GITHUB_TOKEN": "你的GitHub Token" }
    }
  }
}
```

**注意：Windows 上 `.mcp.json` 的 `env` 字段不生效**，所有 API Key 必须通过 `--api-key=` 命令行参数传递。

### 3.3 图片生成 MCP 插件

位置：`MCP/mcp-image-gen/index.js`

核心参数：
- `prompt`：图片描述（中文或英文）
- `model`：模型名称（默认 `nano-banana-fast`）
- `size`：尺寸（`1:1`、`16:9`、`4:3`）
- `reference_image`：**必传**，参考图绝对路径（确保产品结构不变）
- `strength`：参考图控制强度 0-1（默认 0.5，越低越忠实参考图，越高越自由）

API 端点：`POST https://www.maizitech.cn/v1/images/generations`
轮询：`GET https://www.maizitech.cn/v1/tasks/{task_id}`（2s/次，最长 60s）

### 3.4 图片理解 MCP 插件

位置：`MCP/mcp-image-vision/index.js`

核心参数：
- `image_path`：图片绝对路径
- `prompt`：分析指令（OCR/描述/特征提取）
- `model`：默认 `GLM-4V-Plus`（可切换 `GLM-4V-Flash` 免费版）

### 3.5 其他 MCP 插件一览

| 插件 | 功能 | 费用 |
|---|---|---|
| `image-vision` | 图片理解（智谱 GLM-4V-Plus） | ¥5/百万tokens |
| `image-gen` | 图片生成（maiziAI 5模型） | ¥0.06~/次 |
| `github` | GitHub 操作（搜仓库/Issue/PR/代码） | 免费 |
| `memory` | 跨会话知识图谱 | 免费 |
| `sequential-thinking` | 复杂问题分步推理 | 免费 |
| `context7` | 最新技术文档查询 | 免费 |
| `serena` | 代码导航与分析 | 免费 |
| `chrome-devtools` | 浏览器自动化 | 免费 |
| `playwright` | 浏览器自动化 | 免费 |
| `markitdown` | 文档格式转换 | 免费 |

---

## 4. 任务路由（Task Router）

每个任务必须先归类，再分发给对应模型，禁止跳步。

```
Input → Task Classification → Data Collection → Structure Extraction
→ Validation → Reasoning → Verification → Output
```

| 类型 | 说明 | 模型 | 示例 |
|------|------|------|------|
| TYPE-A | 视觉任务 | 智谱 GLM-4V-Plus | OCR、产品识别、构图验证 |
| TYPE-B | 逻辑推理 | DeepSeek v4-pro | fitment、OE 分析、文案 |
| TYPE-C | 数据/代码 | DeepSeek + Python | CSV、计算、导出 |
| TYPE-D | 生图任务 | maiziAI | 主图、场景图（Prompt 由 DS 写） |

### 输出隔离铁律

1. **GLM 输出**：原文直出，不改写、不润色、不总结、不翻译
2. **maiziAI 输出**：只报成功/失败、路径、模型、费用，不评价内容
3. **DeepSeek 输出**：只处理文本/代码/数据，不插手图片
4. **禁止跨模型加工**：任一模型的输出不得作为另一模型的"参考"二次解释
5. **Tool Result 优先级最高**：与模型推理冲突时永远优先 Tool Result
6. **错误隔离**：某模型失败时直报错误原文，不用其他模型猜测补救

---

## 5. 网络环境搭建

### 5.1 代理架构：双 mihomo

```
┌──────────────────────────────────────────┐
│  Clash Verge Rev (GUI)                   │
│  代理端口: 7897    API: 无               │
│  用途: 日常上网                           │
│  策略: 手动选择节点，不做自动切换           │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  独立 mihomo（命令行）                    │
│  代理端口: 7898    API: 127.0.0.1:9098   │
│  用途: 爬虫专用                           │
│  策略: REST API 自动轮换 47 个节点         │
│  美国节点: 2x 权重优先                    │
└──────────────────────────────────────────┘
```

### 5.2 独立 mihomo 部署

**配置文件：** `VPN/mihomo_scraper.yaml`
（从 Clash Verge Rev 订阅 profile 导出，修改端口为 7898/9098）

**启动命令：**
```bash
"C:\Program Files\Clash Verge\verge-mihomo.exe" -f "c:\Users\Hardy\ai-projects\agent升级计划\VPN\mihomo_scraper.yaml"
```

**验证 API 可用：**
```bash
curl http://127.0.0.1:9098/proxies
```

### 5.3 节点自动轮换

**脚本：** `VPN/clash_rotator.py`

**API 端点：**
- 列出节点：`GET /proxies/{group_name}`
- 切换节点：`PUT /proxies/{group_name}` → `{"name": "节点名"}`（返回 204）

**使用方式：**
```python
from VPN.clash_rotator import rotate_node, get_current_node

# 查看当前节点
print(get_current_node())

# 随机切换（避开当前节点，US 节点 2x 权重）
new = rotate_node()
```

### 5.4 eBay 地域锁定验证

**已验证结论（2026-05-23）：** 非美国节点 + `shs=US` cookie，eBay 仍正确展示美国市场数据（实测 JP 节点 → US 价格、US 运费、US 地址）。

爬虫 `warmup_browser()` 已自动写入以下 cookie：
```javascript
document.cookie = 'shs=US;...';     // 收货国家 = US
document.cookie = 'shss=NC;...';    // 州 = North Carolina
document.cookie = 'shzip=27513;...'; // 邮编
```

**全部 46 个 Clash 节点均可用于爬虫**，不限于美国节点。

---

## 6. 爬虫系统

### 6.1 爬虫脚本

**文件：** `爬虫/product_intel.py`

**用法：**
```bash
# 批量抓取（传入 SKU 目录）
python 爬虫/product_intel.py "c:\Users\Hardy\ai-projects\产品卖点主图和信息生成\{SKU目录}"

# 带视觉分析
python 爬虫/product_intel.py "{mother_dir}" --vision
```

**核心能力：**
- Playwright + stealth 反检测 + 持久化浏览器 profile
- 完整 JS 提取（20+字段）：标题/价格/规格/兼容表/卖家/反馈/物流/支付/库存
- **Item Specifics "See all" 自动展开**：EXTRACT_JS 先检查并点击所有折叠按钮，再提取完整规格列表
- 通过 eBay finders API 分页获取完整兼容表（每商品 300-500 条车型记录）
- 输出：每个商品保存为 `采集数据/product_{item_id}.json`
- **产品分类提取**：`_extract_door_config()`（车门配置）、`_is_door_part()`（门件判断）、`_extract_position()`（方位，含2门简化规则）、`_classify_product()`（5维分类含 door_config）
- 竞品匹配：`_is_valid_competitor()` 检查5维（含 door_config），不同车门配置互为排除

### 6.2 反检测机制

| 组件 | 实现 |
|------|------|
| 浏览器 | Playwright persistent context + Chromium |
| User-Agent | 3 个随机轮换（Chrome 129/130/131） |
| 视口 | 3 个随机尺寸（1920×1080 / 1536×864 / 1440×900） |
| 人类行为 | 随机滚动 + 鼠标移动（随机间隔 0.5-1.5s） |
| Stealth | `playwright_stealth` 库（如已安装） |
| Profile | `browser_profile/` 持久化（保持登录态） |
| 预热 | 先访问 Google → 再访问 eBay 首页 → 设置 US cookies |

### 6.3 兼容表抓取（关键）

eBay 页面 HTML 只显示前 20 条兼容数据（第 1 页），**完整数据需通过 finders API 分页获取。**

**API 端点：**
```
POST https://www.ebay.com/g/api/finders
  ?module_groups=PART_FINDER
  &referrer=VIEWITEM
  &offset={offset}
  &module=COMPATIBILITY_TABLE
```

**Payload：**
```json
{
  "scopedContext": {
    "catalogDetails": {
      "itemId": "304052751324",
      "sellerName": "modify-parts",
      "categoryId": "33654",
      "marketplaceId": "EBAY-US"
    }
  }
}
```

**分页逻辑：**
- 每页 20 条
- `offset` 从 0 开始，递增 `len(rows)`
- 最大页数 25（即 500 条上限）
- 从 title 提取总数 `"377 vehicle(s)"` 判断是否还有下一页

**CategoryId 提取：** 从页面 JSON-LD BreadcrumbList 中提取：
```javascript
const m = itemUrl.match(/\/b\/[^/]+\/(\d+)/);
if (m) categoryId = m[1];
```

### 6.4 抓取数据结构

**输出文件：** `采集数据/product_{item_id}.json`

```json
{
  "item_id": "304052751324",
  "url": "https://www.ebay.com/itm/304052751324",
  "title": "Upper Lower Door Hinges LH+RH For Chevrolet Nova 68-79 ...",
  "price": "US $71.00",
  "condition": "New",
  "seller": "modify-parts",
  "sellerUrl": "https://www.ebay.com/str/modify-parts",
  "sellerFeedback": "99.5%",
  "sellerFeedbackPct": 99.5,
  "quantity": "More than 10 available",
  "sold": "161 sold",
  "imageCount": 24,
  "specs": { "Brand": "Unbranded", "Material": "Steel", ... },
  "compatibility": [
    { "Year": "1979", "Make": "Chevrolet", "Model": "Nova", ... },
    ...
  ],
  "shipping": { "cost": "Free", "service": "Standard", ... },
  "returns": "30 days",
  "payment": ["PayPal", "Credit Card"],
  "images": ["https://...jpg", ...],
  "scraped_at": "2026-05-23T09:58:36"
}
```

### 6.5 xlsx 导出

#### 独立商品 xlsx（batch_xlsx.py）

```bash
python 爬虫/batch_xlsx.py "{mother_dir}"
```

为每个 `product_*.json` 生成独立 xlsx，6 个 Sheet：
1. **Product Info** — 标题/价格/状态/数量/eBay ID/URL
2. **Item Specifics** — 完整规格参数
3. **Compatibility** — 完整适配表（300-500行）
4. **Shipping & Returns** — 物流/退换货
5. **Seller Info** — 店铺名/链接/评分/库存/已售
6. **Images** — 所有图片 URL

锚定商品输出到 `锚定产品xlsx/`，对手商品输出到 `对手产品xlsx/`。

#### SKU 汇总 xlsx（summary_xlsx.py）

```bash
python 爬虫/summary_xlsx.py "{mother_dir}" "{SKU}"
```

生成 `{SKU}.xlsx`，6 个 Sheet：
1. **产品概览** — 锚定商品基本信息
2. **Valid竞品** — 通过 Rule 0 的有效竞品（绿底），含 Position/Finish/Structure/Sub-Type/Vehicle 完整字段
3. **Excluded竞品** — 未通过 Rule 0 的排除竞品（黄底），含 Exclude Reason 排除原因列
4. **锚定产品** — 锚定链接详情（蓝底），独立展示不混排
5. **图片索引** — 所有生成图片路径 + 验证结果
6. **市场情报** — 年份扩展告警（含URL）+ 卖家对比 + 适配覆盖统计

---

### 6.6 竞品自动发现流水线（Phase 0.5 NEW）

**目的**：仅凭一条锚点链接，自动搜索→过滤→评分→输出竞品列表，不再需要手动收集对手链接。

**9 阶段流水线**：

```
Stage 0: Anchor Canonicalization — classify_product()
Stage 1: Query Generation — build_queries() → eBay 搜索词
Stage 2: eBay Search — search_ebay() → 60 candidates (title only)
Stage 3: Light Ranking — rank_candidates() → title 级打分排序
Stage 4: Detail Scraping — scrape_batch() → 抓取 top 20-25 详情
Stage 5: Canonical Resolution — classify_product() → 候选规范化
Stage 6: Hard/Soft Filter — filter_candidate() → approve/reject/borderline
Stage 7: Similarity Scoring — compute_similarity() → 加权评分
Stage 8: Output → approved / borderline / rejected
Stage 9: DB Persistence → market.db 入库（7 表：own_products/competitor_listings/relationships/price_snapshots/crawl_jobs/canonical_snapshots/ruleset_version）
```

**核心模块**：

| 文件 | 核心函数 | 职责 |
|------|----------|------|
| `crawler/competitor_search.py` | `build_queries()`, `search_ebay()`, `discover_candidates()` | Stage 1-2：查询构建 + eBay 搜索 |
| `crawler/light_ranker.py` | `rank_candidates()` | Stage 3：vehicle family +30 / product_type +25 / cab hint +15 / position hint +10 / SEO spam -10 |
| `crawler/competitor_filter.py` | `filter_candidate()`, `extract_oe_numbers()`, `oe_fast_pass()` | Stage 6：OE Fast Pass + hard rules（mismatch→reject, absent→skip）+ soft rules |
| `crawler/similarity_engine.py` | `compute_similarity()`, `classify_result()`, `score_candidates()` | Stage 7：8 字段加权评分 + 品类差异化阈值 |
| `crawler/database.py` | `MarketDB` — 7 表 CRUD + `ingest_analysis()` 整次入库 | Stage 9：SQLite 持久化（WAL + FK） |

**三个 P0 设计要点**：

1. **OE Fast Pass**：candidate 和 anchor 的 OE/Interchange 号有交集 → 直接 Approved（similarity=1.0），跳过所有后续规则
2. **mismatch vs absent**：candidate 明确写了不同的 cab → HARD REJECT；candidate 没提 cab → 不 reject，仅 soft penalty -2（未提及 ≠ 冲突）
3. **复合 key 缓存**：SQLite 用 `(item_id, anchor_family, product_type, cab)` 复合主键，同一 listing 对不同车型/品类不污染

**用法**：

```python
from engine.canonicalize import classify_product
from crawler.competitor_search import discover_candidates
from crawler.light_ranker import rank_candidates
from crawler.competitor_filter import filter_candidate
from crawler.similarity_engine import score_candidates
from crawler.database import MarketDB
```

**配置文件**：

| 文件 | 用途 |
|------|------|
| `config/vehicle_ontology.json` | 9 大车型家族（GM Full-Size Truck, Ford F-Series 等） |
| `config/query_templates.json` | 按产品类型的 eBay 搜索模板（primary + fallback） |
| `config/category_thresholds.json` | 品类差异化 similarity 阈值（Door Handle: 0.80, Running Board: 0.72 等） |
| `config/filter_rules.json` | hard/soft rules 配置（含 OE Fast Pass 开关） |
| `config/similarity_weights.json` | 8 项相似度权重（总分 100） |

---

## 7. 图片理解（GLM-4V）

### 7.1 调用方式

通过 MCP 工具 `image-vision` 的 `analyze_image` 方法：

```python
# 参数
{
  "image_path": "C:/绝对路径/image.png",
  "prompt": "描述这张图片中的产品数量、颜色、材质、可见特征",
  "model": "GLM-4V-Plus"  # 可选，默认 GLM-4V-Plus
}
```

### 7.2 使用场景

| 场景 | Prompt 模板 |
|------|-----------|
| 产品特征提取 | "描述产品数量、颜色、材质、可见特征，不做推断" |
| 构图验证 | "描述构图：1)产品数量 2)是否悬浮 3)阴影是否合理 4)优缺点" |
| 竞品图片分析 | "描述图片中的场景风格、摆放方式、光影特点" |
| 生图校验 | "检查图片：1)产品数量是否匹配 2)是否有车标/Logo 3)产品是否浮空 4)结构是否变形" |

### 7.3 看图流程

1. Win+Shift+S 截图 → 剪贴板
2. 告诉 Claude "截好了"
3. Claude 运行 `视觉模块/clipboard3.ps1` 取图 → 调 `image-vision` → 返回 GLM 原文描述

### 7.4 铁律

- **只做**：OCR、目标识别、图片描述、特征识别
- **禁止**：fitment 判断、兼容性分析、OE 推断、平台车推断、Listing 优化、业务决策
- **输出**：原文直出，不改写

---

## 8. 图片生成（maiziAI）— V2 文案驱动

### 8.1 工作流顺序（V2 重要变更）

**先生成文案，再基于文案生图。** 图片 Prompt 由 DeepSeek 根据卖点文案动态生成，不再使用硬编码模板。

```
listing_output.json + market_intel.json
  → prompt_builder.py（DeepSeek 生成6张套图 Prompt）
    → image_prompts.json
      → batch_image_gen.py（maiziAI 批量生图）
        → image_validator.py（GLM-4V 视觉校验）
```

### 8.2 6 张套图类型

| Key | 标签 | 说明 |
|-----|------|------|
| `main` | 产品主图 | 完整产品展示，**不限于白底**。摄影棚布光或户外场景（野地/沙漠/车间），根据产品类型选择最佳场景。 |
| `fitment` | 产品适配图 | 信息图风格，展示适配车型（年份+品牌+车型），干净的高端目录规格页风格。 |
| `install` | 产品安装图 | 产品安装于汽车的效果展示，明确示意安装位置（箭头/柔光高亮）。中性色车身。 |
| `selling_points` | 产品卖点图 | 基于文案 bullets 的场景化卖点展示。防晒→阳光照射、防锈→水珠/耐候、纹理→表面特写。选取 1-2 个最视觉化的卖点。 |
| `detail` | 产品细节图 | 微距特写，展示表面纹理和颜色。浅景深。镀铬反光/哑光颗粒/纹理凹凸。 |
| `shipping` | 发货售后图 | 物流/售后优势展示。默认 Free Shipping / Fast Delivery / 30-Day Returns。仓库信息后续注入。 |

### 8.3 脚本用法

#### 第一步：生成 Prompt（DeepSeek）

```bash
python 生图/prompt_builder.py <mother_dir>
```

- 读取 `market_intel.json` + `listing_output.json` + `ref_ebay.webp`
- 调用 DeepSeek API（`deepseek-chat`）动态生成 6 张套图 Prompt
- 输出 `<mother_dir>/生成图片/image_prompts.json`
- 需要 DeepSeek API Key（已配置在脚本常量中）

#### 第二步：批量生图（maiziAI）

```bash
python 生图/batch_image_gen.py <mother_dir>                    # 默认 gpt-image-2
python 生图/batch_image_gen.py <mother_dir> --model quality    # gpt-image-2
python 生图/batch_image_gen.py <mother_dir> --model fast       # nano-banana-fast（仅1K）
```

- 自动查找 `<mother_dir>/生成图片/image_prompts.json`
- 也可通过 `--prompts-file` 指定自定义路径
- 启动前清理前次失败残留的孤儿 `gen_*.png`
- 自动下载 eBay 参考图（如果 `ref_ebay.webp` 不存在）
- 生成结果保存到 `<mother_dir>/生成图片/`，索引写入 `image_batch.json`

#### 第三步：视觉校验

```bash
python 视觉模块/verification/image_validator.py <image_path> [expected_count]
```

### 8.4 Prompt 生成原理

`prompt_builder.py` 将以下信息发送给 DeepSeek：
- 产品特征（类型/颜色/材质/件数/安装方位）
- 适配车型（年份+品牌+车型）
- 标题 + 6 条卖点文案
- eBay 参考图（通过 DeepSeek Vision 理解产品外观）

DeepSeek 根据 System Prompt 中的 6 种图类型约束，逐张生成 150-300 词的英文 Prompt。

**件数约束（CRITICAL）**：System Prompt 和 User Message 双重强调产品件数，每个 Prompt 必须精确匹配件数（1=a single, 2=a pair, 4=a set of 4）。

### 8.5 调用方式（底层）

#### MCP 工具（单张）

通过 MCP 工具 `image-gen` 的 `generate_image` 方法：

```python
{
  "prompt": "4 black steel door hinges resting flat on a weathered wooden workbench...",
  "model": "gpt-image-2",
  "size": "1:1",
  "reference_image": "C:/绝对路径/reference.webp",  # 必传参考图
  "strength": 0.6
}
```

#### Python 脚本（推荐）

**单张：** `生图/image_gen.py`
```python
from image_gen import generate

result = generate(
    prompt="...",
    model="gpt-image-2",   # 默认，5级降级链自动回退
    size="1:1",
    reference_image="C:/path/to/ref.webp",
    strength=0.5,
    output_dir="C:/path/to/output"
)
# 返回: {path, model_used, size_used, fallback_level}
```

**5 级降级链：** gpt-image-2 → nano-banana-2 → nano-banana-pro → gpt-image-2-official → nano-banana-fast

### 8.6 可用模型

| 模型 | 分辨率 | 价格 |
|------|--------|------|
| nano-banana-fast | 1K | ¥0.06/次 |
| gpt-image-2 | 1K/2K/4K | ¥0.06~0.105/次 |
| gpt-image-2-official | 1K/2K/4K | ¥0.053~11.43/次 |
| nano-banana-2 | 1K/2K/4K | ¥0.12/次 |
| nano-banana-pro | 1K/2K/4K | ¥0.18/次 |

尺寸：1:1, 16:9, 4:3

### 8.7 生图铁律（IMAGE-001 ~ IMAGE-006）

| 编号 | 规则 | 说明 |
|------|------|------|
| IMAGE-001 | 必须有参考图 | 禁止纯 Prompt 生图，无参考图直接拒绝 |
| IMAGE-002 | 禁止修改产品结构 | 禁止新增/修改部件、修改 OE 结构 |
| IMAGE-003 | 优先局部修改 | 优先 inpainting，禁止整图重生成 |
| IMAGE-004 | 禁止车标/Logo | 不得出现 OEM 标志、商标、品牌文字（Ford/BMW/Toyota 等） |
| IMAGE-005 | 产品必须自然融合 | 禁止悬浮，Prompt 必须描述空间关系 + 光影 + 透视 |
| IMAGE-006 | 生图后必须校验 | 每张生成后跑 `image_validator.py`，不通过则重生成 |

### 8.8 Prompt 构图要求

生成 Prompt 必须包含：
1. **空间关系** — 产品如何与背景交互（`resting flat on` / `placed on` / `installed on`）
2. **光影一致性** — 光源方向、阴影投射（`natural window light from upper left casting soft shadows to the right`）
3. **透视匹配** — 参考图视角与生成场景一致

**好坏示例对比：**

```
❌ 差："4 door hinges in an outdoor garage background"
→ 结果：产品悬浮，无接触阴影

✅ 好："4 black steel door hinges resting flat on a weathered wooden workbench,
      natural window light from the left casting soft shadows to the right,
      visible contact shadows grounding each hinge on the wood surface,
      shallow depth of field, professional product photography, 4K, photorealistic"
→ 结果：产品自然摆放，有正确阴影和透视
```

### 8.9 strength 参数指南

| strength | 效果 | 适用场景 |
|----------|------|---------|
| 0.3-0.5 | 高度忠实参考图 | 产品形态要求严格 |
| 0.5-0.7 | 平衡 | 场景合成主图（推荐） |
| 0.7-0.9 | 更自由 | 风格化/艺术化 |

### 8.10 生成结果格式

```
==================================================
[降级 0] gpt-image-2 4K ¥0.06~0.105 — 主力
==================================================
  task_id=xxx model=gpt-image-2 size=4k
  [1] status=processing
  ...
  [24] status=completed
  费用: ¥0.06  saved: C:\...\gen_quality_xxx.png
  模型: quality | 降级级: 0

...

索引文件: C:\...\生成图片\image_batch.json
完成: 6/6 张成功
```

### 8.11 输出文件

| 文件 | 说明 |
|------|------|
| `生成图片/image_prompts.json` | DeepSeek 生成的 6 张套图 Prompt |
| `生成图片/gen_quality_*.png` | 生成的图片（6张） |
| `生成图片/image_batch.json` | 生图结果索引 `{key: {label, path, status}}` |
| `生成图片/image_validation.json` | GLM-4V 校验结果 |

---


## 9. 文案生成与导出

> **V2 工作流变更：文案在生图之前生成。** 先生成 `listing_output.json`，再作为 `prompt_builder.py` 的输入驱动生图 Prompt 构建。

### 9.1 eBay 标题规则

- **≤ 80 字符（含空格）**
- 禁止 OEM Logo、品牌词、商标、®/™ 符号
- 格式：`[产品名称] [适配车型] [关键卖点]`

**80 字符满示例：**
```
Set Of Door Hinges 4pcs Upper Lower For 1968-1979 Chevy Nova / Camaro / Firebird
```

### 9.2 详情页文案规则

- **≥ 5 个卖点**（Bullet Points）
- 每点格式：`**加粗关键词** — 详细描述`
- 全英文
- 基于爬虫数据 + 竞品分析提取卖点

**示例结构：**
```
**HEAVY-DUTY SPRING MECHANISM** - ...
**RUST-PROOF ELECTROPHORETIC COATING** - ...
**COMPLETE 4-PIECE KIT** - ...
**PRECISION FITMENT** - ...
**EASY BOLT-ON INSTALLATION** - ...
```

### 9.3 文件导出

#### Markdown → Word（.docx）

```bash
python md2docx.py listing_output.md listing_output.docx
```

脚本：`agent升级计划/md2docx.py`
- 处理 H1/H2 标题、表格、加粗列表、代码块、普通列表
- 输出 Calibri 11pt + 蓝色表头 + 边框样式

#### 爬虫 JSON → 独立 xlsx

```bash
python 爬虫/batch_xlsx.py "{mother_dir}"
```

为每个商品生成独立 6-Sheet xlsx，锚定/对手分文件夹存放。

#### SKU 汇总 xlsx

```bash
python 爬虫/summary_xlsx.py "{mother_dir}" "{SKU}"
```

生成 4-Sheet 汇总表，包含竞品对比和市场情报。

---

## 10. 产品归档结构

### 10.1 目录命名规则（RULE-006）

**五个维度任一不同 = 不同 SKU，不可混在同一目录：**

| 维度 | 示例 | 区分项 |
|------|------|--------|
| 方位 | Front / Rear / Driver Side / Passenger Side | 前玻璃 ≠ 后玻璃 |
| 件数 | 1pc / 2pcs / 4pcs | 单只把手 ≠ 4件套 |
| 表面处理 | Chrome / Gloss Black / Matte Black / Textured | 镀铬 ≠ 亮黑 |
| 子类型 | Replacement / Cover / Trim / Shell | 替换件 ≠ 覆盖件 |
| 车门配置 | 2-door / 4-door-half / 4-door-full | 2门车窗 ≠ 4门全尺寸车窗 |

目录命名格式：`{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}`

示例：`Ford-F-150_2015-2022_Rear-Driver-Side_Dark_Door-Window-Glass`

缺失维度填 `Unknown`。

#### 方位提取规则（门件 vs 车体件）

**核心原则**：Front/Rear 对车门件和车体件含义完全不同。

| 产品类型 | Front 含义 | Rear 含义 | 2门简化规则 |
|----------|-----------|-----------|------------|
| **车门件**（车窗/把手/铰链/锁/门板/门镜） | 前车门 | 后车门 | ✅ 适用：2门车无后门，去掉 Front/Rear |
| **车体件**（保险杠/中网/翼子板/大灯/尾灯/机盖/尾门） | 车头 | 车尾 | ❌ 不适用：车头尾始终有意义 |

**皮卡车厢类型速查表**：

| 车门配置 | 值 | 典型车型 |
|----------|-----|---------|
| 2门 | `2-door` | Regular Cab / Single Cab / Standard Cab |
| 4门半尺寸 | `4-door-half` | Extended Cab / SuperCab / Double Cab / Quad Cab / Access Cab / King Cab |
| 4门全尺寸 | `4-door-full` | Crew Cab / SuperCrew / CrewMax / Mega Cab / Sedan |

**注意**：Coupe = 2-door，Sedan = 4-door-full。不同车门配置的同一位置产品互为不同SKU。

### 10.2 归档文件清单

```
{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}/
├── 锚定产品xlsx/               #   锚定商品独立 xlsx（6 Sheet，batch_xlsx.py 生成）
│   ├── product_304052751324.xlsx
│   └── ...
├── 对手产品xlsx/               #   对手商品独立 xlsx（6 Sheet，batch_xlsx.py 生成）
│   ├── product_296638207755.xlsx
│   └── ...
├── 生成图片/                   #   AI 生成套图（V2 六类）
│   ├── gen_main_*.png          #     产品主图（白底或场景）
│   ├── gen_fitment_*.png       #     产品适配图（年份+车型信息图）
│   ├── gen_install_*.png       #     产品安装图（安装位置示意）
│   ├── gen_selling_points_*.png#     产品卖点图（场景化卖点展示）
│   ├── gen_detail_*.png        #     产品细节图（微距特写）
│   ├── gen_shipping_*.png      #     发货售后图（物流/售后优势）
│   ├── image_prompts.json      #     DeepSeek 生成的 6 张套图 Prompt
│   ├── image_batch.json        #     生成记录（路径/模型/费用/Prompt）
│   └── image_validation.json   #     GLM-4V 校验结果
├── 采集数据/                   #   爬虫原始数据
│   ├── product_{ID}.json       #     结构化 JSON（20+字段）
│   └── ebay_images/            #     eBay 参考图
├── {SKU}.xlsx                  #   汇总表（产品概览/竞品对比/图片索引/市场情报）
├── listing_output.md           #   标题+卖点 Markdown
├── listing_output.json         #   标题+卖点 JSON
├── listing_output.docx         #   标题+卖点 Word 文档
├── market_intel.json           #   市场情报（含竞品分析 Rule 0-5）
├── source_links.json           #   锚点+对手链接清单
└── ref_ebay.webp               #   参考图（从 eBay 自动下载）
```

### 10.3 eBay 产品 ID 提取

从 URL 提取：`https://www.ebay.com/itm/XXX/304052751324` → ID 为 `304052751324`

---

## 11. 批量化方案与成本

### 11.1 单件耗时分解

| 阶段 | 耗时 | 说明 |
|------|------|------|
| 爬虫 | ~35s | 浏览器预热一次，后续复用 |
| 图片理解（GLM-4V） | ~3s/张 | eBay 参考图特征提取 |
| DeepSeek 文案 | ~20s | 标题 + 6 个卖点 |
| DeepSeek Prompt 构建 | ~10s | prompt_builder.py 生成 6 张套图 Prompt |
| 生图（6张） | ~50s | gpt-image-2 4K，并行提交并行轮询 |
| GLM-4V 验图 | ~20s | 6 张逐张校验 |
| 导出 | ~5s | xlsx + docx |
| **合计** | **~2.3 分钟/件** | |

### 11.2 单件成本

| 项目 | 单价 | 单件用量 | 费用 |
|------|------|---------|------|
| DeepSeek 文案 | ~¥0.01/次 | 1 次 | ¥0.01 |
| DeepSeek Prompt 构建 | ~¥0.005/次 | 1 次 | ¥0.005 |
| 生图（gpt-image-2 4K） | ¥0.06/张 | 6 张 | ¥0.36 |
| GLM-4V 验图 | ~¥0.005/张 | 6 张 | ¥0.03 |
| **合计** | | | **~¥0.41** |

### 11.3 批量处理能力

| 参数 | 值 |
|------|-----|
| 单次抓取间隔 | 30-60s 随机 |
| 单 IP 日安全上限 | 200-300 条 |
| 全节点日处理能力 | 500-1000 条（分时段） |
| 推荐批次 | 50 条/批，每批间隔 1-2 小时 |

### 11.4 批量流程（V2）

```
for batch in batches:
    1. rotate_node()              # 切换代理节点
    2. 抓取 batch 内所有链接
    3. GLM-4V 分析所有产品参考图 → 产品特征描述
    4. DeepSeek 竞品分析 → market_intel.json
    5. DeepSeek 逐件写文案 → listing_output.json
    6. prompt_builder.py 逐件生成 Prompt → image_prompts.json
    7. batch_image_gen.py 并行生图（含 5 级降级）
    8. image_validator.py 逐张 GLM-4V 视觉校验
    9. batch_xlsx.py + summary_xlsx.py 导出
    10. md2docx.py 转换 Word
    11. 间隔 1-2 小时后下一批
```

### 11.5 去重与聚类策略

- **爬虫不去重**，同一产品多条链接 = 市场情报
- 抓取完成后，DeepSeek 按车型/品类/规格聚类
- 每组基于头部 listing 做竞品分析（价格/标题策略/卖点角度）

---

## 12. 核心铁律速查

### RULE-001：禁止猜测
禁止使用：应该是、大概率、可能、看起来像、好像、估计。
信息不足时标记 `UNKNOWN`，必须返回缺失字段清单，必须请求补充数据。

### RULE-002：所有推理基于证据
每个结论必须给出：`claim` / `evidence` / `confidence`（0-1）。

```json
{
  "claim": "结论内容",
  "evidence": ["证据1", "证据2"],
  "confidence": 0.85
}
```

无依据的结论一律禁止。

### RULE-003：视觉模型禁止业务推理
GLM-4V 只做 OCR/识别/描述/特征提取，不做业务决策。

### RULE-004：结构化输出
模块间禁止自然语言裸传，所有传递使用 JSON Schema。

### RULE-005：高风险结果二次验证
高风险：fitment、OE 号、年款、平台车、SKU 映射、自动修改文件。
至少通过 Tool 验证 / Rule 验证 / Schema 验证 其中之一。

### RULE-006：产品归类规则
五个维度任一不同 = 不同 SKU：方位 / 件数 / 表面处理 / 子类型 / 车门配置。
Front/Rear 含义：车门件=前/后车门，车体件=车头/车尾。2门简化仅适用于车门件。
目录命名：`{Make}-{Model}_{Year-Range}_{Position}_{Finish}_{Count}_{Product-Type}`

### Confidence Threshold

| 区间 | 级别 | 行为 |
|------|------|------|
| >= 0.90 | HIGH | 允许自动执行 |
| 0.75 - 0.89 | MEDIUM | 标注后输出 |
| < 0.75 | LOW | **必须请求人工确认，禁止自动执行** |

### 生图铁律 IMAGE-001 ~ IMAGE-006
见第 8.3 节。

### 标题铁律
- ≤ 80 字符（含空格）
- 禁止 OEM Logo、品牌词、商标
- 全英文

### 输出隔离
- 任一模型的输出不得作为另一模型的"参考"二次解释
- Tool Result 优先级最高
- 错误直报原文，不猜测补救

### 上下文管理
- 禁止全历史注入、禁止无限累积上下文
- 每一步保存状态（step/status/result），后续只读状态结果
- 禁止"之前好像识别过..."这类自然语言记忆，必须用结构化引用

### 错误恢复
- 同一错误最多重试 **2 次**
- 失败必须输出：error_type、reason、recoverable
- 禁止伪造成功结果

---

## 13. 故障排查

### 13.1 爬虫被 eBay 拦截

**症状：** 页面返回 "Access Denied" 或 382 bytes 短响应

**排查：**
1. 检查 Clash 代理是否在线：`curl -x http://127.0.0.1:7898 http://ip-api.com/json`
2. 检查独立 mihomo 是否运行：`netstat -ano | grep 7898`
3. 切换节点：`python VPN/clash_rotator.py`
4. 清理 browser_profile 中的 cookies：删除 `browser_profile/Default/Cookies`
5. 检查 `headless` 是否为 `False`（headless 必被拦）

### 13.2 maiziAI 生图失败

**常见错误：**
- `Invalid API key format`：检查 API key 格式，应为 `sk-mz-...`
- 任务超时（60s）：图片复杂度高，重试即可
- 图片 URL 404：返回的 URL 需拼接 `https://www.maizitech.cn` 前缀

### 13.3 GLM-4V 返回乱码 / 连接失败

**原因：** Windows GBK 编码问题，或图片过大导致连接中断

**修复：**
1. 发送前将图片压缩为 JPEG 1024px
2. 在 mcp-image-vision/index.js 中使用 `utf-8` 编码读取响应

### 13.4 Python GBK 编码崩溃

**症状：** `UnicodeEncodeError` 在打印 `¥` 或中文时崩溃

**修复：** 所有含 `¥` 或中文的 Python 脚本顶部须加：
```python
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```

已修复的脚本：`生图/image_gen.py`、`生图/batch_image_gen.py`

### 13.5 孤儿图片残留

**症状：** 前次生图失败后，`生成图片/` 目录残留 `gen_*.png` 文件

**修复：** `batch_image_gen.py` 启动前自动清理孤儿文件。手动清理：
```bash
del "生成图片\gen_*.png"
```

### 13.6 独立 mihomo 端口冲突

**症状：** `bind: address already in use`

**修复：** 修改 `VPN/mihomo_scraper.yaml` 中的 `port` 和 `external-controller` 端口。

### 13.7 Claude Code 权限弹窗

**症状：** 每次执行命令都需要审批

**排查：**
1. 检查 `.claude/settings.json` 的 `permissions.allow` 是否完整
2. 检查项目级 settings 是否覆盖了全局（项目级会完全替换，不合并）
3. 新版本的 Claude Code 可能需要重新检查 settings.json 格式

### 13.8 xlsx 文件锁定

**症状：** `PermissionError` 写入 xlsx 时拒绝访问

**修复：** 关闭 Excel 中打开的 xlsx 文件后重新运行。

---

## 14. 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v2.5 | 2026-05-28 | 不确定性工程三项改进：(1) 字段覆盖率降权 — similarity_engine.py 新增 _compute_field_coverage()；(2) Universal Fit 识别 — competitor_filter.py 新增 universal_detect()；(3) 来源特异性 — resolver.py 新增 specificity override + config/specificity_scores.json；(4) Description Source Integration — product_intel.py 抓取 JS 新增 description_text 提取（#desc_ifr iframe 纯文本，cap 5000 字符），competitor_filter.py 新增 product_semantics 硬规则（cover/overlay vs replacement 互斥 reject），config/filter_rules.json 新增 cover/replacement 高危词列表 |
| v2.4 | 2026-05-27 | Parser 覆盖率提升：5 个 parser（finish/position/structure/count/material）扩增模式 + canonical_maps.json 新增 50+ 映射条目；finish 新增 Black-Chrome/Smoke-Chrome/Satin/Anodized/Powder-Coated + Chrome 滞后匹配防误杀；position 新增 Inner/Outer/Upper/Lower + Front-Rear/Both-Sides 多位置套件 + Exterior 防误判；structure 新增 N-piece 检测 + assemble 误判修复；material 新增 Zinc Alloy/Nylon/PP/PU/TPE/Polycarbonate；summary_xlsx.py 竞品对比 sheet 拆分为 Valid竞品(绿)/Excluded竞品(黄+原因)/锚定产品(蓝) 三 sheet；product_intel.py --max 默认值 8→50 |
| v2.3 | 2026-05-27 | Phase 0.5 + Phase 1 全面上线：新增 crawler/（5模块9阶段竞品自动发现）+ engine/（多源融合规范化）+ parser/（10字段解析器）+ 10个 config/ JSON 配置文件；OE Fast Pass / mismatch vs absent / 复合 key 缓存三项 P0；SOP 同步修正：目录树补全、V1→V2 图片命名、死链修复、import 路径修正；CLAUDE.md 版本规划重写为 V1/V2/V2.5/V3 里程碑体系 |
| v2.2 | 2026-05-26 | 产品归类升级：RULE-006 新增第5维 door_config（车门配置）；新增方位提取规则（门件 vs 车体件区分）；新增皮卡车厢类型速查表（2-door / 4-door-half / 4-door-full）；product_intel.py 新增 _extract_door_config / _is_door_part / 重写 _extract_position；_is_valid_competitor 增加 door_config 排除检查；Item Specifics "See all" 自动展开逻辑 |
| v2.0 | 2026-05-23 | 重大更新：整合 CLAUDE.md 内容；更新目录结构为分类子目录（MCP/视觉模块/VPN/生图/爬虫/SOP文档）；替换 ebay_scraper.py → product_intel.py；新增 batch_xlsx.py 6-Sheet + summary_xlsx.py 4-Sheet；新增 RULE-006 产品归类规则；新增生图5级降级链；新增孤儿图自动清理；新增 GLM-4V 视觉校验流程；新增 GBK 编码修复模板；更新所有路径引用；更新产品归档结构为 SKU 命名目录 |
| v1.0 | 2026-05-23 | 初始版本：完整全链路 SOP（环境 → MCP → 爬虫 → 生图 → 文案 → 导出） |

---

> **维护说明：** 本文档随工作流迭代更新。每次新增功能、修复关键 Bug、调整配置后，请在版本记录中添加条目。
>
> **关联文档：**
> - 核心规则：`../CLAUDE.md`
> - 产品归类规则：参照 CLAUDE.md 中的 RULE-006 及方位提取规则
> - MCP 配置：`../.mcp.json`
