import { useState, useEffect } from "react";
import { priorities, admin, signals } from "../../api/endpoints";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import { WorkflowActionPanel, WorkflowTimeline } from "../../components/workflow";
import type { Priority, PriorityStats, Signal } from "../../types";

export interface PriorityEscalationWorkflowDefinition {
  id: string;
  name: string;
  description: string;
  states: Record<string, {
    id: string;
    label: string;
    description: string;
    color: string;
    icon: string;
    category: "initial" | "active" | "terminal" | "success" | "failure";
  }>;
  transitions: {
    from: string;
    to: string;
    label: string;
    description: string;
    action: string;
    roles: string[];
    requiresConfirmation: boolean;
    requiresForm: boolean;
  }[];
  initialState: string;
  terminalStates: string[];
  roles: string[];
}

const ESCALATION_WORKFLOW: PriorityEscalationWorkflowDefinition = {
  id: "priority-escalation",
  name: "Priority Escalation",
  description: "Manages the lifecycle of priority-based signal escalation from normal monitoring through escalation",
  states: {
    NORMAL: {
      id: "NORMAL",
      label: "Normal",
      description: "Signal is within SLA thresholds. Normal operations continue.",
      color: "green",
      icon: "✓",
      category: "initial",
    },
    WARNING: {
      id: "WARNING",
      label: "Warning",
      description: "Signal is approaching the SLA breach threshold. Attention recommended.",
      color: "yellow",
      icon: "⚠",
      category: "active",
    },
    BREACHED: {
      id: "BREACHED",
      label: "Breached",
      description: "SLA has been exceeded. Immediate action required.",
      color: "red",
      icon: "✕",
      category: "failure",
    },
    ESCALATED: {
      id: "ESCALATED",
      label: "Escalated",
      description: "Signal has been escalated to higher authority for resolution.",
      color: "purple",
      icon: "↑",
      category: "active",
    },
  },
  transitions: [
    {
      from: "NORMAL",
      to: "WARNING",
      label: "Enter Warning",
      description: "Signal crosses the warning threshold (80% of SLA time elapsed)",
      action: "enter_warning",
      roles: ["admin", "manager"],
      requiresConfirmation: false,
      requiresForm: false,
    },
    {
      from: "WARNING",
      to: "BREACHED",
      label: "SLA Breached",
      description: "Signal has exceeded the maximum allowed SLA time",
      action: "sla_breach",
      roles: ["admin", "manager"],
      requiresConfirmation: false,
      requiresForm: false,
    },
    {
      from: "NORMAL",
      to: "BREACHED",
      label: "Direct Breach",
      description: "Signal has directly exceeded SLA thresholds",
      action: "direct_breach",
      roles: ["admin", "manager"],
      requiresConfirmation: true,
      requiresForm: false,
    },
    {
      from: "BREACHED",
      to: "ESCALATED",
      label: "Escalate",
      description: "Escalate the signal to higher authority for immediate action",
      action: "escalate",
      roles: ["admin", "manager"],
      requiresConfirmation: true,
      requiresForm: false,
    },
    {
      from: "WARNING",
      to: "NORMAL",
      label: "Resolve Warning",
      description: "Signal has been resolved and is back within normal thresholds",
      action: "resolve_warning",
      roles: ["admin", "manager", "operator"],
      requiresConfirmation: false,
      requiresForm: false,
    },
    {
      from: "BREACHED",
      to: "NORMAL",
      label: "Resolve Breach",
      description: "Signal has been resolved and SLA breach is addressed",
      action: "resolve_breach",
      roles: ["admin", "manager"],
      requiresConfirmation: true,
      requiresForm: false,
    },
    {
      from: "ESCALATED",
      to: "NORMAL",
      label: "Resolve Escalation",
      description: "Escalated signal has been successfully resolved",
      action: "resolve_escalation",
      roles: ["admin"],
      requiresConfirmation: true,
      requiresForm: false,
    },
  ],
  initialState: "NORMAL",
  terminalStates: [],
  roles: ["admin", "manager", "operator"],
};

