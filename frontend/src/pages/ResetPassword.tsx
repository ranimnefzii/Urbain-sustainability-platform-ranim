import { useState, type FormEvent } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { auth } from "../api/endpoints";
import { useToast } from "../contexts/ToastContext";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const token = searchParams.get("token") || "";

  const [form, setForm] = useState({ password: "", confirm_password: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirm_password) {
      toast("Passwords do not match", "error");
      return;
    }
    setLoading(true);
    try {
      await auth.resetPassword({ token, ...form });
      toast("Password reset successfully. Please sign in.", "success");
      navigate("/login");
    } catch (err: any) {
      toast(err.response?.data?.message || "Reset failed. The link may be expired.", "error");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h1 className="text-xl font-bold text-red-600 mb-2">Invalid Reset Link</h1>
          <p className="text-gray-600 text-sm">This link is missing or invalid. Please request a new one.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">Reset Password</h1>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">New Password</label>
          <input type="password" value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} required minLength={8}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">Confirm Password</label>
          <input type="password" value={form.confirm_password} onChange={(e) => setForm((f) => ({ ...f, confirm_password: e.target.value }))} required minLength={8}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" />
        </div>
        <button type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
    </div>
  );
}
