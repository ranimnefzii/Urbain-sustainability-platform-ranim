import { useState, useEffect, useCallback, useRef } from "react";
import { signals, ai } from "../../api/endpoints";
import { useToast } from "../../contexts/ToastContext";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import type {
  Signal, AIClassification, AIPriorityAssessment, AIAnomalyDetection,
  AISeverityAnalysis, AIReport, AIModelInfo, AITrendPrediction
} from "../../types";

type PipelineStage = "classify" | "priority" | "anomalies" | "severity" | "report";
type StageStatus = "idle" | "running" | "done" | "error";

interface StageResult {
  classification?: AIClassification;
  priority?: AIPriorityAssessment;
  anomalies?: AIAnomalyDetection;
  severity?: AISeverityAnalysis;
  report?: AIReport;
}

const STAGES: { key: PipelineStage; label: string; desc: string; emoji: string }[] = [
  { key: "classify", label: "Classification", desc: "Catégorisation automatique", emoji: "🏷️" },
  { key: "priority", label: "Priorisation", desc: "Score d'urgence & impact", emoji: "⚡" },
  { key: "anomalies", label: "Anomalies", desc: "Détection de patterns inhabituels", emoji: "🔍" },
  { key: "severity", label: "Sévérité", desc: "Analyse combinée complète", emoji: "📊" },
  { key: "report", label: "Rapport", desc: "Génération du rapport IA", emoji: "📄" },
];

const STATUS_COLORS: Record<string, string> = {
  idle: "border-surface-200 bg-surface-50 text-surface-400",
  running: "border-brand-400 bg-brand-50 text-brand-600 animate-pulse",
  done: "border-emerald-400 bg-emerald-50 text-emerald-600",
  error: "border-red-300 bg-red-50 text-red-600",
};

const STATUS_ICONS: Record<string, string> = { idle: "○", running: "◎", done: "●", error: "✕" };

function CircularScore({ value, size = 64, stroke = 6, label }: { value: number; size?: number; stroke?: number; label: string }) {
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - value * circumference;
  const color = value >= 0.8 ? "#10b981" : value >= 0.6 ? "#f59e0b" : value >= 0.4 ? "#f97316" : "#ef4444";
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e5e7eb" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          className="transition-all duration-1000 ease-out" />
      </svg>
      <span className="absolute text-sm font-bold" style={{ lineHeight: `${size}px`, marginTop: 0 }}>{(value * 100).toFixed(0)}%</span>
      <span className="text-[10px] text-surface-500 font-medium mt-1">{label}</span>
    </div>
  );
}

function AnomalyBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    low: "bg-amber-50 text-amber-700 border-amber-200",
    medium: "bg-orange-50 text-orange-700 border-orange-200",
    high: "bg-red-50 text-red-700 border-red-200",
    critical: "bg-rose-50 text-rose-700 border-rose-200",
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border ${colors[severity] || colors.low}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${severity === "low" ? "bg-amber-400" : severity === "medium" ? "bg-orange-400" : "bg-red-400"}`} />
      {severity}
    </span>
  );
}

export default function AIPipeline() {
  const { toast } = useToast();

  const [signalId, setSignalId] = useState<number | null>(null);
  const [signalInput, setSignalInput] = useState("");
  const [signal, setSignal] = useState<Signal | null>(null);
  const [signalLoading, setSignalLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Signal[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const [modelInfo, setModelInfo] = useState<AIModelInfo | null>(null);
  const [statuses, setStatuses] = useState<Record<PipelineStage, StageStatus>>(
    { classify: "idle", priority: "idle", anomalies: "idle", severity: "idle", report: "idle" }
  );
  const [results, setResults] = useState<StageResult>({});
  const [running, setRunning] = useState<PipelineStage | null>(null);
  const [activeTab, setActiveTab] = useState<PipelineStage | "all">("all");

  const [trends, setTrends] = useState<AITrendPrediction | null>(null);
  const [trendDays, setTrendDays] = useState(30);
  const [trendLoading, setTrendLoading] = useState(false);

  const [batchInput, setBatchInput] = useState("");
  const [batchResults, setBatchResults] = useState<any[] | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);

  const [history, setHistory] = useState<{ signalId: number; title: string; time: string; results: StageResult }[]>([]);

  // --- Load model info on mount ---
  useEffect(() => {
    ai.modelInfo().then(r => setModelInfo(r.data.data ?? null)).catch(() => {});
  }, []);

  // --- Click outside search ---
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) setSearchOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // --- Search signals ---
  const handleSearch = useCallback(async (q: string) => {
    setSignalInput(q);
    if (q.length < 2) { setSearchResults([]); setSearchOpen(false); return; }
    try {
      const r = await signals.search(q);
      const items = r.data.data?.items || [];
      setSearchResults(items);
      setSearchOpen(items.length > 0);
      if (items.length === 0) toast("Aucun signalement trouvé pour cette recherche", "info");
    } catch {
      setSearchResults([]);
      setSearchOpen(false);
    }
  }, [toast]);

  const selectSignal = useCallback(async (id: number) => {
    setSignalId(id);
    setSignalInput("");
    setSearchOpen(false);
    setSignalLoading(true);
    setStatuses({ classify: "idle", priority: "idle", anomalies: "idle", severity: "idle", report: "idle" });
    setResults({});
    try {
      const r = await signals.get(id);
      setSignal(r.data.data ?? null);
    } catch { toast("Signal introuvable", "error"); setSignal(null); }
    finally { setSignalLoading(false); }
  }, [toast]);

  // --- Run single stage ---
  const runStage = useCallback(async (stage: PipelineStage) => {
    if (!signal || signalLoading) return;
    setRunning(stage);
    setStatuses(prev => ({ ...prev, [stage]: "running" }));
    try {
      let res: any;
      switch (stage) {
        case "classify":
          res = await ai.classify({ text: signal.description || "", location: { latitude: signal.latitude, longitude: signal.longitude }, images: signal.images || [] });
          setResults(prev => ({ ...prev, classification: res.data.data }));
          break;
        case "priority":
          res = await ai.assessPriority({ description: signal.description || "", latitude: signal.latitude, longitude: signal.longitude, safety_risk_level: signal.safety_risk_level || undefined, affected_people_count: signal.affected_people_count || undefined, affected_area_sqm: signal.affected_area_sqm || undefined });
          setResults(prev => ({ ...prev, priority: res.data.data }));
          break;
        case "anomalies":
          res = await ai.detectAnomalies({ description: signal.description || "", latitude: signal.latitude, longitude: signal.longitude, category: signal.category?.code });
          setResults(prev => ({ ...prev, anomalies: res.data.data }));
          break;
        case "severity":
          res = await ai.analyzeSeverity({ text: signal.description || "", location: { latitude: signal.latitude, longitude: signal.longitude } });
          setResults(prev => ({ ...prev, severity: res.data.data }));
          break;
        case "report":
          res = await ai.generateReport(signal.id);
          setResults(prev => ({ ...prev, report: res.data.data }));
          break;
      }
      setStatuses(prev => ({ ...prev, [stage]: "done" }));
      toast(`${STAGES.find(s => s.key === stage)?.label} terminé`, "success");
    } catch {
      setStatuses(prev => ({ ...prev, [stage]: "error" }));
      toast(`${STAGES.find(s => s.key === stage)?.label} échoué`, "error");
    } finally {
      setRunning(null);
    }
  }, [signal, signalLoading, toast]);

  // --- Run all stages sequentially ---
  const runAll = useCallback(async () => {
    if (!signal || signalLoading) return;
    setResults({});
    setStatuses({ classify: "idle", priority: "idle", anomalies: "idle", severity: "idle", report: "idle" });
    for (const st of STAGES) {
      setRunning(st.key);
      setStatuses(prev => ({ ...prev, [st.key]: "running" }));
      try {
        let res: any;
        switch (st.key) {
          case "classify":
            res = await ai.classify({ text: signal.description || "", location: { latitude: signal.latitude, longitude: signal.longitude }, images: signal.images || [] });
            setResults(prev => ({ ...prev, classification: res.data.data }));
            break;
          case "priority":
            res = await ai.assessPriority({ description: signal.description || "", latitude: signal.latitude, longitude: signal.longitude, safety_risk_level: signal.safety_risk_level || undefined, affected_people_count: signal.affected_people_count || undefined, affected_area_sqm: signal.affected_area_sqm || undefined });
            setResults(prev => ({ ...prev, priority: res.data.data }));
            break;
          case "anomalies":
            res = await ai.detectAnomalies({ description: signal.description || "", latitude: signal.latitude, longitude: signal.longitude, category: signal.category?.code });
            setResults(prev => ({ ...prev, anomalies: res.data.data }));
            break;
          case "severity":
            res = await ai.analyzeSeverity({ text: signal.description || "", location: { latitude: signal.latitude, longitude: signal.longitude } });
            setResults(prev => ({ ...prev, severity: res.data.data }));
            break;
          case "report":
            res = await ai.generateReport(signal.id);
            setResults(prev => ({ ...prev, report: res.data.data }));
            break;
        }
        setStatuses(prev => ({ ...prev, [st.key]: "done" }));
      } catch {
        setStatuses(prev => ({ ...prev, [st.key]: "error" }));
        toast(`${st.label} échoué — pipeline interrompu`, "error");
        setRunning(null);
        return;
      }
    }
    setRunning(null);
    setHistory(prev => [{ signalId: signal.id, title: signal.title, time: new Date().toLocaleString("fr-FR"), results: results }, ...prev].slice(0, 10));
    toast("Pipeline IA terminé avec succès", "success");
  }, [signal, signalLoading, results, toast]);

  // --- Predict trends ---
  const handlePredictTrends = useCallback(async () => {
    setTrendLoading(true);
    try {
      const r = await ai.predictTrends({ days: trendDays });
      setTrends(r.data.data ?? null);
    } catch { toast("Prévision échouée", "error"); }
    finally { setTrendLoading(false); }
  }, [trendDays, toast]);

  // --- Batch classify ---
  const handleBatchClassify = useCallback(async () => {
    if (!batchInput.trim()) return;
    setBatchLoading(true);
    setBatchResults(null);
    try {
      const lines = batchInput.split("\n").filter(Boolean);
      const r = await ai.batchClassify(lines.map(text => ({ description: text })));
      setBatchResults(r.data.data?.results || []);
      toast(`${lines.length} signalements classifiés`, "success");
    } catch { toast("Classification par lot échouée", "error"); }
    finally { setBatchLoading(false); }
  }, [batchInput, toast]);

  // --- Persist AI scores to signal ---
  const persistToSignal = useCallback(async () => {
    if (!signal || !results.classification && !results.priority) return;
    try {
      const update: Record<string, any> = {};
      if (results.classification?.confidence_score) update.ai_confidence_score = results.classification.confidence_score;
      if (results.priority?.priority_score) update.ai_priority_score = results.priority.priority_score;
      if (results.severity?.summary?.confidence) update.ai_severity_score = results.severity.summary.confidence;
      if (Object.keys(update).length > 0) {
        await signals.update(signal.id, update);
        toast("Scores IA enregistrés sur le signalement", "success");
      }
    } catch { toast("Échec de la sauvegarde", "error"); }
  }, [signal, results, toast]);

  const completedCount = Object.values(statuses).filter(s => s === "done" || s === "error").length;
  const allDone = Object.values(statuses).every(s => s === "done" || s === "idle");
  const hasResults = Object.keys(results).length > 0;

  return (
    <div className="space-y-6">
      {/* ========== HEADER ========== */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-surface-900 via-surface-800 to-brand-900 p-6 lg:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-lg shadow-lg shadow-brand-500/30">
                🤖
              </div>
              <div>
                <h1 className="text-xl lg:text-2xl font-bold text-white">Pipeline IA</h1>
                <p className="text-sm text-surface-400">Analyse intelligente des signalements urbains</p>
              </div>
            </div>
            {modelInfo && (
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${modelInfo.status === "loaded" ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}>
                  {modelInfo.status === "loaded" ? "● Modèle actif" : "○ Mode simulation"}
                </span>
                <span className="text-[10px] text-surface-500 bg-surface-800 px-2 py-0.5 rounded-full">{modelInfo.version}</span>
                <span className="text-[10px] text-surface-500 bg-surface-800 px-2 py-0.5 rounded-full">{modelInfo.framework}</span>
                {modelInfo.performance_metrics && (
                  <span className="text-[10px] text-surface-500 bg-surface-800 px-2 py-0.5 rounded-full">
                    ⚡ {modelInfo.performance_metrics.avg_processing_time_ms}ms | {modelInfo.performance_metrics.throughput_per_second}/s
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button onClick={handlePredictTrends} disabled={trendLoading}
              className="px-4 py-2 text-xs font-medium rounded-xl bg-white/10 text-white hover:bg-white/20 disabled:opacity-50 transition-all border border-white/10">
              {trendLoading ? "..." : "📈 Prévisions"}
            </button>
            <button onClick={() => { setResults({}); setStatuses({ classify: "idle", priority: "idle", anomalies: "idle", severity: "idle", report: "idle" }); }}
              className="px-4 py-2 text-xs font-medium rounded-xl bg-white/10 text-white hover:bg-white/20 transition-all border border-white/10">
              🗑️ Réinitialiser
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ========== LEFT PANEL — SIGNAL SELECTOR + PIPELINE ========== */}
        <div className="lg:col-span-1 space-y-4">
          {/* Signal selector */}
          <div className="bg-white rounded-xl border border-surface-200 p-4 shadow-sm">
            <h2 className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-3">Signalement cible</h2>

            {/* Direct ID input */}
            <div className="flex gap-2 mb-2">
              <input type="number" min={1} value={signalId ?? ""} onChange={e => {
                const val = e.target.value ? Number(e.target.value) : null;
                setSignalId(val);
                if (val) selectSignal(val);
                else { setSignal(null); setResults({}); setStatuses({ classify: "idle", priority: "idle", anomalies: "idle", severity: "idle", report: "idle" }); }
              }} placeholder="Entrer un ID directement..."
                className="flex-1 border border-surface-200 rounded-lg px-3 py-2.5 text-sm bg-surface-50 focus:bg-white focus:ring-2 focus:ring-brand-500/30 outline-none transition-all" />
              <button onClick={() => { if (signalId) selectSignal(signalId); }}
                className="px-3 py-2.5 text-xs font-medium rounded-lg bg-brand-600 text-white hover:bg-brand-700 transition-all">
                Charger
              </button>
            </div>

            {/* Search by text */}
            <div className="relative" ref={searchRef}>
              <div className="relative">
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input value={signalInput} onChange={e => handleSearch(e.target.value)}
                  placeholder="Rechercher par mot-clé..."
                  className="w-full border border-surface-200 rounded-lg pl-9 pr-3 py-2.5 text-sm bg-surface-50 focus:bg-white focus:ring-2 focus:ring-brand-500/30 outline-none transition-all" />
              </div>
              {searchOpen && searchResults.length > 0 && (
                <div className="absolute z-50 top-full mt-1 left-0 right-0 bg-white border border-surface-200 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                  {searchResults.map(s => (
                    <button key={s.id} onClick={() => selectSignal(s.id)}
                      className="w-full text-left px-3 py-2.5 hover:bg-brand-50 border-b border-surface-100 last:border-0 transition-colors">
                      <p className="text-sm font-medium text-surface-800">#{s.id} — {s.title}</p>
                      <p className="text-[10px] text-surface-400">{s.reference_number} · {s.status?.replace(/_/g, " ")}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {signalLoading && <div className="mt-3"><LoadingSpinner size="sm" /></div>}
            {signal && !signalLoading && (
              <div className="mt-3 p-3 rounded-lg bg-gradient-to-r from-brand-50 to-purple-50 border border-brand-200">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-semibold text-surface-800">{signal.title}</p>
                    <p className="text-[10px] text-surface-500 font-mono mt-0.5">{signal.reference_number}</p>
                  </div>
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${signal.status === "resolved" ? "bg-emerald-100 text-emerald-700" : signal.status === "in_progress" ? "bg-blue-100 text-blue-700" : "bg-amber-100 text-amber-700"}`}>
                    {signal.status?.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="text-xs text-surface-500 mt-2 line-clamp-2">{signal.description}</p>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-surface-400">
                  <span>📍 {signal.latitude.toFixed(4)}, {signal.longitude.toFixed(4)}</span>
                  {signal.category && <span>📂 {signal.category.name}</span>}
                </div>
              </div>
            )}
            {!signal && !signalLoading && (
              <div className="mt-3 p-4 rounded-lg bg-surface-50 border border-dashed border-surface-200 text-center">
                <p className="text-xs text-surface-400">Entrez un ID ou recherchez un signalement pour lancer l'analyse IA</p>
              </div>
            )}
          </div>

          {/* Pipeline stages */}
          <div className="bg-white rounded-xl border border-surface-200 p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-semibold text-surface-500 uppercase tracking-wider">Pipeline</h2>
              <span className="text-[10px] text-surface-400">{completedCount}/5 étapes</span>
            </div>
            <div className="space-y-1">
              {STAGES.map((st, idx) => {
                const sts = statuses[st.key];
                const isRunning = running === st.key;
                const isPast = sts === "done" || sts === "error";
                return (
                  <button key={st.key} onClick={() => runStage(st.key)}
                    disabled={!signal || running !== null || sts === "running"}
                    className={`w-full flex items-center gap-3 p-2.5 rounded-lg text-left transition-all border
                      ${isRunning ? "border-brand-300 bg-brand-50/50 shadow-sm" :
                        sts === "done" ? "border-emerald-200 bg-emerald-50/50" :
                        sts === "error" ? "border-red-200 bg-red-50/50" :
                        "border-transparent hover:bg-surface-50 hover:border-surface-200"}
                      ${!signal ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 flex-shrink-0 transition-all
                      ${isRunning ? "border-brand-500 bg-brand-500 text-white" :
                        sts === "done" ? "border-emerald-500 bg-emerald-500 text-white" :
                        sts === "error" ? "border-red-400 bg-red-50 text-red-500" :
                        "border-surface-300 bg-white text-surface-500"}`}>
                      {isRunning ? <LoadingSpinner size="sm" /> : sts === "done" ? "✓" : sts === "error" ? "!" : idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${isRunning ? "text-brand-700" : sts === "done" ? "text-emerald-700" : sts === "error" ? "text-red-700" : "text-surface-700"}`}>
                        {st.label}
                      </p>
                      <p className="text-[10px] text-surface-400">{st.desc}</p>
                    </div>
                    {sts !== "idle" && (
                      <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full
                        ${sts === "done" ? "bg-emerald-100 text-emerald-600" :
                          sts === "error" ? "bg-red-100 text-red-600" :
                          "bg-brand-100 text-brand-600"}`}>
                        {sts === "done" ? "Terminé" : sts === "error" ? "Erreur" : "En cours"}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
            {signal && (
              <div className="mt-3 flex gap-2">
                <button onClick={runAll} disabled={running !== null}
                  className="flex-1 px-3 py-2 text-xs font-semibold rounded-lg bg-gradient-to-r from-brand-600 to-purple-600 text-white hover:from-brand-700 hover:to-purple-700 disabled:opacity-50 transition-all shadow-sm">
                  {running !== null ? "Exécution en cours..." : "▶ Lancer tout le pipeline"}
                </button>
                {hasResults && (
                  <button onClick={persistToSignal}
                    className="px-3 py-2 text-xs font-medium rounded-lg border border-surface-200 text-surface-600 hover:bg-surface-50 transition-all">
                    💾 Sauvegarder
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Recent history */}
          {history.length > 0 && (
            <div className="bg-white rounded-xl border border-surface-200 p-4 shadow-sm">
              <h2 className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-3">Analyses récentes</h2>
              <div className="space-y-1.5">
                {history.map((h, i) => (
                  <button key={i} onClick={() => { selectSignal(h.signalId); }}
                    className="w-full flex items-center gap-2 p-2 rounded-lg hover:bg-surface-50 transition-colors text-left">
                    <div className="w-6 h-6 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center text-[10px] font-bold">#</div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-surface-700 truncate">{h.title}</p>
                      <p className="text-[9px] text-surface-400">{h.time}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ========== RIGHT PANEL — RESULTS ========== */}
        <div className="lg:col-span-2 space-y-4">
          {!hasResults && !trends && (
            <div className="bg-white rounded-xl border border-surface-200 p-8 shadow-sm flex flex-col items-center justify-center min-h-[400px]">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-100 to-purple-100 flex items-center justify-center text-3xl mb-4 shadow-inner">
                🤖
              </div>
              <h2 className="text-lg font-semibold text-surface-700 mb-1">Pipeline IA prêt</h2>
              <p className="text-sm text-surface-400 text-center max-w-md">
                Sélectionnez un signalement dans le panneau de gauche, puis lancez les étapes du pipeline
                pour analyser, classifier et générer des rapports intelligents.
              </p>
              <div className="flex flex-wrap gap-2 mt-4">
                {["Classification", "Priorisation", "Anomalies", "Sévérité", "Rapport"].map(f => (
                  <span key={f} className="text-[10px] bg-surface-100 text-surface-500 px-2 py-1 rounded-full">{f}</span>
                ))}
              </div>
            </div>
          )}

          {/* Results tabs */}
          {hasResults && (
            <div className="bg-white rounded-xl border border-surface-200 shadow-sm overflow-hidden">
              <div className="flex border-b border-surface-200 overflow-x-auto">
                {STAGES.map(st => {
                  const sts = statuses[st.key];
                  return (
                    <button key={st.key} onClick={() => setActiveTab(st.key)}
                      className={`flex items-center gap-2 px-4 py-3 text-xs font-medium border-b-2 transition-all whitespace-nowrap
                        ${activeTab === st.key ? "border-brand-500 text-brand-700 bg-brand-50/50" :
                          sts === "done" ? "border-transparent text-emerald-600 hover:text-surface-700" :
                          sts === "error" ? "border-transparent text-red-500 hover:text-surface-700" :
                          "border-transparent text-surface-400 hover:text-surface-600"}`}>
                      <span>{st.emoji}</span>
                      <span>{st.label}</span>
                      {sts === "done" && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
                      {sts === "error" && <span className="w-1.5 h-1.5 rounded-full bg-red-500" />}
                    </button>
                  );
                })}
              </div>

              <div className="p-5">
                {results.classification && (activeTab === "classify" || activeTab === "all") && (
                  <div className={activeTab !== "classify" ? "hidden" : ""}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-lg">🏷️</div>
                      <div>
                        <h3 className="text-sm font-semibold text-surface-800">Classification</h3>
                        <p className="text-[10px] text-surface-400">Modèle : {results.classification.model_version} · {results.classification.processing_time_ms}ms</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="p-4 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 text-center">
                        <p className="text-xs text-surface-500 mb-1">Catégorie prédite</p>
                        <p className="text-lg font-bold text-blue-700 capitalize">{results.classification.predicted_category}</p>
                      </div>
                      <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 text-center">
                        <p className="text-xs text-surface-500 mb-1">Confiance</p>
                        <p className="text-lg font-bold text-emerald-700">{(results.classification.confidence_score * 100).toFixed(1)}%</p>
                      </div>
                      <div className="p-4 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 text-center">
                        <p className="text-xs text-surface-500 mb-1">Méthode</p>
                        <p className="text-sm font-bold text-purple-700 capitalize">{results.classification.classification_method?.replace(/_/g, " ")}</p>
                      </div>
                    </div>
                    {results.classification.all_scores && (
                      <div>
                        <p className="text-xs font-medium text-surface-500 mb-2">Scores par catégorie</p>
                        <div className="space-y-1.5">
                          {Object.entries(results.classification.all_scores).sort(([,a], [,b]) => b - a).map(([cat, score]) => (
                            <div key={cat} className="flex items-center gap-2">
                              <span className="text-xs text-surface-600 w-24 capitalize truncate">{cat}</span>
                              <div className="flex-1 h-2 bg-surface-100 rounded-full overflow-hidden">
                                <div className="h-full rounded-full transition-all duration-500"
                                  style={{ width: `${score * 100}%`, background: score > 0.6 ? "#10b981" : score > 0.3 ? "#f59e0b" : "#ef4444" }} />
                              </div>
                              <span className="text-[10px] text-surface-400 w-10 text-right">{(score * 100).toFixed(0)}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {results.priority && (activeTab === "priority" || activeTab === "all") && (
                  <div className={activeTab !== "priority" ? "hidden" : ""}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center text-lg">⚡</div>
                      <div>
                        <h3 className="text-sm font-semibold text-surface-800">Évaluation de priorité</h3>
                        <p className="text-[10px] text-surface-400">Confiance : {(results.priority.confidence * 100).toFixed(0)}% · {results.priority.processing_time_ms}ms</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                      <CircularScore value={results.priority.priority_score} size={72} label="Priorité" />
                      <CircularScore value={results.priority.severity_score} size={72} label="Sévérité" />
                      <CircularScore value={results.priority.urgency_score} size={72} label="Urgence" />
                      <CircularScore value={results.priority.impact_score} size={72} label="Impact" />
                    </div>
                    <div className="p-4 rounded-xl bg-gradient-to-br from-surface-50 to-amber-50 border border-surface-200">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs font-medium text-surface-600">Niveau de priorité</p>
                        <span className={`text-xs font-bold px-3 py-1 rounded-full ${results.priority.priority_level === "critical" ? "bg-red-100 text-red-700" : results.priority.priority_level === "high" ? "bg-orange-100 text-orange-700" : results.priority.priority_level === "medium" ? "bg-amber-100 text-amber-700" : results.priority.priority_level === "low" ? "bg-blue-100 text-blue-700" : "bg-surface-100 text-surface-600"}`}>
                          {results.priority.priority_level?.toUpperCase()}
                        </span>
                      </div>
                      {results.priority.recommendation && (
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-3">
                          <div className="bg-white rounded-lg p-2.5 border border-surface-200">
                            <p className="text-[9px] text-surface-400 uppercase">Action</p>
                            <p className="text-xs font-medium text-surface-700">{results.priority.recommendation.action}</p>
                          </div>
                          <div className="bg-white rounded-lg p-2.5 border border-surface-200">
                            <p className="text-[9px] text-surface-400 uppercase">Délai</p>
                            <p className="text-xs font-medium text-surface-700">{results.priority.recommendation.response_time}</p>
                          </div>
                          <div className="bg-white rounded-lg p-2.5 border border-surface-200">
                            <p className="text-[9px] text-surface-400 uppercase">Ressources</p>
                            <p className="text-xs font-medium text-surface-700">{results.priority.recommendation.resources}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {results.anomalies && (activeTab === "anomalies" || activeTab === "all") && (
                  <div className={activeTab !== "anomalies" ? "hidden" : ""}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center text-lg">🔍</div>
                      <div>
                        <h3 className="text-sm font-semibold text-surface-800">Détection d'anomalies</h3>
                        <p className="text-[10px] text-surface-400">Score d'anomalie : {(results.anomalies.anomaly_score * 100).toFixed(0)}% · {results.anomalies.processing_time_ms}ms</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium ${results.anomalies.anomalies_detected ? "bg-red-50 text-red-700 border border-red-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200"}`}>
                        <span className="text-lg">{results.anomalies.anomalies_detected ? "⚠️" : "✅"}</span>
                        {results.anomalies.anomalies_detected
                          ? `${results.anomalies.anomaly_count} anomalie(s) détectée(s)`
                          : "Aucune anomalie détectée"}
                      </div>
                      <span className={`text-[10px] font-medium px-2 py-1 rounded-full ${results.anomalies.risk_level === "high" ? "bg-red-100 text-red-700" : results.anomalies.risk_level === "medium" ? "bg-orange-100 text-orange-700" : "bg-emerald-100 text-emerald-700"}`}>
                        Risque : {results.anomalies.risk_level}
                      </span>
                    </div>
                    {results.anomalies.anomalies?.length > 0 && (
                      <div className="space-y-2">
                        {results.anomalies.anomalies.map((a, i) => (
                          <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-surface-50 border border-surface-200">
                            <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${a.severity === "high" || a.severity === "critical" ? "bg-red-500" : a.severity === "medium" ? "bg-orange-400" : "bg-amber-400"}`} />
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <p className="text-xs font-medium text-surface-700 capitalize">{a.type?.replace(/_/g, " ")}</p>
                                <AnomalyBadge severity={a.severity} />
                              </div>
                              <p className="text-[11px] text-surface-500 mt-0.5">{a.detail}</p>
                            </div>
                            <span className="text-[10px] text-surface-400">{(a.score * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {results.severity && (activeTab === "severity" || activeTab === "all") && (
                  <div className={activeTab !== "severity" ? "hidden" : ""}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center text-lg">📊</div>
                      <div>
                        <h3 className="text-sm font-semibold text-surface-800">Analyse de sévérité</h3>
                        <p className="text-[10px] text-surface-400">Analyse combinée classification + priorité + anomalies</p>
                      </div>
                    </div>
                    {results.severity.summary && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 text-center">
                          <p className="text-[10px] text-surface-500">Catégorie</p>
                          <p className="text-sm font-bold text-blue-700 capitalize">{results.severity.summary.category || "N/A"}</p>
                        </div>
                        <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 text-center">
                          <p className="text-[10px] text-surface-500">Confiance</p>
                          <p className="text-lg font-bold text-emerald-700">{(results.severity.summary.confidence * 100).toFixed(0)}%</p>
                        </div>
                        <div className="p-3 rounded-xl bg-gradient-to-br from-orange-50 to-amber-50 border border-orange-200 text-center">
                          <p className="text-[10px] text-surface-500">Priorité</p>
                          <p className="text-sm font-bold text-orange-700 capitalize">{results.severity.summary.priority_level}</p>
                        </div>
                        <div className="p-3 rounded-xl bg-gradient-to-br from-red-50 to-rose-50 border border-red-200 text-center">
                          <p className="text-[10px] text-surface-500">Anomalies</p>
                          <p className="text-sm font-bold text-red-700">{results.severity.summary.anomalies_detected ? "Détectées" : "Aucune"}</p>
                        </div>
                      </div>
                    )}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {results.severity.classification && (
                        <div className="p-3 rounded-lg bg-surface-50 border border-surface-200">
                          <p className="text-[10px] font-semibold text-surface-500 uppercase mb-2">Classification</p>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-surface-700 capitalize">{results.severity.classification.predicted_category}</span>
                            <span className="text-xs text-emerald-600 font-medium">{(results.severity.classification.confidence_score * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      )}
                      {results.severity.priority_assessment && (
                        <div className="p-3 rounded-lg bg-surface-50 border border-surface-200">
                          <p className="text-[10px] font-semibold text-surface-500 uppercase mb-2">Priorité</p>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-surface-700 capitalize">{results.severity.priority_assessment.priority_level}</span>
                            <span className="text-xs text-orange-600 font-medium">{(results.severity.priority_assessment.priority_score * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      )}
                      {results.severity.anomalies && (
                        <div className="md:col-span-2 p-3 rounded-lg bg-surface-50 border border-surface-200">
                          <p className="text-[10px] font-semibold text-surface-500 uppercase mb-2">Anomalies</p>
                          <p className="text-xs text-surface-600">
                            {results.severity.anomalies.anomalies_detected
                              ? `${results.severity.anomalies.anomaly_count} anomalie(s) — score: ${(results.severity.anomalies.anomaly_score * 100).toFixed(0)}%`
                              : "Aucune anomalie détectée"}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {results.report && (activeTab === "report" || activeTab === "all") && (
                  <div className={activeTab !== "report" ? "hidden" : ""}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-lg">📄</div>
                      <div>
                        <h3 className="text-sm font-semibold text-surface-800">Rapport IA</h3>
                        <p className="text-[10px] text-surface-400">{results.report.report_code} · {results.report.processing_time_ms}ms · {new Date(results.report.generated_at).toLocaleString("fr-FR")}</p>
                      </div>
                    </div>
                    <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 mb-4">
                      <p className="text-xs text-surface-600 leading-relaxed">{results.report.summary}</p>
                    </div>
                    {results.report.key_findings?.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs font-semibold text-surface-600 mb-2">🔑 Résultats clés</p>
                        <ul className="space-y-1">
                          {results.report.key_findings.map((f, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-surface-600">
                              <span className="text-emerald-500 mt-0.5">•</span>
                              {f}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {results.report.recommendations?.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs font-semibold text-surface-600 mb-2">💡 Recommandations</p>
                        <ul className="space-y-1">
                          {results.report.recommendations.map((r, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-surface-600">
                              <span className="text-brand-500 mt-0.5">→</span>
                              {r}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {results.report.ai_confidence_score != null && (
                      <div className="flex items-center gap-2 text-xs text-surface-500">
                        <span>Score de confiance global :</span>
                        <span className="font-bold text-surface-700">{(results.report.ai_confidence_score * 100).toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Trends section */}
          <div className="bg-white rounded-xl border border-surface-200 shadow-sm">
            <div className="flex items-center justify-between p-4 border-b border-surface-200">
              <h2 className="text-sm font-semibold text-surface-800">📈 Prévisions de tendances</h2>
              <div className="flex items-center gap-2">
                <select value={trendDays} onChange={e => setTrendDays(Number(e.target.value))}
                  className="border border-surface-200 rounded-lg px-2 py-1.5 text-xs outline-none focus:ring-2 focus:ring-brand-500/30">
                  <option value={7}>7 jours</option>
                  <option value={14}>14 jours</option>
                  <option value={30}>30 jours</option>
                  <option value={60}>60 jours</option>
                  <option value={90}>90 jours</option>
                </select>
                <button onClick={handlePredictTrends} disabled={trendLoading}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-50 transition-all">
                  {trendLoading ? "..." : "Prévoir"}
                </button>
              </div>
            </div>
            {trends ? (
              <div className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  <div className="p-3 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 text-center">
                    <p className="text-2xl font-bold text-blue-700">{trends.predicted_total_signals}</p>
                    <p className="text-[10px] text-blue-500">Signalements prévus</p>
                  </div>
                  <div className={`p-3 rounded-lg border text-center ${trends.trend_direction === "increasing" ? "bg-red-50 border-red-200" : trends.trend_direction === "decreasing" ? "bg-emerald-50 border-emerald-200" : "bg-amber-50 border-amber-200"}`}>
                    <p className={`text-lg font-bold capitalize ${trends.trend_direction === "increasing" ? "text-red-700" : trends.trend_direction === "decreasing" ? "text-emerald-700" : "text-amber-700"}`}>
                      {trends.trend_direction}
                    </p>
                    <p className="text-[10px] text-surface-500">Tendance</p>
                  </div>
                  <div className="p-3 rounded-lg bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 text-center">
                    <p className="text-2xl font-bold text-purple-700">{(trends.confidence_level * 100).toFixed(0)}%</p>
                    <p className="text-[10px] text-purple-500">Confiance</p>
                  </div>
                  <div className="p-3 rounded-lg bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 text-center">
                    <p className="text-2xl font-bold text-amber-700">{trends.trend_strength.toFixed(1)}%</p>
                    <p className="text-[10px] text-amber-500">Force tendance</p>
                  </div>
                </div>
                {trends.weekly_breakdown && Object.keys(trends.weekly_breakdown).length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-surface-500 mb-2">Répartition hebdomadaire</p>
                    <div className="space-y-1.5">
                      {Object.entries(trends.weekly_breakdown).map(([week, count]) => {
                        const maxVal = Math.max(...Object.values(trends.weekly_breakdown), 1);
                        return (
                          <div key={week}>
                            <div className="flex justify-between text-xs text-surface-600 mb-0.5">
                              <span className="capitalize">{week.replace(/_/g, " ")}</span>
                              <span className="font-medium">{count as number}</span>
                            </div>
                            <div className="h-2.5 bg-surface-100 rounded-full overflow-hidden">
                              <div className="h-full rounded-full bg-gradient-to-r from-brand-400 to-purple-500 transition-all duration-500"
                                style={{ width: `${((count as number) / maxVal) * 100}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                {trends.daily_predictions && trends.daily_predictions.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs font-medium text-surface-500 mb-2">Prévisions quotidiennes (14 jours)</p>
                    <div className="flex items-end gap-1 h-32">
                      {trends.daily_predictions.slice(0, 14).map((day, i) => {
                        const maxD = Math.max(...trends.daily_predictions.slice(0, 14).map(d => d.predicted_signals), 1);
                        return (
                          <div key={i} className="flex-1 flex flex-col items-center group relative">
                            <div className="w-full rounded-t-md transition-all duration-300 group-hover:opacity-80"
                              style={{ height: `${(day.predicted_signals / maxD) * 100}%`, background: day.confidence > 0.85 ? "#10b981" : day.confidence > 0.7 ? "#3b82f6" : "#f59e0b" }}>
                              <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-surface-800 text-white text-[9px] px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                                {day.predicted_signals} signaux ({day.date})
                              </div>
                            </div>
                            <span className="text-[8px] text-surface-400 mt-0.5">{day.date.slice(5)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                {trends.factors && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {Object.entries(trends.factors).filter(([, v]) => v).map(([key]) => (
                      <span key={key} className="text-[10px] bg-green-50 text-green-700 px-2 py-0.5 rounded-full capitalize">{key.replace(/_/g, " ")}</span>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center">
                <p className="text-sm text-surface-400">Cliquez sur "Prévoir" pour générer les prévisions de tendances</p>
              </div>
            )}
          </div>

          {/* Batch classifier */}
          <div className="bg-white rounded-xl border border-surface-200 shadow-sm">
            <div className="p-4 border-b border-surface-200">
              <h2 className="text-sm font-semibold text-surface-800">📦 Classification par lot</h2>
              <p className="text-xs text-surface-400 mt-0.5">Analysez jusqu'à 100 signalements en une seule opération</p>
            </div>
            <div className="p-4">
              <textarea value={batchInput} onChange={e => setBatchInput(e.target.value)} rows={4}
                placeholder="Saisissez une description par ligne :&#10;Nid de poule Avenue Habib Bourguiba&#10;Lampadaire défectueux Place de la République&#10;Dépôt sauvage d'ordures Cité Ennasr"
                className="w-full border border-surface-200 rounded-lg px-3 py-2.5 text-sm bg-surface-50 focus:bg-white focus:ring-2 focus:ring-brand-500/30 outline-none resize-none transition-all" />
              <div className="flex items-center justify-between mt-3">
                <span className="text-[10px] text-surface-400">{batchInput.split("\n").filter(Boolean).length || 0} signalement(s)</span>
                <button onClick={handleBatchClassify} disabled={batchLoading || !batchInput.trim()}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-gradient-to-r from-brand-600 to-purple-600 text-white hover:from-brand-700 hover:to-purple-700 disabled:opacity-50 transition-all shadow-sm">
                  {batchLoading ? "Classification en cours..." : "Classifier le lot"}
                </button>
              </div>
              {batchResults && batchResults.length > 0 && (
                <div className="mt-4 max-h-64 overflow-y-auto space-y-1.5 border-t border-surface-200 pt-4">
                  {batchResults.map((res, i) => (
                    <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-surface-50 border border-surface-200">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${res.status === "success" ? "bg-emerald-100 text-emerald-600" : "bg-red-100 text-red-600"}`}>
                        {res.status === "success" ? "✓" : "!"}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-surface-700 capitalize">
                          {res.classification?.predicted_category || res.predicted_category || res.category || "Inconnu"}
                        </p>
                        <p className="text-[9px] text-surface-400">#{i + 1} · Confiance : {((res.classification?.confidence_score || res.confidence_score || 0) * 100).toFixed(0)}%</p>
                      </div>
                      <div className="flex items-center gap-1">
                        {res.priority_assessment && (
                          <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded ${res.priority_assessment.priority_level === "critical" ? "bg-red-100 text-red-600" : res.priority_assessment.priority_level === "high" ? "bg-orange-100 text-orange-600" : "bg-blue-100 text-blue-600"}`}>
                            {res.priority_assessment.priority_level}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
