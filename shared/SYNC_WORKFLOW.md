# 新品复盘 ↔ 三部周报v1 同步工作流

> 每次新周期数据到来时，两个项目需要同步更新。本文档定义了标准操作流程。

## 架构

```
周报/新品检查周源数据和PLP数据.xlsx  ← 唯一数据源
         │
         ├─→ shared/extract_weekly_data.py  ← 共享提取器（本次新增）
         │       │
         │       ├─→ shared/output/latest.json     ← 标准化 JSON
         │       └─→ shared/output/weekly_data_X.X-X.X.json
         │
         ├─→ 新品复盘/gen_html_5_14_5_20.py  ← Python HTML 生成
         │       └─→ 新品板块_X.X-X.X.html
         │
         └─→ 三部周报v1/  ← React/TS 看板
                 ├─→ newProductStatus/weekly_data_X.X-X.X.json  ← 数据文件
                 └─→ newProductStatus/新品板块_X.X-X.X.html     ← 静态参考
```

## 新周期更新步骤

### Step 1: 更新 Excel 数据源
将新周期的 `新品检查周源数据和PLP数据.xlsx` 放到 `新品复盘/周报/`

### Step 2: 运行共享提取器
```bash
cd 新品复盘
.venv\Scripts\python.exe ..\shared\extract_weekly_data.py
```

### Step 3: 更新 新品复盘 HTML
```bash
# 复制 gen_html_5_14_5_20.py → gen_html_X.X-X.X.py
# 修改脚本中的列索引和周期标签
cd 新品复盘
.venv\Scripts\python.exe gen_html_X.X-X.X.py
```

### Step 4: 同步文件到 三部周报v1
```powershell
# 复制 HTML
Copy-Item 新品复盘/新品板块_X.X-X.X.html 三部周报v1/新品周报全流程/
Copy-Item 新品复盘/新品板块_X.X-X.X.html 三部周报v1/New project 2-新品板块已放入/src/modules/newProductStatus/

# 复制 JSON
Copy-Item shared/output/latest.json 三部周报v1/New project 2-新品板块已放入/src/modules/newProductStatus/weekly_data_X.X-X.X.json
```

### Step 5: 验证
```bash
# 验证 HTML（直接浏览器打开）
start 新品板块_X.X-X.X.html

# 验证 React 应用
cd 三部周报v1/New project 2-新品板块已放入
npm run dev
# 打开 http://localhost:5173/?demo=1
```

### Step 6: 提交
```bash
cd ai-projects
git add -A
git commit -m "sync: 更新到 X.X-X.X 周期（新品复盘 + 三部周报v1）"
git push origin master
```

## 文件对照表

| 新品复盘 | 三部周报v1 | 说明 |
|----------|-----------|------|
| `gen_html_X.X-X.X.py` | — | HTML 生成脚本（仅 Python 侧） |
| `新品板块_X.X-X.X.html` | `newProductStatus/新品板块_X.X-X.X.html` | 静态 HTML 副本 |
| `周报/新品检查周源数据和PLP数据.xlsx` | — | 数据源（仅 Python 侧读取） |
| — | `src/modules/newProductStatus/weekly_data_X.X-X.X.json` | 标准化 JSON（React 消费） |
| — | `src/demo/demoParseResult.ts` | Demo 模式数据（需手动更新周期范围） |

## 已同步版本

| 周期 | 新品复盘 HTML | 三部周报v1 HTML | 三部周报v1 JSON |
|------|-------------|----------------|----------------|
| 5.14-5.20 | ✅ | ✅ | ✅ |
| 5.7-5.13 | ✅ | ❌ | ❌ |
| 4.30-5.6 | ✅ | ✅ | ✅ |
