import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { notifications, admin } from "../../api/endpoints";
import type { Notification, AdminDashboard } from "../../types";

interface ActionItem {
  id: string;
  type: "notification" | "escalation" | "overdue" | "pending_review";
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  link: string;
  actionable: boolean;
  onAction?: () => void;
}

export default function ActionCenter() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ActionItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [notifRes, adminRes] = await Promise.all([
          notifications.list({ size: 20, status: "SENT" }).catch(() => ({ data: { data: { items: [] } } })),
          admin.dashboard().catch(() => ({ data: { data: null } })),
        ]);

        const notifs: Notification[] = notifRes.data.data?.items ?? [];
        const dash = adminRes.data.data as AdminDashboard | null;

        const result: ActionItem[] = [];

        // Unread notifications
        const unreadNotifs = notifs.filter((n) => !n.read_at).slice(0, 5);
        unreadNotifs.forEach((n) => {
          result.push({
            id: `notif-${n.id}`,
            type: "notification",
            title: n.title,
            description: n.message.length > 80 ? n.message.slice(0, 80) + "..." : n.message,
            priority: n.priority === "URGENT" || n.priority === "HIGH" ? "high" : "medium",
            link: n.signal_id ? `/signals/${n.signal_id}` : "/admin/notifications",
            actionable: true,
            onAction: async () => {
              try {
                await notifications.markRead(n.id);
              } catch {}
              navigate(n.signal_id ? `/signals/${n.signal_id}` : "/admin/notifications");
            },
          });
        });

        // Escalation/overdue from dashboard stats
        if (dash?.signals_by_status) {
          const pendingReview = (dash.signals_by_status["SUBMITTED"] || 0) +
            (dash.signals_by_status["UNDER_REVIEW"] || 0);
          if (pendingReview > 0) {
            result.push({
              id: "pending-review",
              type: "pending_review",
              title: `${pendingReview} signal${pendingReview > 1 ? "s" : ""} pending review`,
              description: "Signals waiting for initial assessment and assignment",
              priority: "medium",
              link: "/signals?status=SUBMITTED",
              actionable: true,
              onAction: () => navigate("/signals?status=SUBMITTED"),
            });
          }
        }

        setItems(result);
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [navigate]);

  if (loading) return null;
  if (items.length === 0) return null;

  const highPriority = items.filter((i) => i.priority === "high");

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900">Action Center</h3>
        {highPriority.length > 0 && (
          <span className="text-xs font-bold bg-red-100 text-red-700 px-1.5 py-0.5 rounded">
            {highPriority.length} urgent
          </span>
        )}
      </div>

      <div className="space-y-1.5">
        {items.map((item) => (
          <div
            key={item.id}
            className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer text-sm transition-colors ${
              item.priority === "high"
                ? "bg-red-50 hover:bg-red-100 border border-red-100"
                : item.priority === "medium"
                ? "bg-yellow-50 hover:bg-yellow-100 border border-yellow-100"
                : "bg-gray-50 hover:bg-gray-100 border border-gray-100"
            }`}
            onClick={() => item.onAction ? item.onAction() : navigate(item.link)}
          >
            <div className={`h-2 w-2 rounded-full flex-shrink-0 ${
              item.priority === "high" ? "bg-red-500" :
              item.priority === "medium" ? "bg-yellow-500" : "bg-blue-500"
            }`} />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate">{item.title}</p>
              <p className="text-[10px] text-gray-500 truncate">{item.description}</p>
            </div>
            {item.actionable && (
              <svg className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
