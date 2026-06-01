import { useState, useEffect, type ReactNode } from "react";
import { reports } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import Modal from "../../components/ui/Modal";
import StatusBadge from "../../components/ui/StatusBadge";
import { useToast } from "../../contexts/ToastContext";
import type { Report, ReportAnalytics } from "../../types";

const REPORT_TYPE_CONFIG: Record<string, { label: string; description: string; needsRef: boolean; refLabel: string; refPlaceholder: string; autoGenerate: boolean }> = {
  SIGNAL_ANALYSIS: { label: "Signal Analysis", description: "Detailed analysis of a specific citizen signal", needsRef: true, refLabel: "Signal ID", refPlaceholder: "Enter signal ID", autoGenerate: false },
  SECTOR_SUMMARY: { label: "Sector Summary", description: "Performance summary for a municipal sector", needsRef: true, refLabel: "Sector ID", refPlaceholder: "Enter sector ID", autoGenerate: false },
  TREND_ANALYSIS: { label: "Trend Analysis", description: "Analyze signal trends over a date range", needsRef: false, refLabel: "", refPlaceholder: "", autoGenerate: false },
  PERFORMANCE_METRICS: { label: "Performance Metrics", description: "System-wide performance and response metrics", needsRef: false, refLabel: "", refPlaceholder: "", autoGenerate: true },
  CITIZEN_FEEDBACK: { label: "Citizen Feedback", description: "Aggregated citizen satisfaction and feedback data", needsRef: false, refLabel: "", refPlaceholder: "", autoGenerate: true },
  PRIORITY_ASSESSMENT: { label: "Priority Assessment", description: "Assess priority distribution across sectors or levels", needsRef: true, refLabel: "Sector ID or Priority Level", refPlaceholder: "Enter sector ID or priority level", autoGenerate: false },
  GENERIC: { label: "Generic Report", description: "Custom report with configurable parameters", needsRef: false, refLabel: "", refPlaceholder: "", autoGenerate: false },
};

const FREQUENCIES = ["ON_DEMAND", "DAILY", "WEEKLY", "MONTHLY"];

const EXPORT_FORMATS = ["pdf", "xlsx", "csv", "json"];

export const REPORT_WORKFLOW_DEFINITION = {
  states: ["DRAFT", "GENERATING", "COMPLETED", "FAILED", "SCHEDULED", "ARCHIVED"],
  transitions: {
    DRAFT: ["GENERATING", "SCHEDULED"],
    GENERATING: ["COMPLETED", "FAILED", "SCHEDULED"],
    COMPLETED: ["ARCHIVED", "SCHEDULED"],
    FAILED: ["GENERATING", "SCHEDULED"],
    SCHEDULED: ["GENERATING", "DRAFT"],
    ARCHIVED: [],
  },
};

function SimpleBar({ label, value, max, color, unit }: { label: string; value: number; max: number; color: string; unit?: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-600 w-24 truncate flex-shrink-0">{label}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${max > 0 ? (value / max) * 100 : 0}%` }} />
      </div>
      <span className="text-xs text-gray-500 w-10 text-right flex-shrink-0">{value}{unit || ""}</span>
    </div>
  );
}

