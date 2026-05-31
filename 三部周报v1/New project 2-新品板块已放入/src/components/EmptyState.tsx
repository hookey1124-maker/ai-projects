import { FileSpreadsheet } from 'lucide-react';

type EmptyStateProps = {
  message?: string;
  title?: string;
};

export default function EmptyState({ message, title = '上传或放置 Excel 数据源' }: EmptyStateProps) {
  return (
    <section className="empty-state">
      <FileSpreadsheet size={48} />
      <h2>{title}</h2>
      <p>{message || '没有检测到默认数据源时，可以点击右上角“上传 Excel”开始生成周报。'}</p>
    </section>
  );
}
