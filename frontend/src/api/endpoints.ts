import { api } from "./client";
import type {
  ApiResponse, PaginatedData, RegisterData, SignalFilter,
  User, UserStats, Signal, SignalStats, Category, CategoryTree, CategoryStats,
  Sector, SectorStats, Priority, PriorityStats,
  Report, ReportAnalytics, Notification, NotificationStats,
  AdminDashboard, SystemConfig, SystemHealth,
  MapGeocodeResult, MapHeatmapData, MapClusterData, MapCombinedData, MapPlacesResult, MapDistanceResult, MapAddressValidation,
  AIClassification, AIPriorityAssessment, AITrendPrediction, AIAnomalyDetection, AISeverityAnalysis, AIReport, AIModelInfo, AIInsights,
} from "../types";

export const auth = {
  login: (data: { email: string; password: string; remember_me?: boolean }) =>
    api.post<ApiResponse<{ access_token: string; refresh_token: string; token_type: string; expires_in: number; user: User }>>("/auth/login", data),
  register: (data: RegisterData) =>
    api.post<ApiResponse<{ user_id: number; email: string }>>("/auth/register", data),
  me: () =>
    api.get<ApiResponse<User>>("/auth/me"),
  updateProfile: (data: Partial<User>) =>
    api.put<ApiResponse<User>>("/auth/me", data),
  changePassword: (data: { current_password: string; new_password: string; confirm_new_password: string }) =>
    api.put<ApiResponse<void>>("/auth/me/password", data),
  updateNotificationPrefs: (data: { email_notifications_enabled?: boolean; sms_notifications_enabled?: boolean; push_notifications_enabled?: boolean }) =>
    api.put<ApiResponse<void>>("/auth/me/notifications", data),
  logout: () =>
    api.post<ApiResponse<void>>("/auth/logout"),
  refresh: (refreshToken: string) =>
    api.post<ApiResponse<{ access_token: string; token_type: string; expires_in: number }>>(`/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`),
  verifyEmail: (code: string) =>
    api.post<ApiResponse<void>>("/auth/verify-email", { verification_code: code }),
  forgotPassword: (email: string) =>
    api.post<ApiResponse<void>>("/auth/forgot-password", { email }),
  resetPassword: (data: { token: string; password: string; confirm_password: string }) =>
    api.post<ApiResponse<void>>("/auth/reset-password", data),
};

export const users = {
  list: (params?: Record<string, any>) =>
    api.get<ApiResponse<PaginatedData<User>>>("/users", { params }),
  search: (q: string, params?: Record<string, any>) =>
    api.get<ApiResponse<PaginatedData<User>>>("/users/search", { params: { q, ...params } }),
  get: (id: number) =>
    api.get<ApiResponse<User>>(`/users/${id}`),
  update: (id: number, data: Partial<User>) =>
    api.put<ApiResponse<User>>(`/users/${id}`, data),
  delete: (id: number) =>
    api.delete<ApiResponse<void>>(`/users/${id}`),
  getSignals: (id: number, params?: Record<string, any>) =>
    api.get<ApiResponse<PaginatedData<Signal>>>(`/users/${id}/signals`, { params }),
  getStats: (id: number) =>
    api.get<ApiResponse<UserStats>>(`/users/${id}/stats`),
  activate: (id: number) =>
    api.put<ApiResponse<void>>(`/users/${id}/activate`),
  deactivate: (id: number) =>
    api.put<ApiResponse<void>>(`/users/${id}/deactivate`),
};

export const signals = {
  list: (params?: SignalFilter) =>
    api.get<ApiResponse<PaginatedData<Signal>>>("/signals", { params }),
  get: (id: number) =>
    api.get<ApiResponse<Signal>>(`/signals/${id}`),
  create: (data: any) =>
    api.post<ApiResponse<Signal>>("/signals", data),
  update: (id: number, data: any) =>
    api.put<ApiResponse<Signal>>(`/signals/${id}`, data),
  delete: (id: number) =>
    api.delete<ApiResponse<void>>(`/signals/${id}`),
  stats: () =>
    api.get<ApiResponse<SignalStats>>("/signals/stats"),
  nearby: (lat: number, lng: number, radius?: number) =>
    api.get<ApiResponse<{ items: Signal[]; latitude: number; longitude: number; radius: number }>>("/signals/nearby", { params: { latitude: lat, longitude: lng, radius: (radius || 1000) / 1000 } }),
  search: (q: string) =>
    api.get<ApiResponse<{ items: Signal[] }>>("/signals/search", { params: { q } }),
  assign: (id: number, data: { assigned_to_user_id: number; assigned_sector_id?: number }) =>
    api.post<ApiResponse<Signal>>(`/signals/${id}/assign`, data),
  process: (id: number) =>
    api.post<ApiResponse<Signal>>(`/signals/${id}/process`),
  resolve: (id: number, data: any) =>
    api.post<ApiResponse<Signal>>(`/signals/${id}/resolve`, data),
  cancel: (id: number, data?: any) =>
    api.post<ApiResponse<Signal>>(`/signals/${id}/cancel`, data),
  addMedia: (id: number, data: any) =>
    api.post<ApiResponse<any>>(`/signals/${id}/media`, data),
  submitFeedback: (id: number, data: { citizen_satisfaction: number; citizen_feedback?: string }) =>
    api.post<ApiResponse<Signal>>(`/signals/${id}/feedback`, data),
  restore: (id: number) =>
    api.post<ApiResponse<any>>(`/signals/${id}/restore`),
  getTimeline: (id: number) =>
    api.get<ApiResponse<{ id: number; action: string; description: string; timestamp: string; user_name?: string }[]>>(`/signals/${id}/timeline`),
};

