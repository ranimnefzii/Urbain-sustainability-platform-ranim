import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import HubLayout from "../../components/hub/HubLayout";
import WorkflowPanel from "../../components/hub/WorkflowPanel";
import type { WorkflowAction } from "../../components/hub/WorkflowPanel";
import { useTabs } from "../../contexts/TabContext";
import AdminDashboard from "./AdminDashboard";
import UserManagement from "./UserManagement";
import CategoryManagement from "./CategoryManagement";
import PriorityManagement from "./PriorityManagement";
import SectorManagement from "./SectorManagement";
import ReportManagement from "./ReportManagement";
import NotificationManagement from "./NotificationManagement";
import AuditLog from "./AuditLog";
import AIInsights from "./AIInsights";
import AdminOverview from "./AdminOverview";
import AdminUserStats from "./AdminUserStats";
import AdminSectorStats from "./AdminSectorStats";
import AdminCategoryStats from "./AdminCategoryStats";
import SystemHealth from "./SystemHealth";
import PriorityEscalationWorkflow from "./PriorityEscalationWorkflow";
import AIPipelineWorkflow from "./AIPipelineWorkflow";

const ADMIN_TABS = {
  dashboard: { id: "admin-dashboard", label: "Dashboard", icon: "📊" },
  users: { id: "admin-users", label: "Users", icon: "👥" },
  categories: { id: "admin-categories", label: "Categories", icon: "🏷️" },
  priorities: { id: "admin-priorities", label: "Priorities", icon: "🔔" },
  sectors: { id: "admin-sectors", label: "Sectors", icon: "🏢" },
  reports: { id: "admin-reports", label: "Reports", icon: "📄" },
  notifications: { id: "admin-notifications", label: "Notifications", icon: "🔔" },
  audit: { id: "admin-audit", label: "Audit Log", icon: "📋" },
  ai: { id: "admin-ai", label: "AI Insights", icon: "🤖" },
  health: { id: "admin-health", label: "System Health", icon: "❤️" },
  escalation: { id: "admin-escalation", label: "Escalation", icon: "🚨" },
  aiPipeline: { id: "admin-ai-pipeline", label: "AI Pipeline", icon: "🧠" },
  overview: { id: "admin-stats-overview", label: "Overview Stats", icon: "📈" },
  userStats: { id: "admin-stats-users", label: "User Stats", icon: "👤" },
  sectorStats: { id: "admin-stats-sectors", label: "Sector Stats", icon: "🏢" },
  categoryStats: { id: "admin-stats-categories", label: "Category Stats", icon: "🏷️" },
} as const;

/** Map URL path to the tab that should auto-open */
const PATH_TAB_MAP: Record<string, (typeof ADMIN_TABS)[keyof typeof ADMIN_TABS]> = {
  "/admin": ADMIN_TABS.dashboard,
  "/admin/": ADMIN_TABS.dashboard,
  "/admin/dashboard": ADMIN_TABS.dashboard,
  "/admin/users": ADMIN_TABS.users,
  "/admin/categories": ADMIN_TABS.categories,
  "/admin/priorities": ADMIN_TABS.priorities,
  "/admin/sectors": ADMIN_TABS.sectors,
  "/admin/reports": ADMIN_TABS.reports,
  "/admin/notifications": ADMIN_TABS.notifications,
  "/admin/audit-log": ADMIN_TABS.audit,
  "/admin/ai": ADMIN_TABS.ai,
  "/admin/ai-insights": ADMIN_TABS.ai,
  "/admin/health": ADMIN_TABS.health,
  "/admin/escalation": ADMIN_TABS.escalation,
  "/admin/ai-pipeline": ADMIN_TABS.aiPipeline,
  "/admin/stats/overview": ADMIN_TABS.overview,
  "/admin/stats/users": ADMIN_TABS.userStats,
  "/admin/stats/sectors": ADMIN_TABS.sectorStats,
  "/admin/stats/categories": ADMIN_TABS.categoryStats,
};

