import { NavLink } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const mainNavItems = [
  { to: "/", label: "Dashboard", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  {
    to: "/signals",
    label: "Signals",
    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
    children: [
      { to: "/signals", label: "All Signals" },
      { to: "/profile", label: "My Signals" },
    ],
  },
  { to: "/profile", label: "Profile", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
];

const adminNavItems = [
  {
    to: "/admin",
    label: "Admin",
    icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
    children: [
      { to: "/admin", label: "Dashboard" },
      { to: "/admin/users", label: "Users" },
      { to: "/admin/categories", label: "Categories" },
      { to: "/admin/priorities", label: "Priorities" },
      { to: "/admin/sectors", label: "Sectors" },
      { to: "/admin/reports", label: "Reports" },
      { to: "/admin/notifications", label: "Notifications" },
      { to: "/admin/audit-log", label: "Audit Log" },
      { to: "/admin/ai", label: "AI Insights" },
    ],
  },
];

export default function Sidebar() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin" || user?.role === "ADMIN";
  const initials = user ? `${user.first_name?.[0] || ""}${user.last_name?.[0] || ""}`.toUpperCase() : "U";

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0">
      <div className="p-5 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white font-bold text-sm">
            U
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-800">Urbain</h1>
            <p className="text-[10px] text-gray-400">Sustainability System</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {mainNavItems.map((item) => (
          <div key={item.to}>
            <NavLink to={item.to} end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`
              }>
              <svg className="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} /></svg>
              <span>{item.label}</span>
            </NavLink>
            {"children" in item && item.children && (
              <div className="ml-8 mt-0.5 space-y-0.5">
                {item.children.map((child) => (
                  <NavLink key={child.to} to={child.to} end
                    className={({ isActive }) =>
                      `block px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                        isActive ? "text-blue-600 bg-blue-50" : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                      }`
                    }>
                    {child.label}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        ))}

        {isAdmin && (
          <>
            <div className="pt-4 pb-1">
              <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest px-3">Administration</p>
            </div>
            {adminNavItems.map((item) => (
              <div key={item.to}>
                <NavLink to={item.to} end
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive ? "bg-purple-50 text-purple-700" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    }`
                  }>
                  <svg className="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} /></svg>
                  <span>{item.label}</span>
                </NavLink>
                {"children" in item && item.children && (
                  <div className="ml-8 mt-0.5 space-y-0.5">
                    {item.children.slice(1).map((child) => (
                      <NavLink key={child.to} to={child.to} end
                        className={({ isActive }) =>
                          `block px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                            isActive ? "text-purple-600 bg-purple-50" : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                          }`
                        }>
                        {child.label}
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </>
        )}
      </nav>

      {/* User footer */}
      {user && (
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
              {initials || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-700 truncate">{user.first_name} {user.last_name}</p>
              <p className="text-[11px] text-gray-400 truncate">{user.email}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
