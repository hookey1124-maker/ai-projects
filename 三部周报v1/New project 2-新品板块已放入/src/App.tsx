import { useEffect, useMemo, useState } from 'react';
import FileUpload from './components/FileUpload';
import Header from './components/Header';
import PeriodSelector from './components/PeriodSelector';
import Sidebar from './components/Sidebar';
import { DataCenterProvider } from './dataCenter/DataCenterProvider';
import { defaultModuleKey, moduleKeyFromRoute, moduleRegistry, moduleTitle } from './dataCenter/moduleRegistry';
import DataCenterValidationProbe from './dataCenter/validation/DataCenterValidationProbe';
import { demoParseResult } from './demo/demoParseResult';
import SalesStatusPage from './modules/salesStatus/SalesStatusPage';
import type { ModuleKey } from './dataCenter/types';
import type { ParseResult, SortKey, TableDimension, TrendDimension } from './types/weeklyReport';
import { parseWorkbook } from './utils/excelParser';
import { aggregateByDimension, buildKpiMetric, buildTrendSeries, getDimensionValues } from './utils/metrics';
import { buildWeeklyConclusion, buildWeeklyReportText } from './utils/reportGenerator';
import { generateSummary } from './utils/summaryGenerator';

type ViewMode = 'analysis' | 'report';
type RankingDimension = '产品分类' | '产品等级' | '分析人';

declare global {
  interface Window {
    __STATIC_PARSE_RESULT__?: ParseResult;
  }
}

const readActiveModuleFromHash = () => (typeof window === 'undefined' ? defaultModuleKey : moduleKeyFromRoute(window.location.hash));

