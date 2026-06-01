import { type ReactNode } from "react";
import TabContainer from "./TabContainer";
import { useTabs } from "../../contexts/TabContext";

interface HubLayoutProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export default function HubLayout({ title, description, actions, children }: HubLayoutProps) {
  const { tabs, activeTab, setActiveTab, closeTab } = useTabs();

  return (
    <div className="flex flex-col h-full">
      {/* Hub header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{title}</h1>
          {description && <p className="text-sm text-gray-500 mt-0.5">{description}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      {/* Hub tabs */}
      <TabContainer tabs={tabs} activeTab={activeTab} onSelect={setActiveTab} onClose={closeTab} />

      {/* Hub content */}
      <div className="flex-1 overflow-auto bg-gray-50">
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
