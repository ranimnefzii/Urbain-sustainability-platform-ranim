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
  { value: "", label: "Plus récents" },
  { value: "created_at:asc", label: "Plus anciens" },
  { value: "priority_level:desc", label: "Priorité + élevée" },
  { value: "priority_level:asc", label: "Priorité - élevée" },
  { value: "title:asc", label: "Titre A-Z" },
  { value: "title:desc", label: "Titre Z-A" },
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

  const { items, page, pages, total, loading, error } = useSignalList({
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

  const getPriorityStyle = (p: Priority | undefined) => {
    if (!p) return "bg-surface-100 text-surface-500";
    if (p.priority_level >= 4) return "bg-red-100 text-red-700 border-red-200";
    if (p.priority_level >= 3) return "bg-amber-100 text-amber-700 border-amber-200";
    return "bg-green-100 text-green-700 border-green-200";
  };

  const columns: Column<Signal>[] = [
    { key: "reference_number", header: "Réf", render: (s) => <span className="font-mono text-xs text-surface-400 bg-surface-50 px-2 py-0.5 rounded">{s.reference_number}</span> },
    { key: "title", header: "Titre", render: (s) => <span className="font-semibold text-surface-800">{s.title}</span> },
    { key: "category", header: "Catégorie", render: (s) => s.category ? <span className="badge bg-brand-50 text-brand-700">{s.category.name}</span> : <span className="text-surface-400">-</span> },
    { key: "status", header: "Statut", render: (s) => <StatusBadge status={s.status} /> },
    { key: "priority", header: "Priorité", render: (s) => <span className={`badge border ${getPriorityStyle(s.priority)}`}>{s.priority?.name || "-"}</span> },
    { key: "created_at", header: "Date", render: (s) => <span className="text-sm text-surface-500">{new Date(s.created_at).toLocaleDateString("fr-FR")}</span> },
    { key: "created_by_user", header: "Signalé par", render: (s) => <span className="text-sm text-surface-600">{s.created_by_user ? `${s.created_by_user.first_name} ${s.created_by_user.last_name}` : "Anonyme"}</span> },
  ];

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="page-title">Signalements</h1>
          <p className="text-sm text-surface-500 mt-1">Consultez et gérez l'ensemble des signalements</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => setShowAdvanced(!showAdvanced)}
            className={`btn-secondary text-sm ${showAdvanced ? "bg-brand-50 border-brand-300 text-brand-700" : ""}`}>
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Filtres
          </button>
          <button onClick={() => navigate("/signals/new")} className="btn-primary">
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Nouveau
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="card-body space-y-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="input-label">Recherche</label>
              <div className="relative">
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                <input type="text" value={filters.search} onChange={(e) => updateFilter("search", e.target.value)}
                  placeholder="Rechercher par titre, référence, description..." className="input-field pl-10" />
              </div>
            </div>
            <div>
              <label className="input-label">Statut</label>
              <select value={filters.status} onChange={(e) => updateFilter("status", e.target.value)}
                className="input-field min-w-[160px]">
                <option value="">Tous les statuts</option>
                {STATUS_OPTIONS.filter(Boolean).map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Catégorie</label>
              <select value={filters.category_id} onChange={(e) => updateFilter("category_id", e.target.value)}
                className="input-field min-w-[180px]">
                <option value="">Toutes les catégories</option>
                {catList.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Trier par</label>
              <select value={filters.sort_by} onChange={(e) => updateFilter("sort_by", e.target.value)}
                className="input-field min-w-[160px]">
                {SORT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div className="flex items-end">
              <button onClick={clearFilters} disabled={!hasActiveFilters}
                className="btn-ghost text-surface-500 disabled:opacity-30">
                Réinitialiser
              </button>
            </div>
          </div>

          {showAdvanced && (
            <div className="flex flex-wrap gap-4 pt-4 border-t border-surface-100 animate-fade-in">
              <div>
                <label className="input-label">Priorité</label>
                <select value={filters.priority_id} onChange={(e) => updateFilter("priority_id", e.target.value)}
                  className="input-field min-w-[160px]">
                  <option value="">Toutes les priorités</option>
                  {priorityList.filter((p) => p.is_active).map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="input-label">Secteur</label>
                <select value={filters.sector_id} onChange={(e) => updateFilter("sector_id", e.target.value)}
                  className="input-field min-w-[180px]">
                  <option value="">Tous les secteurs</option>
                  {sectorList.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div>
                <label className="input-label">Date début</label>
                <input type="date" value={filters.start_date} onChange={(e) => updateFilter("start_date", e.target.value)}
                  className="input-field" />
              </div>
              <div>
                <label className="input-label">Date fin</label>
                <input type="date" value={filters.end_date} onChange={(e) => updateFilter("end_date", e.target.value)}
                  className="input-field" />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results count */}
      {!loading && (
        <p className="text-sm text-surface-400">
          {total} signalement{total !== 1 ? "s" : ""} trouvé{total !== 1 ? "s" : ""}
          {hasActiveFilters && (
            <button onClick={clearFilters} className="ml-2 text-brand-600 hover:underline cursor-pointer">(effacer filtres)</button>
          )}
        </p>
      )}

      {/* Table */}
      <DataTable
        columns={columns}
        data={items}
        loading={loading}
        emptyTitle="Aucun signalement trouvé"
        emptyDescription={filters.search ? "Essayez un autre terme de recherche" : "Soyez le premier à signaler un problème"}
        onRowClick={(s) => navigate(`/signals/${s.id}`)}
        keyExtractor={(s) => s.id}
        pagination={{ page, pages, total, onPageChange: (p) => updateFilter("page", String(p)) }}
      />
    </div>
  );
}
