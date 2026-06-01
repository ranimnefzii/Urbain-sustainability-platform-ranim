import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { auth } from "../api/endpoints";
import { useToast } from "../contexts/ToastContext";

export default function ForgotPassword() {
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await auth.forgotPassword(email);
      setSent(true);
      toast("If that email exists, a reset link has been sent.", "success");
    } catch (err: any) {
      toast(err.response?.data?.message || "Request failed", "error");
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md text-center">
          <div className="mx-auto h-12 w-12 text-green-500 mb-4">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
          </div>
          <h1 className="text-xl font-bold text-gray-900 mb-2">Check Your Email</h1>
          <p className="text-sm text-gray-600 mb-6">If an account exists for <strong>{email}</strong>, we've sent password reset instructions.</p>
          <Link to="/login" className="text-blue-600 hover:underline text-sm">Back to Sign In</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-2 text-center text-gray-800">Forgot Password</h1>
        <p className="text-sm text-gray-500 text-center mb-6">Enter your email and we'll send you a reset link.</p>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500" />
        </div>
        <button type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Sending..." : "Send Reset Link"}
        </button>
        <p className="mt-4 text-center text-sm text-gray-600">
          Remember your password? <Link to="/login" className="text-blue-600 hover:underline">Sign In</Link>
        </p>
      </form>
    </div>
  );
}
