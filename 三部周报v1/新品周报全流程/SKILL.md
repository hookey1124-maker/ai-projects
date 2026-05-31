---
name: 新品周报全流程
name_en: New Product Weekly Report Full Workflow
description: "完整的新品周报制作全流程SOP：数据源解析 → 列索引确认 → XLSX汇总生成（10Sheet） → JSON导出 → HTML可视化报告。包含所有核心统计规则、Sheet结构、代码模板、HTML风格规范、动画效果。适用4.30-5.6及后续所有周期。"
description_zh: "新品周报全流程：源数据 → XLSX汇总 → JSON导出 → HTML可视化（10Sheet + 9大板块 + 完整动画规范）"
version: 3.0.0
agent_created: true
created_at: 2026-05-13
updated_at: 2026-05-13
tags: [新品周报, eBay, 数据分析, XLSX, HTML可视化, Chart.js]
skills:
  - xlsx
  - html
workdir: "C:/Users/Administrator/Desktop/新品复盘/"
---

# 新品周报全流程 SOP v3.0

> **适用周期**：4.30-5.6 及后续所有周期  
> **工作目录**：`C:/Users/Administrator/Desktop/新品复盘/`  
> **版本**：v3.0 新增完整HTML样式与动画规范

---

## 一、整体流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     新品周报生成全流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [步骤1]            [步骤2]           [步骤3]          [步骤4]  │
│ ┌──────────┐      ┌──────────┐      ┌──────────┐     ┌──────────┐
│ │源数据Excel│ ───→ │ XLSX汇总 │ ────→ │ JSON导出 │ ──→ │HTML可视化│
│ │(.xlsx)   │      │ (10Sheet)│      │ (.json)  │     │ (.html)  │
│ └──────────┘      └──────────┘      └──────────┘     └──────────┘
│     ↓                  ↓                                ↓
│ 新品检查周源数据    新品周报数据_      sheets_506.json  新品周报_4.30-5.6_
│ 和PLP数据.xlsx     {周期}.xlsx                      可视化.html
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 输入输出文件对照

| 步骤 | 输入 | 输出 | 关键操作 |
|------|------|------|---------|
| 步骤1 | `新品检查周源数据和PLP数据.xlsx` | 确认列索引 | 打印表头找列位置 |
| 步骤2 | 源数据 + 列索引 | `新品周报数据_{周期}.xlsx` | 生成10个Sheet |
| 步骤3 | XLSX | `sheets_{缩写}.json` | 导出所有Sheet为JSON |
| 步骤4 | JSON | `新品周报_{周期}_可视化.html` | Chart.js可视化 |

---

## 二、数据源结构与提取方法

### 2.1 源文件清单

| 文件名 | 内容 | Sheet | 关键字段数 |
|--------|------|-------|-----------|
| `新品检查周源数据和PLP数据.xlsx` | SKU级主数据 | `四三数据累计` | 121列 |
| `新品检查周源数据和PLP数据.xlsx` | PLP广告数据 | `PLP明细` | 38列 |

### 2.2 新品数据提取汇总流程

#### Step 1: 读取原始数据

```python
import openpyxl
from datetime import date, datetime

# 读取源数据
wb = openpyxl.load_workbook('新品检查周源数据和PLP数据.xlsx', data_only=True)
ws_main = wb['四三数据累计']
ws_plp = wb['PLP明细']

# 提取所有行数据（跳过表头）
rows_raw = []
for row in ws_main.iter_rows(min_row=2, values_only=True):
    if row[0]:  # 销售编号非空
        rows_raw.append(list(row))
```

#### Step 2: 日期过滤

```python
def get_date(v):
    """将Excel日期转换为date对象"""
    if isinstance(v, datetime): return v.date()
    if isinstance(v, date): return v
    return None

def num(v, default=0):
    """安全转换为数字"""
    try: return float(v) if v else default
    except: return default

# 周期定义（每周期需更新）
cutoff_curr = date(2026, 5, 6)   # 本周期截止日期
cutoff_prev = date(2026, 4, 29)  # 上周期截止日期

# 过滤：只统计截止日期前上架的SKU
rows_curr = [r for r in rows_raw if get_date(r[C['list_date']]) <= cutoff_curr]
rows_prev = [r for r in rows_raw if get_date(r[C['list_date']]) <= cutoff_prev]
```

#### Step 3: 核心指标汇总

