import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { map as mapApi } from "../../api/endpoints";
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

function getStatusColor(status: string): string {
  return statusColors[status] || "#6b7280";
}

function createIcon(color: string, count?: number): L.DivIcon {
  const size = count && count > 1 ? Math.min(48, 28 + count * 2) : 28;
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      border: 3px solid white;
      border-radius: 50%;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: ${count && count > 1 ? "11px" : "0"};
      cursor: pointer;
      transition: transform 0.2s;
    ">${count && count > 1 ? count : ""}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

function createClusterIcon(count: number): L.DivIcon {
  const size = Math.min(60, 30 + count);
  return L.divIcon({
    className: "cluster-marker",
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      background: rgba(99,102,241,0.85);
      border: 3px solid rgba(255,255,255,0.9);
      border-radius: 50%;
      box-shadow: 0 2px 8px rgba(99,102,241,0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 13px;
      cursor: pointer;
    ">${count}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

function createHeatmapCircle(point: MapHeatmapPoint, maxIntensity: number): L.CircleMarker {
  const radius = Math.max(8, point.intensity * 40);
  const opacity = Math.min(0.8, 0.2 + point.count / maxIntensity * 0.6);
  return L.circleMarker([point.latitude, point.longitude], {
    radius,
    color: "#ef4444",
    fillColor: point.count > maxIntensity * 0.5 ? "#ef4444" : point.count > maxIntensity * 0.25 ? "#f97316" : "#eab308",
    fillOpacity: opacity,
    weight: 0,
  });
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

  const [loading, setLoading] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [signals, setSignals] = useState<MapNearbySignal[]>([]);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showClusters, setShowClusters] = useState(true);
  const [radius, setRadius] = useState(5);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [locationError, setLocationError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResult, setSearchResult] = useState<MapGeocodeResult | null>(null);
  const [selectedSignal, setSelectedSignal] = useState<MapNearbySignal | null>(null);
  const [totalNearby, setTotalNearby] = useState(0);
  const [showTools, setShowTools] = useState(false);
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

  const fetchMapData = useCallback(async (center: [number, number], rad: number, _status?: string) => {
    try {
      const res = await mapApi.data({ lat: center[0], lng: center[1], radius_km: rad, zoom_level: mapRef.current?.getZoom() || DEFAULT_ZOOM, days: 30 });
      const d = res.data.data;
      if (!d) return;
      setSignals(d.nearby?.signals || []);
      setTotalNearby(d.nearby?.total_nearby || 0);
      renderMarkers(d.nearby?.signals || []);
      if (d.heatmap && showHeatmap) renderHeatmap(d.heatmap.heatmap_points, d.heatmap.max_intensity);
      if (d.clusters && showClusters) renderClusters(d.clusters.clusters);
    } catch {
      toast("Failed to load map data", "error");
    }
  }, [showHeatmap, showClusters, toast]);

  const fetchHeatmap = useCallback(async () => {
    const bounds = getBounds();
    if (!bounds) return;
    try {
      const res = await mapApi.heatmap({ ...bounds, days: 30 });
      const d = res.data.data;
      if (d?.heatmap_points) renderHeatmap(d.heatmap_points, d.max_intensity);
    } catch { /* ignore */ }
  }, [getBounds]);

  const fetchClusters = useCallback(async () => {
    const bounds = getBounds();
    if (!bounds || !mapRef.current) return;
    try {
      const res = await mapApi.clusters({ ...bounds, zoom_level: mapRef.current.getZoom() });
      const d = res.data.data;
      if (d?.clusters) renderClusters(d.clusters);
    } catch { /* ignore */ }
  }, [getBounds]);

  const renderMarkers = useCallback((signalList: MapNearbySignal[]) => {
    if (!markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();
    signalList.forEach((s) => {
      const color = getStatusColor(s.status);
      const icon = createIcon(color);
      const marker = L.marker([s.latitude, s.longitude], { icon });
      marker.bindPopup(`
        <div style="font-family: system-ui, sans-serif; min-width: 220px;">
          <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${s.title}</div>
          <div style="font-size: 12px; color: #666; margin-bottom: 6px;">${s.reference_number}</div>
          <div style="display: flex; gap: 8px; margin-bottom: 6px;">
            <span style="
              background: ${color};
              color: white;
              padding: 2px 8px;
              border-radius: 999px;
              font-size: 11px;
              font-weight: 500;
            ">${s.status.replace(/_/g, " ")}</span>
            <span style="font-size: 11px; color: #666; align-self: center;">
              ${s.distance_km ? `${s.distance_km.toFixed(2)} km` : ""}
            </span>
          </div>
          <div style="font-size: 11px; color: #999; margin-bottom: 6px;">
            ${s.latitude.toFixed(4)}, ${s.longitude.toFixed(4)}
          </div>
          <button onclick="window.__navigateToSignal && window.__navigateToSignal(${s.id})" style="
            background: #2563eb;
            color: white;
            border: none;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            width: 100%;
          ">View Details</button>
        </div>
      `);
      markersLayerRef.current!.addLayer(marker);
    });
  }, []);

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
        `<div style="font-size: 12px; padding: 2px 0;"><strong>${s.reference_number}</strong> — ${s.title}</div>`
      ).join("");
      marker.bindPopup(`
        <div style="font-family: system-ui, sans-serif; min-width: 200px;">
          <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${c.signal_count} Signals</div>
          <div style="font-size: 12px; color: #666; margin-bottom: 8px;">Radius: ${c.radius_meters}m</div>
          ${previewSignals}
          ${c.signals.length > 5 ? `<div style="font-size: 11px; color: #999; margin-top: 4px;">...and ${c.signals.length - 5} more</div>` : ""}
        </div>
      `);
      clusterLayerRef.current!.addLayer(marker);
    });
  }, []);

  const initMap = useCallback((center: [number, number]) => {
    if (mapRef.current || !mapContainerRef.current) return;
    const map = L.map(mapContainerRef.current, {
      center,
      zoom: DEFAULT_ZOOM,
      zoomControl: true,
      attributionControl: true,
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);
    markersLayerRef.current = L.layerGroup().addTo(map);
    heatmapLayerRef.current = L.layerGroup().addTo(map);
    clusterLayerRef.current = L.layerGroup().addTo(map);
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

    map.on("moveend", () => {
      const c = map.getCenter();
      setUserLocation([c.lat, c.lng]);
      if (showClusters) fetchClusters();
    });
    map.on("click", async (e) => {
      try {
        const res = await mapApi.reverseGeocode(e.latlng.lat, e.latlng.lng);
        const addr = res.data.data?.formatted_address || `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
        L.popup()
          .setLatLng(e.latlng)
          .setContent(`<div style="font-family: system-ui; font-size: 12px; padding: 4px;"><strong>${addr}</strong></div>`)
          .openOn(map);
      } catch { /* ignore */ }
    });

    (window as any).__navigateToSignal = (id: number) => navigateRef.current(`/signals/${id}`);
  }, [radius, showClusters, fetchClusters, navigate]);

  const initUserLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation not supported");
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
        setLocationError("Using default location (Tunis)");
        initMap(TUNIS_CENTER);
        setUserLocation(TUNIS_CENTER);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [initMap]);

  useEffect(() => {
    initUserLocation();
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
    fetchMapData(userLocation, radius, statusFilter || undefined).finally(() => setLoading(false));
  }, [mapReady, userLocation, radius, statusFilter, fetchMapData]);

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
          .setContent(`<div style="font-family: system-ui; font-size: 13px; padding: 6px;"><strong>${result.formatted_address}</strong></div>`)
          .openOn(mapRef.current!);
      }
    } catch {
      toast("Geocoding failed. Try a different address.", "error");
    }
  };

  const handleLocateMe = () => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        setUserLocation(loc);
        mapRef.current?.flyTo(loc, DEFAULT_ZOOM, { duration: 1 });
      },
      () => toast("Could not get your location", "error")
    );
  };

  const handleRefresh = () => {
    if (!userLocation) return;
    setLoading(true);
    fetchMapData(userLocation, radius, statusFilter || undefined).finally(() => setLoading(false));
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Signal Map</h1>
          <p className="text-sm text-gray-500">Interactive map of citizen-reported signals</p>
        </div>
        <div className="flex items-center gap-2">
          {locationError && <span className="text-xs text-amber-600">{locationError}</span>}
          <button onClick={handleLocateMe} className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-1.5">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            Locate Me
          </button>
        </div>
      </div>

      {/* Controls Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-3 flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[200px] max-w-md flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search address or place..."
            className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button onClick={handleSearch} className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            Search
          </button>
        </div>

        {/* Radius */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-500">Radius:</label>
          <select value={radius} onChange={(e) => setRadius(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value={1}>1 km</option>
            <option value={2}>2 km</option>
            <option value={5}>5 km</option>
            <option value={10}>10 km</option>
            <option value={25}>25 km</option>
            <option value={50}>50 km</option>
          </select>
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-500">Status:</label>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">All</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="ASSIGNED">Assigned</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>

        {/* Toggle Layers */}
        <div className="flex items-center gap-3 ml-auto">
          <label className="flex items-center gap-1.5 text-sm cursor-pointer">
            <input type="checkbox" checked={showClusters} onChange={() => setShowClusters((v) => !v)} className="rounded text-blue-600" />
            <span className="text-gray-600 text-xs">Clusters</span>
          </label>
          <label className="flex items-center gap-1.5 text-sm cursor-pointer">
            <input type="checkbox" checked={showHeatmap} onChange={() => setShowHeatmap((v) => !v)} className="rounded text-blue-600" />
            <span className="text-gray-600 text-xs">Heatmap</span>
          </label>
          <button onClick={handleRefresh} disabled={loading}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 flex items-center gap-1">
            <svg className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <button onClick={() => setShowTools(true)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-1">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Tools
          </button>
        </div>
      </div>

      {/* Map + Side Panel */}
      <div className="flex gap-4">
        {/* Map Container */}
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 z-[1000] bg-white/50 flex items-center justify-center rounded-lg">
              <LoadingSpinner size="md" />
            </div>
          )}
          <div ref={mapContainerRef} className="w-full h-[600px] rounded-lg border border-gray-200 z-0" />

          {/* Legend */}
          <div className="absolute bottom-6 right-3 z-[1000] bg-white/95 rounded-lg border border-gray-200 p-3 shadow-lg text-xs space-y-1.5">
            <p className="font-semibold text-gray-700 mb-1">Status</p>
            {Object.entries(statusColors).map(([status, color]) => (
              <div key={status} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
                <span className="text-gray-600">{status.replace(/_/g, " ")}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Side Panel */}
        <div className="w-80 bg-white rounded-lg border border-gray-200 flex flex-col max-h-[600px]">
          <div className="p-3 border-b border-gray-200">
            <h2 className="text-sm font-semibold text-gray-900">
              Nearby Signals
              <span className="ml-2 text-xs text-gray-500 font-normal">({totalNearby} found)</span>
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
            {signals.length === 0 ? (
              <div className="p-6 text-center text-gray-500 text-sm">
                No signals found in this area. Try adjusting the radius or filters.
              </div>
            ) : (
              signals.map((s) => (
                <div key={s.id}
                  onClick={() => { setSelectedSignal(s); navigate(`/signals/${s.id}`); }}
                  onMouseEnter={() => {
                    if (!mapRef.current) return;
                    const color = getStatusColor(s.status);
                    const icon = createIcon(color);
                    const marker = L.marker([s.latitude, s.longitude], { icon });
                    marker.bindPopup(`<div style="font-family: system-ui; font-size: 12px;"><strong>${s.title}</strong></div>`);
                    marker.addTo(mapRef.current);
                    marker.openPopup();
                    setTimeout(() => { if (mapRef.current) { mapRef.current.removeLayer(marker); } }, 2000);
                  }}
                  className={`p-3 cursor-pointer hover:bg-blue-50 transition-colors ${selectedSignal?.id === s.id ? "bg-blue-50 border-l-2 border-blue-500" : ""}`}>
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 truncate">{s.title}</p>
                    <span className="text-[10px] text-gray-400 ml-2 whitespace-nowrap">{s.distance_km?.toFixed(2)} km</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{s.reference_number}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-[10px] font-medium px-1.5 py-0.5 rounded text-white" style={{ background: getStatusColor(s.status) }}>
                      {s.status.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
          {searchResult && (
            <div className="p-3 border-t border-gray-200 bg-gray-50">
              <p className="text-xs text-gray-500">Last search:</p>
              <p className="text-xs font-medium text-gray-700 truncate">{searchResult.formatted_address}</p>
            </div>
          )}
        </div>
      </div>

      <Modal open={showTools} onClose={() => setShowTools(false)} title="Map Tools" size="md">
        <div className="space-y-4">
          <div className="flex gap-2 border-b border-gray-200 pb-3">
            {(["places", "distance", "route", "validate"] as const).map((tab) => (
              <button key={tab} onClick={() => { setToolsSubTab(tab); setPlacesResults([]); setDistResult(null); setAddrValidation(null); }}
                className={`px-3 py-1.5 text-sm rounded-md font-medium ${toolsSubTab === tab ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
                {tab === "places" ? "Search Places" : tab === "distance" ? "Distance" : tab === "route" ? "Route" : "Validate"}
              </button>
            ))}
          </div>

          {toolsSubTab === "places" && (
            <div className="space-y-3">
              <div className="flex gap-2">
                <input type="text" value={placesQuery} onChange={(e) => setPlacesQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && placesQuery.trim()) { setPlacesLoading(true); mapApi.searchPlaces({ query: placesQuery, latitude: userLocation?.[0], longitude: userLocation?.[1] }).then((r) => setPlacesResults(r.data.data?.places || [])).catch(() => { toast("Places search failed", "error"); }).finally(() => setPlacesLoading(false)); } }}
                  placeholder="Search for places nearby..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                <button onClick={async () => { if (!placesQuery.trim()) return; setPlacesLoading(true); try { const r = await mapApi.searchPlaces({ query: placesQuery, latitude: userLocation?.[0], longitude: userLocation?.[1] }); setPlacesResults(r.data.data?.places || []); } catch { toast("Places search failed", "error"); } finally { setPlacesLoading(false); } }}
                  disabled={placesLoading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
                  {placesLoading ? "..." : "Search"}
                </button>
              </div>
              {placesResults.length > 0 && (
                <div className="max-h-60 overflow-y-auto divide-y divide-gray-100 border border-gray-200 rounded-lg">
                  {placesResults.map((p, i) => (
                    <div key={i} className="p-3 hover:bg-gray-50 cursor-pointer text-sm"
                      onClick={() => { mapRef.current?.flyTo([p.latitude, p.longitude], 15, { duration: 1.5 }); setShowTools(false); }}>
                      <p className="font-medium text-gray-800">{p.name}</p>
                      <p className="text-xs text-gray-500">{p.formatted_address}</p>
                      {p.rating && <p className="text-xs text-amber-600">Rating: {p.rating}</p>}
                    </div>
                  ))}
                </div>
              )}
              {placesResults.length === 0 && !placesLoading && (
                <p className="text-sm text-gray-400 text-center py-4">Search for places to find nearby points of interest</p>
              )}
            </div>
          )}

          {toolsSubTab === "distance" && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Origin Address</label>
                <input type="text" value={distOrigin} onChange={(e) => setDistOrigin(e.target.value)}
                  placeholder="e.g., Tunis City Center" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Destination Address</label>
                <input type="text" value={distDest} onChange={(e) => setDistDest(e.target.value)}
                  placeholder="e.g., La Marsa" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <button onClick={async () => { if (!distOrigin.trim() || !distDest.trim()) return; setDistLoading(true); setDistResult(null); try { const [geoO, geoD] = await Promise.all([mapApi.geocode(distOrigin), mapApi.geocode(distDest)]); const o = geoO.data.data; const d = geoD.data.data; if (!o?.latitude || !d?.latitude) { toast("Could not geocode addresses", "error"); return; } const r = await mapApi.distance({ origin_lat: o.latitude, origin_lng: o.longitude, dest_lat: d.latitude, dest_lng: d.longitude }); setDistResult(r.data.data); mapRef.current?.flyTo([(o.latitude + d.latitude) / 2, (o.longitude + d.longitude) / 2], 11, { duration: 1.5 }); L.marker([o.latitude, o.longitude]).addTo(mapRef.current!).bindPopup(`<b>Origin:</b> ${o.formatted_address}`).openPopup(); L.marker([d.latitude, d.longitude]).addTo(mapRef.current!).bindPopup(`<b>Destination:</b> ${d.formatted_address}`); } catch { toast("Distance calculation failed", "error"); } finally { setDistLoading(false); } }}
                disabled={distLoading || !distOrigin.trim() || !distDest.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 w-full">
                {distLoading ? "Calculating..." : "Calculate Distance"}
              </button>
              {distResult && (
                <div className="bg-blue-50 rounded-lg p-4 text-sm space-y-1">
                  <p><span className="font-medium">Distance:</span> {distResult.distance_text}</p>
                  <p><span className="font-medium">Duration:</span> {distResult.duration_text}</p>
                  <p><span className="text-gray-500">Mode:</span> {distResult.mode}</p>
                </div>
              )}
            </div>
          )}

          {toolsSubTab === "route" && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">From Address</label>
                <input type="text" value={distOrigin} onChange={(e) => setDistOrigin(e.target.value)}
                  placeholder="Starting point address" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">To Address</label>
                <input type="text" value={distDest} onChange={(e) => setDistDest(e.target.value)}
                  placeholder="Destination address" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <button onClick={async () => { if (!distOrigin.trim() || !distDest.trim()) return; setDistLoading(true); setDistResult(null); try { const [geoO, geoD] = await Promise.all([mapApi.geocode(distOrigin), mapApi.geocode(distDest)]); const o = geoO.data.data; const d = geoD.data.data; if (!o?.latitude || !d?.latitude) { toast("Could not geocode addresses", "error"); return; } const r = await mapApi.route({ origin_lat: o.latitude, origin_lng: o.longitude, dest_lat: d.latitude, dest_lng: d.longitude }); setDistResult(r.data.data); const midLat = (o.latitude + d.latitude) / 2; const midLng = (o.longitude + d.longitude) / 2; mapRef.current?.flyTo([midLat, midLng], 11, { duration: 1.5 }); L.marker([o.latitude, o.longitude]).addTo(mapRef.current!).bindPopup(`<b>From:</b> ${o.formatted_address}`).openPopup(); L.marker([d.latitude, d.longitude]).addTo(mapRef.current!).bindPopup(`<b>To:</b> ${d.formatted_address}`); } catch { toast("Route calculation failed", "error"); } finally { setDistLoading(false); } }}
                disabled={distLoading || !distOrigin.trim() || !distDest.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 w-full">
                {distLoading ? "Calculating Route..." : "Get Route"}
              </button>
              {distResult && (
                <div className="bg-green-50 rounded-lg p-4 text-sm space-y-1">
                  <p><span className="font-medium">Distance:</span> {distResult.distance_text}</p>
                  <p><span className="font-medium">Duration:</span> {distResult.duration_text}</p>
                  <p><span className="text-gray-500">Mode:</span> {distResult.mode}</p>
                </div>
              )}
            </div>
          )}

          {toolsSubTab === "validate" && (
            <div className="space-y-3">
              <div className="flex gap-2">
                <input type="text" value={addrToValidate} onChange={(e) => setAddrToValidate(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && addrToValidate.trim()) { setAddrLoading(true); mapApi.validateAddress(addrToValidate).then((r) => setAddrValidation(r.data.data)).catch(() => { toast("Validation failed", "error"); }).finally(() => setAddrLoading(false)); } }}
                  placeholder="Enter an address to validate..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                <button onClick={async () => { if (!addrToValidate.trim()) return; setAddrLoading(true); try { const r = await mapApi.validateAddress(addrToValidate); setAddrValidation(r.data.data); } catch { toast("Address validation failed", "error"); } finally { setAddrLoading(false); } }}
                  disabled={addrLoading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
                  {addrLoading ? "..." : "Validate"}
                </button>
              </div>
              {addrValidation && (
                <div className={`rounded-lg p-4 text-sm space-y-2 ${addrValidation.is_valid ? "bg-green-50" : "bg-red-50"}`}>
                  <p className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${addrValidation.is_valid ? "bg-green-500" : "bg-red-500"}`} />
                    <span className={`font-medium ${addrValidation.is_valid ? "text-green-800" : "text-red-800"}`}>
                      {addrValidation.is_valid ? "Valid Address" : "Invalid Address"}
                    </span>
                    {addrValidation.confidence && (
                      <span className="text-xs text-gray-500">Confidence: {addrValidation.confidence}</span>
                    )}
                  </p>
                  {addrValidation.geocoded?.formatted_address && (
                    <p><span className="text-gray-500">Geocoded:</span> {addrValidation.geocoded.formatted_address}</p>
                  )}
                  {addrValidation.issues && addrValidation.issues.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs font-medium text-red-700">Issues:</p>
                      <ul className="list-disc list-inside text-xs text-red-600">
                        {addrValidation.issues.map((issue: string, i: number) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}
