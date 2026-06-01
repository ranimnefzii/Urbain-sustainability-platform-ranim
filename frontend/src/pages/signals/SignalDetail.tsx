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

const SOURCE_STYLES: Record<string, string> = {
  MOBILE: "bg-blue-100 text-blue-800",
  WEB: "bg-purple-100 text-purple-800",
  API: "bg-gray-100 text-gray-800",
  EMAIL: "bg-green-100 text-green-800",
  ADMIN: "bg-yellow-100 text-yellow-800",
};

const VERIFICATION_STYLES: Record<string, string> = {
  VERIFIED: "bg-green-100 text-green-800",
  UNVERIFIED: "bg-yellow-100 text-yellow-800",
  PENDING: "bg-gray-100 text-gray-800",
  REJECTED: "bg-red-100 text-red-800",
};

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
  if (!signal) return <div className="text-center py-20 text-gray-500">Signal not found</div>;

  const isAdmin = user?.role === "admin" || user?.role === "ADMIN";
  const isOwner = user?.id === signal.created_by_user?.id;
  const canEdit = isOwner || isAdmin;

  const handleDelete = async () => {
    if (!confirm("Delete this signal permanently?")) return;
    setActionLoading(true);
    try {
      await signals.delete(Number(id));
      toast("Signal deleted", "success");
      navigate("/signals");
    } catch (err: any) {
      toast(err.response?.data?.message || "Delete failed", "error");
    } finally {
      setActionLoading(false);
    }
  };

  const sourceStyle = SOURCE_STYLES[signal.source] || "bg-gray-100 text-gray-800";
  const verifStyle = VERIFICATION_STYLES[signal.verification_status] || "bg-gray-100 text-gray-800";

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold text-gray-900">{signal.title}</h1>
            <StatusBadge status={signal.status} size="md" />
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${sourceStyle}`}>{signal.source || "UNKNOWN"}</span>
            {signal.verification_status && (
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${verifStyle}`}>
                {signal.verification_status.replace(/_/g, " ")}
              </span>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1">{signal.reference_number} &middot; Created {new Date(signal.created_at).toLocaleString()}</p>
        </div>
        <div className="flex gap-2">
          {canEdit && (
            <button onClick={() => navigate(`/signals/${id}/edit`)} className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Edit</button>
          )}
          {(isAdmin || isOwner) && !signal.is_deleted && (
            <button onClick={handleDelete} disabled={actionLoading} className="px-3 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
              {actionLoading ? "..." : "Delete"}
            </button>
          )}
          {isAdmin && signal.is_deleted && (
            <button onClick={async () => {
              setActionLoading(true);
              try {
                await signals.restore(Number(id));
                toast("Signal restored", "success");
                refetch();
              } catch {
                toast("Restore failed", "error");
              } finally {
                setActionLoading(false);
              }
            }} disabled={actionLoading} className="px-3 py-2 text-sm border border-green-300 text-green-600 rounded-lg hover:bg-green-50">
              {actionLoading ? "..." : "Restore"}
            </button>
          )}
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{signal.description || "No description provided."}</p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Location</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">Latitude:</span> <span className="font-mono">{signal.latitude.toFixed(6)}</span></div>
              <div><span className="text-gray-500">Longitude:</span> <span className="font-mono">{signal.longitude.toFixed(6)}</span></div>
              {signal.address && <div className="col-span-2"><span className="text-gray-500">Address:</span> {signal.address}</div>}
              {signal.city && <div><span className="text-gray-500">City:</span> {signal.city}</div>}
              {signal.postal_code && <div><span className="text-gray-500">Postal Code:</span> {signal.postal_code}</div>}
              {signal.country && <div><span className="text-gray-500">Country:</span> {signal.country}</div>}
              {signal.location_accuracy && <div><span className="text-gray-500">Accuracy:</span> {signal.location_accuracy}</div>}
              {signal.location_description && <div className="col-span-2"><span className="text-gray-500">Location Note:</span> {signal.location_description}</div>}
            </div>
          </div>

          {/* Images */}
          {signal.images && signal.images.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Images</h2>
              <div className="grid grid-cols-3 gap-4">
                {signal.images.map((url, i) => (
                  <a key={i} href={url} target="_blank" rel="noopener noreferrer">
                    <img src={url} alt={`Signal ${i + 1}`} className="rounded-lg object-cover h-40 w-full border hover:opacity-90 transition" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Videos */}
          {signal.videos && signal.videos.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Videos</h2>
              <div className="grid grid-cols-2 gap-4">
                {signal.videos.map((url, i) => (
                  <video key={i} src={url} controls className="rounded-lg w-full border" />
                ))}
              </div>
            </div>
          )}

          {/* Documents */}
          {signal.documents && signal.documents.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Documents</h2>
              <div className="space-y-2">
                {signal.documents.map((url, i) => (
                  <a key={i} href={url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 text-sm">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                    <span className="text-blue-600 hover:underline">Document {i + 1}</span>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Audio */}
          {signal.audio_files && signal.audio_files.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Audio Recordings</h2>
              <div className="space-y-3">
                {signal.audio_files.map((url, i) => (
                  <audio key={i} src={url} controls className="w-full" />
                ))}
              </div>
            </div>
          )}

          {/* Impact Details */}
          {(signal.estimated_damage_cost || signal.affected_people_count || signal.affected_area_sqm) && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Impact Details</h2>
              <div className="grid grid-cols-3 gap-4 text-sm">
                {signal.estimated_damage_cost && <div><span className="text-gray-500">Est. Damage Cost:</span> <span className="font-medium">${signal.estimated_damage_cost.toLocaleString()}</span></div>}
                {signal.affected_people_count && <div><span className="text-gray-500">People Affected:</span> <span className="font-medium">{signal.affected_people_count}</span></div>}
                {signal.affected_area_sqm && <div><span className="text-gray-500">Area Affected:</span> <span className="font-medium">{signal.affected_area_sqm} sqm</span></div>}
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Analysis</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {signal.ai_confidence_score != null && <StatBox label="Confidence" value={`${(signal.ai_confidence_score * 100).toFixed(0)}%`} />}
              {signal.ai_priority_score != null && <StatBox label="Priority Score" value={signal.ai_priority_score.toFixed(1)} />}
              {signal.ai_severity_score != null && <StatBox label="Severity" value={`${(signal.ai_severity_score * 100).toFixed(0)}%`} />}
              {signal.ai_urgency_score != null && <StatBox label="Urgency" value={`${(signal.ai_urgency_score * 100).toFixed(0)}%`} />}
              {signal.safety_risk_level != null && <StatBox label="Safety Risk" value={String(signal.safety_risk_level)} />}
            </div>

            {/* AI Action Buttons */}
            <div className="mt-4 flex flex-wrap gap-2 border-t border-gray-100 pt-4">
              <button onClick={async () => {
                if (!signal.description) return;
                setAiClassifying(true); setAiClassification(null);
                try {
                  const loc = { latitude: signal.latitude, longitude: signal.longitude };
                  const res = await ai.classify({ text: signal.description, location: loc });
                  setAiClassification(res.data.data || null);
                } catch { toast("Classification failed", "error"); } finally { setAiClassifying(false); }
              }} disabled={aiClassifying || !signal.description}
                className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1">
                {aiClassifying ? <LoadingSpinner size="sm" /> : null}
                {aiClassifying ? "Classifying..." : "Classify"}
              </button>
              <button onClick={async () => {
                if (!signal.description) return;
                setAiAssessing(true); setAiPriority(null);
                try {
                  const res = await ai.assessPriority({
                    description: signal.description,
                    latitude: signal.latitude,
                    longitude: signal.longitude,
                    safety_risk_level: signal.safety_risk_level || undefined,
                    affected_people_count: signal.affected_people_count || undefined,
                    affected_area_sqm: signal.affected_area_sqm || undefined,
                  });
                  setAiPriority(res.data.data || null);
                } catch { toast("Priority assessment failed", "error"); } finally { setAiAssessing(false); }
              }} disabled={aiAssessing || !signal.description}
                className="px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-1">
                {aiAssessing ? <LoadingSpinner size="sm" /> : null}
                {aiAssessing ? "Assessing..." : "Assess Priority"}
              </button>
              <button onClick={async () => {
                if (!signal.description) return;
                setAiDetecting(true); setAiAnomalies(null);
                try {
                  const res = await ai.detectAnomalies({
                    description: signal.description,
                    latitude: signal.latitude,
                    longitude: signal.longitude,
                    category: signal.category?.code,
                  });
                  setAiAnomalies(res.data.data || null);
                } catch { toast("Anomaly detection failed", "error"); } finally { setAiDetecting(false); }
              }} disabled={aiDetecting || !signal.description}
                className="px-3 py-1.5 text-xs bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center gap-1">
                {aiDetecting ? <LoadingSpinner size="sm" /> : null}
                {aiDetecting ? "Scanning..." : "Detect Anomalies"}
              </button>
              <button onClick={async () => {
                if (!signal.description) return;
                setAiSeverityAnalyzing(true); setAiSeverity(null);
                try {
                  const loc = { latitude: signal.latitude, longitude: signal.longitude };
                  const res = await ai.analyzeSeverity({ text: signal.description, location: loc });
                  setAiSeverity(res.data.data || null);
                } catch { toast("Severity analysis failed", "error"); } finally { setAiSeverityAnalyzing(false); }
              }} disabled={aiSeverityAnalyzing || !signal.description}
                className="px-3 py-1.5 text-xs bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-1">
                {aiSeverityAnalyzing ? <LoadingSpinner size="sm" /> : null}
                {aiSeverityAnalyzing ? "Analyzing..." : "Analyze Severity"}
              </button>
              <button onClick={async () => {
                if (!signal.id) return;
                setAiReportGenerating(true); setAiReport(null);
                try {
                  const res = await ai.generateReport(signal.id);
                  setAiReport(res.data.data || null);
                  setAiReportModal(true);
                } catch { toast("Report generation failed", "error"); } finally { setAiReportGenerating(false); }
              }} disabled={aiReportGenerating}
                className="px-3 py-1.5 text-xs bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-1">
                {aiReportGenerating ? <LoadingSpinner size="sm" /> : null}
                {aiReportGenerating ? "Generating..." : "Generate AI Report"}
              </button>
            </div>

            {/* Classification Results */}
            {aiClassification && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm space-y-1">
                <p><span className="font-medium text-blue-800">Category:</span> <span className="capitalize">{aiClassification.predicted_category}</span></p>
                <p><span className="font-medium text-blue-800">Confidence:</span> {(aiClassification.confidence_score * 100).toFixed(1)}%</p>
                {aiClassification.all_scores && Object.entries(aiClassification.all_scores).filter(([, s]) => (s as number) > 0.1).length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-blue-600 mb-1">All scores:</p>
                    <div className="space-y-0.5">
                      {Object.entries(aiClassification.all_scores).filter(([, s]) => (s as number) > 0.1).sort(([, a], [, b]) => (b as number) - (a as number)).slice(0, 5).map(([cat, score]) => (
                        <div key={cat} className="flex items-center gap-2">
                          <span className="text-xs text-blue-700 capitalize w-20">{cat}</span>
                          <div className="flex-1 h-1.5 bg-blue-200 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-600 rounded-full" style={{ width: `${(score as number) * 100}%` }} />
                          </div>
                          <span className="text-[10px] text-blue-500 w-8 text-right">{(score as number * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Priority Assessment Results */}
            {aiPriority && (
              <div className="mt-3 p-3 bg-indigo-50 rounded-lg text-sm space-y-1">
                <p className="flex items-center gap-2">
                  <span className="font-medium text-indigo-800">Priority:</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                    aiPriority.priority_level === "critical" ? "bg-red-100 text-red-800" :
                    aiPriority.priority_level === "high" ? "bg-orange-100 text-orange-800" :
                    aiPriority.priority_level === "medium" ? "bg-yellow-100 text-yellow-800" :
                    "bg-green-100 text-green-800"
                  }`}>{aiPriority.priority_level.toUpperCase()}</span>
                  <span className="text-indigo-600">({(aiPriority.priority_score * 100).toFixed(1)}%)</span>
                </p>
                <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                  <div><span className="text-gray-500">Severity:</span> <span className="font-medium">{(aiPriority.severity_score * 100).toFixed(0)}%</span></div>
                  <div><span className="text-gray-500">Urgency:</span> <span className="font-medium">{(aiPriority.urgency_score * 100).toFixed(0)}%</span></div>
                  <div><span className="text-gray-500">Impact:</span> <span className="font-medium">{(aiPriority.impact_score * 100).toFixed(0)}%</span></div>
                </div>
                {aiPriority.recommendation && (
                  <div className="mt-2 p-2 bg-white rounded border border-indigo-100 text-xs">
                    <p className="font-medium text-indigo-700">Recommendation: {aiPriority.recommendation.action}</p>
                    <p className="text-gray-500">Response: {aiPriority.recommendation.response_time} | Resources: {aiPriority.recommendation.resources}</p>
                  </div>
                )}
              </div>
            )}

            {/* Anomaly Detection Results */}
            {aiAnomalies && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${aiAnomalies.anomalies_detected ? "bg-red-50" : "bg-green-50"}`}>
                <p className="flex items-center gap-2 font-medium">
                  {aiAnomalies.anomalies_detected ? (
                    <span className="text-red-700">Anomalies Detected ({aiAnomalies.anomaly_count})</span>
                  ) : (
                    <span className="text-green-700">No Anomalies Detected</span>
                  )}
                  <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                    aiAnomalies.risk_level === "high" ? "bg-red-200 text-red-800" :
                    aiAnomalies.risk_level === "medium" ? "bg-yellow-200 text-yellow-800" :
                    "bg-green-200 text-green-800"
                  }`}>{aiAnomalies.risk_level}</span>
                </p>
                {aiAnomalies.anomalies.map((a, i) => (
                  <div key={i} className="mt-1.5 flex items-start gap-2 text-xs">
                    <span className={`mt-0.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                      a.severity === "critical" ? "bg-red-500" : a.severity === "high" ? "bg-orange-500" : a.severity === "medium" ? "bg-yellow-500" : "bg-gray-500"
                    }`} />
                    <div>
                      <span className="font-medium text-gray-700 capitalize">{a.type.replace(/_/g, " ")}</span>
                      <span className="text-gray-500"> - {a.detail}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Severity Analysis Results */}
            {aiSeverity && (
              <div className="mt-3 p-3 bg-red-50 rounded-lg text-sm space-y-1">
                <h3 className="font-bold text-red-800 mb-2">Severity Analysis Summary</h3>
                <p><span className="font-medium">Category:</span> <span className="capitalize">{aiSeverity.summary.category}</span></p>
                <p><span className="font-medium">Confidence:</span> {(aiSeverity.summary.confidence * 100).toFixed(1)}%</p>
                <p className="flex items-center gap-2">
                  <span className="font-medium">Priority Level:</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                    aiSeverity.summary.priority_level === "critical" ? "bg-red-100 text-red-800" :
                    aiSeverity.summary.priority_level === "high" ? "bg-orange-100 text-orange-800" :
                    aiSeverity.summary.priority_level === "medium" ? "bg-yellow-100 text-yellow-800" :
                    "bg-green-100 text-green-800"
                  }`}>{aiSeverity.summary.priority_level.toUpperCase()}</span>
                  <span>({(aiSeverity.summary.priority_score * 100).toFixed(1)}%)</span>
                </p>
                <p><span className="font-medium">Anomalies Detected:</span> {aiSeverity.summary.anomalies_detected ? "Yes" : "No"}</p>
              </div>
            )}
          </div>

          {signal.resolution_description && (
            <div className="bg-white rounded-lg border border-green-200 p-6">
              <h2 className="text-lg font-semibold text-green-800 mb-4">Resolution</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{signal.resolution_description}</p>
              <div className="grid grid-cols-3 gap-4 mt-4 text-sm">
                {signal.resolution_method && <div><span className="text-gray-500">Method:</span> {signal.resolution_method}</div>}
                {signal.resolution_cost && <div><span className="text-gray-500">Cost:</span> ${signal.resolution_cost.toLocaleString()}</div>}
                {signal.resolved_at && <div><span className="text-gray-500">Resolved:</span> {new Date(signal.resolved_at).toLocaleDateString()}</div>}
              </div>
              {signal.citizen_satisfaction != null && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-gray-600">Citizen Satisfaction: </span>
                  <span className="text-lg font-bold text-blue-700">{signal.citizen_satisfaction}/5</span>
                  {signal.citizen_feedback && <p className="text-sm text-gray-600 mt-1">"{signal.citizen_feedback}"</p>}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <SignalWorkflowPanel signal={signal} onRefresh={refetch} />

          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-3 text-sm">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Details</h3>
            <DetailRow label="Status" value={<StatusBadge status={signal.status} />} />
            <DetailRow label="Source" value={signal.source || "-"} />
            <DetailRow label="Verification" value={signal.verification_status || "-"} />
            <DetailRow label="Visibility" value={signal.is_public ? "Public" : "Private"} />
            <DetailRow label="Anonymous" value={signal.is_anonymous ? "Yes" : "No"} />
            {signal.category && <DetailRow label="Category" value={signal.category.name} />}
            {signal.priority && (
              <DetailRow label="Priority" value={
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${signal.priority.priority_level >= 4 ? "bg-red-100 text-red-800" : signal.priority.priority_level >= 3 ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>
                  {signal.priority.name} (L{signal.priority.priority_level})
                </span>
              } />
            )}
            {signal.created_by_user && <DetailRow label="Reported by" value={`${signal.created_by_user.first_name} ${signal.created_by_user.last_name}`} />}
            {signal.processed_by_user && <DetailRow label="Assigned to" value={`${signal.processed_by_user.first_name} ${signal.processed_by_user.last_name}`} />}
          </div>
        </div>
      </div>

      {/* AI Report Modal */}
      <Modal open={aiReportModal} onClose={() => setAiReportModal(false)} title="AI Report">
        {aiReport && (
          <div className="space-y-4 max-h-[70vh] overflow-y-auto">
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Report Code: {aiReport.report_code}</p>
              <p className="text-sm text-gray-600">Generated: {new Date(aiReport.generated_at).toLocaleString()}</p>
              <p className="text-sm text-gray-600">Status: {aiReport.status}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Summary</h3>
              <p className="text-sm text-gray-700">{aiReport.summary}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Key Findings</h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                {aiReport.key_findings.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Recommendations</h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                {aiReport.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
            <div className="border-t pt-3">
              <h3 className="font-semibold text-gray-900 mb-2">AI Analysis Data</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="p-2 bg-gray-50 rounded">
                  <span className="font-medium text-gray-700">Classification:</span>
                  <p className="text-gray-600">{aiReport.classification.predicted_category} ({(aiReport.classification.confidence_score * 100).toFixed(1)}%)</p>
                </div>
                <div className="p-2 bg-gray-50 rounded">
                  <span className="font-medium text-gray-700">Priority:</span>
                  <p className="text-gray-600">{aiReport.priority_assessment.priority_level} ({(aiReport.priority_assessment.priority_score * 100).toFixed(1)}%)</p>
                </div>
              </div>
              <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                <span className="font-medium text-gray-700">Anomalies:</span>
                <p className="text-gray-600">{aiReport.anomalies_detected.anomalies_detected ? `${aiReport.anomalies_detected.anomaly_count} detected (risk: ${aiReport.anomalies_detected.risk_level})` : "None detected"}</p>
              </div>
            </div>
            <div className="flex justify-end pt-2">
              <button onClick={() => setAiReportModal(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Close</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 text-center">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-bold text-gray-800">{value}</p>
    </div>
  );
}
