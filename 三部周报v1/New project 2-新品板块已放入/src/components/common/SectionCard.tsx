import type { ReactNode } from 'react';

type SectionCardProps = {
  index?: string;
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
};

export default function SectionCard({ index, title, description, children, className = '' }: SectionCardProps) {
  return (
    <section className={`dashboard-section module-section ${className}`}>
      <div className="section-heading">
        <div>
          {index && <span>{index}</span>}
          <h2>{title}</h2>
        </div>
        {description && <p>{description}</p>}
      </div>
      <div className="section-card-body">{children}</div>
    </section>
  );
}
