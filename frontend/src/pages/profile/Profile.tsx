import { useState, type FormEvent, useRef } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { auth } from "../../api/endpoints";
import { api } from "../../api/client";

export default function Profile() {
  const { user } = useAuth();
  const [tab, setTab] = useState<"profile" | "password" | "notifications">("profile");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [profile, setProfile] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone_number: (user as any)?.phone_number || "",
    address: (user as any)?.address || "",
    city: (user as any)?.city || "",
    postal_code: (user as any)?.postal_code || "",
    country: (user as any)?.country || "",
    preferred_language: (user as any)?.preferred_language || "fr",
  });

  const [pw, setPw] = useState({ current_password: "", new_password: "", confirm_new_password: "" });

  const [notif, setNotif] = useState({
    email_notifications_enabled: (user as any)?.email_notifications_enabled ?? true,
    sms_notifications_enabled: (user as any)?.sms_notifications_enabled ?? false,
    push_notifications_enabled: (user as any)?.push_notifications_enabled ?? true,
  });

  const showMessage = (type: string, text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: "", text: "" }), 4000);
  };

  const handleProfileSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await auth.updateProfile(profile);
      showMessage("success", "Profile updated");
    } catch (err: any) {
      showMessage("error", err.response?.data?.message || "Update failed");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (pw.new_password !== pw.confirm_new_password) { showMessage("error", "Passwords do not match"); return; }
    setLoading(true);
    try {
      await auth.changePassword(pw);
      showMessage("success", "Password changed");
      setPw({ current_password: "", new_password: "", confirm_new_password: "" });
    } catch (err: any) {
      showMessage("error", err.response?.data?.message || "Password change failed");
    } finally {
      setLoading(false);
    }
  };

  const handleNotifSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await auth.updateNotificationPrefs(notif);
      showMessage("success", "Notification preferences updated");
    } catch (err: any) {
      showMessage("error", err.response?.data?.message || "Update failed");
    } finally {
      setLoading(false);
    }
  };

  const handleProfilePicUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      const uploadRes = await api.post("/files/upload/profile-picture", formData);
      const url = uploadRes.data.data?.url || uploadRes.data.url;
      if (url) {
        await auth.updateProfile({ profile_picture_url: url } as any);
        showMessage("success", "Profile picture updated");
      } else {
        showMessage("error", "Upload failed - no URL returned");
      }
    } catch {
      showMessage("error", "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "profile" as const, label: "Profile" },
    { id: "password" as const, label: "Password" },
    { id: "notifications" as const, label: "Notifications" },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((t) => (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${tab === t.id ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
                {t.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {message.text && (
            <div className={`mb-4 px-4 py-3 rounded text-sm ${message.type === "success" ? "bg-green-100 text-green-700 border border-green-200" : "bg-red-100 text-red-700 border border-red-200"}`}>
              {message.text}
            </div>
          )}

          {tab === "profile" && (
            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <div className="flex items-center gap-6 mb-4">
                <div className="h-16 w-16 rounded-full bg-blue-600 flex items-center justify-center text-white text-2xl font-bold">
                  {user?.profile_picture_url ? (
                    <img src={user.profile_picture_url} alt="" className="h-16 w-16 rounded-full object-cover" />
                  ) : (
                    `${user?.first_name?.[0] || ""}${user?.last_name?.[0] || ""}`
                  )}
                </div>
                <div>
                  <input ref={fileInputRef} type="file" accept="image/*" hidden onChange={handleProfilePicUpload} />
                  <button type="button" onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                    Change Photo
                  </button>
                  <p className="text-xs text-gray-500 mt-1">JPG, PNG or GIF. 1MB max.</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                  <input type="text" value={profile.first_name} onChange={(e) => setProfile((p) => ({ ...p, first_name: e.target.value }))} required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                  <input type="text" value={profile.last_name} onChange={(e) => setProfile((p) => ({ ...p, last_name: e.target.value }))} required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input type="tel" value={profile.phone_number} onChange={(e) => setProfile((p) => ({ ...p, phone_number: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input type="text" value={profile.address} onChange={(e) => setProfile((p) => ({ ...p, address: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <input type="text" value={profile.city} onChange={(e) => setProfile((p) => ({ ...p, city: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                  <input type="text" value={profile.postal_code} onChange={(e) => setProfile((p) => ({ ...p, postal_code: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                  <input type="text" value={profile.country} onChange={(e) => setProfile((p) => ({ ...p, country: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                <select value={profile.preferred_language} onChange={(e) => setProfile((p) => ({ ...p, preferred_language: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                  <option value="fr">Fran&ccedil;ais</option>
                  <option value="en">English</option>
                  <option value="ar">العربية</option>
                </select>
              </div>
              <div className="pt-2">
                <button type="submit" disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
                  {loading ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          )}

          {tab === "password" && (
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                <input type="password" value={pw.current_password} onChange={(e) => setPw((p) => ({ ...p, current_password: e.target.value }))} required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input type="password" value={pw.new_password} onChange={(e) => setPw((p) => ({ ...p, new_password: e.target.value }))} required minLength={8}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input type="password" value={pw.confirm_new_password} onChange={(e) => setPw((p) => ({ ...p, confirm_new_password: e.target.value }))} required minLength={8}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div className="pt-2">
                <button type="submit" disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
                  {loading ? "Changing..." : "Change Password"}
                </button>
              </div>
            </form>
          )}

          {tab === "notifications" && (
            <form onSubmit={handleNotifSubmit} className="space-y-4">
              <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" checked={notif.email_notifications_enabled} onChange={(e) => setNotif((p) => ({ ...p, email_notifications_enabled: e.target.checked }))} className="rounded" />
                <div><p className="text-sm font-medium text-gray-700">Email Notifications</p><p className="text-xs text-gray-500">Receive updates via email</p></div>
              </label>
              <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" checked={notif.sms_notifications_enabled} onChange={(e) => setNotif((p) => ({ ...p, sms_notifications_enabled: e.target.checked }))} className="rounded" />
                <div><p className="text-sm font-medium text-gray-700">WhatsApp Notifications</p><p className="text-xs text-gray-500">Receive updates via WhatsApp</p></div>
              </label>
              <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" checked={notif.push_notifications_enabled} onChange={(e) => setNotif((p) => ({ ...p, push_notifications_enabled: e.target.checked }))} className="rounded" />
                <div><p className="text-sm font-medium text-gray-700">Push Notifications</p><p className="text-xs text-gray-500">Receive push notifications</p></div>
              </label>
              <div className="pt-2">
                <button type="submit" disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
                  {loading ? "Saving..." : "Save Preferences"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
