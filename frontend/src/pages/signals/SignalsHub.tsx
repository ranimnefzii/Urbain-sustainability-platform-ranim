import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import HubLayout from "../../components/hub/HubLayout";
import WorkflowPanel from "../../components/hub/WorkflowPanel";
import type { WorkflowAction } from "../../components/hub/WorkflowPanel";
import { useTabs } from "../../contexts/TabContext";
import SignalListTab from "./SignalListTab";
import SignalMapTab from "./SignalMapTab";
import SignalCreateTab from "./SignalCreateTab";
import SignalAnalyticsTab from "./SignalAnalyticsTab";
import { useAuth } from "../../contexts/AuthContext";

const HUB_TABS = {
  list: { id: "signals-list", label: "List", icon: "📋" },
  map: { id: "signals-map", label: "Map", icon: "🗺️" },
  create: { id: "signals-create", label: "Create", icon: "➕" },
  analytics: { id: "signals-analytics", label: "Analytics", icon: "📊" },
} as const;

const PATH_TAB_MAP: Record<string, (typeof HUB_TABS)[keyof typeof HUB_TABS]> = {
  "/signals": HUB_TABS.list,
  "/signals/": HUB_TABS.list,
  "/signals/list": HUB_TABS.list,
  "/signals/map": HUB_TABS.map,
  "/signals/new": HUB_TABS.create,
  "/signals/create": HUB_TABS.create,
  "/signals/analytics": HUB_TABS.analytics,
};

export default function SignalsHub({ initialPath }: { initialPath?: string }) {
  const navigate = useNavigate();
  const { openTab, closeAll } = useTabs();
  const { user } = useAuth();

  useEffect(() => {
    const tab = initialPath ? PATH_TAB_MAP[initialPath] : PATH_TAB_MAP["/signals"];
    closeAll();
    openTab(tab || HUB_TABS.list);
  }, [initialPath]);

  const workflows: WorkflowAction[] = [
    {
      id: "new-signal",
      label: "Report an Issue",
      icon: "🚨",
      description: "Submit a new urban problem report",
      variant: "primary",
      onClick: () => { navigate("/signals/new"); openTab(HUB_TABS.create); },
    },
    {
      id: "view-map",
      label: "Explore Map",
      icon: "🗺️",
      description: "View signals on interactive map",
      onClick: () => { navigate("/signals/map"); openTab(HUB_TABS.map); },
    },
    {
      id: "view-analytics",
      label: "Trends & Stats",
      icon: "📊",
      description: "Signal analytics and predictions",
      onClick: () => { navigate("/signals/analytics"); openTab(HUB_TABS.analytics); },
    },
    {
      id: "my-signals",
      label: "My Signals",
      icon: "👤",
      description: "View signals you submitted",
      onClick: () => {
        navigate("/signals");
        closeAll();
        openTab(HUB_TABS.list);
      },
    },
  ];

  if (user?.role === "admin" || user?.role === "ADMIN") {
    workflows.push({
      id: "admin-dashboard",
      label: "Admin Panel",
      icon: "⚙️",
      description: "Full admin management dashboard",
      onClick: () => navigate("/admin"),
    });
  }

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 min-w-0">
        <HubLayout title="Signals" description="Manage, track, and analyze urban problem reports">
          <SignalContent />
        </HubLayout>
      </div>
      <div className="w-64 flex-shrink-0 pt-4">
        <WorkflowPanel title="Quick Actions" actions={workflows} />
      </div>
    </div>
  );
}

function SignalContent() {
  const { tabs, activeTab } = useTabs();
  if (tabs.length === 0 || !activeTab) {
    return <div className="text-center py-20 text-gray-400">Open a tab to get started</div>;
  }
  return (
    <div className="space-y-4">
      {activeTab === "signals-list" && <SignalListTab />}
      {activeTab === "signals-map" && <SignalMapTab />}
      {activeTab === "signals-create" && <SignalCreateTab />}
      {activeTab === "signals-analytics" && <SignalAnalyticsTab />}
    </div>
  );
}
