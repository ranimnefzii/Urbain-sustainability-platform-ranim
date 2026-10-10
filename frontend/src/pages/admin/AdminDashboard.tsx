import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAdminDashboard } from "../../hooks/useAdmin";
import { admin } from "../../api/endpoints";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import StatusBadge from "../../components/ui/StatusBadge";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { dashboard, loading } = useAdminDashboard();
  const [responseTimes, setResponseTimes] = useState<any>(null);
  const [predictions, setPredictions] = useState<any>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      admin.responseTimes(30).then((r) => setResponseTimes(r.data.data)).catch(() => {}),
      admin.predictions().then((r) => setPredictions(r.data.data)).catch(() => {}),
    ]).finally(() => setStatsLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;
  if (!dashboard) return <div className="text-center py-20 text-surface-500">Aucune donnée disponible</div>;

  const totalSignals = dashboard.total_signals || 0;
  const resolvedCount = dashboard.resolved_signals || 0;
  const pendingCount = dashboard.open_signals || 0;
  const resolutionRate = totalSignals > 0 ? ((resolvedCount / totalSignals) * 100).toFixed(1) : "0";

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Tableau de bord</h1>
          <p className="text-sm text-surface-500 mt-1">Vue d'ensemble du système de signalements</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => navigate("/signals/new")} className="btn-primary">
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Nouveau signalement
          </button>
          <button onClick={() => navigate("/admin/reports")} className="btn-secondary">Rapports</button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-brand-50 flex items-center justify-center"><svg className="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg></div>
          <div><p className="text-xs text-surface-400 uppercase tracking-wider font-medium">Total signalements</p><p className="kpi-value">{totalSignals.toLocaleString()}</p></div>
        </div></div>
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-green-50 flex items-center justify-center"><svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <div><p className="text-xs text-surface-400 uppercase tracking-wider font-medium">Taux résolution</p><p className="kpi-value text-green-600">{resolutionRate}%</p></div>
        </div></div>
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-amber-50 flex items-center justify-center"><svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <div><p className="text-xs text-surface-400 uppercase tracking-wider font-medium">En attente</p><p className="kpi-value text-amber-600">{pendingCount.toLocaleString()}</p></div>
        </div></div>
        <div className="kpi-card"><div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-purple-50 flex items-center justify-center"><svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg></div>
          <div><p className="text-xs text-surface-400 uppercase tracking-wider font-medium">Temps moyen</p><p className="kpi-value text-purple-600">{dashboard.avg_resolution_time_hours ? `${dashboard.avg_resolution_time_hours.toFixed(1)} h` : "N/A"}</p></div>
        </div></div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        {dashboard.signals_by_status && (
          <div className="card">
            <div className="card-body">
              <h2 className="section-title mb-5">Signalements par statut</h2>
              <div className="space-y-4">
                {Object.entries(dashboard.signals_by_status).map(([status, count]) => {
                  const total = totalSignals || 1;
                  const pct = ((count as number) / total) * 100;
                  return (
                    <div key={status}>
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="text-surface-600 font-medium">{status.replace(/_/g, " ")}</span>
                        <span className="text-surface-400">{count as number} ({(pct).toFixed(1)}%)</span>
                      </div>
                      <div className="h-3 bg-surface-100 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all duration-500 ${getStatusBarColor(status)}`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Priority Distribution */}
        {dashboard.signals_by_priority && (
          <div className="card">
            <div className="card-body">
              <h2 className="section-title mb-5">Signalements par priorité</h2>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(dashboard.signals_by_priority).map(([priority, count]) => (
                  <div key={priority} className={`rounded-xl border-2 p-4 transition-all hover:shadow-md ${priority === "CRITICAL" ? "bg-red-50 border-red-200" : priority === "HIGH" ? "bg-orange-50 border-orange-200" : priority === "MEDIUM" ? "bg-yellow-50 border-yellow-200" : "bg-green-50 border-green-200"}`}>
                    <p className="text-xs font-semibold uppercase tracking-wider text-surface-500">{priority}</p>
                    <p className={`text-3xl font-bold mt-1 ${priority === "CRITICAL" ? "text-red-600" : priority === "HIGH" ? "text-orange-600" : priority === "MEDIUM" ? "text-yellow-600" : "text-green-600"}`}>{count as number}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Response Times + Predictions */}
      {!statsLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {responseTimes && (
            <div className="card">
              <div className="card-body">
                <h2 className="section-title mb-5">Temps de réponse (30 jours)</h2>
                <div className="space-y-3">
                  {(Object.entries(responseTimes) as [string, any][]).slice(0, 8).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between py-1.5 border-b border-surface-100 last:border-0">
                      <span className="text-sm text-surface-600">{key.replace(/_/g, " ")}</span>
                      <span className="badge bg-brand-50 text-brand-700 font-medium">{typeof val === "number" ? `${val.toFixed(1)}h` : String(val)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          {predictions && (
            <div className="card">
              <div className="card-body">
                <div className="flex items-center gap-2 mb-5">
                  <h2 className="section-title">Prédictions IA</h2>
                  <span className="badge bg-purple-100 text-purple-700 text-[10px]">IA</span>
                </div>
                <div className="space-y-3">
                  {(Object.entries(predictions) as [string, any][]).slice(0, 8).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between py-1.5">
                      <span className="text-sm text-surface-600">{key.replace(/_/g, " ")}</span>
                      <span className={`badge ${typeof val === "number" && val > 0.7 ? "bg-green-100 text-green-800" : typeof val === "number" && val > 0.4 ? "bg-yellow-100 text-yellow-800" : "bg-surface-100 text-surface-800"}`}>
                        {typeof val === "number" ? `${(val * 100).toFixed(0)}%` : String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Category Breakdown */}
      {dashboard.signals_by_category && (
        <div className="card">
          <div className="card-body">
            <h2 className="section-title mb-5">Répartition par catégorie</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-surface-400 text-xs uppercase tracking-wider border-b border-surface-200">
                    <th className="pb-3 font-semibold">Catégorie</th>
                    <th className="pb-3 font-semibold text-right">Nombre</th>
                    <th className="pb-3 font-semibold text-right">Pourcentage</th>
                    <th className="pb-3 font-semibold w-1/3">Barre</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(dashboard.signals_by_category).map(([cat, count]) => {
                    const pct = totalSignals > 0 ? ((count as number) / totalSignals) * 100 : 0;
                    const colors = ["bg-brand-500", "bg-green-500", "bg-purple-500", "bg-amber-500", "bg-red-500", "bg-teal-500", "bg-pink-500", "bg-indigo-500"];
                    const colorIdx = Object.keys(dashboard.signals_by_category!).indexOf(cat) % colors.length;
                    return (
                      <tr key={cat} className="border-b border-surface-100 hover:bg-surface-50 transition-colors">
                        <td className="py-3.5 text-surface-700 font-medium">{cat}</td>
                        <td className="py-3.5 text-right font-semibold text-surface-800">{count as number}</td>
                        <td className="py-3.5 text-right text-surface-400">{pct.toFixed(1)}%</td>
                        <td className="py-3.5 pr-4">
                          <div className="h-2.5 bg-surface-100 rounded-full overflow-hidden">
                            <div className={`h-full rounded-full ${colors[colorIdx]} transition-all duration-500`} style={{ width: `${pct}%` }} />
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Recent Signals */}
      {dashboard.recent_signals && (
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between mb-5">
              <h2 className="section-title">Signalements récents</h2>
              <button onClick={() => navigate("/signals")} className="btn-ghost text-brand-600 text-sm">Voir tout</button>
            </div>
            {dashboard.recent_signals.length === 0 ? (
              <p className="py-8 text-center text-surface-400">Aucun signalement récent</p>
            ) : (
              <div className="divide-y divide-surface-100">
                {dashboard.recent_signals.slice(0, 6).map((s) => (
                  <div key={s.id} className="py-3.5 flex items-center justify-between cursor-pointer hover:bg-surface-50 -mx-6 px-6 rounded-lg transition-colors"
                    onClick={() => navigate(`/signals/${s.id}`)}>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-surface-800 truncate">{s.title}</p>
                      <p className="text-xs text-surface-400 mt-0.5">{s.reference_number} <span className="mx-1">&middot;</span> {new Date(s.created_at).toLocaleDateString("fr-FR")}</p>
                    </div>
                    <StatusBadge status={s.status} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sector Performance */}
      {dashboard.sector_performance && dashboard.sector_performance.length > 0 && (
        <div className="card">
          <div className="card-body">
            <h2 className="section-title mb-5">Performance des secteurs</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-surface-400 text-xs uppercase tracking-wider border-b border-surface-200">
                    <th className="pb-3 font-semibold">Secteur</th>
                    <th className="pb-3 font-semibold text-right">Résolus</th>
                    <th className="pb-3 font-semibold text-right">Temps moyen</th>
                    <th className="pb-3 font-semibold">Performance</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.sector_performance.map((sp) => {
                    const maxTime = Math.max(...dashboard.sector_performance!.map((x) => x.avg_time), 1);
                    const pct = 100 - (sp.avg_time / maxTime) * 100;
                    return (
                      <tr key={sp.sector_id} className="border-b border-surface-100">
                        <td className="py-3.5 text-surface-700 font-medium">{sp.sector_name}</td>
                        <td className="py-3.5 text-right font-semibold text-surface-800">{sp.resolved}</td>
                        <td className="py-3.5 text-right text-surface-400">{sp.avg_time.toFixed(1)}h</td>
                        <td className="py-3.5 pr-4">
                          <div className="h-2.5 bg-surface-100 rounded-full overflow-hidden">
                            <div className={`h-full rounded-full transition-all duration-500 ${pct > 70 ? "bg-green-500" : pct > 40 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${pct}%` }} />
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* System Overview Stats */}
      <div className="card">
        <div className="card-body">
          <h2 className="section-title mb-5">Aperçu du système</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-6">
            <OverviewItem label="Total signalements" value={totalSignals.toLocaleString()} />
            <OverviewItem label="Résolus" value={resolvedCount.toLocaleString()} />
            <OverviewItem label="Taux résolution" value={`${resolutionRate}%`} />
            <OverviewItem label="Temps moyen" value={dashboard.avg_resolution_time_hours ? `${dashboard.avg_resolution_time_hours.toFixed(1)}h` : "N/A"} />
            {dashboard.total_users != null && <OverviewItem label="Utilisateurs" value={dashboard.total_users.toLocaleString()} />}
            {dashboard.active_users != null && <OverviewItem label="Actifs" value={dashboard.active_users.toLocaleString()} />}
            {dashboard.citizen_satisfaction_rate != null && <OverviewItem label="Satisfaction" value={`${dashboard.citizen_satisfaction_rate}/5`} />}
            {dashboard.top_categories && <OverviewItem label="Catégories" value={String(dashboard.top_categories.length)} />}
          </div>
        </div>
      </div>
    </div>
  );
}

function OverviewItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center p-3 bg-surface-50 rounded-xl">
      <dt className="text-[10px] text-surface-400 uppercase tracking-wider font-semibold">{label}</dt>
      <dd className="text-lg font-bold text-surface-800 mt-1">{value}</dd>
    </div>
  );
}

function getStatusBarColor(status: string): string {
  switch (status) {
    case "SUBMITTED": return "bg-surface-400";
    case "PENDING": return "bg-yellow-400";
    case "UNDER_REVIEW": return "bg-blue-400";
    case "ASSIGNED": return "bg-indigo-400";
    case "IN_PROGRESS": return "bg-brand-500";
    case "RESOLVED": return "bg-green-500";
    case "CLOSED": return "bg-surface-500";
    case "CANCELLED": return "bg-red-400";
    default: return "bg-surface-300";
  }
}
