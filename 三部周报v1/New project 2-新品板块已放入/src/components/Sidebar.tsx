import { moduleDefinitions, moduleTitle, type ModuleDefinition } from '../dataCenter/moduleRegistry';
import type { ModuleKey } from '../dataCenter/types';

export type { ModuleKey };
export { moduleTitle };

type SidebarProps = {
  activeModule: ModuleKey;
  collapsed: boolean;
  onModuleChange: (module: ModuleKey) => void;
  onToggle: () => void;
};

export const moduleItems: ModuleDefinition[] = moduleDefinitions;

export default function Sidebar({ activeModule, collapsed, onModuleChange, onToggle }: SidebarProps) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <span>W</span>
          {!collapsed && <strong>周报看板</strong>}
        </div>
        <button type="button" className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? '展开' : '收起'}
        </button>
      </div>
      <nav className="sidebar-nav">
        {moduleItems.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`sidebar-item ${activeModule === item.key ? 'active' : ''}`}
            onClick={() => onModuleChange(item.key)}
            title={collapsed ? `${item.label}：${item.description}` : undefined}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {!collapsed && (
              <span className="sidebar-text">
                <strong>{item.label}</strong>
                <em>{item.description}</em>
              </span>
            )}
          </button>
        ))}
      </nav>
    </aside>
  );
}
