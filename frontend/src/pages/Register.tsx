import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../contexts/ToastContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [form, setForm] = useState({
    email: "", username: "", password: "", confirm_password: "",
    first_name: "", last_name: "", phone_number: "",
    agree_terms: false, privacy_policy: false,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm_password) {
      setError("Passwords do not match");
      return;
    }
    if (!form.agree_terms || !form.privacy_policy) {
      setError("You must agree to the terms and privacy policy");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      toast("Account created! Please check your email to verify.", "success");
      navigate("/login");
    } catch (err: any) {
      setError(err.response?.data?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">Create Account</h1>
        {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div><label className="block text-gray-700 text-sm font-bold mb-2">First Name</label>
            <input type="text" value={form.first_name} onChange={update("first_name")} required
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
          <div><label className="block text-gray-700 text-sm font-bold mb-2">Last Name</label>
            <input type="text" value={form.last_name} onChange={update("last_name")} required
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
        </div>
        <div className="mb-4"><label className="block text-gray-700 text-sm font-bold mb-2">Username</label>
          <input type="text" value={form.username} onChange={update("username")} required
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
        <div className="mb-4"><label className="block text-gray-700 text-sm font-bold mb-2">Email</label>
          <input type="email" value={form.email} onChange={update("email")} required
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
        <div className="mb-4"><label className="block text-gray-700 text-sm font-bold mb-2">Phone</label>
          <input type="tel" value={form.phone_number} onChange={update("phone_number")}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
        <div className="mb-4"><label className="block text-gray-700 text-sm font-bold mb-2">Password</label>
          <input type="password" value={form.password} onChange={update("password")} required minLength={8}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
        <div className="mb-4"><label className="block text-gray-700 text-sm font-bold mb-2">Confirm Password</label>
          <input type="password" value={form.confirm_password} onChange={update("confirm_password")} required minLength={8}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" /></div>
        <div className="mb-2 flex items-center gap-2">
          <input type="checkbox" id="agree_terms" checked={form.agree_terms} onChange={update("agree_terms")} required />
          <label htmlFor="agree_terms" className="text-sm text-gray-600">I agree to the Terms &amp; Conditions</label>
        </div>
        <div className="mb-6 flex items-center gap-2">
          <input type="checkbox" id="privacy_policy" checked={form.privacy_policy} onChange={update("privacy_policy")} required />
          <label htmlFor="privacy_policy" className="text-sm text-gray-600">I accept the Privacy Policy</label>
        </div>
        <button type="submit" disabled={loading}
          className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50">
          {loading ? "Creating account..." : "Register"}
        </button>
        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Sign In</Link>
        </p>
      </form>
    </div>
  );
}
