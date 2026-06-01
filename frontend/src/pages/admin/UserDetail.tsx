import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { users } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import StatusBadge from "../../components/ui/StatusBadge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import { useToast } from "../../contexts/ToastContext";
import type { User, Signal, UserStats as UserStatsType } from "../../types";

export default function UserDetail() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const uid = Number(userId);

  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<UserStatsType | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [tab, setTab] = useState<"overview" | "signals">("overview");

  useEffect(() => {
    if (!uid) return;
    setLoading(true);
    Promise.all([
      users.get(uid),
      users.getStats(uid).catch(() => ({ data: { data: null as any } })),
      users.getSignals(uid, { size: 20 }).catch(() => ({ data: { data: { items: [] } } })),
    ])
      .then(([uRes, sRes, sigRes]) => {
        setUser(uRes.data.data ?? null);
        setStats(sRes.data.data);
        setSignals(sigRes.data.data?.items ?? []);
      })
      .catch(() => toast("Failed to load user details", "error"))
      .finally(() => setLoading(false));
  }, [uid, toast]);

  const handleToggleStatus = async () => {
    if (!user) return;
    setActionLoading(true);
    try {
      if (user.status === "ACTIVE") await users.deactivate(user.id);
      else await users.activate(user.id);
      const res = await users.get(user.id);
      setUser(res.data.data ?? null);
      toast(`User ${user.status === "ACTIVE" ? "deactivated" : "activated"}`, "success");
    } catch { toast("Action failed", "error"); } finally { setActionLoading(false); }
  };

  const handleDelete = async () => {
    if (!user || !confirm("Permanently delete this user?")) return;
    setActionLoading(true);
    try {
      await users.delete(user.id);
      toast("User deleted", "success");
      navigate("/admin/users");
    } catch { toast("Delete failed", "error"); } finally { setActionLoading(false); }
  };

  const columns: Column<Signal>[] = [
    { key: "reference_number", header: "Ref", render: (s) => <span className="font-mono text-xs">{s.reference_number}</span> },
    { key: "title", header: "Title" },
    { key: "status", header: "Status", render: (s) => <StatusBadge status={s.status} /> },
    { key: "created_at", header: "Created", render: (s) => new Date(s.created_at).toLocaleDateString() },
  ];

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;
  if (!user) return <div className="text-center py-20 text-gray-500">User not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{user.first_name} {user.last_name}</h1>
          <p className="text-sm text-gray-500">{user.email} &middot; @{user.username}</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleToggleStatus} disabled={actionLoading}
            className={`px-4 py-2 text-sm rounded-lg text-white ${user.status === "ACTIVE" ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"} disabled:opacity-50`}>
            {actionLoading ? "..." : user.status === "ACTIVE" ? "Deactivate" : "Activate"}
          </button>
          <button onClick={handleDelete} disabled={actionLoading} className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 disabled:opacity-50">
            {actionLoading ? "..." : "Delete"}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-6">
          {(["overview", "signals"] as const).map((t) => (
            <button key={t} onClick={() => setTab(t)}
              className={`pb-3 text-sm font-medium border-b-2 ${tab === t ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
              {t === "overview" ? "Overview" : `Signals (${signals.length})`}
            </button>
          ))}
        </nav>
      </div>

      {tab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <h2 className="text-lg font-semibold">User Information</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <InfoRow label="User ID" value={String(user.id)} />
              <InfoRow label="Role" value={<span className="uppercase font-medium">{user.role}</span>} />
              <InfoRow label="Status" value={<StatusBadge status={user.status} />} />
              <InfoRow label="Email Verified" value={user.is_email_verified ? "Yes" : "No"} />
              <InfoRow label="Phone" value={user.phone_number || "-"} />
              <InfoRow label="City" value={user.city || "-"} />
              <InfoRow label="Joined" value={user.created_at ? new Date(user.created_at).toLocaleDateString() : "-"} />
              <InfoRow label="Last Login" value={user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "Never"} />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <h2 className="text-lg font-semibold">Statistics</h2>
            {stats ? (
              <div className="space-y-3 text-sm">
                <InfoRow label="Signals Created" value={String(stats.total_signals_created)} />
                <InfoRow label="Signals Processed" value={String(stats.total_signals_processed)} />
                <InfoRow label="Avg Resolution" value={`${stats.avg_resolution_time_hours?.toFixed(1) || "-"}h`} />
                <InfoRow label="Satisfaction" value={stats.citizen_satisfaction_rate ? `${stats.citizen_satisfaction_rate}/5` : "-"} />
              </div>
            ) : (
              <p className="text-sm text-gray-500">Stats unavailable</p>
            )}
          </div>
        </div>
      )}

      {tab === "signals" && (
        <DataTable
          columns={columns}
          data={signals}
          emptyTitle="No signals from this user"
          keyExtractor={(s) => s.id}
          onRowClick={(s) => navigate(`/signals/${s.id}`)}
        />
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-gray-100 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
