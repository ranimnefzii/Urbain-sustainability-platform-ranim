import { useState, useEffect } from "react";
import { analytics } from "../../api/endpoints";
import LoadingSpinner from "../../components/ui/LoadingSpinner";

const DAY_OPTIONS = [7, 14, 30, 60, 90];
const SECTION_LABELS: Record<string, string> = {
  dashboard: "Dashboard Overview",
  trends: "Trends",
  category: "Category Breakdown",
  sector: "Sector Performance",
  satisfaction: "Satisfaction",
  responseTimes: "Response Times",
  predictions: "Predictions",
  hotspots: "Hotspots",
  temporal: "Temporal Patterns",
  summary: "Summary Report",
};
const SECTIONS = Object.keys(SECTION_LABELS);

export default function SignalAnalyticsTab() {
  const [days, setDays] = useState(30);
  const [activeSection, setActiveSection] = useState("dashboard");
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<Record<string, any>>({});

  useEffect(() => {
    setLoading(true);
    const results: Record<string, any> = {};

    Promise.all([
      analytics.dashboard(days).then(r => { results.dashboard = r.data?.data; }).catch(() => { results.dashboard = null; }),
      analytics.trends(days, "day").then(r => { results.trends = r.data?.data; }).catch(() => { results.trends = null; }),
      analytics.sectorPerformance(days).then(r => { results.sector = r.data?.data; }).catch(() => { results.sector = null; }),
      analytics.categoryBreakdown(days).then(r => { results.category = r.data?.data; }).catch(() => { results.category = null; }),
      analytics.satisfaction(days).then(r => { results.satisfaction = r.data?.data; }).catch(() => { results.satisfaction = null; }),
      analytics.responseTimes(days).then(r => { results.responseTimes = r.data?.data; }).catch(() => { results.responseTimes = null; }),
      analytics.predictions(days).then(r => { results.predictions = r.data?.data; }).catch(() => { results.predictions = null; }),
      analytics.hotspots(days, 0).then(r => { results.hotspots = r.data?.data; }).catch(() => { results.hotspots = null; }),
      analytics.temporalPatterns(days).then(r => { results.temporal = r.data?.data; }).catch(() => { results.temporal = null; }),
      analytics.summaryReport(days, false).then(r => { results.summary = r.data?.data; }).catch(() => { results.summary = null; }),
    ]).then(() => {
      setData(results);
    }).finally(() => setLoading(false));
  }, [days]);

  const d = data;

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Period:</span>
          <select
            value={days}
            onChange={e => setDays(Number(e.target.value))}
            className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {DAY_OPTIONS.map(d => (
              <option key={d} value={d}>{d} days</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          {SECTIONS.map(s => (
            <button
              key={s}
              onClick={() => setActiveSection(s)}
              className={`text-xs px-2.5 py-1.5 rounded-md font-medium transition-colors ${
                activeSection === s
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {SECTION_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      {activeSection === "dashboard" && (
        <DashboardView data={d.dashboard} days={days} />
      )}
      {activeSection === "trends" && (
        <TrendsView data={d.trends} />
      )}
      {activeSection === "category" && (
        <CategoryBreakdownView data={d.category} />
      )}
      {activeSection === "sector" && (
        <SectorPerformanceView data={d.sector} />
      )}
      {activeSection === "satisfaction" && (
        <SatisfactionView data={d.satisfaction} />
      )}
      {activeSection === "responseTimes" && (
        <ResponseTimesView data={d.responseTimes} />
      )}
      {activeSection === "predictions" && (
        <PredictionsView data={d.predictions} />
      )}
      {activeSection === "hotspots" && (
        <HotspotsView data={d.hotspots} />
      )}
      {activeSection === "temporal" && (
        <TemporalPatternsView data={d.temporal} />
      )}
      {activeSection === "summary" && (
        <SummaryReportView data={d.summary} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard label="Total Signals" value={d.dashboard?.total_signals ?? "—"} color="blue" />
        <KPICard label="Open" value={d.dashboard?.open_signals ?? "—"} color="amber" />
        <KPICard label="Resolved" value={d.dashboard?.resolved_signals ?? "—"} color="green" />
        <KPICard label="Resolution Rate" value={d.dashboard?.resolution_rate != null ? `${d.dashboard.resolution_rate}%` : "—"} color="purple" />
      </div>
    </div>
  );
}

function DashboardView({ data, days }: { data: any; days: number }) {
  if (!data) return <EmptySection />;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Dashboard Overview — Last {days} Days</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStat label="Total Signals" value={String(data.total_signals ?? 0)} />
        <MiniStat label="Open" value={String(data.open_signals ?? 0)} />
        <MiniStat label="In Progress" value={String(data.in_progress_signals ?? 0)} />
        <MiniStat label="Resolved" value={String(data.resolved_signals ?? 0)} />
        <MiniStat label="Cancelled" value={String(data.cancelled_signals ?? 0)} />
        <MiniStat label="Avg Resolution Time" value={data.avg_resolution_time != null ? `${data.avg_resolution_time}h` : "—"} />
        <MiniStat label="Resolution Rate" value={data.resolution_rate != null ? `${data.resolution_rate}%` : "—"} />
        <MiniStat label="Citizen Satisfaction" value={data.avg_satisfaction != null ? `${data.avg_satisfaction}/5` : "—"} />
      </div>
    </div>
  );
}

function TrendsView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const entries = Array.isArray(data) ? data : data.trends ?? data.data ?? [];
  if (!entries.length) return <EmptySection />;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Trends</h3>
      <div className="space-y-2">
        {entries.slice(0, 30).map((item: any, i: number) => {
          const count = item.count ?? item.total ?? 0;
          const maxCount = Math.max(...entries.map((e: any) => e.count ?? e.total ?? 0), 1);
          const label = item.date ?? item.period ?? item.label ?? `#${i + 1}`;
          return (
            <div key={i} className="flex items-center gap-3">
              <span className="text-xs text-gray-500 w-24 truncate shrink-0">{label}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-4 relative overflow-hidden">
                <div
                  className="h-full rounded-full bg-blue-500 transition-all"
                  style={{ width: `${(count / maxCount) * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium text-gray-600 w-10 text-right">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CategoryBreakdownView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const items = Array.isArray(data) ? data : data.categories ?? data.breakdown ?? data.data ?? [];
  if (!items.length) return <EmptySection />;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Category Breakdown</h3>
      <div className="space-y-2">
        {items.map((item: any, i: number) => {
          const count = item.count ?? item.total ?? 0;
          const maxCount = Math.max(...items.map((e: any) => e.count ?? e.total ?? 0), 1);
          return (
            <div key={i} className="flex items-center gap-3">
              <span className="text-sm text-gray-700 w-32 truncate shrink-0 capitalize">{item.name ?? item.category ?? `Category ${i + 1}`}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-3">
                <div className="h-full rounded-full bg-indigo-500" style={{ width: `${(count / maxCount) * 100}%` }} />
              </div>
              <span className="text-sm font-medium text-gray-600 w-10 text-right">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function SectorPerformanceView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const items = Array.isArray(data) ? data : data.sectors ?? data.data ?? [];
  if (!items.length) return <EmptySection />;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Sector Performance</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 px-3 font-medium text-gray-600">Sector</th>
              <th className="text-right py-2 px-3 font-medium text-gray-600">Signals</th>
              <th className="text-right py-2 px-3 font-medium text-gray-600">Resolved</th>
              <th className="text-right py-2 px-3 font-medium text-gray-600">Avg Time</th>
              <th className="text-right py-2 px-3 font-medium text-gray-600">Rate</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item: any, i: number) => (
              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-2 px-3 capitalize">{item.name ?? item.sector ?? `Sector ${i + 1}`}</td>
                <td className="py-2 px-3 text-right">{item.total_signals ?? item.count ?? 0}</td>
                <td className="py-2 px-3 text-right">{item.resolved_signals ?? item.resolved ?? 0}</td>
                <td className="py-2 px-3 text-right">{item.avg_resolution_time != null ? `${item.avg_resolution_time}h` : "—"}</td>
                <td className="py-2 px-3 text-right">{item.resolution_rate != null ? `${item.resolution_rate}%` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SatisfactionView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const dist = data.distribution ?? data.ratings ?? null;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Citizen Satisfaction</h3>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
        <MiniStat label="Avg Rating" value={data.avg_satisfaction != null ? `${data.avg_satisfaction}/5` : "—"} />
        <MiniStat label="Total Responses" value={String(data.total_responses ?? data.total ?? 0)} />
        <MiniStat label="Positive" value={data.positive_percentage != null ? `${data.positive_percentage}%` : "—"} />
        <MiniStat label="Neutral" value={data.neutral_percentage != null ? `${data.neutral_percentage}%` : "—"} />
        <MiniStat label="Negative" value={data.negative_percentage != null ? `${data.negative_percentage}%` : "—"} />
      </div>
      {dist && typeof dist === "object" && (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map(r => {
            const count = dist[r] ?? dist[`${r}_star`] ?? dist[`star_${r}`] ?? 0;
            const maxCount = Math.max(...[1, 2, 3, 4, 5].map(x => dist[x] ?? dist[`${x}_star`] ?? dist[`star_${x}`] ?? 0), 1);
            const colors = ["bg-red-500", "bg-orange-500", "bg-amber-500", "bg-lime-500", "bg-green-500"];
            return (
              <div key={r} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-16">{r} Star{r > 1 ? "s" : ""}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-3">
                  <div className={`h-full rounded-full ${colors[r - 1]}`} style={{ width: `${(count / maxCount) * 100}%` }} />
                </div>
                <span className="text-sm font-medium text-gray-600 w-8 text-right">{count}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ResponseTimesView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Response Times</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStat label="Avg Response" value={data.avg_response_time != null ? `${data.avg_response_time}h` : "—"} />
        <MiniStat label="Avg Resolution" value={data.avg_resolution_time != null ? `${data.avg_resolution_time}h` : "—"} />
        <MiniStat label="Median Response" value={data.median_response_time != null ? `${data.median_response_time}h` : "—"} />
        <MiniStat label="Max Response" value={data.max_response_time != null ? `${data.max_response_time}h` : "—"} />
      </div>
      {data.by_priority && (
        <div className="mt-4">
          <h4 className="text-xs font-semibold text-gray-600 mb-3">By Priority Level</h4>
          <div className="space-y-3">
            {Object.entries(data.by_priority).map(([level, d]: [string, any]) => (
              <div key={level} className="flex items-center gap-4">
                <span className="w-24 text-sm font-medium text-gray-600 capitalize">{level}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                  <div
                    className="h-2.5 rounded-full"
                    style={{
                      width: `${Math.min(100, d.avg_response_time * 5)}%`,
                      backgroundColor: level === "high" ? "#ef4444" : level === "medium" ? "#f59e0b" : "#3b82f6",
                    }}
                  />
                </div>
                <span className="text-sm text-gray-500 w-20 text-right">{d.avg_response_time}h avg</span>
                <span className="text-sm text-gray-500 w-20 text-right">{d.count} signals</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PredictionsView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const items = Array.isArray(data) ? data : data.predictions ?? data.data ?? [];
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Predictions</h3>
      {data.predicted_trend && (
        <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <MiniStat label="Predicted Trend" value={data.predicted_trend} />
          <MiniStat label="Confidence" value={data.confidence != null ? `${(data.confidence * 100).toFixed(1)}%` : "—"} />
          <MiniStat label="Expected Volume" value={String(data.expected_volume ?? data.predicted_count ?? "—")} />
        </div>
      )}
      {items.length > 0 && (
        <div className="space-y-2">
          {items.slice(0, 20).map((item: any, i: number) => (
            <div key={i} className="flex items-center gap-3 py-1.5 border-b border-gray-100 last:border-0">
              <span className="text-sm text-gray-700 flex-1 capitalize">{item.label ?? item.category ?? item.name ?? `Item ${i + 1}`}</span>
              <span className="text-sm font-medium text-gray-600">{item.predicted_count ?? item.count ?? item.value ?? 0}</span>
              {item.confidence != null && (
                <span className="text-xs text-gray-400">{(item.confidence * 100).toFixed(0)}%</span>
              )}
            </div>
          ))}
        </div>
      )}
      {!data.predicted_trend && items.length === 0 && (
        <p className="text-sm text-gray-400">No prediction data available for this period.</p>
      )}
    </div>
  );
}

function HotspotsView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const items = Array.isArray(data) ? data : data.hotspots ?? data.data ?? [];
  if (!items.length) return <EmptySection />;
  const maxDensity = Math.max(...items.map((h: any) => h.density ?? h.count ?? 0), 1);
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Hotspots</h3>
      <div className="space-y-2">
        {items.map((h: any, i: number) => {
          const density = h.density ?? h.count ?? 0;
          const pct = (density / maxDensity) * 100;
          const color = pct > 66 ? "#ef4444" : pct > 33 ? "#f59e0b" : "#3b82f6";
          return (
            <div key={i} className="flex items-center gap-3">
              <span className="text-sm text-gray-700 w-36 truncate shrink-0">
                {h.name ?? h.location ?? h.area ?? `Hotspot ${i + 1}`}
              </span>
              <div className="flex-1 bg-gray-100 rounded-full h-3">
                <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
              </div>
              <span className="text-xs font-medium text-gray-500 w-14 text-right">{density.toFixed(1)}</span>
            </div>
          );
        })}
      </div>
      {items.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> High</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Medium</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" /> Low</span>
          </div>
        </div>
      )}
    </div>
  );
}

function TemporalPatternsView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  const byHour = data.by_hour ?? data.hourly ?? null;
  const byDay = data.by_day_of_week ?? data.by_weekday ?? data.weekday ?? null;
  const byMonth = data.by_month ?? data.monthly ?? null;
  const hasAny = byHour || byDay || byMonth;
  if (!hasAny) {
    if (Array.isArray(data) && data.length > 0) {
      return (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Temporal Patterns</h3>
          {data.slice(0, 20).map((item: any, i: number) => (
            <div key={i} className="flex items-center gap-3 py-1.5 border-b border-gray-100 last:border-0">
              <span className="text-sm text-gray-700 flex-1">{item.label ?? item.period ?? item.time ?? `#${i + 1}`}</span>
              <span className="text-sm font-medium text-gray-600">{item.count ?? item.value ?? 0}</span>
            </div>
          ))}
        </div>
      );
    }
    return <EmptySection />;
  }
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Temporal Patterns</h3>
      {byHour && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-gray-600 mb-2">By Hour of Day</h4>
          <div className="grid grid-cols-12 gap-1">
            {Array.isArray(byHour) ? byHour.map((v: any, i: number) => {
              const count = typeof v === "number" ? v : v.count ?? v.value ?? 0;
              const maxVal = Math.max(...byHour.map((x: any) => typeof x === "number" ? x : x.count ?? x.value ?? 0), 1);
              return (
                <div key={i} className="flex flex-col items-center gap-0.5">
                  <div className="w-full bg-gray-100 rounded-sm" style={{ height: 32 }}>
                    <div className="bg-blue-500 rounded-sm" style={{ height: `${(count / maxVal) * 100}%`, width: "100%" }} />
                  </div>
                  <span className="text-[10px] text-gray-400">{i}h</span>
                </div>
              );
            }) : (
              <p className="text-sm text-gray-400">Hourly data available</p>
            )}
          </div>
        </div>
      )}
      {byDay && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-gray-600 mb-2">By Day of Week</h4>
          <div className="grid grid-cols-7 gap-2">
            {Array.isArray(byDay) ? byDay.map((v: any, i: number) => {
              const count = typeof v === "number" ? v : v.count ?? v.value ?? 0;
              const maxVal = Math.max(...byDay.map((x: any) => typeof x === "number" ? x : x.count ?? x.value ?? 0), 1);
              const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
              return (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div className="w-full bg-gray-100 rounded-sm" style={{ height: 40 }}>
                    <div className="bg-teal-500 rounded-sm" style={{ height: `${(count / maxVal) * 100}%`, width: "100%" }} />
                  </div>
                  <span className="text-[10px] text-gray-400">{days[i]}</span>
                  <span className="text-[10px] font-medium text-gray-500">{count}</span>
                </div>
              );
            }) : (
              <p className="text-sm text-gray-400 text-center col-span-7">Weekly data available</p>
            )}
          </div>
        </div>
      )}
      {byMonth && (
        <div>
          <h4 className="text-xs font-semibold text-gray-600 mb-2">By Month</h4>
          <div className="grid grid-cols-6 md:grid-cols-12 gap-2">
            {Array.isArray(byMonth) ? byMonth.map((v: any, i: number) => {
              const count = typeof v === "number" ? v : v.count ?? v.value ?? 0;
              const maxVal = Math.max(...byMonth.map((x: any) => typeof x === "number" ? x : x.count ?? x.value ?? 0), 1);
              const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
              return (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div className="w-full bg-gray-100 rounded-sm" style={{ height: 36 }}>
                    <div className="bg-purple-500 rounded-sm" style={{ height: `${(count / maxVal) * 100}%`, width: "100%" }} />
                  </div>
                  <span className="text-[10px] text-gray-400">{months[i] ?? i + 1}</span>
                  <span className="text-[10px] font-medium text-gray-500">{count}</span>
                </div>
              );
            }) : (
              <p className="text-sm text-gray-400 text-center col-span-12">Monthly data available</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryReportView({ data }: { data: any }) {
  if (!data) return <EmptySection />;
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Summary Report</h3>
      <div className="prose prose-sm max-w-none text-gray-600">
        {data.summary && <p className="text-sm leading-relaxed mb-4 whitespace-pre-line">{data.summary}</p>}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          {data.total_signals != null && <StatBox label="Total Signals" value={String(data.total_signals)} />}
          {data.total_open != null && <StatBox label="Open" value={String(data.total_open)} />}
          {data.total_resolved != null && <StatBox label="Resolved" value={String(data.total_resolved)} />}
          {data.resolution_rate != null && <StatBox label="Resolution Rate" value={`${data.resolution_rate}%`} />}
          {data.avg_response_time != null && <StatBox label="Avg Response" value={`${data.avg_response_time}h`} />}
          {data.avg_resolution_time != null && <StatBox label="Avg Resolution" value={`${data.avg_resolution_time}h`} />}
          {data.avg_satisfaction != null && <StatBox label="Avg Satisfaction" value={`${data.avg_satisfaction}/5`} />}
          {data.total_sectors != null && <StatBox label="Active Sectors" value={String(data.total_sectors)} />}
          {data.total_categories != null && <StatBox label="Categories" value={String(data.total_categories)} />}
          {data.peak_hours && <StatBox label="Peak Hours" value={String(data.peak_hours)} />}
        </div>
        {data.highlights && Array.isArray(data.highlights) && data.highlights.length > 0 && (
          <div className="mt-4">
            <h4 className="text-xs font-semibold text-gray-600 mb-2">Highlights</h4>
            <ul className="list-disc list-inside space-y-1">
              {data.highlights.map((h: any, i: number) => (
                <li key={i} className="text-sm text-gray-600">{typeof h === "string" ? h : h.message ?? h.text ?? String(h)}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function EmptySection() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
      <p className="text-sm text-gray-400">No data available for this section.</p>
    </div>
  );
}

function KPICard({ label, value, color }: { label: string; value: string | number; color: string }) {
  const colors: Record<string, string> = {
    blue: "border-blue-200 bg-blue-50 text-blue-700",
    amber: "border-amber-200 bg-amber-50 text-amber-700",
    green: "border-green-200 bg-green-50 text-green-700",
    purple: "border-purple-200 bg-purple-50 text-purple-700",
  };
  return (
    <div className={`rounded-lg border p-4 ${colors[color] || colors.blue}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs font-medium opacity-75 mt-0.5">{label}</div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <div className="text-lg font-semibold text-gray-800">{value}</div>
      <div className="text-xs text-gray-500 mt-0.5">{label}</div>
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
