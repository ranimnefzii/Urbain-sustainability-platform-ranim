"""
Report Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des rapports
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class ReportBase(BaseModel):
    """Schéma de base pour les rapports"""
    title: str = Field(..., min_length=5, max_length=200, description="Titre du rapport")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    report_type: str = Field(..., description="Type de rapport")
    frequency: str = Field("on_demand", description="Fréquence du rapport")
    
    @validator('title')
    def validate_title(cls, v):
        """Validation du titre"""
        if not v.strip():
            raise ValueError('Le titre ne peut pas être vide')
        return v.strip()


class ReportCreate(ReportBase):
    """Schéma pour la création de rapport"""
    signal_id: Optional[int] = Field(None, ge=0, description="ID du signal associé")
    generated_by: Optional[int] = Field(None, ge=0, description="ID du générateur")
    sector_id: Optional[int] = Field(None, ge=0, description="ID du secteur")
    start_date: Optional[datetime] = Field(None, description="Date de début")
    end_date: Optional[datetime] = Field(None, description="Date de fin")
    analysis_period_hours: Optional[int] = Field(None, ge=1, le=8760, description="Période d'analyse en heures")
    ai_model_version: Optional[str] = Field(None, max_length=50, description="Version modèle IA")
    ai_parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres IA")
    is_public: bool = Field(False, description="Rapport public")
    auto_share_enabled: bool = Field(False, description="Partage automatique")
    notification_enabled: bool = Field(True, description="Notifications activées")
    tags: Optional[List[str]] = Field(None, max_items=20, description="Tags")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validation de la plage de dates"""
        if 'start_date' in values and v and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('La date de fin doit être postérieure à la date de début')
        return v


class ReportUpdate(BaseModel):
    """Schéma pour la mise à jour de rapport"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    analysis_period_hours: Optional[int] = Field(None, ge=1, le=8760)
    summary: Optional[str] = Field(None, max_length=5000, description="Résumé")
    key_findings: Optional[List[Dict[str, Any]]] = Field(None, description="Découvertes principales")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommandations")
    insights: Optional[List[Dict[str, Any]]] = Field(None, description="Insights")
    is_public: Optional[bool] = None
    auto_share_enabled: Optional[bool] = None
    notification_enabled: Optional[bool] = None
    tags: Optional[List[str]] = Field(None, max_items=20)
    metadata: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Schéma de réponse pour les rapports"""
    id: int
    title: str
    description: Optional[str]
    report_code: str
    report_type: str
    status: str
    frequency: str
    signal_id: Optional[int]
    generated_by: Optional[int]
    sector_id: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    analysis_period_hours: Optional[int]
    ai_model_version: Optional[str]
    ai_confidence_score: Optional[float]
    ai_processing_time_ms: Optional[int]
    ai_parameters: Optional[Dict[str, Any]]
    summary: Optional[str]
    key_findings: Optional[List[Dict[str, Any]]]
    recommendations: Optional[List[Dict[str, Any]]]
    insights: Optional[List[Dict[str, Any]]]
    total_signals_analyzed: int
    critical_signals_count: int
    high_priority_count: int
    avg_resolution_time_hours: Optional[float]
    citizen_satisfaction_rate: Optional[float]
    category_breakdown: Optional[Dict[str, Any]]
    priority_breakdown: Optional[Dict[str, Any]]
    sector_performance: Optional[Dict[str, Any]]
    geographic_hotspots: Optional[Dict[str, Any]]
    temporal_patterns: Optional[Dict[str, Any]]
    predicted_signals_next_period: Optional[int]
    trend_analysis: Optional[Dict[str, Any]]
    seasonal_patterns: Optional[Dict[str, Any]]
    anomaly_detection: Optional[Dict[str, Any]]
    system_performance: Optional[Dict[str, Any]]
    resource_utilization: Optional[Dict[str, Any]]
    bottleneck_identification: Optional[Dict[str, Any]]
    charts_data: Optional[Dict[str, Any]]
    map_visualization: Optional[Dict[str, Any]]
    dashboard_config: Optional[Dict[str, Any]]
    export_formats: Optional[List[str]]
    sharing_settings: Optional[Dict[str, Any]]
    access_permissions: Optional[Dict[str, Any]]
    is_public: bool
    auto_share_enabled: bool
    notification_enabled: bool
    file_urls: Optional[List[str]]
    thumbnail_url: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    version: int
    created_at: datetime
    updated_at: datetime
    generated_at: Optional[datetime]
    expires_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    
    # Relations
    signal: Optional[Dict[str, Any]]
    generated_by_user: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ReportList(BaseModel):
    """Schéma pour la liste des rapports"""
    items: List[ReportResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True


class ReportAnalytics(BaseModel):
    """Schéma pour les analytics de rapports"""
    total_reports: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    reports_by_frequency: Dict[str, int]
    avg_generation_time_ms: float
    most_accessed_reports: List[Dict[str, Any]]
    recent_trends: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ReportSummary(BaseModel):
    """Schéma pour le résumé de rapport"""
    report_id: int
    report_code: str
    title: str
    report_type: str
    status: str
    total_signals: int
    critical_signals: int
    high_priority_signals: int
    avg_resolution_time: float
    satisfaction_rate: float
    generated_at: Optional[datetime]
    file_size_kb: Optional[int]
    download_count: int
    
    class Config:
        from_attributes = True


class ReportFilter(BaseModel):
    """Schéma pour le filtrage des rapports"""
    report_type: Optional[str] = None
    status: Optional[str] = None
    frequency: Optional[str] = None
    generated_by: Optional[int] = None
    sector_id: Optional[int] = None
    signal_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class ReportSchedule(BaseModel):
    """Schéma pour la planification de rapports"""
    report_type: str = Field(..., description="Type de rapport")
    frequency: str = Field(..., description="Fréquence")
    scheduled_time: str = Field(..., description="Heure planifiée (HH:MM)")
    recipients: List[str] = Field(..., description="Liste des destinataires")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres du rapport")
    is_active: bool = Field(True, description="Planification active")
    
    @validator('scheduled_time')
    def validate_time_format(cls, v):
        """Validation du format de l'heure"""
        import re
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Format d\'heure invalide (HH:MM)')
        return v


