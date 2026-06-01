import { useState, useEffect } from "react";
import { categories } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import type { Category, CategoryStats, CategoryTree } from "../../types";

export default function CategoryManagement() {
  const { toast } = useToast();
  const [catList, setCatList] = useState<Category[]>([]);
  const [tree, setTree] = useState<CategoryTree[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<"list" | "tree">("list");
  const [editModal, setEditModal] = useState(false);
  const [selected, setSelected] = useState<Category | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: "", code: "", description: "", category_type: "infrastructure", color: "#3B82F6", icon: "", sort_order: 0 });

  const [detailModal, setDetailModal] = useState(false);
  const [detailCategory, setDetailCategory] = useState<Category | null>(null);
  const [detailStats, setDetailStats] = useState<CategoryStats | null>(null);
  const [detailSubcategories, setDetailSubcategories] = useState<Category[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [typeFilter, setTypeFilter] = useState("");
  const [byTypeData, setByTypeData] = useState<Category[]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [listRes, treeRes] = await Promise.all([categories.list(), categories.tree()]);
      setCatList(listRes.data.data ?? []);
      setTree(treeRes.data.data ?? []);
    } catch { toast("Failed to load categories", "error"); } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const openEdit = (cat?: Category) => {
    if (cat) {
      setSelected(cat);
      setForm({ name: cat.name, code: cat.code, description: cat.description || "", category_type: cat.category_type, color: cat.color || "#3B82F6", icon: cat.icon || "", sort_order: cat.sort_order });
    } else {
      setSelected(null);
      setForm({ name: "", code: "", description: "", category_type: "infrastructure", color: "#3B82F6", icon: "", sort_order: catList.length + 1 });
    }
    setEditModal(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (selected) await categories.update(selected.id, form);
      else await categories.create(form);
      setEditModal(false);
      fetchData();
    } catch (err: any) { toast(err.response?.data?.message || "Save failed", "error"); } finally { setSaving(false); }
  };

  const openDetail = async (category: Category) => {
    setDetailCategory(category);
    setDetailLoading(true);
    setDetailModal(true);
    try {
      const [res, statsRes, subRes] = await Promise.all([
        categories.get(category.id),
        categories.stats(category.id),
        categories.subcategories(category.id),
      ]);
      setDetailCategory(res.data.data ?? category);
      setDetailStats(statsRes.data.data ?? null);
      setDetailSubcategories(subRes.data.data ?? []);
    } catch {
      toast("Failed to load category details", "error");
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    if (!typeFilter) {
      setByTypeData([]);
      return;
    }
    (async () => {
      try {
        const res = await categories.byType(typeFilter);
        setByTypeData(res.data.data ?? []);
      } catch {
        toast("Failed to filter categories by type", "error");
      }
    })();
  }, [typeFilter]);

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this category?")) return;
    try {
      await categories.delete(id);
      fetchData();
    } catch { toast("Delete failed", "error"); }
  };

  const columns: Column<Category>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "name", header: "Name", render: (c) => <span className="font-medium">{c.name}</span> },
    { key: "code", header: "Code", render: (c) => <span className="font-mono text-xs">{c.code}</span> },
    { key: "category_type", header: "Type" },
    { key: "status", header: "Status", render: (c) => <span className={`text-xs font-medium ${c.status === "active" ? "text-green-600" : "text-gray-500"}`}>{c.status}</span> },
    { key: "total_signals", header: "Signals", className: "text-center" },
    { key: "avg_resolution_time_hours", header: "Avg Time (h)", className: "text-center", render: (c) => c.avg_resolution_time_hours?.toFixed(1) || "-" },
  ];

  const renderTree = (nodes: CategoryTree[], depth = 0) => (
    <div className="space-y-1">
      {nodes.map((node) => (
        <div key={node.id}>
          <div className="flex items-center gap-2 py-1.5 px-2 hover:bg-gray-50 rounded" style={{ paddingLeft: `${depth * 20 + 8}px` }}>
            {node.children?.length > 0 ? (
              <span className="text-gray-400">{depth === 0 ? "▼" : "▸"}</span>
            ) : <span className="text-gray-300 ml-4">-</span>}
            <span className="text-sm" style={{ color: node.color || undefined }}>{node.icon && `${node.icon} `}{node.name}</span>
            <span className="text-xs text-gray-400 font-mono">{node.code}</span>
          </div>
          {node.children && renderTree(node.children, depth + 1)}
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Categories</h1>
        <div className="flex gap-3">
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button onClick={() => setView("list")} className={`px-3 py-1.5 text-sm ${view === "list" ? "bg-blue-600 text-white" : "hover:bg-gray-50"}`}>List</button>
            <button onClick={() => setView("tree")} className={`px-3 py-1.5 text-sm ${view === "tree" ? "bg-blue-600 text-white" : "hover:bg-gray-50"}`}>Tree</button>
          </div>
          <button onClick={() => openEdit()} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ New Category</button>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {loading ? <p className="text-center py-8 text-gray-500">Loading...</p> : (
          view === "list" ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <label className="text-sm font-medium text-gray-700">Type:</label>
                <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm">
                  <option value="">All</option>
                  <option value="infrastructure">Infrastructure</option>
                  <option value="environment">Environment</option>
                  <option value="safety">Safety</option>
                  <option value="service">Service</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <DataTable columns={columns} data={typeFilter ? byTypeData : catList} emptyTitle="No categories" keyExtractor={(c) => c.id} onRowClick={(c) => openDetail(c)} />
            </>
          ) : renderTree(tree)
        )}
      </div>

      <Modal open={detailModal} onClose={() => setDetailModal(false)} title={detailCategory?.name || "Category Details"}>
        {detailLoading ? (
          <p className="text-center py-8 text-gray-500">Loading...</p>
        ) : detailCategory ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Name</label>
                <p className="text-sm font-medium">{detailCategory.name}</p>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Code</label>
                <p className="text-sm font-mono">{detailCategory.code}</p>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Type</label>
                <p className="text-sm capitalize">{detailCategory.category_type}</p>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Status</label>
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${detailCategory.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>{detailCategory.status}</span>
              </div>
              {detailCategory.color && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Color</label>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded border" style={{ backgroundColor: detailCategory.color }} />
                    <span className="text-xs text-gray-500">{detailCategory.color}</span>
                  </div>
                </div>
              )}
            </div>
            {detailCategory.description && (
              <div>
                <label className="block text-xs text-gray-500 mb-1">Description</label>
                <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">{detailCategory.description}</p>
              </div>
            )}

            {detailStats && (
              <>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800 mb-3">Statistics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-gray-900">{detailStats.total_signals}</p>
                      <p className="text-xs text-gray-500 mt-1">Total Signals</p>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-blue-600">{detailStats.active_signals}</p>
                      <p className="text-xs text-gray-500 mt-1">Active</p>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-green-600">{detailStats.resolved_signals}</p>
                      <p className="text-xs text-gray-500 mt-1">Resolved</p>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-gray-900">{detailStats.avg_resolution_time_hours?.toFixed(1) || "-"}</p>
                      <p className="text-xs text-gray-500 mt-1">Avg Time (h)</p>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center inline-block">
                      <p className="text-lg font-bold text-yellow-600">{(detailStats.citizen_satisfaction_rate * 100).toFixed(0) || "-"}%</p>
                      <p className="text-xs text-gray-500 mt-1">Citizen Satisfaction</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-gray-800 mb-2">Signals by Priority</h5>
                    <div className="space-y-2">
                      {Object.entries(detailStats.signals_by_priority || {}).map(([key, count]) => {
                        const total = Object.values(detailStats.signals_by_priority || {}).reduce((a: number, b: number) => a + b, 0);
                        const pct = total > 0 ? (count as number / total) * 100 : 0;
                        return (
                          <div key={key}>
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span className="capitalize">{key}</span>
                              <span>{count as number}</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2">
                              <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-gray-800 mb-2">Signals by Status</h5>
                    <div className="space-y-2">
                      {Object.entries(detailStats.signals_by_status || {}).map(([key, count]) => {
                        const total = Object.values(detailStats.signals_by_status || {}).reduce((a: number, b: number) => a + b, 0);
                        const pct = total > 0 ? (count as number / total) * 100 : 0;
                        return (
                          <div key={key}>
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span className="capitalize">{key}</span>
                              <span>{count as number}</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {detailStats.monthly_trend && detailStats.monthly_trend.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-gray-800 mb-2">Monthly Trend</h5>
                    <div className="space-y-1.5">
                      {detailStats.monthly_trend.map((t) => (
                        <div key={t.month} className="flex items-center gap-3 text-xs">
                          <span className="w-20 text-gray-600">{t.month}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-2">
                            <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${Math.min((t.count / Math.max(...detailStats.monthly_trend.map((x) => x.count))) * 100, 100)}%` }} />
                          </div>
                          <span className="w-10 text-right text-gray-700 font-medium">{t.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {detailSubcategories.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Subcategories ({detailSubcategories.length})</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {detailSubcategories.map((sub) => (
                    <div key={sub.id} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2 text-sm">
                      {sub.color && <div className="w-3 h-3 rounded-full" style={{ backgroundColor: sub.color }} />}
                      <span className="font-medium">{sub.name}</span>
                      <span className="text-xs text-gray-400 font-mono">{sub.code}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2 border-t border-gray-100">
              <button onClick={() => { setDetailModal(false); openEdit(detailCategory); }} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Edit</button>
              <button onClick={() => { setDetailModal(false); handleDelete(detailCategory.id); }} className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">Delete</button>
              <button onClick={() => setDetailModal(false)} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">Close</button>
            </div>
          </div>
        ) : null}
      </Modal>

      <Modal open={editModal} onClose={() => setEditModal(false)} title={selected ? "Edit Category" : "New Category"}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input type="text" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code *</label>
              <input type="text" value={form.code} onChange={(e) => setForm((f) => ({ ...f, code: e.target.value.toUpperCase() }))} required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select value={form.category_type} onChange={(e) => setForm((f) => ({ ...f, category_type: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="infrastructure">Infrastructure</option>
                <option value="environment">Environment</option>
                <option value="safety">Safety</option>
                <option value="service">Service</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
              <input type="color" value={form.color} onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
                className="w-full h-9 border border-gray-300 rounded-lg cursor-pointer" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Icon</label>
              <input type="text" value={form.icon} onChange={(e) => setForm((f) => ({ ...f, icon: e.target.value }))} placeholder="e.g., road, trash"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sort Order</label>
              <input type="number" value={form.sort_order} onChange={(e) => setForm((f) => ({ ...f, sort_order: Number(e.target.value) }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button onClick={() => setEditModal(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
            {selected && <button onClick={() => handleDelete(selected.id)} className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">Delete</button>}
            <button onClick={handleSave} disabled={saving || !form.name || !form.code}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
              {saving ? "..." : selected ? "Update" : "Create"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