export const categories = {
  list: () =>
    api.get<ApiResponse<Category[]>>("/categories"),
  tree: () =>
    api.get<ApiResponse<CategoryTree[]>>("/categories/tree"),
  get: (id: number) =>
    api.get<ApiResponse<Category>>(`/categories/${id}`),
  create: (data: any) =>
    api.post<ApiResponse<Category>>("/categories", data),
  update: (id: number, data: any) =>
    api.put<ApiResponse<Category>>(`/categories/${id}`, data),
  delete: (id: number) =>
    api.delete<ApiResponse<void>>(`/categories/${id}`),
  byType: (type: string) =>
    api.get<ApiResponse<Category[]>>(`/categories/by-type/${type}`),
  subcategories: (id: number) =>
    api.get<ApiResponse<Category[]>>(`/categories/${id}/subcategories`),
  stats: (id: number) =>
    api.get<ApiResponse<CategoryStats>>(`/categories/${id}/stats`),
};

export const priorities = {
  list: () =>
    api.get<ApiResponse<Priority[]>>("/priorities"),
  get: (id: number) =>
    api.get<ApiResponse<Priority>>(`/priorities/${id}`),
  create: (data: any) =>
    api.post<ApiResponse<Priority>>("/priorities", data),
  update: (id: number, data: any) =>
    api.put<ApiResponse<Priority>>(`/priorities/${id}`, data),
  delete: (id: number) =>
    api.delete<ApiResponse<void>>(`/priorities/${id}`),
  stats: (id: number) =>
    api.get<ApiResponse<PriorityStats>>(`/priorities/${id}/stats`),
};

export const sectors = {
  list: () =>
    api.get<ApiResponse<Sector[]>>("/sectors"),
  get: (id: number) =>
    api.get<ApiResponse<Sector>>(`/sectors/${id}`),
  create: (data: any) =>
    api.post<ApiResponse<Sector>>("/sectors", data),
  update: (id: number, data: any) =>
    api.put<ApiResponse<Sector>>(`/sectors/${id}`, data),
  delete: (id: number) =>
    api.delete<ApiResponse<void>>(`/sectors/${id}`),
  stats: (id: number) =>
    api.get<ApiResponse<SectorStats>>(`/sectors/${id}/stats`),
};

export const reports = {
  list: (params?: Record<string, any>) =>
    api.get<ApiResponse<PaginatedData<Report>>>("/reports", { params }),
  get: (id: number) =>
    api.get<ApiResponse<Report>>(`/reports/${id}`),
  create: (data: any) =>
    api.post<ApiResponse<Report>>("/reports", data),
  update: (id: number, data: any) =>
    api.put<ApiResponse<Report>>(`/reports/${id}`, data),
  delete: (id: number) =>
    api.delete<ApiResponse<void>>(`/reports/${id}`),
  stats: () =>
    api.get<ApiResponse<ReportAnalytics>>("/reports/stats"),
  dashboard: () =>
    api.get<ApiResponse<AdminDashboard>>("/reports/dashboard"),
  schedule: (reportId: number, frequency?: string, scheduleConfig?: Record<string, any>) =>
    api.post<ApiResponse<Report>>("/reports/schedule", { report_id: reportId, frequency: frequency || "DAILY", schedule_config: scheduleConfig || {} }),
  archive: (id: number) =>
    api.post<ApiResponse<Report>>(`/reports/${id}/archive`),
  generateSignalReport: (signalId: number) =>
    api.post<ApiResponse<Report>>(`/reports/generate/signal/${signalId}`),
  generateSectorReport: (sectorId: number) =>
    api.post<ApiResponse<Report>>(`/reports/generate/sector/${sectorId}`),
  generateTrendReport: (data: any) =>
    api.post<ApiResponse<Report>>("/reports/generate/trends", data),
  generatePerformanceReport: (params?: { start_date?: string; end_date?: string }) =>
    api.post<ApiResponse<Report>>("/reports/generate/performance", null, { params }),
  generateCitizenFeedbackReport: (params?: { start_date?: string; end_date?: string }) =>
    api.post<ApiResponse<Report>>("/reports/generate/citizen-feedback", null, { params }),
  generatePriorityAssessment: (params?: { sector_id?: number; priority_level?: number; start_date?: string; end_date?: string }) =>
    api.post<ApiResponse<Report>>("/reports/generate/priority-assessment", null, { params }),
  export: (id: number, format: string) =>
    api.get<ApiResponse<any>>(`/reports/${id}/export`, { params: { export_format: format } }),
};

