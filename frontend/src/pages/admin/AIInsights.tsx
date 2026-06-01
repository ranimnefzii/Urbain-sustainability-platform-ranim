import { useEffect, useState } from "react";
import { ai } from "../../api/endpoints";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useToast } from "../../contexts/ToastContext";
import type { AIInsights, AIModelInfo, AITrendPrediction } from "../../types";

export default function AIInsights() {
  const { toast } = useToast();
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [modelInfo, setModelInfo] = useState<AIModelInfo | null>(null);
  const [trends, setTrends] = useState<AITrendPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [trendDays, setTrendDays] = useState(30);
  const [predicting, setPredicting] = useState(false);
  const [batchText, setBatchText] = useState("");
  const [batchResults, setBatchResults] = useState<any[] | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [iRes, mRes] = await Promise.all([
          ai.insights(30),
          ai.modelInfo(),
        ]);
        setInsights(iRes.data.data || null);
        setModelInfo(mRes.data.data || null);
        setTrends(iRes.data.data?.trends || null);
      } catch {
        toast("Failed to load AI insights", "error");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [toast]);

  const handlePredict = async () => {
    setPredicting(true);
    try {
      const res = await ai.predictTrends({ days: trendDays });
      setTrends(res.data.data || null);
    } catch {
      toast("Trend prediction failed", "error");
    } finally {
      setPredicting(false);
    }
  };

  const maxWeekly = trends?.weekly_breakdown ? Math.max(...Object.values(trends.weekly_breakdown), 1) : 1;

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Insights</h1>
          <p className="text-sm text-gray-500 mt-1">Machine learning analytics and predictions</p>
        </div>
      </div>

      {/* Model Info Card */}
      {modelInfo && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-900">AI Model</h2>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${modelInfo.status === "loaded" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
              {modelInfo.status}
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-xs text-gray-500">Model</p>
              <p className="font-medium">{modelInfo.name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Version</p>
              <p className="font-medium">{modelInfo.version}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Type</p>
              <p className="font-medium">{modelInfo.type}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Framework</p>
              <p className="font-medium">{modelInfo.framework}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Confidence Threshold</p>
              <p className="font-medium">{(modelInfo.confidence_threshold * 100).toFixed(0)}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Avg Processing</p>
              <p className="font-medium">{modelInfo.performance_metrics?.avg_processing_time_ms}ms</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Throughput</p>
              <p className="font-medium">{modelInfo.performance_metrics?.throughput_per_second}/s</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Uptime</p>
              <p className="font-medium">{modelInfo.performance_metrics?.uptime_percentage}%</p>
            </div>
          </div>
          {modelInfo.capabilities && modelInfo.capabilities.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {modelInfo.capabilities.map((cap) => (
                <span key={cap} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">{cap.replace(/_/g, " ")}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Trend Prediction */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-900">Signal Trend Prediction</h2>
          <div className="flex items-center gap-2">
            <select value={trendDays} onChange={(e) => setTrendDays(Number(e.target.value))}
              className="border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
            <button onClick={handlePredict} disabled={predicting}
              className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              {predicting ? "..." : "Predict"}
            </button>
          </div>
        </div>

        {trends ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-gray-900">{trends.predicted_total_signals}</p>
                <p className="text-xs text-gray-500">Predicted Total</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className={`text-2xl font-bold ${trends.trend_direction === "increasing" ? "text-red-600" : trends.trend_direction === "decreasing" ? "text-green-600" : "text-yellow-600"}`}>
                  {trends.trend_direction}
                </p>
                <p className="text-xs text-gray-500">Trend Direction</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-blue-600">{(trends.confidence_level * 100).toFixed(0)}%</p>
                <p className="text-xs text-gray-500">Confidence</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-gray-900">{trends.trend_strength.toFixed(1)}%</p>
                <p className="text-xs text-gray-500">Trend Strength</p>
              </div>
            </div>

            {trends.weekly_breakdown && Object.keys(trends.weekly_breakdown).length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Weekly Breakdown</p>
                <div className="space-y-1.5">
                  {Object.entries(trends.weekly_breakdown).map(([week, count]) => (
                    <div key={week}>
                      <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                        <span className="capitalize">{week.replace(/_/g, " ")}</span>
                        <span className="font-medium">{count as number}</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${((count as number) / maxWeekly) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {trends.daily_predictions && trends.daily_predictions.length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-500 mb-2">Daily Predictions (first 14 days)</p>
                <div className="overflow-x-auto">
                  <div className="flex gap-1 min-w-[400px]">
                    {trends.daily_predictions.slice(0, 14).map((day, i) => {
                      const maxD = Math.max(...trends.daily_predictions.slice(0, 14).map((d) => d.predicted_signals), 1);
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center">
                          <div className="w-full bg-gray-100 rounded-t" style={{ height: "60px", position: "relative" }}>
                            <div className="absolute bottom-0 w-full bg-blue-500 rounded-t transition-all"
                              style={{ height: `${(day.predicted_signals / maxD) * 100}%`, minHeight: "4px" }} />
                          </div>
                          <span className="text-[9px] text-gray-400 mt-0.5">{day.date.slice(5)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {trends.factors && (
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(trends.factors).filter(([, v]) => v).map(([key]) => (
                  <span key={key} className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">{key.replace(/_/g, " ")}</span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500 text-center py-6">Run a prediction to see trend data</p>
        )}
      </div>

      {/* Supported Categories */}
      {modelInfo?.supported_categories && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Supported Classification Categories</h2>
          <div className="flex flex-wrap gap-2">
            {modelInfo.supported_categories.map((cat) => (
              <div key={cat} className="bg-gray-50 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 capitalize">
                {cat}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Batch Classification */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-gray-900 mb-3">Batch Classification</h2>
        <p className="text-xs text-gray-500 mb-3">Enter signal descriptions (one per line) to batch-classify them using AI</p>
        <textarea value={batchText} onChange={(e) => setBatchText(e.target.value)} rows={5}
          placeholder="Road pothole near the market&#10;Street light not working on Avenue Habib Bourguiba&#10;Garbage not collected for 3 days in Lafayette"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3" />
        <button onClick={async () => { if (!batchText.trim()) return; setBatchLoading(true); setBatchResults(null); try { const lines = batchText.split("\n").filter(Boolean); const r = await ai.batchClassify(lines.map((text) => ({ description: text }))); setBatchResults(r.data.data?.results || []); } catch { toast("Batch classification failed", "error"); } finally { setBatchLoading(false); } }}
          disabled={batchLoading || !batchText.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
          {batchLoading ? "Classifying..." : `Classify ${batchText.split("\n").filter(Boolean).length || 0} Descriptions`}
        </button>
        {batchResults && batchResults.length > 0 && (
          <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
            {batchResults.map((res, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg text-sm">
                <p className="text-xs text-gray-400 mb-1">#{i + 1}</p>
                <p className="font-medium capitalize text-blue-800">{res.predicted_category || res.category || "Unknown"}</p>
                {res.confidence_score != null && (
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(res.confidence_score * 100)}%` }} />
                    </div>
                    <span className="text-xs text-gray-500">{(res.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dashboard Summary */}
      {insights?.dashboard && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">AI Dashboard Summary</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-blue-700">{insights.dashboard.predicted_signals_next_30d}</p>
              <p className="text-xs text-blue-600 mt-1">Predicted Signals (30d)</p>
            </div>
            <div className={`rounded-lg p-4 text-center ${
              insights.dashboard.trend_direction === "increasing" ? "bg-red-50" :
              insights.dashboard.trend_direction === "decreasing" ? "bg-green-50" : "bg-yellow-50"
            }`}>
              <p className={`text-lg font-bold capitalize ${
                insights.dashboard.trend_direction === "increasing" ? "text-red-700" :
                insights.dashboard.trend_direction === "decreasing" ? "text-green-700" : "text-yellow-700"
              }`}>{insights.dashboard.trend_direction}</p>
              <p className="text-xs text-gray-500 mt-1">Trend</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-purple-700">{(insights.dashboard.confidence_level * 100).toFixed(0)}%</p>
              <p className="text-xs text-purple-600 mt-1">AI Confidence</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
