/**
 * 新品出单情况数据
 */

// 出单情况-总体
export const orderTotal = [
  { label: '在售SKU合计', cur: 101, pre: 90, change: '+11' },
  { label: '8日内出单(Y)', cur: 27, pre: 21, change: '+6' },
  { label: '8日外出单(N)', cur: 13, pre: 16, change: '-3' },
  { label: '有对手口径出单率', cur: '62.8%', pre: '58.2%', change: '+4.6%' },
  { label: '无对手口径出单率', cur: '69.0%', pre: '65.5%', change: '+3.5%' },
  { label: '真正未出单(无对手)', cur: 22, pre: 19, change: '+3' }
];

// 出单情况-按分析人
export const orderAn = [
  { name: '俞东旭', total: 12, y: 10, n: 1, un: 1, ordered: 11, rate: '91.7%', preRate: '90.9%', change: '+0.8%' },
  { name: '张潇', total: 16, y: 9, n: 5, un: 2, ordered: 14, rate: '87.5%', preRate: '83.8%', change: '+3.7%' },
  { name: '朱培源', total: 8, y: 3, n: 5, un: 0, ordered: 8, rate: '100.0%', preRate: '80.0%', change: '+20.0%' },
  { name: '王偲涵', total: 10, y: 5, n: 2, un: 3, ordered: 7, rate: '70.0%', preRate: '69.2%', change: '+0.8%' },
  { name: '章鹏', total: 1, y: 0, n: 0, un: 1, ordered: 0, rate: '0%', preRate: '0%', change: '-' },
  { name: '胡煜星', total: 15, y: 9, n: 6, un: 0, ordered: 15, rate: '100.0%', preRate: '100.0%', change: '+0.0%' }
];

// 出单情况-按品线
export const orderCat = [
  { name: '其他', total: 11, y: 6, n: 5, un: 0, ordered: 11, rate: '100.0%', preRate: '100.0%', change: '+0.0%' },
  { name: '挡泥板', total: 4, y: 2, n: 2, un: 0, ordered: 4, rate: '100.0%', preRate: '100.0%', change: '+0.0%' },
  { name: '机盖及附件', total: 7, y: 5, n: 1, un: 1, ordered: 6, rate: '85.7%', preRate: '80.0%', change: '+5.7%' },
  { name: '牌照板支架', total: 1, y: 0, n: 0, un: 1, ordered: 0, rate: '0%', preRate: '0%', change: '-' },
  { name: '车身外扩件', total: 6, y: 3, n: 2, un: 1, ordered: 5, rate: '83.3%', preRate: '80.0%', change: '+3.3%' },
  { name: '车门系统', total: 17, y: 11, n: 5, un: 1, ordered: 16, rate: '94.1%', preRate: '92.3%', change: '+1.8%' },
  { name: '饰条', total: 6, y: 4, n: 2, un: 0, ordered: 6, rate: '100.0%', preRate: '100.0%', change: '+0.0%' }
];
