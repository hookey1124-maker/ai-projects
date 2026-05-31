import type { ReactNode } from 'react';

type FilterBarProps = {
  children?: ReactNode;
};

export default function FilterBar({ children }: FilterBarProps) {
  return (
    <div className="trend-filter common-filter-bar">
      {children ?? <span>筛选器待接入</span>}
    </div>
  );
}
