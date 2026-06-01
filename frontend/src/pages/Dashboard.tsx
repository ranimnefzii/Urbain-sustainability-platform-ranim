import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { admin, signals, notifications } from "../api/endpoints";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../contexts/ToastContext";
import StatusBadge from "../components/ui/StatusBadge";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import type { Signal, AdminDashboard, SignalStats } from "../types";

interface MergedStats {
  total_signals: number;
  open_signals: number;
  resolved_signals: number;
  total_users?: number;
  active_users?: number;
  avg_resolution_time_hours?: number;
  citizen_satisfaction_rate?: number;
  signals_by_status?: Record<string, number>;
  signals_by_category?: Record<string, number>;
  signals_by_priority?: Record<string, number>;
  sector_performance?: { sector_id: number; sector_name: string; resolved: number; avg_time: number }[];
  top_categories?: { id: number; name: string; count: number }[];
}

export default function Dashboard() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [stats, setStats] = useState<MergedStats>({ total_signals: 0, open_signals: 0, resolved_signals: 0 });
  const [signalList, setSignalList] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  const isAdmin = user?.role === "admin" || user?.role === "ADMIN";

  useEffect(() => {
    const load = async () => {
      try {
        if (isAdmin) {
          const [dRes, sRes, nRes] = await Promise.all([
            admin.dashboard(),
            signals.list({ size: 10 }),
            notifications.stats().catch(() => ({ data: { data: null } })),
          ]);
          const d = dRes.data.data as AdminDashboard | null;
          if (d) {
            setStats({
              total_signals: d.total_signals || 0,
              open_signals: d.open_signals || 0,
              resolved_signals: d.resolved_signals || 0,
              total_users: d.total_users || 0,
              active_users: d.active_users || 0,
              avg_resolution_time_hours: d.avg_resolution_time_hours,
              citizen_satisfaction_rate: d.citizen_satisfaction_rate,
              signals_by_status: d.signals_by_status,
              signals_by_category: d.signals_by_category,
              signals_by_priority: d.signals_by_priority,
              sector_performance: d.sector_performance,
              top_categories: d.top_categories,
            });
          }
          setSignalList(sRes.data.data?.items || []);
          const ns = nRes.data.data;
          if (ns) setUnreadCount(ns.total_sent - Math.round(ns.total_sent * ns.read_rate));
        } else {
          const [sRes, statsRes] = await Promise.all([
            signals.list({ size: 10 }),
            signals.stats(),
          ]);
          setSignalList(sRes.data.data?.items || []);
          const sd = statsRes.data.data as SignalStats | null;
          if (sd) {
            const openKeys = Object.entries(sd.signals_by_status || {})
              .filter(([k]) => !["RESOLVED", "CLOSED", "CANCELLED", "REJECTED"].includes(k))
              .reduce((sum, [, v]) => sum + (v as number), 0);
            setStats({
              total_signals: sd.total_signals || 0,
              open_signals: openKeys,
              resolved_signals: (sd.signals_by_status?.RESOLVED || 0) + (sd.signals_by_status?.CLOSED || 0),
              avg_resolution_time_hours: sd.avg_resolution_time_hours,
              citizen_satisfaction_rate: sd.citizen_satisfaction_rate,
              signals_by_status: sd.signals_by_status,
              signals_by_category: sd.signals_by_category,
              signals_by_priority: sd.signals_by_priority,
            });
          }
        }
      } catch (err: any) {
        setSignalList([]);
        toast(err?.response?.data?.message || "Failed to load dashboard", "error");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [isAdmin, toast]);

  const statusBarTotal = stats.total_signals || 1;

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">
            Welcome back, {user?.first_name}! {isAdmin ? "You have admin access." : ""}
            {unreadCount > 0 && (
              <span className="ml-2 text-blue-600 font-medium">{unreadCount} unread notification{unreadCount > 1 ? "s" : ""}</span>
            )}
          </p>
        </div>
        <button onClick={() => navigate("/signals/new")} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
          + New Signal
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Total Signals</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_signals.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Open</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">{stats.open_signals.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Resolved</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{stats.resolved_signals.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Avg Resolution</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {stats.avg_resolution_time_hours ? `${stats.avg_resolution_time_hours.toFixed(1)}h` : "N/A"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution */}
        {stats.signals_by_status && Object.keys(stats.signals_by_status).length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Signals by Status</h2>
            <div className="space-y-2">
              {Object.entries(stats.signals_by_status).map(([status, count]) => {
                const pct = ((count as number) / statusBarTotal) * 100;
                return (
                  <div key={status}>
                    <div className="flex justify-between text-xs mb-0.5">
                      <span className="text-gray-600">{status.replace(/_/g, " ")}</span>
                      <span className="text-gray-500">{count as number} ({(pct).toFixed(0)}%)</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${getBarColor(status)}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Priority Distribution */}
        {stats.signals_by_priority && Object.keys(stats.signals_by_priority).length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Signals by Priority</h2>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(stats.signals_by_priority).map(([priority, count]) => (
                <div key={priority} className={`rounded-lg p-3 text-center ${getPriorityBg(priority)}`}>
                  <p className="text-[10px] font-medium opacity-80">{priority.replace(/_/g, " ")}</p>
                  <p className="text-lg font-bold">{count as number}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Quick Actions</h2>
          <div className="space-y-2">
            <button onClick={() => navigate("/signals/new")} className="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 text-sm text-blue-700 font-medium flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
              Report a Signal
            </button>
            <button onClick={() => navigate("/signals/map")} className="w-full text-left px-3 py-2 rounded-lg hover:bg-green-50 text-sm text-green-700 font-medium flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /></svg>
              View Map
            </button>
            <button onClick={() => navigate(isAdmin ? "/admin" : "/profile")} className="w-full text-left px-3 py-2 rounded-lg hover:bg-purple-50 text-sm text-purple-700 font-medium flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /></svg>
              {isAdmin ? "Admin Panel" : "My Profile"}
            </button>
          </div>

          {isAdmin && stats.total_users != null && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Total Users</span>
                <span className="font-medium">{stats.total_users}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Active Users</span>
                <span className="font-medium">{stats.active_users || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Satisfaction</span>
                <span className="font-medium">{stats.citizen_satisfaction_rate ? `${stats.citizen_satisfaction_rate}/5` : "N/A"}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sector Performance (admin) */}
      {isAdmin && stats.sector_performance && stats.sector_performance.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Sector Performance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="pb-2 font-medium">Sector</th>
                  <th className="pb-2 font-medium text-right">Resolved</th>
                  <th className="pb-2 font-medium text-right">Avg Time</th>
                </tr>
              </thead>
              <tbody>
                {stats.sector_performance.map((sp) => (
                  <tr key={sp.sector_id} className="border-b border-gray-100">
                    <td className="py-2 text-gray-800">{sp.sector_name}</td>
                    <td className="py-2 text-right font-medium">{sp.resolved}</td>
                    <td className="py-2 text-right text-gray-500">{sp.avg_time.toFixed(1)}h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top Categories */}
      {stats.top_categories && stats.top_categories.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Top Categories</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {stats.top_categories.map((tc) => (
              <div key={tc.id} className="text-center p-3 rounded-lg bg-gray-50">
                <p className="text-lg font-bold text-gray-800">{tc.count}</p>
                <p className="text-xs text-gray-500 truncate">{tc.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Category Breakdown */}
      {stats.signals_by_category && Object.keys(stats.signals_by_category).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Categories</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {Object.entries(stats.signals_by_category).map(([cat, count]) => {
              const pct = ((count as number) / statusBarTotal) * 100;
              return (
                <div key={cat} className="flex justify-between items-center text-sm px-3 py-1.5 rounded bg-gray-50">
                  <span className="text-gray-700 truncate">{cat}</span>
                  <span className="font-medium text-gray-500 ml-2">{count as number} ({(pct).toFixed(0)}%)</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Signals */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-900">Recent Signals</h2>
          <button onClick={() => navigate("/signals")} className="text-xs text-blue-600 hover:underline">View all</button>
        </div>
        <div className="divide-y divide-gray-100">
          {signalList.length === 0 ? (
            <p className="px-5 py-8 text-center text-gray-500 text-sm">No signals yet. Be the first to report one!</p>
          ) : (
            signalList.slice(0, 5).map((sig) => (
              <div key={sig.id} onClick={() => navigate(`/signals/${sig.id}`)}
                className="px-5 py-3 flex items-center justify-between hover:bg-gray-50 cursor-pointer">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">{sig.title}</p>
                  <p className="text-xs text-gray-500">{sig.reference_number} &middot; {new Date(sig.created_at).toLocaleString()}</p>
                </div>
                <StatusBadge status={sig.status} />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function getBarColor(status: string): string {
  switch (status) {
    case "SUBMITTED": case "PENDING": return "bg-yellow-400";
    case "UNDER_REVIEW": return "bg-blue-400";
    case "ASSIGNED": return "bg-indigo-400";
    case "IN_PROGRESS": return "bg-blue-500";
    case "RESOLVED": case "CLOSED": return "bg-green-500";
    case "CANCELLED": case "REJECTED": return "bg-red-400";
    default: return "bg-gray-300";
  }
}

function getPriorityBg(priority: string): string {
  switch (priority) {
    case "CRITICAL": return "bg-red-50 text-red-700";
    case "HIGH": return "bg-orange-50 text-orange-700";
    case "MEDIUM": return "bg-yellow-50 text-yellow-700";
    case "LOW": return "bg-green-50 text-green-700";
    default: return "bg-gray-50 text-gray-700";
  }
}
