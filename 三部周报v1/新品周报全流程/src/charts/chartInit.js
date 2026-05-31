/**
 * Chart.js 图表初始化模块
 */

import { CHART_COLORS } from '../config.js';

/**
 * 创建饼图/环形图配置
 */
export function createPieConfig(labels, data, colors) {
  return {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors || CHART_COLORS.slice(0, data.length),
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  };
}

/**
 * 创建柱状图配置（单系列）
 */
export function createBarConfig(labels, data, label, color) {
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: color || 'rgba(192,57,43,0.8)',
        borderColor: '#c0392b',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  };
}

/**
 * 创建分组柱状图配置
 */
export function createGroupedBarConfig(labels, datasets) {
  return {
    type: 'bar',
    data: {
      labels,
      datasets
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: true } }
    }
  };
}

/**
 * 初始化总览图表
 */
export function initOverviewCharts(Chart) {
  // 出单分布
  new Chart(document.getElementById('chartOrderPie'), createPieConfig(
    ['8日内出单(Y): 27', '8日外出单(N): 13', '真正未出单: 3'],
    [27, 13, 3],
    ['#08845a', '#e07b24', '#c0392b']
  ));

  // 分析及时率
  new Chart(document.getElementById('chartTimelyPie'), createPieConfig(
    ['及时分析(71)', '8日内无分析(16)', '超7日未分析(15)'],
    [71, 16, 15],
    ['#08845a', '#e07b24', '#c0392b']
  ));
}

/**
 * 初始化品线维度图表
 */
export function initCatCharts(Chart, catData) {
  // 销量对比
  new Chart(document.getElementById('chartCatQty'), createGroupedBarConfig(
    catData.map(r => r.name),
    [
      { label: '本周销量', data: catData.map(r => r.qtyCur), backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
      { label: '上周销量', data: catData.map(r => r.qtyPre), backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
    ]
  ));

  // 销量占比
  new Chart(document.getElementById('chartCatPie2'), createPieConfig(
    catData.map(r => r.name),
    catData.map(r => r.qtyCur),
    CHART_COLORS
  ));
}

/**
 * 初始化分析人维度图表
 */
export function initAnCharts(Chart, anData) {
  new Chart(document.getElementById('chartAnQty'), createGroupedBarConfig(
    anData.map(r => r.name),
    [
      { label: '本周销量', data: anData.map(r => r.qtyCur), backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
      { label: '上周销量', data: anData.map(r => r.qtyPre), backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
    ]
  ));

  new Chart(document.getElementById('chartAnPie'), createPieConfig(
    anData.map(r => r.name),
    anData.map(r => r.qtyCur),
    CHART_COLORS
  ));
}

/**
 * 初始化拓展类型图表
 */
export function initTzCharts(Chart, tzData) {
  const filteredData = tzData.filter(r => r.sku > 0);

  // 出单率对比
  new Chart(document.getElementById('chartTzRate'), createGroupedBarConfig(
    filteredData.map(r => r.name),
    [
      { label: '本周出单率', data: filteredData.map(r => parseFloat(r.rateCur)), backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
      { label: '上周出单率', data: filteredData.map(r => parseFloat(r.ratePre)), backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
    ]
  ));

  // 销量对比
  new Chart(document.getElementById('chartTzQty'), createGroupedBarConfig(
    filteredData.map(r => r.name),
    [
      { label: '本周销量', data: filteredData.map(r => r.qtyCur), backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
      { label: '上周销量', data: filteredData.map(r => r.qtyPre), backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
    ]
  ));
}
