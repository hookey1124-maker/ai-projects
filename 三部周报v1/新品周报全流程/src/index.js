/**
 * 主应用入口
 */

import { Chart } from 'chart.js/auto';
import {
  PERIOD,
  CHART_COLORS,
  kpiData,
  catData,
  anData,
  tzData,
  timelyData,
  orderTotal,
  orderAn,
  orderCat,
  lowShareData,
  plpAnData,
  plpCatData,
  cum43Data,
  cum43Stats
} from './data/index.js';

import {
  initOverviewCharts,
  initCatCharts,
  initAnCharts,
  initTzCharts
} from './charts/chartInit.js';

import {
  buildCatTable,
  buildAnTable,
  buildLowShareTable,
  buildCum43Table
} from './components/tableRender.js';

/**
 * 切换显示板块
 */
export function showSection(sectionId, linkEl) {
  // 隐藏所有板块
  document.querySelectorAll('.section-wrap').forEach(el => {
    el.style.display = 'none';
  });

  // 显示目标板块
  const target = document.getElementById(`section-${sectionId}`);
  if (target) {
    target.style.display = 'block';
  }

  // 更新侧边栏高亮
  document.querySelectorAll('.sidebar li a').forEach(a => {
    a.classList.remove('active');
  });
  if (linkEl) {
    linkEl.classList.add('active');
  }
}

/**
 * 初始化筛选功能
 */
function initFilters() {
  // 低占比新品筛选
  const lowShareFilterBtn = document.getElementById('filterLowShareBtn');
  const resetLowShareBtn = document.getElementById('resetLowShareBtn');

  if (lowShareFilterBtn) {
    lowShareFilterBtn.addEventListener('click', () => {
      const filters = {
        status: document.getElementById('filterStatus')?.value || '',
        an: document.getElementById('filterAn')?.value || '',
        cat: document.getElementById('filterCat')?.value || '',
        ord8: document.getElementById('filterOrd8')?.value || ''
      };
      const count = buildLowShareTable('lowShareTableBody', lowShareData, filters);

      const resultEl = document.getElementById('filterResult');
      if (resultEl) {
        resultEl.textContent = `筛选结果：共 ${count} 条（总计 ${lowShareData.length} 条）`;
      }
    });
  }

  if (resetLowShareBtn) {
    resetLowShareBtn.addEventListener('click', () => {
      ['filterStatus', 'filterAn', 'filterCat', 'filterOrd8'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      buildLowShareTable('lowShareTableBody', lowShareData);
      const resultEl = document.getElementById('filterResult');
      if (resultEl) resultEl.textContent = '';
    });
  }

  // 四三累计筛选
  const cum43FilterBtn = document.getElementById('filterCum43Btn');
  const resetCum43Btn = document.getElementById('resetCum43Btn');

  if (cum43FilterBtn) {
    cum43FilterBtn.addEventListener('click', () => {
      const filters = {
        status: document.getElementById('filterCumStatus')?.value || '',
        an: document.getElementById('filterCumAn')?.value || '',
        cat: document.getElementById('filterCumCat')?.value || '',
        expand: document.getElementById('filterCumExpand')?.value || '',
        ord8: document.getElementById('filterCumOrd8')?.value || ''
      };
      const count = buildCum43Table('cum43TableBody', cum43Data, filters, PERIOD.cutoffDate);

      const resultDiv = document.getElementById('cum43Result');
      if (resultDiv) {
        resultDiv.textContent = `共 ${count} 条结果（总计 ${cum43Stats.total} 条，已排除周期外上架 ${cum43Stats.filteredOut} 条）`;
      }
    });
  }

  if (resetCum43Btn) {
    resetCum43Btn.addEventListener('click', () => {
      ['filterCumStatus', 'filterCumAn', 'filterCumCat', 'filterCumExpand', 'filterCumOrd8'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      buildCum43Table('cum43TableBody', cum43Data, {}, PERIOD.cutoffDate);
      const resultDiv = document.getElementById('cum43Result');
      if (resultDiv) {
        resultDiv.textContent = `共 ${cum43Stats.total} 条结果（总计 ${cum43Stats.total} 条，已排除周期外上架 ${cum43Stats.filteredOut} 条）`;
      }
    });
  }
}

/**
 * 初始化所有图表
 */
function initCharts() {
  initOverviewCharts(Chart);
  initCatCharts(Chart, catData);
  initAnCharts(Chart, anData);
  initTzCharts(Chart, tzData);
}

/**
 * 初始化所有表格
 */
function initTables() {
  buildCatTable('catTableBody', catData);
  buildAnTable('anTableBody', anData);
  buildLowShareTable('lowShareTableBody', lowShareData);
  buildCum43Table('cum43TableBody', cum43Data, {}, PERIOD.cutoffDate);
}

/**
 * 页面初始化
 */
window.onload = function() {
  // 初始化表格
  initTables();

  // 初始化图表
  initCharts();

  // 初始化筛选
  initFilters();

  // 绑定导航事件
  window.showSection = showSection;

  // 初始化默认显示
  showSection('overview');
};