```python
# ===== 1. 基础统计 =====
total_sku = len(rows_curr)                    # 累计SKU数
new_listed = len([r for r in rows_curr         # 本周新上架
                  if get_date(r[C['list_date']]) > cutoff_prev])

# ===== 2. 有对手/无对手 =====
has_rival = [r for r in rows_curr if num(r[C['rival_curr']]) > 0]
no_rival = [r for r in rows_curr if num(r[C['rival_curr']]) == 0]

# ===== 3. 销量/销售额汇总 =====
total_sales = sum(num(r[C['sales_curr']]) for r in rows_curr)
total_rev = sum(num(r[C['rev_curr']]) for r in rows_curr)

# ===== 4. 出单情况统计 =====
def count_ord8(rows, col):
    """统计Y/N/未出单数量"""
    y = n = no = 0
    for r in rows:
        v = str(r[col] or '').strip()
        if v == 'Y':          y += 1
        elif v == 'N':        n += 1  # ⚠️ N是已出单！
        elif v == '未出单':   no += 1
    return y, n, no

# 有对手口径出单情况
y, n, no_order = count_ord8(has_rival, C['ord8_curr'])
order_rate = f"{round((y+n)/len(has_rival)*100, 1)}%" if has_rival else "0%"

# ===== 5. 分析及时率 =====
def count_timeliness(rows, freq7_col, nfreq7_col):
    timely = no_8d = no_7d = 0
    for r in rows:
        freq = str(r[freq7_col] or '').strip()
        nfreq = str(r[nfreq7_col] or '').strip()
        if nfreq == '异常':       no_8d += 1
        elif freq == '异常':      no_7d += 1
        else:                     timely += 1
    return timely, no_8d, no_7d

timely, no_8d, no_7d = count_timeliness(rows_curr, C['freq7_curr'], C['nfreq7_curr'])
timely_rate = f"{round(timely/len(rows_curr)*100, 1)}%"

# ===== 6. 低占比新品 =====
low_share = [r for r in rows_curr 
             if num(r[C['share_curr']]) < 0.75 
             and num(r[C['rival_curr']]) > 0]
```

### 2.3 多维度汇总（品线/分析人/拓展类型）

```python
def group_by(dimension_col):
    """按维度分组统计"""
    groups = {}
    for r in rows_curr:
        key = str(r[dimension_col] or '').strip() or '未知'
        if key not in groups:
            groups[key] = {'skus': [], 'sales': 0, 'rev': 0, 'has_rival': []}
        groups[key]['skus'].append(r)
        groups[key]['sales'] += num(r[C['sales_curr']])
        groups[key]['rev'] += num(r[C['rev_curr']])
        if num(r[C['rival_curr']]) > 0:
            groups[key]['has_rival'].append(r)
    return groups

# 品线维度
cat_groups = group_by(C['category'])

# 分析人维度
an_groups = group_by(C['analyst'])

# 拓展类型维度
ex_groups = group_by(C['expand_type'])
```

---

## 三、核心数据规则（最高优先级）

### 3.1 8日出单情况——最关键规则

> ⚠️ **这是最常被误解的规则，错误理解会导致整个报告数据全错！**

| 列值 | 正确含义 | 统计处理 |
|------|---------|---------|
| **Y** | 8日**内**出单——产品在上架8天**内**出单 | ✅ 计入"已出单" |
| **N** | 8日**外**出单——产品已出单，但出单时间距上架**超过8天** | ✅ 计入"已出单"（不是未出单！） |
| **未出单** | 真正未出单——从上架至今从未出单的新品 | ❌ 计入"未出单" |
| **未上架** | 当日尚未上架（是未来日期） | ❌ **不计入任何统计** |

**出单率计算**：
```
出单率 = (Y + N) / 有对手总SKU × 100%
```
分母是"有对手SKU"，不是全部SKU。有对手 = 对手销量 > 0。

### 3.2 分析及时率规则

| 指标 | 判断规则 |
|------|---------|
| 8日内新品无分析 | 7日**新品**频次标签 = "异常" |
| 超7日低占比未分析 | 7日**频次标签** = "异常" |
| 及时分析产品 | 以上两列都**不是**"异常" |

### 3.3 低占比新品定义

同时满足：**本期末市占比 < 0.75** 且 **有对手（对手销量 > 0）**

### 3.4 PLP统计过滤规则