export default function AdminHub({ initialPath }: { initialPath?: string }) {
  const navigate = useNavigate();
  const { openTab } = useTabs();

  useEffect(() => {
    const tab = initialPath ? PATH_TAB_MAP[initialPath] : PATH_TAB_MAP["/admin"];
    if (tab) openTab(tab);
    else openTab(ADMIN_TABS.dashboard);
  }, [initialPath]);

  const workflows: WorkflowAction[] = [
    { id: "manage-users", label: "Manage Users", icon: "👥", description: "Create, edit, activate/deactivate users", onClick: () => { openTab(ADMIN_TABS.users); navigate("/admin/users"); } },
    { id: "manage-categories", label: "Categories", icon: "🏷️", description: "Organize signal categories & types", onClick: () => { openTab(ADMIN_TABS.categories); navigate("/admin/categories"); } },
    { id: "manage-priorities", label: "Priorities", icon: "🔔", description: "Configure priority levels & SLAs", onClick: () => { openTab(ADMIN_TABS.priorities); navigate("/admin/priorities"); } },
    { id: "manage-sectors", label: "Sectors", icon: "🏢", description: "Manage municipal sectors & teams", onClick: () => { openTab(ADMIN_TABS.sectors); navigate("/admin/sectors"); } },
    { id: "view-reports", label: "Reports", icon: "📄", description: "Generate and export reports", onClick: () => { openTab(ADMIN_TABS.reports); navigate("/admin/reports"); } },
    { id: "view-notifications", label: "Notifications", icon: "🔔", description: "Send and manage notifications", onClick: () => { openTab(ADMIN_TABS.notifications); navigate("/admin/notifications"); } },
    { id: "view-audit", label: "Audit Log", icon: "📋", description: "System activity audit trail", onClick: () => { openTab(ADMIN_TABS.audit); navigate("/admin/audit-log"); } },
    { id: "view-ai", label: "AI Insights", icon: "🤖", description: "AI-powered predictions & analysis", onClick: () => { openTab(ADMIN_TABS.ai); navigate("/admin/ai"); } },
    { id: "stats-overview", label: "Overview Stats", icon: "📈", description: "System-wide statistics overview", onClick: () => { openTab(ADMIN_TABS.overview); navigate("/admin/stats/overview"); } },
    { id: "stats-users", label: "User Stats", icon: "👤", description: "User statistics & activity", onClick: () => { openTab(ADMIN_TABS.userStats); navigate("/admin/stats/users"); } },
    { id: "stats-sectors", label: "Sector Stats", icon: "🏢", description: "Sector performance metrics", onClick: () => { openTab(ADMIN_TABS.sectorStats); navigate("/admin/stats/sectors"); } },
    { id: "stats-categories", label: "Category Stats", icon: "🏷️", description: "Category breakdown statistics", onClick: () => { openTab(ADMIN_TABS.categoryStats); navigate("/admin/stats/categories"); } },
    { id: "sys-health", label: "System Health", icon: "❤️", description: "System health and configuration", onClick: () => { openTab(ADMIN_TABS.health); navigate("/admin/health"); } },
    { id: "escalation", label: "Escalation", icon: "🚨", description: "Priority escalation & SLA monitoring", onClick: () => { openTab(ADMIN_TABS.escalation); navigate("/admin/escalation"); } },
    { id: "ai-pipeline", label: "AI Pipeline", icon: "🧠", description: "Run AI analysis pipeline on signals", onClick: () => { openTab(ADMIN_TABS.aiPipeline); navigate("/admin/ai-pipeline"); } },
    { id: "signals", label: "Signal Hub", icon: "📋", description: "Back to signal management", onClick: () => navigate("/signals") },
  ];

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 min-w-0">
        <HubLayout title="Administration" description="Full system management and configuration">
          <AdminContent />
        </HubLayout>
      </div>
      <div className="w-64 flex-shrink-0 pt-4">
        <WorkflowPanel title="Admin Modules" actions={workflows} />
      </div>
    </div>
  );
}

function AdminContent() {
  const { activeTab } = useTabs();
  if (!activeTab) {
    return <div className="text-center py-20 text-gray-400">Select an admin module from the sidebar</div>;
  }
  return (
    <div className="space-y-4">
      {activeTab === "admin-dashboard" && <AdminDashboard />}
      {activeTab === "admin-users" && <UserManagement />}
      {activeTab === "admin-categories" && <CategoryManagement />}
      {activeTab === "admin-priorities" && <PriorityManagement />}
      {activeTab === "admin-sectors" && <SectorManagement />}
      {activeTab === "admin-reports" && <ReportManagement />}
      {activeTab === "admin-notifications" && <NotificationManagement />}
      {activeTab === "admin-audit" && <AuditLog />}
      {activeTab === "admin-ai" && <AIInsights />}
      {activeTab === "admin-stats-overview" && <AdminOverview />}
      {activeTab === "admin-stats-users" && <AdminUserStats />}
      {activeTab === "admin-stats-sectors" && <AdminSectorStats />}
      {activeTab === "admin-stats-categories" && <AdminCategoryStats />}
      {activeTab === "admin-health" && <SystemHealth />}
      {activeTab === "admin-escalation" && <PriorityEscalationWorkflow />}
      {activeTab === "admin-ai-pipeline" && <AIPipelineWorkflow />}
    </div>
  );
}
