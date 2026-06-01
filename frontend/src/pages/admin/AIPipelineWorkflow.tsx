import { useState, useEffect } from "react";
import { signals, ai } from "../../api/endpoints";
import { useToast } from "../../contexts/ToastContext";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import type { Signal } from "../../types";

interface PipelineStep {
  id: string;
  label: string;
  description: string;
  icon: string;
  color: string;
  requiresSignal: boolean;
  apiCall: (s: Signal) => Promise<any>;
  resultKey: string;
}

const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: "classify",
    label: "Classify",
    description: "Categorize signal by type",
    icon: "🏷️",
    color: "blue",
    requiresSignal: true,
    apiCall: (s) => ai.classify({ text: s.description || "", location: { latitude: s.latitude, longitude: s.longitude }, images: s.images || [] }),
    resultKey: "classification",
  },
  {
    id: "assess-priority",
    label: "Assess Priority",
    description: "Evaluate urgency & impact",
    icon: "⚡",
    color: "orange",
    requiresSignal: true,
    apiCall: (s) => ai.assessPriority({ description: s.description || "", latitude: s.latitude, longitude: s.longitude }),
    resultKey: "priority",
  },
  {
    id: "detect-anomalies",
    label: "Detect Anomalies",
    description: "Flag unusual patterns",
    icon: "🔍",
    color: "red",
    requiresSignal: true,
    apiCall: (s) => ai.detectAnomalies({ description: s.description || "", latitude: s.latitude, longitude: s.longitude }),
    resultKey: "anomalies",
  },
  {
    id: "analyze-severity",
    label: "Severity Analysis",
    description: "Combined severity assessment",
    icon: "📊",
    color: "purple",
    requiresSignal: true,
    apiCall: (s) => ai.analyzeSeverity({ text: s.description || "", location: { latitude: s.latitude, longitude: s.longitude } }),
    resultKey: "severity",
  },
  {
    id: "generate-report",
    label: "Generate Report",
    description: "Full AI report",
    icon: "📄",
    color: "green",
    requiresSignal: false,
    apiCall: (s) => ai.generateReport(s.id),
    resultKey: "report",
  },
];

