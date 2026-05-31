import EmptyState from '../../components/common/EmptyState';
import ModulePageLayout from '../../components/common/ModulePageLayout';
import type { ModuleKey } from '../../dataCenter/types';
import { useModulePeriodInfo } from '../useModulePeriodInfo';

type TemplateStatusPageProps = {
  moduleKey: ModuleKey;
  title: string;
  subtitle: string;
};

export default function TemplateStatusPage({ moduleKey, title, subtitle }: TemplateStatusPageProps) {
  const { dataPeriod, periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo(moduleKey);

  return (
    <ModulePageLayout
      title={title}
      subtitle={subtitle}
      dataPeriod={dataPeriod}
      periodTypeLabel={periodTypeLabel}
      sourceStatusLabel={sourceStatusLabel}
    >
      <EmptyState title="模块开发壳子" message="页面结构、指标体系、数据处理、异常规则和汇报输出方式由模块负责人自行设计。模板只保留主项目框架、周期信息和空状态。" />
    </ModulePageLayout>
  );
}