**所有PLP维度统计**都必须排除：`实际上架日期 > 统计截止日期` 的SKU

---

## 四、XLSX汇总生成（10个Sheet）

### 4.1 Sheet结构总览

| # | Sheet名 | 核心内容 |
|---|---------|---------|
| 1 | 总体数据 | KPI汇总（SKU/销量/销售额/有对手/分析及时率/出单率） |
| 2 | 品线维度 | 各品线SKU/新上架/销量/销售额/有对手，含环比 |
| 3 | 分析人维度 | 各分析人SKU/新上架/销量/销售额/有对手 |
| 4 | 拓展类型 | 原开品/拓展品/组合件出单率/销量/销售额，含环比 |
| 5 | 分析及时率 | 各分析人及时率/8日内无分析/超7日未分析/及时率 |
| 6 | 低占比新品 | 所有低占比SKU完整明细，共25列 |
| 7 | 新品PLP | 总览+分析人/品线/拓展类型维度，含ACOAS |
| 8 | 新品出单情况 | 有对手口径出单情况（Y/N/未出单/出单率） |
| 9 | 新品未出单原因 | A/B双板块：原因分布/按分析人/按品线 |
| 10 | 新品PLG维度 | PLG维度明细表 |

### 4.2 Sheet 7 新品PLP（新增ACOAS列）

**列结构**：
| 列号 | 字段名 | 说明 |
|------|--------|------|
| 1-2 | 周期/活动数 | 本周期广告活动数量 |
| 3 | 链接数 | 有曝光的SKU数 |
| 4-7 | 曝光/点击/售出/花费 | 广告基础指标 |
| 8 | 销售额 | PLP带来的销售额 |
| 9-12 | ROAS/CVR/CTR/CTR | 效率指标 |
| 13 | CPC | 点击成本 |
| 14 | CPA | 单次成交成本 |
| 15 | ACOS% | 广告成本占PLP销售额比 |
| **16** | **ACOAS%** | **广告成本占全部销售额比（新增）** |
| 17+ | 上周数据 | 环比对比数据 |

**ACOAS计算公式**：
```
ACOAS = PLP广告花费合计 / 该SKU周期总销售额 × 100%
```
数据来源：广告花费从PLP明细，销售额从四三数据累计Sheet

---

## 五、JSON导出

```python
import openpyxl
import json

wb = openpyxl.load_workbook('新品周报数据_{周期}.xlsx', data_only=True)
out = {}
for name in wb.sheetnames:
    ws = wb[name]
    rows = []
    for row in ws.iter_rows(values_only=True):
        rows.append(list(row))
    out[name] = rows

with open('sheets_{缩写}.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, default=str)
```

---

## 六、HTML可视化报告规范

### 6.1 CSS样式规范

#### 全局样式
```css
/* 背景渐变 - 深色主题 */
body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #1a1a2e;
    font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}

/* 头部 */
.header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 28px 40px;
}
.header h1 { font-size: 26px; font-weight: 700; letter-spacing: 2px; }
.header .subtitle { font-size: 13px; opacity: 0.75; margin-top: 6px; }

/* 容器布局 */
.container { display: flex; min-height: calc(100vh - 80px); }

/* 侧边栏 - 白色背景，sticky定位 */
.sidebar {
    width: 230px;
    background: #fff;
    border-right: 1px solid #e8e8e8;
    padding: 20px 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    flex-shrink: 0;
}
.sidebar ul { list-style: none; }
.sidebar li a {
    display: block;
    padding: 10px 20px;
    font-size: 13px;
    color: #555;
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.2s;  /* 平滑过渡动画 */
}
.sidebar li a:hover,
.sidebar li a.active {
    background: #f0f6ff;
    color: #0f3460;
    border-left-color: #0f3460;
    font-weight: 600;
}
```

#### KPI卡片样式
```css
/* KPI网格 */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}

/* KPI卡片 - 白色背景 + 阴影 */
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;  /* 悬停动画 */
}
.kpi-card:hover {
    transform: translateY(-2px);  /* 轻微上浮 */
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.kpi-card .val { font-size: 26px; font-weight: 700; color: #0f3460; }
.kpi-card .label { font-size: 12px; color: #888; margin-top: 6px; }
.kpi-card .hb { font-size: 11px; margin-top: 4px; font-weight: 600; }

/* KPI卡片颜色变体 */
.kpi-card.green .val { color: #08845a; }   /* 绿色 - 正向指标 */
.kpi-card.orange .val { color: #e07b24; }  /* 橙色 - 警示指标 */
.kpi-card.red .val { color: #c0392b; }      /* 红色 - 负向指标 */
.kpi-card.purple .val { color: #8e44ad; }  /* 紫色 - 重点指标 */
```

