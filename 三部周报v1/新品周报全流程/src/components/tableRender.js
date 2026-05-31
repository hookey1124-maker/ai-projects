/**
 * 表格渲染模块
 */

import { calcHb, getStatusColor, getOrd8Color, formatCurrency } from '../utils/helpers.js';

/**
 * 渲染品线表格
 */
export function buildCatTable(tbodyId, catData) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = catData.map(r => `
    <tr>
      <td><b>${r.name}</b></td>
      <td>${r.sku}</td>
      <td>${r.newList}</td>
      <td>${r.qtyCur}</td>
      <td>$${r.revCur.toFixed(2)}</td>
      <td>${r.qtyPre}</td>
      <td>$${r.revPre.toFixed(2)}</td>
      <td>${calcHb(r.qtyCur, r.qtyPre)}</td>
      <td>${calcHb(r.revCur, r.revPre)}</td>
    </tr>
  `).join('');
}

/**
 * 渲染分析人表格
 */
export function buildAnTable(tbodyId, anData) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = anData.map(r => `
    <tr>
      <td><b>${r.name}</b></td>
      <td>${r.sku}</td>
      <td>${r.newList}</td>
      <td>${r.qtyCur}</td>
      <td>$${r.revCur.toFixed(2)}</td>
      <td>${r.qtyPre}</td>
      <td>$${r.revPre.toFixed(2)}</td>
      <td>${calcHb(r.qtyCur, r.qtyPre)}</td>
      <td>${calcHb(r.revCur, r.revPre)}</td>
    </tr>
  `).join('');
}

/**
 * 渲染低占比新品表格（支持筛选）
 */
export function buildLowShareTable(tbodyId, lowShareData, filters = {}) {
  const tbody = document.getElementById(tbodyId);

  // 应用筛选
  let filtered = [...lowShareData];
  if (filters.status) {
    filtered = filtered.filter(r => r.status === filters.status);
  }
  if (filters.an) {
    filtered = filtered.filter(r => r.an === filters.an);
  }
  if (filters.cat) {
    filtered = filtered.filter(r => r.cat === filters.cat);
  }
  if (filters.ord8) {
    filtered = filtered.filter(r => r.ord8 === filters.ord8);
  }

  tbody.innerHTML = filtered.map(r => {
    const shareColor = parseFloat(r.share) < 50 ? 'hb-down' : '';
    return `
      <tr>
        <td>${r.id}</td>
        <td style="text-align:left">${r.sku}</td>
        <td>${r.cat}</td>
        <td>${r.an}</td>
        <td>${r.listDate}</td>
        <td>${r.qty}</td>
        <td>$${r.rev.toFixed(2)}</td>
        <td>${r.rivalQty}</td>
        <td class="${shareColor}">${r.share}</td>
        <td><span class="badge ${r.ord8 === 'Y' ? 'badge-y' : r.ord8 === 'N' ? 'badge-n' : 'badge-un'}">${r.ord8}</span></td>
        <td><span class="badge ${r.status === '竞争无优势' ? 'badge-un' : r.status === '无市场' ? 'badge-n' : 'badge-normal'}">${r.status}</span></td>
      </tr>
    `;
  }).join('');

  return filtered.length;
}

/**
 * 渲染四三累计明细表格
 */
export function buildCum43Table(tbodyId, cum43Data, filters = {}, cutoffDate = '2026-05-06') {
  const tbody = document.getElementById(tbodyId);

  // 应用筛选 + 过滤周期外上架
  let filtered = cum43Data.filter(r => {
    // 过滤周期外上架的SKU
    const listDate = r['实际上架日期'];
    if (listDate && listDate > cutoffDate) return false;

    // 其他筛选
    if (filters.status && r['5.6市场状态'] !== filters.status) return false;
    if (filters.an && r['4月分析人'] !== filters.an) return false;
    if (filters.cat && r['品类'] !== filters.cat) return false;
    if (filters.expand && r['产品拓展'] !== filters.expand) return false;
    if (filters.ord8 && r['5.6 8日出单情况'] !== filters.ord8) return false;

    return true;
  });

  tbody.innerHTML = filtered.map(r => {
    const statusColor = getStatusColor(r['5.6市场状态']);
    const ord8Color = getOrd8Color(r['5.6 8日出单情况']);
    const qty = r['4.30-5.6销量'];
    const rev = r['4.30-5.6销售额'];

    return `
      <tr>
        <td><b>${r.SKU}</b></td>
        <td>${r['实际上架日期']}</td>
        <td>${r['首次出单日期']}</td>
        <td>${r['4月分析人']}</td>
        <td>${r['品类'] || '-'}</td>
        <td>${r['产品拓展'] || '-'}</td>
        <td>${typeof qty === 'number' ? qty : qty}</td>
        <td>${typeof rev === 'number' ? '$' + rev.toFixed(2) : rev}</td>
        <td>${r['5.6对手销量']}</td>
        <td>${r['5.6市占比'].toFixed(1)}%</td>
        <td><span style="background:${statusColor};color:white;padding:2px 8px;border-radius:10px;font-size:11px;">${r['5.6市场状态']}</span></td>
        <td><span style="background:${ord8Color};color:white;padding:2px 8px;border-radius:10px;font-size:11px;">${r['5.6 8日出单情况']}</span></td>
      </tr>
    `;
  }).join('');

  return filtered.length;
}
