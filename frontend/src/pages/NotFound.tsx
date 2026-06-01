import { useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300">404</h1>
        <p className="mt-4 text-lg text-gray-600">Page not found</p>
        <button onClick={() => navigate("/")} className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
          Go Home
        </button>
      </div>
    </div>
  );
}
