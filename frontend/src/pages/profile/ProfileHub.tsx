import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import HubLayout from "../../components/hub/HubLayout";
import WorkflowPanel from "../../components/hub/WorkflowPanel";
import type { WorkflowAction } from "../../components/hub/WorkflowPanel";
import { useTabs } from "../../contexts/TabContext";
import Profile from "./Profile";

const PROFILE_TABS = {
  profile: { id: "profile-main", label: "Profile", icon: "👤" },
  password: { id: "profile-password", label: "Password", icon: "🔑" },
  notifications: { id: "profile-notifications", label: "Notifications", icon: "🔔" },
  activity: { id: "profile-activity", label: "Activity", icon: "📊" },
} as const;

export default function ProfileHub() {
  const navigate = useNavigate();
  const { openTab } = useTabs();

  useEffect(() => {
    openTab(PROFILE_TABS.profile);
  }, []);

  const workflows: WorkflowAction[] = [
    { id: "my-signals", label: "My Signals", icon: "📋", description: "View your submitted signals", variant: "primary", onClick: () => navigate("/signals") },
    { id: "change-password", label: "Change Password", icon: "🔑", description: "Update your password", onClick: () => openTab(PROFILE_TABS.password) },
    { id: "preferences", label: "Notifications", icon: "🔔", description: "Manage notification preferences", onClick: () => openTab(PROFILE_TABS.notifications) },
    { id: "activity", label: "Activity Log", icon: "📊", description: "View your recent activity", onClick: () => openTab(PROFILE_TABS.activity) },
  ];

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 min-w-0">
        <HubLayout title="My Profile" description="Manage your account settings and preferences">
          <ProfileContent />
        </HubLayout>
      </div>
      <div className="w-64 flex-shrink-0 pt-4">
        <WorkflowPanel title="Account Actions" actions={workflows} />
      </div>
    </div>
  );
}

function ProfileContent() {
  const { activeTab } = useTabs();
  return (
    <div className="space-y-4">
      {(activeTab === "profile-main" || activeTab === "profile-password" || activeTab === "profile-notifications") && <Profile />}
      {activeTab === "profile-activity" && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center text-gray-500">
          Your recent activity will appear here
        </div>
      )}
    </div>
  );
}
