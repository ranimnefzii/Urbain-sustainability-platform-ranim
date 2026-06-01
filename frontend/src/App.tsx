import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ToastProvider } from "./contexts/ToastContext";
import { TabProvider } from "./contexts/TabContext";
import ErrorBoundary from "./components/ui/ErrorBoundary";
import AppLayout from "./components/layout/AppLayout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";
import Dashboard from "./pages/Dashboard";
import SignalsHub from "./pages/signals/SignalsHub";
import SignalDetail from "./pages/signals/SignalDetail";
import SignalEdit from "./pages/signals/SignalEdit";
import ProfileHub from "./pages/profile/ProfileHub";
import AdminHub from "./pages/admin/AdminHub";
import UserManagement from "./pages/admin/UserManagement";
import CategoryManagement from "./pages/admin/CategoryManagement";
import PriorityManagement from "./pages/admin/PriorityManagement";
import SectorManagement from "./pages/admin/SectorManagement";
import ReportManagement from "./pages/admin/ReportManagement";
import NotificationManagement from "./pages/admin/NotificationManagement";
import AuditLog from "./pages/admin/AuditLog";
import AIInsights from "./pages/admin/AIInsights";
import UserDetail from "./pages/admin/UserDetail";
import MapHub from "./pages/map/MapHub";
import ReportsHub from "./pages/reports/ReportsHub";
import NotFound from "./pages/NotFound";
import LoadingSpinner from "./components/ui/LoadingSpinner";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner size="lg" className="min-h-screen" />;
  return user ? <>{children}</> : <Navigate to="/login" />;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner size="lg" className="min-h-screen" />;
  if (!user) return <Navigate to="/login" />;
  if (user.role.toLowerCase() !== "admin") return <Navigate to="/" />;
  return <>{children}</>;
}

function SignalsHubRoute() {
  const location = useLocation();
  return <SignalsHub initialPath={location.pathname} />;
}

function AdminHubRoute() {
  const location = useLocation();
  return <AdminRoute><AdminHub initialPath={location.pathname} /></AdminRoute>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner size="lg" className="min-h-screen" />;
  return user ? <Navigate to="/" /> : <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <TabProvider>
            <ErrorBoundary>
            <Routes>
              {/* Public auth routes */}
              <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
              <Route path="/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
              <Route path="/reset-password" element={<PublicRoute><ResetPassword /></PublicRoute>} />
              <Route path="/verify-email" element={<VerifyEmail />} />

              {/* Protected routes with layout */}
              <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                <Route path="/" element={<Dashboard />} />

                {/* Signals Hub */}
                <Route path="/signals" element={<SignalsHubRoute />} />
                <Route path="/signals/list" element={<SignalsHubRoute />} />
                <Route path="/signals/new" element={<SignalsHubRoute />} />
                <Route path="/signals/map" element={<SignalsHubRoute />} />
                <Route path="/signals/analytics" element={<SignalsHubRoute />} />
                <Route path="/signals/:id" element={<SignalDetail />} />
                <Route path="/signals/:id/edit" element={<SignalEdit />} />

                {/* Map Hub */}
                <Route path="/map" element={<MapHub />} />

                {/* Reports Hub */}
                <Route path="/reports" element={<ReportsHub />} />

                {/* User profile */}
                <Route path="/profile" element={<ProfileHub />} />

                {/* Admin Hub & direct admin routes */}
                <Route path="/admin" element={<AdminHubRoute />} />
                <Route path="/admin/dashboard" element={<AdminHubRoute />} />
                <Route path="/admin/users" element={<AdminRoute><UserManagement /></AdminRoute>} />
                <Route path="/admin/users/:userId" element={<AdminRoute><UserDetail /></AdminRoute>} />
                <Route path="/admin/categories" element={<AdminRoute><CategoryManagement /></AdminRoute>} />
                <Route path="/admin/priorities" element={<AdminRoute><PriorityManagement /></AdminRoute>} />
                <Route path="/admin/sectors" element={<AdminRoute><SectorManagement /></AdminRoute>} />
                <Route path="/admin/reports" element={<AdminRoute><ReportManagement /></AdminRoute>} />
                <Route path="/admin/notifications" element={<AdminRoute><NotificationManagement /></AdminRoute>} />
                <Route path="/admin/audit-log" element={<AdminRoute><AuditLog /></AdminRoute>} />
                <Route path="/admin/ai" element={<AdminRoute><AIInsights /></AdminRoute>} />
                <Route path="/admin/ai-insights" element={<AdminRoute><AIInsights /></AdminRoute>} />
                <Route path="/admin/stats/overview" element={<AdminHubRoute />} />
                <Route path="/admin/stats/users" element={<AdminHubRoute />} />
                <Route path="/admin/stats/sectors" element={<AdminHubRoute />} />
                <Route path="/admin/stats/categories" element={<AdminHubRoute />} />
                <Route path="/admin/health" element={<AdminHubRoute />} />
              </Route>

              <Route path="*" element={<NotFound />} />
            </Routes>
            </ErrorBoundary>
          </TabProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
