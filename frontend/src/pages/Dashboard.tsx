import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { admin, signals, notifications } from "../api/endpoints";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../contexts/ToastContext";
import StatusBadge from "../components/ui/StatusBadge";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import type { Signal, AdminDashboard, SignalStats } from "../types";

interface MergedStats {
  total_signals: number; open_signals: number; resolved_signals: number;
  total_users?: number; active_users?: number; avg_resolution_time_hours?: number;
  citizen_satisfaction_rate?: number; signals_by_status?: Record<string, number>;
  signals_by_category?: Record<string, number>; signals_by_priority?: Record<string, number>;
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
            admin.dashboard(), signals.list({ size: 10 }),
            notifications.stats().catch(() => ({ data: { data: null } })),
          ]);
          const d = dRes.data.data as AdminDashboard | null;
          if (d) setStats({
            total_signals: d.total_signals || 0, open_signals: d.open_signals || 0, resolved_signals: d.resolved_signals || 0,
            total_users: d.total_users || 0, active_users: d.active_users || 0, avg_resolution_time_hours: d.avg_resolution_time_hours,
            citizen_satisfaction_rate: d.citizen_satisfaction_rate, signals_by_status: d.signals_by_status,
            signals_by_category: d.signals_by_category, signals_by_priority: d.signals_by_priority,
            sector_performance: d.sector_performance, top_categories: d.top_categories,
          });
          setSignalList(sRes.data.data?.items || []);
          const ns = nRes.data.data;
          if (ns) setUnreadCount(ns.total_sent - Math.round(ns.total_sent * ns.read_rate));
        } else {
          const [sRes, statsRes] = await Promise.all([signals.list({ size: 10 }), signals.stats()]);
          setSignalList(sRes.data.data?.items || []);
          const sd = statsRes.data.data as SignalStats | null;
          if (sd) {
            const openKeys = Object.entries(sd.signals_by_status || {})
              .filter(([k]) => !["RESOLVED", "CLOSED", "CANCELLED", "REJECTED"].includes(k))
              .reduce((sum, [, v]) => sum + (v as number), 0);
            setStats({
              total_signals: sd.total_signals || 0, open_signals: openKeys,
              resolved_signals: (sd.signals_by_status?.RESOLVED || 0) + (sd.signals_by_status?.CLOSED || 0),
              avg_resolution_time_hours: sd.avg_resolution_time_hours, citizen_satisfaction_rate: sd.citizen_satisfaction_rate,
              signals_by_status: sd.signals_by_status, signals_by_category: sd.signals_by_category,
              signals_by_priority: sd.signals_by_priority,
            });
          }
        }
      } catch { setSignalList([]); } finally { setLoading(false); }
    };
    load();
  }, [isAdmin]);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  const statusBarTotal = stats.total_signals || 1;
  const quickActions = [
    { label: "Nouveau signalement", icon: "M12 4v16m8-8H4", color: "brand", to: "/signals/new" },
    { label: "Voir la carte", icon: "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z", color: "green", to: "/map" },
    { label: "Mes signalements", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z", color: "purple", to: "/signals" },
    { label: isAdmin ? "Administration" : "Mon profil", icon: isAdmin ? "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0..." : "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z", color: "amber", to: isAdmin ? "/admin" : "/profile" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="page-title">Bonjour, {user?.first_name} !</h1>
          <p className="text-sm text-surface-500 mt-1">
            {isAdmin ? "Vous avez les droits d'administration." : "Bienvenue sur votre espace citoyen."}
            {unreadCount > 0 && (
              <span className="ml-2 inline-flex items-center gap-1.5 text-brand-600 font-semibold bg-brand-50 px-2.5 py-0.5 rounded-full text-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse" />
                {unreadCount} notification{unreadCount > 1 ? "s" : ""} non lue{unreadCount > 1 ? "s" : ""}
              </span>
            )}
          </p>
        </div>
        <button onClick={() => navigate("/signals/new")} className="btn-primary">
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          Nouveau signalement
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-brand-50 flex items-center justify-center"><svg className="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg></div>
          <div><p className="kpi-label">Total signalements</p><p className="kpi-value">{stats.total_signals.toLocaleString()}</p></div>
        </div></div>
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-amber-50 flex items-center justify-center"><svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <div><p className="kpi-label">En cours</p><p className="kpi-value text-amber-600">{stats.open_signals.toLocaleString()}</p></div>
        </div></div>
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-green-50 flex items-center justify-center"><svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <div><p className="kpi-label">Résolus</p><p className="kpi-value text-green-600">{stats.resolved_signals.toLocaleString()}</p></div>
        </div></div>
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-purple-50 flex items-center justify-center"><svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg></div>
          <div><p className="kpi-label">Temps résolution</p><p className="kpi-value text-purple-600">{stats.avg_resolution_time_hours ? `${stats.avg_resolution_time_hours.toFixed(1)}h` : "N/A"}</p></div>
        </div></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution */}
        {stats.signals_by_status && Object.keys(stats.signals_by_status).length > 0 && (
          <div className="card"><div className="card-body">
            <h2 className="section-title mb-4">Signalements par statut</h2>
            <div className="space-y-3">
              {Object.entries(stats.signals_by_status).map(([status, count]) => {
                const pct = ((count as number) / statusBarTotal) * 100;
                return (
                  <div key={status}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-surface-600 font-medium capitalize">{status.replace(/_/g, " ").toLowerCase()}</span>
                      <span className="text-surface-400">{count as number} ({(pct).toFixed(0)}%)</span>
                    </div>
                    <div className="h-2 bg-surface-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-500 ${getBarColor(status)}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div></div>
        )}

        {/* Priority Distribution */}
        {stats.signals_by_priority && Object.keys(stats.signals_by_priority).length > 0 && (
          <div className="card"><div className="card-body">
            <h2 className="section-title mb-4">Signalements par priorité</h2>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(stats.signals_by_priority).map(([priority, count]) => (
                <div key={priority} className={`rounded-xl border-2 p-3 text-center transition-all hover:shadow-sm ${getPriorityBg(priority)}`}>
                  <p className="text-[10px] font-semibold uppercase tracking-wider opacity-70">{priority}</p>
                  <p className={`text-2xl font-bold mt-0.5 ${getPriorityText(priority)}`}>{count as number}</p>
                </div>
              ))}
            </div>
          </div></div>
        )}

        {/* Quick Actions */}
        <div className="card"><div className="card-body">
          <h2 className="section-title mb-4">Actions rapides</h2>
          <div className="space-y-2">
            {quickActions.map(({ label, icon, color, to }) => {
              const colorMap: Record<string, string> = {
                brand: "bg-brand-50 text-brand-700 hover:bg-brand-100 border-brand-200",
                green: "bg-green-50 text-green-700 hover:bg-green-100 border-green-200",
                purple: "bg-purple-50 text-purple-700 hover:bg-purple-100 border-purple-200",
                amber: "bg-amber-50 text-amber-700 hover:bg-amber-100 border-amber-200",
              };
              return (
                <button key={label} onClick={() => navigate(to)}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm font-semibold border transition-all duration-200 flex items-center gap-3 ${colorMap[color]}`}>
                  <svg className="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={icon} /></svg>
                  {label}
                </button>
              );
            })}
          </div>

          {isAdmin && stats.total_users != null && (
            <div className="mt-5 pt-4 border-t border-surface-100 space-y-2.5 text-sm">
              <div className="flex justify-between items-center"><span className="text-surface-400">Utilisateurs</span><span className="font-semibold text-surface-800">{stats.total_users}</span></div>
              <div className="flex justify-between items-center"><span className="text-surface-400">Actifs</span><span className="font-semibold text-surface-800">{stats.active_users || 0}</span></div>
              <div className="flex justify-between items-center"><span className="text-surface-400">Satisfaction</span><span className="font-semibold text-surface-800">{stats.citizen_satisfaction_rate ? `${stats.citizen_satisfaction_rate}/5` : "N/A"}</span></div>
            </div>
          )}
        </div></div>
      </div>

      {/* Category Distribution */}
      {stats.signals_by_category && Object.keys(stats.signals_by_category).length > 0 && (
        <div className="card"><div className="card-body">
          <h2 className="section-title mb-4">Répartition par catégorie</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {Object.entries(stats.signals_by_category).map(([cat, count]) => {
              const pct = ((count as number) / statusBarTotal) * 100;
              return (
                <div key={cat} className="flex items-center justify-between px-4 py-2.5 bg-surface-50 rounded-xl">
                  <span className="text-sm font-medium text-surface-700 truncate">{cat}</span>
                  <span className="text-xs font-semibold text-surface-500 ml-2 bg-white px-2 py-0.5 rounded-full">{count as number}</span>
                </div>
              );
            })}
          </div>
        </div></div>
      )}

      {/* Recent Signals */}
      <div className="card"><div className="card-body">
        <div className="flex items-center justify-between mb-4">
          <h2 className="section-title">Signalements récents</h2>
          <button onClick={() => navigate("/signals")} className="btn-ghost text-brand-600 text-sm">Voir tout</button>
        </div>
        {signalList.length === 0 ? (
          <div className="py-10 text-center">
            <svg className="w-12 h-12 text-surface-200 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            <p className="text-sm text-surface-400">Aucun signalement pour le moment.</p>
            <button onClick={() => navigate("/signals/new")} className="btn-primary mt-3 text-sm">Signaler un problème</button>
          </div>
        ) : (
          <div className="divide-y divide-surface-100">
            {signalList.slice(0, 5).map((sig) => (
              <div key={sig.id} onClick={() => navigate(`/signals/${sig.id}`)}
                className="py-3.5 flex items-center justify-between cursor-pointer hover:bg-surface-50 -mx-6 px-6 rounded-lg transition-colors">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-surface-800 truncate">{sig.title}</p>
                  <p className="text-xs text-surface-400 mt-0.5">{sig.reference_number} <span className="mx-1">&middot;</span> {new Date(sig.created_at).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" })}</p>
                </div>
                <StatusBadge status={sig.status} />
              </div>
            ))}
          </div>
        )}
      </div></div>
    </div>
  );
}

function getBarColor(status: string): string {
  switch (status) {
    case "SUBMITTED": case "PENDING": return "bg-amber-400";
    case "UNDER_REVIEW": return "bg-blue-400";
    case "ASSIGNED": return "bg-indigo-400";
    case "IN_PROGRESS": return "bg-brand-500";
    case "RESOLVED": case "CLOSED": return "bg-green-500";
    case "CANCELLED": case "REJECTED": return "bg-red-400";
    default: return "bg-surface-300";
  }
}

function getPriorityBg(priority: string): string {
  switch (priority) {
    case "CRITICAL": return "bg-red-50 border-red-200";
    case "HIGH": return "bg-orange-50 border-orange-200";
    case "MEDIUM": return "bg-yellow-50 border-yellow-200";
    case "LOW": return "bg-green-50 border-green-200";
    default: return "bg-surface-50 border-surface-200";
  }
}

function getPriorityText(priority: string): string {
  switch (priority) {
    case "CRITICAL": return "text-red-600";
    case "HIGH": return "text-orange-600";
    case "MEDIUM": return "text-yellow-600";
    case "LOW": return "text-green-600";
    default: return "text-surface-600";
  }
}