const PRIORITY_COLORS: Record<number, { badge: string; bg: string; border: string; text: string; level: string }> = {
  5: { badge: "bg-red-100 text-red-800", bg: "bg-red-50", border: "border-red-200", text: "text-red-700", level: "Critical" },
  4: { badge: "bg-orange-100 text-orange-800", bg: "bg-orange-50", border: "border-orange-200", text: "text-orange-700", level: "High" },
  3: { badge: "bg-yellow-100 text-yellow-800", bg: "bg-yellow-50", border: "border-yellow-200", text: "text-yellow-700", level: "Medium" },
  2: { badge: "bg-green-100 text-green-800", bg: "bg-green-50", border: "border-green-200", text: "text-green-700", level: "Low" },
  1: { badge: "bg-green-100 text-green-800", bg: "bg-green-50", border: "border-green-200", text: "text-green-700", level: "Low" },
};

function getPerformanceColor(breachRate: number): string {
  if (breachRate <= 5) return "bg-green-500";
  if (breachRate <= 15) return "bg-yellow-500";
  return "bg-red-500";
}

function getPerformanceLabel(breachRate: number): string {
  if (breachRate <= 5) return "Good";
  if (breachRate <= 15) return "Warning";
  return "Critical";
}

function getPerformanceTextColor(breachRate: number): string {
  if (breachRate <= 5) return "text-green-700";
  if (breachRate <= 15) return "text-yellow-700";
  return "text-red-700";
}

function getPerformanceBgColor(breachRate: number): string {
  if (breachRate <= 5) return "bg-green-50";
  if (breachRate <= 15) return "bg-yellow-50";
  return "bg-red-50";
}

interface ResponseTimeData {
  priority_level: number;
  priority_name: string;
  avg_response_time: number;
  sla_target_hours: number;
  avg_resolution_time: number;
  total_signals: number;
  breached_count: number;
}

interface EscalationCandidate {
  signal: Signal;
  priority: Priority;
  hoursElapsed: number;
  deadline: number;
  state: "NORMAL" | "WARNING" | "BREACHED" | "ESCALATED";
}

