import {
  Area,
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { TrendDimension, TrendPoint } from '../types/weeklyReport';
import { formatAmount, formatInteger, formatPercent } from '../utils/formatters';

type TrendChartsProps = {
  series: TrendPoint[];
  selectedPeriodLabel: string;
  dimension: TrendDimension;
  value: string;
  showCharts?: Array<'sales' | 'market' | 'price' | 'share'>;
  rangeLabel?: string;
  showPriceInSalesCard?: boolean;
};

const chartTitle = (dimension: TrendDimension, value: string, suffix: string) => {
  if (dimension === '总盘') return `总盘${suffix}`;
  if (dimension === '产品等级') return `${value}档产品${suffix}`;
  if (dimension === '分析人') return `${value}负责产品${suffix}`;
  return `${value}${suffix}`;
};

const PeriodTick = ({ x, y, payload, selectedPeriodLabel }: any) => (
  <g transform={`translate(${x},${y})`}>
    <text x={0} y={0} dy={16} textAnchor="middle" fill={payload.value === selectedPeriodLabel ? '#1d4ed8' : '#64748b'} fontSize={12} fontWeight={payload.value === selectedPeriodLabel ? 700 : 500}>
      {payload.value}
    </text>
  </g>
);

export default function TrendCharts({
  series,
  selectedPeriodLabel,
  dimension,
  value,
  showCharts = ['sales', 'market', 'price', 'share'],
  rangeLabel,
  showPriceInSalesCard = false,
}: TrendChartsProps) {
  const data = series.map((item) => ({
    ...item,
    marketSharePercent: item.marketShare == null ? null : item.marketShare * 100,
    salesQtySharePercent: item.salesQtyShare == null ? null : item.salesQtyShare * 100,
    salesAmountSharePercent: item.salesAmountShare == null ? null : item.salesAmountShare * 100,
  }));
  const visibleCharts = showCharts.filter((chart) => !(dimension === '总盘' && chart === 'share'));

  return (
    <section className="trend-chart-section">
      {rangeLabel && <div className="trend-range-note">{rangeLabel}</div>}
      <div className="charts-grid">
        {visibleCharts.includes('sales') && <article className="chart-card">
        <h3>{chartTitle(dimension, value, '销售趋势')}</h3>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="periodLabel" tick={<PeriodTick selectedPeriodLabel={selectedPeriodLabel} />} interval={0} />
            <YAxis yAxisId="left" tickFormatter={formatInteger} />
            <YAxis yAxisId="right" orientation="right" tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
            <Tooltip formatter={(val: any, name) => name === '销售额' ? formatAmount(Number(val)) : formatInteger(Number(val))} />
            <Bar yAxisId="left" dataKey="salesQty" name="销量" fill="#2563eb" radius={[4, 4, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="salesAmount" name="销售额" stroke="#f59e0b" strokeWidth={2.4} dot={{ r: 3 }} />
          </ComposedChart>
        </ResponsiveContainer>
        {showPriceInSalesCard && (
          <div className="price-subchart">
            <h4>均价趋势</h4>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="periodLabel" tick={<PeriodTick selectedPeriodLabel={selectedPeriodLabel} />} interval={0} />
                <YAxis tickFormatter={(v) => Number(v).toFixed(0)} />
                <Tooltip formatter={(val: any) => val == null ? '--' : formatAmount(Number(val))} />
                <Line type="monotone" dataKey="listingAvgPrice" name="在售均价" stroke="#7c3aed" strokeWidth={2.2} dot={{ r: 2.8 }} connectNulls />
                <Line type="monotone" dataKey="soldAvgPrice" name="出单均价" stroke="#dc2626" strokeWidth={2.2} strokeDasharray="5 4" dot={{ r: 2.8 }} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </article>}

        {visibleCharts.includes('market') && <article className="chart-card">
        <h3>{chartTitle(dimension, value, '市占与竞争趋势')}</h3>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="periodLabel" tick={<PeriodTick selectedPeriodLabel={selectedPeriodLabel} />} interval={0} />
            <YAxis yAxisId="left" tickFormatter={(v) => `${v}%`} />
            <YAxis yAxisId="right" orientation="right" tickFormatter={formatInteger} />
            <Tooltip formatter={(val: any, name) => name === '市占比' ? (val == null ? '--' : `${Number(val).toFixed(1)}%`) : formatInteger(val == null ? null : Number(val))} />
            <Line yAxisId="left" type="monotone" dataKey="marketSharePercent" name="市占比" stroke="#059669" strokeWidth={2.4} dot={{ r: 3 }} />
            <Bar yAxisId="right" dataKey="competitorOrders" name="直接对手出单" fill="#94a3b8" radius={[4, 4, 0, 0]} />
          </ComposedChart>
        </ResponsiveContainer>
      </article>}

        {visibleCharts.includes('price') && <article className="chart-card">
        <h3>{chartTitle(dimension, value, '价格趋势')}</h3>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="periodLabel" tick={<PeriodTick selectedPeriodLabel={selectedPeriodLabel} />} interval={0} />
            <YAxis tickFormatter={(v) => Number(v).toFixed(0)} />
            <Tooltip formatter={(val: any) => formatAmount(Number(val))} />
            <Line type="monotone" dataKey="listingAvgPrice" name="在售均价" stroke="#7c3aed" strokeWidth={2.4} dot={{ r: 3 }} connectNulls />
            <Line type="monotone" dataKey="soldAvgPrice" name="出单均价" stroke="#dc2626" strokeWidth={2.4} strokeDasharray="5 4" dot={{ r: 3 }} connectNulls />
          </LineChart>
        </ResponsiveContainer>
      </article>}

        {visibleCharts.includes('share') && <article className="chart-card">
        <h3>{dimension === '总盘' ? '总盘销量 / 销售额占比' : chartTitle(dimension, value, '贡献占比趋势')}</h3>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="periodLabel" tick={<PeriodTick selectedPeriodLabel={selectedPeriodLabel} />} interval={0} />
            <YAxis tickFormatter={(v) => `${v}%`} domain={[0, 100]} />
            <Tooltip formatter={(val: any) => formatPercent(Number(val) / 100)} />
            <Area type="monotone" dataKey="salesQtySharePercent" name="销量占比" stroke="#2563eb" fill="#dbeafe" strokeWidth={2.2} />
            <Line type="monotone" dataKey="salesAmountSharePercent" name="销售额占比" stroke="#f97316" strokeWidth={2.4} dot={{ r: 3 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </article>}
      </div>
    </section>
  );
}
