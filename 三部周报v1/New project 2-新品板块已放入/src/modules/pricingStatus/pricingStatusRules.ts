export const pricingStatusRuleIds = [
  'listing_price_change',
  'avg_order_price_drop',
  'price_sales_divergence',
] as const;

export type PricingStatusRuleId = typeof pricingStatusRuleIds[number];
