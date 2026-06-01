import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signals, priorities } from "../../api/endpoints";
import type { Signal, Priority } from "../../types";

interface EscalationWarning {
  signal: Signal;
  priority: Priority | null;
  hoursSinceCreation: number;
  hoursUntilSla: number;
  isBreached: boolean;
}

export default function EscalationDashboard() {
  const navigate = useNavigate();
  const [warnings, setWarnings] = useState<EscalationWarning[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [sigRes, priRes] = await Promise.all([
          signals.list({ status: "UNDER_REVIEW,ASSIGNED,IN_PROGRESS,SUBMITTED", size: 200 }),
          priorities.list(),
        ]);
        const sigs: Signal[] = sigRes.data.data?.items ?? [];
        const priList: Priority[] = priRes.data.data ?? [];

        const now = Date.now();
        const result: EscalationWarning[] = sigs
          .map((s) => {
            const pri = priList.find((p) => p.id === s.priority_id) || null;
            const hoursSinceCreation = (now - new Date(s.created_at).getTime()) / 3600000;
            const slaHours = pri?.sla_hours || 72;
            const hoursUntilSla = slaHours - hoursSinceCreation;
            return {
              signal: s,
              priority: pri,
              hoursSinceCreation,
              hoursUntilSla,
              isBreached: hoursUntilSla <= 0,
            };
          })
          .filter((w) => w.hoursUntilSla < 24 || w.isBreached)
          .sort((a, b) => a.hoursUntilSla - b.hoursUntilSla)
          .slice(0, 20);

        setWarnings(result);
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">SLA Monitoring</h3>
        <div className="animate-pulse space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-10 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (warnings.length === 0) return null;

  const breachedCount = warnings.filter((w) => w.isBreached).length;
  const atRiskCount = warnings.length - breachedCount;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-900">SLA Monitoring</h3>
          {breachedCount > 0 && (
            <span className="text-xs font-bold bg-red-100 text-red-700 px-1.5 py-0.5 rounded">
              {breachedCount} breached
            </span>
          )}
          {atRiskCount > 0 && (
            <span className="text-xs font-bold bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">
              {atRiskCount} at risk
            </span>
          )}
        </div>
      </div>

      <div className="space-y-2">
        {warnings.map((w) => (
          <div
            key={w.signal.id}
            onClick={() => navigate(`/signals/${w.signal.id}`)}
            className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer text-sm border transition-colors ${
              w.isBreached
                ? "bg-red-50 border-red-200 hover:bg-red-100"
                : w.hoursUntilSla < 4
                ? "bg-orange-50 border-orange-200 hover:bg-orange-100"
                : "bg-yellow-50 border-yellow-200 hover:bg-yellow-100"
            }`}
          >
            <div className={`h-2 w-2 rounded-full flex-shrink-0 ${
              w.isBreached ? "bg-red-500" : w.hoursUntilSla < 4 ? "bg-orange-500" : "bg-yellow-500"
            }`} />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate">{w.signal.title}</p>
              <p className="text-[10px] text-gray-500">
                {w.signal.reference_number} &middot; {w.signal.status.replace(/_/g, " ")}
                {w.priority && <span> &middot; {w.priority.name}</span>}
              </p>
            </div>
            <div className="text-right flex-shrink-0">
              <p className={`text-xs font-bold ${
                w.isBreached ? "text-red-600" : w.hoursUntilSla < 4 ? "text-orange-600" : "text-yellow-600"
              }`}>
                {w.isBreached ? "OVERDUE" : `${Math.round(w.hoursUntilSla)}h left`}
              </p>
              <p className="text-[10px] text-gray-400">
                {w.hoursSinceCreation.toFixed(0)}h elapsed
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
