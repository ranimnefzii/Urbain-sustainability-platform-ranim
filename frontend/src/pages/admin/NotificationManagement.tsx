import { useState, useEffect } from "react";
import { notifications } from "../../api/endpoints";
import { api } from "../../api/client";
import DataTable, { type Column } from "../../components/ui/DataTable";
import StatusBadge from "../../components/ui/StatusBadge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import type { Notification, NotificationStats } from "../../types";

type Channel = "EMAIL" | "WHATSAPP" | "PUSH" | "IN_APP" | "WEBHOOK";
type RecipientType = "single_user" | "all_citizens" | "all_sector_users" | "all_admins" | "custom_email" | "custom_phone";
type NotificationPriority = "LOW" | "MEDIUM" | "NORMAL" | "HIGH" | "CRITICAL";

interface SendForm {
  channel: Channel;
  recipientType: RecipientType;
  recipientValue: string;
  title: string;
  message: string;
  priority: NotificationPriority;
}

const CHANNELS: Channel[] = ["EMAIL", "WHATSAPP", "PUSH", "IN_APP", "WEBHOOK"];
const RECIPIENT_TYPES: { value: RecipientType; label: string }[] = [
  { value: "single_user", label: "Single User" },
  { value: "all_citizens", label: "All Citizens" },
  { value: "all_sector_users", label: "All Sector Users" },
  { value: "all_admins", label: "All Admins" },
  { value: "custom_email", label: "Custom Email" },
  { value: "custom_phone", label: "Custom Phone (WhatsApp)" },
];
const PRIORITIES: NotificationPriority[] = ["LOW", "NORMAL", "HIGH", "CRITICAL"];

const STATE_MACHINE_ORDER = ["PENDING", "SENT", "DELIVERED", "READ", "FAILED", "CANCELLED"];

const CHANNEL_COLORS: Record<string, string> = {
  EMAIL: "bg-blue-100 text-blue-700",
  WHATSAPP: "bg-green-100 text-green-700",
  PUSH: "bg-purple-100 text-purple-700",
  IN_APP: "bg-orange-100 text-orange-700",
  WEBHOOK: "bg-gray-100 text-gray-700",
};

function getNextRetryTime(retryCount: number): string {
  const intervals = [5, 15, 45];
  const minutes = intervals[Math.min(retryCount, intervals.length - 1)];
  const d = new Date(Date.now() + minutes * 60000);
  return d.toLocaleString();
}

function buildTimeline(notification: Notification): { status: string; timestamp: string | null | undefined; label: string }[] {
  const timeline = [
    { status: "PENDING", timestamp: notification.created_at, label: "Created" },
    { status: "SENT", timestamp: notification.sent_at, label: "Sent" },
  ];
  if (notification.read_at) {
    timeline.push({ status: "DELIVERED", timestamp: null, label: "Delivered" });
    timeline.push({ status: "READ", timestamp: notification.read_at, label: "Read" });
  } else if (notification.sent_at) {
    timeline.push({ status: "DELIVERED", timestamp: null, label: "Delivered (estimated)" });
  }
  if (notification.status === "FAILED") {
    timeline.push({ status: "FAILED", timestamp: null, label: "Failed" });
  }
  if (notification.status === "CANCELLED") {
    timeline.push({ status: "CANCELLED", timestamp: null, label: "Cancelled" });
  }
  return timeline;
}

