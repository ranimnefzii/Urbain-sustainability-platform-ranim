import { useState, useEffect } from "react";
import { users } from "../../api/endpoints";
import DataTable, { type Column } from "../../components/ui/DataTable";
import StatusBadge from "../../components/ui/StatusBadge";
import Modal from "../../components/ui/Modal";
import { useToast } from "../../contexts/ToastContext";
import type { User } from "../../types";

export default function UserManagement() {
  const { toast } = useToast();
  const [data, setData] = useState<{ items: User[]; page: number; pages: number; total: number }>({ items: [], page: 1, pages: 1, total: 0 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<User | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetch = async (p: number, q?: string) => {
    setLoading(true);
    try {
      const res = q ? await users.search(q, { page: p, size: 20 }) : await users.list({ page: p, size: 20 });
      setData(res.data.data ?? { items: [], page: 1, pages: 1, total: 0 });
    } catch { toast("Failed to load users", "error"); } finally { setLoading(false); }
  };

  useEffect(() => { fetch(page, search || undefined); }, [page, search]);

  const handleSearch = () => { setPage(1); fetch(1, search || undefined); };

  const handleToggleStatus = async (user: User) => {
    setActionLoading(true);
    try {
      if (user.status === "ACTIVE") await users.deactivate(user.id);
      else await users.activate(user.id);
      setSelected(null);
      fetch(page, search || undefined);
    } catch { toast("Action failed", "error"); } finally { setActionLoading(false); }
  };

  const handleRoleChange = async (userId: number, role: string) => {
    setActionLoading(true);
    try {
      await users.update(userId, { role } as Partial<User>);
      setSelected(null);
      fetch(page, search || undefined);
    } catch { toast("Role update failed", "error"); } finally { setActionLoading(false); }
  };

  const columns: Column<User>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "name", header: "Name", render: (u) => <span className="font-medium">{u.first_name} {u.last_name}</span> },
    { key: "email", header: "Email" },
    { key: "username", header: "Username" },
    { key: "role", header: "Role", render: (u) => <span className="uppercase text-xs font-medium">{u.role}</span> },
    { key: "status", header: "Status", render: (u) => <StatusBadge status={u.status} /> },
    { key: "created_at", header: "Joined", render: (u) => new Date(u.created_at || "").toLocaleDateString() },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <div className="text-sm text-gray-500">{data.total} users</div>
      </div>

      <div className="flex gap-4">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Search by name, email, username..." className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button onClick={handleSearch} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Search</button>
      </div>

      <DataTable
        columns={columns}
        data={data.items}
        loading={loading}
        emptyTitle="No users found"
        keyExtractor={(u) => u.id}
        onRowClick={setSelected}
        pagination={{ page: data.page, pages: data.pages, total: data.total, onPageChange: setPage }}
      />

      <Modal open={!!selected} onClose={() => setSelected(null)} title={selected ? `${selected.first_name} ${selected.last_name}` : ""} size="lg">
        {selected && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">Email:</span> <span className="font-medium">{selected.email}</span></div>
              <div><span className="text-gray-500">Username:</span> <span className="font-medium">{selected.username}</span></div>
              <div><span className="text-gray-500">Role:</span>
                <select value={selected.role} onChange={(e) => handleRoleChange(selected.id, e.target.value)} disabled={actionLoading}
                  className="ml-2 border border-gray-300 rounded px-2 py-1 text-sm">
                  <option value="citizen">Citizen</option>
                  <option value="sector_user">Sector User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div><span className="text-gray-500">Status:</span> <StatusBadge status={selected.status} /></div>
              <div><span className="text-gray-500">Phone:</span> {selected.phone_number || "-"}</div>
              <div><span className="text-gray-500">Verified:</span> {selected.is_email_verified ? "Yes" : "No"}</div>
              <div><span className="text-gray-500">City:</span> {selected.city || "-"}</div>
              <div><span className="text-gray-500">Joined:</span> {selected.created_at ? new Date(selected.created_at).toLocaleDateString() : "-"}</div>
            </div>
            <div className="flex justify-end gap-3 pt-2 border-t">
              <button onClick={() => handleToggleStatus(selected)} disabled={actionLoading}
                className={`px-4 py-2 text-sm rounded-lg text-white ${selected.status === "ACTIVE" ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"} disabled:opacity-50`}>
                {actionLoading ? "..." : selected.status === "ACTIVE" ? "Deactivate" : "Activate"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
