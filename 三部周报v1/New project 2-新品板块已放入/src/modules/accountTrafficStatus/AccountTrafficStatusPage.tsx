import EmptyState from '../../components/common/EmptyState';
import ModulePageLayout from '../../components/common/ModulePageLayout';
import { useModulePeriodInfo } from '../useModulePeriodInfo';

export default function AccountTrafficStatusPage() {
  const { dataPeriod, periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo('accountTrafficStatus');

  return (
    <ModulePageLayout title="账号流量状态" subtitle="跟踪账号访问、转化、流量来源和流量异常" dataPeriod={dataPeriod} periodTypeLabel={periodTypeLabel} sourceStatusLabel={sourceStatusLabel}>
      <EmptyState title="账号流量状态模块待开发" message="该模块当前为开发壳子。页面结构、指标体系、数据处理、异常规则和汇报输出方式由模块负责人自行设计。开发时请遵守模块开发规范，不要修改 DataCenter、Sidebar、周期系统和全局样式。" />
    </ModulePageLayout>
  );
}
