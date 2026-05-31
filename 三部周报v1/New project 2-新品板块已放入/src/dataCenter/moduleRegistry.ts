import type { ComponentType } from 'react';
import { AccountTrafficStatusPage } from '../modules/accountTrafficStatus';
import { AdsStatusPage } from '../modules/adsStatus';
import { NewProductStatusPage } from '../modules/newProductStatus';
import { PricingStatusPage } from '../modules/pricingStatus';
import { SalesForecastPage } from '../modules/salesForecast';
import { modulePeriodConfig } from './periodConfig';
import type { PeriodType } from './periodTypes';
import type { ModuleKey } from './types';

export type ModuleDefinition = {
  key: ModuleKey;
  label: string;
  description: string;
  icon: string;
  route: string;
  periodType: PeriodType;
  Page?: ComponentType;
};

export const moduleDefinitions: ModuleDefinition[] = [
  {
    key: 'salesStatus',
    label: '总销售状态',
    description: '销量 / 销售额 / 市占 / 均价',
    icon: '总',
    route: '/sales-status',
    periodType: modulePeriodConfig.salesStatus.periodType,
  },
  {
    key: 'newProductStatus',
    label: '新品状态',
    description: '上市 / 动销 / 爬坡 / 异常',
    icon: '新',
    route: '/new-product-status',
    periodType: modulePeriodConfig.newProductStatus.periodType,
    Page: NewProductStatusPage,
  },
  {
    key: 'adsStatus',
    label: '广告状态',
    description: '花费 / ACOS / CPC / 转化',
    icon: '广',
    route: '/ads-status',
    periodType: modulePeriodConfig.adsStatus.periodType,
    Page: AdsStatusPage,
  },
  {
    key: 'pricingStatus',
    label: '价格状态',
    description: '在售价 / 均价 / 调价',
    icon: '价',
    route: '/pricing-status',
    periodType: modulePeriodConfig.pricingStatus.periodType,
    Page: PricingStatusPage,
  },
  {
    key: 'accountTrafficStatus',
    label: '账号流量状态',
    description: '会话 / 浏览 / 转化 / 流量',
    icon: '流',
    route: '/account-traffic-status',
    periodType: modulePeriodConfig.accountTrafficStatus.periodType,
    Page: AccountTrafficStatusPage,
  },
  {
    key: 'salesForecast',
    label: '销量预估',
    description: '预测 / 偏差 / 风险 SKU',
    icon: '预',
    route: '/sales-forecast',
    periodType: modulePeriodConfig.salesForecast.periodType,
    Page: SalesForecastPage,
  },
];

export const moduleRegistry = Object.fromEntries(
  moduleDefinitions.map((definition) => [definition.key, definition]),
) as Record<ModuleKey, ModuleDefinition>;

export const defaultModuleKey: ModuleKey = 'salesStatus';

export const moduleTitle = (key: ModuleKey) => moduleRegistry[key]?.label ?? moduleRegistry[defaultModuleKey].label;

export const moduleKeyFromRoute = (route: string): ModuleKey => {
  const normalizedRoute = route.replace(/^#/, '') || moduleRegistry[defaultModuleKey].route;
  return moduleDefinitions.find((definition) => definition.route === normalizedRoute)?.key ?? defaultModuleKey;
};