class ReportExport(BaseModel):
    """Schéma pour l'export de rapports"""
    report_id: int = Field(..., gt=0, description="ID du rapport")
    format: str = Field("pdf", pattern="^(pdf|xlsx|csv|json)$", description="Format d'export")
    include_charts: bool = Field(True, description="Inclure les graphiques")
    include_raw_data: bool = Field(False, description="Inclure les données brutes")
    watermark: Optional[str] = Field(None, max_length=100, description="Filigrane")
    
    @validator('watermark')
    def validate_watermark(cls, v):
        """Validation du filigrane"""
        if v and len(v) > 100:
            raise ValueError('Le filigrane ne doit pas dépasser 100 caractères')
        return v


class ReportShare(BaseModel):
    """Schéma pour le partage de rapports"""
    report_id: int = Field(..., gt=0, description="ID du rapport")
    share_type: str = Field(..., pattern="^(public|private|link)$", description="Type de partage")
    recipients: Optional[List[str]] = Field(None, description="Destinataires")
    expires_hours: Optional[int] = Field(None, ge=1, le=8760, description="Expiration en heures")
    allow_download: bool = Field(True, description="Autoriser le téléchargement")
    password_protected: bool = Field(False, description="Protection par mot de passe")
    share_password: Optional[str] = Field(None, min_length=8, description="Mot de passe de partage")


class ReportTemplate(BaseModel):
    """Schéma pour les modèles de rapports"""
    name: str = Field(..., min_length=2, max_length=100, description="Nom du modèle")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    report_type: str = Field(..., description="Type de rapport")
    template_config: Dict[str, Any] = Field(..., description="Configuration du modèle")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres par défaut")
    is_default: bool = Field(False, description="Modèle par défaut")
    is_active: bool = Field(True, description="Modèle actif")
    
    class Config:
        from_attributes = True


class ReportBulkAction(BaseModel):
    """Schéma pour les actions en masse sur les rapports"""
    report_ids: List[int] = Field(..., min_items=1, max_items=100, description="IDs des rapports")
    action: str = Field(..., description="Action à effectuer")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres de l'action")


class ReportValidation(BaseModel):
    """Schéma pour la validation de rapport"""
    title: str = Field(..., min_length=5, max_length=200)
    report_type: str = Field(..., description="Type de rapport")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validation de la plage de dates"""
        if 'start_date' in values and v and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('La date de fin doit être postérieure à la date de début')
        return v


class ReportMetrics(BaseModel):
    """Schéma pour les métriques de rapport"""
    report_id: int
    generation_time_ms: int
    file_size_bytes: int
    download_count: int
    view_count: int
    share_count: int
    average_rating: Optional[float]
    last_accessed: Optional[datetime]
    performance_score: float
    
    class Config:
        from_attributes = True
