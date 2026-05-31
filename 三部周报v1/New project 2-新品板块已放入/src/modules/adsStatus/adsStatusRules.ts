export const adsStatusRuleIds = [
  'acos_high',
  'spend_up_sales_down',
  'keyword_conversion_drop',
] as const;

export type AdsStatusRuleId = typeof adsStatusRuleIds[number];
