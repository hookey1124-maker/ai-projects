/**
 * 新品周报数据管理器
 * 统一导出所有模块数据
 */

export const PERIOD = {
  start: '2026-04-30',
  end: '2026-05-06',
  label: '4.30-5.6',
  cutoffDate: '2026-05-06' // 周期外上架判断日期
};

export const CHART_COLORS = [
  '#0f3460', '#667eea', '#764ba2', '#f093fb', '#f5576c',
  '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#ff9a9e',
  '#a18cd1', '#fbc2eb', '#8fd3f4', '#84fab0', '#cfd9df'
];

export const STATUS_COLORS = {
  '正常': '#08845a',
  '竞争无优势': '#e07b24',
  '无市场': '#c0392b',
  '站外出单': '#8e44ad',
  '未上架': '#888'
};

export const ORD8_COLORS = {
  'Y': '#08845a',
  'N': '#e07b24',
  '未出单': '#c0392b',
  '未上架': '#888'
};
