import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { map as mapApi, categories as categoriesApi } from "../../api/endpoints";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import type { MapNearbySignal, MapClusterItem, MapHeatmapPoint, MapGeocodeResult } from "../../types";

const TUNIS_CENTER: [number, number] = [36.8065, 10.1815];
const DEFAULT_ZOOM = 12;

const statusColors: Record<string, string> = {
  SUBMITTED: "#eab308",
  UNDER_REVIEW: "#3b82f6",
  ASSIGNED: "#6366f1",
  IN_PROGRESS: "#2563eb",
  RESOLVED: "#22c55e",
  CLOSED: "#16a34a",
  CANCELLED: "#ef4444",
  REJECTED: "#f97316",
};

const statusLabels: Record<string, string> = {
  SUBMITTED: "Soumis",
  UNDER_REVIEW: "En examen",
  ASSIGNED: "Assigné",
  IN_PROGRESS: "En cours",
  RESOLVED: "Résolu",
  CLOSED: "Fermé",
  CANCELLED: "Annulé",
  REJECTED: "Rejeté",
};

const priorityColors: Record<string, string> = {
  LOW: "#22c55e",
  MEDIUM: "#eab308",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
  NORMAL: "#3b82f6",
};

const priorityLabels: Record<string, string> = {
  LOW: "Faible",
  MEDIUM: "Moyen",
  NORMAL: "Normal",
  HIGH: "Élevé",
  CRITICAL: "Critique",
};

function getStatusColor(status: string): string {
  return statusColors[status] || "#6b7280";
}

function createIcon(color: string, selected = false, pulse = false): L.DivIcon {
  const size = 32;
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      border: ${selected ? "3px solid #1e40af" : "3px solid white"};
      border-radius: 50%;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3), ${selected ? "0 0 0 4px rgba(30,64,175,0.3)" : ""};
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 0;
      cursor: pointer;
      transition: all 0.2s;
      ${pulse ? "animation: pulse 1.5s infinite;" : ""}
    "><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 21C12 21 4 13 4 8C4 4.5 8 2 12 2C16 2 20 4.5 20 8C20 13 12 21 12 21Z"/></svg></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

