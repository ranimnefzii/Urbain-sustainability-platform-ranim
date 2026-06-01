import { useState, useCallback, useMemo } from "react";

export interface WorkflowSideEffect {
  type: "notification" | "analytics" | "ai_classification" | "ai_assessment" | "assignment" | "escalation" | "feedback";
  label: string;
  status: "idle" | "running" | "done" | "failed";
  detail?: string;
}

export interface WorkflowStep {
  id: string;
  label: string;
  description: string;
  status: "pending" | "current" | "done" | "skipped" | "blocked";
  required: boolean;
  sideEffects: WorkflowSideEffect[];
}

export interface WorkflowState {
  id: string;
  entityType: "signal" | "user" | "sector";
  entityId: number;
  steps: WorkflowStep[];
  currentStepIndex: number;
  isComplete: boolean;
  progressPercent: number;
}

type ActionHandler = (stepId: string) => Promise<void>;

export function useWorkflow(
  initialState: WorkflowState,
  onExecuteStep: ActionHandler
) {
  const [state, setState] = useState(initialState);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentStep = useMemo(
    () => state.steps[state.currentStepIndex] ?? null,
    [state.steps, state.currentStepIndex]
  );

  const canAdvance = useMemo(() => {
    if (!currentStep) return false;
    if (executing) return false;
    if (currentStep.status === "done") return true;
    if (currentStep.status === "skipped") return true;
    return false;
  }, [currentStep, executing]);

  const advance = useCallback(() => {
    if (!canAdvance) return;
    setState((prev) => {
      const nextIndex = prev.currentStepIndex + 1;
      if (nextIndex >= prev.steps.length) {
        return { ...prev, currentStepIndex: prev.steps.length, isComplete: true };
      }
      const updated = prev.steps.map((s, i) => {
        if (i === prev.currentStepIndex) return { ...s, status: "done" as const };
        if (i === nextIndex) return { ...s, status: "current" as const };
        return s;
      });
      return { ...prev, steps: updated, currentStepIndex: nextIndex };
    });
  }, [canAdvance]);

  const executeCurrent = useCallback(async () => {
    if (!currentStep || executing) return;
    setExecuting(true);
    setError(null);
    setState((prev) => ({
      ...prev,
      steps: prev.steps.map((s) =>
        s.id === currentStep.id ? { ...s, status: "current" as const } : s
      ),
    }));
    try {
      await onExecuteStep(currentStep.id);
      setState((prev) => ({
        ...prev,
        steps: prev.steps.map((s) =>
          s.id === currentStep.id
            ? {
                ...s,
                status: "done" as const,
                sideEffects: s.sideEffects.map((e) => ({ ...e, status: "done" as const })),
              }
            : s
        ),
      }));
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || "Step failed";
      setError(msg);
      setState((prev) => ({
        ...prev,
        steps: prev.steps.map((s) =>
          s.id === currentStep.id ? { ...s, status: "blocked" as const } : s
        ),
      }));
    } finally {
      setExecuting(false);
    }
  }, [currentStep, executing, onExecuteStep]);

  const updateSideEffect = useCallback(
    (stepId: string, effectIndex: number, status: WorkflowSideEffect["status"], detail?: string) => {
      setState((prev) => ({
        ...prev,
        steps: prev.steps.map((s) =>
          s.id === stepId
            ? {
                ...s,
                sideEffects: s.sideEffects.map((e, i) =>
                  i === effectIndex ? { ...e, status, detail: detail || e.detail } : e
                ),
              }
            : s
        ),
      }));
    },
    []
  );

  const reset = useCallback(
    (newState?: WorkflowState) => {
      setState(newState || initialState);
      setExecuting(false);
      setError(null);
    },
    [initialState]
  );

  return {
    state,
    currentStep,
    executing,
    error,
    canAdvance,
    advance,
    executeCurrent,
    updateSideEffect,
    reset,
    setState,
  };
}

