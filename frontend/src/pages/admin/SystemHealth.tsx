import { useSystemHealth } from "../../hooks/useAdmin";
import LoadingSpinner from "../../components/ui/LoadingSpinner";

export default function SystemHealth() {
  const { health, config, loading } = useSystemHealth();

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">System Health</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Health Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Health Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <span className="text-sm text-gray-600">Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${health?.status === "healthy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                {health?.status || "unknown"}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <span className="text-sm text-gray-600">Database</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${health?.database === "healthy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                {health?.database || "unknown"}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <span className="text-sm text-gray-600">Version</span>
              <span className="font-mono text-sm">{health?.version || "-"}</span>
            </div>
          </div>
        </div>

        {/* Config */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration</h2>
          {config ? (
            <div className="space-y-3 text-sm">
              <ConfigRow label="App Name" value={config.app_name} />
              <ConfigRow label="Version" value={config.app_version} />
              <ConfigRow label="Environment" value={config.environment} />
              <ConfigRow label="Debug Mode" value={String(config.debug)} />
              <ConfigRow label="Auth Token Expiry" value={`${config.access_token_expire_minutes} min`} />
              <ConfigRow label="Refresh Token Expiry" value={`${config.refresh_token_expire_days} days`} />
              <ConfigRow label="AI Confidence Threshold" value={String(config.ai_confidence_threshold)} />
              <ConfigRow label="Max File Size" value={`${(config.max_file_size / 1024 / 1024).toFixed(0)} MB`} />
              <ConfigRow label="Rate Limit" value={`${config.rate_limit_per_minute}/min`} />
              <ConfigRow label="Allowed Origins" value={config.allowed_origins?.join(", ")} />
            </div>
          ) : (
            <p className="text-gray-500">Config unavailable</p>
          )}
        </div>
      </div>
    </div>
  );
}

function ConfigRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-gray-100 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-800 text-right max-w-[60%] truncate" title={value}>{value}</span>
    </div>
  );
}
