import { ArrowDownRight, ArrowUpRight, Minus } from 'lucide-react';
import type { DimensionMetrics } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatPrice, formatRate, signedClass } from '../utils/formatters';

type KpiCardsProps = {
  metric: DimensionMetrics;
};

const TrendIcon = ({ className }: { className: string }) => {
  if (className === 'positive') return <ArrowUpRight size={16} />;
  if (className === 'negative') return <ArrowDownRight size={16} />;
  return <Minus size={16} />;
};

export default function KpiCards({ metric }: KpiCardsProps) {
  const prefix = metric.dimensionName === '总盘' ? '' : `${metric.dimensionName}`;
  const cards = [
    {
      name: `${prefix}销量`,
      value: formatInteger(metric.salesQty),
      change: formatRate(metric.salesQtyRate, metric.salesQtyRateStatus),
      className: signedClass(metric.salesQtyRate, metric.salesQtyRateStatus),
    },
    {
      name: `${prefix}销售额`,
      value: formatAmount(metric.salesAmount),
      change: formatRate(metric.salesAmountRate, metric.salesAmountRateStatus),
      className: signedClass(metric.salesAmountRate, metric.salesAmountRateStatus),
    },
    {
      name: `${prefix}市占比`,
      value: formatPercent(metric.marketShare),
      change: formatBp(metric.marketShareBpChange),
      className: signedClass(metric.marketShareBpChange),
    },
    {
      name: `${prefix}直接对手出单`,
      value: formatInteger(metric.competitorOrders),
      change: formatRate(metric.competitorRate, metric.competitorRateStatus),
      className: signedClass(metric.competitorRate, metric.competitorRateStatus),
    },
    {
      name: `${prefix}在售均价`,
      value: formatPrice(metric.listingAvgPrice),
      change: formatRate(metric.listingAvgPriceRate, metric.listingAvgPriceRateStatus),
      className: signedClass(metric.listingAvgPriceRate, metric.listingAvgPriceRateStatus),
    },
    {
      name: `${prefix}出单均价`,
      value: formatPrice(metric.soldAvgPrice),
      change: formatRate(metric.soldAvgPriceRate, metric.soldAvgPriceRateStatus),
      className: signedClass(metric.soldAvgPriceRate, metric.soldAvgPriceRateStatus),
    },
  ];

  return (
    <section className="kpi-grid">
      {cards.map((card) => (
        <article className="kpi-card" key={card.name}>
          <div className="kpi-label">{card.name || '总盘'}</div>
          <div className="kpi-value">{card.value}</div>
          <div className={`kpi-change ${card.className}`}>
            <TrendIcon className={card.className} />
            {card.change}
          </div>
        </article>
      ))}
    </section>
  );
}