#### 图表卡片样式
```css
/* 图表网格 */
.chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

/* 图表卡片 */
.chart-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.chart-card h4 {
    font-size: 13px;
    font-weight: 600;
    color: #0f3460;
    margin-bottom: 14px;
}
.chart-card canvas { max-height: 260px; }

/* 宽图表卡片 - 横跨整行 */
.chart-card-wide {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    grid-column: 1 / -1;
}
```

#### 表格样式
```css
/* 表格容器 */
.table-wrap { overflow-x: auto; }

/* 数据表格 */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.data-table th {
    background: #0f3460;
    color: white;
    padding: 8px 8px;
    text-align: center;
    white-space: nowrap;
    font-weight: 600;
}
/* 表头颜色分类 */
.data-table th.p1 { background: #6c757d; }
.data-table th.p2 { background: #667eea; }
.data-table th.p3 { background: #2980b9; }
.data-table th.p4 { background: #c0392b; }
.data-table th.hb { background: #e07b24; }

.data-table td {
    padding: 6px 8px;
    text-align: center;
    border-bottom: 1px solid #f0f0f0;
    white-space: nowrap;
}
.data-table tr:hover td { background: #f5f7ff; }  /* 行悬停高亮 */

/* 环比颜色 */
.hb-up { color: #c0392b; font-weight: 700; }
.hb-down { color: #08845a; font-weight: 700; }
.hb-flat { color: #888; }

/* 标签徽章 */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    color: white;
    font-weight: 600;
}
.badge-y { background: #08845a; }      /* Y-已出单 */
.badge-n { background: #e07b24; }      /* N-8日外 */
.badge-un { background: #c0392b; }     /* 未出单 */
.badge-normal { background: #2980b9; }  /* 正常 */
```

#### PLP卡片样式
```css
/* PLP指标网格 */
.plp-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}

/* PLP卡片 - 带顶部边框颜色 */
.plp-card {
    background: white;
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-top: 3px solid #8e44ad;  /* 紫色顶部边框 */
}
.plp-card[style*="c0392b"] { border-top-color: #c0392b; }  /* 红色变体 */
.plp-card[style*="2980b9"] { border-top-color: #2980b9; }  /* 蓝色变体 */

.plp-card h4 { font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 12px; }
.plp-metric {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 12px;
}
.plp-metric:last-child { border-bottom: none; }
.plp-metric .lbl { color: #666; }
.plp-metric .val { font-weight: 600; color: #1a1a2e; }

/* PLP高亮区块 */
.plp-highlight {
    background: #f5f0ff;
    border-radius: 6px;
    padding: 10px;
    margin-top: 10px;
}
.plp-highlight .val { color: #8e44ad; font-weight: 700; }
```

#### 响应式设计
```css
@media (max-width: 900px) {
    .sidebar { display: none; }
    .chart-grid { grid-template-columns: 1fr; }
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

/* 滚动条样式 */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
```

### 6.2 JavaScript交互规范

#### 导航切换函数
```javascript
// ===== 侧边栏导航 =====
function showSection(id, el) {
    // 隐藏所有板块
    document.querySelectorAll('.section-wrap').forEach(s => s.style.display = 'none');
    // 移除所有active样式
    document.querySelectorAll('.sidebar li a').forEach(a => a.classList.remove('active'));
    // 显示目标板块
    document.getElementById('section-' + id).style.display = 'block';
    // 添加active样式
    if(el) el.classList.add('active');
}
```

#### 数据处理函数
```javascript
// ===== 数据行过滤 =====
function data_rows(rows) {
    return rows.slice(1).filter(r => 
        r && r[0] && !['合计','总计','维度'].includes(String(r[0]).trim())
    );
}

// ===== 颜色常量 =====
const P_COLORS = [
    'rgba(102,126,234,0.8)',  // 紫色
    'rgba(41,128,185,0.8)',   // 蓝色
    'rgba(192,57,43,0.8)',    // 红色
    'rgba(142,68,173,0.8)',   // 深紫
    'rgba(224,123,36,0.8)',   // 橙色
    'rgba(8,132,90,0.8)'      // 绿色
];
const P_COLORS_BORDER = ['#667eea', '#2980b9', '#c0392b', '#8e44ad', '#e07b24', '#08845a'];
```

