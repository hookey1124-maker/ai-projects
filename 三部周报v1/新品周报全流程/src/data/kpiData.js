/**
 * KPI总览数据
 */

export const kpiData = {
  totalSku: 101,
  newListCount: 11,
  yCount: 27,
  nCount: 13,
  unCount: 22,
  yRate: '62.8%',
  nRate: '30.2%',
  totalOrdered: 40,
  totalOrderedRival: 43,
  totalOrderedNoRival: 58,
  totalQty: 195,
  timelyRate: '70.3%',
  totalRevenue: '$20,495',
  lowShareCount: 40,
  lowShareY: 24,
  lowShareN: 12,
  lowShareUn: 3
};

export const orderDistribution = [
  { label: '8日内出单(Y)', count: 27, color: '#08845a' },
  { label: '8日外出单(N)', count: 13, color: '#e07b24' },
  { label: '真正未出单', count: 3, color: '#c0392b' }
];

export const timelyDistribution = [
  { label: '及时分析', count: 71, color: '#08845a' },
  { label: '8日内无分析', count: 16, color: '#e07b24' },
  { label: '超7日未分析', count: 15, color: '#c0392b' }
];
