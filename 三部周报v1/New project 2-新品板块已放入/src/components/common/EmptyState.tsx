import EmptyStateBase from '../EmptyState';

type EmptyStateProps = {
  title?: string;
  message?: string;
};

export default function EmptyState({ title = '暂无可展示数据', message }: EmptyStateProps) {
  return (
    <div className="module-empty">
      <EmptyStateBase title={title} message={message ?? '该模块已预留入口，等待接入数据源、规则和周报文案。'} />
    </div>
  );
}
