import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { auth } from "../api/endpoints";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const code = searchParams.get("code") || "";
  const [status, setStatus] = useState<"verifying" | "success" | "error">("verifying");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!code) {
      setStatus("error");
      setMessage("No verification code provided.");
      return;
    }
    auth.verifyEmail(code)
      .then(() => {
        setStatus("success");
        setMessage("Email verified successfully! You can now sign in.");
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.message || "Verification failed. The link may be expired.");
      });
  }, [code]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md text-center">
        {status === "verifying" && (
          <>
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4" />
            <h1 className="text-xl font-bold text-gray-900">Verifying your email...</h1>
          </>
        )}
        {status === "success" && (
          <>
            <div className="mx-auto h-12 w-12 text-green-500 mb-4">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h1 className="text-xl font-bold text-green-700 mb-2">Email Verified!</h1>
            <p className="text-sm text-gray-600 mb-6">{message}</p>
            <Link to="/login" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">Sign In</Link>
          </>
        )}
        {status === "error" && (
          <>
            <div className="mx-auto h-12 w-12 text-red-500 mb-4">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
            </div>
            <h1 className="text-xl font-bold text-red-600 mb-2">Verification Failed</h1>
            <p className="text-sm text-gray-600 mb-6">{message}</p>
            <Link to="/login" className="text-blue-600 hover:underline text-sm">Back to Sign In</Link>
          </>
        )}
      </div>
    </div>
  );
}
