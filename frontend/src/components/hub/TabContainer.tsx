import type { Tab } from "../../contexts/TabContext";

interface TabContainerProps {
  tabs: Tab[];
  activeTab: string | null;
  onSelect: (id: string) => void;
  onClose: (id: string) => void;
}

export default function TabContainer({ tabs, activeTab, onSelect, onClose }: TabContainerProps) {
  if (tabs.length === 0) return null;
  return (
    <div className="flex items-center gap-0.5 border-b border-gray-200 bg-gray-50 px-2 overflow-x-auto">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onSelect(tab.id)}
          className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === tab.id
              ? "border-blue-600 text-blue-700 bg-white"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          }`}
        >
          {tab.icon && <span className="text-base">{tab.icon}</span>}
          <span>{tab.label}</span>
          <svg
            onClick={(e) => { e.stopPropagation(); onClose(tab.id); }}
            className="w-3.5 h-3.5 ml-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      ))}
    </div>
  );
}
