import { useState, useEffect } from "react";
import { sectors } from "../../api/endpoints";
import { useAdminSignalStats } from "../../hooks/useAdmin";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import type { Sector, SectorStats } from "../../types";

export default function SectorManagement() {
  const { toast } = useToast();
  const { stats } = useAdminSignalStats();
  const [sectorList, setSectorList] = useState<Sector[]>([]);
  const [loading, setLoading] = useState(true);
  const [editModal, setEditModal] = useState(false);
  const [selected, setSelected] = useState<Sector | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: "", code: "", description: "", sector_type: "administration", max_daily_signals: 50 });
  const [detailModal, setDetailModal] = useState(false);
  const [detailSector, setDetailSector] = useState<Sector | null>(null);
  const [detailStats, setDetailStats] = useState<SectorStats | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchSectors = async () => {
    setLoading(true);
    try {
      const res = await sectors.list();
      setSectorList(res.data.data ?? []);
    } catch { toast("Failed to load sectors", "error"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchSectors(); }, []);

  const openEdit = (sector?: Sector) => {
    if (sector) {
      setSelected(sector);
      setForm({ name: sector.name, code: sector.code, description: sector.description || "", sector_type: sector.sector_type || "administration", max_daily_signals: sector.max_daily_signals || 50 });
    } else {
      setSelected(null);
      setForm({ name: "", code: "", description: "", sector_type: "administration", max_daily_signals: 50 });
    }
    setEditModal(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (selected) await sectors.update(selected.id, form);
      else await sectors.create(form);
      setEditModal(false);
      toast(selected ? "Sector updated" : "Sector created", "success");
      fetchSectors();
    } catch (err: any) { toast(err.response?.data?.message || "Save failed", "error"); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this sector?")) return;
    try {
      await sectors.delete(id);
      toast("Sector deleted", "success");
      fetchSectors();
    }     catch { toast("Delete failed", "error"); }
  };

  const openDetail = async (sector: Sector) => {
    setDetailSector(sector);
    setDetailLoading(true);
    setDetailModal(true);
    try {
      const [sectorRes, statsRes] = await Promise.all([
        sectors.get(sector.id),
        sectors.stats(sector.id),
      ]);
      setDetailSector(sectorRes.data.data ?? null);
      setDetailStats(statsRes.data.data ?? null);
    } catch {
      toast("Failed to load sector details", "error");
    } finally {
      setDetailLoading(false);
    }
  };

  if (loading && sectorList.length === 0) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Sector Management</h1>
        <button onClick={() => openEdit()} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ New Sector</button>
      </div>

      {/* Stats summary */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Total Signals" value={stats.total_signals.toLocaleString()} color="blue" />
          <StatCard label="Resolution Rate" value={stats.avg_resolution_time_hours ? `${(24 / stats.avg_resolution_time_hours * 100).toFixed(1)}%` : "N/A"} color="green" />
          <StatCard label="Categories" value={Object.keys(stats.signals_by_category || {}).length.toString()} color="purple" />
          <StatCard label="Avg Time" value={stats.avg_resolution_time_hours ? `${stats.avg_resolution_time_hours.toFixed(1)}h` : "N/A"} color="yellow" />
        </div>
      )}

      {/* Sector cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sectorList.map((sector) => (
          <div key={sector.id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-semibold text-gray-900">{sector.name}</h3>
              </div>
              <span className="text-xs font-mono text-gray-400">{sector.code}</span>
            </div>
            <p className="text-sm text-gray-500 mb-4">{sector.description || "No description"}</p>
            <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
              <span>Type: {sector.sector_type || "municipal"}</span>
              <span>Max/day: {sector.max_daily_signals || "N/A"}</span>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-gray-100">
              <button onClick={() => openDetail(sector)} className="px-3 py-1.5 text-xs border border-blue-300 text-blue-600 rounded hover:bg-blue-50">View Details</button>
              <button onClick={() => openEdit(sector)} className="px-3 py-1.5 text-xs border border-gray-300 rounded hover:bg-gray-50">Edit</button>
              <button onClick={() => handleDelete(sector.id)} className="px-3 py-1.5 text-xs border border-red-300 text-red-600 rounded hover:bg-red-50">Delete</button>
            </div>
          </div>
        ))}
      </div>

      {sectorList.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">No sectors found. Create your first sector.</div>
      )}

      {/* Category breakdown from stats */}
      {stats?.signals_by_category && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Signals by Category</h2>
          <div className="space-y-3">
            {Object.entries(stats.signals_by_category).map(([category, count]) => {
              const pct = stats.total_signals > 0 ? ((count as number) / stats.total_signals) * 100 : 0;
              return (
                <div key={category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 font-medium">{category}</span>
                    <span className="text-gray-500">{count as number} ({pct.toFixed(1)}%)</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <Modal open={editModal} onClose={() => setEditModal(false)} title={selected ? "Edit Sector" : "New Sector"}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code *</label>
              <input value={form.code} onChange={(e) => setForm((f) => ({ ...f, code: e.target.value.toUpperCase() }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={3} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select value={form.sector_type} onChange={(e) => setForm((f) => ({ ...f, sector_type: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="water">Water & Sanitation</option>
                <option value="roads">Roads & Transport</option>
                <option value="waste">Waste & Cleanliness</option>
                <option value="lighting">Public Lighting</option>
                <option value="green_spaces">Green Spaces</option>
                <option value="buildings">Public Buildings</option>
                <option value="safety">Safety & Police</option>
                <option value="environment">Environment</option>
                <option value="administration">General Administration</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Signals/Day</label>
              <input type="number" value={form.max_daily_signals} onChange={(e) => setForm((f) => ({ ...f, max_daily_signals: Number(e.target.value) }))} min={1} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button onClick={() => setEditModal(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
            <button onClick={handleSave} disabled={saving || !form.name || !form.code} className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
              {saving ? "..." : selected ? "Update" : "Create"}
            </button>
          </div>
        </div>
      </Modal>

      <Modal open={detailModal} onClose={() => setDetailModal(false)} title={`Sector Details${detailSector ? ` — ${detailSector.name}` : ""}`} size="xl">
        {detailLoading ? (
          <LoadingSpinner size="md" className="py-12" />
        ) : detailSector ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <StatCard label="Code" value={detailSector.code} color="blue" />
              <StatCard label="Type" value={detailSector.sector_type} color="purple" />
              <StatCard label="Status" value={detailSector.status} color={detailSector.status === "active" ? "green" : "yellow"} />
              <StatCard label="Max/Day" value={String(detailSector.max_daily_signals)} color="blue" />
            </div>

            {detailSector.manager_name && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Manager</h4>
                <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                  <p><span className="text-gray-500">Name:</span> {detailSector.manager_name}</p>
                  {detailSector.manager_email && <p><span className="text-gray-500">Email:</span> {detailSector.manager_email}</p>}
                  {detailSector.manager_phone && <p><span className="text-gray-500">Phone:</span> {detailSector.manager_phone}</p>}
                </div>
              </div>
            )}

            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Contact</h4>
              <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                {detailSector.email && <p><span className="text-gray-500">Email:</span> {detailSector.email}</p>}
                {detailSector.phone && <p><span className="text-gray-500">Phone:</span> {detailSector.phone}</p>}
                {detailSector.address && <p><span className="text-gray-500">Address:</span> {detailSector.address}{detailSector.city ? `, ${detailSector.city}` : ""}</p>}
              </div>
            </div>

            {detailSector.working_hours && Object.keys(detailSector.working_hours).length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Working Hours</h4>
                <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                  {Object.entries(detailSector.working_hours).map(([day, hours]) => (
                    <p key={day}><span className="text-gray-500">{day}:</span> {hours as string}</p>
                  ))}
                </div>
              </div>
            )}

            {detailSector.emergency_contact && Object.keys(detailSector.emergency_contact).length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Emergency Contact</h4>
                <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                  {Object.entries(detailSector.emergency_contact).map(([key, value]) => (
                    <p key={key}><span className="text-gray-500 capitalize">{key}:</span> {value as string}</p>
                  ))}
                </div>
              </div>
            )}

            {detailStats && (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  <StatCard label="Total Processed" value={(detailStats.total_signals_processed ?? 0).toLocaleString()} color="blue" />
                  <StatCard label="Active" value={(detailStats.active_signals ?? 0).toLocaleString()} color="yellow" />
                  <StatCard label="Resolved" value={(detailStats.resolved_signals ?? 0).toLocaleString()} color="green" />
                  <StatCard label="Avg Resolution" value={detailStats.avg_resolution_time_hours ? `${detailStats.avg_resolution_time_hours.toFixed(1)}h` : "N/A"} color="purple" />
                  <StatCard label="Satisfaction" value={detailStats.satisfaction_rate ? `${detailStats.satisfaction_rate.toFixed(1)}%` : "N/A"} color="green" />
                  <StatCard label="Perf. Score" value={detailStats.performance_score ? detailStats.performance_score.toFixed(1) : "N/A"} color="blue" />
                </div>

                {(detailStats.signals_by_category ?? {}) && Object.keys(detailStats.signals_by_category ?? {}).length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Signals by Category</h4>
                    <div className="space-y-2">
                      {Object.entries(detailStats.signals_by_category).map(([category, count]) => {
                        const total = detailStats.total_signals_processed;
                        const pct = total > 0 ? (count / total) * 100 : 0;
                        return (
                          <div key={category}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-700">{category}</span>
                              <span className="text-gray-500">{count} ({pct.toFixed(1)}%)</span>
                            </div>
                            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {detailStats.monthly_trend && detailStats.monthly_trend.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Monthly Trend</h4>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="flex items-end gap-1 h-20">
                        {(() => {
                          const max = Math.max(...detailStats.monthly_trend.map((m) => m.count), 1);
                          return detailStats.monthly_trend.map((item, i) => {
                            const h = (item.count / max) * 100;
                            return (
                              <div key={i} className="flex-1 flex flex-col items-center">
                                <div className="w-full bg-blue-500 rounded-t" style={{ height: `${h}%`, minHeight: "4px" }} title={`${item.period}: ${item.count}`} />
                                <span className="text-[10px] text-gray-400 mt-1 truncate w-full text-center">{item.period.slice(-5)}</span>
                              </div>
                            );
                          });
                        })()}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}

            {detailSector.users && detailSector.users.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Assigned Users ({detailSector.users.length})</h4>
                <div className="space-y-2">
                  {detailSector.users.map((user) => (
                    <div key={user.id} className="bg-gray-50 rounded-lg p-3 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{user.first_name} {user.last_name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="capitalize text-gray-400">{user.role}</span>
                        <span className={user.status === "active" ? "text-green-600" : "text-red-600"}>{user.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : null}
      </Modal>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    blue: "bg-blue-50 text-blue-600", green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600", yellow: "bg-yellow-50 text-yellow-600",
  };
  return (
    <div className={`rounded-lg border p-4 ${colors[color] || "bg-gray-50"}`}>
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}
