import { useMemo } from "react";
import { useWorkflow, buildSignalWorkflow } from "../../hooks/useWorkflow";
import type { Signal } from "../../types";

interface SignalWorkflowProps {
  signal: Signal;
  onRefetch: () => void;
  onAction: (action: string, data?: any) => void;
  actionLoading: boolean;
  canTransitions: boolean;
  canFeedback: boolean;
  transitions: string[];
}

const SIDE_EFFECT_ICONS: Record<string, string> = {
  notification: "🔔",
  analytics: "📊",
  ai_classification: "🤖",
  ai_assessment: "📋",
  assignment: "👤",
  escalation: "⚠️",
  feedback: "⭐",
};

const STATUS_TRANSITIONS: Record<string, string[]> = {
  DRAFT: ["SUBMITTED", "CANCELLED"],
  SUBMITTED: ["UNDER_REVIEW", "CANCELLED"],
  UNDER_REVIEW: ["IN_PROGRESS", "ASSIGNED", "CANCELLED", "REJECTED"],
  ASSIGNED: ["IN_PROGRESS", "CANCELLED"],
  IN_PROGRESS: ["RESOLVED", "CANCELLED"],
  RESOLVED: ["CLOSED"],
  REJECTED: ["SUBMITTED"],
};

export default function SignalWorkflow({
  signal,
  onRefetch,
  onAction,
  actionLoading,
  canTransitions,
  canFeedback,
  transitions,
}: SignalWorkflowProps) {
  const workflowState = useMemo(() => buildSignalWorkflow(signal), [signal]);
  const { state, executeCurrent, executing, error } = useWorkflow(
    workflowState,
    async (stepId) => {
      const stepTransitions: Record<string, string> = {
        submitted: "SUBMITTED",
        under_review: "UNDER_REVIEW",
        assigned: "ASSIGNED",
        in_progress: "IN_PROGRESS",
        resolved: "RESOLVED",
        closed: "CLOSED",
      };
      const targetStatus = stepTransitions[stepId];
      if (targetStatus && transitions.includes(targetStatus)) {
        await onAction(targetStatus);
        onRefetch();
      }
    }
  );

  const availableTransitions = STATUS_TRANSITIONS[signal.status] || [];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Signal Lifecycle</h3>
        <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
          {state.progressPercent}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-gray-100 rounded-full mb-5 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-400 via-green-400 to-green-500 rounded-full transition-all duration-700"
          style={{ width: `${state.progressPercent}%` }}
        />
      </div>

      {/* Steps */}
      <div className="space-y-2">
        {state.steps.map((step, idx) => {
          const isCurrent = step.status === "current";
          const isDone = step.status === "done";
          const isBlocked = step.status === "blocked";
          const isSkipped = step.status === "skipped";

          return (
            <div key={step.id}>
              <div
                className={`relative flex items-start gap-3 p-3 rounded-lg transition-colors ${
                  isCurrent
                    ? "bg-blue-50 border border-blue-200"
                    : isDone
                    ? "bg-green-50 border border-green-100"
                    : isBlocked
                    ? "bg-red-50 border border-red-200"
                    : "bg-gray-50 border border-gray-100"
                }`}
              >
                {/* Step indicator */}
                <div
                  className={`mt-0.5 h-5 w-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    isDone
                      ? "bg-green-500 text-white"
                      : isCurrent
                      ? "bg-blue-600 text-white"
                      : isBlocked
                      ? "bg-red-500 text-white"
                      : "bg-gray-300 text-gray-500"
                  }`}
                >
                  {isDone ? "✓" : isBlocked ? "!" : idx + 1}
                </div>

                {/* Step content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm font-medium ${
                        isDone
                          ? "text-green-800"
                          : isCurrent
                          ? "text-blue-800"
                          : isBlocked
                          ? "text-red-800"
                          : "text-gray-500"
                      }`}
                    >
                      {step.label}
                    </span>
                    {!step.required && (
                      <span className="text-[10px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">optional</span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{step.description}</p>

                  {/* Side effects */}
                  {step.sideEffects.filter((e) => e.status !== "idle").length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {step.sideEffects
                        .filter((e) => e.status !== "idle")
                        .map((effect, ei) => (
                          <span
                            key={ei}
                            className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full ${
                              effect.status === "done"
                                ? "bg-green-100 text-green-700"
                                : effect.status === "running"
                                ? "bg-blue-100 text-blue-700"
                                : effect.status === "failed"
                                ? "bg-red-100 text-red-700"
                                : "bg-gray-100 text-gray-500"
                            }`}
                          >
                            <span>{SIDE_EFFECT_ICONS[effect.type] || "•"}</span>
                            <span>{effect.label}</span>
                            {effect.detail && (
                              <span className="opacity-70">({effect.detail})</span>
                            )}
                          </span>
                        ))}
                    </div>
                  )}

                  {/* Step action button */}
                  {isCurrent && !isDone && canTransitions && (
                    <div className="mt-3 flex gap-2">
                      {availableTransitions.includes("IN_PROGRESS") && (
                        <button
                          onClick={() => onAction("IN_PROGRESS")}
                          disabled={actionLoading}
                          className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                          {actionLoading ? "..." : "Start Processing"}
                        </button>
                      )}
                      {availableTransitions.includes("ASSIGNED") && (
                        <button
                          onClick={() => onAction("ASSIGNED")}
                          disabled={actionLoading}
                          className="px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                        >
                          {actionLoading ? "..." : "Assign to Me"}
                        </button>
                      )}
                      {availableTransitions.includes("RESOLVED") && (
                        <button
                          onClick={() => onAction("RESOLVED")}
                          disabled={actionLoading}
                          className="px-3 py-1.5 text-xs bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                        >
                          Resolve
                        </button>
                      )}
                      {availableTransitions.includes("SUBMITTED") && (
                        <button
                          onClick={() => onAction("SUBMITTED")}
                          disabled={actionLoading}
                          className="px-3 py-1.5 text-xs bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
                        >
                          Reactivate
                        </button>
                      )}
                      {availableTransitions.includes("CANCELLED") && (
                        <button
                          onClick={() => onAction("CANCELLED")}
                          disabled={actionLoading}
                          className="px-3 py-1.5 text-xs border border-red-300 text-red-600 rounded-lg hover:bg-red-50 disabled:opacity-50"
                        >
                          Cancel Signal
                        </button>
                      )}
                      {availableTransitions.includes("REJECTED") && (
                        <button
                          onClick={() => onAction("REJECTED")}
                          disabled={actionLoading}
                          className="px-3 py-1.5 text-xs bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                        >
                          Reject
                        </button>
                      )}
                    </div>
                  )}

                  {/* Feedback button */}
                  {isCurrent && step.id === "feedback" && canFeedback && (
                    <div className="mt-3">
                      <button
                        onClick={() => onAction("FEEDBACK")}
                        className="px-3 py-1.5 text-xs bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                      >
                        Submit Feedback
                      </button>
                    </div>
                  )}

                  {/* Execute step button (for auto transitions) */}
                  {isCurrent && !isDone && canTransitions && availableTransitions.length === 0 && !step.required && (
                    <div className="mt-3">
                      <button
                        onClick={executeCurrent}
                        disabled={executing}
                        className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {executing ? "..." : "Mark Complete"}
                      </button>
                    </div>
                  )}
                </div>

                {/* Status badge */}
                {isDone && (
                  <span className="text-[10px] font-medium text-green-600 bg-green-100 px-1.5 py-0.5 rounded flex-shrink-0">
                    Done
                  </span>
                )}
                {isSkipped && (
                  <span className="text-[10px] font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded flex-shrink-0">
                    Skipped
                  </span>
                )}
              </div>

              {/* Connector line */}
              {idx < state.steps.length - 1 && (
                <div className="ml-2.5 pl-7">
                  <div
                    className={`w-0.5 h-3 ${
                      isDone ? "bg-green-400" : "bg-gray-200"
                    }`}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {error && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
          {error}
        </div>
      )}
    </div>
  );
}
