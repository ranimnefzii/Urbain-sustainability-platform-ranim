import { useState, useEffect, useRef } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate, useLocation } from "react-router-dom";
import { notifications } from "../../api/endpoints";
import type { Notification } from "../../types";

interface NavbarProps { onMenuToggle: () => void; }

const pageTitles: Record<string, string> = {
  "/": "Tableau de bord",
  "/signals": "Signalements",
  "/map": "Carte interactive",
  "/reports": "Rapports",
  "/profile": "Mon profil",
  "/admin": "Administration",
  "/admin/users": "Gestion des utilisateurs",
  "/admin/categories": "Gestion des catégories",
  "/admin/priorities": "Gestion des priorités",
  "/admin/sectors": "Gestion des secteurs",
  "/admin/notifications": "Centre de notifications",
  "/admin/ai": "Intelligence Artificielle",
  "/admin/audit-log": "Journal d'audit",
  "/admin/reports": "Rapports d'administration",
};

export default function Navbar({ onMenuToggle }: NavbarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifList, setNotifList] = useState<Notification[]>([]);
  const notifRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  const pageTitle = Object.entries(pageTitles).find(([path]) => location.pathname.startsWith(path))?.[1] || "Urbain";

  const fetchNotifications = () => {
    if (!user) return;
    Promise.all([
      notifications.stats().then((res) => {
        const stats = res.data.data;
        if (stats) { const unread = stats.total_sent - Math.round(stats.total_sent * (stats.read_rate || 0)); setUnreadCount(Math.max(0, unread)); }
      }).catch(() => {}),
      notifications.list({ size: 10 }).then((res) => { setNotifList(res.data.data?.items ?? []); }).catch(() => {}),
    ]);
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [user]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setShowNotifications(false);
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setShowUserMenu(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleMarkRead = async (id: number) => { try { await notifications.markRead(id); fetchNotifications(); } catch {} };
  const handleMarkAllRead = async () => { try { await notifications.markAllRead(); fetchNotifications(); } catch {} };

  return (
    <header className="bg-white border-b border-surface-200 h-16 flex items-center px-4 lg:px-8 sticky top-0 z-30">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button onClick={onMenuToggle} className="lg:hidden p-2 text-surface-500 hover:text-surface-700 hover:bg-surface-100 rounded-lg transition-colors">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
        </button>
        <div>
          <h2 className="text-lg font-bold text-surface-900">{pageTitle}</h2>
          <p className="text-xs text-surface-400 hidden sm:block">
            {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </p>
        </div>
      </div>

      <div className="flex-1" />

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Notification bell */}
        <div className="relative" ref={notifRef}>
          <button onClick={() => { setShowNotifications(!showNotifications); if (!showNotifications) fetchNotifications(); }}
            className="relative p-2.5 text-surface-500 hover:text-surface-700 hover:bg-surface-100 rounded-xl transition-all duration-200">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 h-5 w-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center ring-2 ring-white shadow-sm">
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl border border-surface-200 shadow-elevated z-50 animate-scale-in">
              <div className="flex items-center justify-between p-4 border-b border-surface-100">
                <p className="text-sm font-bold text-surface-900">Notifications</p>
                {unreadCount > 0 && (
                  <button onClick={handleMarkAllRead} className="text-xs text-brand-600 font-semibold hover:text-brand-700 transition-colors">Tout marquer lu</button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifList.length === 0 ? (
                  <div className="p-8 text-center">
                    <svg className="w-8 h-8 text-surface-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                    <p className="text-sm text-surface-400">Aucune notification</p>
                  </div>
                ) : (
                  notifList.map((n) => (
                    <div key={n.id} className={`p-4 border-b border-surface-50 cursor-pointer transition-all duration-150 hover:bg-surface-50 ${n.read_at ? "" : "bg-brand-50/50"}`}
                      onClick={() => { if (!n.read_at) handleMarkRead(n.id); if (n.signal_id) { setShowNotifications(false); navigate(`/signals/${n.signal_id}`); } }}>
                      <p className="text-sm font-semibold text-surface-900">{n.title}</p>
                      <p className="text-xs text-surface-500 mt-0.5 line-clamp-2">{n.message}</p>
                      <p className="text-[10px] text-surface-400 mt-1.5 flex items-center gap-1.5">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        {new Date(n.created_at).toLocaleString("fr-FR")}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User avatar + menu */}
        <div className="relative" ref={userMenuRef}>
          <button onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2.5 p-1.5 pr-3 rounded-xl hover:bg-surface-100 transition-all duration-200">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold shadow-sm ring-2 ring-white">
              {user?.first_name?.[0] || ""}{user?.last_name?.[0] || ""}
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-sm font-medium text-surface-800 leading-tight">{user?.first_name} {user?.last_name}</p>
              <p className="text-[10px] text-surface-400 capitalize">{user?.role?.toLowerCase() === "admin" ? "Administrateur" : "Citoyen"}</p>
            </div>
            <svg className={`w-4 h-4 text-surface-400 transition-transform duration-200 ${showUserMenu ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl border border-surface-200 shadow-elevated z-50 animate-scale-in py-1">
              <div className="px-4 py-3 border-b border-surface-100">
                <p className="text-sm font-semibold text-surface-900">{user?.first_name} {user?.last_name}</p>
                <p className="text-xs text-surface-400">{user?.email}</p>
              </div>
              <button onClick={() => { setShowUserMenu(false); navigate("/profile"); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-surface-700 hover:bg-surface-50 transition-colors">
                <svg className="w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                Mon profil
              </button>
              {user?.role?.toLowerCase() === "admin" && (
                <button onClick={() => { setShowUserMenu(false); navigate("/admin"); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-surface-700 hover:bg-surface-50 transition-colors">
                  <svg className="w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /></svg>
                  Administration
                </button>
              )}
              <div className="border-t border-surface-100 mt-1 pt-1">
                <button onClick={async () => { await logout(); navigate("/login"); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                  Déconnexion
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
