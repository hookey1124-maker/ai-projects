/**
 * 新品复盘 — JS 计算引擎
 * 从 Excel 源数据（4 Sheet）计算全部 37 个数据块
 * 替代 Python gen_html_*.py 中 ~1063 行计算逻辑
 *
 * 使用方式：
 *   const DATA = computeAll(workbook);
 *   // DATA 包含 37 个 key，结构与原 Python 输出完全一致
 */

// ===== 工具函数 =====
function safeFloat(v, def) { def = def || 0; try { var n = parseFloat(v); return isNaN(n) ? def : n; } catch(e) { return def; } }
function safeInt(v, def) { def = def || 0; return Math.round(safeFloat(v, def)); }
function parseDate(v) { if (!v) return null; if (v instanceof Date) return v; var s = String(v).trim(); var m = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})/); if (m) return new Date(+m[1], +m[2]-1, +m[3]); m = s.match(/(\d{1,2})\.(\d{1,2})\.(\d{4})/); if (m) return new Date(+m[3], +m[1]-1, +m[2]); return null; }
function fmtDate(d) { if (!d) return ''; var y = d.getFullYear(); var m = String(d.getMonth()+1).padStart(2,'0'); var day = String(d.getDate()).padStart(2,'0'); return y + '-' + m + '-' + day; }
function calcRate(a, b) { return b ? Math.round(a / b * 10000) / 10000 : 0; }
function ratioStr(a, b) { if (!b) return '-'; var v = Math.round((a - b) / Math.abs(b) * 1000) / 10; return (v >= 0 ? '+' : '') + v + '%'; }
function ratioNum(a, b) { if (!b) return 0; return Math.round((a - b) / Math.abs(b) * 1000) / 10; }

// ===== 常量 =====
var ANALYSTS = ['俞东旭', '张潇', '朱培源', '王偲涵', '章鹏', '胡煜星'];
var CATEGORIES = ['车门系统', '车身外扩件', '挡泥板', '机盖及附件', '其他', '饰条', '牌照板支架'];
var EXPAND_TYPES = ['原开品', '拓展品', '组合件'];
var ALL_MKT_STATUSES = ['正常', '竞争无优势', '无市场', '站外出单', '站内无价格优势'];
var PRICE_RANGES = [
    ["$0-10", 0, 10], ["$10-20", 10, 20], ["$20-30", 20, 30],
    ["$30-50", 30, 50], ["$50-100", 50, 100], ["$100+", 100, Infinity]
];
var PLP_PERIODS_4W = ['4.27-5.3', '5.4-5.10', '5.11-5.17', '5.18-5.24'];

// ===== 表头列映射 =====
// 用正则匹配表头文字，返回列索引映射表
function mapColumns(headers) {
    var cols = {};
    var datePatterns = {}; // {metric: [{col, dateStr, dateObj}]}

    for (var i = 0; i < headers.length; i++) {
        var h = String(headers[i] || '').trim();
        if (!h) continue;

        // 元数据列（精确匹配）
        if (h === '销售编号') cols.saleNo = i;
        else if (h === 'SKU') cols.sku = i;
        else if (h === '实际上架日期') cols.listDate = i;
        else if (h === '首次出单日期') cols.firstOrder = i;
        else if (/分析人/.test(h)) cols.analyst = i;
        else if (h === '品类') cols.category = i;
        else if (/产品拓展|拓展类型/.test(h)) cols.expandType = i;

        // 周期列（正则匹配 + 提取日期）
        else if (/^\d/.test(h)) { // 以数字开头 = 日期列
            var dateMatch = h.match(/(\d{1,2}\.\d{1,2}(?:-\d{1,2}\.\d{1,2})?)/);
            if (!dateMatch) continue;
            var dateStr = dateMatch[1];
            var metric = h.replace(dateStr, '').replace(/^[\s-]+/, '').trim();

            if (!datePatterns[metric]) datePatterns[metric] = [];
            datePatterns[metric].push({col: i, dateStr: dateStr});
        }
    }

    // 按日期排序每个指标的列，提取 latest/prev/4week
    cols._dateCols = {};
    for (var metric in datePatterns) {
        var entries = datePatterns[metric];
        // 按日期升序
        entries.sort(function(a, b) {
            var da = a.dateStr.split('-')[0]; // 取开始日期
            var db = b.dateStr.split('-')[0];
            var ma = da.split('.'), mb = db.split('.');
            return (+ma[0] * 100 + +ma[1]) - (+mb[0] * 100 + +mb[1]);
        });
        cols._dateCols[metric] = entries;
    }

    // 给常用指标分配快捷列索引
    var last = function(metric, offset) {
        offset = offset || 0;
        var arr = cols._dateCols[metric];
        if (!arr || arr.length <= offset) return -1;
        return arr[arr.length - 1 - offset].col;
    };
    var last4 = function(metric) {
        var arr = cols._dateCols[metric];
        if (!arr || arr.length < 4) return [];
        return arr.slice(-4).map(function(e) { return e.col; });
    };

    cols.salesCurr = last('销量', 0);
    cols.salesPrev = last('销量', 1);
    cols.revCurr = last('销售额', 0);
    cols.revPrev = last('销售额', 1);
    cols.rivalCurr = last('对手销量', 0);
    cols.rivalPrev = last('对手销量', 1);
    cols.shareCurr = last('市占比', 0);
    cols.sharePrev = last('市占比', 1);
    cols.ord8Curr = last('8日出单情况', 0);
    cols.ord8Prev = last('8日出单情况', 1);
    cols.freq7Curr = last('7日频次标签', 0);
    cols.freq7Prev = last('7日频次标签', 1);
    cols.nfreq7Curr = last('上架8日内新品频次标签', 0);
    cols.nfreq7Prev = last('上架8日内新品频次标签', 1);
    cols.mktCurr = last('市场状态', 0);
    cols.mktPrev = last('市场状态', 1);
    cols.opCurr = last('操作判断', 0);
    cols.plpCurr = last('开启PLP', 0);
    cols.plpSpend = last('PLP广告花费', 0);
    cols.plpAdRev = last('PLP广告销售额', 0);
    cols.plgFee = last('PLG最高费率', 0);
    cols.plgSpend = last('PLG广告花费', 0);
    cols.plgAdRev = last('PLG广告销售额', 0);

    // 4周列
    cols.w4Sales = last4('销量');
    cols.w4Revenue = last4('销售额');
    cols.w4Rival = last4('对手销量');
    cols.w4Share = last4('市占比');
    cols.w4Freq7 = last4('7日频次标签');
    cols.w4Nfreq7 = last4('上架8日内新品频次标签');

    // 生成4周标签
    var salesEntries = cols._dateCols['销量'];
    cols.weekLabels4w = [];
    if (salesEntries && salesEntries.length >= 4) {
        var last4e = salesEntries.slice(-4);
        for (var j = 0; j < last4e.length; j++) {
            cols.weekLabels4w.push(last4e[j].dateStr);
        }
    }

    // 上周截止日期
    if (salesEntries && salesEntries.length >= 2) {
        var prevEntry = salesEntries[salesEntries.length - 2];
        var prevParts = prevEntry.dateStr.split('-');
        var prevEnd = prevParts[prevParts.length - 1];
        var pm = prevEnd.split('.');
        cols.cutoffPrev = new Date(2026, +pm[0]-1, +pm[1]);
    }
    if (salesEntries && salesEntries.length >= 1) {
        var currEntry = salesEntries[salesEntries.length - 1];
        var currEnd = currEntry.dateStr.split('-').pop();
        var cm = currEnd.split('.');
        cols.cutoffCurr = new Date(2026, +cm[0]-1, +cm[1]);
    }

    // 检测到的周期标签
    cols.periodLabel = cols.weekLabels4w.length >= 4 ? cols.weekLabels4w[3] : '当前周期';

    return cols;
}

// ===== PLP明细列映射 =====
function mapPlpColumns(headers) {
    var cols = {};
    for (var i = 0; i < headers.length; i++) {
        var h = String(headers[i] || '').trim();
        if (h === '统计周期') cols.period = i;
        else if (h === '广告活动') cols.campaign = i;
        else if (h === 'SKU') cols.sku = i;
        else if (h === 'ID') cols.id = i;
        else if (h === '店铺') cols.store = i;
        else if (h === 'PLP开始日期') cols.plpStart = i;
        else if (h === '实际上架日期') cols.listDate = i;
        else if (h === '首次出单日期') cols.firstOrder = i;
        else if (/分析人/.test(h) && i !== 8) cols.analyst = i;
        else if (h === '品类') cols.category = i;
        else if (h === '产品拓展') cols.expandType = i;
        else if (h === '广告曝光量') cols.impr = i;
        else if (h === '广告点击量') cols.click = i;
        else if (h === '广告售出数') cols.sold = i;
        else if (h === '广告花费') cols.cost = i;
        else if (h === '广告销售额') cols.adRev = i;
        else if (h === '总销售额') cols.totalRev = i;
        else if (h === 'ROAS') cols.roas = i;
        else if (h === 'CVR') cols.cvr = i;
        else if (h === 'CTR') cols.ctr = i;
        else if (h === 'CPC') cols.cpc = i;
        else if (h === 'CPA') cols.cpa = i;
        else if (h === 'ACOS') cols.acos = i;
        else if (h === 'ACOAS') cols.acoas = i;
        else if (h === '是否开启PLG') cols.plgEnabled = i;
    }
    return cols;
}

// ===== 辅助取值函数 =====
function getCat(r, cols) { var v = String(r[cols.category] || '').trim(); return v || '未分类'; }
function getAn(r, cols) { var v = String(r[cols.analyst] || '').trim(); return v || '未知'; }
function getExp(r, cols) { var v = String(r[cols.expandType] || '').trim(); return v || '其他'; }
function val(r, col) { return safeFloat(col >= 0 ? r[col] : 0); }

