import { useState, useEffect } from "react";
import { admin } from "../../api/endpoints";
import { useToast } from "../../contexts/ToastContext";
import LoadingSpinner from "../../components/ui/LoadingSpinner";

export default function AdminUserStats() {
  const { toast } = useToast();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    admin.userStats()
      .then((r) => setStats(r.data.data))
      .catch(() => toast("Failed to load user statistics", "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;
  if (!stats) return <div className="text-center py-20 text-gray-500">No user stats available</div>;

  const total = stats.total_users ?? 0;
  const active = stats.active_users ?? 0;
  const inactive = stats.inactive_users ?? (total - active);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">User Statistics</h1>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Total Users</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{total.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Active Users</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{active.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Inactive Users</p>
          <p className="text-2xl font-bold text-red-500 mt-1">{inactive.toLocaleString()}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">User Distribution</h2>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Active</span>
              <span className="text-gray-500 font-medium">{active} ({total > 0 ? ((active / total) * 100).toFixed(1) : 0}%)</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 rounded-full" style={{ width: `${total > 0 ? (active / total) * 100 : 0}%` }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Inactive</span>
              <span className="text-gray-500 font-medium">{inactive} ({total > 0 ? ((inactive / total) * 100).toFixed(1) : 0}%)</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-red-400 rounded-full" style={{ width: `${total > 0 ? (inactive / total) * 100 : 0}%` }} />
            </div>
          </div>
        </div>
      </div>

      {stats.roles && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Users by Role</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="pb-3 font-medium">Role</th>
                  <th className="pb-3 font-medium text-right">Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats.roles).map(([role, count]) => (
                  <tr key={role} className="border-b border-gray-100">
                    <td className="py-3 text-gray-800 capitalize">{role.replace(/_/g, " ")}</td>
                    <td className="py-3 text-right font-medium">{(count as number).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
