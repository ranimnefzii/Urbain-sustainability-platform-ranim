import { useEffect } from "react";
import HubLayout from "../../components/hub/HubLayout";
import WorkflowPanel from "../../components/hub/WorkflowPanel";
import type { WorkflowAction } from "../../components/hub/WorkflowPanel";
import { useTabs } from "../../contexts/TabContext";
import ReportManagement from "../admin/ReportManagement";

const REPORTS_TABS = {
  list: { id: "reports-list", label: "All Reports", icon: "📄" },
  generate: { id: "reports-generate", label: "Generate", icon: "➕" },
  dashboard: { id: "reports-dashboard", label: "Dashboard", icon: "📊" },
  export: { id: "reports-export", label: "Export", icon: "📥" },
} as const;

export default function ReportsHub() {
  const { openTab } = useTabs();

  useEffect(() => {
    openTab(REPORTS_TABS.list);
  }, []);

  const workflows: WorkflowAction[] = [
    { id: "new-report", label: "Generate Report", icon: "➕", description: "Create a new report", variant: "primary", onClick: () => openTab(REPORTS_TABS.generate) },
    { id: "signal-report", label: "Signal Report", icon: "📋", description: "Generate report for a signal", onClick: () => openTab(REPORTS_TABS.generate) },
    { id: "sector-report", label: "Sector Report", icon: "🏢", description: "Generate sector performance report", onClick: () => openTab(REPORTS_TABS.generate) },
    { id: "trend-report", label: "Trend Report", icon: "📈", description: "Generate trend analysis report", onClick: () => openTab(REPORTS_TABS.generate) },
    { id: "export-all", label: "Export Data", icon: "📥", description: "Export reports to PDF/CSV", onClick: () => openTab(REPORTS_TABS.export) },
  ];

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 min-w-0">
        <HubLayout title="Reports" description="Generate, manage, and export reports">
          <ReportsContent />
        </HubLayout>
      </div>
      <div className="w-64 flex-shrink-0 pt-4">
        <WorkflowPanel title="Report Actions" actions={workflows} />
      </div>
    </div>
  );
}

function ReportsContent() {
  const { activeTab } = useTabs();
  return (
    <div className="space-y-4">
      {(activeTab === "reports-list" || activeTab === "reports-generate" || activeTab === "reports-dashboard" || activeTab === "reports-export") && <ReportManagement />}
    </div>
  );
}