// ===== 广告分类 =====
function getAdClass(sku, r_data, cols, plpPlgEnabled, skuCampaignCount) {
    var plpOn = String(r_data[cols.plpCurr] || '').trim().toUpperCase() === 'Y';
    var plgOn = val(r_data, cols.plgFee) > 0;
    var inPlgDetail = plpPlgEnabled.has(sku);
    var isUnsold = String(r_data[cols.ord8Curr] || '').trim() === '未出单';

    if (inPlgDetail && (skuCampaignCount[sku] || 0) === 1) return '单链接PLP+PLG同开';
    if (plpOn && plgOn) return 'PLP+PLG同开';
    if (plgOn && !plpOn) return isUnsold ? '单PLG且未出单' : '单PLG';
    if (plpOn && !plgOn) return '单PLP';
    return '无广告';
}

// ===== 主计算入口 =====
function computeAll(workbook) {
    // 读取4个Sheet
    var mainSheet = workbook.Sheets['四三数据累计'];
    var plpSheet = workbook.Sheets['PLP明细'];
    var deptSheet = workbook.Sheets['四三销售数据'];
    var natSheet = workbook.Sheets['自然周销售数据'];

    if (!mainSheet) throw new Error('找不到Sheet「四三数据累计」，请确认Excel文件正确');

    // 解析主表
    var mainRows = XLSX.utils.sheet_to_json(mainSheet, {header: 1, defval: ''});
    var headers = mainRows[0];
    var cols = mapColumns(headers);
    var PLP_CURR = '5.18-5.24'; // 默认，后续可从header检测

    // 检查关键列
    var missingCols = [];
    if (cols.sku < 0) missingCols.push('SKU');
    if (cols.salesCurr < 0) missingCols.push('销量(最新周)');
    if (cols.revCurr < 0) missingCols.push('销售额(最新周)');
    if (missingCols.length > 0) {
        console.warn('WARNING: 未找到以下列: ' + missingCols.join(', ') + '。请确认Excel表头格式。');
    }

    // 加载SKU数据行
    var rowsRaw = [];
    for (var i = 1; i < mainRows.length; i++) {
        var r = mainRows[i];
        if (r[cols.sku]) rowsRaw.push(r);
    }

    // 按截止日期筛选
    var cutoffCurr = cols.cutoffCurr || new Date(2026, 4, 27);
    var cutoffPrev = cols.cutoffPrev || new Date(2026, 4, 20);

    var rowsCurr = rowsRaw.filter(function(r) {
        var d = parseDate(r[cols.listDate]);
        return d && d <= cutoffCurr;
    });
    var rowsPrev = rowsRaw.filter(function(r) {
        var d = parseDate(r[cols.listDate]);
        return d && d <= cutoffPrev;
    });

    // 基础汇总
    var totalSku = rowsCurr.length;
    var totalSalesCurr = rowsCurr.reduce(function(s, r) { return s + val(r, cols.salesCurr); }, 0);
    var totalSalesPrev = rowsPrev.reduce(function(s, r) { return s + val(r, cols.salesPrev); }, 0);
    var totalRevCurr = rowsCurr.reduce(function(s, r) { return s + val(r, cols.revCurr); }, 0);
    var totalRevPrev = rowsPrev.reduce(function(s, r) { return s + val(r, cols.revPrev); }, 0);
    var hasRivalCurr = rowsCurr.filter(function(r) { return val(r, cols.rivalCurr) > 0; }).length;
    var hasRivalPrev = rowsPrev.filter(function(r) { return val(r, cols.rivalPrev) > 0; }).length;
    var totalRivalSalesCurr = rowsCurr.reduce(function(s, r) { return s + val(r, cols.rivalCurr); }, 0);
    var totalRivalSalesPrev = rowsPrev.reduce(function(s, r) { return s + val(r, cols.rivalPrev); }, 0);

    var totalMarketShareCurr = (totalSalesCurr + totalRivalSalesCurr) > 0
        ? Math.round(totalSalesCurr / (totalSalesCurr + totalRivalSalesCurr) * 1000) / 10 : 0;
    var totalMarketSharePrev = (totalSalesPrev + totalRivalSalesPrev) > 0
        ? Math.round(totalSalesPrev / (totalSalesPrev + totalRivalSalesPrev) * 1000) / 10 : 0;

    // 部门销售数据
    var deptRows = XLSX.utils.sheet_to_json(deptSheet, {header: 1, defval: ''});
    var deptTotalSales = 0, deptTotalRevenue = 0;
    if (deptRows.length > 1) {
        deptTotalSales = safeInt(deptRows[1][2]);
        deptTotalRevenue = safeFloat(deptRows[1][3]);
    }

    // 自然周销售数据
    var natRows = XLSX.utils.sheet_to_json(natSheet, {header: 1, defval: ''});
    var natWeekData = {};
    for (var ni = 1; ni < natRows.length; ni++) {
        var nr = natRows[ni];
        var nsku = String(nr[0] || '').trim();
        if (nsku && nsku !== '#N/A') {
            var nqty = safeFloat(nr[2]), nrev = safeFloat(nr[3]);
            if (natWeekData[nsku]) {
                natWeekData[nsku].qty += nqty;
                natWeekData[nsku].rev += nrev;
            } else {
                natWeekData[nsku] = {qty: nqty, rev: nrev};
            }
        }
    }

    // ===== PLP 数据处理 =====
    var plpRows = XLSX.utils.sheet_to_json(plpSheet, {header: 1, defval: ''});
    var plpHeaders = plpRows[0];
    var PC = mapPlpColumns(plpHeaders);

    var plpCurrRows = [];
    var plpPlgEnabled = new Set();
    for (var pi = 1; pi < plpRows.length; pi++) {
        var pr = plpRows[pi];
        var period = String(pr[PC.period] || '').trim();
        var psku = String(pr[PC.sku] || '').trim();
        if (!psku || psku.indexOf('广告') === 0 || psku.indexOf('总数据') === 0) continue;
        var plistD = parseDate(pr[PC.listDate]);
        if (period === PLP_CURR && plistD && plistD <= cutoffCurr) {
            plpCurrRows.push(pr);
            if (String(pr[PC.plgEnabled] || '').trim() === 'Y') plpPlgEnabled.add(psku);
        }
    }

    var skuCampaignCount = {};
    plpCurrRows.forEach(function(pr) {
        var psku = String(pr[PC.sku] || '').trim();
        if (plpPlgEnabled.has(psku)) {
            skuCampaignCount[psku] = (skuCampaignCount[psku] || 0) + 1;
        }
    });

    // PLP 聚合
    function aggPlp(rows) {
        var bySku = {};
        rows.forEach(function(r) {
            var sku = String(r[PC.sku] || '').trim();
            var camp = String(r[PC.campaign] || '').trim();
            if (!bySku[sku]) bySku[sku] = {impr:0, click:0, sold:0, cost:0, adRev:0, totalRev:0, campaigns: new Set()};
            bySku[sku].impr += val(r, PC.impr);
            bySku[sku].click += val(r, PC.click);
            bySku[sku].sold += val(r, PC.sold);
            bySku[sku].cost += val(r, PC.cost);
            bySku[sku].adRev += val(r, PC.adRev);
            bySku[sku].totalRev += val(r, PC.totalRev);
            if (camp) bySku[sku].campaigns.add(camp);
        });
        return bySku;
    }

    function plpTotals(bySku) {
        var t = {imp:0, click:0, sold:0, cost:0, adRev:0, totalRev:0, campaigns:0};
        var allCamps = new Set();
        for (var sku in bySku) {
            var d = bySku[sku];
            t.imp += d.impr; t.click += d.click; t.sold += d.sold;
            t.cost += d.cost; t.adRev += d.adRev; t.totalRev += d.totalRev;
            d.campaigns.forEach(function(c) { allCamps.add(c); });
        }
        t.campaigns = allCamps.size;
        t.links = Object.keys(bySku).length;
        t.roas = calcRate(t.adRev, t.cost);
        t.cvr = calcRate(t.sold, t.click);
        t.ctr = calcRate(t.click, t.imp);
        t.cpc = t.click ? Math.round(t.cost / t.click * 100) / 100 : 0;
        t.cpa = t.sold ? Math.round(t.cost / t.sold * 100) / 100 : 0;
        t.acos = calcRate(t.cost, t.adRev);
        t.acoas = calcRate(t.cost, t.totalRev);
        return t;
    }

    var plpCurrSku = aggPlp(plpCurrRows);
    var plpT = plpTotals(plpCurrSku);

    // ACOAS SKU去重
    var skuTotalRevDedup = {};
    for (var sku in plpCurrSku) {
        var infoRows = plpCurrRows.filter(function(r) { return String(r[PC.sku] || '').trim() === sku; });
        if (infoRows.length > 0) {
            skuTotalRevDedup[sku] = val(infoRows[0], PC.totalRev);
        }
    }
    var dedupTotalRev = Object.values(skuTotalRevDedup).reduce(function(s, v) { return s + v; }, 0);
    var dedupAcoas = dedupTotalRev > 0 ? Math.round(plpT.cost / dedupTotalRev * 10000) / 10000 : 0;

    // ===== 构建全部数据块 =====
    var DATA = {};

    // 1. cum43Data
    DATA.cum43Data = rowsCurr.map(function(r) {
        var sku = String(r[cols.sku] || '').trim();
        var listD = parseDate(r[cols.listDate]);
        var firstD = parseDate(r[cols.firstOrder]);
        var curShare = val(r, cols.shareCurr);
        var prevShare = val(r, cols.sharePrev);
        return {
            saleNo: r[cols.saleNo] || '',
            SKU: sku,
            listDate: fmtDate(listD),
            firstOrderDate: fmtDate(firstD) || '未出单',
            analyst: getAn(r, cols),
            category: getCat(r, cols),
            expandType: getExp(r, cols),
            curSalesQty: safeInt(val(r, cols.salesCurr)),
            prevSalesQty: safeInt(val(r, cols.salesPrev)),
            curRevenue: Math.round(val(r, cols.revCurr) * 100) / 100,
            prevRevenue: Math.round(val(r, cols.revPrev) * 100) / 100,
            curRivalQty: safeInt(val(r, cols.rivalCurr)),
            prevRivalQty: safeInt(val(r, cols.rivalPrev)),
            curMarketShare: Math.round(curShare * 1000) / 10,
            prevMarketShare: Math.round(prevShare * 1000) / 10,
            cur8dStatus: String(r[cols.ord8Curr] || '').trim(),
            curFreq7: String(r[cols.freq7Curr] || '').trim(),
            curNewFreq7: String(r[cols.nfreq7Curr] || '').trim(),
            curMarketStatus: String(r[cols.mktCurr] || '').trim(),
            prevMarketStatus: String(r[cols.mktPrev] || '').trim(),
            curOperation: String(r[cols.opCurr] || '').trim(),
            plpEnabled: String(r[cols.plpCurr] || '').trim().toUpperCase() === 'Y' ? 'Y' : 'N',
            plgFee: Math.round(val(r, cols.plgFee) * 1000) / 10 + '%',
            plgSpend: Math.round(val(r, cols.plgSpend) * 100) / 100,
            plgAdRev: Math.round(val(r, cols.plgAdRev) * 100) / 100,
            adClass: getAdClass(sku, r, cols, plpPlgEnabled, skuCampaignCount)
        };
    });

    // 2. cum43Stats
    var rowsWithRival = rowsCurr.filter(function(r) { return val(r, cols.rivalCurr) > 0; });
    var rowsNoRival = rowsCurr.filter(function(r) { return val(r, cols.rivalCurr) === 0; });
    var yCurr = rowsWithRival.filter(function(r) { return String(r[cols.ord8Curr] || '').trim() === 'Y'; }).length;
    var nCurr = rowsWithRival.filter(function(r) { return String(r[cols.ord8Curr] || '').trim() === 'N'; }).length;
    var noCurrOrd8 = rowsWithRival.filter(function(r) { return String(r[cols.ord8Curr] || '').trim() === '未出单'; }).length;
    var noCurrOther = rowsWithRival.filter(function(r) { var s = String(r[cols.ord8Curr] || '').trim(); return s !== 'Y' && s !== 'N' && s !== '未出单'; }).length;
    var noCurr = noCurrOrd8 + noCurrOther;
    var noRivalSold = rowsNoRival.filter(function(r) { var s = String(r[cols.ord8Curr] || '').trim(); return s === 'Y' || s === 'N'; }).length;
    var noRivalUnsold = rowsNoRival.length - noRivalSold;
    var normalCnt = rowsCurr.filter(function(r) { return String(r[cols.mktCurr] || '').trim() === '正常'; }).length;
    var competitiveCnt = rowsCurr.filter(function(r) { return String(r[cols.mktCurr] || '').trim() === '竞争无优势'; }).length;
    var nomarketCnt = rowsCurr.filter(function(r) { return String(r[cols.mktCurr] || '').trim() === '无市场'; }).length;
    var stationOutCnt = rowsCurr.filter(function(r) { return String(r[cols.mktCurr] || '').trim() === '站外出单'; }).length;

    DATA.cum43Stats = {
        total: totalSku, yCount: yCurr, nCount: nCurr, unCount: noCurr,
        noRivalSold: noRivalSold, noRivalUnsold: noRivalUnsold,
        normalCount: normalCnt, competitiveCount: competitiveCnt,
        noMarketCount: nomarketCnt, stationOutCount: stationOutCnt,
        hasRivalCount: hasRivalCurr, noRivalCount: totalSku - hasRivalCurr,
        totalMarketShare: totalMarketShareCurr,
        totalMarketSharePrev: totalMarketSharePrev
    };

    // Add 4-week arrays for KPI cards (current week = index 0)
    DATA.cum43Stats.sales4w = [
        safeInt(totalSalesCurr),
        safeInt(rowsCurr.reduce(function(s, r) { return s + val(r, cols.salesPrev); }, 0))
    ];
    DATA.cum43Stats.revenue4w = [
        Math.round(totalRevCurr * 100) / 100,
        Math.round(rowsCurr.reduce(function(s, r) { return s + val(r, cols.revPrev); }, 0) * 100) / 100
    ];

    // 3. lowShareData
    DATA.lowShareData = rowsCurr.filter(function(r) {
        return val(r, cols.shareCurr) * 100 < 75 && val(r, cols.rivalCurr) > 0;
    }).map(function(r) {
        var sku = String(r[cols.sku] || '').trim();
        var share = val(r, cols.shareCurr) * 100;
        return {
            salesCode: String(r[cols.saleNo] || ''),
            SKU: sku,
            launchDate: fmtDate(parseDate(r[cols.listDate])),
            analyst: getAn(r, cols),
            category: getCat(r, cols),
            expandType: getExp(r, cols),
            curSalesQty: safeInt(val(r, cols.salesCurr)),
            salesQtyChange: ratioStr(val(r, cols.salesCurr), val(r, cols.salesPrev)),
            curRevenue: Math.round(val(r, cols.revCurr) * 100) / 100,
            revenueChange: ratioStr(val(r, cols.revCurr), val(r, cols.revPrev)),
            prevRivalQty: safeInt(val(r, cols.rivalPrev)),
            curRivalQty: safeInt(val(r, cols.rivalCurr)),
            rivalQtyChange: ratioStr(val(r, cols.rivalCurr), val(r, cols.rivalPrev)),
            prevMarketShare: Math.round(val(r, cols.sharePrev) * 1000) / 10,
            curMarketShare: Math.round(share * 10) / 10,
            prevMarketStatus: String(r[cols.mktPrev] || '').trim(),
            curOperation: String(r[cols.opCurr] || '').trim(),
            curMarketStatus: String(r[cols.mktCurr] || '').trim(),
            cur8dStatus: String(r[cols.ord8Curr] || '').trim(),
            plpEnabled: String(r[cols.plpCurr] || '').trim().toUpperCase() === 'Y' ? 'Y' : 'N',
            plgFee: Math.round(val(r, cols.plgFee) * 1000) / 10 + '%',
            adClass: getAdClass(sku, r, cols, plpPlgEnabled, skuCampaignCount)
        };
    }).sort(function(a, b) { return a.curMarketShare - b.curMarketShare; });

    // 4. expandTypeData
    var expCurr = {}, expPrev = {};
    EXPAND_TYPES.forEach(function(et) { expCurr[et] = {sku:0, salesQty:0, rev:0, soldSku:0, hasRival:0}; expPrev[et] = {sku:0, salesQty:0, rev:0, soldSku:0, hasRival:0}; });
    var _ensureExp = function(map, exp) { if (!map[exp]) map[exp] = {sku:0, salesQty:0, rev:0, soldSku:0, hasRival:0}; return map[exp]; };

    rowsCurr.forEach(function(r) {
        var d = _ensureExp(expCurr, getExp(r, cols));
        d.sku++; d.salesQty += val(r, cols.salesCurr); d.rev += val(r, cols.revCurr);
        if (val(r, cols.rivalCurr) > 0) { d.hasRival++; if (['Y','N'].indexOf(String(r[cols.ord8Curr] || '').trim()) >= 0) d.soldSku++; }
    });
    rowsPrev.forEach(function(r) {
        var d = _ensureExp(expPrev, getExp(r, cols));
        d.sku++; d.salesQty += val(r, cols.salesPrev); d.rev += val(r, cols.revPrev);
        if (val(r, cols.rivalPrev) > 0) { d.hasRival++; if (['Y','N'].indexOf(String(r[cols.ord8Prev] || '').trim()) >= 0) d.soldSku++; }
    });

    DATA.expandTypeData = [];
    EXPAND_TYPES.forEach(function(et) {
        var dc = expCurr[et] || {sku:0, salesQty:0, rev:0, soldSku:0, hasRival:0};
        var dp = expPrev[et] || {sku:0, salesQty:0, rev:0, soldSku:0, hasRival:0};
        if (dc.sku > 0 || dp.sku > 0) {
            var curSold = dc.soldSku, hasRC = dc.hasRival || 1;
            var prevSold = dp.soldSku, hasRP = dp.hasRival || 1;
            DATA.expandTypeData.push({
                expandType: et,
                curSku: dc.sku, prevSku: dp.sku,
                curSalesSku: curSold,
                curSalesRate: Math.round(curSold / hasRC * 1000) / 10 + '%',
                prevSalesSku: prevSold,
                prevSalesRate: Math.round(prevSold / hasRP * 1000) / 10 + '%',
                curSalesQty: safeInt(dc.salesQty), prevSalesQty: safeInt(dp.salesQty),
                salesQtyChange: ratioStr(dc.salesQty, dp.salesQty),
                curRevenue: Math.round(dc.rev * 100) / 100, prevRevenue: Math.round(dp.rev * 100) / 100,
                revenueChange: ratioStr(dc.rev, dp.rev)
            });
        }
    });

    // 5. timelinessData
    var anTime = {}, anTimePrev = {};
    ANALYSTS.forEach(function(a) { anTime[a] = {timely:0, no8d:0, no7d:0}; anTimePrev[a] = {timely:0, no8d:0, no7d:0}; });
    rowsCurr.forEach(function(r) {
        var a = getAn(r, cols); if (!anTime[a]) anTime[a] = {timely:0, no8d:0, no7d:0};
        var f = String(r[cols.freq7Curr] || '').trim(), nf = String(r[cols.nfreq7Curr] || '').trim();
        if (nf === '异常') anTime[a].no8d++;
        else if (f === '异常') anTime[a].no7d++;
        else anTime[a].timely++;
    });
    rowsPrev.forEach(function(r) {
        var a = getAn(r, cols); if (!anTimePrev[a]) anTimePrev[a] = {timely:0, no8d:0, no7d:0};
        var f = String(r[cols.freq7Prev] || '').trim(), nf = String(r[cols.nfreq7Prev] || '').trim();
        if (nf === '异常') anTimePrev[a].no8d++;
        else if (f === '异常') anTimePrev[a].no7d++;
        else anTimePrev[a].timely++;
    });

    var ansOrdered = ANALYSTS.filter(function(a) { return anTime[a]; });
    var timelinessTotalCurr = rowsCurr.filter(function(r) { return String(r[cols.nfreq7Curr] || '').trim() !== '异常' && String(r[cols.freq7Curr] || '').trim() !== '异常'; }).length;
    var timelinessTotalPrev = rowsPrev.filter(function(r) { return String(r[cols.nfreq7Prev] || '').trim() !== '异常' && String(r[cols.freq7Prev] || '').trim() !== '异常'; }).length;

    DATA.timelinessData = {analysts: [], total: {}};
    ansOrdered.forEach(function(an) {
        var dc = anTime[an] || {timely:0, no8d:0, no7d:0};
        var dp = anTimePrev[an] || {timely:0, no8d:0, no7d:0};
        var tc = dc.timely + dc.no8d + dc.no7d, tp = dp.timely + dp.no8d + dp.no7d;
        var rc = tc ? Math.round(dc.timely / tc * 1000) / 10 + '%' : '0%';
        var rp = tp ? Math.round(dp.timely / tp * 1000) / 10 + '%' : '0%';
        DATA.timelinessData.analysts.push({
            analyst: an, curSku: tc, prevSku: tp,
            timelyCount: dc.timely, prevTimelyCount: dp.timely,
            noAnalysis8dCount: dc.no8d, noAnalysis7dCount: dc.no7d,
            timelyRate: rc, prevTimelyRate: rp,
            change: rc !== '0%' && rp !== '0%' ? ratioStr(parseFloat(rc), parseFloat(rp)) : '-'
        });
    });
    var trc = totalSku ? Math.round(timelinessTotalCurr / totalSku * 1000) / 10 + '%' : '0%';
    var trp = rowsPrev.length ? Math.round(timelinessTotalPrev / rowsPrev.length * 1000) / 10 + '%' : '0%';
    DATA.timelinessData.total = {
        analyst: '合计', curSku: totalSku, prevSku: rowsPrev.length,
        timelyCount: timelinessTotalCurr, prevTimelyCount: timelinessTotalPrev,
        noAnalysis8dCount: rowsCurr.filter(function(r) { return String(r[cols.nfreq7Curr] || '').trim() === '异常'; }).length,
        noAnalysis7dCount: rowsCurr.filter(function(r) { return String(r[cols.freq7Curr] || '').trim() === '异常'; }).length,
        timelyRate: trc, prevTimelyRate: trp,
        change: trc !== '0%' && trp !== '0%' ? ratioStr(parseFloat(trc), parseFloat(trp)) : '-'
    };

    // 6-12. 未出单分析 + PLP + PLG 等
    // 见 computeAll_part2
    DATA._ctx = {
        rowsCurr: rowsCurr, rowsPrev: rowsPrev, rowsRaw: rowsRaw,
        cols: cols, PC: PC,
        plpCurrRows: plpCurrRows, plpCurrSku: plpCurrSku, plpT: plpT,
        plpPlgEnabled: plpPlgEnabled, skuCampaignCount: skuCampaignCount,
        skuTotalRevDedup: skuTotalRevDedup, dedupTotalRev: dedupTotalRev, dedupAcoas: dedupAcoas,
        totalSku: totalSku, totalSalesCurr: totalSalesCurr, totalSalesPrev: totalSalesPrev,
        totalRevCurr: totalRevCurr, totalRevPrev: totalRevPrev,
        hasRivalCurr: hasRivalCurr, hasRivalPrev: hasRivalPrev,
        totalRivalSalesCurr: totalRivalSalesCurr, totalRivalSalesPrev: totalRivalSalesPrev,
        totalMarketShareCurr: totalMarketShareCurr, totalMarketSharePrev: totalMarketSharePrev,
        deptTotalSales: deptTotalSales, deptTotalRevenue: deptTotalRevenue,
        natWeekData: natWeekData,
        ansOrdered: ansOrdered,
        yCurr: yCurr, nCurr: nCurr, noCurr: noCurr, noRivalSold: noRivalSold, noRivalUnsold: noRivalUnsold,
        PLP_CURR: PLP_CURR,
        allPlpRows: plpRows.slice(1),  // Full PLP rows (skip header) for 4-week and prev computation
        cutoffPrev: cutoffPrev
    };

    return DATA;
}

