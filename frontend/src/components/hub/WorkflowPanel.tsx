interface WorkflowAction {
  id: string;
  label: string;
  icon: string;
  description: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";
}

interface WorkflowPanelProps {
  title: string;
  actions: WorkflowAction[];
}

export default function WorkflowPanel({ title, actions }: WorkflowPanelProps) {
  if (actions.length === 0) return null;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      <div className="space-y-2">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={action.onClick}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
              action.variant === "primary"
                ? "bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200"
                : action.variant === "danger"
                ? "bg-red-50 text-red-700 hover:bg-red-100 border border-red-200"
                : "bg-gray-50 text-gray-700 hover:bg-gray-100 border border-gray-200"
            }`}
          >
            <span className="text-lg">{action.icon}</span>
            <div className="text-left flex-1">
              <div className="font-medium">{action.label}</div>
              <div className="text-xs text-gray-500">{action.description}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export type { WorkflowAction };