function StatusFlow({ status }: { status: string }) {
  const failed = status === "FAILED";
  const scheduled = status === "SCHEDULED";
  const archived = status === "ARCHIVED";
  const current = scheduled ? "SCHEDULED" : archived ? "ARCHIVED" : status;

  const steps = ["DRAFT", "GENERATING", "COMPLETED"];
  const stepIdx = steps.indexOf(current);

  return (
    <div className="flex items-center gap-0">
      {steps.map((s, i) => (
        <div key={s} className="flex items-center">
          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
            i === stepIdx ? "bg-blue-600 text-white border-blue-600" : i < stepIdx ? "bg-blue-100 text-blue-600 border-blue-300" : "bg-gray-50 text-gray-400 border-gray-200"
          }`}>
            {i < stepIdx ? (
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
            ) : i + 1}
          </div>
          {i < steps.length - 1 && (
            <div className={`w-8 h-0.5 ${i < stepIdx - (failed ? 0 : 0) ? "bg-blue-300" : "bg-gray-200"}`} />
          )}
        </div>
      ))}
      {failed && (
        <>
          <div className="w-8 h-0.5 bg-red-300" />
          <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 bg-red-100 text-red-600 border-red-300">!</div>
        </>
      )}
    </div>
  );
}

function ReportIcon({ type }: { type: string }) {
  const icons: Record<string, ReactNode> = {
    SIGNAL_ANALYSIS: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
    SECTOR_SUMMARY: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>,
    TREND_ANALYSIS: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>,
    PERFORMANCE_METRICS: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>,
    CITIZEN_FEEDBACK: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>,
    PRIORITY_ASSESSMENT: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" /></svg>,
  };
  return (
    <span className="text-gray-500">{icons[type] || <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}</span>
  );
}

export default function ReportManagement() {
  const { toast } = useToast();
  const [data, setData] = useState<{ items: Report[]; page: number; pages: number; total: number }>({ items: [], page: 1, pages: 1, total: 0 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [reportStats, setReportStats] = useState<ReportAnalytics | null>(null);
  const [viewModal, setViewModal] = useState(false);
  const [selected, setSelected] = useState<Report | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Report | null>(null);

  const [wizardOpen, setWizardOpen] = useState(false);
  const [wizardStep, setWizardStep] = useState(1);
  const [wizardData, setWizardData] = useState({
    reportType: "SIGNAL_ANALYSIS",
    refId: "",
    startDate: "",
    endDate: "",
    filters: { categoryId: "", priorityLevel: "", sectorId: "" },
    includeCharts: true,
    frequency: "ON_DEMAND",
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const [scheduleModal, setScheduleModal] = useState(false);
  const [scheduleTarget, setScheduleTarget] = useState<Report | null>(null);
  const [scheduleFreq, setScheduleFreq] = useState("ON_DEMAND");
  const [scheduleSaving, setScheduleSaving] = useState(false);

  const [exportFormat, setExportFormat] = useState("pdf");
  const [exportingId, setExportingId] = useState<number | null>(null);

  const fetchData = async (p: number) => {
    setLoading(true);
    try {
      const [listRes, statsRes] = await Promise.all([
        reports.list({ page: p, size: 20 }),
        reports.stats(),
      ]);
      setData(listRes.data.data ?? { items: [], page: 1, pages: 1, total: 0 });
      setReportStats(statsRes.data.data ?? null);
    } catch { toast("Failed to load reports", "error"); } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(page); }, [page]);

  const resetWizard = () => {
    setWizardStep(1);
    setWizardData({
      reportType: "SIGNAL_ANALYSIS",
      refId: "",
      startDate: "",
      endDate: "",
      filters: { categoryId: "", priorityLevel: "", sectorId: "" },
      includeCharts: true,
      frequency: "ON_DEMAND",
    });
    setIsGenerating(false);
  };

  const handleWizardGenerate = async () => {
    setIsGenerating(true);
    try {
      const config = {
        title: `${REPORT_TYPE_CONFIG[wizardData.reportType]?.label || wizardData.reportType} Report`,
        report_type: wizardData.reportType,
        parameters: {
          ...(wizardData.startDate ? { start_date: wizardData.startDate } : {}),
          ...(wizardData.endDate ? { end_date: wizardData.endDate } : {}),
          ...(wizardData.filters.categoryId ? { category_id: Number(wizardData.filters.categoryId) } : {}),
          ...(wizardData.filters.priorityLevel ? { priority_level: Number(wizardData.filters.priorityLevel) } : {}),
          ...(wizardData.filters.sectorId ? { sector_id: Number(wizardData.filters.sectorId) } : {}),
          include_charts: wizardData.includeCharts,
        },
      };

      let res;
      switch (wizardData.reportType) {
        case "SIGNAL_ANALYSIS":
          res = await reports.generateSignalReport(Number(wizardData.refId));
          break;
        case "SECTOR_SUMMARY":
          res = await reports.generateSectorReport(Number(wizardData.refId));
          break;
        case "TREND_ANALYSIS":
          res = await reports.generateTrendReport(config);
          break;
        case "PERFORMANCE_METRICS":
          res = await reports.generatePerformanceReport({
            ...(wizardData.startDate ? { start_date: wizardData.startDate } : {}),
            ...(wizardData.endDate ? { end_date: wizardData.endDate } : {}),
          });
          break;
        case "CITIZEN_FEEDBACK":
          res = await reports.generateCitizenFeedbackReport({
            ...(wizardData.startDate ? { start_date: wizardData.startDate } : {}),
            ...(wizardData.endDate ? { end_date: wizardData.endDate } : {}),
          });
          break;
        case "PRIORITY_ASSESSMENT":
          res = await reports.generatePriorityAssessment({
            ...(wizardData.filters.sectorId ? { sector_id: Number(wizardData.filters.sectorId) } : {}),
            ...(wizardData.filters.priorityLevel ? { priority_level: Number(wizardData.filters.priorityLevel) } : {}),
            ...(wizardData.startDate ? { start_date: wizardData.startDate } : {}),
            ...(wizardData.endDate ? { end_date: wizardData.endDate } : {}),
          });
          break;
        default:
          res = await reports.create(config);
      }

      if (wizardData.frequency && wizardData.frequency !== "ON_DEMAND" && res.data.data?.id) {
        await reports.schedule(res.data.data.id, wizardData.frequency);
        toast("Report scheduled successfully", "success");
      }

      toast("Report generated successfully", "success");
      setWizardOpen(false);
      resetWizard();
      fetchData(page);
    } catch (err: any) {
      toast(err.response?.data?.message || "Generation failed", "error");
    } finally { setIsGenerating(false); }
  };

  const handleExport = async (report: Report, format: string) => {
    setExportingId(report.id);
    try {
      const res = await reports.export(report.id, format);
      const content = res.data?.data ? JSON.stringify(res.data.data, null, 2) : "";
      const mimeTypes: Record<string, string> = { pdf: "application/pdf", xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", csv: "text/csv", json: "application/json" };
      const blob = new Blob([content], { type: mimeTypes[format] || "application/octet-stream" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${report.title || "report"}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast("Export successful", "success");
    } catch { toast("Export failed", "error"); } finally { setExportingId(null); }
  };

  const handleArchive = async (report: Report) => {
    try {
      await reports.archive(report.id);
      toast("Report archived", "success");
      fetchData(page);
      setViewModal(false);
    } catch { toast("Failed to archive report", "error"); }
  };

  const handleSchedule = async () => {
    if (!scheduleTarget) return;
    setScheduleSaving(true);
    try {
      await reports.schedule(scheduleTarget.id, scheduleFreq);
      toast("Report scheduled successfully", "success");
      setScheduleModal(false);
      setScheduleTarget(null);
      fetchData(page);
    } catch { toast("Failed to update schedule", "error"); } finally { setScheduleSaving(false); }
  };

  const reportTypesKeyed = Object.entries(REPORT_TYPE_CONFIG);

  const columns: Column<Report>[] = [
    {
      key: "title", header: "Title",
      render: (r) => (
        <div className="flex items-center gap-2">
          <ReportIcon type={r.report_type} />
          <span className="font-medium">{r.title}</span>
          {r.frequency && r.frequency !== "ON_DEMAND" && (
            <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium">SCHEDULED</span>
          )}
        </div>
      ),
    },
    { key: "report_type", header: "Type", render: (r) => <span className="text-xs font-medium text-gray-500">{REPORT_TYPE_CONFIG[r.report_type]?.label || r.report_type}</span> },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "frequency", header: "Frequency", render: (r) => {
      const freq = r.frequency || "ON_DEMAND";
      return <span className={`text-xs font-medium px-2 py-0.5 rounded ${freq === "ON_DEMAND" ? "bg-gray-100 text-gray-600" : "bg-purple-100 text-purple-700"}`}>{freq}</span>;
    }},
    { key: "created_at", header: "Created", render: (r) => <span className="text-gray-500">{new Date(r.created_at).toLocaleDateString()}</span> },
    { key: "generated_at", header: "Generated", render: (r) => r.generated_at ? <span className="text-gray-500">{new Date(r.generated_at).toLocaleDateString()}</span> : <span className="text-gray-400">-</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <button onClick={() => { resetWizard(); setWizardOpen(true); }} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Generate Report</button>
      </div>

      {reportStats && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Total Reports</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{reportStats.total_reports}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Reports by Type</p>
            <div className="space-y-1.5">
              {Object.entries(reportStats.reports_by_type || {}).map(([k, v], i) => {
                const colors = ["bg-blue-400", "bg-green-400", "bg-purple-400", "bg-yellow-400", "bg-red-400", "bg-indigo-400"];
                return <SimpleBar key={k} label={REPORT_TYPE_CONFIG[k]?.label || k} value={v} max={reportStats.total_reports} color={colors[i % colors.length]} unit="" />;
              })}
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Reports by Status</p>
            <div className="space-y-1.5">
              {Object.entries(reportStats.reports_by_status || {}).map(([k, v]) => {
                const statusColors: Record<string, string> = { DRAFT: "bg-gray-400", GENERATING: "bg-blue-400", COMPLETED: "bg-green-400", FAILED: "bg-red-400", SCHEDULED: "bg-purple-400", ARCHIVED: "bg-gray-300" };
                return <SimpleBar key={k} label={k} value={v} max={reportStats.total_reports} color={statusColors[k] || "bg-blue-400"} unit="" />;
              })}
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Avg Generation Time</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{(reportStats.avg_generation_time_ms / 1000).toFixed(1)}<span className="text-lg font-normal text-gray-500">s</span></p>
            <div className="mt-4 space-y-1.5">
              {reportStats.most_accessed_reports && reportStats.most_accessed_reports.slice(0, 3).map((r, i) => (
                <SimpleBar key={r.id} label={r.title} value={r.access_count} max={reportStats.most_accessed_reports?.[0]?.access_count || 1} color={["bg-amber-400", "bg-amber-300", "bg-amber-200"][i]} unit="x" />
              ))}
            </div>
            {reportStats.reports_by_frequency && Object.keys(reportStats.reports_by_frequency).length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Frequency</p>
                {Object.entries(reportStats.reports_by_frequency).map(([k, v]) => (
                  <SimpleBar key={k} label={k} value={v} max={Math.max(...Object.values(reportStats.reports_by_frequency || {}), 1)} color="bg-teal-400" />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <DataTable columns={columns} data={data.items} loading={loading} emptyTitle="No reports yet" keyExtractor={(r) => r.id}
        onRowClick={async (r) => {
          try {
            const res = await reports.get(r.id);
            setSelected(res.data.data ?? null);
          } catch { setSelected(r); }
          setViewModal(true);
        }}
        pagination={{ page: data.page, pages: data.pages, total: data.total, onPageChange: setPage }} />

      <Modal open={viewModal} onClose={() => setViewModal(false)} title={selected?.title || "Report"} size="xl">
        {selected && (
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <ReportIcon type={selected.report_type} />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{selected.title}</h3>
                <p className="text-sm text-gray-500">{REPORT_TYPE_CONFIG[selected.report_type]?.label || selected.report_type}</p>
              </div>
              <StatusBadge status={selected.status} size="md" />
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Status Timeline</p>
              <StatusFlow status={selected.status} />
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-white border border-gray-200 rounded-lg p-3">
                <p className="text-xs text-gray-500">Frequency</p>
                <p className="font-medium mt-0.5">{selected.frequency || "ON_DEMAND"}</p>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-3">
                <p className="text-xs text-gray-500">Created</p>
                <p className="font-medium mt-0.5">{new Date(selected.created_at).toLocaleString()}</p>
              </div>
              {selected.generated_at && (
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Generated</p>
                  <p className="font-medium mt-0.5">{new Date(selected.generated_at).toLocaleString()}</p>
                </div>
              )}
              {selected.scheduled_at && (
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Next Scheduled</p>
                  <p className="font-medium mt-0.5">{new Date(selected.scheduled_at).toLocaleString()}</p>
                </div>
              )}
              {selected.status === "FAILED" && (
                <div className="bg-white border border-red-200 rounded-lg p-3 col-span-2">
                  <p className="text-xs text-red-500">Error Details</p>
                  <p className="text-sm text-red-700 mt-0.5">{selected.description || "Generation failed"}</p>
                </div>
              )}
            </div>

            {selected.parameters && typeof selected.parameters === "object" && Object.keys(selected.parameters).length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-3">
                <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Parameters</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(selected.parameters).filter(([k]) => k !== "include_charts").map(([k, v]) => (
                    <span key={k} className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-700">
                      <span className="font-medium">{k.replace(/_/g, " ")}:</span> {String(v)}
                    </span>
                  ))}
                  {selected.parameters?.include_charts !== undefined && (
                    <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-700">
                      <span className="font-medium">Charts:</span> {selected.parameters.include_charts ? "Yes" : "No"}
                    </span>
                  )}
                </div>
              </div>
            )}

            {selected.tags && selected.tags.length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {selected.tags.map((t, i) => <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs border border-blue-200">{t}</span>)}
              </div>
            )}

            {selected.description && !selected.status?.includes("FAIL") && (
              <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">{selected.description}</p>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2">
                {(selected.status === "DRAFT" || selected.status === "SCHEDULED" || selected.status === "COMPLETED" || selected.status === "GENERATING") && (
                  <div className="flex items-center gap-2">
                    <select value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}
                      className="border border-gray-300 rounded-lg px-2 py-2 text-sm bg-white">
                      {EXPORT_FORMATS.map((f) => <option key={f} value={f}>{f.toUpperCase()}</option>)}
                    </select>
                    <button onClick={() => handleExport(selected, exportFormat)} disabled={exportingId === selected.id}
                      className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50">
                      {exportingId === selected.id ? "Exporting..." : "Export"}
                    </button>
                  </div>
                )}
                {selected.status !== "ARCHIVED" && (
                  <button onClick={() => handleArchive(selected)}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                    Archive
                  </button>
                )}
                {(selected.status === "DRAFT" || selected.status === "GENERATING" || selected.status === "COMPLETED" || selected.status === "FAILED") && (
                  <button onClick={() => { setScheduleTarget(selected); setScheduleFreq(selected.frequency || "ON_DEMAND"); setScheduleModal(true); }}
                    className="px-4 py-2 text-sm border border-purple-300 text-purple-700 rounded-lg hover:bg-purple-50">
                    Schedule
                  </button>
                )}
              </div>
              <button onClick={() => { setDeleteTarget(selected!); setShowDeleteConfirm(true); }}
                className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
                Delete
              </button>
            </div>
          </div>
        )}
      </Modal>

      <Modal open={showDeleteConfirm} onClose={() => { setShowDeleteConfirm(false); setDeleteTarget(null); }} title="Delete Report">
        <div className="space-y-4">
          <p className="text-sm text-gray-700">Are you sure you want to delete <strong>{deleteTarget?.title}</strong>? This action cannot be undone.</p>
          <div className="flex justify-end gap-3 pt-2">
            <button onClick={() => { setShowDeleteConfirm(false); setDeleteTarget(null); }} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
            <button onClick={async () => {
              if (!deleteTarget) return;
              setLoading(true);
              try {
                await reports.delete(deleteTarget.id);
                toast("Report deleted", "success");
                setShowDeleteConfirm(false);
                setDeleteTarget(null);
                setViewModal(false);
                fetchData(page);
              } catch { toast("Failed to delete report", "error"); } finally { setLoading(false); }
            }} className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">Delete</button>
          </div>
        </div>
      </Modal>

      <Modal open={wizardOpen} onClose={() => { if (!isGenerating) { setWizardOpen(false); resetWizard(); } }} title={`Generate Report - Step ${wizardStep} of 4`} size="lg">
        <div className="space-y-5">
          {wizardStep === 1 && (
            <div>
              <p className="text-sm text-gray-600 mb-3">Select the type of report you want to generate.</p>
              <div className="grid grid-cols-1 gap-2">
                {reportTypesKeyed.map(([key, cfg]) => (
                  <button key={key} onClick={() => setWizardData((p) => ({ ...p, reportType: key }))}
                    className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-colors ${
                      wizardData.reportType === key ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500" : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    }`}>
                    <span className={`mt-0.5 ${wizardData.reportType === key ? "text-blue-600" : "text-gray-400"}`}><ReportIcon type={key} /></span>
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${wizardData.reportType === key ? "text-blue-800" : "text-gray-900"}`}>{cfg.label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{cfg.description}</p>
                    </div>
                    {cfg.autoGenerate && <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">Auto</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          {wizardStep === 2 && (
            <div className="space-y-4">
              {REPORT_TYPE_CONFIG[wizardData.reportType]?.needsRef && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{REPORT_TYPE_CONFIG[wizardData.reportType].refLabel}</label>
                  <input type="number" value={wizardData.refId} onChange={(e) => setWizardData((p) => ({ ...p, refId: e.target.value }))} min={1}
                    placeholder={REPORT_TYPE_CONFIG[wizardData.reportType].refPlaceholder} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
              )}
              {!REPORT_TYPE_CONFIG[wizardData.reportType]?.autoGenerate && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                      <input type="date" value={wizardData.startDate} onChange={(e) => setWizardData((p) => ({ ...p, startDate: e.target.value }))}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                      <input type="date" value={wizardData.endDate} onChange={(e) => setWizardData((p) => ({ ...p, endDate: e.target.value }))}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                      <input type="number" value={wizardData.filters.categoryId} onChange={(e) => setWizardData((p) => ({ ...p, filters: { ...p.filters, categoryId: e.target.value } }))} placeholder="Category ID"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                      <input type="number" min={1} max={5} value={wizardData.filters.priorityLevel} onChange={(e) => setWizardData((p) => ({ ...p, filters: { ...p.filters, priorityLevel: e.target.value } }))} placeholder="Level 1-5"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Sector</label>
                      <input type="number" value={wizardData.filters.sectorId} onChange={(e) => setWizardData((p) => ({ ...p, filters: { ...p.filters, sectorId: e.target.value } }))} placeholder="Sector ID"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                    </div>
                  </div>
                </>
              )}
              <div className="flex items-center gap-2">
                <input type="checkbox" id="includeCharts" checked={wizardData.includeCharts}
                  onChange={(e) => setWizardData((p) => ({ ...p, includeCharts: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                <label htmlFor="includeCharts" className="text-sm text-gray-700">Include charts in report</label>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Frequency (for scheduling)</label>
                <select value={wizardData.frequency} onChange={(e) => setWizardData((p) => ({ ...p, frequency: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                  {FREQUENCIES.map((f) => <option key={f} value={f}>{f.replace(/_/g, " ")}</option>)}
                </select>
              </div>
            </div>
          )}

          {wizardStep === 3 && (
            <div className="space-y-4">
              <p className="text-sm text-gray-500">Review your report configuration before generating.</p>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <ReportIcon type={wizardData.reportType} />
                  <span className="text-sm font-medium text-gray-900">{REPORT_TYPE_CONFIG[wizardData.reportType]?.label || wizardData.reportType}</span>
                </div>
                <div className="text-xs text-gray-500 space-y-1">
                  {wizardData.refId && <p>Reference ID: <span className="font-medium text-gray-700">{wizardData.refId}</span></p>}
                  {wizardData.startDate && <p>Date Range: <span className="font-medium text-gray-700">{wizardData.startDate} to {wizardData.endDate || "now"}</span></p>}
                  {wizardData.filters.categoryId && <p>Category: <span className="font-medium text-gray-700">ID {wizardData.filters.categoryId}</span></p>}
                  {wizardData.filters.priorityLevel && <p>Priority: <span className="font-medium text-gray-700">Level {wizardData.filters.priorityLevel}</span></p>}
                  {wizardData.filters.sectorId && <p>Sector: <span className="font-medium text-gray-700">ID {wizardData.filters.sectorId}</span></p>}
                  <p>Charts: <span className="font-medium text-gray-700">{wizardData.includeCharts ? "Included" : "Excluded"}</span></p>
                  <p>Frequency: <span className="font-medium text-gray-700">{wizardData.frequency.replace(/_/g, " ")}</span></p>
                </div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 text-sm text-blue-800">
                <p className="font-medium">What will be generated:</p>
                <p className="mt-1 text-blue-700">
                  {wizardData.reportType === "SIGNAL_ANALYSIS" && "Signal details, priority assessment, status history, and AI insights for the selected signal."}
                  {wizardData.reportType === "SECTOR_SUMMARY" && "Sector performance metrics, signal distribution, resolution times, and satisfaction rates."}
                  {wizardData.reportType === "TREND_ANALYSIS" && "Signal trends over time, category breakdowns, and prediction insights within the date range."}
                  {wizardData.reportType === "PERFORMANCE_METRICS" && "System-wide KPIs including resolution rates, response times, and operational efficiency."}
                  {wizardData.reportType === "CITIZEN_FEEDBACK" && "Aggregated citizen feedback scores, satisfaction trends, and category-level ratings."}
                  {wizardData.reportType === "PRIORITY_ASSESSMENT" && "Priority distribution analysis, SLA compliance, and escalation patterns."}
                  {wizardData.reportType === "GENERIC" && "Custom report with the configured parameters and filters."}
                  {!["SIGNAL_ANALYSIS", "SECTOR_SUMMARY", "TREND_ANALYSIS", "PERFORMANCE_METRICS", "CITIZEN_FEEDBACK", "PRIORITY_ASSESSMENT", "GENERIC"].includes(wizardData.reportType) && "Report with the selected configuration."}
                </p>
              </div>
            </div>
          )}

          {wizardStep === 4 && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <svg className="w-12 h-12 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm font-medium text-green-800 mt-2">Ready to Generate</p>
                <p className="text-xs text-green-700 mt-1">Click "Generate" to create the report. This may take a moment.</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600">
                <p><strong>Type:</strong> {REPORT_TYPE_CONFIG[wizardData.reportType]?.label || wizardData.reportType}</p>
                {wizardData.frequency !== "ON_DEMAND" && <p className="mt-1"><strong>Schedule:</strong> This report will be set to {wizardData.frequency.replace(/_/g, " ").toLowerCase()} generation.</p>}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t">
            <div className="flex gap-1">
              {[1, 2, 3, 4].map((s) => (
                <div key={s} className={`w-2 h-2 rounded-full ${s === wizardStep ? "bg-blue-600" : s < wizardStep ? "bg-blue-300" : "bg-gray-200"}`} />
              ))}
            </div>
            <div className="flex gap-3">
              {wizardStep > 1 && (
                <button onClick={() => setWizardStep((s) => s - 1)} disabled={isGenerating}
                  className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50">
                  Previous
                </button>
              )}
              {wizardStep < 4 ? (
                <button onClick={() => setWizardStep((s) => s + 1)}
                  disabled={wizardStep === 1 && !wizardData.reportType}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
                  Next
                </button>
              ) : (
                <button onClick={handleWizardGenerate} disabled={isGenerating || (REPORT_TYPE_CONFIG[wizardData.reportType]?.needsRef && !wizardData.refId)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50 flex items-center gap-2">
                  {isGenerating && (
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  )}
                  {isGenerating ? "Generating..." : "Generate"}
                </button>
              )}
            </div>
          </div>
        </div>
      </Modal>

      <Modal open={scheduleModal} onClose={() => { setScheduleModal(false); setScheduleTarget(null); }} title="Schedule Report">
        {scheduleTarget && (
          <div className="space-y-4">
            <p className="text-sm text-gray-700">Configure schedule for <strong>{scheduleTarget.title}</strong></p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Generation Frequency</label>
              <select value={scheduleFreq} onChange={(e) => setScheduleFreq(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                {FREQUENCIES.map((f) => <option key={f} value={f}>{f.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            {scheduleFreq !== "ON_DEMAND" && (
              <div className="bg-purple-50 rounded-lg p-3 text-sm text-purple-800">
                <p className="font-medium">Schedule Active</p>
                <p className="text-purple-700 mt-1">This report will be automatically generated {scheduleFreq.toLowerCase()}. Set to "ON_DEMAND" to disable scheduling.</p>
              </div>
            )}
            <div className="flex justify-end gap-3 pt-2">
              <button onClick={() => { setScheduleModal(false); setScheduleTarget(null); }} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={handleSchedule} disabled={scheduleSaving}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50">
                {scheduleSaving ? "Saving..." : "Save Schedule"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
