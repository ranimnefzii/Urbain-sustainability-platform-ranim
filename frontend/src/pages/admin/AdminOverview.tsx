import { useState, useEffect } from "react";
import { admin } from "../../api/endpoints";
import { useToast } from "../../contexts/ToastContext";
import LoadingSpinner from "../../components/ui/LoadingSpinner";

export default function AdminOverview() {
  const { toast } = useToast();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    admin.overview()
      .then((r) => setData(r.data.data))
      .catch(() => toast("Failed to load overview data", "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;
  if (!data) return <div className="text-center py-20 text-gray-500">No overview data available</div>;

  const { total_signals = 0, total_users = 0, total_sectors = 0, total_categories = 0 } = data;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Admin Overview</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard title="Total Signals" value={total_signals.toLocaleString()}  />
        <KpiCard title="Total Users" value={total_users.toLocaleString()}  />
        <KpiCard title="Total Sectors" value={total_sectors.toLocaleString()}  />
        <KpiCard title="Total Categories" value={total_categories.toLocaleString()}  />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {data.signals_by_status && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Signals by Status</h2>
            <div className="space-y-3">
              {Object.entries(data.signals_by_status).map(([status, count]) => {
                const total = Object.values(data.signals_by_status).reduce((a: number, b: any) => a + (b as number), 0) || 1;
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

        {data.recent_activity && data.recent_activity.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="divide-y divide-gray-100">
              {data.recent_activity.map((item: any, i: number) => (
                <div key={i} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.action || item.description}</p>
                    <p className="text-xs text-gray-500">{item.user ? `${item.user} \u00b7 ` : ""}{item.timestamp ? new Date(item.timestamp).toLocaleString() : ""}</p>
                  </div>
                  <span className="text-xs text-gray-400">{item.type || item.entity_type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {data.recent_signals && data.recent_signals.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Signals</h2>
          <div className="divide-y divide-gray-100">
            {data.recent_signals.slice(0, 5).map((s: any) => (
              <div key={s.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{s.title}</p>
                  <p className="text-xs text-gray-500">{s.reference_number} &middot; {new Date(s.created_at).toLocaleDateString()}</p>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${getStatusBadgeClass(s.status)}`}>
                  {s.status?.replace(/_/g, " ")}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function KpiCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wider">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
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

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case "SUBMITTED": return "bg-gray-100 text-gray-700";
    case "PENDING": return "bg-yellow-100 text-yellow-700";
    case "UNDER_REVIEW": return "bg-blue-100 text-blue-700";
    case "ASSIGNED": return "bg-indigo-100 text-indigo-700";
    case "IN_PROGRESS": return "bg-blue-100 text-blue-700";
    case "RESOLVED": return "bg-green-100 text-green-700";
    case "CLOSED": return "bg-gray-100 text-gray-700";
    case "CANCELLED": return "bg-red-100 text-red-700";
    default: return "bg-gray-100 text-gray-700";
  }
}