#### 图表创建模板
```javascript
// ===== 饼图模板 =====
function createPieChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 15, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = (context.raw / total * 100).toFixed(1);
                            return `${context.label}: ${context.raw} (${pct}%)`;
                        }
                    }
                }
            },
            // 动画配置
            animation: {
                animateRotate: true,      // 旋转动画
                animateScale: true,       // 缩放动画
                duration: 800,            // 动画时长(ms)
                easing: 'easeOutQuart'    // 缓动函数
            }
        }
    });
}

// ===== 柱状图模板 =====
function createBarChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: { beginAtZero: true, grid: { color: '#f0f0f0' } },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: { position: 'top', labels: { font: { size: 11 } } },
                tooltip: { mode: 'index', intersect: false }
            },
            // 动画配置
            animation: {
                y: { duration: 1000, easing: 'easeOutQuart' },
                x: { duration: 800, easing: 'easeOutQuart' }
            }
        }
    });
}
```

### 6.3 动画效果规范

#### 全局动画配置
```javascript
// Chart.js 全局动画配置
Chart.defaults.animation = {
    duration: 800,           // 默认动画时长 800ms
    easing: 'easeOutQuart',  // 缓动函数：快出慢入
    delay: 0,                // 延迟开始时间
    loop: false              // 是否循环
};

// 图表入场动画
const chartAnimation = {
    // 入场动画类型
    type: 'scale',           // 或 'rotate', 'slide', 'fade'
    // 动画时长
    duration: 1000,
    // 缓动函数
    easing: 'easeOutElastic(1, .5)',  // 弹性效果
    // 延迟（staggered animation）
    delay: function(context) {
        return context.dataIndex * 50 + context.datasetIndex * 100;
    }
};
```

#### 各类图表推荐动画

| 图表类型 | 推荐动画 | 配置 |
|---------|---------|------|
| 饼图/环形图 | 旋转+缩放入场 | `animateRotate: true, animateScale: true` |
| 柱状图 | 从下往上生长 | `animation.y: { duration: 800, from: 0 }` |
| 折线图 | 从左往右绘制 | `animation.x: { duration: 1000, easing: 'linear' }` |
| 堆叠柱状图 | 依次堆叠生长 | `animation.stagger: true, delay: 50` |

#### CSS过渡动画

```css
/* 卡片悬停效果 */
.card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

/* 侧边栏项切换 */
.sidebar-item {
    transition: all 0.2s ease;
}
.sidebar-item:hover {
    padding-left: 25px;  /* 左侧内边距增加 */
    background: #f0f6ff;
}

/* 表格行悬停 */
.table-row {
    transition: background-color 0.15s ease;
}
.table-row:hover {
    background-color: #f5f7ff;
}

/* KPI数值变化动画 */
.kpi-value {
    animation: countUp 1s ease-out forwards;
}
@keyframes countUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 渐入效果 */
.fade-in {
    animation: fadeIn 0.5s ease-out forwards;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* 滑入效果 */
.slide-in {
    animation: slideIn 0.4s ease-out forwards;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}
```

### 6.4 HTML结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新品周报 · {周期}</title>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        /* 完整CSS样式（见6.1节） */
    </style>
</head>
<body>

<!-- 头部 -->
<div class="header">
    <h1>📊 新品周报 · {周期}</h1>
    <div class="subtitle">
        统计周期：{开始日期} - {结束日期} |
        在跟SKU：{SKU数} |
        生成：{生成日期}
    </div>
</div>

