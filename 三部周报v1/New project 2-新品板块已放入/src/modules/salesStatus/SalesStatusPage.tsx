import DimensionTable from '../../components/DimensionTable';
import DimensionTabs from '../../components/DimensionTabs';
import EmptyState from '../../components/EmptyState';
import FieldInfo from '../../components/FieldInfo';
import KpiCards from '../../components/KpiCards';
import RiskRankingPanel from '../../components/RiskRankingPanel';
import SummaryConclusion from '../../components/SummaryConclusion';
import SummaryPanel from '../../components/SummaryPanel';
import TrendCharts from '../../components/TrendCharts';
import TrendFilterBar from '../../components/TrendFilterBar';
import ModulePeriodInfo from '../../components/common/ModulePeriodInfo';
import type { DimensionMetrics, ParseResult, SortKey, TableDimension, TrendDimension, TrendPoint } from '../../types/weeklyReport';
import type { WeeklyConclusion } from '../../utils/reportGenerator';
import { useModulePeriodInfo } from '../useModulePeriodInfo';

type ViewMode = 'analysis' | 'report';
type RankingDimension = '产品分类' | '产品等级' | '分析人';

type SalesStatusPageProps = {
  parseResult: ParseResult | null;
  blockingWarning?: string;
  loadMessage: string;
  uploadError: string;
  isStaticSnapshotMode: boolean;
  isDemoMode: boolean;
  viewMode: ViewMode;
  selectedPeriodIndex: number;
  kpiMetric: DimensionMetrics | null;
  totalKpiMetric: DimensionMetrics | null;
  totalMetrics: DimensionMetrics[];
  categoryMetrics: DimensionMetrics[];
  gradeMetrics: DimensionMetrics[];
  analystMetrics: DimensionMetrics[];
  conclusion: WeeklyConclusion | null;
  conclusionExpanded: boolean;
  onToggleConclusion: () => void;
  chartTotalTrendSeries: TrendPoint[];
  chartTrendSeries: TrendPoint[];
  trendSeries: TrendPoint[];
  trendRangeLabel: string;
  currentObjectLabel: string;
  trendDimension: TrendDimension;
  trendValue: string;
  trendValues: string[];
  onTrendDimensionChange: (dimension: TrendDimension) => void;
  onTrendValueChange: (value: string) => void;
  onDrill: (dimension: TrendDimension, value: string) => void;
  rankingDimension: RankingDimension;
  onRankingDimensionChange: (dimension: RankingDimension) => void;
  activeTab: TableDimension;
  onActiveTabChange: (tab: TableDimension) => void;
  tableMetrics: DimensionMetrics[];
  sortKey: SortKey;
  sortDirection: 'asc' | 'desc';
  onSort: (key: SortKey) => void;
  summary: {
    comparison: string[];
    detail: string[];
  };
  copyText: string;
};

