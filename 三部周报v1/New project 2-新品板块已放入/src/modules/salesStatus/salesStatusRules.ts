import { classifyInsight } from '../../utils/insightRules';

export const salesStatusRuleIds = [
  'sales_qty_change',
  'sales_amount_change',
  'market_share_change',
  'avg_order_price_change',
  'competitiveness_drop',
  'price_structure_risk',
] as const;

export type SalesStatusRuleId = typeof salesStatusRuleIds[number];

export { classifyInsight as evaluateSalesStatusInsight };
