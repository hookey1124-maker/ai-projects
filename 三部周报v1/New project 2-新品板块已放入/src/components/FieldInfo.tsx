import type { ParseResult } from '../types/weeklyReport';

type FieldInfoProps = {
  result: ParseResult;
  selectedPeriodIndex?: number;
};

const warningType = (warning: string) => {
  if (warning.includes('日期不一致')) return '辅助字段日期不一致';
  if (warning.includes('缺失市占比') || warning.includes('缺失直接对手') || warning.includes('缺失在售价')) return '周期辅助字段缺失';
  if (warning.includes('未识别到')) return '固定字段缺失';
  return '数据质量异常';
};

export default function FieldInfo({ result, selectedPeriodIndex }: FieldInfoProps) {
  const latest = result.periods.at(-1)?.label ?? '--';
  const current = selectedPeriodIndex == null ? latest : result.periods[selectedPeriodIndex]?.label ?? '--';
  const previous = selectedPeriodIndex != null && selectedPeriodIndex > 0 ? result.periods[selectedPeriodIndex - 1]?.label ?? '--' : '--';
  const hasMissingField = result.warnings.some((warning) => warning.includes('未识别到'));
  return (
    <details className="field-info">
      <summary>
        字段识别与数据源状态
        {result.warnings.length > 0 && <span className="warning-count">{result.warnings.length} 条 warning</span>}
      </summary>
      <div className="field-grid">
        <div><span>数据源</span><strong>{result.sourceName}</strong></div>
        <div><span>分析人字段</span><strong>{result.fields.analyst ?? '未识别'}</strong></div>
        <div><span>产品等级字段</span><strong>{result.fields.productGrade ?? '未识别'}</strong></div>
        <div><span>最新周期</span><strong>{latest}</strong></div>
        <div><span>当前查看</span><strong>{current}</strong></div>
        <div><span>对比周期</span><strong>{previous}</strong></div>
        <div><span>周期数量</span><strong>{result.periods.length}</strong></div>
        <div><span>SKU 数据</span><strong>{result.rows.length}</strong></div>
        <div><span>字段缺失</span><strong>{hasMissingField ? '存在' : '无'}</strong></div>
        <div><span>数据提示</span><strong>{result.warnings.length ? `${result.warnings.length} 条 warning` : '无 warning'}</strong></div>
      </div>
      {result.warnings.length > 0 && (
        <div className="warning-list">
          {result.warnings.map((warning) => (
            <div key={warning}>
              <span>{warningType(warning)}</span>
              {warning}
            </div>
          ))}
        </div>
      )}
    </details>
  );
}
