export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface PaginatedData<T> {
  items: T[];
  page: number;
  size: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone_number?: string | null;
  profile_picture_url?: string | null;
  role: string;
  status: string;
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  email_notifications_enabled?: boolean;
  sms_notifications_enabled?: boolean;
  push_notifications_enabled?: boolean;
  preferred_language?: string;
  is_email_verified?: boolean;
  is_phone_verified?: boolean;
  created_at?: string;
  updated_at?: string;
  last_login_at?: string | null;
  total_signals_created?: number;
  total_signals_processed?: number;
}

export interface UserStats {
  total_signals_created: number;
  total_signals_processed: number;
  avg_resolution_time_hours: number;
  citizen_satisfaction_rate: number;
  signals_by_status: Record<string, number>;
  signals_by_category: Record<string, number>;
  recent_activity: any[];
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  confirm_password: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  preferred_language?: string;
  agree_terms: boolean;
  privacy_policy: boolean;
}

export interface Category {
  id: number;
  name: string;
  code: string;
  description?: string | null;
  parent_id?: number | null;
  level: number;
  sort_order: number;
  category_type: string;
  status: string;
  icon?: string | null;
  color?: string | null;
  marker_icon?: string | null;
  default_priority_level: number;
  default_severity_level: number;
  ai_confidence_threshold: number;
  requires_image_verification: boolean;
  default_processing_time_hours: number;
  auto_assignment_enabled: boolean;
  requires_approval: boolean;
  responsible_sectors?: number[];
  escalation_sectors?: number[];
  auto_notify_citizen: boolean;
  auto_notify_sector: boolean;
  required_fields?: any | null;
  optional_fields?: any | null;
  validation_rules?: any | null;
  total_signals: number;
  avg_resolution_time_hours: number;
  satisfaction_rate: number;
  created_at: string;
  updated_at: string;
  subcategories?: Category[] | null;
}

export interface CategoryTree {
  id: number;
  name: string;
  code: string;
  level: number;
  icon?: string | null;
  color?: string | null;
  children: CategoryTree[];
}

export interface CategoryStats {
  id: number;
  name: string;
  code: string;
  total_signals: number;
  active_signals: number;
  resolved_signals: number;
  avg_resolution_time_hours: number;
  citizen_satisfaction_rate: number;
  signals_by_priority: Record<string, number>;
  signals_by_status: Record<string, number>;
  monthly_trend: { month: string; count: number }[];
}

export interface Priority {
  id: number;
  name: string;
  code: string;
  description?: string | null;
  priority_level: number;
  severity_level: number;
  color?: string | null;
  icon?: string | null;
  sla_hours: number;
  escalation_minutes: number;
  auto_escalate: boolean;
  requires_approval: boolean;
  notification_templates?: any | null;
  is_active: boolean;
  total_signals: number;
  avg_resolution_time_hours: number;
  created_at: string;
  updated_at: string;
}

export interface PriorityStats {
  id: number;
  name: string;
  code: string;
  total_signals: number;
  resolved_signals: number;
  avg_resolution_time_hours: number;
  sla_breach_count: number;
  escalation_count: number;
}

export interface Sector {
  id: number;
  name: string;
  code: string;
  description?: string | null;
  sector_type: string;
  status: string;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  manager_name?: string | null;
  manager_email?: string | null;
  manager_phone?: string | null;
  working_hours?: Record<string, string> | null;
  emergency_contact?: Record<string, string> | null;
  max_daily_signals: number;
  avg_processing_time_hours: number;
  priority_level: number;
  email_templates?: any | null;
  auto_assignment_enabled: boolean;
  escalation_enabled: boolean;
  ai_confidence_threshold: number;
  supported_categories?: number[] | null;
  external_systems?: any | null;
  api_endpoints?: Record<string, string> | null;
  total_signals_processed: number;
  avg_resolution_time_hours: number;
  satisfaction_rate: number;
  created_at: string;
  updated_at: string;
  users?: { id: number; username: string; email: string; first_name: string; last_name: string; role: string; status: string }[] | null;
}

export interface SectorStats {
  id: number;
  name: string;
  code: string;
  sector_type: string;
  total_signals_processed: number;
  active_signals: number;
  resolved_signals: number;
  avg_resolution_time_hours: number;
  satisfaction_rate: number;
  signals_by_category: Record<string, number>;
  signals_by_priority: Record<string, number>;
  monthly_trend: { period: string; count: number }[];
  performance_score: number;
}

