import { useState, useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { notifications } from "../../api/endpoints";
import type { Notification } from "../../types";

interface NavbarProps {
  onMenuToggle: () => void;
}

export default function Navbar({ onMenuToggle }: NavbarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifList, setNotifList] = useState<Notification[]>([]);

  const fetchNotifications = () => {
    if (!user) return;
    Promise.all([
      notifications.stats().then((res) => {
        const stats = res.data.data;
        if (stats) {
          const unread = stats.total_sent - Math.round(stats.total_sent * stats.read_rate);
          setUnreadCount(Math.max(0, unread));
        }
      }).catch(() => {}),
      notifications.list({ size: 10 }).then((res) => {
        setNotifList(res.data.data?.items ?? []);
      }).catch(() => {}),
    ]);
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const handleMarkRead = async (id: number) => {
    try {
      await notifications.markRead(id);
      fetchNotifications();
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await notifications.markAllRead();
      fetchNotifications();
    } catch {}
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center px-4 lg:px-8">
      <button onClick={onMenuToggle} className="lg:hidden mr-4 text-gray-500 hover:text-gray-700">
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
      </button>
      <div className="flex-1" />
      <div className="flex items-center gap-4">
        {/* Notification bell */}
        <div className="relative">
          <button onClick={() => { setShowNotifications(!showNotifications); if (!showNotifications) fetchNotifications(); }}
            className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 h-4 w-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </button>
          {showNotifications && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)} />
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg border border-gray-200 shadow-lg z-20">
                <div className="flex items-center justify-between p-3 border-b border-gray-100">
                  <p className="text-sm font-semibold text-gray-900">Notifications</p>
                  {unreadCount > 0 && (
                    <button onClick={handleMarkAllRead} className="text-xs text-blue-600 hover:underline">Mark all read</button>
                  )}
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {notifList.length === 0 ? (
                    <div className="p-8 text-center text-sm text-gray-500">No notifications</div>
                  ) : (
                    notifList.map((n) => (
                      <div key={n.id} className={`p-3 border-b border-gray-50 hover:bg-gray-50 cursor-pointer ${n.read_at ? "" : "bg-blue-50"}`}
                        onClick={() => { if (!n.read_at) handleMarkRead(n.id); if (n.signal_id) { setShowNotifications(false); navigate(`/signals/${n.signal_id}`); } }}>
                        <p className="text-sm font-medium text-gray-900">{n.title}</p>
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                        <p className="text-[10px] text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          )}
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-700">{user?.first_name} {user?.last_name}</p>
          <p className="text-xs text-gray-500">{user?.email}</p>
        </div>
        <div onClick={() => navigate("/profile")} className="h-9 w-9 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold cursor-pointer hover:bg-blue-700">
          {user?.profile_picture_url ? (
            <img src={user.profile_picture_url} alt="" className="h-9 w-9 rounded-full object-cover" />
          ) : (
            `${user?.first_name?.[0] || ""}${user?.last_name?.[0] || ""}`
          )}
        </div>
        <button onClick={async () => { await logout(); navigate("/login"); }} className="text-sm text-red-600 hover:text-red-800 ml-2">
          Logout
        </button>
      </div>
    </header>
  );
}
