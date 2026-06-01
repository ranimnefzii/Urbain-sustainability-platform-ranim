import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import HubLayout from "../../components/hub/HubLayout";
import WorkflowPanel from "../../components/hub/WorkflowPanel";
import type { WorkflowAction } from "../../components/hub/WorkflowPanel";
import { useTabs } from "../../contexts/TabContext";
import SignalMap from "../signals/SignalMap";

const MAP_TABS = {
  explorer: { id: "map-explorer", label: "Explorer", icon: "🗺️" },
  heatmap: { id: "map-heatmap", label: "Heatmap", icon: "🔥" },
  clusters: { id: "map-clusters", label: "Clusters", icon: "📌" },
  geocode: { id: "map-geocode", label: "Geocode", icon: "📍" },
} as const;

export default function MapHub() {
  const navigate = useNavigate();
  const { openTab } = useTabs();

  useEffect(() => {
    openTab(MAP_TABS.explorer);
  }, []);

  const workflows: WorkflowAction[] = [
    { id: "list-view", label: "List View", icon: "📋", description: "Switch to signals list", variant: "primary", onClick: () => navigate("/signals") },
    { id: "new-signal", label: "Report Issue", icon: "🚨", description: "Submit a new signal from map", onClick: () => navigate("/signals/new") },
    { id: "heatmap", label: "Heatmap Layer", icon: "🔥", description: "Toggle density heatmap", onClick: () => openTab(MAP_TABS.heatmap) },
    { id: "clusters", label: "Cluster View", icon: "📌", description: "View signal clusters", onClick: () => openTab(MAP_TABS.clusters) },
    { id: "geocode", label: "Search Address", icon: "📍", description: "Geocode an address", onClick: () => openTab(MAP_TABS.geocode) },
  ];

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 min-w-0">
        <HubLayout title="Map Explorer" description="Interactive map with heatmap, clusters, and geocoding">
          <MapContent />
        </HubLayout>
      </div>
      <div className="w-64 flex-shrink-0 pt-4">
        <WorkflowPanel title="Map Actions" actions={workflows} />
      </div>
    </div>
  );
}

function MapContent() {
  const { activeTab } = useTabs();
  return (
    <div className="space-y-4">
      {(activeTab === "map-explorer" || activeTab === "map-heatmap" || activeTab === "map-clusters") && <SignalMap />}
      {activeTab === "map-geocode" && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 text-center text-gray-500">
          Geocoding tools available within the Map Explorer
        </div>
      )}
    </div>
  );
}
