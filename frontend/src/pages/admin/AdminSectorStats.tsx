import { useState, useEffect } from "react";
import { admin } from "../../api/endpoints";
import { useToast } from "../../contexts/ToastContext";
import LoadingSpinner from "../../components/ui/LoadingSpinner";

export default function AdminSectorStats() {
  const { toast } = useToast();
  const [sectors, setSectors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    admin.sectorStats()
      .then((r) => setSectors(r.data.data?.sectors || []))
      .catch(() => toast("Failed to load sector statistics", "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Sector Performance</h1>

      {sectors.length === 0 ? (
        <div className="text-center py-20 text-gray-500">No sector data available</div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="pb-3 font-medium">Sector Name</th>
                  <th className="pb-3 font-medium text-right">Total Signals</th>
                  <th className="pb-3 font-medium text-right">Resolved</th>
                  <th className="pb-3 font-medium text-right">Pending</th>
                  <th className="pb-3 font-medium text-right">Resolution Rate</th>
                  <th className="pb-3 font-medium text-right">Avg Response Time</th>
                </tr>
              </thead>
              <tbody>
                {sectors.map((s: any) => {
                  const total = s.total_signals ?? s.total ?? 0;
                  const resolved = s.resolved_signals ?? s.resolved ?? 0;
                  const pending = s.pending_signals ?? s.pending ?? 0;
                  const rate = total > 0 ? ((resolved / total) * 100).toFixed(1) : "0";
                  const avgTime = s.avg_response_time ?? s.avg_time ?? s.avg_resolution_time_hours;
                  return (
                    <tr key={s.sector_id ?? s.id} className="border-b border-gray-100">
                      <td className="py-3 text-gray-800 font-medium">{s.sector_name ?? s.name}</td>
                      <td className="py-3 text-right">{total.toLocaleString()}</td>
                      <td className="py-3 text-right text-green-600 font-medium">{resolved.toLocaleString()}</td>
                      <td className="py-3 text-right text-yellow-600">{pending.toLocaleString()}</td>
                      <td className="py-3 text-right">{rate}%</td>
                      <td className="py-3 text-right text-gray-500">{avgTime != null ? `${Number(avgTime).toFixed(1)}h` : "N/A"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sectors.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sectors.map((s: any) => {
            const total = s.total_signals ?? s.total ?? 0;
            const resolved = s.resolved_signals ?? s.resolved ?? 0;
            const rate = total > 0 ? ((resolved / total) * 100).toFixed(1) : "0";
            return (
              <div key={s.sector_id ?? s.id} className="bg-white rounded-lg border border-gray-200 p-5">
                <p className="text-sm font-semibold text-gray-900 mb-2">{s.sector_name ?? s.name}</p>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Resolution Rate</span>
                  <span>{rate}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${rate}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
