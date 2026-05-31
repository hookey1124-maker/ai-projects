import EmptyState from '../../components/common/EmptyState';
import ModulePageLayout from '../../components/common/ModulePageLayout';
import { useModulePeriodInfo } from '../useModulePeriodInfo';

export default function SalesForecastPage() {
  const { dataPeriod, periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo('salesForecast');

  return (
    <ModulePageLayout title="销量预估" subtitle="基于历史销量、趋势和业务假设输出销量预测" dataPeriod={dataPeriod} periodTypeLabel={periodTypeLabel} sourceStatusLabel={sourceStatusLabel}>
      <EmptyState title="销量预估模块待开发" message="该模块当前为开发壳子。页面结构、指标体系、数据处理、异常规则和汇报输出方式由模块负责人自行设计。开发时请遵守模块开发规范，不要修改 DataCenter、Sidebar、周期系统和全局样式。" />
    </ModulePageLayout>
  );
}