<!-- 主体容器 -->
<div class="container">

    <!-- 侧边栏导航 -->
    <nav class="sidebar">
        <ul>
            <li><a href="#" onclick="showSection('overview',this)" class="active">📊 数据总览</a></li>
            <li><a href="#" onclick="showSection('pinxian',this)">🏷️ 品线维度</a></li>
            <li><a href="#" onclick="showSection('analyst',this)">👤 分析人维度</a></li>
            <li><a href="#" onclick="showSection('expand',this)">🔗 拓展类型</a></li>
            <li><a href="#" onclick="showSection('timely',this)">⏱️ 分析及时率</a></li>
            <li><a href="#" onclick="showSection('order',this)">📦 新品出单情况</a></li>
            <li><a href="#" onclick="showSection('unorder',this)">❌ 新品未出单</a></li>
            <li><a href="#" onclick="showSection('lowshare',this)">📉 低占比新品</a></li>
            <li><a href="#" onclick="showSection('plp',this)">💰 PLP复盘</a></li>
        </ul>
    </nav>

    <!-- 主内容区 -->
    <div class="main-content">

        <!-- KPI总览卡片 -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="val">{SKU总数}</div>
                <div class="label">在跟SKU总数</div>
                <div class="hb" style="color:#888">本周新上架 {新上架}</div>
            </div>
            <!-- 更多KPI卡片... -->
        </div>

        <!-- 板块1: 数据总览（默认显示） -->
        <div id="section-overview" class="section-wrap">
            <div class="section">
                <h3>📊 数据总览 · 图形可视化</h3>
                <div class="chart-grid">
                    <div class="chart-card">
                        <h4>📦 出单分布</h4>
                        <canvas id="chartOrderPie"></canvas>
                    </div>
                    <div class="chart-card">
                        <h4>❌ 未出单原因分布</h4>
                        <canvas id="chartUnorderPie"></canvas>
                    </div>
                    <div class="chart-card">
                        <h4>⏱️ 分析情况分布</h4>
                        <canvas id="chartTimelyPie"></canvas>
                    </div>
                    <div class="chart-card">
                        <h4>📉 低占比新品分布</h4>
                        <canvas id="chartLowShareCat"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- 更多板块（默认隐藏） -->
        <div id="section-pinxian" class="section-wrap" style="display:none">
            <!-- 品线维度内容 -->
        </div>

    </div><!-- end main-content -->
</div><!-- end container -->

<script>
// ===== JS数据 =====
const sheets = { /* JSON数据 */ };

// ===== 图表初始化 =====
function initCharts() {
    // 从sheets读取数据并创建图表
}

// ===== 启动 =====
document.addEventListener('DOMContentLoaded', initCharts);
</script>

</body>
</html>
```

---

## 七、报告板块结构（9个板块）

| # | 板块ID | 板块名 | 默认显示 | 核心图表 |
|---|--------|--------|---------|---------|
| 1 | overview | 数据总览 | ✅常驻 | 出单分布饼图/未出单原因柱图/分析情况饼图/低占比分布 |
| 2 | pinxian | 品线维度 | ❌隐藏 | 本周vs上周销量柱状图+占比饼图+明细表 |
| 3 | analyst | 分析人维度 | ❌隐藏 | 同上结构，6个分析人 |
| 4 | expand | 拓展类型 | ❌隐藏 | 出单率对比柱图+销量分布 |
| 5 | timely | 分析及时率 | ❌隐藏 | 汇总表+各分析人明细 |
| 6 | order | 新品出单情况 | ❌隐藏 | 出单分布图+出单率趋势 |
| 7 | unorder | 新品未出单 | ❌隐藏 | A/B双板块：原因分布图+明细 |
| 8 | lowshare | 低占比新品 | ❌隐藏 | 品类分布+出单状态分布+完整25列明细表 |
| 9 | plp | PLP复盘 | ❌隐藏 | 总览指标卡+分析人/品线维度+明细表 |

---

## 八、常量与名单

### 分析人名单（共6人）
俞东旭 / 张潇 / 朱培源 / 王偲涵 / 章鹏 / 胡煜星

### 品线名单（7类）
车门系统 / 车身外扩件 / 挡泥板 / 机盖及附件 / 牌照板支架 / 其他 / 饰条

### 拓展类型（3类）
原开品 / 拓展品 / 组合件

---

## 九、新周期生成步骤清单

```
┌─────────────────────────────────────────────────────────────┐
│                    新周期生成步骤                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1] 确认列索引                                              │
│      └─ 运行列索引打印脚本，确认当前周期各列位置              │
│                                                             │
│  [2] 创建XLSX生成脚本                                        │
│      ├─ 复制上期 gen_xlsx_XXXX.py                           │
│      ├─ 更新日期边界（cutoff_curr/cutoff_prev）              │
│      ├─ 更新列索引字典 C                                     │
│      ├─ 更新PLP period字符串                                 │
│      └─ 更新输出文件名                                       │
│                                                             │
│  [3] 运行XLSX生成脚本                                        │
│      └─ 检查10个Sheet数据正确性                              │
│                                                             │
│  [4] 导出JSON                                               │
│      └─ 将XLSX所有Sheet导出为sheets_{缩写}.json              │
│                                                             │
│  [5] 生成HTML可视化报告                                      │
│      ├─ 参考本skill第6节HTML规范                            │
│      ├─ 参考 4.30-5.6_可视化.html 样式                       │
│      └─ 按第7节板块结构组织内容                              │
│                                                             │
│  [6] 自我校验（必须逐项检查）                                │
│      ├─ ☐ 出单率：(Y+N)/有对手SKU×100%                     │
│      ├─ ☐ 分析及时率：用频次标签列而非iv列                    │
│      ├─ ☐ PLP过滤：排除截止日期后上架的SKU                   │
│      ├─ ☐ 低占比：share<0.75且rival>0                        │
│      ├─ ☐ 未出单拆分：有对手/无对手分开统计                   │
│      └─ ☐ 销售额：USD原值，无货币转换                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十、常见错误与排查