export interface Signal {
  id: number;
  reference_number: string;
  title: string;
  description: string;
  status: string;
  source: string;
  verification_status: string;
  latitude: number;
  longitude: number;
  address?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  location_accuracy?: string | null;
  location_description?: string | null;
  images?: string[] | null;
  videos?: string[] | null;
  documents?: string[] | null;
  audio_files?: string[] | null;
  ai_confidence_score?: number | null;
  ai_priority_score?: number | null;
  ai_severity_score?: number | null;
  ai_urgency_score?: number | null;
  estimated_damage_cost?: number | null;
  affected_people_count?: number | null;
  affected_area_sqm?: number | null;
  safety_risk_level?: number | null;
  assigned_at?: string | null;
  started_processing_at?: string | null;
  resolved_at?: string | null;
  closed_at?: string | null;
  resolution_description?: string | null;
  resolution_method?: string | null;
  resolution_cost?: number | null;
  resolution_images?: string[] | null;
  citizen_satisfaction?: number | null;
  citizen_feedback?: string | null;
  citizen_response_time_hours?: number | null;
  is_public: boolean;
  is_anonymous: boolean;
  allow_contact: boolean;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  created_by_user?: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    profile_picture_url?: string | null;
  } | null;
  processed_by_user?: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
  } | null;
  category?: Category | null;
  priority?: Priority | null;
  category_id?: number;
  priority_id?: number;
  is_deleted?: boolean | null;
  deleted_at?: string | null;
}

export interface SignalStats {
  total_signals: number;
  signals_by_status: Record<string, number>;
  signals_by_category: Record<string, number>;
  signals_by_priority: Record<string, number>;
  avg_resolution_time_hours: number;
  citizen_satisfaction_rate: number;
  signals_by_month: Record<string, number>;
  geographic_hotspots: { latitude: number; longitude: number; count: number }[];
  recent_trends: { period: string; count: number }[];
}