function createClusterIcon(count: number): L.DivIcon {
  const size = Math.min(56, 28 + count);
  return L.divIcon({
    className: "cluster-marker",
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      border: 3px solid rgba(255,255,255,0.95);
      border-radius: 50%;
      box-shadow: 0 4px 12px rgba(99,102,241,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      transition: transform 0.2s;
    ">${count}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

function createHeatmapCircle(point: MapHeatmapPoint, maxIntensity: number): L.CircleMarker {
  const radius = Math.max(10, point.intensity * 35);
  const ratio = maxIntensity > 0 ? point.count / maxIntensity : 0;
  const color = ratio > 0.5 ? "#ef4444" : ratio > 0.25 ? "#f97316" : "#eab308";
  return L.circleMarker([point.latitude, point.longitude], {
    radius,
    color,
    fillColor: color,
    fillOpacity: Math.min(0.7, 0.15 + ratio * 0.55),
    weight: 0,
  });
}

interface FilterState {
  status: string;
  priority: string;
  category: string;
  search: string;
}

interface AnalyticsSnapshot {
  total: number;
  byStatus: Record<string, number>;
  byPriority: Record<string, number>;
  avgDistance: number;
}

export default function SignalMap() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const navigateRef = useRef(navigate);
  navigateRef.current = navigate;

  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const heatmapLayerRef = useRef<L.LayerGroup | null>(null);
  const clusterLayerRef = useRef<L.LayerGroup | null>(null);
  const circleLayerRef = useRef<L.Circle | null>(null);
  const tempMarkersRef = useRef<L.LayerGroup | null>(null);
  const routeLineRef = useRef<L.Polyline | null>(null);

  const [loading, setLoading] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [signals, setSignals] = useState<MapNearbySignal[]>([]);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showClusters, setShowClusters] = useState(true);
  const [radius, setRadius] = useState(10);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [locationError, setLocationError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [_searchResult, setSearchResult] = useState<MapGeocodeResult | null>(null);
  const [selectedSignalId, setSelectedSignalId] = useState<number | null>(null);
  const [totalNearby, setTotalNearby] = useState(0);
  const [showTools, setShowTools] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [autoRefreshInterval] = useState(30);
  const [fullscreen, setFullscreen] = useState(false);
  const [showSidePanel, setShowSidePanel] = useState(true);
  const [filters, setFilters] = useState<FilterState>({ status: "", priority: "", category: "", search: "" });
  const [_categories, setCategories] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSnapshot | null>(null);
  const [sidePanelTab, setSidePanelTab] = useState<"list" | "stats" | "detail">("list");

  const [placesQuery, setPlacesQuery] = useState("");
  const [placesResults, setPlacesResults] = useState<any[]>([]);
  const [placesLoading, setPlacesLoading] = useState(false);
  const [distOrigin, setDistOrigin] = useState("");
  const [distDest, setDistDest] = useState("");
  const [distResult, setDistResult] = useState<any>(null);
  const [distLoading, setDistLoading] = useState(false);
  const [addrToValidate, setAddrToValidate] = useState("");
  const [addrValidation, setAddrValidation] = useState<any>(null);
  const [addrLoading, setAddrLoading] = useState(false);
  const [toolsSubTab, setToolsSubTab] = useState<"places" | "distance" | "validate" | "route">("places");

  const getBounds = useCallback((): { lat_min: number; lat_max: number; lng_min: number; lng_max: number } | null => {
    if (!mapRef.current) return null;
    const b = mapRef.current.getBounds();
    return { lat_min: b.getSouthWest().lat, lat_max: b.getNorthEast().lat, lng_min: b.getSouthWest().lng, lng_max: b.getNorthEast().lng };
  }, []);

  const computeAnalytics = useCallback((signalList: MapNearbySignal[]) => {
    if (signalList.length === 0) { setAnalytics(null); return; }
    const byStatus: Record<string, number> = {};
    const byPriority: Record<string, number> = {};
    let totalDist = 0;
    signalList.forEach((s) => {
      byStatus[s.status] = (byStatus[s.status] || 0) + 1;
      const p = (s as any).priority || "NORMAL";
      byPriority[p] = (byPriority[p] || 0) + 1;
      totalDist += s.distance_km || 0;
    });
    setAnalytics({
      total: signalList.length,
      byStatus,
      byPriority,
      avgDistance: signalList.length > 0 ? totalDist / signalList.length : 0,
    });
  }, []);

  const renderMarkers = useCallback((signalList: MapNearbySignal[]) => {
    if (!markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();
    signalList.forEach((s) => {
      const color = getStatusColor(s.status);
      const isSelected = s.id === selectedSignalId;
      const icon = createIcon(color, isSelected);
      const marker = L.marker([s.latitude, s.longitude], { icon });
      const statusLabel = statusLabels[s.status] || s.status.replace(/_/g, " ");
      const priorityLabel = priorityLabels[(s as any).priority] || "";
      const priorityColor = priorityColors[(s as any).priority] || "#6b7280";
      const imgUrl = s.images && s.images.length > 0 ? (typeof s.images[0] === 'string' ? s.images[0] : null) : null;
      marker.bindPopup(`
        <div style="font-family: system-ui, sans-serif; min-width: 280px; max-width: 320px;">
          ${imgUrl ? `<div style="width:100%;height:140px;overflow:hidden;border-radius:8px 8px 0 0;margin:-12px -12px 8px -12px;background:#f3f4f6;"><img src="${imgUrl}" style="width:100%;height:100%;object-fit:cover;" onerror="this.parentElement.style.display='none'"/></div>` : ""}
          <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
            <div style="font-weight: 600; font-size: 14px; color: #111; line-height: 1.3; flex: 1;">${s.title}</div>
            <button onclick="document.querySelector('.leaflet-popup-close-button')?.click()" style="background:none;border:none;cursor:pointer;color:#999;font-size:18px;line-height:1;padding:0 0 0 8px;">×</button>
          </div>
          <div style="font-size: 11px; color: #888; margin-bottom: 8px; font-family: monospace;">${s.reference_number}</div>
          <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;">
            <span style="background:${color};color:white;padding:2px 10px;border-radius:999px;font-size:10px;font-weight:600;">${statusLabel}</span>
            ${(s as any).priority ? `<span style="background:${priorityColor};color:white;padding:2px 10px;border-radius:999px;font-size:10px;font-weight:600;">${priorityLabel}</span>` : ""}
            ${s.distance_km ? `<span style="background:#f3f4f6;color:#6b7280;padding:2px 10px;border-radius:999px;font-size:10px;">${s.distance_km.toFixed(2)} km</span>` : ""}
          </div>
          ${(s as any).category_name ? `<div style="font-size:12px;color:#6b7280;margin-bottom:4px;"><span style="font-weight:500;">Catégorie:</span> ${(s as any).category_name}</div>` : ""}
          ${s.created_at ? `<div style="font-size:11px;color:#9ca3af;margin-bottom:6px;">${new Date(s.created_at).toLocaleDateString("fr-FR", { day:"numeric",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit" })}</div>` : ""}
          <div style="font-size:10px;color:#bbb;margin-bottom:8px;">${s.latitude.toFixed(5)}, ${s.longitude.toFixed(5)}</div>
          <button onclick="window.__navigateToSignal && window.__navigateToSignal(${s.id})" style="
            background: #1d4ed8;
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            transition: background 0.2s;
          " onmouseover="this.style.background='#1e40af'" onmouseout="this.style.background='#1d4ed8'">Voir les détails →</button>
        </div>
      `);
      marker.on("click", () => {
        setSelectedSignalId(s.id);
        setSidePanelTab("detail");
      });
      markersLayerRef.current!.addLayer(marker);
    });
  }, [selectedSignalId]);

  const renderHeatmap = useCallback((points: MapHeatmapPoint[], maxIntensity: number) => {
    if (!heatmapLayerRef.current) return;
    heatmapLayerRef.current.clearLayers();
    points.forEach((p) => {
      const circle = createHeatmapCircle(p, maxIntensity);
      heatmapLayerRef.current!.addLayer(circle);
    });
  }, []);

  const renderClusters = useCallback((clusterList: MapClusterItem[]) => {
    if (!clusterLayerRef.current) return;
    clusterLayerRef.current.clearLayers();
    clusterList.forEach((c) => {
      const icon = createClusterIcon(c.signal_count);
      const marker = L.marker([c.center.latitude, c.center.longitude], { icon });
      const previewSignals = c.signals.slice(0, 5).map((s) =>
        `<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px solid #f3f4f6;"><span><strong>${s.reference_number}</strong> — ${s.title}</span><span style="color:#6b7280;font-size:10px;">${statusLabels[s.status] || s.status}</span></div>`
      ).join("");
      marker.bindPopup(`
        <div style="font-family: system-ui, sans-serif; min-width: 240px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-weight:700;font-size:15px;color:#4f46e5;">${c.signal_count} Signalements</span>
            <span style="font-size:11px;color:#9ca3af;">${c.radius_meters}m</span>
          </div>
          <div style="max-height:200px;overflow-y:auto;">${previewSignals}</div>
          ${c.signals.length > 5 ? `<div style="font-size:11px;color:#9ca3af;margin-top:6px;text-align:center;">...et ${c.signals.length - 5} autres</div>` : ""}
          <button onclick="window.__mapRef?.current?.flyTo([${c.center.latitude},${c.center.longitude}], 15)" style="
            background: #4f46e5; color:white; border:none; padding:5px 12px; border-radius:6px; font-size:11px; cursor:pointer; width:100%; margin-top:8px;
          ">Zoom sur cette zone</button>
        </div>
      `);
      clusterLayerRef.current!.addLayer(marker);
    });
  }, []);

  const fetchMapData = useCallback(async (center: [number, number], rad: number) => {
    try {
      const res = await mapApi.data({ lat: center[0], lng: center[1], radius_km: rad, zoom_level: mapRef.current?.getZoom() || DEFAULT_ZOOM, days: 30 });
      const d = res.data.data;
      if (!d) return;
      const filtered = (d.nearby?.signals || []).filter((s: MapNearbySignal) => {
        if (filters.status && s.status !== filters.status) return false;
        if (filters.priority && (s as any).priority !== filters.priority) return false;
        if (filters.search && !s.title.toLowerCase().includes(filters.search.toLowerCase()) && !s.reference_number.toLowerCase().includes(filters.search.toLowerCase())) return false;
        return true;
      });
      setSignals(filtered);
      setTotalNearby(d.nearby?.total_nearby || 0);
      renderMarkers(filtered);
      computeAnalytics(filtered);
      if (d.heatmap && showHeatmap) renderHeatmap(d.heatmap.heatmap_points, d.heatmap.max_intensity);
      if (d.clusters && showClusters) renderClusters(d.clusters.clusters);
    } catch (err) {
      console.error("Map fetch error:", err);
      const msg = err?.response?.data?.message || err?.message || "Erreur inconnue";
      toast(`Échec du chargement: ${msg}`, "error");
    }
  }, [showHeatmap, showClusters, filters, renderMarkers, renderHeatmap, renderClusters, computeAnalytics, toast]);

  const fetchHeatmap = useCallback(async () => {
    const bounds = getBounds();
    if (!bounds) return;
    try {
      const res = await mapApi.heatmap({ ...bounds, days: 30 });
      const d = res.data.data;
      if (d?.heatmap_points) renderHeatmap(d.heatmap_points, d.max_intensity);
    } catch { /* ignore */ }
  }, [getBounds, renderHeatmap]);

  const fetchClusters = useCallback(async () => {
    const bounds = getBounds();
    if (!bounds || !mapRef.current) return;
    try {
      const res = await mapApi.clusters({ ...bounds, zoom_level: mapRef.current.getZoom() });
      const d = res.data.data;
      if (d?.clusters) renderClusters(d.clusters);
    } catch { /* ignore */ }
  }, [getBounds, renderClusters]);

  const fetchCategories = useCallback(async () => {
    try {
      const res = await categoriesApi.list();
      if (res.data.data) setCategories(res.data.data);
    } catch { /* ignore */ }
  }, []);

  const initMap = useCallback((center: [number, number]) => {
    if (mapRef.current || !mapContainerRef.current) return;
    const map = L.map(mapContainerRef.current, {
      center,
      zoom: DEFAULT_ZOOM,
      zoomControl: true,
      attributionControl: true,
      zoomSnap: 0.5,
      wheelPxPerZoomLevel: 60,
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    heatmapLayerRef.current = L.layerGroup().addTo(map);
    clusterLayerRef.current = L.layerGroup().addTo(map);
    tempMarkersRef.current = L.layerGroup().addTo(map);

    mapRef.current = map;
    setMapReady(true);

    const radiusCircle = L.circle(center, {
      radius: radius * 1000,
      color: "#3b82f6",
      fillColor: "#3b82f6",
      fillOpacity: 0.06,
      weight: 2,
      dashArray: "8 8",
    }).addTo(map);
    circleLayerRef.current = radiusCircle;

    let moveTimeout: ReturnType<typeof setTimeout>;
    map.on("moveend", () => {
      const c = map.getCenter();
      setUserLocation([c.lat, c.lng]);
      clearTimeout(moveTimeout);
      moveTimeout = setTimeout(() => {
        if (showClusters) fetchClusters();
      }, 300);
    });

    map.on("click", async (e) => {
      setSelectedSignalId(null);
      try {
        const res = await mapApi.reverseGeocode(e.latlng.lat, e.latlng.lng);
        const addr = res.data.data?.formatted_address || `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
        L.popup()
          .setLatLng(e.latlng)
          .setContent(`<div style="font-family:system-ui;font-size:12px;padding:4px;"><strong>📍 ${addr}</strong><br/><span style="color:#999;font-size:10px;">${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}</span></div>`)
          .openOn(map);
      } catch { /* ignore */ }
    });

    (window as any).__navigateToSignal = (id: number) => navigateRef.current(`/signals/${id}`);
    (window as any).__mapRef = mapRef;
  }, [radius, showClusters, fetchClusters, navigate]);

  const initUserLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError("Géolocalisation non supportée");
      initMap(TUNIS_CENTER);
      setUserLocation(TUNIS_CENTER);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        setUserLocation(loc);
        initMap(loc);
      },
      () => {
        setLocationError("Position par défaut (Tunis)");
        initMap(TUNIS_CENTER);
        setUserLocation(TUNIS_CENTER);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [initMap]);

  useEffect(() => {
    initUserLocation();
    fetchCategories();
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
      delete (window as any).__navigateToSignal;
    };
  }, []);

  useEffect(() => {
    if (!mapReady || !userLocation) return;
    setLoading(true);
    fetchMapData(userLocation, radius).finally(() => setLoading(false));
  }, [mapReady, userLocation, radius, fetchMapData]);

  useEffect(() => {
    if (!mapReady || !mapRef.current) return;
    if (showHeatmap) fetchHeatmap();
    else heatmapLayerRef.current?.clearLayers();
  }, [showHeatmap, fetchHeatmap, mapReady]);

  useEffect(() => {
    if (!mapReady || !mapRef.current) return;
    if (showClusters) fetchClusters();
    else clusterLayerRef.current?.clearLayers();
  }, [showClusters, fetchClusters, mapReady]);

  useEffect(() => {
    if (!mapRef.current || !userLocation) return;
    if (circleLayerRef.current) {
      circleLayerRef.current.setLatLng(userLocation);
      circleLayerRef.current.setRadius(radius * 1000);
    }
  }, [radius, userLocation]);

  useEffect(() => {
    if (!mapReady || !userLocation || !autoRefresh) return;
    const interval = setInterval(() => {
      fetchMapData(userLocation, radius);
    }, autoRefreshInterval * 1000);
    return () => clearInterval(interval);
  }, [autoRefresh, autoRefreshInterval, mapReady, userLocation, radius, fetchMapData]);

  useEffect(() => {
    if (!mapReady || !userLocation) return;
    renderMarkers(signals);
  }, [selectedSignalId]);

  useEffect(() => {
    if (!mapReady || !userLocation) return;
    setLoading(true);
    fetchMapData(userLocation, radius).finally(() => setLoading(false));
  }, [filters.status, filters.priority, filters.search]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const res = await mapApi.geocode(searchQuery);
      const result = res.data.data as MapGeocodeResult;
      if (result?.latitude && result?.longitude) {
        setSearchResult(result);
        mapRef.current?.flyTo([result.latitude, result.longitude], 14, { duration: 1.5 });
        setUserLocation([result.latitude, result.longitude]);
        L.popup()
          .setLatLng([result.latitude, result.longitude])
          .setContent(`<div style="font-family:system-ui;font-size:13px;padding:6px;"><strong>📍 ${result.formatted_address}</strong></div>`)
          .openOn(mapRef.current!);
      }
    } catch {
      toast("Échec du géocodage. Essayez une autre adresse.", "error");
    }
  };

  const handleLocateMe = () => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        setUserLocation(loc);
        mapRef.current?.flyTo(loc, DEFAULT_ZOOM, { duration: 1 });
      },
      () => toast("Impossible d'obtenir votre position", "error")
    );
  };

  const handleRefresh = () => {
    if (!userLocation) return;
    setLoading(true);
    fetchMapData(userLocation, radius).finally(() => setLoading(false));
  };

  const toggleFullscreen = () => {
    setFullscreen((v) => !v);
    setTimeout(() => mapRef.current?.invalidateSize(), 300);
  };

  const clearTempMarkers = () => {
    tempMarkersRef.current?.clearLayers();
    routeLineRef.current?.remove();
    routeLineRef.current = null;
  };

  const exportCSV = () => {
    if (signals.length === 0) { toast("Aucun signalement à exporter", "error"); return; }
    const headers = ["ID", "Référence", "Titre", "Statut", "Priorité", "Latitude", "Longitude", "Distance (km)", "Date"];
    const rows = signals.map((s) => [
      s.id,
      s.reference_number,
      `"${s.title.replace(/"/g, '""')}"`,
      s.status,
      (s as any).priority || "",
      s.latitude,
      s.longitude,
      s.distance_km?.toFixed(3) || "",
      s.created_at || "",
    ]);
    const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8;" }); // BOM for Excel
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `signalements_carte_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    toast(`Exporté ${signals.length} signalements en CSV`, "success");
  };

  const selectedSignal = signals.find((s) => s.id === selectedSignalId);

  const quickFilters = [
    { label: "Tous", status: "", priority: "" },
    { label: "Urgent", status: "", priority: "CRITICAL" },
    { label: "En cours", status: "IN_PROGRESS", priority: "" },
    { label: "Résolu", status: "RESOLVED", priority: "" },
    { label: "Soumis", status: "SUBMITTED", priority: "" },
  ];

  // chart colors available inline in JSX

  return (
    <div className={`space-y-4 ${fullscreen ? "fixed inset-0 z-[9999] bg-white p-4" : ""}`}>
      {/* Enterprise Header */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-xl p-4 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-brand-600/20 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Carte Interactive</h1>
              <p className="text-xs text-slate-400">Explorer, analyser et gérer les signalements urbains</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {locationError && <span className="text-[10px] text-amber-400 bg-amber-400/10 px-2 py-1 rounded">{locationError}</span>}
            <button onClick={handleLocateMe} className="px-3 py-1.5 text-xs font-medium bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all flex items-center gap-1.5 border border-white/10">
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Me localiser
            </button>
            <button onClick={toggleFullscreen} className="p-1.5 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-all">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {fullscreen
                  ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M15 9h4.5M15 9V4.5M9 15v4.5M9 15H4.5M15 15h4.5M15 15v4.5" />
                  : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Controls Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-3 shadow-sm flex flex-wrap items-center gap-2">
        {/* Search */}
        <div className="flex-1 min-w-[180px] max-w-sm flex gap-1.5">
          <div className="relative flex-1">
            <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Rechercher une adresse..." className="w-full pl-8 pr-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500" />
          </div>
          <button onClick={handleSearch} className="px-3 py-1.5 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 transition-colors">OK</button>
        </div>

        {/* Radius */}
        <div className="flex items-center gap-1.5">
          <label className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Rayon</label>
          <select value={radius} onChange={(e) => setRadius(Number(e.target.value))}
            className="border border-slate-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30 bg-white">
            <option value={1}>1 km</option>
            <option value={2}>2 km</option>
            <option value={5}>5 km</option>
            <option value={10}>10 km</option>
            <option value={25}>25 km</option>
            <option value={50}>50 km</option>
          </select>
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-1.5">
          <label className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Statut</label>
          <select value={filters.status} onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
            className="border border-slate-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30 bg-white">
            <option value="">Tous</option>
            {Object.entries(statusLabels).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>

        {/* Priority Filter */}
        <div className="flex items-center gap-1.5">
          <label className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Priorité</label>
          <select value={filters.priority} onChange={(e) => setFilters((f) => ({ ...f, priority: e.target.value }))}
            className="border border-slate-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30 bg-white">
            <option value="">Toutes</option>
            {Object.entries(priorityLabels).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1.5 ml-auto">
          {/* Quick Filters */}
          <div className="hidden md:flex items-center gap-1 mr-1">
            {quickFilters.map((qf, i) => (
              <button key={i} onClick={() => setFilters({ ...filters, status: qf.status, priority: qf.priority })}
                className={`px-2 py-1 text-[10px] font-medium rounded-md transition-colors ${
                  filters.status === qf.status && filters.priority === qf.priority
                    ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}>{qf.label}</button>
            ))}
          </div>

          <div className="w-px h-5 bg-slate-200 mx-1" />

          {/* Layer Toggles */}
          <label className="flex items-center gap-1 text-[10px] font-medium text-slate-600 cursor-pointer select-none">
            <input type="checkbox" checked={showClusters} onChange={() => setShowClusters((v) => !v)} className="rounded border-slate-300 text-brand-600 focus:ring-brand-500/30 w-3 h-3" />
            <span>Groupes</span>
          </label>
          <label className="flex items-center gap-1 text-[10px] font-medium text-slate-600 cursor-pointer select-none">
            <input type="checkbox" checked={showHeatmap} onChange={() => setShowHeatmap((v) => !v)} className="rounded border-slate-300 text-brand-600 focus:ring-brand-500/30 w-3 h-3" />
            <span>Chaleur</span>
          </label>

          <div className="w-px h-5 bg-slate-200 mx-1" />

          {/* Auto-refresh */}
          <button onClick={() => setAutoRefresh((v) => !v)}
            className={`px-2 py-1 text-[10px] font-medium rounded-md transition-colors flex items-center gap-1 ${
              autoRefresh ? "bg-green-100 text-green-700 border border-green-200" : "bg-slate-100 text-slate-500 hover:bg-slate-200"
            }`}>
            <svg className={`h-3 w-3 ${autoRefresh ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {autoRefresh ? `${autoRefreshInterval}s` : "Auto"}
          </button>

          <button onClick={handleRefresh} disabled={loading}
            className="p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50">
            <svg className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>

          <div className="w-px h-5 bg-slate-200 mx-1" />

          {/* Export */}
          <button onClick={exportCSV} disabled={signals.length === 0}
            className="px-2 py-1 text-[10px] font-medium bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors disabled:opacity-40 flex items-center gap-1">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            CSV
          </button>
          <button onClick={() => setShowTools(true)}
            className="px-2 py-1 text-[10px] font-medium bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors flex items-center gap-1">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Outils
          </button>
          <button onClick={() => setShowSidePanel((v) => !v)}
            className={`p-1.5 rounded-lg transition-colors ${showSidePanel ? "bg-brand-100 text-brand-600" : "text-slate-500 hover:bg-slate-100"}`}>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Map + Side Panel */}
      <div className="flex gap-4">
        {/* Map Container */}
        <div className="flex-1 relative min-h-[500px]">
          {loading && (
            <div className="absolute inset-0 z-[1000] bg-white/60 backdrop-blur-[1px] flex items-center justify-center rounded-xl">
              <div className="bg-white shadow-xl rounded-xl p-5 flex items-center gap-3">
                <LoadingSpinner size="md" />
                <span className="text-sm text-slate-600 font-medium">Chargement des données...</span>
              </div>
            </div>
          )}
          <div ref={mapContainerRef} className="w-full h-[620px] rounded-xl border border-slate-200 z-0 shadow-sm" />

          {/* Analytics Widget */}
          {analytics && showSidePanel && (
            <div className="absolute top-3 left-3 z-[1000] bg-white/95 backdrop-blur rounded-xl border border-slate-200 p-3 shadow-lg max-w-[200px]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Analyses</span>
                <span className="text-lg font-bold text-slate-900">{analytics.total}</span>
              </div>
              <div className="space-y-1">
                {Object.entries(analytics.byStatus).sort(([, a], [, b]) => b - a).slice(0, 4).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between text-[10px]">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full" style={{ background: getStatusColor(status) }} />
                      <span className="text-slate-600">{statusLabels[status] || status}</span>
                    </div>
                    <span className="font-medium text-slate-800">{count}</span>
                  </div>
                ))}
              </div>
              {analytics.avgDistance > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100 text-[10px] text-slate-500">
                  Distance moy. <span className="font-medium text-slate-700">{analytics.avgDistance.toFixed(2)} km</span>
                </div>
              )}
            </div>
          )}

          {/* Legend */}
          <div className="absolute bottom-4 right-3 z-[1000] bg-white/95 backdrop-blur rounded-xl border border-slate-200 p-3 shadow-lg text-[10px]">
            <p className="font-semibold text-slate-700 mb-1.5 text-[10px] uppercase tracking-wider">Légende</p>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1">
              {Object.entries(statusLabels).map(([status, label]) => (
                <div key={status} className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full inline-block flex-shrink-0" style={{ background: getStatusColor(status) }} />
                  <span className="text-slate-600 whitespace-nowrap">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Side Panel */}
        {showSidePanel && (
          <div className="w-80 bg-white rounded-xl border border-slate-200 flex flex-col shadow-sm max-h-[620px]">
            {/* Panel Tabs */}
            <div className="flex border-b border-slate-200">
              {(["list", "stats", "detail"] as const).map((tab) => (
                <button key={tab} onClick={() => setSidePanelTab(tab)}
                  className={`flex-1 py-2.5 text-[11px] font-medium text-center transition-colors ${
                    sidePanelTab === tab
                      ? "text-brand-600 border-b-2 border-brand-600 bg-brand-50/50"
                      : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                  }`}>
                  {tab === "list" ? `Liste (${signals.length})` : tab === "stats" ? "Statistiques" : "Détail"}
                </button>
              ))}
            </div>

            {/* List Tab */}
            {sidePanelTab === "list" && (
              <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
                <div className="px-3 py-2 bg-slate-50/50 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500">
                    {totalNearby > signals.length
                      ? `${signals.length} / ${totalNearby} signalements`
                      : `${signals.length} signalements`}
                  </span>
                  <div className="relative">
                    <svg className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <input type="text" value={filters.search} onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
                      placeholder="Filtrer..." className="pl-7 pr-2 py-1 border border-slate-200 rounded-lg text-[10px] w-32 focus:outline-none focus:ring-1 focus:ring-brand-500/30" />
                  </div>
                </div>
                {signals.length === 0 ? (
                  <div className="p-6 text-center">
                    <svg className="h-10 w-10 text-slate-300 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                    <p className="text-xs text-slate-400">Aucun signalement trouvé</p>
                    <p className="text-[10px] text-slate-300 mt-1">Essayez d'ajuster les filtres ou le rayon</p>
                  </div>
                ) : (
                  signals.map((s) => (
                    <div key={s.id}
                      onClick={() => { setSelectedSignalId(s.id); setSidePanelTab("detail"); }}
                      onMouseEnter={() => {
                        if (!mapRef.current || !tempMarkersRef.current) return;
                        tempMarkersRef.current.clearLayers();
                        const color = getStatusColor(s.status);
                        const m = L.marker([s.latitude, s.longitude], { icon: createIcon(color, false, true) }).addTo(tempMarkersRef.current);
                        m.bindPopup(`<div style="font-family:system-ui;font-size:11px;padding:2px;"><strong>${s.title}</strong></div>`).openPopup();
                      }}
                      onMouseLeave={() => tempMarkersRef.current?.clearLayers()}
                      className={`p-3 cursor-pointer transition-all ${
                        selectedSignalId === s.id ? "bg-brand-50 border-l-2 border-brand-500 shadow-sm" : "hover:bg-slate-50 border-l-2 border-transparent"
                      }`}>
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-medium text-slate-900 truncate">{s.title}</p>
                          <p className="text-[10px] text-slate-400 font-mono mt-0.5">{s.reference_number}</p>
                        </div>
                        <span className="text-[10px] text-slate-400 whitespace-nowrap">{s.distance_km?.toFixed(1)} km</span>
                      </div>
                      <div className="flex items-center gap-1.5 mt-1.5">
                        <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded text-white" style={{ background: getStatusColor(s.status) }}>
                          {statusLabels[s.status] || s.status.replace(/_/g, " ")}
                        </span>
                        {(s as any).priority && (
                          <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded text-white" style={{ background: priorityColors[(s as any).priority] || "#6b7280" }}>
                            {priorityLabels[(s as any).priority] || (s as any).priority}
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Stats Tab */}
            {sidePanelTab === "stats" && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {analytics ? (
                  <>
                    {/* Bar chart - Status */}
                    <div>
                      <h3 className="text-[11px] font-semibold text-slate-700 mb-2 uppercase tracking-wider">Par Statut</h3>
                      <div className="space-y-1.5">
                        {Object.entries(analytics.byStatus).sort(([, a], [, b]) => b - a).map(([status, count]) => {
                          const maxVal = Math.max(...Object.values(analytics.byStatus));
                          const pct = maxVal > 0 ? (count / maxVal) * 100 : 0;
                          return (
                            <div key={status} className="flex items-center gap-2">
                              <span className="text-[10px] text-slate-500 w-20 truncate">{statusLabels[status] || status}</span>
                              <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
                                <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: getStatusColor(status) }} />
                              </div>
                              <span className="text-[10px] font-medium text-slate-700 w-6 text-right">{count}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Bar chart - Priority */}
                    {Object.keys(analytics.byPriority).length > 0 && (
                      <div>
                        <h3 className="text-[11px] font-semibold text-slate-700 mb-2 uppercase tracking-wider">Par Priorité</h3>
                        <div className="space-y-1.5">
                          {Object.entries(analytics.byPriority).sort(([, a], [, b]) => b - a).map(([priority, count]) => {
                            const maxVal = Math.max(...Object.values(analytics.byPriority));
                            const pct = maxVal > 0 ? (count / maxVal) * 100 : 0;
                            return (
                              <div key={priority} className="flex items-center gap-2">
                                <span className="text-[10px] text-slate-500 w-20 truncate">{priorityLabels[priority] || priority}</span>
                                <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
                                  <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: priorityColors[priority] || "#6b7280" }} />
                                </div>
                                <span className="text-[10px] font-medium text-slate-700 w-6 text-right">{count}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Donut chart placeholder */}
                    <div>
                      <h3 className="text-[11px] font-semibold text-slate-700 mb-2 uppercase tracking-wider">Répartition</h3>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(analytics.byStatus).sort(([, a], [, b]) => b - a).map(([status, count]) => (
                          <div key={status} className="bg-slate-50 rounded-lg px-2.5 py-1.5 flex items-center gap-2">
                            <span className="w-2.5 h-2.5 rounded-full" style={{ background: getStatusColor(status) }} />
                            <span className="text-[10px] text-slate-600">{statusLabels[status] || status}</span>
                            <span className="text-[10px] font-bold text-slate-800">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-brand-50 to-blue-50 rounded-lg p-3 text-center">
                      <p className="text-[10px] text-slate-500">Distance moyenne</p>
                      <p className="text-lg font-bold text-brand-700">{analytics.avgDistance.toFixed(2)} km</p>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8 text-slate-400 text-xs">Aucune donnée disponible</div>
                )}
              </div>
            )}

            {/* Detail Tab */}
            {sidePanelTab === "detail" && (
              <div className="flex-1 overflow-y-auto p-4">
                {selectedSignal ? (
                  <div className="space-y-3">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">{selectedSignal.title}</h3>
                      <p className="text-[10px] text-slate-400 font-mono">{selectedSignal.reference_number}</p>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded text-white" style={{ background: getStatusColor(selectedSignal.status) }}>
                        {statusLabels[selectedSignal.status] || selectedSignal.status.replace(/_/g, " ")}
                      </span>
                      {(selectedSignal as any).priority && (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded text-white" style={{ background: priorityColors[(selectedSignal as any).priority] || "#6b7280" }}>
                          {priorityLabels[(selectedSignal as any).priority] || (selectedSignal as any).priority}
                        </span>
                      )}
                    </div>
                    {(selectedSignal as any).category_name && (
                      <div className="text-xs text-slate-600">
                        <span className="font-medium">Catégorie:</span> {(selectedSignal as any).category_name}
                      </div>
                    )}
                    <div className="text-xs text-slate-500">
                      <span className="font-medium">Position:</span> {selectedSignal.latitude.toFixed(5)}, {selectedSignal.longitude.toFixed(5)}
                    </div>
                    {selectedSignal.distance_km && (
                      <div className="text-xs text-slate-500">
                        <span className="font-medium">Distance:</span> {selectedSignal.distance_km.toFixed(2)} km
                      </div>
                    )}
                    {selectedSignal.created_at && (
                      <div className="text-xs text-slate-500">
                        <span className="font-medium">Créé le:</span> {new Date(selectedSignal.created_at).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                      </div>
                    )}
                    <button onClick={() => navigate(`/signals/${selectedSignal.id}`)}
                      className="w-full py-2 bg-brand-600 text-white text-xs font-medium rounded-lg hover:bg-brand-700 transition-colors">
                      Voir la fiche complète →
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <svg className="h-8 w-8 text-slate-300 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-xs text-slate-400">Cliquez sur un signalement sur la carte pour voir ses détails</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Map Tools Modal */}
      <Modal open={showTools} onClose={() => setShowTools(false)} title="Outils cartographiques" size="lg">
        <div className="space-y-4">
          <div className="flex gap-2 border-b border-slate-200 pb-3 overflow-x-auto">
            {(["places", "distance", "route", "validate"] as const).map((tab) => (
              <button key={tab} onClick={() => { setToolsSubTab(tab); setPlacesResults([]); setDistResult(null); setAddrValidation(null); clearTempMarkers(); }}
                className={`px-3 py-1.5 text-xs rounded-lg font-medium whitespace-nowrap transition-colors ${
                  toolsSubTab === tab ? "bg-brand-600 text-white shadow-sm" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}>
                {tab === "places" ? "🔍 Lieux" : tab === "distance" ? "📏 Distance" : tab === "route" ? "🗺️ Itinéraire" : "✅ Validation"}
              </button>
            ))}
          </div>

          {/* Places Tab */}
          {toolsSubTab === "places" && (
            <div className="space-y-3">
              <p className="text-xs text-slate-500">Recherchez des points d'intérêt à proximité de votre position</p>
              <div className="flex gap-2">
                <input type="text" value={placesQuery} onChange={(e) => setPlacesQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && placesQuery.trim()) searchPlaces(); }}
                  placeholder="Ex: hôpital, école, pharmacie..."
                  className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30" />
                <button onClick={searchPlaces} disabled={placesLoading || !placesQuery.trim()}
                  className="px-4 py-2 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors">
                  {placesLoading ? <LoadingSpinner size="sm" /> : "Rechercher"}
                </button>
              </div>
              {placesResults.length > 0 && (
                <div className="max-h-60 overflow-y-auto divide-y divide-slate-100 border border-slate-200 rounded-lg">
                  {placesResults.map((p, i) => (
                    <div key={i} className="p-3 hover:bg-brand-50 cursor-pointer transition-colors"
                      onClick={() => { mapRef.current?.flyTo([p.latitude, p.longitude], 15, { duration: 1.5 }); setShowTools(false); }}>
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-xs font-medium text-slate-800">{p.name}</p>
                          <p className="text-[10px] text-slate-400 mt-0.5">{p.formatted_address}</p>
                          {p.types && <p className="text-[9px] text-slate-300 mt-0.5">{p.types.slice(0, 3).join(", ")}</p>}
                        </div>
                        {p.rating && (
                          <span className="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-medium">{p.rating} ★</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {placesResults.length === 0 && !placesLoading && (
                <div className="text-center py-6">
                  <svg className="h-8 w-8 text-slate-300 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                  <p className="text-xs text-slate-400">Recherchez des lieux autour de vous</p>
                </div>
              )}
            </div>
          )}

          {/* Distance Tab */}
          {toolsSubTab === "distance" && (
            <div className="space-y-3">
              <p className="text-xs text-slate-500">Calculez la distance entre deux adresses</p>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Adresse de départ</label>
                <div className="flex gap-2">
                  <input type="text" value={distOrigin} onChange={(e) => setDistOrigin(e.target.value)}
                    placeholder="Ex: Tunis Centre" className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30" />
                  <button onClick={() => { if (userLocation) { mapApi.reverseGeocode(userLocation[0], userLocation[1]).then((r) => setDistOrigin(r.data.data?.formatted_address || "Position actuelle")).catch(() => {}); } }}
                    className="px-2 py-1 text-[10px] bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200" title="Utiliser ma position">
                    📍
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Adresse de destination</label>
                <input type="text" value={distDest} onChange={(e) => setDistDest(e.target.value)}
                  placeholder="Ex: La Marsa" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30" />
              </div>
              <button onClick={calculateDistance} disabled={distLoading || !distOrigin.trim() || !distDest.trim()}
                className="px-4 py-2 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 disabled:opacity-50 w-full transition-colors">
                {distLoading ? "Calcul en cours..." : "Calculer la distance"}
              </button>
              {distResult && (
                <div className="bg-brand-50 rounded-xl p-4 text-xs space-y-2 border border-brand-100">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Distance</span>
                    <span className="font-bold text-lg text-brand-700">{distResult.distance_text}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Durée estimée</span>
                    <span className="font-semibold text-slate-800">{distResult.duration_text}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Mode</span>
                    <span className="text-slate-600 capitalize">{distResult.mode || "voiture"}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Route Tab */}
          {toolsSubTab === "route" && (
            <div className="space-y-3">
              <p className="text-xs text-slate-500">Calculez un itinéraire entre deux points</p>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Point de départ</label>
                <input type="text" value={distOrigin} onChange={(e) => setDistOrigin(e.target.value)}
                  placeholder="Ex: Tunis" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30" />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Point d'arrivée</label>
                <input type="text" value={distDest} onChange={(e) => setDistDest(e.target.value)}
                  placeholder="Ex: Sousse" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30" />
              </div>
              <button onClick={calculateRoute} disabled={distLoading || !distOrigin.trim() || !distDest.trim()}
                className="px-4 py-2 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 disabled:opacity-50 w-full transition-colors">
                {distLoading ? "Calcul en cours..." : "Calculer l'itinéraire"}
              </button>
              {distResult && (
                <div className="bg-green-50 rounded-xl p-4 text-xs space-y-2 border border-green-100">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Distance</span>
                    <span className="font-bold text-lg text-green-700">{distResult.distance_text}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Durée estimée</span>
                    <span className="font-semibold text-slate-800">{distResult.duration_text}</span>
                  </div>
                  {distResult.mode && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Mode</span>
                      <span className="text-slate-600 capitalize">{distResult.mode}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Validate Tab */}
          {toolsSubTab === "validate" && (
            <div className="space-y-3">
              <p className="text-xs text-slate-500">Validez et géocodez une adresse</p>
              <div className="flex gap-2">
                <input type="text" value={addrToValidate} onChange={(e) => setAddrToValidate(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && addrToValidate.trim()) validateAddress(); }}
                  placeholder="Entrez une adresse à valider..."
                  className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/30" />
                <button onClick={validateAddress} disabled={addrLoading || !addrToValidate.trim()}
                  className="px-4 py-2 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors">
                  {addrLoading ? <LoadingSpinner size="sm" /> : "Valider"}
                </button>
              </div>
              {addrValidation && (
                <div className={`rounded-xl p-4 text-xs space-y-2 border ${
                  addrValidation.is_valid ? "bg-green-50 border-green-100" : "bg-red-50 border-red-100"
                }`}>
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${addrValidation.is_valid ? "bg-green-500" : "bg-red-500"}`} />
                    <span className={`font-semibold ${addrValidation.is_valid ? "text-green-800" : "text-red-800"}`}>
                      {addrValidation.is_valid ? "Adresse valide ✓" : "Adresse invalide ✗"}
                    </span>
                    {addrValidation.confidence && (
                      <span className="text-[10px] text-slate-400 ml-auto">Confiance: {addrValidation.confidence}</span>
                    )}
                  </div>
                  {addrValidation.geocoded?.formatted_address && (
                    <div className="bg-white/60 rounded-lg p-2 mt-1">
                      <p className="text-[10px] text-slate-400">Adresse géocodée:</p>
                      <p className="text-xs font-medium text-slate-700">{addrValidation.geocoded.formatted_address}</p>
                      <p className="text-[9px] text-slate-400 mt-0.5">
                        {addrValidation.geocoded.latitude?.toFixed(5)}, {addrValidation.geocoded.longitude?.toFixed(5)}
                      </p>
                    </div>
                  )}
                  {addrValidation.issues && addrValidation.issues.length > 0 && (
                    <div className="bg-red-50/80 rounded-lg p-2">
                      <p className="text-[10px] font-medium text-red-700 mb-1">Problèmes détectés:</p>
                      <ul className="list-disc list-inside text-[10px] text-red-600 space-y-0.5">
                        {addrValidation.issues.map((issue: string, i: number) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {addrValidation.is_valid && addrValidation.geocoded?.latitude && (
                    <button onClick={() => { mapRef.current?.flyTo([addrValidation.geocoded.latitude, addrValidation.geocoded.longitude], 15); setShowTools(false); }}
                      className="w-full py-1.5 bg-brand-600 text-white rounded-lg text-[10px] font-medium hover:bg-brand-700 transition-colors">
                      Voir sur la carte
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );

  async function searchPlaces() {
    if (!placesQuery.trim()) return;
    setPlacesLoading(true);
    try {
      const r = await mapApi.searchPlaces({ query: placesQuery, latitude: userLocation?.[0], longitude: userLocation?.[1] });
      setPlacesResults(r.data.data?.places || []);
      if (r.data.data?.places?.length === 0) toast("Aucun lieu trouvé", "info");
    } catch { toast("Recherche de lieux échouée", "error"); }
    finally { setPlacesLoading(false); }
  }

  async function calculateDistance() {
    if (!distOrigin.trim() || !distDest.trim()) return;
    setDistLoading(true);
    setDistResult(null);
    clearTempMarkers();
    try {
      const [geoO, geoD] = await Promise.all([mapApi.geocode(distOrigin), mapApi.geocode(distDest)]);
      const o = geoO.data.data;
      const d = geoD.data.data;
      if (!o?.latitude || !d?.latitude) { toast("Impossible de géocoder les adresses", "error"); return; }
      const r = await mapApi.distance({ origin_lat: o.latitude, origin_lng: o.longitude, dest_lat: d.latitude, dest_lng: d.longitude });
      setDistResult(r.data.data);
      const midLat = (o.latitude + d.latitude) / 2;
      const midLng = (o.longitude + d.longitude) / 2;
      mapRef.current?.flyTo([midLat, midLng], 11, { duration: 1.5 });
      if (tempMarkersRef.current) {
        const m1 = L.marker([o.latitude, o.longitude], { icon: createIcon("#22c55e") }).addTo(tempMarkersRef.current);
        m1.bindPopup(`<b>Départ:</b> ${o.formatted_address}`).openPopup();
        const m2 = L.marker([d.latitude, d.longitude], { icon: createIcon("#ef4444") }).addTo(tempMarkersRef.current);
        m2.bindPopup(`<b>Arrivée:</b> ${d.formatted_address}`);
        const line = L.polyline([[o.latitude, o.longitude], [d.latitude, d.longitude]], {
          color: "#6366f1", weight: 3, opacity: 0.7, dashArray: "10 10",
        }).addTo(tempMarkersRef.current);
        routeLineRef.current = line;
      }
    } catch { toast("Calcul de distance échoué", "error"); }
    finally { setDistLoading(false); }
  }

  async function calculateRoute() {
    if (!distOrigin.trim() || !distDest.trim()) return;
    setDistLoading(true);
    setDistResult(null);
    clearTempMarkers();
    try {
      const [geoO, geoD] = await Promise.all([mapApi.geocode(distOrigin), mapApi.geocode(distDest)]);
      const o = geoO.data.data;
      const d = geoD.data.data;
      if (!o?.latitude || !d?.latitude) { toast("Impossible de géocoder les adresses", "error"); return; }
      const r = await mapApi.route({ origin_lat: o.latitude, origin_lng: o.longitude, dest_lat: d.latitude, dest_lng: d.longitude });
      setDistResult(r.data.data);
      const midLat = (o.latitude + d.latitude) / 2;
      const midLng = (o.longitude + d.longitude) / 2;
      mapRef.current?.flyTo([midLat, midLng], 11, { duration: 1.5 });
      if (tempMarkersRef.current) {
        const m1 = L.marker([o.latitude, o.longitude], { icon: createIcon("#22c55e") }).addTo(tempMarkersRef.current);
        m1.bindPopup(`<b>Départ:</b> ${o.formatted_address}`).openPopup();
        const m2 = L.marker([d.latitude, d.longitude], { icon: createIcon("#ef4444") }).addTo(tempMarkersRef.current);
        m2.bindPopup(`<b>Arrivée:</b> ${d.formatted_address}`);
        const line = L.polyline([[o.latitude, o.longitude], [d.latitude, d.longitude]], {
          color: "#22c55e", weight: 4, opacity: 0.8,
        }).addTo(tempMarkersRef.current);
        routeLineRef.current = line;
      }
    } catch { toast("Calcul d'itinéraire échoué", "error"); }
    finally { setDistLoading(false); }
  }

  async function validateAddress() {
    if (!addrToValidate.trim()) return;
    setAddrLoading(true);
    try {
      const r = await mapApi.validateAddress(addrToValidate);
      setAddrValidation(r.data.data);
    } catch { toast("Validation d'adresse échouée", "error"); }
    finally { setAddrLoading(false); }
  }
}
