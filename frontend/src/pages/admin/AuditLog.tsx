import { useState, useEffect } from "react";
import { admin } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import StatusBadge from "../../components/ui/StatusBadge";
import { useToast } from "../../contexts/ToastContext";

export default function AuditLog() {
  const { toast } = useToast();
  const [data, setData] = useState<{ items: any[]; page: number; pages: number; total: number }>({ items: [], page: 1, pages: 1, total: 0 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("");

  const fetchData = async (p: number) => {
    setLoading(true);
    try {
      const params: Record<string, any> = { page: p, size: 50 };
      if (search) params.search = search;
      if (actionFilter) params.action = actionFilter;
      const res = await admin.auditLog(params);
      setData(res.data.data ?? { items: [], page: 1, pages: 1, total: 0 });
    } catch { toast("Failed to load audit log", "error"); } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(page); }, [page, search, actionFilter]);

  const columns: Column<any>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "reference_number", header: "Ref", render: (r) => <span className="font-mono text-xs">{r.reference_number || "-"}</span> },
    { key: "title", header: "Title", render: (r) => <span className="font-medium">{r.title || r.action || "-"}</span> },
    { key: "action", header: "Action", render: (r) => <span className="text-xs font-medium px-2 py-0.5 rounded bg-gray-100">{r.action || "-"}</span> },
    { key: "status", header: "Status", render: (r) => r.status ? <StatusBadge status={r.status} /> : "-" },
    { key: "actor", header: "Actor", render: (r) => r.actor_email || r.actor || "-" },
    { key: "created_at", header: "Date", render: (r) => r.created_at ? new Date(r.created_at).toLocaleString() : "-" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
        <span className="text-sm text-gray-500">{data.total} entries</span>
      </div>

      <div className="bg-white p-4 rounded-lg border border-gray-200 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Search</label>
          <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search entries..." className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div className="w-48">
          <label className="block text-xs font-medium text-gray-500 mb-1">Action</label>
          <select value={actionFilter} onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">All Actions</option>
            <option value="CREATE">Create</option>
            <option value="UPDATE">Update</option>
            <option value="DELETE">Delete</option>
            <option value="ASSIGN">Assign</option>
            <option value="RESOLVE">Resolve</option>
            <option value="CANCEL">Cancel</option>
            <option value="LOGIN">Login</option>
          </select>
        </div>
        <div className="flex items-end">
          <button onClick={() => { setSearch(""); setActionFilter(""); setPage(1); }}
            disabled={!search && !actionFilter}
            className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg disabled:opacity-50">
            Clear
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={data.items}
          loading={loading}
          emptyTitle="No audit log entries"
          keyExtractor={(r) => r.id}
          pagination={{ page: data.page, pages: data.pages, total: data.total, onPageChange: setPage }}
        />
      </div>
    </div>
  );
}
