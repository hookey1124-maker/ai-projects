export type TemplateStatusRuleResult = {
  id: string;
  title: string;
  severity: 'info' | 'warning' | 'critical';
  description: string;
};

export const templateStatusRuleIds = [
  'template_metric_missing',
  'template_metric_abnormal',
] as const;

export type TemplateStatusRuleId = typeof templateStatusRuleIds[number];

export const evaluateTemplateStatusRules = (): TemplateStatusRuleResult[] => [];
