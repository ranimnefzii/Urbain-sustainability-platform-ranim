import { useState, useEffect, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useSignalList } from "../../hooks/useSignals";
import { useCategories } from "../../hooks/useCategories";
import { priorities, sectors } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import StatusBadge from "../../components/ui/StatusBadge";
import type { Signal, Priority, Sector } from "../../types";

const STATUS_OPTIONS = ["", "SUBMITTED", "PENDING", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED", "CANCELLED", "REJECTED", "DRAFT"];
const SORT_OPTIONS = [
  { value: "", label: "Newest First" },
  { value: "created_at:asc", label: "Oldest First" },
  { value: "priority_level:desc", label: "Highest Priority" },
  { value: "priority_level:asc", label: "Lowest Priority" },
  { value: "title:asc", label: "Title A-Z" },
  { value: "title:desc", label: "Title Z-A" },
];

export default function SignalList() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { categories: catList } = useCategories();
  const [priorityList, setPriorityList] = useState<Priority[]>([]);
  const [sectorList, setSectorList] = useState<Sector[]>([]);

  const [showAdvanced, setShowAdvanced] = useState(false);

  const [filters, setFilters] = useState({
    status: searchParams.get("status") || "",
    category_id: searchParams.get("category_id") || "",
    priority_id: searchParams.get("priority_id") || "",
    sector_id: searchParams.get("sector_id") || "",
    search: searchParams.get("search") || "",
    start_date: searchParams.get("start_date") || "",
    end_date: searchParams.get("end_date") || "",
    sort_by: searchParams.get("sort_by") || "",
    page: parseInt(searchParams.get("page") || "1"),
    size: 20,
  });

  useEffect(() => {
    priorities.list().then((res) => setPriorityList(res.data.data ?? [])).catch(() => {});
    sectors.list().then((res) => setSectorList(res.data.data ?? [])).catch(() => {});
  }, []);

  const { items, page, pages, total, loading } = useSignalList({
    ...filters,
    status: filters.status || undefined,
    category_id: filters.category_id ? Number(filters.category_id) : undefined,
    priority_id: filters.priority_id ? Number(filters.priority_id) : undefined,
    sector_id: filters.sector_id ? Number(filters.sector_id) : undefined,
    search: filters.search || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
    sort_by: filters.sort_by || undefined,
  });

  const updateFilter = useCallback((key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: key === "page" ? Number(value) : 1 }));
    const sp = new URLSearchParams(searchParams);
    if (value) sp.set(key, value); else sp.delete(key);
    if (key !== "page") sp.set("page", "1");
    setSearchParams(sp);
  }, [searchParams, setSearchParams]);

  const clearFilters = () => {
    setFilters({ status: "", category_id: "", priority_id: "", sector_id: "", search: "", start_date: "", end_date: "", sort_by: "", page: 1, size: 20 });
    setSearchParams({});
  };

  const hasActiveFilters = filters.status || filters.category_id || filters.priority_id || filters.sector_id || filters.search || filters.start_date || filters.end_date || filters.sort_by;

  const columns: Column<Signal>[] = [
    { key: "reference_number", header: "Ref #", render: (s) => <span className="font-mono text-xs text-gray-500">{s.reference_number}</span> },
    { key: "title", header: "Title", render: (s) => <span className="font-medium text-gray-900">{s.title}</span> },
    { key: "category", header: "Category", render: (s) => s.category?.name || "-" },
    { key: "status", header: "Status", render: (s) => <StatusBadge status={s.status} /> },
    { key: "priority", header: "Priority", render: (s) => s.priority ? <span className={`text-xs font-medium px-2 py-0.5 rounded ${s.priority.priority_level >= 4 ? "bg-red-100 text-red-800" : s.priority.priority_level >= 3 ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>{s.priority.name}</span> : "-" },
    { key: "created_at", header: "Created", render: (s) => new Date(s.created_at).toLocaleDateString() },
    { key: "created_by_user", header: "Reporter", render: (s) => s.created_by_user ? `${s.created_by_user.first_name} ${s.created_by_user.last_name}` : "Anonymous" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Signals</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowAdvanced(!showAdvanced)} className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
            {showAdvanced ? "Simple" : "Advanced"} Filters
          </button>
          <button onClick={() => navigate("/signals/new")} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
            + New Signal
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-gray-500 mb-1">Search</label>
            <input type="text" value={filters.search} onChange={(e) => updateFilter("search", e.target.value)}
              placeholder="Search by title, ref, description..." className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="w-40">
            <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
            <select value={filters.status} onChange={(e) => updateFilter("status", e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">All Statuses</option>
              {STATUS_OPTIONS.filter(Boolean).map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
            </select>
          </div>
          <div className="w-48">
            <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
            <select value={filters.category_id} onChange={(e) => updateFilter("category_id", e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">All Categories</option>
              {catList.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="w-40">
            <label className="block text-xs font-medium text-gray-500 mb-1">Sort</label>
            <select value={filters.sort_by} onChange={(e) => updateFilter("sort_by", e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              {SORT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
          <div className="flex items-end">
            <button onClick={clearFilters} disabled={!hasActiveFilters}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg disabled:opacity-50">
              Clear
            </button>
          </div>
        </div>

        {showAdvanced && (
          <div className="flex flex-wrap gap-4 pt-2 border-t border-gray-100">
            <div className="w-48">
              <label className="block text-xs font-medium text-gray-500 mb-1">Priority</label>
              <select value={filters.priority_id} onChange={(e) => updateFilter("priority_id", e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">All Priorities</option>
                {priorityList.filter((p) => p.is_active).map((p) => (
                  <option key={p.id} value={p.id}>{p.name} (L{p.priority_level})</option>
                ))}
              </select>
            </div>
            <div className="w-48">
              <label className="block text-xs font-medium text-gray-500 mb-1">Sector</label>
              <select value={filters.sector_id} onChange={(e) => updateFilter("sector_id", e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">All Sectors</option>
                {sectorList.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Start Date</label>
              <input type="date" value={filters.start_date} onChange={(e) => updateFilter("start_date", e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">End Date</label>
              <input type="date" value={filters.end_date} onChange={(e) => updateFilter("end_date", e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
        )}
      </div>

      <DataTable
        columns={columns}
        data={items}
        loading={loading}
        emptyTitle="No signals found"
        emptyDescription={filters.search ? "Try a different search term" : "Be the first to report a signal"}
        onRowClick={(s) => navigate(`/signals/${s.id}`)}
        keyExtractor={(s) => s.id}
        pagination={{ page, pages, total, onPageChange: (p) => updateFilter("page", String(p)) }}
      />
    </div>
  );
}