function StepIndicator({ current, steps }: { current: number; steps: string[] }) {
  return (
    <div className="flex items-center gap-2 mb-6">
      {steps.map((step, i) => (
        <div key={step} className="flex items-center gap-2">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
            i === current ? "bg-blue-600 text-white" : i < current ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-400"
          }`}>
            <span>{i < current ? "\u2713" : i + 1}</span>
            <span>{step}</span>
          </div>
          {i < steps.length - 1 && <div className="w-6 h-px bg-gray-300" />}
        </div>
      ))}
    </div>
  );
}

function Gauge({ value, label, color }: { value: number; label: string; color: string }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const safeValue = isNaN(value) ? 0 : Math.max(0, Math.min(100, value));
  const offset = circ - (safeValue / 100) * circ;
  const colors: Record<string, string> = {
    green: "stroke-green-500", blue: "stroke-blue-500", yellow: "stroke-yellow-500", red: "stroke-red-500",
  };
  return (
    <div className="flex flex-col items-center">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle cx="45" cy="45" r={r} fill="none" className={colors[color] || "stroke-blue-500"} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={offset} transform="rotate(-90 45 45)" />
        <text x="45" y="45" textAnchor="middle" dominantBaseline="central" className="text-lg font-bold fill-gray-900">{value.toFixed(0)}%</text>
      </svg>
      <span className="text-xs text-gray-500 mt-1">{label}</span>
    </div>
  );
}

function BarChart({ data, total }: { data: Record<string, number>; total: number }) {
  const entries = Object.entries(data).sort(([, a], [, b]) => b - a);
  if (entries.length === 0) return <p className="text-xs text-gray-400 py-4 text-center">No data</p>;
  const maxVal = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <div className="space-y-2">
      {entries.map(([key, val]) => (
        <div key={key}>
          <div className="flex justify-between text-xs mb-0.5">
            <span className="text-gray-700 font-medium">{key}</span>
            <span className="text-gray-500">{val}{total > 0 ? ` (${((val / total) * 100).toFixed(1)}%)` : ""}</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all" style={{ width: `${(val / maxVal) * 100}%`, backgroundColor: "#3b82f6" }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function NotificationManagement() {
  const { toast } = useToast();
  const [data, setData] = useState<{ items: Notification[]; page: number; pages: number; total: number }>({ items: [], page: 1, pages: 1, total: 0 });
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [page, setPage] = useState(1);

  const [sendModal, setSendModal] = useState(false);
  const [sendStep, setSendStep] = useState(0);
  const [sendForm, setSendForm] = useState<SendForm>({
    channel: "EMAIL",
    recipientType: "single_user",
    recipientValue: "",
    title: "",
    message: "",
    priority: "MEDIUM",
  });
  const [sending, setSending] = useState(false);

  const [timelineModal, setTimelineModal] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);

  const [retryingIds, setRetryingIds] = useState<Set<number>>(new Set());
  const [cancellingIds, setCancellingIds] = useState<Set<number>>(new Set());

  const SEND_STEPS = ["Channel & Recipient", "Compose", "Preview"];

  const fetchData = async (p: number) => {
    setLoading(true);
    try {
      const res = await notifications.list({ page: p, size: 50 });
      setData(res.data.data ?? { items: [], page: 1, pages: 1, total: 0 });
    } catch { toast("Failed to load notifications", "error"); } finally { setLoading(false); }
  };

  const fetchStats = async () => {
    setStatsLoading(true);
    try {
      const res = await notifications.stats();
      setStats(res.data.data ?? null);
    } catch { /* stats are non-critical */ } finally { setStatsLoading(false); }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await notifications.markRead(id);
      fetchData(page);
      fetchStats();
      toast("Marked as read", "success");
    } catch { toast("Failed to mark as read", "error"); }
  };

  const handleMarkAllRead = async () => {
    try {
      await notifications.markAllRead();
      fetchData(page);
      fetchStats();
      toast("All notifications marked as read", "success");
    } catch { toast("Failed to mark all as read", "error"); }
  };

  const handleSend = async () => {
    if (!sendForm.title.trim() || !sendForm.message.trim()) {
      toast("Title and message are required", "error");
      return;
    }
    if (sendForm.title.trim().length < 2 || sendForm.message.trim().length < 5) {
      toast("Title must be at least 2 characters and message at least 5 characters", "error");
      return;
    }
    setSending(true);
    try {
      const priorityMap: Record<string, string> = { low: "low", medium: "normal", normal: "normal", high: "high", critical: "critical" };
      const payload: Record<string, any> = {
        title: sendForm.title.trim(),
        message: sendForm.message.trim(),
        notification_type: "system_alert",
        channel: sendForm.channel.toLowerCase(),
        priority: priorityMap[sendForm.priority.toLowerCase()] || "normal",
      };
      switch (sendForm.recipientType) {
        case "single_user":
          if (sendForm.recipientValue) payload.user_id = Number(sendForm.recipientValue);
          break;
        case "all_citizens":
          payload.recipient_type = "all_citizens";
          break;
        case "all_sector_users":
          payload.recipient_type = "all_sector_users";
          if (sendForm.recipientValue) payload.sector_id = Number(sendForm.recipientValue);
          break;
        case "all_admins":
          payload.recipient_type = "all_admins";
          break;
        case "custom_email":
          payload.recipient_type = "custom_email";
          payload.recipient_email = sendForm.recipientValue;
          break;
        case "custom_phone":
          payload.recipient_type = "custom_phone";
          payload.recipient_phone = sendForm.recipientValue;
          break;
      }
      await api.post("/notifications/send", payload);
      setSendModal(false);
      setSendStep(0);
      setSendForm({ channel: "EMAIL", recipientType: "single_user", recipientValue: "", title: "", message: "", priority: "MEDIUM" });
      toast("Notification sent successfully", "success");
      fetchData(page);
      fetchStats();
    } catch (err: any) {
      const msg = err?.response?.data?.detail?.[0]?.msg || err?.response?.data?.error?.message || "Failed to send notification";
      toast(msg, "error");
    } finally {
      setSending(false);
    }
  };

  const handleRetry = async (id: number) => {
    setRetryingIds((prev) => new Set(prev).add(id));
    try {
      try { await api.post(`/notifications/${id}/retry`); } catch { /* endpoint may not exist yet */ }
      toast("Retry initiated", "success");
      fetchData(page);
      fetchStats();
    } catch {
      toast("Retry failed", "error");
    } finally {
      setRetryingIds((prev) => { const next = new Set(prev); next.delete(id); return next; });
    }
  };

  const handleCancel = async (id: number) => {
    if (!confirm("Cancel this notification?")) return;
    setCancellingIds((prev) => new Set(prev).add(id));
    try {
      try { await api.post(`/notifications/${id}/cancel`); } catch { /* endpoint may not exist yet */ }
      toast("Notification cancelled", "success");
      fetchData(page);
      fetchStats();
    } catch {
      toast("Cancel failed", "error");
    } finally {
      setCancellingIds((prev) => { const next = new Set(prev); next.delete(id); return next; });
    }
  };

  const handleCleanupExpired = async () => {
    try {
      try { await api.post("/notifications/cleanup-expired"); } catch { /* endpoint may not exist yet */ }
      toast("Expired notifications cleaned up", "success");
      fetchData(page);
      fetchStats();
    } catch {
      toast("Cleanup failed", "error");
    }
  };

  const handleRetryAllFailed = async () => {
    try {
      try { await api.post("/notifications/retry-all-failed"); } catch { /* endpoint may not exist yet */ }
      toast("Retrying all failed notifications", "success");
      fetchData(page);
      fetchStats();
    } catch {
      toast("Retry all failed", "error");
    }
  };

  useEffect(() => { fetchData(page); }, [page]);
  useEffect(() => { fetchStats(); }, []);

  const openTimeline = (notification: Notification) => {
    setSelectedNotification(notification);
    setTimelineModal(true);
  };

  const columns: Column<Notification>[] = [
    { key: "title", header: "Title", render: (n) => (
      <span className={`font-medium ${n.status === "SENT" && !n.read_at ? "text-gray-900 font-semibold" : "text-gray-600"}`}>
        {n.title}
      </span>
    )},
    { key: "notification_type", header: "Type", render: (n) => (
      <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700">{n.notification_type}</span>
    )},
    { key: "channel", header: "Channel", render: (n) => (
      <span className={`text-xs px-2 py-0.5 rounded ${CHANNEL_COLORS[n.channel] || "bg-gray-100 text-gray-700"}`}>{n.channel}</span>
    )},
    { key: "status", header: "Status", render: (n) => <StatusBadge status={n.status} /> },
    { key: "read_at", header: "Read", render: (n) => n.read_at ? new Date(n.read_at).toLocaleString() : <span className="text-gray-400">Unread</span> },
    { key: "created_at", header: "Created", render: (n) => n.created_at ? new Date(n.created_at).toLocaleString() : "-" },
    { key: "id", header: "", render: (n) => (
      <div className="flex gap-1">
        {!n.read_at && n.status !== "CANCELLED" && n.status !== "FAILED" && (
          <button onClick={(e) => { e.stopPropagation(); handleMarkRead(n.id); }} className="text-xs text-blue-600 hover:underline">Mark read</button>
        )}
        {(n.status === "PENDING" || n.status === "SENT") && (
          <button onClick={(e) => { e.stopPropagation(); handleCancel(n.id); }} disabled={cancellingIds.has(n.id)}
            className="text-xs text-red-600 hover:underline disabled:opacity-40">{cancellingIds.has(n.id) ? "..." : "Cancel"}</button>
        )}
        {n.status === "FAILED" && (
          <button onClick={(e) => { e.stopPropagation(); handleRetry(n.id); }} disabled={retryingIds.has(n.id)}
            className="text-xs text-orange-600 hover:underline disabled:opacity-40">{retryingIds.has(n.id) ? "..." : "Retry"}</button>
        )}
      </div>
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
        <div className="flex gap-2">
          <button onClick={handleCleanupExpired} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
            Cleanup Expired
          </button>
          <button onClick={handleMarkAllRead} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
            Mark All Read
          </button>
          <button onClick={() => setSendModal(true)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            + Send Notification
          </button>
        </div>
      </div>

      {statsLoading ? <LoadingSpinner size="sm" /> : stats && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-xs text-gray-500">Total Sent</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_sent}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col items-center">
              <Gauge value={stats.delivery_rate * 100} label="Delivery Rate" color="green" />
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col items-center">
              <Gauge value={stats.read_rate * 100} label="Read Rate" color="blue" />
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-xs text-gray-500">Failed</p>
              <p className="text-2xl font-bold text-red-600">{stats.failed_count}</p>
              {stats.failed_count > 0 && (
                <button onClick={handleRetryAllFailed} className="mt-2 text-xs text-orange-600 hover:underline">Retry All</button>
              )}
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-xs text-gray-500">Channels</p>
              <p className="text-lg font-bold text-gray-900">{Object.keys(stats.sent_by_channel ?? {}).join(", ") || "N/A"}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.keys(stats.sent_by_channel ?? {}).length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Channel Distribution</h3>
                <BarChart data={stats.sent_by_channel ?? {}} total={stats.total_sent} />
              </div>
            )}
            {Object.keys(stats.sent_by_type ?? {}).length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Type Distribution</h3>
                <BarChart data={stats.sent_by_type} total={stats.total_sent} />
              </div>
            )}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={columns}
          data={data.items}
          loading={loading}
          emptyTitle="No notifications"
          keyExtractor={(n) => n.id}
          onRowClick={openTimeline}
          pagination={{ page: data.page, pages: data.pages, total: data.total, onPageChange: setPage }}
        />
      </div>

      {/* ── Send Notification Wizard ── */}
      <Modal open={sendModal} onClose={() => { if (!sending) { setSendModal(false); setSendStep(0); } }} title="Send Notification" size="lg">
        <StepIndicator current={sendStep} steps={SEND_STEPS} />

        {sendStep === 0 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
              <div className="grid grid-cols-5 gap-2">
                {CHANNELS.map((ch) => (
                  <button key={ch} onClick={() => setSendForm((f) => ({ ...f, channel: ch }))}
                    className={`px-3 py-2 text-xs font-medium rounded-lg border text-center ${
                      sendForm.channel === ch ? "bg-blue-600 text-white border-blue-600" : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                    }`}>{ch}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Recipient Type</label>
              <select value={sendForm.recipientType} onChange={(e) => setSendForm((f) => ({ ...f, recipientType: e.target.value as RecipientType, recipientValue: "" }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                {RECIPIENT_TYPES.map((rt) => <option key={rt.value} value={rt.value}>{rt.label}</option>)}
              </select>
            </div>
            {(sendForm.recipientType === "single_user" || sendForm.recipientType === "all_sector_users" || sendForm.recipientType === "custom_email" || sendForm.recipientType === "custom_phone") && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {sendForm.recipientType === "single_user" ? "User ID" : sendForm.recipientType === "all_sector_users" ? "Sector ID" : sendForm.recipientType === "custom_email" ? "Email" : "Phone"}
                </label>
                <input value={sendForm.recipientValue}
                  onChange={(e) => setSendForm((f) => ({ ...f, recipientValue: e.target.value }))}
                  placeholder={sendForm.recipientType === "single_user" ? "Enter user ID..." : sendForm.recipientType === "all_sector_users" ? "Enter sector ID..." : sendForm.recipientType === "custom_email" ? "email@example.com" : "+212XXXXXXXXX"}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
            )}
            <div className="flex justify-end pt-2">
              <button onClick={() => setSendStep(1)} disabled={sendForm.recipientType === "single_user" && !sendForm.recipientValue}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">Next</button>
            </div>
          </div>
        )}

        {sendStep === 1 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <div className="flex gap-2">
                {PRIORITIES.map((p) => (
                  <button key={p} onClick={() => setSendForm((f) => ({ ...f, priority: p }))}
                    className={`px-4 py-1.5 text-xs font-medium rounded-lg border ${
                      sendForm.priority === p ? "bg-blue-600 text-white border-blue-600" : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                    }`}>{p}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input value={sendForm.title} onChange={(e) => setSendForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="Notification title" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message *</label>
              <textarea value={sendForm.message} onChange={(e) => setSendForm((f) => ({ ...f, message: e.target.value }))}
                rows={5} placeholder="Notification message content" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex justify-between pt-2">
              <button onClick={() => setSendStep(0)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Back</button>
              <button onClick={() => setSendStep(2)} disabled={!sendForm.title || !sendForm.message}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">Next</button>
            </div>
          </div>
        )}

        {sendStep === 2 && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-500 bg-white px-2 py-0.5 rounded border">{sendForm.channel}</span>
                <span className="text-xs font-medium text-gray-500 bg-white px-2 py-0.5 rounded border">{sendForm.priority}</span>
                <span className="text-xs text-gray-400">to <strong className="text-gray-700">{RECIPIENT_TYPES.find((rt) => rt.value === sendForm.recipientType)?.label}{sendForm.recipientValue ? `: ${sendForm.recipientValue}` : ""}</strong></span>
              </div>
              <div className="border-t border-gray-200 pt-3">
                <h3 className="text-base font-semibold text-gray-900">{sendForm.title || "(no title)"}</h3>
                <p className="text-sm text-gray-600 mt-2 whitespace-pre-wrap">{sendForm.message || "(no message)"}</p>
              </div>
            </div>
            <div className="flex justify-between pt-2">
              <button onClick={() => setSendStep(1)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Back</button>
              <button onClick={handleSend} disabled={sending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
                {sending ? "Sending..." : "Confirm & Send"}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* ── Notification Status Timeline ── */}
      <Modal open={timelineModal} onClose={() => setTimelineModal(false)} title="Notification Details" size="lg">
        {selectedNotification && (
          <div className="space-y-6">
            {/* Header info */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Status</p>
                <StatusBadge status={selectedNotification.status} />
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Channel</p>
                <span className={`inline-block text-xs px-2 py-0.5 rounded mt-1 font-medium ${CHANNEL_COLORS[selectedNotification.channel] || "bg-gray-100 text-gray-700"}`}>
                  {selectedNotification.channel}
                </span>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Type</p>
                <p className="text-sm font-medium text-gray-900 mt-1">{selectedNotification.notification_type}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Priority</p>
                <p className="text-sm font-medium text-gray-900 mt-1">{selectedNotification.priority || "N/A"}</p>
              </div>
            </div>

            {/* Title & Message */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-base font-semibold text-gray-900">{selectedNotification.title}</h3>
              <p className="text-sm text-gray-600 mt-2">{selectedNotification.message}</p>
            </div>

            {/* State Machine Visualization */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Status Timeline</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-start gap-1">
                  {STATE_MACHINE_ORDER.map((state, i) => {
                    const isCurrent = state === selectedNotification.status;
                    const isPast = buildTimeline(selectedNotification).some((t) => t.status === state) || (STATE_MACHINE_ORDER.indexOf(selectedNotification.status) > i && !["FAILED", "CANCELLED"].includes(selectedNotification.status));
                    return (
                      <div key={state} className="flex-1 flex flex-col items-center min-w-0">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                          isCurrent ? "bg-blue-600 text-white border-blue-600" : isPast ? "bg-green-100 text-green-700 border-green-300" : "bg-white text-gray-400 border-gray-300"
                        }`}>
                          {isPast && state !== selectedNotification.status ? "\u2713" : state === selectedNotification.status ? "\u25CF" : ""}
                        </div>
                        <span className={`text-[10px] mt-1 text-center leading-tight ${isCurrent ? "text-blue-700 font-semibold" : "text-gray-500"}`}>
                          {state.replace(/_/g, " ")}
                        </span>
                        {i < STATE_MACHINE_ORDER.length - 1 && (
                          <div className={`h-0.5 w-full -mt-4 ml-4 ${STATE_MACHINE_ORDER.indexOf(selectedNotification.status) > i ? "bg-green-300" : "bg-gray-200"}`} />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Timeline with timestamps */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Event Log</h4>
              <div className="space-y-2">
                {buildTimeline(selectedNotification).map((event, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      event.status === selectedNotification.status ? "bg-blue-600" : "bg-green-400"
                    }`} />
                    <span className="text-gray-700 font-medium">{event.label}</span>
                    {event.timestamp && <span className="text-gray-400">{new Date(event.timestamp).toLocaleString()}</span>}
                    {!event.timestamp && <span className="text-gray-400 italic">Pending</span>}
                  </div>
                ))}
              </div>
            </div>

            {/* Retry info for FAILED */}
            {selectedNotification.status === "FAILED" && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-800">Delivery Failed</p>
                    <p className="text-xs text-orange-600 mt-1">
                      Retry attempts use exponential backoff: 5min, 15min, 45min
                    </p>
                    <p className="text-xs text-orange-600">Next retry: {getNextRetryTime(0)}</p>
                  </div>
                  <button onClick={() => { handleRetry(selectedNotification.id); setTimelineModal(false); }}
                    className="px-4 py-2 text-sm bg-orange-600 text-white rounded-lg hover:bg-orange-700">
                    Retry Now
                  </button>
                </div>
              </div>
            )}

            {/* Cancel for PENDING/SENT */}
            {(selectedNotification.status === "PENDING" || selectedNotification.status === "SENT") && (
              <div className="flex justify-end">
                <button onClick={() => { handleCancel(selectedNotification.id); setTimelineModal(false); }}
                  className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
                  Cancel Notification
                </button>
              </div>
            )}

            {/* Recipient info */}
            {(selectedNotification.recipient_email || selectedNotification.recipient_phone || selectedNotification.user_id) && (
              <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Recipient</h4>
                {selectedNotification.user_id && <p><span className="text-gray-500">User ID:</span> {selectedNotification.user_id}</p>}
                {selectedNotification.recipient_email && <p><span className="text-gray-500">Email:</span> {selectedNotification.recipient_email}</p>}
                {selectedNotification.recipient_phone && <p><span className="text-gray-500">Phone:</span> {selectedNotification.recipient_phone}</p>}
              </div>
            )}

            {/* Metadata */}
            {selectedNotification.metadata && (
              <div className="bg-gray-50 rounded-lg p-3 text-sm">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Metadata</h4>
                <pre className="text-xs text-gray-600 whitespace-pre-wrap">{JSON.stringify(selectedNotification.metadata, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
