export const accountTrafficStatusRuleIds = [
  'traffic_drop',
  'conversion_drop',
  'traffic_sales_divergence',
] as const;

export type AccountTrafficStatusRuleId = typeof accountTrafficStatusRuleIds[number];
