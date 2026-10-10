import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const mainNavItems = [
  { to: "/", label: "Tableau de bord", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { to: "/signals", label: "Signalements", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { to: "/map", label: "Carte interactive", icon: "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" },
  { to: "/reports", label: "Rapports", icon: "M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { to: "/profile", label: "Profil", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
];

const adminNavItems = [
  { to: "/admin", label: "Dashboard", icon: "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6z" },
  { to: "/admin/users", label: "Utilisateurs", icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" },
  { to: "/admin/categories", label: "Catégories", icon: "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" },
  { to: "/admin/priorities", label: "Priorités", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
  { to: "/admin/sectors", label: "Secteurs", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
  { to: "/admin/notifications", label: "Notifications", icon: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" },
  { to: "/admin/ai", label: "IA & Analytics", icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" },
  { to: "/admin/ai/pipeline", label: "Pipeline IA", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm12 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" },
  { to: "/admin/audit-log", label: "Audit", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" },
];

export default function Sidebar() {
  const { user } = useAuth();
  const location = useLocation();
  const isAdmin = user?.role === "admin" || user?.role === "ADMIN";
  const initials = user ? `${user.first_name?.[0] || ""}${user.last_name?.[0] || ""}`.toUpperCase() : "U";

  const isActivePath = (path: string) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="w-64 bg-surface-900 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="p-5 border-b border-surface-700/50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-brand-600/20">
            U
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Urbain</h1>
            <p className="text-[10px] text-surface-400 font-medium">Gestion Urbaine</p>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-0.5 scrollbar-thin">
        <p className="text-[10px] font-semibold text-surface-400 uppercase tracking-widest px-3 pb-1 pt-2">Principal</p>
        {mainNavItems.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === "/"}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
              isActivePath(item.to)
                ? "bg-brand-600/20 text-brand-300 shadow-sm"
                : "text-surface-300 hover:bg-surface-800 hover:text-white"
            }`}>
            <svg className={`h-5 w-5 flex-shrink-0 transition-colors ${
              isActivePath(item.to) ? "text-brand-400" : "text-surface-500 group-hover:text-surface-300"
            }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
            </svg>
            <span>{item.label}</span>
            {isActivePath(item.to) && item.to !== "/" && (
              <div className="ml-auto w-1.5 h-1.5 rounded-full bg-brand-400" />
            )}
          </NavLink>
        ))}

        {/* Admin Section */}
        {isAdmin && (
          <>
            <div className="pt-5 pb-1">
              <p className="text-[10px] font-semibold text-surface-400 uppercase tracking-widest px-3">Administration</p>
            </div>
            {adminNavItems.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.to === "/admin"}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActivePath(item.to) && item.to !== "/admin" ? "bg-purple-600/20 text-purple-300" :
                  isActivePath(item.to) ? "bg-purple-600/20 text-purple-300" : "text-surface-300 hover:bg-surface-800 hover:text-white"
                }`}>
                <svg className={`h-5 w-5 flex-shrink-0 ${
                  isActivePath(item.to) ? "text-purple-400" : "text-surface-500 group-hover:text-surface-300"
                }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
                </svg>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* User footer */}
      {user && (
        <div className="p-4 border-t border-surface-700/50 bg-surface-800/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-xs font-bold text-white shadow-sm">
              {initials || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-surface-200 truncate">{user.first_name} {user.last_name}</p>
              <p className="text-[11px] text-surface-400 truncate">{user.role}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
