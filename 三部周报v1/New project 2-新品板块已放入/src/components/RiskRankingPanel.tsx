import type { DimensionMetrics, RateStatus, TrendDimension } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatRate } from '../utils/formatters';

type RankingDimension = '产品分类' | '产品等级' | '分析人';

type RiskRankingPanelProps = {
  dimension: RankingDimension;
  onDimensionChange: (dimension: RankingDimension) => void;
  categoryMetrics: DimensionMetrics[];
  gradeMetrics: DimensionMetrics[];
  analystMetrics: DimensionMetrics[];
  onDrill: (dimension: TrendDimension, value: string) => void;
  compact?: boolean;
};

const dimensionToTrend: Record<RankingDimension, TrendDimension> = {
  产品分类: '产品分类',
  产品等级: '产品等级',
  分析人: '分析人',
};

const dimensions: RankingDimension[] = ['产品分类', '产品等级', '分析人'];

const getMetrics = (dimension: RankingDimension, categoryMetrics: DimensionMetrics[], gradeMetrics: DimensionMetrics[], analystMetrics: DimensionMetrics[]) => {
  if (dimension === '产品等级') return gradeMetrics;
  if (dimension === '分析人') return analystMetrics;
  return categoryMetrics;
};

const TagList = ({ tags }: { tags: string[] }) => (
  <div className="tag-list compact">
    {tags.map((tag) => <span className={`tag tag-${tag}`} key={tag}>{tag}</span>)}
  </div>
);

const marketShareRate = (item: DimensionMetrics): { value: number | null; status: RateStatus } => {
  if (item.marketShare == null || item.prevMarketShare == null) return { value: null, status: 'none' };
  if (item.prevMarketShare === 0) return { value: item.marketShare > 0 ? null : 0, status: item.marketShare > 0 ? 'new' : 'normal' };
  return { value: (item.marketShare - item.prevMarketShare) / item.prevMarketShare, status: 'normal' };
};

const RankingList = ({
  title,
  items,
  valueLabel,
  changeLabel,
  rateLabel,
  onClick,
}: {
  title: string;
  items: DimensionMetrics[];
  valueLabel: (item: DimensionMetrics) => string;
  changeLabel: (item: DimensionMetrics) => string;
  rateLabel: (item: DimensionMetrics) => string;
  onClick: (item: DimensionMetrics) => void;
}) => (
  <div className="ranking-list">
    <h3>{title}</h3>
    {items.length === 0 ? (
      <div className="ranking-empty">暂无明显下滑项</div>
    ) : items.map((item, index) => (
      <button type="button" className="ranking-item" key={`${title}-${item.dimensionName}`} onClick={() => onClick(item)}>
        <span className="ranking-index">{index + 1}</span>
        <span className="ranking-main">
          <strong>{item.dimensionName}</strong>
          <span className="ranking-metrics">
            <span><b>本期</b>{valueLabel(item)}</span>
            <span><b>变化</b>{changeLabel(item)}</span>
            <span><b>环比</b>{rateLabel(item)}</span>
          </span>
          <TagList tags={item.insightTags} />
        </span>
        <span className="ranking-action">{item.action}</span>
      </button>
    ))}
  </div>
);

export default function RiskRankingPanel({
  dimension,
  onDimensionChange,
  categoryMetrics,
  gradeMetrics,
  analystMetrics,
  onDrill,
  compact = false,
}: RiskRankingPanelProps) {
  const metrics = getMetrics(dimension, categoryMetrics, gradeMetrics, analystMetrics);
  const limit = compact ? 5 : 10;
  const titleSuffix = compact ? 'TOP 5' : 'TOP 10';
  const drill = (item: DimensionMetrics) => onDrill(dimensionToTrend[dimension], item.dimensionName);
  const amountDrag = [...metrics].filter((item) => item.salesAmountChange < 0).sort((a, b) => a.salesAmountChange - b.salesAmountChange).slice(0, limit);
  const qtyDrag = [...metrics].filter((item) => item.salesQtyChange < 0).sort((a, b) => a.salesQtyChange - b.salesQtyChange).slice(0, limit);
  const shareDrag = [...metrics]
    .filter((item) => item.marketShare != null && item.marketShareBpChange != null && item.marketShareBpChange < 0)
    .sort((a, b) => (a.marketShareBpChange ?? 0) - (b.marketShareBpChange ?? 0))
    .slice(0, limit);

  return (
    <section className={`risk-panel ${compact ? 'compact' : ''}`}>
      <div className="risk-header">
        <h2>重点异常排行榜</h2>
        <div className="segmented small">
          {dimensions.map((item) => (
            <button type="button" key={item} className={dimension === item ? 'active' : ''} onClick={() => onDimensionChange(item)}>
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="ranking-grid">
        <RankingList
          title={`销售额拖累 ${titleSuffix}`}
          items={amountDrag}
          valueLabel={(item) => formatAmount(item.salesAmount)}
          changeLabel={(item) => formatAmount(item.salesAmountChange)}
          rateLabel={(item) => formatRate(item.salesAmountRate, item.salesAmountRateStatus)}
          onClick={drill}
        />
        <RankingList
          title={`销量拖累 ${titleSuffix}`}
          items={qtyDrag}
          valueLabel={(item) => formatInteger(item.salesQty)}
          changeLabel={(item) => formatInteger(item.salesQtyChange)}
          rateLabel={(item) => formatRate(item.salesQtyRate, item.salesQtyRateStatus)}
          onClick={drill}
        />
        <RankingList
          title={`市占下滑 ${titleSuffix}`}
          items={shareDrag}
          valueLabel={(item) => formatPercent(item.marketShare)}
          changeLabel={(item) => formatBp(item.marketShareBpChange)}
          rateLabel={(item) => {
            const rate = marketShareRate(item);
            return formatRate(rate.value, rate.status);
          }}
          onClick={drill}
        />
      </div>
    </section>
  );
}