export default function SalesStatusPage({
  parseResult,
  blockingWarning,
  loadMessage,
  uploadError,
  isStaticSnapshotMode,
  isDemoMode,
  viewMode,
  selectedPeriodIndex,
  kpiMetric,
  totalKpiMetric,
  totalMetrics,
  categoryMetrics,
  gradeMetrics,
  analystMetrics,
  conclusion,
  conclusionExpanded,
  onToggleConclusion,
  chartTotalTrendSeries,
  chartTrendSeries,
  trendSeries,
  trendRangeLabel,
  currentObjectLabel,
  trendDimension,
  trendValue,
  trendValues,
  onTrendDimensionChange,
  onTrendValueChange,
  onDrill,
  rankingDimension,
  onRankingDimensionChange,
  activeTab,
  onActiveTabChange,
  tableMetrics,
  sortKey,
  sortDirection,
  onSort,
  summary,
  copyText,
}: SalesStatusPageProps) {
  const { dataPeriod, periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo('salesStatus');

  if (!parseResult || blockingWarning || !parseResult.periods.length || !kpiMetric || !totalKpiMetric) {
    return (
      <main className="page-main">
        <ModulePeriodInfo dataPeriod={dataPeriod} periodTypeLabel={periodTypeLabel} sourceStatusLabel={sourceStatusLabel} />
        <EmptyState message={blockingWarning || loadMessage} />
        {uploadError && <div className="error-banner">{uploadError}</div>}
        {parseResult && <FieldInfo result={parseResult} selectedPeriodIndex={selectedPeriodIndex} />}
      </main>
    );
  }

  return (
    <main className="page-main">
      <ModulePeriodInfo dataPeriod={dataPeriod} periodTypeLabel={periodTypeLabel} sourceStatusLabel={sourceStatusLabel} />
      {uploadError && <div className="error-banner">{uploadError}</div>}

      <section className="dashboard-section overview-section">
        {isStaticSnapshotMode && <div className="demo-banner">当前为静态快照展示模式，数据来自真实 Excel。</div>}
        {isDemoMode && <div className="demo-banner">当前为 Demo 展示模式，数据来自周报展示源数据。</div>}
        <div className="section-heading">
          <div>
            <span>01</span>
            <h2>总盘概览</h2>
          </div>
          {parseResult.warnings.length > 0 && (
            <p>数据提示：当前数据源存在 {parseResult.warnings.length} 条 warning，部分字段判断需谨慎。</p>
          )}
        </div>
        <KpiCards metric={totalKpiMetric} />
        {conclusion && totalMetrics[0] && (
          <SummaryConclusion
            conclusion={conclusion}
            totalMetric={totalMetrics[0]}
            categoryMetrics={categoryMetrics}
            gradeMetrics={gradeMetrics}
            expanded={conclusionExpanded}
            onToggle={onToggleConclusion}
          />
        )}
        <TrendCharts
          series={chartTotalTrendSeries}
          selectedPeriodLabel={parseResult.periods[selectedPeriodIndex].label}
          dimension="总盘"
          value="全部"
          showCharts={['sales', 'market']}
          rangeLabel={trendRangeLabel}
          showPriceInSalesCard
        />
      </section>

      <section className="dashboard-section drilldown-section">
        <div className="section-heading">
          <div>
            <span>02</span>
            <h2>细分诊断</h2>
          </div>
          <p>当前分析对象：{currentObjectLabel}</p>
        </div>
        <div className="drilldown-toolbar">
          {viewMode === 'analysis' && (
            <TrendFilterBar
              dimension={trendDimension}
              value={trendValue}
              values={trendValues}
              onDimensionChange={onTrendDimensionChange}
              onValueChange={onTrendValueChange}
            />
          )}
          {trendDimension !== '总盘' && (
            <button type="button" className="secondary-button" onClick={() => onDrill('总盘', '全部')}>返回总盘</button>
          )}
        </div>
        {viewMode === 'analysis' && trendDimension === '总盘' ? (
          <div className="drilldown-empty-card">当前为总盘视角。请选择产品分类、产品等级或分析人，查看细分趋势和异常对象。</div>
        ) : viewMode === 'analysis' ? (
          <TrendCharts
            series={chartTrendSeries}
            selectedPeriodLabel={parseResult.periods[selectedPeriodIndex].label}
            dimension={trendDimension}
            value={trendValue}
            showCharts={trendDimension === '总盘' ? ['sales', 'market', 'price'] : ['sales', 'market', 'price', 'share']}
            rangeLabel={trendRangeLabel}
          />
        ) : null}
        <RiskRankingPanel
          dimension={rankingDimension}
          onDimensionChange={onRankingDimensionChange}
          categoryMetrics={categoryMetrics}
          gradeMetrics={gradeMetrics}
          analystMetrics={analystMetrics}
          onDrill={onDrill}
          compact={viewMode === 'report'}
        />
      </section>

      {viewMode === 'analysis' && (
        <section className="dashboard-section detail-section">
          <div className="section-heading">
            <div>
              <span>03</span>
              <h2>明细拆解</h2>
            </div>
            <p>表格保留全量横向对比，不随当前下钻对象过滤。</p>
          </div>
          <div className="table-card">
            <div className="table-header">
              <h2>多维拆解</h2>
              <DimensionTabs active={activeTab} onChange={onActiveTabChange} />
            </div>
            <DimensionTable
              metrics={tableMetrics}
              activeTab={activeTab}
              selectedDimension={trendDimension}
              selectedValue={trendValue}
              sortKey={sortKey}
              sortDirection={sortDirection}
              onSort={onSort}
              onDrill={onDrill}
              emptyMessage={trendDimension === '总盘' ? '当前维度暂无可展示数据。' : '当前筛选条件下暂无数据，请调整趋势对象或周期。'}
            />
          </div>
        </section>
      )}

      <section className="dashboard-section report-output-section">
        <div className="section-heading">
          <div>
            <span>{viewMode === 'analysis' ? '04' : '03'}</span>
            <h2>汇报输出</h2>
          </div>
          <p>总盘判断已合并到本周核心结论，这里聚焦维度横向对比和当前对象解释。</p>
        </div>
        <SummaryPanel
          comparison={summary.comparison}
          detail={summary.detail}
          copyText={copyText}
          gradeMetrics={gradeMetrics}
          currentMetric={kpiMetric}
          trendDimension={trendDimension}
          trendValue={trendValue}
          trendSeries={trendSeries}
          selectedPeriodIndex={selectedPeriodIndex}
        />
      </section>

      {viewMode === 'analysis' && <FieldInfo result={parseResult} selectedPeriodIndex={selectedPeriodIndex} />}
    </main>
  );
}
