import { useDataCenter } from '../dataCenter/DataCenterProvider';
import { modulePeriodConfig } from '../dataCenter/periodConfig';
import { periodLabelFromIsoRange } from '../dataCenter/periodParser';
import type { ModuleKey } from '../dataCenter/types';

export const useModulePeriodInfo = (moduleKey: ModuleKey) => {
  const { sources, weeklyReportContext } = useDataCenter();
  const config = modulePeriodConfig[moduleKey];
  const period = weeklyReportContext.periods[config.reportPeriodKey];
  const source = sources[config.dataSourceKind];
  const sourceStatusLabel = source.status === 'loaded'
    ? `已接入${source.sourceName ? `：${source.sourceName}` : ''}`
    : source.status === 'error'
      ? '数据源异常'
      : '待接入数据源';

  return {
    period,
    dataPeriod: period ? periodLabelFromIsoRange(period) : '--',
    periodTypeLabel: config.periodTypeLabel,
    sourceStatusLabel,
  };
};
