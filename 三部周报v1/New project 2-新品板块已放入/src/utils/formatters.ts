import type { RateStatus } from '../types/weeklyReport';

export const formatInteger = (value: number | null | undefined) =>
  value == null || Number.isNaN(value)
    ? '--'
    : Math.round(value).toLocaleString('zh-CN');

export const formatAmount = (value: number | null | undefined) =>
  value == null || Number.isNaN(value)
    ? '--'
    : value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const formatPercent = (value: number | null | undefined, digits = 1) =>
  value == null || Number.isNaN(value) ? '--' : `${(value * 100).toFixed(digits)}%`;

export const formatRate = (value: number | null | undefined, status: RateStatus = 'normal') => {
  if (status === 'new') return '新增';
  if (status === 'none' || value == null || Number.isNaN(value)) return '--';
  const sign = value > 0 ? '+' : '';
  return `${sign}${(value * 100).toFixed(1)}%`;
};

export const formatPrice = (value: number | null | undefined) => formatAmount(value);

export const formatBp = (bp: number | null | undefined) => {
  if (bp == null || Number.isNaN(bp)) return '--';
  const pct = bp / 100;
  const sign = pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(1)}pct`;
};

export const signedClass = (value: number | null | undefined, status: RateStatus = 'normal') => {
  if (status === 'new') return 'positive';
  if (value == null || Number.isNaN(value) || Math.abs(value) < 0.000001) return 'neutral';
  return value > 0 ? 'positive' : 'negative';
};

export const safeDisplay = (value: unknown) => {
  const text = String(value ?? '').trim();
  return text && text !== '#N/A' && text !== '#REF!' && text !== 'undefined' ? text : '未分组';
};