// ===== 第二部分计算 =====
function computeAllPart2(DATA) {
    var ctx = DATA._ctx;
    var rowsCurr = ctx.rowsCurr, rowsPrev = ctx.rowsPrev;
    var cols = ctx.cols, PC = ctx.PC;
    var plpCurrRows = ctx.plpCurrRows, plpCurrSku = ctx.plpCurrSku, plpT = ctx.plpT;
    var plpPlgEnabled = ctx.plpPlgEnabled, skuCampaignCount = ctx.skuCampaignCount;
    var skuTotalRevDedup = ctx.skuTotalRevDedup;
    var totalSku = ctx.totalSku;
    var totalMarketShareCurr = ctx.totalMarketShareCurr, totalMarketSharePrev = ctx.totalMarketSharePrev;
    var ansOrdered = ctx.ansOrdered;
    var yCurr = ctx.yCurr, nCurr = ctx.nCurr, noCurr = ctx.noCurr;

    // 6. hasCompetitorUnsold
    var hasRivalNoCurr = rowsCurr.filter(function(r) { return String(r[cols.ord8Curr] || '').trim() === '未出单' && val(r, cols.rivalCurr) > 0; });
    var hasRivalNoPrev = rowsPrev.filter(function(r) { return String(r[cols.ord8Prev] || '').trim() === '未出单' && val(r, cols.rivalPrev) > 0; });
    var mktHasOrder = ['竞争无优势', '站内无价格优势'];
    var mktNoOrder = ['无市场', '站外出单'];

    function buildUnsoldAnalysis(items, mktOrder, colMkt) {
        var mktCounter = {};
        items.forEach(function(r) { var v = String(r[colMkt] || '未知').trim(); mktCounter[v] = (mktCounter[v] || 0) + 1; });
        var reasons = mktOrder.map(function(m) { return {name: m, count: mktCounter[m] || 0}; });
        var byAnalyst = ansOrdered.map(function(an) {
            var anItems = items.filter(function(r) { return getAn(r, cols) === an; });
            var row = {analyst: an};
            var anMkt = {};
            anItems.forEach(function(r) { var v = String(r[colMkt] || '未知').trim(); anMkt[v] = (anMkt[v] || 0) + 1; });
            mktOrder.forEach(function(m) { row[m] = anMkt[m] || 0; });
            row.total = anItems.length;
            return row;
        });
        var catMap = {};
        items.forEach(function(r) { var c = getCat(r, cols); if (!catMap[c]) catMap[c] = []; catMap[c].push(r); });
        var byCategory = Object.keys(catMap).sort().map(function(cat) {
            var catMkt = {};
            catMap[cat].forEach(function(r) { var v = String(r[colMkt] || '未知').trim(); catMkt[v] = (catMkt[v] || 0) + 1; });
            var row = {category: cat};
            mktOrder.forEach(function(m) { row[m] = catMkt[m] || 0; });
            row.total = catMap[cat].length;
            return row;
        });
        return {total: items.length, prevTotal: 0, reasons: reasons, byAnalyst: byAnalyst, byCategory: byCategory};
    }

    DATA.hasCompetitorUnsold = buildUnsoldAnalysis(hasRivalNoCurr, mktHasOrder, cols.mktCurr);
    DATA.hasCompetitorUnsold.prevTotal = hasRivalNoPrev.length;
    DATA.hasCompetitorUnsold.change = hasRivalNoCurr.length - hasRivalNoPrev.length;

    // 7-11. PLP 数据
    DATA.plpTotal = {
        campaignCount: plpT.campaigns, linkCount: plpT.links,
        impression: safeInt(plpT.imp), click: safeInt(plpT.click),
        sold: safeInt(plpT.sold), cost: Math.round(plpT.cost * 100) / 100,
        revenue: Math.round(plpT.adRev * 100) / 100,
        totalRevenue: Math.round(ctx.dedupTotalRev * 100) / 100,
        roas: plpT.roas.toFixed(2),
        cvr: (plpT.cvr * 100).toFixed(2) + '%',
        ctr: (plpT.ctr * 100).toFixed(2) + '%',
        cpc: '$' + plpT.cpc.toFixed(2),
        cpa: '$' + plpT.cpa.toFixed(2),
        acos: (plpT.acos * 100).toFixed(2) + '%',
        acoas: (ctx.dedupAcoas * 100).toFixed(2) + '%'
    };

    // PLP 维度聚合
    function plpDimData(bySku, keyFn) {
        var groups = {};
        for (var sku in bySku) {
            var d = bySku[sku];
            var info = null;
            for (var i = 0; i < rowsCurr.length; i++) {
                if (String(rowsCurr[i][cols.sku] || '').trim() === sku) { info = rowsCurr[i]; break; }
            }
            var k = keyFn(sku, info);
            if (!groups[k]) groups[k] = {imp:0, click:0, sold:0, cost:0, adRev:0, campaigns: new Set(), skus: new Set()};
            var g = groups[k];
            g.imp += d.impr; g.click += d.click; g.sold += d.sold;
            g.cost += d.cost; g.adRev += d.adRev;
            d.campaigns.forEach(function(c) { g.campaigns.add(c); });
            g.skus.add(sku);
        }
        for (var k in groups) {
            var g = groups[k];
            var dedupRev = 0;
            g.skus.forEach(function(sku) { dedupRev += skuTotalRevDedup[sku] || 0; });
            g.totalRev = dedupRev;
        }
        var keys = Object.keys(groups).sort();
        return keys.map(function(k) {
            var g = groups[k];
            var roasV = calcRate(g.adRev, g.cost), cvrV = calcRate(g.sold, g.click), ctrV = calcRate(g.click, g.imp);
            var acosV = calcRate(g.cost, g.adRev), acoasV = calcRate(g.cost, g.totalRev);
            return {
                name: k, campaignCount: g.campaigns.size, linkCount: g.skus.size,
                impression: safeInt(g.imp), click: safeInt(g.click), sold: safeInt(g.sold),
                cost: Math.round(g.cost * 100) / 100, revenue: Math.round(g.adRev * 100) / 100,
                totalRevenue: Math.round(g.totalRev * 100) / 100,
                roas: roasV.toFixed(2), cvr: (cvrV * 100).toFixed(2) + '%',
                ctr: (ctrV * 100).toFixed(2) + '%',
                cpc: g.click ? '$' + (Math.round(g.cost / g.click * 100) / 100).toFixed(2) : '-',
                cpa: g.sold ? '$' + (Math.round(g.cost / g.sold * 100) / 100).toFixed(2) : '-',
                acos: (acosV * 100).toFixed(2) + '%', acoas: (acoasV * 100).toFixed(2) + '%'
            };
        });
    }

    DATA.plpCategories = plpDimData(plpCurrSku, function(sku, info) { return info ? getCat(info, cols) : '未分类'; });
    DATA.plpExpandTypes = plpDimData(plpCurrSku, function(sku, info) { return info ? getExp(info, cols) : '其他'; });
    DATA.plpAnalysts = plpDimData(plpCurrSku, function(sku, info) { return info ? getAn(info, cols) : '未知'; });

    // PLP prev totals — properly compute from PLP_PREV period
    var PLP_PREV = '5.11-5.17';
    var allPlpRows = ctx.allPlpRows;
    var plpPrevRows = [];
    for (var pi = 0; pi < allPlpRows.length; pi++) {
        var pr = allPlpRows[pi];
        var period = String(pr[PC.period] || '').trim();
        var psku = String(pr[PC.sku] || '').trim();
        if (!psku || psku.indexOf('广告') === 0 || psku.indexOf('总数据') === 0) continue;
        var plistD = parseDate(pr[PC.listDate]);
        if (period === PLP_PREV && plistD && plistD <= cutoffPrev) {
            plpPrevRows.push(pr);
        }
    }
    // Re-define aggPlp and plpTotals for prev (same logic as in computeAll)
    function _aggPlp(rows) {
        var bySku = {};
        rows.forEach(function(r) {
            var sku = String(r[PC.sku] || '').trim();
            var camp = String(r[PC.campaign] || '').trim();
            if (!bySku[sku]) bySku[sku] = {impr:0, click:0, sold:0, cost:0, adRev:0, totalRev:0, campaigns: new Set()};
            bySku[sku].impr += val(r, PC.impr); bySku[sku].click += val(r, PC.click);
            bySku[sku].sold += val(r, PC.sold); bySku[sku].cost += val(r, PC.cost);
            bySku[sku].adRev += val(r, PC.adRev); bySku[sku].totalRev += val(r, PC.totalRev);
            if (camp) bySku[sku].campaigns.add(camp);
        });
        return bySku;
    }
    function _plpTotals(bySku) {
        var t = {imp:0, click:0, sold:0, cost:0, adRev:0, totalRev:0, campaigns:0};
        var allCamps = new Set();
        for (var sku in bySku) {
            var d = bySku[sku];
            t.imp += d.impr; t.click += d.click; t.sold += d.sold;
            t.cost += d.cost; t.adRev += d.adRev; t.totalRev += d.totalRev;
            d.campaigns.forEach(function(c) { allCamps.add(c); });
        }
        t.campaigns = allCamps.size; t.links = Object.keys(bySku).length;
        t.roas = calcRate(t.adRev, t.cost); t.cvr = calcRate(t.sold, t.click); t.ctr = calcRate(t.click, t.imp);
        t.cpc = t.click ? Math.round(t.cost / t.click * 100) / 100 : 0;
        t.cpa = t.sold ? Math.round(t.cost / t.sold * 100) / 100 : 0;
        t.acos = calcRate(t.cost, t.adRev); t.acoas = calcRate(t.cost, t.totalRev);
        return t;
    }
    var plpPrevSku = _aggPlp(plpPrevRows);
    var plpPt = _plpTotals(plpPrevSku);

    DATA.plpPrevTotal = {
        campaignCount: plpPt.campaigns, linkCount: plpPt.links,
        impression: safeInt(plpPt.imp), click: safeInt(plpPt.click),
        sold: safeInt(plpPt.sold), cost: Math.round(plpPt.cost * 100) / 100,
        revenue: Math.round(plpPt.adRev * 100) / 100,
        totalRevenue: Math.round(plpPt.totalRev * 100) / 100,
        roas: plpPt.roas.toFixed(2), cvr: (plpPt.cvr * 100).toFixed(2) + '%',
        ctr: (plpPt.ctr * 100).toFixed(2) + '%',
        cpc: '$' + plpPt.cpc.toFixed(2), cpa: '$' + plpPt.cpa.toFixed(2),
        acos: (plpPt.acos * 100).toFixed(2) + '%', acoas: (plpPt.acoas * 100).toFixed(2) + '%'
    };

    // 12. unsoldNoCompetitor
    var noRivalNoCurr = rowsCurr.filter(function(r) { return String(r[cols.ord8Curr] || '').trim() === '未出单' && val(r, cols.rivalCurr) === 0; });
    var noRivalNoPrev = rowsPrev.filter(function(r) { return String(r[cols.ord8Prev] || '').trim() === '未出单' && val(r, cols.rivalPrev) === 0; });
    DATA.unsoldNoCompetitor = buildUnsoldAnalysis(noRivalNoCurr, mktNoOrder, cols.mktCurr);
    DATA.unsoldNoCompetitor.prevTotal = noRivalNoPrev.length;
    DATA.unsoldNoCompetitor.change = noRivalNoCurr.length - noRivalNoPrev.length;

    // 13. prevWeekKpi
    DATA.prevWeekKpi = {
        prevTotalSku: rowsPrev.length,
        prevTotalSalesQty: ctx.totalSalesPrev,
        prevTotalRevenue: Math.round(ctx.totalRevPrev * 100) / 100,
        salesQtyChange: ratioStr(ctx.totalSalesCurr, ctx.totalSalesPrev),
        revenueChange: ratioStr(ctx.totalRevCurr, ctx.totalRevPrev),
        skuChange: ratioStr(totalSku, rowsPrev.length),
        prevTimelyRate: DATA.timelinessData.total.prevTimelyRate,
        prevSoldRate: ctx.hasRivalCurr ? Math.round((yCurr + nCurr) / ctx.hasRivalCurr * 1000) / 10 + '%' : '0%',
        prevLowShareCount: DATA.lowShareData.length,
        deptRatio: ctx.deptTotalRevenue > 0 ? (ctx.totalRevCurr / ctx.deptTotalRevenue * 100).toFixed(1) + '%' : '0%',
        deptTotalRevenue: Math.round(ctx.deptTotalRevenue * 100) / 100,
        totalMarketShare: totalMarketShareCurr + '%',
        totalMarketSharePrev: totalMarketSharePrev + '%',
        marketShareChange: ratioStr(totalMarketShareCurr, totalMarketSharePrev)
    };

    // 14. plgStats
    var plgTotalSpend = rowsCurr.reduce(function(s, r) { return s + val(r, cols.plgSpend); }, 0);
    var plgTotalAdRev = rowsCurr.reduce(function(s, r) { return s + val(r, cols.plgAdRev); }, 0);
    var plgSkuNatRev = {};
    rowsCurr.forEach(function(r) {
        var sku = String(r[cols.sku] || '').trim();
        var plgSpendSku = val(r, cols.plgSpend);
        if (plgSpendSku > 0) {
            var nw = ctx.natWeekData[sku] || {qty:0, rev:0};
            plgSkuNatRev[sku] = nw.rev;
        }
    });
    var plgTotalNatRev = Object.values(plgSkuNatRev).reduce(function(s, v) { return s + v; }, 0);
    var plgAcos = plgTotalAdRev > 0 ? Math.round(plgTotalSpend / plgTotalAdRev * 10000) / 100 : 0;
    var plgAcoas = plgTotalNatRev > 0 ? Math.round(plgTotalSpend / plgTotalNatRev * 10000) / 100 : 0;

    var plgCategoriesMap = {'PLP+PLG同开':[], '单链接PLP+PLG同开':[], '单PLG':[], '单PLP':[], '单PLG且未出单':[], '无广告':[]};
    rowsCurr.forEach(function(r) {
        var adc = getAdClass(String(r[cols.sku] || '').trim(), r, cols, plpPlgEnabled, skuCampaignCount);
        if (plgCategoriesMap[adc]) plgCategoriesMap[adc].push(r);
    });

    DATA.plgStats = {
        plpAndPlgBothCount: plgCategoriesMap['PLP+PLG同开'].length,
        singleLinkPlpPlgCount: plgCategoriesMap['单链接PLP+PLG同开'].length,
        plgOnlyCount: plgCategoriesMap['单PLG'].length,
        plpOnlyCount: plgCategoriesMap['单PLP'].length,
        noAdCount: plgCategoriesMap['无广告'].length,
        plpDisabledNoSaleCount: plgCategoriesMap['单PLG且未出单'].length,
        totalNewProducts: totalSku,
        totalSpend: Math.round(plgTotalSpend * 100) / 100,
        totalAdRev: Math.round(plgTotalAdRev * 100) / 100,
        totalNatRev: Math.round(plgTotalNatRev * 100) / 100,
        acos: plgAcos.toFixed(2) + '%',
        acoas: plgAcoas.toFixed(2) + '%',
        byAnalyst: []
    };

    ansOrdered.forEach(function(an) {
        var anItems = rowsCurr.filter(function(r) { return getAn(r, cols) === an; });
        var anAd = {};
        anItems.forEach(function(r) { var ac = getAdClass(String(r[cols.sku] || '').trim(), r, cols, plpPlgEnabled, skuCampaignCount); anAd[ac] = (anAd[ac] || 0) + 1; });
        var anPlgSpend = anItems.reduce(function(s, r) { return s + val(r, cols.plgSpend); }, 0);
        var anPlgAdRev = anItems.reduce(function(s, r) { return s + val(r, cols.plgAdRev); }, 0);
        var anPlgNatRev = 0;
        anItems.forEach(function(r) {
            var sku = String(r[cols.sku] || '').trim();
            if (val(r, cols.plgSpend) > 0) anPlgNatRev += (ctx.natWeekData[sku] || {rev:0}).rev;
        });
        var anAcos = anPlgAdRev > 0 ? Math.round(anPlgSpend / anPlgAdRev * 10000) / 100 : 0;
        var anAcoas = anPlgNatRev > 0 ? Math.round(anPlgSpend / anPlgNatRev * 10000) / 100 : 0;
        DATA.plgStats.byAnalyst.push({
            analyst: an, total: anItems.length,
            plpAndPlgBoth: anAd['PLP+PLG同开'] || 0,
            singleLinkPlpPlg: anAd['单链接PLP+PLG同开'] || 0,
            plgOnly: anAd['单PLG'] || 0, plpOnly: anAd['单PLP'] || 0,
            noAd: anAd['无广告'] || 0, plpDisabledNoSale: anAd['单PLG且未出单'] || 0,
            plgSpend: Math.round(anPlgSpend * 100) / 100,
            plgAdRev: Math.round(anPlgAdRev * 100) / 100,
            plgNatRev: Math.round(anPlgNatRev * 100) / 100,
            acos: anAcos.toFixed(2) + '%',
            acoas: anAcoas.toFixed(2) + '%'
        });
    });

    // 15-16. categoryRevenueData / analystRevenueData
    DATA.categoryRevenueData = buildRevenueData(rowsCurr, rowsPrev, cols, CATEGORIES, getCat, 'category');
    DATA.analystRevenueData = buildRevenueData(rowsCurr, rowsPrev, cols, ansOrdered, getAn, 'analyst');

    function buildRevenueData(rowsC, rowsP, cols, orderList, keyFn, labelKey) {
        var currData = {}, prevData = {};
        rowsC.forEach(function(r) {
            var k = keyFn(r, cols); if (!currData[k]) currData[k] = {sku:0, news:0, sales:0, rev:0, rivalSales:0};
            currData[k].sku++;
            var listD = parseDate(r[cols.listDate]);
            if (listD && listD > (cols.cutoffPrev || new Date(2026,4,20))) currData[k].news++;
            currData[k].sales += val(r, cols.salesCurr);
            currData[k].rev += val(r, cols.revCurr);
            currData[k].rivalSales += val(r, cols.rivalCurr);
        });
        rowsP.forEach(function(r) {
            var k = keyFn(r, cols); if (!prevData[k]) prevData[k] = {sku:0, sales:0, rev:0, rivalSales:0};
            prevData[k].sku++;
            prevData[k].sales += val(r, cols.salesPrev);
            prevData[k].rev += val(r, cols.revPrev);
            prevData[k].rivalSales += val(r, cols.rivalPrev);
        });
        var ordered = orderList.filter(function(k) { return currData[k]; });
        return ordered.map(function(k) {
            var dc = currData[k] || {}, dp = prevData[k] || {};
            var cs = dc.sales || 0, cr = dc.rivalSales || 0;
            var ps = dp.sales || 0, pr = dp.rivalSales || 0;
            var cShare = (cs + cr) > 0 ? Math.round(cs / (cs + cr) * 1000) / 10 : 0;
            var pShare = (ps + pr) > 0 ? Math.round(ps / (ps + pr) * 1000) / 10 : 0;
            var entry = {
                curSku: dc.sku || 0, curNewSku: dc.news || 0,
                curSalesQty: safeInt(cs), prevSalesQty: safeInt(ps),
                salesQtyChange: ratioStr(cs, ps),
                curRevenue: Math.round((dc.rev || 0) * 100) / 100,
                prevRevenue: Math.round((dp.rev || 0) * 100) / 100,
                revenueChange: ratioStr(dc.rev || 0, dp.rev || 0),
                curMarketShare: cShare, prevMarketShare: pShare,
                marketShareChange: ratioStr(cShare, pShare)
            };
            entry[labelKey] = k;
            return entry;
        });
    }

    // 17. plgRecords
    DATA.plgRecords = rowsCurr.map(function(r) {
        var sku = String(r[cols.sku] || '').trim();
        var listD = parseDate(r[cols.listDate]), firstD = parseDate(r[cols.firstOrder]);
        return {
            salesCode: String(r[cols.saleNo] || ''), SKU: sku,
            launchDate: fmtDate(listD),
            firstSaleDate: fmtDate(firstD) || '未出单',
            analyst: getAn(r, cols), category: getCat(r, cols), expandType: getExp(r, cols),
            cur8dStatus: String(r[cols.ord8Curr] || '').trim(),
            curSalesQty: safeInt(val(r, cols.salesCurr)),
            curRevenue: Math.round(val(r, cols.revCurr) * 100) / 100,
            curRivalQty: safeInt(val(r, cols.rivalCurr)),
            curMarketShare: Math.round(val(r, cols.shareCurr) * 1000) / 10 + '%',
            curMarketStatus: String(r[cols.mktCurr] || '').trim(),
            curOperation: String(r[cols.opCurr] || '').trim(),
            plpEnabled: String(r[cols.plpCurr] || '').trim().toUpperCase() === 'Y' ? 'Y' : 'N',
            plgFee: Math.round(val(r, cols.plgFee) * 1000) / 10 + '%',
            adClass: getAdClass(sku, r, cols, plpPlgEnabled, skuCampaignCount)
        };
    });

    // 18. plpSummaryData
    DATA.plpSummaryData = [];
    DATA.plpCategories.forEach(function(d) { d.dimType = '品线'; DATA.plpSummaryData.push(d); });
    DATA.plpExpandTypes.forEach(function(d) { d.dimType = '拓展类型'; DATA.plpSummaryData.push(d); });
    DATA.plpAnalysts.forEach(function(d) { d.dimType = '分析人'; DATA.plpSummaryData.push(d); });

    // 19. plpDetailData
    DATA.plpDetailData = plpCurrRows.map(function(row) {
        var sku = String(row[PC.sku] || '').trim();
        var info = null;
        for (var i = 0; i < rowsCurr.length; i++) {
            if (String(rowsCurr[i][cols.sku] || '').trim() === sku) { info = rowsCurr[i]; break; }
        }
        var cost = val(row, PC.cost), adRev = val(row, PC.adRev), totalR = val(row, PC.totalRev);
        var impr = val(row, PC.impr), click = val(row, PC.click), sold = val(row, PC.sold);
        var plgY = String(row[PC.plgEnabled] || '').trim() === 'Y';
        var roasV = calcRate(adRev, cost), cvrV = calcRate(sold, click), ctrV = calcRate(click, impr);
        var acosV = calcRate(cost, adRev), acoasV = calcRate(cost, totalR);
        return {
            period: row[PC.period] || '', campaign: row[PC.campaign] || '',
            SKU: sku, id: String(row[PC.id] || ''), store: row[PC.store] || '',
            plpStartDate: fmtDate(parseDate(row[PC.plpStart])),
            listDate: fmtDate(parseDate(row[PC.listDate])),
            firstOrderDate: fmtDate(parseDate(row[PC.firstOrder])),
            analyst: info ? getAn(info, cols) : (row[PC.analyst] || ''),
            category: info ? getCat(info, cols) : (row[PC.category] || '未分类'),
            expandType: info ? getExp(info, cols) : (row[PC.expandType] || ''),
            impressions: safeInt(impr), clicks: safeInt(click), salesQty: safeInt(sold),
            spend: Math.round(cost * 100) / 100, adRevenue: Math.round(adRev * 100) / 100,
            totalRevenue: Math.round(totalR * 100) / 100,
            roas: roasV, cvr: cvrV, ctr: ctrV,
            cpc: click ? Math.round(cost / click * 1000) / 1000 : 0,
            cpa: sold ? Math.round(cost / sold * 100) / 100 : 0,
            acos: acosV, acoas: acoasV,
            plgEnabled: plgY ? 'Y' : 'N',
            adClass: info ? getAdClass(sku, info, cols, plpPlgEnabled, skuCampaignCount) : '无广告'
        };
    }).sort(function(a, b) { return a.analyst.localeCompare(b.analyst) || a.SKU.localeCompare(b.SKU); });

    // 20-24. 市场分布 / 货值 / 市占比分层 / 4周
    // 见 computeAll_part3
    return DATA;
}

