import { useState, useEffect, type FormEvent } from "react";
import { priorities } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import type { Priority, PriorityStats } from "../../types";

const INITIAL_FORM = {
  name: "",
  code: "",
  description: "",
  priority_level: 1,
  severity_level: 1,
  color: "#3B82F6",
  sla_hours: 24,
  escalation_minutes: 60,
  auto_escalate: false,
  requires_approval: false,
  is_active: true,
};

export default function PriorityManagement() {
  const { toast } = useToast();
  const [items, setItems] = useState<Priority[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Priority | null>(null);
  const [saving, setSaving] = useState(false);
  const [stats, setStats] = useState<Record<number, PriorityStats>>({});
  const [form, setForm] = useState(INITIAL_FORM);
  const [detailModal, setDetailModal] = useState(false);
  const [detailPriority, setDetailPriority] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await priorities.list();
      const items = res.data.data ?? [];
      setItems(items);
      items.forEach((p: Priority) => fetchStats(p.id));
    } catch { toast("Failed to load priorities", "error"); } finally { setLoading(false); }
  };

  const openDetail = async (priority: Priority) => {
    setDetailLoading(true);
    try {
      const res = await priorities.get(priority.id);
      setDetailPriority(res.data.data);
      setDetailModal(true);
    } catch { toast("Failed to load priority details", "error"); } finally { setDetailLoading(false); }
  };

  const fetchStats = async (id: number) => {
    try {
      const res = await priorities.stats(id);
      setStats((prev) => ({ ...prev, [id]: res.data.data! }));
    } catch { /* ignore */ }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(INITIAL_FORM);
    setShowModal(true);
  };

  const openEdit = (p: Priority) => {
    setEditing(p);
    setForm({
      name: p.name,
      code: p.code,
      description: p.description || "",
      priority_level: p.priority_level,
      severity_level: p.severity_level,
      color: p.color || "#3B82F6",
      sla_hours: p.sla_hours,
      escalation_minutes: p.escalation_minutes,
      auto_escalate: p.auto_escalate,
      requires_approval: p.requires_approval,
      is_active: p.is_active,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editing) {
        await priorities.update(editing.id, form);
        toast("Priority updated", "success");
      } else {
        await priorities.create(form);
        toast("Priority created", "success");
      }
      setShowModal(false);
      fetchItems();
    } catch (err: any) {
      toast(err.response?.data?.message || "Failed to save priority", "error");
    } finally { setSaving(false); }
  };

  const handleDelete = async (p: Priority) => {
    try {
      await priorities.delete(p.id);
      toast("Priority deleted", "success");
      fetchItems();
    } catch { toast("Failed to delete priority", "error"); }
  };

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const value = e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const columns: Column<Priority>[] = [
    { key: "priority_level", header: "Level", render: (p) => (
      <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${p.priority_level >= 4 ? "bg-red-100 text-red-800" : p.priority_level >= 3 ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>{p.priority_level}</span>
    )},
    { key: "name", header: "Name", render: (p) => (
      <span className="font-medium flex items-center gap-2">
        {p.color && <span className="w-3 h-3 rounded-full" style={{ backgroundColor: p.color }} />}
        {p.name}
      </span>
    )},
    { key: "code", header: "Code", render: (p) => <span className="font-mono text-xs text-gray-500">{p.code}</span> },
    { key: "sla_hours", header: "SLA (h)", render: (p) => <span className="text-sm">{p.sla_hours}h</span> },
    { key: "escalation_minutes", header: "Escalation", render: (p) => <span className="text-sm">{p.escalation_minutes}min</span> },
    { key: "auto_escalate", header: "Auto", render: (p) => p.auto_escalate ? <span className="text-green-600 text-sm">Yes</span> : <span className="text-gray-400 text-sm">No</span> },
    { key: "is_active", header: "Active", render: (p) => p.is_active ? <span className="text-green-600 text-sm">Active</span> : <span className="text-red-600 text-sm">Inactive</span> },
    { key: "total_signals", header: "Signals", render: (p) => {
      const s = stats[p.id];
      return <span className="text-sm">{s ? `${s.total_signals}` : "-"}</span>;
    }},
    { key: "actions", header: "", render: (p) => (
      <div className="flex gap-2">
        <button onClick={() => openDetail(p)} className="text-xs text-gray-600 hover:underline">View</button>
        <button onClick={() => openEdit(p)} className="text-xs text-blue-600 hover:underline">Edit</button>
        <button onClick={() => handleDelete(p)} className="text-xs text-red-600 hover:underline">Delete</button>
      </div>
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Priority Management</h1>
        <button onClick={openCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
          + New Priority
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={items}
          loading={loading}
          emptyTitle="No priorities defined"
          keyExtractor={(p) => p.id}
        />
      </div>

      <Modal open={showModal} onClose={() => setShowModal(false)} title={editing ? "Edit Priority" : "Create Priority"} size="lg">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input type="text" value={form.name} onChange={update("name")} required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code *</label>
              <input type="text" value={form.code} onChange={update("code")} required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea value={form.description} onChange={update("description")} rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority Level (1-5)</label>
              <input type="number" min={1} max={5} value={form.priority_level} onChange={update("priority_level")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Severity Level (1-5)</label>
              <input type="number" min={1} max={5} value={form.severity_level} onChange={update("severity_level")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
              <input type="color" value={form.color} onChange={update("color")}
                className="w-full h-9 border border-gray-300 rounded-lg cursor-pointer" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SLA (hours)</label>
              <input type="number" min={1} value={form.sla_hours} onChange={update("sla_hours")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Escalation (min)</label>
              <input type="number" min={0} value={form.escalation_minutes} onChange={update("escalation_minutes")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex gap-6">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={form.auto_escalate} onChange={update("auto_escalate")} className="rounded border-gray-300" />
              <span className="text-sm text-gray-700">Auto-escalate</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={form.requires_approval} onChange={update("requires_approval")} className="rounded border-gray-300" />
              <span className="text-sm text-gray-700">Requires approval</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={form.is_active} onChange={update("is_active")} className="rounded border-gray-300" />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
            <button type="submit" disabled={saving} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
              {saving ? "Saving..." : editing ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={detailModal} onClose={() => setDetailModal(false)} title="Priority Details" size="lg">
        {detailLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        ) : detailPriority ? (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <span className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-lg font-bold ${detailPriority.priority_level >= 4 ? "bg-red-100 text-red-800" : detailPriority.priority_level >= 3 ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>{detailPriority.priority_level}</span>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{detailPriority.name}</h3>
                <span className="font-mono text-xs text-gray-500">{detailPriority.code}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
                <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">General</h4>
                {detailPriority.description && (
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Description</label>
                    <p className="text-sm text-gray-900">{detailPriority.description}</p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">SLA Hours</label>
                    <p className="text-sm font-medium text-gray-900">{detailPriority.sla_hours}h</p>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Escalation Minutes</label>
                    <p className="text-sm font-medium text-gray-900">{detailPriority.escalation_minutes}min</p>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
                <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Flags</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Auto-escalate</span>
                    <span className={`text-sm font-medium ${detailPriority.auto_escalate ? "text-green-600" : "text-gray-400"}`}>{detailPriority.auto_escalate ? "Yes" : "No"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Requires Approval</span>
                    <span className={`text-sm font-medium ${detailPriority.requires_approval ? "text-green-600" : "text-gray-400"}`}>{detailPriority.requires_approval ? "Yes" : "No"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Active</span>
                    <span className={`text-sm font-medium ${detailPriority.is_active ? "text-green-600" : "text-red-600"}`}>{detailPriority.is_active ? "Active" : "Inactive"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Color</span>
                    <span className="flex items-center gap-2 text-sm font-medium text-gray-900">
                      <span className="w-4 h-4 rounded-full border border-gray-300" style={{ backgroundColor: detailPriority.color }} />
                      {detailPriority.color}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Stats</h4>
              <div className="grid grid-cols-5 gap-4">
                <div className="text-center">
                  <label className="block text-xs text-gray-500 mb-1">Total Signals</label>
                  <p className="text-xl font-bold text-gray-900">{detailPriority.total_signals ?? "-"}</p>
                </div>
                <div className="text-center">
                  <label className="block text-xs text-gray-500 mb-1">Resolved</label>
                  <p className="text-xl font-bold text-green-600">{detailPriority.resolved_count ?? "-"}</p>
                </div>
                <div className="text-center">
                  <label className="block text-xs text-gray-500 mb-1">Avg Resolution</label>
                  <p className="text-xl font-bold text-gray-900">{detailPriority.avg_resolution_time ? `${detailPriority.avg_resolution_time}h` : "-"}</p>
                </div>
                <div className="text-center">
                  <label className="block text-xs text-gray-500 mb-1">SLA Breaches</label>
                  <p className="text-xl font-bold text-red-600">{detailPriority.sla_breach_count ?? "-"}</p>
                </div>
                <div className="text-center">
                  <label className="block text-xs text-gray-500 mb-1">Escalations</label>
                  <p className="text-xl font-bold text-yellow-600">{detailPriority.escalation_count ?? "-"}</p>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={() => setDetailModal(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Close</button>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