export default function PriorityEscalationWorkflow() {
  const { toast } = useToast();

  const [loading, setLoading] = useState(true);
  const [priorityList, setPriorityList] = useState<Priority[]>([]);
  const [priorityDetails, setPriorityDetails] = useState<Record<number, Priority>>({});
  const [priorityStatsMap, setPriorityStatsMap] = useState<Record<number, PriorityStats>>({});
  const [responseTimes, setResponseTimes] = useState<ResponseTimeData[]>([]);
  const [escalationCandidates, setEscalationCandidates] = useState<EscalationCandidate[]>([]);
  const [escalatingIds, setEscalatingIds] = useState<Set<number>>(new Set());

  const [editModal, setEditModal] = useState(false);
  const [editingPriority, setEditingPriority] = useState<Priority | null>(null);
  const [editForm, setEditForm] = useState({
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
  });
  const [saving, setSaving] = useState(false);

  const [selectedWorkflowPriority, setSelectedWorkflowPriority] = useState<Priority | null>(null);
  const [workflowEntries, setWorkflowEntries] = useState<{ stateId: string; timestamp?: string; note?: string }[]>([]);
  const [currentWorkflowState, setCurrentWorkflowState] = useState("NORMAL");

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [listRes, responseTimesRes] = await Promise.all([
        priorities.list(),
        admin.responseTimes(30),
      ]);

      const items: Priority[] = listRes.data.data ?? [];
      setPriorityList(items);
      setResponseTimes(responseTimesRes.data.data ?? []);

      const detailsMap: Record<number, Priority> = {};
      const statsMap: Record<number, PriorityStats> = {};
      await Promise.all(
        items.map(async (p: Priority) => {
          try {
            const [detailRes, statsRes] = await Promise.all([
              priorities.get(p.id),
              priorities.stats(p.id),
            ]);
            if (detailRes.data.data) detailsMap[p.id] = detailRes.data.data;
            if (statsRes.data.data) statsMap[p.id] = statsRes.data.data;
          } catch {
            // skip individual failures
          }
        })
      );
      setPriorityDetails(detailsMap);
      setPriorityStatsMap(statsMap);

      const autoPriorities = items.filter((p: Priority) => p.auto_escalate);
      if (autoPriorities.length > 0) {
        const candidates: EscalationCandidate[] = [];
        await Promise.all(
          autoPriorities.map(async (p: Priority) => {
            try {
              const sigRes = await signals.list({
                priority_id: p.id,
                status: "open",
                size: 50,
              });
              const sigs: Signal[] = (sigRes.data.data as any)?.items ?? sigRes.data.data ?? [];
              const slaHours = p.sla_hours || 24;
              const warningThreshold = slaHours * 0.8;
              const now = new Date();
              for (const sig of sigs) {
                const createdAt = new Date(sig.created_at);
                const hoursElapsed = (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60);
                const deadline = slaHours;
                let state: EscalationCandidate["state"] = "NORMAL";
                if (hoursElapsed >= deadline) state = "BREACHED";
                else if (hoursElapsed >= warningThreshold) state = "WARNING";
                candidates.push({
                  signal: sig,
                  priority: p,
                  hoursElapsed,
                  deadline,
                  state,
                });
              }
            } catch {
              // skip
            }
          })
        );
        candidates.sort((a, b) => b.hoursElapsed - a.hoursElapsed);
        setEscalationCandidates(candidates);
      }
    } catch {
      toast("Failed to load escalation workflow data", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleEscalateNow = async (candidate: EscalationCandidate) => {
    setEscalatingIds((prev) => new Set(prev).add(candidate.signal.id));
    try {
      await signals.update(candidate.signal.id, { escalated: true });
      toast(`Signal ${candidate.signal.reference_number} escalated successfully`, "success");
      setEscalationCandidates((prev) => prev.filter((c) => c.signal.id !== candidate.signal.id));
    } catch {
      toast("Failed to escalate signal", "error");
    } finally {
      setEscalatingIds((prev) => {
        const next = new Set(prev);
        next.delete(candidate.signal.id);
        return next;
      });
    }
  };

  const openEditModal = (p: Priority) => {
    setEditingPriority(p);
    setEditForm({
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
    setEditModal(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPriority) return;
    setSaving(true);
    try {
      await priorities.update(editingPriority.id, editForm);
      toast("Priority updated", "success");
      setEditModal(false);
      fetchAll();
    } catch (err: any) {
      toast(err.response?.data?.message || "Failed to update priority", "error");
    } finally {
      setSaving(false);
    }
  };

  const openWorkflow = (p: Priority) => {
    setSelectedWorkflowPriority(p);
    const detail = priorityDetails[p.id];
    const stats = priorityStatsMap[p.id];
    const breachRate = stats && stats.total_signals > 0
      ? (stats.sla_breach_count / stats.total_signals) * 100
      : 0;

    let state = "NORMAL";
    if (breachRate > 15) state = "ESCALATED";
    else if (breachRate > 10) state = "BREACHED";
    else if (breachRate > 5) state = "WARNING";
    setCurrentWorkflowState(state);

    setWorkflowEntries([
      { stateId: "NORMAL", timestamp: detail?.created_at, note: "Priority configured and active" },
      ...(breachRate > 5 ? [{ stateId: "WARNING" as const, timestamp: undefined, note: "SLA breach rate exceeded 5%" }] : []),
      ...(breachRate > 10 ? [{ stateId: "BREACHED" as const, timestamp: undefined, note: "SLA breach rate exceeded 10%" }] : []),
      ...(breachRate > 15 ? [{ stateId: "ESCALATED" as const, timestamp: undefined, note: "Escalation threshold triggered" }] : []),
    ]);
  };

  const handleWorkflowAction = (actionId: string) => {
    const transition = ESCALATION_WORKFLOW.transitions.find((t) => t.to === actionId);
    if (transition) {
      setCurrentWorkflowState(actionId);
      setWorkflowEntries((prev) => [
        ...prev,
        { stateId: actionId, timestamp: new Date().toISOString(), note: transition.description },
      ]);
      toast(`Workflow: ${transition.description}`, "success");
    }
  };

  const updateEditForm = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const value = e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value;
    setEditForm((f) => ({ ...f, [field]: value }));
  };

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Priority Escalation Workflow</h1>
        <div className="flex gap-2">
          <button onClick={fetchAll} className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
            Refresh
          </button>
        </div>
      </div>

      {/* Priority Matrix Grid */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Priority Matrix</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {priorityList.map((p) => {
            const levelColors = PRIORITY_COLORS[p.priority_level] || PRIORITY_COLORS[1];
            const stats = priorityStatsMap[p.id];
            const breachRate = stats && stats.total_signals > 0
              ? (stats.sla_breach_count / stats.total_signals) * 100
              : 0;

            return (
              <div key={p.id} className={`bg-white rounded-lg border ${levelColors.border} overflow-hidden`}>
                <div className={`${levelColors.bg} px-4 py-3 border-b ${levelColors.border}`}>
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${levelColors.badge}`}>
                      {p.priority_level}
                    </span>
                    <span className={`text-xs font-medium ${levelColors.text}`}>{levelColors.level}</span>
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900 mt-2">{p.name}</h3>
                  {p.code && <span className="font-mono text-xs text-gray-500">{p.code}</span>}
                </div>
                <div className="px-4 py-3 space-y-2">
                  {p.description && (
                    <p className="text-xs text-gray-500 line-clamp-2">{p.description}</p>
                  )}
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-gray-400 block">Response SLA</span>
                      <span className="font-medium text-gray-900">{p.sla_hours}h</span>
                    </div>
                    <div>
                      <span className="text-gray-400 block">Resolution SLA</span>
                      <span className="font-medium text-gray-900">{p.sla_hours}h</span>
                    </div>
                    <div>
                      <span className="text-gray-400 block">Escalation</span>
                      <span className="font-medium text-gray-900">{p.escalation_minutes}min</span>
                    </div>
                  </div>
                  {stats && (
                    <>
                      <div className="border-t border-gray-100 pt-2 grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-gray-400 block">Signals</span>
                          <span className="font-medium">{stats.total_signals}</span>
                        </div>
                        <div>
                          <span className="text-gray-400 block">Resolved</span>
                          <span className="font-medium text-green-600">{stats.resolved_signals}</span>
                        </div>
                        <div>
                          <span className="text-gray-400 block">Avg Resolution</span>
                          <span className="font-medium">{stats.avg_resolution_time_hours?.toFixed(1) || "-"}h</span>
                        </div>
                        <div>
                          <span className="text-gray-400 block">SLA Breaches</span>
                          <span className="font-medium text-red-600">{stats.sla_breach_count}</span>
                        </div>
                      </div>
                      <div className="border-t border-gray-100 pt-2 flex items-center justify-between">
                        <span className="text-xs text-gray-400">Performance</span>
                        <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-full ${getPerformanceTextColor(breachRate)} ${getPerformanceBgColor(breachRate)}`}>
                          <span className={`h-1.5 w-1.5 rounded-full ${getPerformanceColor(breachRate)}`} />
                          {getPerformanceLabel(breachRate)}
                        </span>
                      </div>
                    </>
                  )}
                  <div className="border-t border-gray-100 pt-2 flex gap-2">
                    <button
                      onClick={() => openEditModal(p)}
                      className="flex-1 text-xs text-center py-1.5 border border-gray-300 rounded-md hover:bg-gray-50 text-gray-700 font-medium"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => openWorkflow(p)}
                      className="flex-1 text-xs text-center py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                    >
                      Workflow
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SLA Performance Section */}
      {responseTimes.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">SLA Performance</h2>
          <div className="space-y-4">
            {responseTimes.map((rt) => {
              const levelColors = PRIORITY_COLORS[rt.priority_level] || PRIORITY_COLORS[1];
              const pctOfSla = rt.sla_target_hours > 0
                ? (rt.avg_response_time / rt.sla_target_hours) * 100
                : 0;
              const isBreached = pctOfSla > 100;
              const barColor = isBreached
                ? "bg-red-500"
                : pctOfSla > 80
                ? "bg-yellow-500"
                : "bg-blue-500";

              return (
                <div key={rt.priority_level}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${levelColors.badge}`}>
                        {rt.priority_level}
                      </span>
                      <span className="text-sm font-medium text-gray-900">{rt.priority_name}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-gray-500">
                        Avg: <strong className={isBreached ? "text-red-600" : "text-gray-900"}>{rt.avg_response_time.toFixed(1)}h</strong>
                      </span>
                      <span className="text-gray-400">SLA: {rt.sla_target_hours}h</span>
                      {isBreached && (
                        <span className="text-red-600 font-medium">Breached</span>
                      )}
                    </div>
                  </div>
                  <div className="h-4 bg-gray-100 rounded-full overflow-hidden relative">
                    <div
                      className={`h-full rounded-full transition-all ${barColor}`}
                      style={{ width: `${Math.min(pctOfSla, 100)}%` }}
                    />
                    {pctOfSla > 100 && (
                      <div className="absolute inset-0 flex items-center justify-end pr-1">
                        <span className="text-[10px] font-bold text-white drop-shadow-sm">
                          +{(pctOfSla - 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
                    <span>{rt.total_signals} signals</span>
                    <span>{rt.breached_count} breached</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Escalation Candidates Section */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Escalation Candidates</h2>
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
            {escalationCandidates.length} overdue
          </span>
        </div>
        {escalationCandidates.length === 0 ? (
          <div className="text-center py-12 text-gray-500 text-sm">
            No signals currently require escalation
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="px-6 py-3 font-medium">Reference</th>
                  <th className="px-6 py-3 font-medium">Title</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Priority</th>
                  <th className="px-6 py-3 font-medium">Created</th>
                  <th className="px-6 py-3 font-medium">Hours Elapsed</th>
                  <th className="px-6 py-3 font-medium">Deadline</th>
                  <th className="px-6 py-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {escalationCandidates.map((c) => {
                  const levelColors = PRIORITY_COLORS[c.priority.priority_level] || PRIORITY_COLORS[1];
                  const stateStyles: Record<string, string> = {
                    NORMAL: "text-green-600 bg-green-50",
                    WARNING: "text-yellow-600 bg-yellow-50",
                    BREACHED: "text-red-600 bg-red-50",
                    ESCALATED: "text-purple-600 bg-purple-50",
                  };
                  return (
                    <tr key={c.signal.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="px-6 py-3 font-mono text-xs text-gray-600">
                        {c.signal.reference_number}
                      </td>
                      <td className="px-6 py-3 text-gray-900 max-w-[200px] truncate">
                        {c.signal.title}
                      </td>
                      <td className="px-6 py-3">
                        <span className="text-xs capitalize text-gray-600">{c.signal.status}</span>
                      </td>
                      <td className="px-6 py-3">
                        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${levelColors.badge}`}>
                          {c.priority.priority_level}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-xs text-gray-500">
                        {new Date(c.signal.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-3">
                        <span className={`text-xs font-medium ${
                          c.hoursElapsed >= c.deadline ? "text-red-600" : c.hoursElapsed >= c.deadline * 0.8 ? "text-yellow-600" : "text-gray-600"
                        }`}>
                          {c.hoursElapsed.toFixed(1)}h
                        </span>
                      </td>
                      <td className="px-6 py-3 text-xs text-gray-500">
                        {c.deadline}h
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleEscalateNow(c)}
                            disabled={escalatingIds.has(c.signal.id)}
                            className="text-xs px-3 py-1.5 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 font-medium"
                          >
                            {escalatingIds.has(c.signal.id) ? "..." : "Escalate Now"}
                          </button>
                          <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${stateStyles[c.state]}`}>
                            {c.state}
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* SLA Configuration Visualization */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">SLA Configuration Hierarchy</h2>
        <div className="space-y-0">
          {priorityList.map((p, idx) => {
            const levelColors = PRIORITY_COLORS[p.priority_level] || PRIORITY_COLORS[1];
            const slaHours = p.sla_hours || 24;
            const escMinutes = p.escalation_minutes || 60;
            const warningThreshold = slaHours * 0.8;
            const breachThreshold = slaHours;

            return (
              <div key={p.id}>
                <div className={`flex items-stretch ${idx < priorityList.length - 1 ? "border-b border-gray-100" : ""}`}>
                  <div className={`w-16 flex items-center justify-center ${levelColors.bg} py-4`}>
                    <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${levelColors.badge}`}>
                      {p.priority_level}
                    </span>
                  </div>
                  <div className="flex-1 px-4 py-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-semibold text-gray-900">{p.name}</span>
                      {p.auto_escalate && (
                        <span className="text-[10px] font-medium text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded-full">Auto</span>
                      )}
                    </div>
                    <div className="relative h-6 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="absolute inset-y-0 left-0 bg-green-400 rounded-full"
                        style={{ width: `${(warningThreshold / breachThreshold) * 100}%` }}
                      />
                      <div
                        className="absolute inset-y-0 bg-yellow-400"
                        style={{
                          left: `${(warningThreshold / breachThreshold) * 100}%`,
                          width: `${((breachThreshold - warningThreshold) / breachThreshold) * 100}%`,
                        }}
                      />
                      <div
                        className="absolute inset-y-0 right-0 bg-red-400 rounded-r-full"
                        style={{
                          left: `${(breachThreshold / breachThreshold) * 100}%`,
                          width: "0%",
                        }}
                      />
                      <div
                        className="absolute inset-y-0 bg-gradient-to-r from-green-400 via-yellow-400 to-red-400"
                        style={{
                          width: `${(escMinutes / 60 / breachThreshold) * 100}%`,
                          opacity: 0.3,
                        }}
                      />
                      <div className="absolute inset-0 flex items-center justify-between px-2 text-[10px] text-white font-medium drop-shadow-sm">
                        <span>0h</span>
                        <span className="text-gray-700">{warningThreshold.toFixed(0)}h (Warning)</span>
                        <span>{breachThreshold}h (Breach)</span>
                      </div>
                    </div>
                    <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                      <span>Normal</span>
                      <span>Escalation: {escMinutes}min</span>
                      <span>Overdue</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Workflow Modal */}
      <Modal
        open={!!selectedWorkflowPriority}
        onClose={() => setSelectedWorkflowPriority(null)}
        title={selectedWorkflowPriority ? `Workflow: ${selectedWorkflowPriority.name}` : ""}
        size="xl"
      >
        {selectedWorkflowPriority && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <WorkflowTimeline
              workflow={ESCALATION_WORKFLOW}
              entries={workflowEntries}
              currentState={currentWorkflowState}
            />
            <WorkflowActionPanel
              workflow={ESCALATION_WORKFLOW}
              currentState={currentWorkflowState}
              userRole="admin"
              onAction={handleWorkflowAction}
            />
          </div>
        )}
      </Modal>

      {/* Edit Priority Modal */}
      <Modal open={editModal} onClose={() => setEditModal(false)} title="Edit Priority" size="lg">
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input type="text" value={editForm.name} onChange={updateEditForm("name")} required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code *</label>
              <input type="text" value={editForm.code} onChange={updateEditForm("code")} required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea value={editForm.description} onChange={updateEditForm("description")} rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority Level</label>
              <input type="number" min={1} max={5} value={editForm.priority_level} onChange={updateEditForm("priority_level")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Severity Level</label>
              <input type="number" min={1} max={5} value={editForm.severity_level} onChange={updateEditForm("severity_level")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
              <input type="color" value={editForm.color} onChange={updateEditForm("color")}
                className="w-full h-9 border border-gray-300 rounded-lg cursor-pointer" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SLA (hours)</label>
              <input type="number" min={1} value={editForm.sla_hours} onChange={updateEditForm("sla_hours")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Escalation (min)</label>
              <input type="number" min={0} value={editForm.escalation_minutes} onChange={updateEditForm("escalation_minutes")}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex gap-6">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={editForm.auto_escalate} onChange={updateEditForm("auto_escalate")} className="rounded border-gray-300" />
              <span className="text-sm text-gray-700">Auto-escalate</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={editForm.requires_approval} onChange={updateEditForm("requires_approval")} className="rounded border-gray-300" />
              <span className="text-sm text-gray-700">Requires approval</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={editForm.is_active} onChange={updateEditForm("is_active")} className="rounded border-gray-300" />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setEditModal(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
            <button type="submit" disabled={saving} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
              {saving ? "Saving..." : "Update"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
