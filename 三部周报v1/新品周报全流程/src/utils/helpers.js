/**
 * 辅助工具函数
 */

/**
 * 计算环比变化
 * @param {number} cur - 当前值
 * @param {number} pre - 上期值
 * @returns {string} HTML格式的环比标签
 */
export function calcHb(cur, pre) {
  if (!pre || pre === 0 || pre === '-') return '<span class="hb-flat">-</span>';
  const diff = cur - pre;
  const pct = ((diff / pre) * 100).toFixed(1);
  return diff >= 0 ? `<span class="hb-up">+${pct}%</span>` : `<span class="hb-down">${pct}%</span>`;
}

/**
 * 计算环比值（纯文本）
 * @param {number} cur - 当前值
 * @param {number} pre - 上期值
 * @returns {string} 文本格式的环比值
 */
export function calcHbVal(cur, pre) {
  if (!pre || pre === 0 || pre === '-') return '-';
  const diff = cur - pre;
  const pct = ((diff / pre) * 100).toFixed(1);
  return diff >= 0 ? `+${pct}%` : `${pct}%`;
}

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @param {string} currency - 货币符号
 * @returns {string} 格式化后的金额
 */
export function formatCurrency(amount, currency = '$') {
  if (amount === null || amount === undefined) return '-';
  return `${currency}${amount.toFixed(2)}`;
}

/**
 * 格式化数字（千分位）
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '-';
  return num.toLocaleString();
}

/**
 * 获取状态颜色
 * @param {string} status - 状态值
 * @returns {string} CSS颜色值
 */
export function getStatusColor(status) {
  const colors = {
    '正常': '#08845a',
    '竞争无优势': '#e07b24',
    '无市场': '#c0392b',
    '站外出单': '#8e44ad',
    '未上架': '#888'
  };
  return colors[status] || '#888';
}

/**
 * 获取出单情况颜色
 * @param {string} ord8 - 出单情况值
 * @returns {string} CSS颜色值
 */
export function getOrd8Color(ord8) {
  const colors = {
    'Y': '#08845a',
    'N': '#e07b24',
    '未出单': '#c0392b',
    '未上架': '#888'
  };
  return colors[ord8] || '#888';
}

/**
 * 过滤周期外上架的SKU
 * @param {Array} data - 数据数组
 * @param {string} cutoffDate - 截止日期
 * @returns {Array} 过滤后的数据
 */
export function filterByCutoffDate(data, cutoffDate, dateField = '实际上架日期') {
  return data.filter(item => {
    const listDate = item[dateField];
    if (!listDate) return true;
    return listDate <= cutoffDate;
  });
}