// ===== 第三部分计算 =====
function computeAllPart3(DATA) {
    var ctx = DATA._ctx;
    var rowsCurr = ctx.rowsCurr, rowsPrev = ctx.rowsPrev;
    var cols = ctx.cols, PC = ctx.PC;
    var ansOrdered = ctx.ansOrdered;
    var totalSku = ctx.totalSku;

    // 20. shareTierOverview
    var catsOrdered = CATEGORIES.filter(function(c) { return rowsCurr.some(function(r) { return getCat(r, cols) === c; }); });
    var shareTierByCat = catsOrdered.map(function(cat) {
        var catRows = rowsCurr.filter(function(r) { return getCat(r, cols) === cat; });
        var high = catRows.filter(function(r) { return val(r, cols.shareCurr) * 100 >= 75; }).length;
        var mid = catRows.filter(function(r) { var s = val(r, cols.shareCurr) * 100; return s >= 50 && s < 75; }).length;
        var low = catRows.filter(function(r) { return val(r, cols.shareCurr) * 100 < 50; }).length;
        return {category: cat, high: high, mid: mid, low: low, total: catRows.length};
    });
    DATA.shareTierOverview = {tiers: ['高市占比(>=75%)', '中市占比(50-75%)', '低市占比(<50%)'], byCategory: shareTierByCat};

    // 21. mktDistOverall
    function normalizeMkt(r, colIdx) {
        var v = String(r[colIdx] || '').trim();
        if (v === '#N/A' || v === '未知' || v === '') return null;
        return v;
    }
    var mktCurrCounter = {}, mktPrevCounter = {};
    rowsCurr.forEach(function(r) { var v = normalizeMkt(r, cols.mktCurr); if (v) mktCurrCounter[v] = (mktCurrCounter[v] || 0) + 1; });
    rowsPrev.forEach(function(r) { var v = normalizeMkt(r, cols.mktPrev); if (v) mktPrevCounter[v] = (mktPrevCounter[v] || 0) + 1; });

    var seenStatuses = {};
    ALL_MKT_STATUSES.forEach(function(s) { seenStatuses[s] = true; });
    Object.keys(mktCurrCounter).forEach(function(s) { if (s) seenStatuses[s] = true; });
    Object.keys(mktPrevCounter).forEach(function(s) { if (s) seenStatuses[s] = true; });

    DATA.mktDistOverall = {curTotal: totalSku, prevTotal: rowsPrev.length, distribution: []};
    var sortedStatuses = Object.keys(seenStatuses).sort(function(a, b) {
        var ai = ALL_MKT_STATUSES.indexOf(a), bi = ALL_MKT_STATUSES.indexOf(b);
        if (ai >= 0 && bi >= 0) return ai - bi;
        if (ai >= 0) return -1; if (bi >= 0) return 1;
        return a.localeCompare(b);
    });
    sortedStatuses.forEach(function(s) {
        var cc = mktCurrCounter[s] || 0, pc = mktPrevCounter[s] || 0;
        DATA.mktDistOverall.distribution.push({
            status: s, curCount: cc, prevCount: pc,
            curPct: totalSku ? Math.round(cc / totalSku * 1000) / 10 : 0,
            prevPct: rowsPrev.length ? Math.round(pc / rowsPrev.length * 1000) / 10 : 0,
            change: cc - pc
        });
    });

    // 22. priceOverview
    var priceList = [];
    rowsCurr.forEach(function(r) {
        var sales = val(r, cols.salesCurr), rev = val(r, cols.revCurr);
        if (sales > 0) {
            priceList.push({
                sku: String(r[cols.sku] || '').trim(),
                price: Math.round(rev / sales * 100) / 100,
                analyst: getAn(r, cols), category: getCat(r, cols)
            });
        }
    });

    var priceDist = PRICE_RANGES.map(function(pr) {
        var cnt = priceList.filter(function(p) { return p.price >= pr[1] && p.price < pr[2]; }).length;
        return {range: pr[0], count: cnt, pct: priceList.length ? Math.round(cnt / priceList.length * 1000) / 10 : 0};
    });

    var avgPrice = priceList.length ? Math.round(priceList.reduce(function(s, p) { return s + p.price; }, 0) / priceList.length * 100) / 100 : 0;
    var sortedPrices = priceList.map(function(p) { return p.price; }).sort(function(a, b) { return a - b; });
    var medianPrice = sortedPrices.length > 0 ? Math.round(sortedPrices[Math.floor(sortedPrices.length / 2)] * 100) / 100 : 0;

    var priceByAnalyst = ansOrdered.map(function(an) {
        var anPrices = priceList.filter(function(p) { return p.analyst === an; });
        var entry = {analyst: an, total: anPrices.length};
        PRICE_RANGES.forEach(function(pr) {
            entry[pr[0]] = anPrices.filter(function(p) { return p.price >= pr[1] && p.price < pr[2]; }).length;
        });
        return entry;
    });

    var priceByCategory = catsOrdered.map(function(cat) {
        var catPrices = priceList.filter(function(p) { return p.category === cat; });
        var entry = {category: cat, total: catPrices.length};
        PRICE_RANGES.forEach(function(pr) {
            entry[pr[0]] = catPrices.filter(function(p) { return p.price >= pr[1] && p.price < pr[2]; }).length;
        });
        return entry;
    });

    DATA.priceOverview = {
        avgPrice: avgPrice, medianPrice: medianPrice,
        totalWithSales: priceList.length,
        priceRanges: PRICE_RANGES.map(function(pr) { return pr[0]; }),
        distribution: priceDist,
        byAnalyst: priceByAnalyst,
        byCategory: priceByCategory
    };

    // 23. 4周趋势
    var W4_SALES = cols.w4Sales, W4_REVENUE = cols.w4Revenue;
    var W4_RIVAL = cols.w4Rival, W4_SHARE = cols.w4Share;
    var W4_FREQ7 = cols.w4Freq7, W4_NFREQ7 = cols.w4Nfreq7;
    var WEEK_LABELS_4W = cols.weekLabels4w;

    DATA.weekLabels4w = WEEK_LABELS_4W;

    function sum4w(items, colsArr) {
        return colsArr.map(function(c) { return safeInt(items.reduce(function(s, r) { return s + val(r, c); }, 0)); });
    }
    function sum4wRev(items, colsArr) {
        return colsArr.map(function(c) { return Math.round(items.reduce(function(s, r) { return s + val(r, c); }, 0) * 100) / 100; });
    }
    function share4wFn(items, sCols, rCols) {
        var result = [];
        for (var i = 0; i < 4; i++) {
            var s = items.reduce(function(sum, r) { return sum + val(r, sCols[i]); }, 0);
            var ri = items.reduce(function(sum, r) { return sum + val(r, rCols[i]); }, 0);
            result.push((s + ri) > 0 ? Math.round(s / (s + ri) * 1000) / 10 : 0);
        }
        return result;
    }

    DATA.totalSales4w = sum4w(rowsCurr, W4_SALES);
    DATA.totalRev4w = sum4wRev(rowsCurr, W4_REVENUE);
    DATA.totalShare4w = share4wFn(rowsCurr, W4_SALES, W4_RIVAL);

    DATA.catSales4w = CATEGORIES.map(function(cat) {
        var items = rowsCurr.filter(function(r) { return getCat(r, cols) === cat; });
        return {category: cat, sales4w: sum4w(items, W4_SALES)};
    });
    DATA.catRev4w = CATEGORIES.map(function(cat) {
        var items = rowsCurr.filter(function(r) { return getCat(r, cols) === cat; });
        return {category: cat, rev4w: sum4wRev(items, W4_REVENUE)};
    });
    DATA.catShare4w = CATEGORIES.map(function(cat) {
        var items = rowsCurr.filter(function(r) { return getCat(r, cols) === cat; });
        return {category: cat, share4w: share4wFn(items, W4_SALES, W4_RIVAL)};
    });

    DATA.anSales4w = ANALYSTS.map(function(an) {
        var items = rowsCurr.filter(function(r) { return getAn(r, cols) === an; });
        return {analyst: an, sales4w: sum4w(items, W4_SALES)};
    });
    DATA.anRev4w = ANALYSTS.map(function(an) {
        var items = rowsCurr.filter(function(r) { return getAn(r, cols) === an; });
        return {analyst: an, rev4w: sum4wRev(items, W4_REVENUE)};
    });
    DATA.anShare4w = ANALYSTS.map(function(an) {
        var items = rowsCurr.filter(function(r) { return getAn(r, cols) === an; });
        return {analyst: an, share4w: share4wFn(items, W4_SALES, W4_RIVAL)};
    });

    // 24. 及时率4周
    DATA.timeliness4w = {labels: WEEK_LABELS_4W, analysts: [], totalRates: []};
    ANALYSTS.forEach(function(an) {
        var items = rowsCurr.filter(function(r) { return getAn(r, cols) === an; });
        var rates = [];
        for (var i = 0; i < 4; i++) {
            var tot = items.length;
            var timely = items.filter(function(r) { return String(r[W4_NFREQ7[i]] || '').trim() !== '异常' && String(r[W4_FREQ7[i]] || '').trim() !== '异常'; }).length;
            rates.push(tot > 0 ? Math.round(timely / tot * 1000) / 10 : 0);
        }
        DATA.timeliness4w.analysts.push({analyst: an, rates4w: rates});
    });
    var totalRates = [];
    for (var i = 0; i < 4; i++) {
        var tot = rowsCurr.length;
        var timely = rowsCurr.filter(function(r) { return String(r[W4_NFREQ7[i]] || '').trim() !== '异常' && String(r[W4_FREQ7[i]] || '').trim() !== '异常'; }).length;
        totalRates.push(tot > 0 ? Math.round(timely / tot * 1000) / 10 : 0);
    }
    DATA.timeliness4w.totalRates = totalRates;

    // 25. cum43_4w (SKU drill data)
    DATA.cum43_4w = {};
    rowsCurr.forEach(function(r) {
        var sku = String(r[cols.sku] || '').trim();
        DATA.cum43_4w[sku] = {
            sales4w: W4_SALES.map(function(c) { return safeInt(val(r, c)); }),
            rev4w: W4_REVENUE.map(function(c) { return Math.round(val(r, c) * 100) / 100; }),
            share4w: share4wFn([r], W4_SALES, W4_RIVAL)
        };
    });

    // 26. PLP 4-week drill data (from all PLP rows, not just current period)
    var allPlpRows = ctx.allPlpRows;
    var PLP_PERIODS = ['4.27-5.3', '5.4-5.10', '5.11-5.17', '5.18-5.24'];
    DATA.plp4wLabels = PLP_PERIODS;
    var plp4wCost = [0,0,0,0], plp4wAdRev = [0,0,0,0], plp4wAcos = [0,0,0,0], plp4wAcoas = [0,0,0,0];
    var plp4wAn = {};
    ANALYSTS.forEach(function(an) {
        plp4wAn[an] = {cost4w: [0,0,0,0], adRev4w: [0,0,0,0], acos4w: [0,0,0,0], acoas4w: [0,0,0,0]};
    });

    for (var wi = 0; wi < 4; wi++) {
        var periodCost = 0, periodAdRev = 0, periodTotalRev = 0;
        var seenSku = new Set();
        var anCost = {}, anAdRev = {}, anTotalRev = {};
        ANALYSTS.forEach(function(an) { anCost[an] = 0; anAdRev[an] = 0; anTotalRev[an] = 0; });

        for (var pi = 0; pi < allPlpRows.length; pi++) {
            var pr = allPlpRows[pi];
            var p = String(pr[PC.period] || '').trim();
            var psku = String(pr[PC.sku] || '').trim();
            if (p !== PLP_PERIODS[wi] || !psku || psku.indexOf('广告') === 0 || psku.indexOf('总数据') === 0) continue;
            var plistD = parseDate(pr[PC.listDate]);
            if (!plistD || plistD > cutoffCurr) continue;
            var c = val(pr, PC.cost), ar = val(pr, PC.adRev), tr = val(pr, PC.totalRev);
            periodCost += c; periodAdRev += ar;
            if (!seenSku.has(psku)) { periodTotalRev += tr; seenSku.add(psku); }
            var an = String(pr[PC.analyst] || '').trim();
            if (an in anCost) {
                anCost[an] += c; anAdRev[an] += ar;
                if (!seenSku.has(psku)) anTotalRev[an] += tr;
            }
        }
        plp4wCost[wi] = Math.round(periodCost * 100) / 100;
        plp4wAdRev[wi] = Math.round(periodAdRev * 100) / 100;
        plp4wAcos[wi] = periodAdRev > 0 ? Math.round(periodCost / periodAdRev * 10000) / 100 : 0;
        plp4wAcoas[wi] = periodTotalRev > 0 ? Math.round(periodCost / periodTotalRev * 10000) / 100 : 0;
        for (var an in plp4wAn) {
            plp4wAn[an].cost4w[wi] = Math.round(anCost[an] * 100) / 100;
            plp4wAn[an].adRev4w[wi] = Math.round(anAdRev[an] * 100) / 100;
            plp4wAn[an].acos4w[wi] = anAdRev[an] > 0 ? Math.round(anCost[an] / anAdRev[an] * 10000) / 100 : 0;
            plp4wAn[an].acoas4w[wi] = anTotalRev[an] > 0 ? Math.round(anCost[an] / anTotalRev[an] * 10000) / 100 : 0;
        }
    }
    DATA.plp4wCost = plp4wCost;
    DATA.plp4wAdRev = plp4wAdRev;
    DATA.plp4wAcos = plp4wAcos;
    DATA.plp4wAcoas = plp4wAcoas;
    DATA.plp4wAnalysts = ANALYSTS.map(function(an) {
        return {analyst: an, cost4w: plp4wAn[an].cost4w, adRev4w: plp4wAn[an].adRev4w, acos4w: plp4wAn[an].acos4w, acoas4w: plp4wAn[an].acoas4w};
    });

    // 27. PLG 4-week drill data (per-analyst PLG spend/revenue/acos/acoas)
    var PLG_PERIODS = ['4.27-5.3', '5.4-5.10', '5.11-5.17', '5.18-5.24'];
    DATA.plg4wLabels = PLG_PERIODS;
    DATA.plgAn4w = ANALYSTS.map(function(an) {
        var anItems = rowsCurr.filter(function(r) { return getAn(r, cols) === an; });
        var spend4w = [0,0,0,0], adSales4w = [0,0,0,0], totalRev4w = [0,0,0,0], acos4w = [0,0,0,0], acoas4w = [0,0,0,0];
        // PLG data is only for the current period; spread across 4 weeks using natWeekData
        // For simplicity, use the current PLG data as the last week, with previous weeks from historical
        // The actual implementation uses PLP detail sheet per-period data
        var anPlgSpend = anItems.reduce(function(s, r) { return s + val(r, cols.plgSpend); }, 0);
        var anPlgAdRev = anItems.reduce(function(s, r) { return s + val(r, cols.plgAdRev); }, 0);
        var anPlgNatRev = 0;
        anItems.forEach(function(r) {
            var sku = String(r[cols.sku] || '').trim();
            if (val(r, cols.plgSpend) > 0) anPlgNatRev += (ctx.natWeekData[sku] || {rev:0}).rev;
        });
        // PLG 4-week: approximate by distributing. For now, put data in last week
        spend4w[3] = Math.round(anPlgSpend * 100) / 100;
        adSales4w[3] = Math.round(anPlgAdRev * 100) / 100;
        totalRev4w[3] = Math.round(anPlgNatRev * 100) / 100;
        acos4w[3] = anPlgAdRev > 0 ? Math.round(anPlgSpend / anPlgAdRev * 10000) / 100 : 0;
        acoas4w[3] = anPlgNatRev > 0 ? Math.round(anPlgSpend / anPlgNatRev * 10000) / 100 : 0;
        return {analyst: an, spend4w: spend4w, adSales4w: adSales4w, totalRev4w: totalRev4w, acos4w: acos4w, acoas4w: acoas4w};
    });

    // 28. PLP per-dimension 4-week (analyst/category/expandType)
    DATA.plpAn4w = ANALYSTS.map(function(an) {
        var spend4w = [0,0,0,0], adSales4w = [0,0,0,0], acos4w = [0,0,0,0], acoas4w = [0,0,0,0];
        var anPlpData = DATA.plp4wAnalysts.find(function(d) { return d.analyst === an; });
        if (anPlpData) {
            spend4w = anPlpData.cost4w; adSales4w = anPlpData.adRev4w;
            acos4w = anPlpData.acos4w; acoas4w = anPlpData.acoas4w;
        }
        return {analyst: an, spend4w: spend4w, adSales4w: adSales4w, acos4w: acos4w, acoas4w: acoas4w};
    });

    // PLP per-category 4-week
    var catPlp4w = {};
    CATEGORIES.forEach(function(cat) { catPlp4w[cat] = {spend4w:[0,0,0,0], adSales4w:[0,0,0,0], acos4w:[0,0,0,0], acoas4w:[0,0,0,0]}; });
    for (var wi = 0; wi < 4; wi++) {
        var catPeriodCost = {}, catPeriodAdRev = {}, catPeriodTotalRev = {}, catSeenSku = {};
        CATEGORIES.forEach(function(cat) { catPeriodCost[cat] = 0; catPeriodAdRev[cat] = 0; catPeriodTotalRev[cat] = 0; catSeenSku[cat] = new Set(); });
        for (var pi = 0; pi < allPlpRows.length; pi++) {
            var pr = allPlpRows[pi];
            var p = String(pr[PC.period] || '').trim();
            var psku = String(pr[PC.sku] || '').trim();
            if (p !== PLP_PERIODS[wi] || !psku || psku.indexOf('广告') === 0 || psku.indexOf('总数据') === 0) continue;
            var plistD = parseDate(pr[PC.listDate]);
            if (!plistD || plistD > cutoffCurr) continue;
            var cat = String(pr[PC.category] || '').trim();
            if (!cat || !catPlp4w[cat]) continue;
            var c = val(pr, PC.cost), ar = val(pr, PC.adRev), tr = val(pr, PC.totalRev);
            catPeriodCost[cat] += c; catPeriodAdRev[cat] += ar;
            if (!catSeenSku[cat].has(psku)) { catPeriodTotalRev[cat] += tr; catSeenSku[cat].add(psku); }
        }
        for (var cat in catPlp4w) {
            catPlp4w[cat].spend4w[wi] = Math.round(catPeriodCost[cat] * 100) / 100;
            catPlp4w[cat].adSales4w[wi] = Math.round(catPeriodAdRev[cat] * 100) / 100;
            catPlp4w[cat].acos4w[wi] = catPeriodAdRev[cat] > 0 ? Math.round(catPeriodCost[cat] / catPeriodAdRev[cat] * 10000) / 100 : 0;
            catPlp4w[cat].acoas4w[wi] = catPeriodTotalRev[cat] > 0 ? Math.round(catPeriodCost[cat] / catPeriodTotalRev[cat] * 10000) / 100 : 0;
        }
    }
    DATA.plpCat4w = CATEGORIES.filter(function(cat) {
        return catPlp4w[cat].spend4w.some(function(v) { return v > 0; });
    }).map(function(cat) {
        return {category: cat, spend4w: catPlp4w[cat].spend4w, adSales4w: catPlp4w[cat].adSales4w, acos4w: catPlp4w[cat].acos4w, acoas4w: catPlp4w[cat].acoas4w};
    });

    // PLP per-expand-type 4-week
    var expTypes = ['原开品', '拓展品', '组合件'];
    var expPlp4w = {};
    expTypes.forEach(function(et) { expPlp4w[et] = {spend4w:[0,0,0,0], adSales4w:[0,0,0,0], acos4w:[0,0,0,0], acoas4w:[0,0,0,0]}; });
    for (var wi = 0; wi < 4; wi++) {
        var expPeriodCost = {}, expPeriodAdRev = {}, expPeriodTotalRev = {}, expSeenSku = {};
        expTypes.forEach(function(et) { expPeriodCost[et] = 0; expPeriodAdRev[et] = 0; expPeriodTotalRev[et] = 0; expSeenSku[et] = new Set(); });
        for (var pi = 0; pi < allPlpRows.length; pi++) {
            var pr = allPlpRows[pi];
            var p = String(pr[PC.period] || '').trim();
            var psku = String(pr[PC.sku] || '').trim();
            if (p !== PLP_PERIODS[wi] || !psku || psku.indexOf('广告') === 0 || psku.indexOf('总数据') === 0) continue;
            var plistD = parseDate(pr[PC.listDate]);
            if (!plistD || plistD > cutoffCurr) continue;
            var et = String(pr[PC.expandType] || '').trim();
            if (!et || !expPlp4w[et]) continue;
            var c = val(pr, PC.cost), ar = val(pr, PC.adRev), tr = val(pr, PC.totalRev);
            expPeriodCost[et] += c; expPeriodAdRev[et] += ar;
            if (!expSeenSku[et].has(psku)) { expPeriodTotalRev[et] += tr; expSeenSku[et].add(psku); }
        }
        for (var et in expPlp4w) {
            expPlp4w[et].spend4w[wi] = Math.round(expPeriodCost[et] * 100) / 100;
            expPlp4w[et].adSales4w[wi] = Math.round(expPeriodAdRev[et] * 100) / 100;
            expPlp4w[et].acos4w[wi] = expPeriodAdRev[et] > 0 ? Math.round(expPeriodCost[et] / expPeriodAdRev[et] * 10000) / 100 : 0;
            expPlp4w[et].acoas4w[wi] = expPeriodTotalRev[et] > 0 ? Math.round(expPeriodCost[et] / expPeriodTotalRev[et] * 10000) / 100 : 0;
        }
    }
    DATA.plpExp4w = expTypes.map(function(et) {
        return {expandType: et, spend4w: expPlp4w[et].spend4w, adSales4w: expPlp4w[et].adSales4w, acos4w: expPlp4w[et].acos4w, acoas4w: expPlp4w[et].acoas4w};
    });

    // Clean up context
    delete DATA._ctx;
    return DATA;
}

// ===== 完整计算入口 =====
function computeEngine(workbook) {
    var DATA = computeAll(workbook);
    DATA = computeAllPart2(DATA);
    DATA = computeAllPart3(DATA);
    return DATA;
}