export interface SignalFilter {
  status?: string;
  category_id?: number;
  priority_id?: number;
  sector_id?: number;
  created_by?: number;
  assigned_to?: number;
  search?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface Report {
  id: number;
  title: string;
  description?: string | null;
  report_type: string;
  status: string;
  frequency: string;
  config?: any | null;
  parameters?: any | null;
  tags?: string[] | null;
  generated_at?: string | null;
  scheduled_at?: string | null;
  created_by?: number | null;
  created_at: string;
  updated_at: string;
}

export interface ReportAnalytics {
  total_reports: number;
  reports_by_type: Record<string, number>;
  reports_by_status: Record<string, number>;
  reports_by_frequency: Record<string, number>;
  avg_generation_time_ms: number;
  most_accessed_reports: { id: number; title: string; access_count: number }[];
  recent_trends: { period: string; count: number }[];
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  channel: string;
  status: string;
  priority: string;
  recipient_email?: string | null;
  recipient_phone?: string | null;
  user_id?: number | null;
  signal_id?: number | null;
  metadata?: any | null;
  sent_at?: string | null;
  read_at?: string | null;
  created_at: string;
}

export interface NotificationStats {
  total_sent: number;
  sent_by_channel: Record<string, number>;
  sent_by_type: Record<string, number>;
  delivery_rate: number;
  read_rate: number;
  failed_count: number;
}

export interface AdminDashboard {
  total_signals: number;
  open_signals: number;
  resolved_signals: number;
  total_users: number;
  active_users: number;
  signals_by_status: Record<string, number>;
  signals_by_category: Record<string, number>;
  signals_by_priority: Record<string, number>;
  avg_resolution_time_hours: number;
  citizen_satisfaction_rate: number;
  recent_signals: Signal[];
  recent_users: User[];
  signals_by_month: Record<string, number>;
  top_categories: { id: number; name: string; count: number }[];
  sector_performance: { sector_id: number; sector_name: string; resolved: number; avg_time: number }[];
}

export interface SystemConfig {
  app_name: string;
  app_version: string;
  environment: string;
  debug: boolean;
  access_token_expire_minutes: number;
  refresh_token_expire_days: number;
  ai_confidence_threshold: number;
  max_file_size: number;
  rate_limit_per_minute: number;
  allowed_origins: string[];
}

export interface SystemHealth {
  status: string;
  database: string;
  version: string;
}

export interface MapGeocodeResult {
  latitude: number;
  longitude: number;
  formatted_address: string;
  components: Record<string, string>;
  place_id?: string;
  source: string;
  accuracy?: string;
}

export interface MapHeatmapPoint {
  latitude: number;
  longitude: number;
  intensity: number;
  count: number;
  avg_priority: number;
  signals: { id: number; latitude: number; longitude: number; priority: number }[];
}

export interface MapHeatmapData {
  bounds: { lat_min: number; lat_max: number; lng_min: number; lng_max: number };
  grid_size: number;
  period_days: number;
  total_signals: number;
  grid_cells: number;
  heatmap_points: MapHeatmapPoint[];
  max_intensity: number;
}

export interface MapClusterItem {
  cluster_id: string;
  center: { latitude: number; longitude: number };
  signal_count: number;
  radius_meters: number;
  signals: { id: number; reference_number: string; title: string; status: string; latitude: number; longitude: number }[];
}

export interface MapClusterData {
  bounds: { lat_min: number; lat_max: number; lng_min: number; lng_max: number };
  zoom_level: number;
  cluster_radius_pixels: number;
  total_signals: number;
  total_clusters: number;
  clusters: MapClusterItem[];
}

export interface MapNearbySignal {
  id: number;
  reference_number: string;
  title: string;
  status: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  category_id?: number;
  priority_id?: number;
  created_at?: string;
}

export interface MapCombinedData {
  center: { latitude: number; longitude: number };
  radius_km: number;
  bounds: { lat_min: number; lat_max: number; lng_min: number; lng_max: number };
  heatmap: MapHeatmapData | null;
  clusters: MapClusterData | null;
  nearby: {
    center: { latitude: number; longitude: number };
    radius_km: number;
    total_nearby: number;
    signals: MapNearbySignal[];
    filters_applied: { status: string[] | null; limit: number };
  } | null;
}

export interface MapPlacesResult {
  places: {
    place_id: string;
    name: string;
    formatted_address: string;
    latitude: number;
    longitude: number;
    rating?: number;
    types: string[];
    source: string;
  }[];
}

export interface MapDistanceResult {
  distance_km: number;
  distance_text: string;
  duration_minutes: number;
  duration_text: string;
  origin: { latitude: number; longitude: number };
  destination: { latitude: number; longitude: number };
  mode: string;
  source: string;
}

export interface MapAddressValidation {
  address: string;
  is_valid: boolean;
  geocoded: MapGeocodeResult;
  confidence: string;
  issues: string[];
}

export interface AIClassification {
  predicted_category: string;
  predicted_category_id: number | null;
  confidence_score: number;
  all_scores: Record<string, number>;
  processing_time_ms: number;
  model_version: string;
  features_used: { text_analysis: boolean; image_analysis: boolean; location_analysis: boolean };
  classification_method: string;
}

export interface AIPriorityAssessment {
  priority_score: number;
  priority_level: string;
  priority_level_value: number;
  predicted_priority_id: number | null;
  severity_score: number;
  urgency_score: number;
  impact_score: number;
  confidence: number;
  processing_time_ms: number;
  model_version: string;
  factors: Record<string, boolean>;
  recommendation: { action: string; response_time: string; resources: string; notify: string[] };
}

export interface AITrendPrediction {
  predicted_total_signals: number;
  prediction_period_days: number;
  category: string;
  daily_predictions: { date: string; predicted_signals: number; confidence: number }[];
  weekly_breakdown: Record<string, number>;
  trend_direction: string;
  trend_strength: number;
  seasonal_factor: number;
  confidence_level: number;
  model_version: string;
  methodology: string;
  factors: Record<string, boolean>;
}

export interface AIAnomalyDetection {
  anomalies_detected: boolean;
  anomaly_count: number;
  anomaly_score: number;
  anomalies: { type: string; severity: string; detail: string; score: number }[];
  processing_time_ms: number;
  model_version: string;
  risk_level: string;
}

export interface AISeverityAnalysis {
  classification: AIClassification;
  priority_assessment: AIPriorityAssessment;
  anomalies: AIAnomalyDetection;
  summary: {
    category: string;
    confidence: number;
    priority_level: string;
    priority_score: number;
    anomalies_detected: boolean;
  };
}

export interface AIReport {
  report_id: string;
  report_code: string;
  signal_id: number;
  reference_number: string;
  summary: string;
  key_findings: string[];
  recommendations: string[];
  classification: AIClassification;
  priority_assessment: AIPriorityAssessment;
  ai_insights: { classification_details: any; priority_details: any; signal_metrics: any };
  predicted_trend: AITrendPrediction;
  anomalies_detected: AIAnomalyDetection;
  model_version: string;
  ai_confidence_score: number;
  processing_time_ms: number;
  generated_at: string;
  status: string;
}

export interface AIModelInfo {
  name: string;
  version: string;
  type: string;
  framework: string;
  input_format: string;
  confidence_threshold: number;
  supported_languages: string[];
  status: string;
  config: { confidence_threshold: number; model_path: string | null; environment: string };
  capabilities: string[];
  supported_categories: string[];
  performance_metrics: { avg_processing_time_ms: number; throughput_per_second: number; uptime_percentage: number };
}

export interface AIInsights {
  model: AIModelInfo;
  trends: AITrendPrediction;
  dashboard: {
    predicted_signals_next_30d: number;
    trend_direction: string;
    confidence_level: number;
    weekly_breakdown: Record<string, number>;
  };
}

export interface AnalyticsDashboard {
  total_signals: number;
  open_signals: number;
  resolved_signals: number;
  resolution_rate: number;
  avg_response_time_hours: number;
  avg_resolution_time_hours: number;
  citizen_satisfaction_rate: number;
  signals_by_status: Record<string, number>;
  signals_by_category: Record<string, number>;
  signals_by_priority: Record<string, number>;
  recent_trends: { period: string; count: number }[];
}

export interface AnalyticsTrends {
  periods: { date: string; total: number; open: number; resolved: number }[];
  category_trends: Record<string, number[]>;
  priority_trends: Record<string, number[]>;
  summary: { total_signals: number; avg_daily: number; growth_rate: number };
}

export interface AnalyticsSectorPerformance {
  sectors: { id: number; name: string; total_signals: number; resolved: number; avg_response_time: number; avg_resolution_time: number; satisfaction: number }[];
  summary: { best_sector: string; worst_sector: string; avg_response_time: number };
}

export interface AnalyticsCategoryBreakdown {
  categories: { id: number; name: string; count: number; percentage: number; trend: number }[];
  total: number;
}

export interface AnalyticsSatisfaction {
  overall_score: number;
  total_feedback: number;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
  trends: { period: string; score: number }[];
}

export interface AnalyticsResponseTimes {
  avg_response_time: number;
  avg_resolution_time: number;
  median_response_time: number;
  max_response_time: number;
  by_priority: Record<string, { avg_response_time: number; count: number }>;
  by_category: Record<string, { avg_response_time: number; count: number }>;
  by_sector: Record<string, { avg_response_time: number; count: number }>;
}

export interface AnalyticsPredictions {
  predicted_total: number;
  prediction_period_days: number;
  confidence: number;
  daily_predictions: { date: string; predicted: number; lower_bound: number; upper_bound: number }[];
  trend_direction: string;
  trend_strength: number;
  seasonal_factors: Record<string, number>;
}

export interface AnalyticsHotspots {
  hotspots: { latitude: number; longitude: number; density: number; signal_count: number; avg_priority: number; area_name: string }[];
  bounds: { lat_min: number; lat_max: number; lng_min: number; lng_max: number };
  total_hotspots: number;
}

export interface AnalyticsTemporalPatterns {
  by_hour: Record<string, number>;
  by_day_of_week: Record<string, number>;
  by_month: Record<string, number>;
  peak_hours: number[];
  peak_day: string;
  busiest_month: string;
  description: string;
}

export interface AnalyticsSummaryReport {
  generated_at: string;
  period_days: number;
  metrics: AnalyticsDashboard;
  trends: AnalyticsTrends;
  sector_performance: AnalyticsSectorPerformance;
  category_breakdown: AnalyticsCategoryBreakdown;
  satisfaction: AnalyticsSatisfaction;
  response_times: AnalyticsResponseTimes;
  predictions: AnalyticsPredictions;
  hotspots: AnalyticsHotspots;
  temporal_patterns: AnalyticsTemporalPatterns;
  summary_text: string;
}