| # | 错误现象 | 根本原因 | 解决方案 |
|---|---------|---------|---------|
| 1 | N被统计为未出单 | 误解N含义 | N=8日外已出单，Y=8日内已出单，只有"未出单"才是真正未出单 |
| 2 | PLP均值明显偏低 | 未过滤未来上架SKU | 所有PLP统计都要 `if list_date > cutoff_date: continue` |
| 3 | 分析及时率数字异常 | 用了iv列而非频次标签列 | 及时率用7日频次标签+7日新品频次标签，不用iv |
| 4 | 品线上架产品数偏大 | 统计了历史累计而非周期内上架 | 上架产品数 = 该周期内上架的新SKU数 |
| 5 | 出单率偏低 | 分母用了全部SKU | 分母 = 有对手SKU（对手销量>0），不是全部SKU |
| 6 | openpyxl写入报错MergedCell | 直接对合并单元格赋值 | 先 `ws.unmerge_cells()` 取消合并再写入 |
| 7 | 低占比新品数量不一致 | 市占比阈值判断错误 | 严格用 < 0.75（非 <=），且要求有对手 |
| 8 | HTML图表显示空白 | JSON读取路径错误 | 确认Sheet名称与JSON中的key完全一致 |
| 9 | 列索引偏移 | 直接用上期索引 | 必须用脚本重新确认每列位置 |
| 10 | 销售额显示NaN | 数据类型问题 | 用 `num()` 函数处理：非数字返回默认值 |
| 11 | 未出单模块未拆分 | 用了旧版Sheet 9结构 | 更新为A/B双板块结构 |
| 12 | HTML样式不一致 | 参考了错误的模板 | 必须参考 4.30-5.6_可视化.html |

---

## 十一、参考文件

| 文件类型 | 文件名 | 用途 |
|---------|--------|------|
| 源数据 | `新品检查周源数据和PLP数据.xlsx` | 原始数据来源 |
| XLSX生成脚本 | `gen_xlsx_506_acoas.py` | 4.30-5.6周期（含ACOAS）参考 |
| HTML可视化参考 | `新品周报_4.30-5.6_可视化.html` | **必须参考此风格** |
| JSON中间层 | `sheets_506.json` | 当前周期JSON数据 |
| Skill本体 | 本文件 | 新品周报全流程SOP |

---

## 十二、最终交付物规范

### 12.1 XLSX文件
- 文件名：`新品周报数据_{周期}.xlsx`
- 包含10个Sheet，结构见第4节
- Sheet 7 新增ACOAS%列

### 12.2 JSON文件
- 文件名：`sheets_{周期缩写}.json`
- 包含所有Sheet的二维数组数据

### 12.3 HTML文件
- 文件名：`新品周报_{周期}_可视化.html`
- 单文件，自包含（CSS+HTML+JS）
- 包含Chart.js CDN引用
- 9个板块，侧边栏导航
- 紫色主题，白色卡片布局
- 图表动画：旋转/缩放/生长效果

### 12.4 验证清单
- [ ] XLSX 10个Sheet完整
- [ ] Sheet 7 包含ACOAS%列
- [ ] JSON 数据与XLSX一致
- [ ] HTML 9个板块可切换
- [ ] HTML 侧边栏导航正常
- [ ] HTML 图表正确渲染
- [ ] HTML 动画效果正常
- [ ] 响应式布局正常

---

*更新于 2026-05-13 v3.0*
