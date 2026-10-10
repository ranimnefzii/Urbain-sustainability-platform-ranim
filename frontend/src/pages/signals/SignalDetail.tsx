import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useSignal } from "../../hooks/useSignals";
import { signals, ai } from "../../api/endpoints";
import StatusBadge from "../../components/ui/StatusBadge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Modal from "../../components/ui/Modal";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";
import SignalWorkflowPanel from "./SignalWorkflowPanel";
import type { AIClassification, AIPriorityAssessment, AIAnomalyDetection, AISeverityAnalysis, AIReport } from "../../types";

const SOURCE_STYLES: Record<string, string> = { MOBILE: "bg-blue-100 text-blue-800", WEB: "bg-purple-100 text-purple-800", API: "bg-surface-100 text-surface-800", EMAIL: "bg-green-100 text-green-800", ADMIN: "bg-yellow-100 text-yellow-800" };
const VERIFICATION_STYLES: Record<string, string> = { VERIFIED: "bg-green-100 text-green-800", UNVERIFIED: "bg-yellow-100 text-yellow-800", PENDING: "bg-surface-100 text-surface-800", REJECTED: "bg-red-100 text-red-800" };

export default function SignalDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const { signal, loading, error, refetch } = useSignal(Number(id));
  const [actionLoading, setActionLoading] = useState(false);
  const [aiClassifying, setAiClassifying] = useState(false);
  const [aiClassification, setAiClassification] = useState<AIClassification | null>(null);
  const [aiAssessing, setAiAssessing] = useState(false);
  const [aiPriority, setAiPriority] = useState<AIPriorityAssessment | null>(null);
  const [aiDetecting, setAiDetecting] = useState(false);
  const [aiAnomalies, setAiAnomalies] = useState<AIAnomalyDetection | null>(null);
  const [aiSeverityAnalyzing, setAiSeverityAnalyzing] = useState(false);
  const [aiSeverity, setAiSeverity] = useState<AISeverityAnalysis | null>(null);
  const [aiReportGenerating, setAiReportGenerating] = useState(false);
  const [aiReport, setAiReport] = useState<AIReport | null>(null);
  const [aiReportModal, setAiReportModal] = useState(false);

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;
  if (error) return <div className="text-center py-20 text-red-600">{error}</div>;
  if (!signal) return <div className="text-center py-20 text-surface-500">Signalement introuvable</div>;

  const isAdmin = user?.role === "admin" || user?.role === "ADMIN";
  const isOwner = user?.id === signal.created_by_user?.id;
  const canEdit = isOwner || isAdmin;

  const handleDelete = async () => {
    if (!window.confirm("Supprimer ce signalement définitivement ?")) return;
    setActionLoading(true);
    try {
      await signals.delete(Number(id));
      toast("Signalement supprimé", "success");
      navigate("/signals");
    } catch (err: any) {
      toast(err.response?.data?.message || "Échec de la suppression", "error");
    } finally { setActionLoading(false); }
  };

  const sourceStyle = SOURCE_STYLES[signal.source] || "bg-surface-100 text-surface-800";
  const verifStyle = VERIFICATION_STYLES[signal.verification_status] || "bg-surface-100 text-surface-800";

  const runAIClassify = async () => {
    if (!signal.description) return;
    setAiClassifying(true); setAiClassification(null);
    try { const res = await ai.classify({ text: signal.description, location: { latitude: signal.latitude, longitude: signal.longitude } }); setAiClassification(res.data.data || null); } catch { toast("Classification échouée", "error"); } finally { setAiClassifying(false); }
  };
  const runAIAssess = async () => {
    if (!signal.description) return;
    setAiAssessing(true); setAiPriority(null);
    try { const res = await ai.assessPriority({ description: signal.description, latitude: signal.latitude, longitude: signal.longitude, safety_risk_level: signal.safety_risk_level || undefined, affected_people_count: signal.affected_people_count || undefined, affected_area_sqm: signal.affected_area_sqm || undefined }); setAiPriority(res.data.data || null); } catch { toast("Évaluation échouée", "error"); } finally { setAiAssessing(false); }
  };
  const runAIDetect = async () => {
    if (!signal.description) return;
    setAiDetecting(true); setAiAnomalies(null);
    try { const res = await ai.detectAnomalies({ description: signal.description, latitude: signal.latitude, longitude: signal.longitude, category: signal.category?.code }); setAiAnomalies(res.data.data || null); } catch { toast("Détection échouée", "error"); } finally { setAiDetecting(false); }
  };
  const runAISeverity = async () => {
    if (!signal.description) return;
    setAiSeverityAnalyzing(true); setAiSeverity(null);
    try { const res = await ai.analyzeSeverity({ text: signal.description, location: { latitude: signal.latitude, longitude: signal.longitude } }); setAiSeverity(res.data.data || null); } catch { toast("Analyse échouée", "error"); } finally { setAiSeverityAnalyzing(false); }
  };
  const runAIReport = async () => {
    if (!signal.id) return;
    setAiReportGenerating(true); setAiReport(null);
    try { const res = await ai.generateReport(signal.id); setAiReport(res.data.data || null); setAiReportModal(true); } catch { toast("Génération échouée", "error"); } finally { setAiReportGenerating(false); }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Header Section */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 flex-wrap mb-2">
                <h1 className="page-title truncate">{signal.title}</h1>
                <StatusBadge status={signal.status} size="md" />
                <span className={`badge ${sourceStyle}`}>{signal.source || "UNKNOWN"}</span>
                {signal.verification_status && (
                  <span className={`badge ${verifStyle}`}>{signal.verification_status.replace(/_/g, " ")}</span>
                )}
              </div>
              <p className="text-sm text-surface-400">
                {signal.reference_number}
                <span className="mx-2">&middot;</span>
                Créé le {new Date(signal.created_at).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
                {signal.created_by_user && <span> par {signal.created_by_user.first_name} {signal.created_by_user.last_name}</span>}
              </p>
            </div>
            <div className="flex gap-2">
              {canEdit && (
                <button onClick={() => navigate(`/signals/${id}/edit`)} className="btn-secondary">
                  <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  Modifier
                </button>
              )}
              {(isAdmin || isOwner) && !signal.is_deleted && (
                <button onClick={handleDelete} disabled={actionLoading} className="btn-ghost text-red-600 hover:bg-red-50">
                  Supprimer
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="card">
            <div className="card-body">
              <h2 className="section-title mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" /></svg>
                Description
              </h2>
              <p className="text-surface-700 whitespace-pre-wrap leading-relaxed">{signal.description || "Aucune description fournie."}</p>
            </div>
          </div>

          {/* Location */}
          <div className="card">
            <div className="card-body">
              <h2 className="section-title mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /></svg>
                Localisation
              </h2>
              <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                <div className="flex items-center gap-2"><span className="text-surface-400 w-20">Latitude</span><span className="font-mono bg-surface-50 px-2 py-0.5 rounded text-surface-700">{signal.latitude.toFixed(6)}</span></div>
                <div className="flex items-center gap-2"><span className="text-surface-400 w-20">Longitude</span><span className="font-mono bg-surface-50 px-2 py-0.5 rounded text-surface-700">{signal.longitude.toFixed(6)}</span></div>
                {signal.address && <div className="col-span-2 flex items-center gap-2"><span className="text-surface-400 w-20">Adresse</span><span className="text-surface-700">{signal.address}</span></div>}
                {signal.city && <div className="flex items-center gap-2"><span className="text-surface-400 w-20">Ville</span><span className="text-surface-700">{signal.city}</span></div>}
                {signal.country && <div className="flex items-center gap-2"><span className="text-surface-400 w-20">Pays</span><span className="text-surface-700">{signal.country}</span></div>}
              </div>
            </div>
          </div>

          {/* Media */}
          {signal.images && signal.images.length > 0 && (
            <div className="card">
              <div className="card-body">
                <h2 className="section-title mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                  Photos
                </h2>
                <div className="grid grid-cols-3 gap-4">
                  {signal.images.map((url, i) => (
                    <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="group relative">
                      <img src={url} alt={`Photo ${i + 1}`} className="rounded-xl object-cover h-44 w-full border border-surface-200 group-hover:opacity-90 transition-all duration-200" />
                      <div className="absolute inset-0 rounded-xl bg-black/0 group-hover:bg-black/10 transition-all duration-200 flex items-center justify-center">
                        <svg className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-all duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Impact */}
          {(signal.estimated_damage_cost || signal.affected_people_count || signal.affected_area_sqm) && (
            <div className="card">
              <div className="card-body">
                <h2 className="section-title mb-4">Impact</h2>
                <div className="grid grid-cols-3 gap-4">
                  {signal.estimated_damage_cost != null && <div className="kpi-card text-center"><p className="kpi-label">Coût estimé</p><p className="kpi-value text-brand-600">{signal.estimated_damage_cost.toLocaleString()} $</p></div>}
                  {signal.affected_people_count != null && <div className="kpi-card text-center"><p className="kpi-label">Personnes affectées</p><p className="kpi-value text-orange-600">{signal.affected_people_count}</p></div>}
                  {signal.affected_area_sqm != null && <div className="kpi-card text-center"><p className="kpi-label">Zone</p><p className="kpi-value text-green-600">{signal.affected_area_sqm} m²</p></div>}
                </div>
              </div>
            </div>
          )}

          {/* AI Section */}
          <div className="card">
            <div className="card-body">
              <h2 className="section-title mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                Analyse IA
                <span className="badge bg-purple-100 text-purple-700 text-[10px]">Automatique</span>
              </h2>

              {/* AI Score Cards */}
              {signal.ai_confidence_score != null && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                  {signal.ai_confidence_score != null && (
                    <div className="bg-purple-50 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-purple-500 font-medium uppercase tracking-wider">Confiance</p>
                      <p className="text-lg font-bold text-purple-700">{(signal.ai_confidence_score * 100).toFixed(0)}%</p>
                    </div>
                  )}
                  {signal.ai_priority_score != null && (
                    <div className="bg-orange-50 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-orange-500 font-medium uppercase tracking-wider">Priorité</p>
                      <p className="text-lg font-bold text-orange-700">{signal.ai_priority_score.toFixed(1)}</p>
                    </div>
                  )}
                  {signal.ai_severity_score != null && (
                    <div className="bg-red-50 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-red-500 font-medium uppercase tracking-wider">Sévérité</p>
                      <p className="text-lg font-bold text-red-700">{(signal.ai_severity_score * 100).toFixed(0)}%</p>
                    </div>
                  )}
                  {signal.ai_urgency_score != null && (
                    <div className="bg-amber-50 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-amber-500 font-medium uppercase tracking-wider">Urgence</p>
                      <p className="text-lg font-bold text-amber-700">{(signal.ai_urgency_score * 100).toFixed(0)}%</p>
                    </div>
                  )}
                </div>
              )}

              {/* AI Action Buttons */}
              <div className="flex flex-wrap gap-2">
                <button onClick={runAIClassify} disabled={aiClassifying || !signal.description}
                  className="btn-ghost text-xs bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200">
                  {aiClassifying ? <LoadingSpinner size="sm" /> : null}
                  {aiClassifying ? "Classification..." : "Classifier"}
                </button>
                <button onClick={runAIAssess} disabled={aiAssessing || !signal.description}
                  className="btn-ghost text-xs bg-orange-50 text-orange-700 hover:bg-orange-100 border border-orange-200">
                  {aiAssessing ? <LoadingSpinner size="sm" /> : null}
                  {aiAssessing ? "Évaluation..." : "Évaluer priorité"}
                </button>
                <button onClick={runAIDetect} disabled={aiDetecting || !signal.description}
                  className="btn-ghost text-xs bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200">
                  {aiDetecting ? <LoadingSpinner size="sm" /> : null}
                  {aiDetecting ? "Détection..." : "Détecter anomalies"}
                </button>
                <button onClick={runAISeverity} disabled={aiSeverityAnalyzing || !signal.description}
                  className="btn-ghost text-xs bg-red-50 text-red-700 hover:bg-red-100 border border-red-200">
                  {aiSeverityAnalyzing ? <LoadingSpinner size="sm" /> : null}
                  {aiSeverityAnalyzing ? "Analyse..." : "Analyser sévérité"}
                </button>
                <button onClick={runAIReport} disabled={aiReportGenerating}
                  className="btn-ghost text-xs bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200">
                  {aiReportGenerating ? <LoadingSpinner size="sm" /> : null}
                  {aiReportGenerating ? "Génération..." : "Rapport IA complet"}
                </button>
              </div>

              {/* AI Results */}
              {aiClassification && (
                <div className="mt-4 p-4 bg-purple-50/70 border border-purple-100 rounded-xl text-sm space-y-2 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-purple-800">Classification</span>
                    <span className="badge bg-purple-200 text-purple-800">{(aiClassification.confidence_score * 100).toFixed(1)}% de confiance</span>
                  </div>
                  <p className="text-purple-700">Catégorie prédite : <span className="font-bold capitalize">{aiClassification.predicted_category}</span></p>
                  {aiClassification.all_scores && Object.entries(aiClassification.all_scores).filter(([, s]) => (s as number) > 0.1).sort(([, a], [, b]) => (b as number) - (a as number)).slice(0, 5).map(([cat, score]) => (
                    <div key={cat} className="flex items-center gap-2">
                      <span className="text-xs text-purple-600 capitalize w-24">{cat}</span>
                      <div className="flex-1 h-2 bg-purple-200 rounded-full overflow-hidden"><div className="h-full bg-purple-600 rounded-full transition-all duration-500" style={{ width: `${(score as number) * 100}%` }} /></div>
                      <span className="text-[10px] text-purple-500 w-8 text-right">{(score as number * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              )}
              {aiPriority && (
                <div className="mt-4 p-4 bg-orange-50/70 border border-orange-100 rounded-xl text-sm space-y-2 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-orange-800">Évaluation de priorité</span>
                    <span className={`badge ${aiPriority.priority_level === "critical" ? "bg-red-100 text-red-800" : aiPriority.priority_level === "high" ? "bg-orange-100 text-orange-800" : aiPriority.priority_level === "medium" ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>{aiPriority.priority_level.toUpperCase()}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 mt-2">
                    {[
                      { label: "Sévérité", value: aiPriority.severity_score, color: "red" },
                      { label: "Urgence", value: aiPriority.urgency_score, color: "amber" },
                      { label: "Impact", value: aiPriority.impact_score, color: "blue" }
                    ].map(({ label, value, color }) => (
                      <div key={label} className="text-center p-2 bg-white rounded-lg border border-orange-100">
                        <p className="text-[10px] text-surface-400 uppercase">{label}</p>
                        <p className={`text-lg font-bold text-${color}-600`}>{(value * 100).toFixed(0)}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {aiAnomalies && (
                <div className={`mt-4 p-4 rounded-xl text-sm space-y-2 animate-fade-in ${aiAnomalies.anomalies_detected ? "bg-red-50/70 border border-red-100" : "bg-green-50/70 border border-green-100"}`}>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{aiAnomalies.anomalies_detected ? `Anomalies détectées (${aiAnomalies.anomaly_count})` : "Aucune anomalie détectée"}</span>
                    <span className={`badge ${aiAnomalies.risk_level === "high" ? "bg-red-200 text-red-800" : aiAnomalies.risk_level === "medium" ? "bg-yellow-200 text-yellow-800" : "bg-green-200 text-green-800"}`}>{aiAnomalies.risk_level}</span>
                  </div>
                </div>
              )}
              {aiSeverity && (
                <div className="mt-4 p-4 bg-red-50/70 border border-red-100 rounded-xl text-sm space-y-2 animate-fade-in">
                  <span className="font-semibold text-red-800">Analyse de sévérité</span>
                  <p className="text-red-700">Catégorie : <span className="font-bold capitalize">{aiSeverity.summary.category}</span></p>
                  <p className="text-red-700">Confiance : <span className="font-bold">{(aiSeverity.summary.confidence * 100).toFixed(1)}%</span></p>
                </div>
              )}
            </div>
          </div>

          {/* Resolution */}
          {signal.resolution_description && (
            <div className="card border-green-200">
              <div className="card-body">
                <h2 className="section-title text-green-800 mb-4">Résolution</h2>
                <p className="text-surface-700 whitespace-pre-wrap">{signal.resolution_description}</p>
                <div className="grid grid-cols-3 gap-4 mt-4 text-sm">
                  {signal.resolution_method && <div><span className="text-surface-400">Méthode :</span> <span className="font-medium">{signal.resolution_method}</span></div>}
                  {signal.resolution_cost && <div><span className="text-surface-400">Coût :</span> <span className="font-medium">{signal.resolution_cost.toLocaleString()} $</span></div>}
                  {signal.resolved_at && <div><span className="text-surface-400">Résolu le :</span> <span className="font-medium">{new Date(signal.resolved_at).toLocaleDateString("fr-FR")}</span></div>}
                </div>
                {signal.citizen_satisfaction != null && (
                  <div className="mt-4 p-4 bg-brand-50 rounded-xl flex items-center gap-4">
                    <span className="text-sm text-surface-500">Satisfaction citoyen :</span>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <svg key={star} className={`w-5 h-5 ${star <= signal.citizen_satisfaction ? "text-yellow-400" : "text-surface-200"}`} fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                      ))}
                    </div>
                    {signal.citizen_feedback && <p className="text-sm text-surface-600 italic">"{signal.citizen_feedback}"</p>}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <SignalWorkflowPanel signal={signal} onRefresh={refetch} />

          <div className="card">
            <div className="card-body space-y-3 text-sm">
              <h3 className="text-[10px] font-semibold text-surface-400 uppercase tracking-widest">Détails</h3>
              <DetailRow label="Statut" value={<StatusBadge status={signal.status} />} />
              <DetailRow label="Source" value={signal.source || "-"} />
              <DetailRow label="Visibilité" value={signal.is_public ? "Public" : "Privé"} />
              <DetailRow label="Anonyme" value={signal.is_anonymous ? "Oui" : "Non"} />
              {signal.category && <DetailRow label="Catégorie" value={<span className="badge bg-brand-50 text-brand-700">{signal.category.name}</span>} />}
              {signal.priority && (
                <DetailRow label="Priorité" value={
                  <span className={`badge ${signal.priority.priority_level >= 4 ? "bg-red-100 text-red-800" : signal.priority.priority_level >= 3 ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>
                    {signal.priority.name}
                  </span>
                } />
              )}
              <div className="divider my-1" />
              {signal.created_by_user && <DetailRow label="Signalé par" value={<span className="font-medium">{signal.created_by_user.first_name} {signal.created_by_user.last_name}</span>} />}
              {signal.processed_by_user && <DetailRow label="Assigné à" value={<span className="font-medium">{signal.processed_by_user.first_name} {signal.processed_by_user.last_name}</span>} />}
            </div>
          </div>
        </div>
      </div>

      {/* AI Report Modal */}
      <Modal open={aiReportModal} onClose={() => setAiReportModal(false)} title="Rapport IA">
        {aiReport && (
          <div className="space-y-4 max-h-[70vh] overflow-y-auto">
            <div className="p-4 bg-purple-50 rounded-xl">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-surface-400">Code :</span> <span className="font-medium">{aiReport.report_code}</span></div>
                <div><span className="text-surface-400">Généré le :</span> <span className="font-medium">{new Date(aiReport.generated_at).toLocaleString("fr-FR")}</span></div>
                <div><span className="text-surface-400">Statut :</span> <StatusBadge status={aiReport.status} /></div>
              </div>
            </div>
            <div><h3 className="font-semibold text-surface-800 mb-2">Résumé</h3><p className="text-sm text-surface-600 leading-relaxed">{aiReport.summary}</p></div>
            <div><h3 className="font-semibold text-surface-800 mb-2">Constats principaux</h3><ul className="list-disc list-inside text-sm text-surface-600 space-y-1">{aiReport.key_findings.map((f, i) => <li key={i}>{f}</li>)}</ul></div>
            <div><h3 className="font-semibold text-surface-800 mb-2">Recommandations</h3><ul className="list-disc list-inside text-sm text-surface-600 space-y-1">{aiReport.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul></div>
            <div className="flex justify-end pt-2"><button onClick={() => setAiReportModal(false)} className="btn-secondary">Fermer</button></div>
          </div>
        )}
      </Modal>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between items-center py-1.5">
      <span className="text-surface-400 text-xs">{label}</span>
      <span className="font-medium text-surface-700 text-right">{value}</span>
    </div>
  );
}
