# eBay Aftermarket 汽配 Agent 开发总规划（运营风控版）

## 项目定位

当前系统已经具备：

- Playwright 批量爬虫
- eBay 搜索
- compatibility API
- DeepSeek 文案生成
- GLM 视觉分类
- xlsx 导出
- Clash 代理轮换

当前目标：

从“竞品爬虫工具”升级为“汽配运营风控 Agent”。

核心方向：

- fitment 风控
- 市场共识
- compatibility 分析
- aftermarket 规则系统
- listing 风险识别
- 自家产品知识库

---

# 当前最大问题

1. 字段不统一（CrewCab / crew cab / Crew-Cab）
2. AI 幻觉（DS自由提词、GLM误判）
3. 缺少字段优先级系统
4. 缺少 confidence system
5. 缺少市场共识系统

---

# 最终架构

eBay URL
↓
Playwright
↓
Compatibility API
↓
HTML Parser
↓
Canonical Layer
↓
Field Priority
↓
Confidence Engine
↓
Market Consensus
↓
Risk Rules
↓
DeepSeek
↓
xlsx / Listing 输出

---

# 推荐目录结构

project/
├── crawler/
├── parser/
├── engine/
├── ai/
├── database/
├── export/
├── config/
└── tests/

---

# PHASE 1：标准化字段层

新增：

canonical_fields.py

目标：

统一：

- vehicle
- cab
- finish
- position
- count
- bed_length

例如：

- crewcab → Crew Cab
- LH → Front Left
- pair → 2PCS

输出：

{
  "canonical_vehicle":"",
  "canonical_cab":"",
  "canonical_finish":"",
  "canonical_position":"",
  "canonical_count":""
}

禁止：

- AI自由命名字段
- 同义字段混乱

---

# PHASE 2：字段优先级系统

新增：

field_priority.py

核心：

compatibility > specifics > title > image > AI inference

示例：

FIELD_PRIORITY = {
  "cab":[
    "compatibility_api",
    "specifics",
    "title",
    "image"
  ]
}

作用：

- 多来源交叉验证
- 自动选择高可信来源
- 降低视觉误判

---

# PHASE 3：Confidence Engine

新增：

confidence_engine.py

输出：

{
  "value":"Crew Cab",
  "confidence":0.91,
  "source":"compatibility_api"
}

评分逻辑：

- 多来源一致：0.95
- compatibility冲突：0.60
- 仅视觉识别：0.35
- AI推断：0.25

禁止系统“假装确定”。

---

# PHASE 4：市场共识系统

新增：

market_consensus.py

利用50个竞品形成市场统计共识。

例如：

- Crew Cab：46
- Extended Cab：4

输出：

{
  "market_consensus":"Crew Cab",
  "risk":"Extended Cab low consensus"
}

统计学通常比 AI 推断更可靠。

---

# PHASE 5：风险规则系统

新增：

risk_rules.py

高风险规则：

- Crew mismatch
- Classic missing
- Dually conflict
- Fleetside mismatch
- DRW/SRW conflict

示例：

if title_cab != fitment_cab:
    risk += 30

输出：

{
  "risk_score":82,
  "reasons":[]
}

---

# PHASE 6：内部产品知识库

新增：

internal_products.db

推荐：

SQLite

数据来源：

- 自家 listing
- 自家 fitment
- 高不良产品
- 市场共识

结构：

{
  "sku":"",
  "vehicle":"",
  "cab":"",
  "finish":"",
  "position":"",
  "count":"",
  "fitment":[]
}

---

# PHASE 7：AI运营分析层

DeepSeek 只负责：

- 标题优化
- bullet生成
- 市场总结
- 风险解释

禁止：

- fitment判断
- OCR结构化
- compatibility分析
- 年份提取

这些优先使用 Python 规则。

---

# 视觉模块正确定位

EasyOCR：

- 参数图
- note
- 安装图

GLM：

- 特殊结构
- Universal产品
- HTML缺失信息

禁止整个系统依赖视觉。

---

# DS Token 节省策略

1. Python优先
2. 视觉只做兜底
3. 建立 cache/
4. canonical layer 前置

缓存：

- compatibility
- title parse
- image classification

---

# 推荐开发顺序（未来1~2个月）

Week 1：
canonical_fields.py

Week 2：
field_priority.py

Week 3：
confidence_engine.py

Week 4：
market_consensus.py

Week 5：
risk_rules.py

Week 6：
internal_products.db

Week 7：
DS Prompt Engineering

---

# Agent 正确协作方式

正确：

“单模块开发”

错误：

“帮我优化整个系统”

正确示例：

请帮我开发 canonical_fields.py

目标：
统一 vehicle/cab/finish 字段

要求：

- Python实现
- 支持扩展
- 添加测试
- 可维护

---

# 工程纪律

1. AI最后介入

规则
>
数据库
>
统计
>
最后AI

2. 模块独立

要求：

- 可测试
- 可替换
- 可维护

3. 禁止巨型 product_intel.py

必须拆模块。

4. 规则资产优先

真正值钱的是：

- Crew Cab 风险
- Classic 风险
- Dually 风险
- 市场适配规则

而不是 AI 文案生成。

---

# 最终目标

当前最终目标不是：

“AI自动运营”

而是：

“汽配运营风控 Agent”

核心能力：

- fitment风险识别
- 市场适配判断
- compatibility分析
- 市场共识
- listing风控
- confidence system
- aftermarket规则工程

---

# 长期高级方向

1. 市场趋势监控
2. 售后风险预测
3. 自动运营辅助

例如：

- 自动生成note
- 自动竞品对比
- 自动listing审核
- 自动风险提示

---

# 最终定位

你现在做的已经不是普通爬虫，而是：

Aftermarket 汽配知识工程系统