export const admin = {
  dashboard: () =>
    api.get<ApiResponse<AdminDashboard>>("/admin/dashboard"),
  overview: () =>
    api.get<ApiResponse<any>>("/admin/stats/overview"),
  signalStats: () =>
    api.get<ApiResponse<SignalStats>>("/admin/stats/signals"),
  userStats: () =>
    api.get<ApiResponse<{ total_users: number; active_users: number }>>("/admin/stats/users"),
  sectorStats: () =>
    api.get<ApiResponse<any>>("/admin/stats/sectors"),
  categoryStats: () =>
    api.get<ApiResponse<any>>("/admin/stats/categories"),
  responseTimes: (days = 30) =>
    api.get<ApiResponse<any>>("/admin/stats/response-times", { params: { days } }),
  predictions: () =>
    api.get<ApiResponse<any>>("/admin/stats/predictions"),
  health: () =>
    api.get<ApiResponse<SystemHealth>>("/admin/health"),
  config: () =>
    api.get<ApiResponse<SystemConfig>>("/admin/system/config"),
  auditLog: (params?: Record<string, any>) =>
    api.get<ApiResponse<PaginatedData<any>>>("/admin/audit-log", { params }),
};

export const map = {
  geocode: (address: string) =>
    api.post<ApiResponse<MapGeocodeResult>>("/map/geocode", { address }),
  reverseGeocode: (latitude: number, longitude: number) =>
    api.post<ApiResponse<MapGeocodeResult>>("/map/reverse-geocode", { latitude, longitude }),
  heatmap: (params: { lat_min: number; lat_max: number; lng_min: number; lng_max: number; days?: number; grid_size?: number }) =>
    api.get<ApiResponse<MapHeatmapData>>("/map/heatmap", { params }),
  clusters: (params: { lat_min: number; lat_max: number; lng_min: number; lng_max: number; zoom_level?: number; cluster_radius?: number }) =>
    api.get<ApiResponse<MapClusterData>>("/map/clusters", { params }),
  nearby: (params: { latitude: number; longitude: number; radius_km?: number; status?: string; limit?: number }) =>
    api.get<ApiResponse<any>>("/map/nearby", { params }),
  data: (params: { lat: number; lng: number; radius_km?: number; zoom_level?: number; days?: number }) =>
    api.get<ApiResponse<MapCombinedData>>("/map/data", { params }),
  searchPlaces: (params: { query: string; latitude?: number; longitude?: number; radius?: number; place_type?: string }) =>
    api.post<ApiResponse<MapPlacesResult>>("/map/places", null, { params }),
  distance: (data: { origin_lat: number; origin_lng: number; dest_lat: number; dest_lng: number; mode?: string }) =>
    api.post<ApiResponse<MapDistanceResult>>("/map/distance", data),
  validateAddress: (address: string) =>
    api.post<ApiResponse<MapAddressValidation>>("/map/validate-address", { address }),
  route: (data: { origin_lat: number; origin_lng: number; dest_lat: number; dest_lng: number; mode?: string }) =>
    api.post<ApiResponse<any>>("/map/route", data),
};

export const escalation = {
  listCandidates: (params?: { priority_id?: number; min_ratio?: number }) =>
    api.get<ApiResponse<{ items: any[]; total: number }>>("/escalation/candidates", { params }),
  escalateSignal: (signalId: number) =>
    api.post<ApiResponse<any>>(`/escalation/${signalId}/escalate`),
  checkSla: (signalId: number) =>
    api.get<ApiResponse<any>>(`/escalation/sla-check/${signalId}`),
  getSummary: () =>
    api.get<ApiResponse<any>>("/escalation/summary"),
};

export const auditLog = {
  list: (params?: { page?: number; size?: number; entity_type?: string; entity_id?: number; action?: string; user_id?: number; severity?: string; start_date?: string; end_date?: string }) =>
    api.get<ApiResponse<{ items: any[]; page: number; size: number; total: number; pages: number }>>("/audit-logs", { params }),
  getEntityHistory: (entityType: string, entityId: number) =>
    api.get<ApiResponse<any>>(`/audit-logs/entity/${entityType}/${entityId}`),
  getStats: () =>
    api.get<ApiResponse<{ total_entries: number }>>("/audit-logs/stats"),
};

