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
  if (!dashboard) return <div className="text-center py-20 text-gray-500">No data available</div>;

  const totalSignals = dashboard.total_signals || 0;
  const resolvedCount = dashboard.resolved_signals || 0;
  const pendingCount = dashboard.open_signals || 0;
  const resolutionRate = totalSignals > 0 ? ((resolvedCount / totalSignals) * 100).toFixed(1) : "0";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <div className="flex gap-2">
          <button onClick={() => navigate("/signals")} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">Manage Signals</button>
          <button onClick={() => navigate("/admin/reports")} className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">Reports</button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Signals" value={totalSignals.toLocaleString()} icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" color="blue" />
        <KPICard title="Resolution Rate" value={`${resolutionRate}%`} icon="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" color="green" />
        <KPICard title="Pending" value={pendingCount.toLocaleString()} icon="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" color="yellow" />
        <KPICard title="Avg Resolution Time" value={dashboard.avg_resolution_time_hours ? `${dashboard.avg_resolution_time_hours.toFixed(1)}h` : "N/A"} icon="M13 10V3L4 14h7v7l9-11h-7z" color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        {dashboard.signals_by_status && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Signals by Status</h2>
            <div className="space-y-3">
              {Object.entries(dashboard.signals_by_status).map(([status, count]) => {
                const total = totalSignals || 1;
                const pct = ((count as number) / total) * 100;
                return (
                  <div key={status}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">{status.replace(/_/g, " ")}</span>
                      <span className="text-gray-500 font-medium">{count as number} ({pct.toFixed(1)}%)</span>
                    </div>
                    <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${getStatusBarColor(status)}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Priority Distribution */}
        {dashboard.signals_by_priority && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Signals by Priority</h2>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(dashboard.signals_by_priority).map(([priority, count]) => (
                <PriorityCard key={priority} priority={priority} count={count as number} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Response Times + Predictions */}
      {!statsLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {responseTimes && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Response Times (30 days)</h2>
              <div className="space-y-3">
                {(Object.entries(responseTimes) as [string, any][]).slice(0, 8).map(([key, val]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">{key.replace(/_/g, " ")}</span>
                      <span className="font-medium text-gray-800">{typeof val === "number" ? `${val.toFixed(1)}h` : String(val)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {predictions && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Predictions</h2>
              <div className="space-y-3">
                {(Object.entries(predictions) as [string, any][]).slice(0, 8).map(([key, val]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{key.replace(/_/g, " ")}</span>
                    <span className={`text-sm font-medium px-2 py-0.5 rounded ${
                      typeof val === "number" && val > 0.7 ? "bg-green-100 text-green-800" :
                      typeof val === "number" && val > 0.4 ? "bg-yellow-100 text-yellow-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {typeof val === "number" ? `${(val * 100).toFixed(0)}%` : String(val)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Category Breakdown */}
      {dashboard.signals_by_category && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Category Distribution</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="pb-3 font-medium">Category</th>
                  <th className="pb-3 font-medium text-right">Count</th>
                  <th className="pb-3 font-medium text-right">Percentage</th>
                  <th className="pb-3 font-medium text-right">Bar</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(dashboard.signals_by_category).map(([cat, count]) => {
                  const pct = totalSignals > 0 ? ((count as number) / totalSignals) * 100 : 0;
                  return (
                    <tr key={cat} className="border-b border-gray-100">
                      <td className="py-3 text-gray-800">{cat}</td>
                      <td className="py-3 text-right font-medium">{count as number}</td>
                      <td className="py-3 text-right text-gray-500">{pct.toFixed(1)}%</td>
                      <td className="py-3 w-1/3">
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Signals */}
      {dashboard.recent_signals && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Signals</h2>
            <button onClick={() => navigate("/signals")} className="text-sm text-blue-600 hover:underline">View all</button>
          </div>
          <div className="divide-y divide-gray-100">
            {dashboard.recent_signals.length === 0 ? (
              <p className="py-6 text-center text-gray-500">No signals yet</p>
            ) : (
              dashboard.recent_signals.slice(0, 5).map((s) => (
                <div key={s.id} className="py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 -mx-6 px-6"
                  onClick={() => navigate(`/signals/${s.id}`)}>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{s.title}</p>
                    <p className="text-xs text-gray-500">{s.reference_number} &middot; {new Date(s.created_at).toLocaleDateString()}</p>
                  </div>
                  <StatusBadge status={s.status} />
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Sector Performance */}
      {dashboard.sector_performance && dashboard.sector_performance.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Sector Performance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="pb-3 font-medium">Sector</th>
                  <th className="pb-3 font-medium text-right">Resolved</th>
                  <th className="pb-3 font-medium text-right">Avg Time</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.sector_performance.map((sp) => (
                  <tr key={sp.sector_id} className="border-b border-gray-100">
                    <td className="py-3 text-gray-800">{sp.sector_name}</td>
                    <td className="py-3 text-right font-medium">{sp.resolved}</td>
                    <td className="py-3 text-right text-gray-500">{sp.avg_time.toFixed(1)}h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Overall stats */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Overview</h2>
        <dl className="grid grid-cols-2 sm:grid-cols-4 gap-6">
          <OverviewItem label="Total Signals" value={totalSignals.toLocaleString()} />
          <OverviewItem label="Resolved" value={resolvedCount.toLocaleString()} />
          <OverviewItem label="Resolution Rate" value={`${resolutionRate}%`} />
          <OverviewItem label="Avg Resolution" value={dashboard.avg_resolution_time_hours ? `${dashboard.avg_resolution_time_hours.toFixed(1)}h` : "N/A"} />
          {dashboard.total_users != null && <OverviewItem label="Total Users" value={dashboard.total_users.toLocaleString()} />}
          {dashboard.active_users != null && <OverviewItem label="Active Users" value={dashboard.active_users.toLocaleString()} />}
          {dashboard.citizen_satisfaction_rate != null && <OverviewItem label="Satisfaction" value={`${dashboard.citizen_satisfaction_rate}/5`} />}
          {dashboard.top_categories && <OverviewItem label="Top Categories" value={String(dashboard.top_categories.length)} />}
        </dl>
      </div>
    </div>
  );
}

function KPICard({ title, value, icon, color }: { title: string; value: string; icon: string; color: string }) {
  const colors: Record<string, string> = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    yellow: "bg-yellow-50 text-yellow-600",
    purple: "bg-purple-50 text-purple-600",
  };
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center gap-3">
        <div className={`h-10 w-10 rounded-lg ${colors[color] || colors.blue} flex items-center justify-center`}>
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} /></svg>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}

function PriorityCard({ priority, count }: { priority: string; count: number }) {
  const colors: Record<string, string> = {
    CRITICAL: "bg-red-50 border-red-200 text-red-700",
    HIGH: "bg-orange-50 border-orange-200 text-orange-700",
    MEDIUM: "bg-yellow-50 border-yellow-200 text-yellow-700",
    LOW: "bg-green-50 border-green-200 text-green-700",
  };
  return (
    <div className={`rounded-lg border p-4 ${colors[priority] || "bg-gray-50 border-gray-200"}`}>
      <p className="text-sm font-medium">{priority.replace(/_/g, " ")}</p>
      <p className="text-2xl font-bold mt-1">{count}</p>
    </div>
  );
}

function OverviewItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-gray-500 uppercase tracking-wider">{label}</dt>
      <dd className="text-lg font-semibold text-gray-900 mt-1">{value}</dd>
    </div>
  );
}

function getStatusBarColor(status: string): string {
  switch (status) {
    case "SUBMITTED": return "bg-gray-400";
    case "PENDING": return "bg-yellow-400";
    case "UNDER_REVIEW": return "bg-blue-400";
    case "ASSIGNED": return "bg-indigo-400";
    case "IN_PROGRESS": return "bg-blue-500";
    case "RESOLVED": return "bg-green-500";
    case "CLOSED": return "bg-gray-500";
    case "CANCELLED": return "bg-red-400";
    default: return "bg-gray-300";
  }
}
