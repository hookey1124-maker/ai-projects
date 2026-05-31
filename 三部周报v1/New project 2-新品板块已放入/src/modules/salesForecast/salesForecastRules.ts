export const salesForecastRuleIds = [
  'forecast_drop',
  'forecast_gap',
  'high_risk_sku',
] as const;

export type SalesForecastRuleId = typeof salesForecastRuleIds[number];
