# 周报自动生成看板

本项目是一个本地网页形式的跨境电商汽配业务周报看板。页面通过读取 Excel 数据源，自动识别周周期、字段和维度，生成总销售数据的 KPI、趋势图、多维拆解表和中文复盘总结。

当前阶段只实现“总销售数据”模块，广告数据、价格数据、其他模块暂未接入。

## 正常模式

```bash
npm install
npm run dev
```

默认访问：

```bash
http://localhost:5173/
```

页面打开后会进入上传引导状态。请点击页面右上角“上传 Excel”读取本地文件，所有解析和计算都在浏览器前端完成。

## Demo 模式

Demo 展示模式不要求上传 Excel，访问：

```bash
http://localhost:5173/?demo=1
```

Demo 模式使用 `src/demo/demoParseResult.ts` 中的 `ParseResult` 快照作为输入，后续 KPI、趋势图、异常排行榜、明细表格和汇报文本仍走正常模式相同的计算链路。Demo 模式不会读取 `public/data/weekly-sales.xlsx`。

## 没有全局 npm 时

如果终端提示 `npm: command not found`，请先安装 Node.js（会包含 npm），或使用项目已准备的本地 npm CLI：

```bash
/Users/kun/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node .tools/package/bin/npm-cli.js install
/Users/kun/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node .tools/package/bin/npm-cli.js run dev
```

也可以安装 Node.js LTS 后重新打开终端，再使用标准命令：

```bash
npm install
npm run dev
```

## 数据源与部署安全

真实 Excel 不要放进 `public/` 目录公开部署。Vite 会把 `public/` 中的文件作为静态资源打包并公开访问。

当前本地真实文件如需保留，请放在：

```bash
private-data/weekly-sales.xlsx
```

该目录已加入 `.gitignore`，不会进入部署包。

当前项目的 `?demo=1` 使用 `demoParseResult`，不依赖真实 Excel 文件，也不会读取 `public/data/weekly-sales.xlsx`。如果需要公开部署，请确认真实 Excel 没有放入 `public` 目录。

### 提交与部署安全边界

- 不要把真实 Excel 或真实业务明细放入 `public/data/`。
- 不要提交真实业务数据文件，包括 `.xlsx`、`.xls`、`.xlsm`、`.csv`、`.tsv`。
- 不要提交 `static-export/`。该目录仅作为本地临时会议展示产物使用。
- `static-export/weekly-report-static.html` 可能内联真实 Excel 解析快照，不应部署到 Vercel、静态服务器或公开网盘。
- 会议展示静态快照如必须使用真实数据，只允许在本机临时生成和打开，确认接收范围后再展示，会后应清理。
- 如果要部署给外部访问，必须使用脱敏 demo 数据或默认上传模式，不要内置真实业务数据。

## Excel 格式要求

- 工作表名称必须为：`数据源`
- 周销量字段格式示例：`4/16-4/22销量`
- 周销售额字段格式示例：`4/16-4/22销售额`
- 市占字段格式示例：`4/23市占比`
- 直接对手出单字段格式示例：`4/23直接对手出单`
- 在售价字段格式示例：`2026/4/23在售价`

固定维度字段按表头识别，不依赖列字母。分析人字段会匹配包含“分析人”的表头，产品等级字段会匹配包含“等级”且不是“是否淘汰/停单”的表头。

## 构建

```bash
npm run build
```

没有全局 npm 时：

```bash
/Users/kun/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node .tools/package/bin/npm-cli.js run build
```

构建产物生成在 `dist/`。项目已配置 Vite `base: './'`，静态资源会以相对路径加载。将整个 `dist` 文件夹发给同事后，可打开：

```bash
cd dist
python3 -m http.server 8000
```

然后访问：

```bash
http://localhost:8000/?demo=1
```

也可以把整个 `dist/` 文件夹交给同事，让对方在 `dist` 目录中启动同样的本地静态服务后访问 Demo 地址。

## 常见问题

### 未找到“数据源”工作表

请检查 Excel 中是否存在名称完全等于 `数据源` 的 sheet。

### 未识别到周期

请检查周销量表头是否符合格式，例如 `4/16-4/22销量`。不要写成 `4.16-4.22销量` 或 `4/16-4/22 销量`。

### npm command not found

说明系统没有全局 npm。请安装 Node.js LTS，或使用上文的本地 npm CLI 命令。

### 上传文件后页面无数据

请确认上传的是 `.xlsx` 或 `.xls` 文件，并检查是否包含 `数据源` sheet、固定字段和周销量字段。页面底部“字段识别与数据源状态”会展示 warning，可根据提示修正数据源。
