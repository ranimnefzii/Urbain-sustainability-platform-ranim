import { useState, useEffect } from "react";
import { admin } from "../../api/endpoints";
import { useToast } from "../../contexts/ToastContext";
import LoadingSpinner from "../../components/ui/LoadingSpinner";

export default function AdminCategoryStats() {
  const { toast } = useToast();
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    admin.categoryStats()
      .then((r) => {
        const data = r.data.data;
        setCategories(Array.isArray(data) ? data : []);
      })
      .catch(() => toast("Failed to load category statistics", "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  if (categories.length === 0) {
    return <div className="text-center py-20 text-gray-500">No category stats available</div>;
  }

  const maxCount = Math.max(...categories.map((c: any) => c.total_signals ?? c.count ?? c.total ?? 0), 1);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Category Statistics</h1>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Category Breakdown</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="pb-3 font-medium">Category</th>
                <th className="pb-3 font-medium text-right">Total Signals</th>
                <th className="pb-3 font-medium text-right">Resolved</th>
                <th className="pb-3 font-medium text-right">Pending</th>
                <th className="pb-3 font-medium text-right">Bar</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat: any) => {
                const total = cat.total_signals ?? cat.count ?? cat.total ?? 0;
                const resolved = cat.resolved_signals ?? cat.resolved ?? 0;
                const pending = cat.pending_signals ?? cat.pending ?? 0;
                const pct = maxCount > 0 ? (total / maxCount) * 100 : 0;
                return (
                  <tr key={cat.category_id ?? cat.id ?? cat.name} className="border-b border-gray-100">
                    <td className="py-3 text-gray-800 font-medium">{cat.category_name ?? cat.name}</td>
                    <td className="py-3 text-right font-medium">{total.toLocaleString()}</td>
                    <td className="py-3 text-right text-green-600">{resolved.toLocaleString()}</td>
                    <td className="py-3 text-right text-yellow-600">{pending.toLocaleString()}</td>
                    <td className="py-3 w-1/3">
                      <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
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

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((cat: any) => {
          const total = cat.total_signals ?? cat.count ?? cat.total ?? 0;
          const resolved = cat.resolved_signals ?? cat.resolved ?? 0;
          const pending = cat.pending_signals ?? cat.pending ?? 0;
          return (
            <div key={cat.category_id ?? cat.id ?? cat.name} className="bg-white rounded-lg border border-gray-200 p-5">
              <p className="text-sm font-semibold text-gray-900 mb-2">{cat.category_name ?? cat.name}</p>
              <div className="space-y-1 text-xs text-gray-500">
                <div className="flex justify-between">
                  <span>Total Signals</span>
                  <span className="font-medium text-gray-800">{(total).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Resolved</span>
                  <span className="font-medium text-green-600">{resolved.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Pending</span>
                  <span className="font-medium text-yellow-600">{pending.toLocaleString()}</span>
                </div>
              </div>
              <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${maxCount > 0 ? (total / maxCount) * 100 : 0}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