export function buildSignalWorkflow(signal: {
  id: number;
  status: string;
  citizen_satisfaction?: number | null;
  ai_confidence_score?: number | null;
  assigned_at?: string | null;
  resolved_at?: string | null;
}): WorkflowState {
  const isDone = (s: string) => {
    const order = ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"];
    const current = order.indexOf(signal.status);
    const step = order.indexOf(s);
    return step < current || (step === current);
  };

  const steps: WorkflowStep[] = [
    {
      id: "submitted",
      label: "Signal Submitted",
      description: "Signal has been reported and is awaiting review",
      status: isDone("SUBMITTED") ? "done" : signal.status === "SUBMITTED" ? "current" : "pending",
      required: true,
      sideEffects: [
        { type: "ai_classification", label: "AI Classification", status: signal.ai_confidence_score ? "done" : "idle", detail: signal.ai_confidence_score ? `${(signal.ai_confidence_score * 100).toFixed(0)}% confidence` : undefined },
        { type: "notification", label: "Confirmation notification", status: signal.status !== "DRAFT" ? "done" : "idle" },
        { type: "analytics", label: "Analytics updated", status: "done" },
      ],
    },
    {
      id: "under_review",
      label: "Under Review",
      description: "Signal is being reviewed by the team",
      status: isDone("UNDER_REVIEW") ? "done" : signal.status === "UNDER_REVIEW" ? "current" : isDone("SUBMITTED") ? "pending" : "skipped",
      required: true,
      sideEffects: [
        { type: "notification", label: "Reviewer notified", status: isDone("UNDER_REVIEW") ? "done" : "idle" },
      ],
    },
    {
      id: "assigned",
      label: "Assigned",
      description: "Signal assigned to a team member or sector",
      status: isDone("ASSIGNED") ? "done" : signal.status === "ASSIGNED" ? "current" : isDone("UNDER_REVIEW") ? "pending" : "skipped",
      required: true,
      sideEffects: [
        { type: "assignment", label: "Team assigned", status: signal.assigned_at ? "done" : "idle" },
        { type: "notification", label: "Assignee notified", status: signal.assigned_at ? "done" : "idle" },
      ],
    },
    {
      id: "in_progress",
      label: "In Progress",
      description: "Work is actively being done on this signal",
      status: isDone("IN_PROGRESS") ? "done" : signal.status === "IN_PROGRESS" ? "current" : isDone("ASSIGNED") ? "pending" : "skipped",
      required: true,
      sideEffects: [
        { type: "notification", label: "Citizen notified of progress", status: isDone("IN_PROGRESS") ? "done" : "idle" },
      ],
    },
    {
      id: "resolved",
      label: "Resolved",
      description: "The issue has been resolved",
      status: isDone("RESOLVED") ? "done" : signal.status === "RESOLVED" ? "current" : isDone("IN_PROGRESS") ? "pending" : "skipped",
      required: true,
      sideEffects: [
        { type: "notification", label: "Resolution notification sent", status: isDone("RESOLVED") ? "done" : "idle" },
        { type: "analytics", label: "Resolution metrics updated", status: isDone("RESOLVED") ? "done" : "idle" },
      ],
    },
    {
      id: "feedback",
      label: "Citizen Feedback",
      description: "Citizen provides satisfaction rating",
      status: signal.citizen_satisfaction ? "done" : signal.status === "RESOLVED" || signal.status === "CLOSED" ? "current" : "pending",
      required: false,
      sideEffects: [
        { type: "feedback", label: "Satisfaction recorded", status: signal.citizen_satisfaction ? "done" : "idle", detail: signal.citizen_satisfaction ? `${signal.citizen_satisfaction}/5` : undefined },
        { type: "analytics", label: "Satisfaction metrics updated", status: signal.citizen_satisfaction ? "done" : "idle" },
      ],
    },
    {
      id: "closed",
      label: "Closed",
      description: "Signal lifecycle complete",
      status: signal.status === "CLOSED" ? "current" : isDone("CLOSED") ? "done" : "pending",
      required: true,
      sideEffects: [],
    },
  ];

  const currentIdx = steps.findIndex((s) => s.status === "current");
  const doneCount = steps.filter((s) => s.status === "done").length;
  const total = steps.length;

  return {
    id: `signal-workflow-${signal.id}`,
    entityType: "signal",
    entityId: signal.id,
    steps,
    currentStepIndex: currentIdx >= 0 ? currentIdx : doneCount,
    isComplete: signal.status === "CLOSED",
    progressPercent: Math.round((doneCount / total) * 100),
  };
}
