import * as XLSX from 'xlsx';
import type { FieldMap, ParseResult, RawExcelRow, WeeklyPeriod } from '../types/weeklyReport';
import { buildPeriods } from './periodParser';

const normalizeHeader = (value: unknown) => String(value ?? '').trim();
const highEmptyCompetitorRatio = 0.2;
const minEmptyCompetitorRows = 5;

const findHeaderRowIndex = (matrix: unknown[][]) =>
  matrix.findIndex((row) => {
    const headers = row.map(normalizeHeader);
    return headers.includes('销售编码') || headers.includes('在售SKU') || headers.some((header) => /销量$/.test(header));
  });

const identifyFields = (headers: string[]): FieldMap => {
  const exact = (name: string) => headers.find((header) => header === name);
  return {
    salesCode: exact('销售编码'),
    sku: exact('在售SKU'),
    category: exact('分类'),
    tertiaryCategory: exact('三级类目'),
    analyst: headers.find((header) => header.includes('分析人')),
    isLoss: exact('是否亏本'),
    inventory: exact('库存'),
    sellableWeeks: exact('可售周'),
    productGrade: headers.find((header) => header.includes('等级') && header !== '是否淘汰/停单' && !header.includes('淘汰') && !header.includes('停单')),
    discontinued: exact('是否淘汰/停单'),
  };
};

const toNumber = (value: unknown) => {
  const raw = normalizeHeader(value);
  if (!raw || raw.startsWith('#')) return 0;
  const cleaned = raw.replace(/,/g, '').replace(/￥|\$/g, '');
  const parsed = Number(cleaned.endsWith('%') ? Number(cleaned.slice(0, -1)) / 100 : cleaned);
  return Number.isFinite(parsed) ? parsed : 0;
};

const isEmptyCell = (value: unknown) => normalizeHeader(value) === '';

const buildDataQualityWarnings = (rows: RawExcelRow[], periods: WeeklyPeriod[]) => {
  const warnings: string[] = [];

  periods.forEach((period) => {
    if (!period.salesAmountColumn) {
      warnings.push(`周期 ${period.label} 缺失销售额列，销售额、出单均价和销售额趋势判断需谨慎。`);
    }

    const competitorColumn = period.competitorColumn;
    if (!competitorColumn) return;
    const activeRows = rows.filter((row) => toNumber(row[period.salesQtyColumn]) > 0);
    if (!activeRows.length) return;

    const emptyCount = activeRows.filter((row) => isEmptyCell(row[competitorColumn])).length;
    const emptyRatio = emptyCount / activeRows.length;
    if (emptyCount >= minEmptyCompetitorRows && emptyRatio >= highEmptyCompetitorRatio) {
      warnings.push(`周期 ${period.label} 直接对手出单字段存在较多空值，市占判断需谨慎。`);
    }
  });

  return warnings;
};

export const parseWorkbook = (buffer: ArrayBuffer, sourceName: string): ParseResult => {
  const workbook = XLSX.read(buffer, { type: 'array', cellDates: false });
  const sheet = workbook.Sheets['数据源'];
  if (!sheet) {
    return {
      rows: [],
      headers: [],
      fields: {},
      periods: [],
      warnings: ['未找到“数据源”工作表，请检查 Excel 文件。'],
      sourceName,
    };
  }

  const matrix = XLSX.utils.sheet_to_json<unknown[]>(sheet, {
    header: 1,
    raw: false,
    defval: '',
    blankrows: false,
  });
  const headerRowIndex = findHeaderRowIndex(matrix);
  if (headerRowIndex < 0) {
    return {
      rows: [],
      headers: [],
      fields: {},
      periods: [],
      warnings: ['未识别到表头行，请检查“数据源”工作表。'],
      sourceName,
    };
  }

  const rawHeaders = matrix[headerRowIndex].map(normalizeHeader);
  const headers = rawHeaders.map((header, index) => header || `未命名列${index + 1}`);
  const rows: RawExcelRow[] = matrix.slice(headerRowIndex + 1).map((row) => {
    const item: RawExcelRow = {};
    headers.forEach((header, index) => {
      item[header] = row[index] ?? '';
    });
    return item;
  }).filter((row) => Object.values(row).some((value) => String(value ?? '').trim() !== ''));

  const fields = identifyFields(headers);
  const { periods, warnings: periodWarnings } = buildPeriods(headers);
  const warnings: string[] = [];
  if (!periods.length) warnings.push('未识别到周销量字段，请检查表头格式，例如“4/16-4/22销量”。');
  const requiredFields: Array<[keyof FieldMap, string]> = [
    ['salesCode', '销售编码'],
    ['sku', '在售SKU'],
    ['category', '分类'],
    ['tertiaryCategory', '三级类目'],
    ['analyst', '分析人'],
    ['isLoss', '是否亏本'],
    ['inventory', '库存'],
    ['sellableWeeks', '可售周'],
    ['productGrade', '产品等级'],
    ['discontinued', '是否淘汰/停单'],
  ];
  requiredFields.forEach(([key, label]) => {
    if (!fields[key]) warnings.push(`未识别到${label}字段。`);
  });
  warnings.push(...periodWarnings);
  warnings.push(...buildDataQualityWarnings(rows, periods));

  return { rows, headers, fields, periods, warnings, sourceName };
};
