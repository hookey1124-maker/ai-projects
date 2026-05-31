import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const distDir = path.join(projectRoot, 'dist');
const outputDir = path.join(projectRoot, 'static-export');
const outputHtmlPath = path.join(outputDir, 'weekly-report-static.html');
const readmePath = path.join(outputDir, 'README-如何打开.md');
const verificationPath = path.join(outputDir, 'verification-report.md');

const publicExcelPath = path.join(projectRoot, 'public/data/weekly-sales.xlsx');
const privateExcelPath = path.join(projectRoot, 'private-data/weekly-sales.xlsx');
const excelPath = existsSync(publicExcelPath) ? publicExcelPath : privateExcelPath;

if (!existsSync(excelPath)) {
  throw new Error(`未找到真实 Excel 数据源：${publicExcelPath} 或 ${privateExcelPath}`);
}

if (!existsSync(path.join(distDir, 'index.html'))) {
  throw new Error('未找到 dist/index.html。请先运行 npm run build，再运行 npm run export:static。');
}

const toArrayBuffer = (buffer) =>
  buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);

const fmtNumber = (value, digits = 2) =>
  value == null || Number.isNaN(value) ? '--' : Number(value).toLocaleString('zh-CN', { maximumFractionDigits: digits });

const fmtPercent = (value) =>
  value == null || Number.isNaN(value) ? '--' : `${(value * 100).toFixed(1)}%`;

const assertEqual = (label, actual, expected) => {
  if (actual !== expected) {
    throw new Error(`${label} 校验失败：期望 ${expected}，实际 ${actual}`);
  }
};

const loadProjectModules = async () => {
  const server = await createServer({
    root: projectRoot,
    logLevel: 'silent',
    server: { middlewareMode: true },
    appType: 'custom',
  });
  try {
    const parser = await server.ssrLoadModule('/src/utils/excelParser.ts');
    const metrics = await server.ssrLoadModule('/src/utils/metrics.ts');
    return { server, parser, metrics };
  } catch (error) {
    await server.close();
    throw error;
  }
};