export default function AIPipelineWorkflow() {
  const { toast } = useToast();
  const [signalId, setSignalId] = useState("");
  const [signal, setSignal] = useState<Signal | null>(null);
  const [runningStep, setRunningStep] = useState<string | null>(null);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [results, setResults] = useState<Record<string, any>>({});
  const id = Number(signalId);

  useEffect(() => {
    if (!id) { setSignal(null); return; }
    signals.get(id).then((res) => setSignal(res.data.data ?? null)).catch(() => setSignal(null));
  }, [id]);

  const persistResult = async (stepKey: string, resultData: any) => {
    try {
      const updateData: Record<string, any> = {};
      if (stepKey === "classification" && resultData?.predicted_category) {
        updateData.ai_confidence_score = resultData.confidence_score;
      } else if (stepKey === "priority" && resultData?.priority_score) {
        updateData.ai_priority_score = resultData.priority_score;
      } else if (stepKey === "severity" && resultData?.summary) {
        updateData.ai_severity_score = resultData.summary.confidence;
        updateData.ai_urgency_score = resultData.summary.urgency_score;
        updateData.safety_risk_level = resultData.summary.priority_level;
      }
      if (Object.keys(updateData).length > 0) {
        await signals.update(id, updateData);
      }
    } catch {
      // non-critical — pipeline result still shown even if persist fails
    }
  };

  const runStep = async (step: PipelineStep) => {
    if (!id) { toast("Enter a signal ID", "error"); return; }
    if (step.requiresSignal && !signal) { toast("Signal not found or loading", "error"); return; }
    setRunningStep(step.id);
    try {
      const res = await step.apiCall(signal!);
      const resultData = res.data.data;
      setResults((prev) => ({ ...prev, [step.resultKey]: resultData }));
      setCompletedSteps((prev) => new Set(prev).add(step.id));
      await persistResult(step.resultKey, resultData);
      toast(`${step.label} completed`, "success");
    } catch {
      toast(`${step.label} failed`, "error");
    } finally {
      setRunningStep(null);
    }
  };

  const runAll = async () => {
    if (!id) { toast("Enter a signal ID", "error"); return; }
    if (!signal) { toast("Signal not found", "error"); return; }
    for (const step of PIPELINE_STEPS) {
      if (step.requiresSignal && !signal) { toast("Signal data unavailable for " + step.label, "error"); return; }
      setRunningStep(step.id);
      try {
        const res = await step.apiCall(signal);
        const resultData = res.data.data;
        setResults((prev) => ({ ...prev, [step.resultKey]: resultData }));
        setCompletedSteps((prev) => new Set(prev).add(step.id));
        await persistResult(step.resultKey, resultData);
      } catch {
        toast(`${step.label} failed – pipeline paused`, "error");
        setRunningStep(null);
        return;
      }
    }
    setRunningStep(null);
    toast("Full AI pipeline completed", "success");
  };

  const colorClasses: Record<string, string> = {
    blue: "border-blue-200 bg-blue-50 text-blue-700",
    orange: "border-orange-200 bg-orange-50 text-orange-700",
    red: "border-red-200 bg-red-50 text-red-700",
    purple: "border-purple-200 bg-purple-50 text-purple-700",
    green: "border-green-200 bg-green-50 text-green-700",
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">AI Pipeline Workflow</h2>
        <p className="text-sm text-gray-500 mb-4">
          Run the full AI analysis pipeline on a signal: classify &rarr; assess priority &rarr; detect anomalies &rarr; analyze severity &rarr; generate report.
        </p>
        <div className="flex items-end gap-4">
          <div className="flex-1">
            <label className="block text-xs font-medium text-gray-700 mb-1">Signal ID</label>
            <input
              type="number"
              value={signalId}
              onChange={(e) => setSignalId(e.target.value)}
              placeholder="Enter signal ID..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <button
            onClick={runAll}
            disabled={!signalId || runningStep !== null}
            className="px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {runningStep ? "Running..." : "Run Full Pipeline"}
          </button>
        </div>
      </div>

      <div className="relative">
        {PIPELINE_STEPS.map((step, idx) => {
          const isCompleted = completedSteps.has(step.id);
          const isRunning = runningStep === step.id;
          const isPending = !isCompleted && !isRunning;
          const isLast = idx === PIPELINE_STEPS.length - 1;

          return (
            <div key={step.id} className="flex gap-4">
              <div className="flex flex-col items-center">
                <button
                  onClick={() => runStep(step)}
                  disabled={!signalId || runningStep !== null}
                  className={`h-10 w-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 transition-all border-2
                    ${isCompleted ? "bg-green-500 border-green-500 text-white" : ""}
                    ${isRunning ? "bg-blue-500 border-blue-500 text-white animate-pulse" : ""}
                    ${isPending ? "bg-white border-gray-300 text-gray-400 hover:border-gray-400" : ""}
                  `}
                >
                  {isCompleted ? "✓" : isRunning ? <LoadingSpinner size="sm" /> : step.icon}
                </button>
                {!isLast && <div className={`w-0.5 h-8 ${isCompleted ? "bg-green-400" : "bg-gray-200"}`} />}
              </div>
              <div className={`pb-6 flex-1 ${isPending ? "opacity-50" : ""}`}>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-semibold ${isCompleted ? "text-green-700" : isRunning ? "text-blue-700" : "text-gray-500"}`}>
                    {step.label}
                  </span>
                  {isRunning && <span className="text-[10px] font-medium text-blue-600 bg-blue-100 px-1.5 py-0.5 rounded-full">Running...</span>}
                </div>
                <p className="text-xs text-gray-500">{step.description}</p>
                {isCompleted && results[step.resultKey] && (
                  <div className={`mt-2 p-3 rounded-lg text-xs border ${colorClasses[step.color] || "border-gray-200 bg-gray-50"}`}>
                    {step.id === "classify" && (
                      <p>Category: <strong>{(results.classification as any)?.predicted_category || "N/A"}</strong> ({(results.classification as any)?.confidence_score ? `${((results.classification as any).confidence_score * 100).toFixed(1)}%` : "N/A"})</p>
                    )}
                    {step.id === "assess-priority" && (
                      <p>Priority: <strong>{(results.priority as any)?.priority_level || "N/A"}</strong> (Score: {(results.priority as any)?.priority_score ? ((results.priority as any).priority_score * 100).toFixed(1) : "N/A"})</p>
                    )}
                    {step.id === "detect-anomalies" && (
                      <p>Anomalies: {(results.anomalies as any)?.anomalies_detected ? <strong className="text-red-600">Detected ({(results.anomalies as any).anomaly_count})</strong> : <strong className="text-green-600">None</strong>}</p>
                    )}
                    {step.id === "severity" && (
                      <div className="space-y-0.5">
                        <p>Category: <strong>{(results.severity as any)?.summary?.category || "N/A"}</strong></p>
                        <p>Priority: <strong>{(results.severity as any)?.summary?.priority_level || "N/A"}</strong></p>
                        <p>Anomalies: {(results.severity as any)?.summary?.anomalies_detected ? "Yes" : "No"}</p>
                      </div>
                    )}
                    {step.id === "report" && (
                      <div className="space-y-0.5">
                        <p>Report: <strong>{(results.report as any)?.report_code || "N/A"}</strong></p>
                        <p>Status: {(results.report as any)?.status || "N/A"}</p>
                        <p>Findings: {(results.report as any)?.key_findings?.length || 0} items</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {Object.keys(results).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Pipeline Summary</h3>
          <div className="grid grid-cols-5 gap-3 text-center">
            <div className={`p-3 rounded-lg ${completedSteps.has("classify") ? "bg-green-50" : "bg-gray-50"}`}>
              <p className="text-lg mb-1">🏷️</p>
              <p className="text-xs font-medium">{completedSteps.has("classify") ? "Classified" : "Pending"}</p>
            </div>
            <div className={`p-3 rounded-lg ${completedSteps.has("assess-priority") ? "bg-green-50" : "bg-gray-50"}`}>
              <p className="text-lg mb-1">⚡</p>
              <p className="text-xs font-medium">{completedSteps.has("assess-priority") ? "Assessed" : "Pending"}</p>
            </div>
            <div className={`p-3 rounded-lg ${completedSteps.has("detect-anomalies") ? "bg-green-50" : "bg-gray-50"}`}>
              <p className="text-lg mb-1">🔍</p>
              <p className="text-xs font-medium">{completedSteps.has("detect-anomalies") ? "Scanned" : "Pending"}</p>
            </div>
            <div className={`p-3 rounded-lg ${completedSteps.has("analyze-severity") ? "bg-green-50" : "bg-gray-50"}`}>
              <p className="text-lg mb-1">📊</p>
              <p className="text-xs font-medium">{completedSteps.has("analyze-severity") ? "Analyzed" : "Pending"}</p>
            </div>
            <div className={`p-3 rounded-lg ${completedSteps.has("generate-report") ? "bg-green-50" : "bg-gray-50"}`}>
              <p className="text-lg mb-1">📄</p>
              <p className="text-xs font-medium">{completedSteps.has("generate-report") ? "Reported" : "Pending"}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