export const feedbackService = {
  process: (signalId: number, satisfaction: number, feedback?: string) =>
    api.post<ApiResponse<{ reopened: boolean; reason: string; new_status?: string }>>(`/feedback/${signalId}/process`, { satisfaction, feedback }),
  getStats: () =>
    api.get<ApiResponse<any>>("/feedback/stats"),
};

export const ai = {
  classify: (data: { text: string; images?: string[]; location?: { latitude: number; longitude: number } }) =>
    api.post<ApiResponse<AIClassification>>("/ai/classify", data),
  assessPriority: (data: { description: string; latitude: number; longitude: number; safety_risk_level?: number; affected_people_count?: number; affected_area_sqm?: number }) =>
    api.post<ApiResponse<AIPriorityAssessment>>("/ai/assess-priority", data),
  predictTrends: (data: { category?: string; days?: number }) =>
    api.post<ApiResponse<AITrendPrediction>>("/ai/predict-trends", data),
  detectAnomalies: (data: { description: string; latitude: number; longitude: number; category?: string }) =>
    api.post<ApiResponse<AIAnomalyDetection>>("/ai/detect-anomalies", data),
  analyzeSeverity: (data: { text: string; images?: string[]; location?: { latitude: number; longitude: number } }) =>
    api.post<ApiResponse<AISeverityAnalysis>>("/ai/analyze-severity", data),
  generateReport: (signalId: number) =>
    api.post<ApiResponse<AIReport>>("/ai/generate-report", { signal_id: signalId }),
  batchClassify: (signals: { id?: number; description?: string; text?: string; images?: string[]; location?: { latitude: number; longitude: number } }[]) =>
    api.post<ApiResponse<{ results: any[] }>>("/ai/batch-classify", { signals }),
  modelInfo: () =>
    api.get<ApiResponse<AIModelInfo>>("/ai/model-info"),
  insights: (days?: number) =>
    api.get<ApiResponse<AIInsights>>("/ai/insights", { params: { days } }),
};

export const analytics = {
  dashboard: (days = 30) =>
    api.get<ApiResponse<any>>(`/analytics/dashboard?days=${days}`),
  trends: (days = 30, granularity = "day") =>
    api.get<ApiResponse<any>>(`/analytics/trends?days=${days}&granularity=${granularity}`),
  sectorPerformance: (days = 30) =>
    api.get<ApiResponse<any>>(`/analytics/sector-performance?days=${days}`),
  categoryBreakdown: (days = 30) =>
    api.get<ApiResponse<any>>(`/analytics/category-breakdown?days=${days}`),
  satisfaction: (days = 30) =>
    api.get<ApiResponse<any>>(`/analytics/satisfaction?days=${days}`),
  responseTimes: (days = 30) =>
    api.get<ApiResponse<any>>(`/analytics/response-times?days=${days}`),
  predictions: (days = 30) =>
    api.get<ApiResponse<any>>(`/analytics/predictions?days=${days}`),
  hotspots: (days = 30, minDensity = 0) =>
    api.get<ApiResponse<any>>(`/analytics/hotspots?days=${days}&min_density=${minDensity}`),
  temporalPatterns: (days = 90) =>
    api.get<ApiResponse<any>>(`/analytics/temporal-patterns?days=${days}`),
  summaryReport: (days = 30, includeCharts = false) =>
    api.get<ApiResponse<any>>(`/analytics/summary-report?days=${days}&include_charts=${includeCharts}`),
};

export const notifications = {
  list: (params?: Record<string, any>) =>
    api.get<ApiResponse<PaginatedData<Notification>>>("/notifications", { params }),
  stats: () =>
    api.get<ApiResponse<NotificationStats>>("/notifications/stats"),
  markRead: (id: number) =>
    api.put<ApiResponse<void>>(`/notifications/${id}/read`),
  markAllRead: () =>
    api.put<ApiResponse<void>>("/notifications/read-all"),
  send: (data: any) =>
    api.post<ApiResponse<Notification>>("/notifications/send", data),
  retry: (id: number) =>
    api.post<ApiResponse<Notification>>(`/notifications/${id}/retry`),
  cancel: (id: number) =>
    api.post<ApiResponse<Notification>>(`/notifications/${id}/cancel`),
  cleanupExpired: (days?: number) =>
    api.post<ApiResponse<any>>("/notifications/cleanup-expired", { days }),
  retryAllFailed: () =>
    api.post<ApiResponse<any>>("/notifications/retry-all-failed"),
};