const inlineDistHtml = async (parseResult) => {
  const safeInlineScript = (content) =>
    content
      .replace(/<\/script/gi, '<\\/script');

  let html = await readFile(path.join(distDir, 'index.html'), 'utf8');
  const snapshotScript = [
    '<script>',
    'window.__STATIC_PARSE_RESULT__ = ',
    safeInlineScript(JSON.stringify(parseResult)),
    ';',
    '</script>',
  ].join('');

  html = html.replace('<title>周报自动生成看板</title>', '<title>周报看板静态展示版</title>');
  html = html.replace('</head>', () => `${snapshotScript}\n</head>`);

  const cssMatches = [...html.matchAll(/<link rel="stylesheet" href="([^"]+)">/g)];
  for (const match of cssMatches) {
    const href = match[1].replace(/^\.\//, '');
    const css = await readFile(path.join(distDir, href), 'utf8');
    html = html.replace(match[0], () => `<style>\n${css}\n</style>`);
  }

  const scriptMatches = [...html.matchAll(/<script type="module" crossorigin src="([^"]+)"><\/script>/g)];
  for (const match of scriptMatches) {
    const src = match[1].replace(/^\.\//, '');
    const js = await readFile(path.join(distDir, src), 'utf8');
    html = html.replace(match[0], () => `<script type="module">\n${safeInlineScript(js)}\n</script>`);
  }
  return html;
};

const writeReadme = async () => {
  const content = `# 周报看板静态展示版打开方式

## 直接打开

可以直接双击：

\`\`\`bash
weekly-report-static.html
\`\`\`

这个文件已经内联 CSS、JS 和真实 Excel 解析快照，不依赖 npm、dev server、网络或 Excel 文件。

## 如果双击打不开

在终端运行：

\`\`\`bash
cd "/Users/kun/Documents/New project 2/static-export"
python3 -m http.server 8000
\`\`\`

然后打开：

\`\`\`bash
http://localhost:8000/weekly-report-static.html
\`\`\`
`;
  await writeFile(readmePath, content);
};

const writeVerification = async ({ parseResult, totalKpiMetric, mappingResults, sourcePath }) => {
  const latestPeriod = parseResult.periods.at(-1);
  const reference = {
    salesQty: '约 4,792',
    salesAmount: '约 331,484.75',
    marketShare: '约 45.4%',
    competitorOrders: '约 5,771',
    listingAvgPrice: '约 94.35',
    soldAvgPrice: '约 69.17',
  };
  const actual = {
    salesQty: fmtNumber(totalKpiMetric.salesQty, 0),
    salesAmount: fmtNumber(totalKpiMetric.salesAmount, 2),
    marketShare: fmtPercent(totalKpiMetric.marketShare),
    competitorOrders: fmtNumber(totalKpiMetric.competitorOrders, 0),
    listingAvgPrice: fmtNumber(totalKpiMetric.listingAvgPrice, 2),
    soldAvgPrice: fmtNumber(totalKpiMetric.soldAvgPrice, 2),
  };
  const content = `# 静态快照验证报告

## 数据源

- 使用 Excel：\`${sourcePath}\`
- 生成方式：通过当前项目 \`parseWorkbook\` 解析 Excel，并将 \`ParseResult\` 快照内嵌到 \`weekly-report-static.html\`
- 静态页面打开后不再读取 Excel，也不依赖 \`public/data/weekly-sales.xlsx\`

## 基础识别结果

- SKU 行数：${parseResult.rows.length}
- 周周期数量：${parseResult.periods.length}
- 最新周期：${latestPeriod?.label ?? '--'}
- 分析人字段：${parseResult.fields.analyst ?? '--'}
- 产品等级字段：${parseResult.fields.productGrade ?? '--'}
- warning 数量：${parseResult.warnings.length}

## 最新周期核心 KPI

| 指标 | 当前项目真实计算结果 | 参考值 |
| --- | ---: | ---: |
| 销量 | ${actual.salesQty} | ${reference.salesQty} |
| 销售额 | ${actual.salesAmount} | ${reference.salesAmount} |
| 市占比 | ${actual.marketShare} | ${reference.marketShare} |
| 直接对手出单 | ${actual.competitorOrders} | ${reference.competitorOrders} |
| 在售均价 | ${actual.listingAvgPrice} | ${reference.listingAvgPrice} |
| 出单均价 | ${actual.soldAvgPrice} | ${reference.soldAvgPrice} |

如与参考值存在小数展示差异，以当前项目真实计算结果为准；本报告中的结果来自 \`buildKpiMetric(..., '总盘', '全部')\`。

## 周期映射校验

| 周期 | 市占比列 | 直接对手出单列 | 在售价列 | 结果 |
| --- | --- | --- | --- | --- |
${mappingResults.map((item) => `| ${item.label} | ${item.actual.marketShareColumn} | ${item.actual.competitorColumn} | ${item.actual.listingPriceColumn} | ${item.ok ? '通过' : '失败'} |`).join('\n')}

周期映射逻辑仍使用当前项目 \`buildPeriods\`：按周结束日、结束日 +1、结束日 +2、结束日 +3 独立候选匹配辅助字段。

## 页面一致性

- 静态页面复用当前 React 组件、CSS、布局和指标计算逻辑。
- 静态页面的数据边界是 \`ParseResult\`，不是手写 KPI、趋势、排行榜或表格结果。
- 静态页面与当前项目页面的差异：静态页隐藏 Excel 上传入口，并显示“静态快照展示模式”提示；数据和渲染链路保持一致。
`;
  await writeFile(verificationPath, content);
};

const main = async () => {
  const { server, parser, metrics } = await loadProjectModules();
  try {
    const excelBuffer = await readFile(excelPath);
    const parseResult = parser.parseWorkbook(toArrayBuffer(excelBuffer), path.basename(excelPath));
    assertEqual('SKU 行数', parseResult.rows.length, 1100);
    assertEqual('周周期数量', parseResult.periods.length, 8);
    assertEqual('最新周期', parseResult.periods.at(-1)?.label, '4/16-4/22');
    assertEqual('分析人字段', parseResult.fields.analyst, '4月分析人');
    assertEqual('产品等级字段', parseResult.fields.productGrade, '4月等级');

    const selectedPeriodIndex = parseResult.periods.length - 1;
    const totalKpiMetric = metrics.buildKpiMetric(
      parseResult.rows,
      parseResult.fields,
      parseResult.periods,
      selectedPeriodIndex,
      '总盘',
      '全部',
    );

    const requiredMappings = [
      {
        label: '2/26-3/4',
        expected: {
          marketShareColumn: '3/4市占比',
          competitorColumn: '3/4直接对手出单',
          listingPriceColumn: '2026/3/4在售价',
        },
      },
      {
        label: '3/12-3/18',
        expected: {
          marketShareColumn: '3/20市占比',
          competitorColumn: '3/20直接对手出单',
          listingPriceColumn: '2026/3/19在售价',
        },
      },
      {
        label: '4/16-4/22',
        expected: {
          marketShareColumn: '4/23市占比',
          competitorColumn: '4/23直接对手出单',
          listingPriceColumn: '2026/4/23在售价',
        },
      },
    ];

    const mappingResults = requiredMappings.map((item) => {
      const period = parseResult.periods.find((candidate) => candidate.label === item.label);
      const actual = {
        marketShareColumn: period?.marketShareColumn ?? '--',
        competitorColumn: period?.competitorColumn ?? '--',
        listingPriceColumn: period?.listingPriceColumn ?? '--',
      };
      const ok =
        actual.marketShareColumn === item.expected.marketShareColumn &&
        actual.competitorColumn === item.expected.competitorColumn &&
        actual.listingPriceColumn === item.expected.listingPriceColumn;
      if (!ok) {
        throw new Error(`${item.label} 周期映射校验失败：${JSON.stringify(actual)}`);
      }
      return { label: item.label, actual, ok };
    });

    await mkdir(outputDir, { recursive: true });
    await writeFile(outputHtmlPath, await inlineDistHtml(parseResult));
    await writeReadme();
    await writeVerification({
      parseResult,
      totalKpiMetric,
      mappingResults,
      sourcePath: path.relative(projectRoot, excelPath),
    });

    console.log(JSON.stringify({
      outputHtmlPath,
      verificationPath,
      readmePath,
      sourcePath: path.relative(projectRoot, excelPath),
      rows: parseResult.rows.length,
      periods: parseResult.periods.length,
      latestPeriod: parseResult.periods.at(-1)?.label,
      kpi: {
        salesQty: totalKpiMetric.salesQty,
        salesAmount: totalKpiMetric.salesAmount,
        marketShare: totalKpiMetric.marketShare,
        competitorOrders: totalKpiMetric.competitorOrders,
        listingAvgPrice: totalKpiMetric.listingAvgPrice,
        soldAvgPrice: totalKpiMetric.soldAvgPrice,
      },
    }, null, 2));
  } finally {
    await server.close();
  }
};

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