export default function App() {
  const staticParseResult = window.__STATIC_PARSE_RESULT__;
  const isStaticSnapshotMode = Boolean(staticParseResult);
  const isDemoMode = !isStaticSnapshotMode && new URLSearchParams(window.location.search).get('demo') === '1';
  const [parseResult, setParseResult] = useState<ParseResult | null>(staticParseResult ?? (isDemoMode ? demoParseResult : null));
  const [loadMessage, setLoadMessage] = useState(isStaticSnapshotMode || isDemoMode ? '' : '请上传 Excel 文件开始生成周报。线上部署版本不内置真实业务数据源。');
  const [uploadError, setUploadError] = useState('');
  const [selectedPeriodIndex, setSelectedPeriodIndex] = useState(0);
  const [trendDimension, setTrendDimension] = useState<TrendDimension>('总盘');
  const [trendValue, setTrendValue] = useState('全部');
  const [activeTab, setActiveTab] = useState<TableDimension>('按产品分类');
  const [viewMode, setViewMode] = useState<ViewMode>('analysis');
  const [rankingDimension, setRankingDimension] = useState<RankingDimension>('产品分类');
  const [activeModule, setActiveModule] = useState<ModuleKey>(() => readActiveModuleFromHash());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [conclusionExpanded, setConclusionExpanded] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>('salesQty');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    if (!parseResult?.periods.length) return;
    setSelectedPeriodIndex(parseResult.periods.length - 1);
    setTrendDimension('总盘');
    setTrendValue('全部');
  }, [parseResult]);

  const handleFile = async (file: File) => {
    setUploadError('');
    if (!/\.(xlsx|xls)$/i.test(file.name)) {
      setUploadError('请上传 Excel 文件，支持 .xlsx 或 .xls 格式。');
      return;
    }
    try {
      const result = parseWorkbook(await file.arrayBuffer(), file.name);
      const blocking = result.warnings.find((warning) => warning.includes('未找到') || warning.includes('未识别到周销量'));
      if (blocking) {
        setUploadError(blocking.includes('未找到') ? '未找到‘数据源’工作表，请检查 Excel 文件。' : '未识别到周销量字段，请检查表头格式，例如 4/16-4/22销量。');
        if (!parseResult) setParseResult(result);
        return;
      }
      setParseResult(result);
      setLoadMessage('');
    } catch {
      setUploadError('Excel 解析失败，请检查文件是否损坏或格式是否正确。');
    }
  };

  const values = useMemo(() => {
    if (!parseResult) return ['全部'];
    return getDimensionValues(parseResult.rows, parseResult.fields, trendDimension);
  }, [parseResult, trendDimension]);

  useEffect(() => {
    if (trendDimension === '总盘') {
      setTrendValue('全部');
      return;
    }
    if (!values.includes(trendValue)) setTrendValue(values[0] ?? '未分组');
  }, [trendDimension, trendValue, values]);

  useEffect(() => {
    setConclusionExpanded(viewMode === 'report');
  }, [viewMode]);

  useEffect(() => {
    const syncModuleFromHash = () => setActiveModule(readActiveModuleFromHash());
    window.addEventListener('hashchange', syncModuleFromHash);
    return () => window.removeEventListener('hashchange', syncModuleFromHash);
  }, []);

  const tableMetrics = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return aggregateByDimension(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, activeTab);
  }, [activeTab, parseResult, selectedPeriodIndex]);

  const totalMetrics = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return aggregateByDimension(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, '总体');
  }, [parseResult, selectedPeriodIndex]);

  const categoryMetrics = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return aggregateByDimension(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, '按产品分类');
  }, [parseResult, selectedPeriodIndex]);

  const gradeMetrics = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return aggregateByDimension(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, '按产品等级');
  }, [parseResult, selectedPeriodIndex]);

  const analystMetrics = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return aggregateByDimension(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, '按分析人');
  }, [parseResult, selectedPeriodIndex]);

  const kpiMetric = useMemo(() => {
    if (!parseResult?.periods.length) return null;
    return buildKpiMetric(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, trendDimension, trendValue);
  }, [parseResult, selectedPeriodIndex, trendDimension, trendValue]);

  const totalKpiMetric = useMemo(() => {
    if (!parseResult?.periods.length) return null;
    return buildKpiMetric(parseResult.rows, parseResult.fields, parseResult.periods, selectedPeriodIndex, '总盘', '全部');
  }, [parseResult, selectedPeriodIndex]);

  const chartPeriods = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return parseResult.periods.slice(Math.max(0, selectedPeriodIndex - 7), selectedPeriodIndex + 1);
  }, [parseResult, selectedPeriodIndex]);

  const trendSeries = useMemo(() => {
    if (!parseResult?.periods.length) return [];
    return buildTrendSeries(parseResult.rows, parseResult.fields, parseResult.periods, trendDimension, trendValue);
  }, [parseResult, trendDimension, trendValue]);

  const chartTrendSeries = useMemo(() => {
    if (!parseResult?.periods.length || !chartPeriods.length) return [];
    return buildTrendSeries(parseResult.rows, parseResult.fields, chartPeriods, trendDimension, trendValue);
  }, [chartPeriods, parseResult, trendDimension, trendValue]);

  const chartTotalTrendSeries = useMemo(() => {
    if (!parseResult?.periods.length || !chartPeriods.length) return [];
    return buildTrendSeries(parseResult.rows, parseResult.fields, chartPeriods, '总盘', '全部');
  }, [chartPeriods, parseResult]);

  const summary = useMemo(() => {
    const total = totalMetrics[0];
    if (!parseResult?.periods.length || !total || !kpiMetric) return { total: [], comparison: [], detail: [] };
    return generateSummary(
      parseResult.periods[selectedPeriodIndex].label,
      total,
      kpiMetric,
      trendDimension,
      categoryMetrics,
      gradeMetrics,
      analystMetrics,
      trendSeries,
      selectedPeriodIndex,
    );
  }, [analystMetrics, categoryMetrics, gradeMetrics, kpiMetric, parseResult, selectedPeriodIndex, totalMetrics, trendDimension, trendSeries]);

  const conclusion = useMemo(() => {
    const total = totalMetrics[0];
    const periodLabel = parseResult?.periods[selectedPeriodIndex]?.label ?? '--';
    if (!total) return null;
    return buildWeeklyConclusion(periodLabel, total, categoryMetrics, gradeMetrics, analystMetrics, parseResult?.warnings ?? []);
  }, [analystMetrics, categoryMetrics, gradeMetrics, parseResult, selectedPeriodIndex, totalMetrics]);

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDirection((direction) => direction === 'desc' ? 'asc' : 'desc');
      return;
    }
    setSortKey(key);
    setSortDirection('desc');
  };

  const handleDrill = (dimension: TrendDimension, value: string) => {
    setTrendDimension(dimension);
    setTrendValue(value);
  };

  const handleModuleChange = (module: ModuleKey) => {
    setActiveModule(module);
    const nextHash = `#${moduleRegistry[module].route}`;
    if (window.location.hash !== nextHash) window.location.hash = moduleRegistry[module].route;
  };

  const statusText = parseResult
    ? `已识别 ${parseResult.periods.length} 个周周期，${parseResult.rows.length} 条 SKU 数据。${parseResult.warnings.length ? ` 数据提示：${parseResult.warnings.length} 条 warning。` : ''}`
    : loadMessage;

  const controls = (
    <>
      <div className="mode-switch">
        <button type="button" className={viewMode === 'analysis' ? 'active' : ''} onClick={() => setViewMode('analysis')}>分析模式</button>
        <button type="button" className={viewMode === 'report' ? 'active' : ''} onClick={() => setViewMode('report')}>汇报模式</button>
      </div>
      {activeModule === 'salesStatus' && viewMode === 'analysis' && !isDemoMode && !isStaticSnapshotMode && <FileUpload onFile={handleFile} />}
      {activeModule === 'salesStatus' && parseResult?.periods.length ? (
        <PeriodSelector periods={parseResult.periods} selectedIndex={selectedPeriodIndex} onChange={setSelectedPeriodIndex} />
      ) : null}
    </>
  );

  const blockingWarning = parseResult?.warnings.find((warning) => warning.includes('未找到') || warning.includes('未识别到周销量'));
  const periodLabel = parseResult?.periods[selectedPeriodIndex]?.label ?? '--';
  const previousLabel = selectedPeriodIndex > 0 ? parseResult?.periods[selectedPeriodIndex - 1]?.label ?? '--' : '--';
  const copyText = conclusion ? buildWeeklyReportText(periodLabel, previousLabel, conclusion, summary.comparison, summary.detail, parseResult?.warnings.length ?? 0, totalMetrics[0]) : '';
  const activeTitle = moduleTitle(activeModule);
  const placeholderMessage = `${activeTitle}模块开发中`;
  const currentObjectLabel = trendDimension === '总盘' ? '总盘 / 全部' : `${trendDimension} / ${trendValue}`;
  const trendRangeLabel = chartPeriods.length
    ? `趋势范围：${chartPeriods[0].label} 至 ${chartPeriods[chartPeriods.length - 1].label}`
    : '趋势范围：近 8 周';
  const ActiveModulePage = moduleRegistry[activeModule].Page;

  return (
    <DataCenterProvider salesParseResult={parseResult} selectedSourcePeriodIndex={selectedPeriodIndex}>
      <DataCenterValidationProbe parseResult={parseResult} />
      <div className={`app-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar
        activeModule={activeModule}
        collapsed={sidebarCollapsed}
        onModuleChange={handleModuleChange}
        onToggle={() => setSidebarCollapsed((value) => !value)}
      />
      <div className={`main-content app ${viewMode === 'report' ? 'report-mode' : ''}`}>
        <Header controls={controls} statusText={activeModule === 'salesStatus' ? statusText : placeholderMessage} moduleTitle={activeTitle} />

        {activeModule === 'salesStatus' ? (
          <SalesStatusPage
            parseResult={parseResult}
            blockingWarning={blockingWarning}
            loadMessage={loadMessage}
            uploadError={uploadError}
            isStaticSnapshotMode={isStaticSnapshotMode}
            isDemoMode={isDemoMode}
            viewMode={viewMode}
            selectedPeriodIndex={selectedPeriodIndex}
            kpiMetric={kpiMetric}
            totalKpiMetric={totalKpiMetric}
            totalMetrics={totalMetrics}
            categoryMetrics={categoryMetrics}
            gradeMetrics={gradeMetrics}
            analystMetrics={analystMetrics}
            conclusion={conclusion}
            conclusionExpanded={conclusionExpanded}
            onToggleConclusion={() => setConclusionExpanded((value) => !value)}
            chartTotalTrendSeries={chartTotalTrendSeries}
            chartTrendSeries={chartTrendSeries}
            trendSeries={trendSeries}
            trendRangeLabel={trendRangeLabel}
            currentObjectLabel={currentObjectLabel}
            trendDimension={trendDimension}
            trendValue={trendValue}
            trendValues={values}
            onTrendDimensionChange={setTrendDimension}
            onTrendValueChange={setTrendValue}
            onDrill={handleDrill}
            rankingDimension={rankingDimension}
            onRankingDimensionChange={setRankingDimension}
            activeTab={activeTab}
            onActiveTabChange={setActiveTab}
            tableMetrics={tableMetrics}
            sortKey={sortKey}
            sortDirection={sortDirection}
            onSort={handleSort}
            summary={summary}
            copyText={copyText}
          />
        ) : ActiveModulePage ? <ActiveModulePage /> : null}
      </div>
      </div>
    </DataCenterProvider>
  );
}
