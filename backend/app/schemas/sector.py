"""
Sector Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des secteurs
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class SectorBase(BaseModel):
    """Schéma de base pour les secteurs"""
    name: str = Field(..., min_length=2, max_length=100, description="Nom du secteur")
    code: str = Field(..., min_length=2, max_length=20, description="Code unique")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    sector_type: str = Field(..., description="Type de secteur")
    
    @validator('code')
    def validate_code(cls, v):
        """Validation du code de secteur"""
        if not v.isalnum() and '_' not in v:
            raise ValueError('Le code ne doit contenir que des lettres, chiffres et underscores')
        return v.upper()


class SectorCreate(SectorBase):
    """Schéma pour la création de secteur"""
    email: Optional[str] = Field(None, description="Email du secteur")
    phone: Optional[str] = Field(None, description="Téléphone du secteur")
    address: Optional[str] = Field(None, max_length=500, description="Adresse")
    city: Optional[str] = Field(None, max_length=100, description="Ville")
    postal_code: Optional[str] = Field(None, max_length=20, description="Code postal")
    manager_name: Optional[str] = Field(None, max_length=100, description="Nom du responsable")
    manager_email: Optional[str] = Field(None, description="Email du responsable")
    manager_phone: Optional[str] = Field(None, description="Téléphone du responsable")
    working_hours: Optional[Dict[str, str]] = Field(None, description="Heures de travail")
    emergency_contact: Optional[Dict[str, str]] = Field(None, description="Contact d'urgence")
    max_daily_signals: int = Field(100, ge=1, le=10000, description="Max signalements/jour")
    avg_processing_time_hours: int = Field(24, ge=1, le=8760, description="Temps traitement moyen")
    priority_level: int = Field(3, ge=1, le=5, description="Niveau de priorité")
    email_templates: Optional[Dict[str, Any]] = Field(None, description="Templates email")
    auto_assignment_enabled: bool = Field(True, description="Assignation automatique")
    escalation_enabled: bool = Field(True, description="Escalation activée")
    ai_confidence_threshold: int = Field(70, ge=0, le=100, description="Seuil confiance IA")
    supported_categories: Optional[List[int]] = Field(None, description="Catégories supportées")
    external_systems: Optional[Dict[str, Any]] = Field(None, description="Systèmes externes")
    api_endpoints: Optional[Dict[str, str]] = Field(None, description="Endpoints API")
    
    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format d\'email invalide')
        return v
    
    @validator('manager_email')
    def validate_manager_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format d\'email invalide')
        return v
    
    @validator('phone', 'manager_phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Format de téléphone invalide')
        return v


class SectorUpdate(BaseModel):
    """Schéma pour la mise à jour de secteur"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    manager_name: Optional[str] = Field(None, max_length=100)
    manager_email: Optional[str] = None
    manager_phone: Optional[str] = None
    working_hours: Optional[Dict[str, str]] = None
    emergency_contact: Optional[Dict[str, str]] = None
    max_daily_signals: Optional[int] = Field(None, ge=1, le=10000)
    avg_processing_time_hours: Optional[int] = Field(None, ge=1, le=8760)
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    email_templates: Optional[Dict[str, Any]] = None
    auto_assignment_enabled: Optional[bool] = None
    escalation_enabled: Optional[bool] = None
    ai_confidence_threshold: Optional[int] = Field(None, ge=0, le=100)
    supported_categories: Optional[List[int]] = None
    external_systems: Optional[Dict[str, Any]] = None
    api_endpoints: Optional[Dict[str, str]] = None


class SectorResponse(BaseModel):
    """Schéma de réponse pour les secteurs"""
    id: int
    name: str
    code: str
    description: Optional[str]
    sector_type: str
    status: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    manager_name: Optional[str]
    manager_email: Optional[str]
    manager_phone: Optional[str]
    working_hours: Optional[Dict[str, str]]
    emergency_contact: Optional[Dict[str, str]]
    max_daily_signals: int
    avg_processing_time_hours: int
    priority_level: int
    email_templates: Optional[Dict[str, Any]]
    auto_assignment_enabled: bool
    escalation_enabled: bool
    ai_confidence_threshold: int
    supported_categories: Optional[List[int]]
    external_systems: Optional[Dict[str, Any]]
    api_endpoints: Optional[Dict[str, str]]
    total_signals_processed: int
    avg_resolution_time_hours: int
    satisfaction_rate: int
    created_at: datetime
    updated_at: datetime
    
    # Relations
    users: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True


class SectorStats(BaseModel):
    """Schéma pour les statistiques de secteur"""
    id: int
    name: str
    code: str
    sector_type: str
    total_signals_processed: int
    active_signals: int
    resolved_signals: int
    avg_resolution_time_hours: float
    satisfaction_rate: float
    signals_by_category: Dict[str, int]
    signals_by_priority: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]
    performance_score: float
    
    class Config:
        from_attributes = True


class SectorPerformance(BaseModel):
    """Schéma pour la performance de secteur"""
    sector_id: int
    sector_name: str
    period_start: datetime
    period_end: datetime
    total_signals: int
    processed_signals: int
    resolved_signals: int
    avg_processing_time_hours: float
    resolution_rate: float
    escalation_rate: float
    citizen_satisfaction: float
    efficiency_score: float
    workload_percentage: float
    response_time_compliance: float
    
    class Config:
        from_attributes = True


class SectorFilter(BaseModel):
    """Schéma pour le filtrage des secteurs"""
    sector_type: Optional[str] = None
    status: Optional[str] = None
    auto_assignment_enabled: Optional[bool] = None
    escalation_enabled: Optional[bool] = None
    manager_email: Optional[str] = None
    city: Optional[str] = None


class SectorBulkAction(BaseModel):
    """Schéma pour les actions en masse sur les secteurs"""
    sector_ids: List[int] = Field(..., min_items=1, max_items=50, description="IDs des secteurs")
    action: str = Field(..., description="Action à effectuer")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres de l'action")


class SectorImport(BaseModel):
    """Schéma pour l'import de secteurs"""
    sectors: List[SectorCreate] = Field(..., min_items=1, description="Secteurs à importer")
    overwrite_existing: bool = Field(False, description="Écraser les secteurs existants")
    validate_categories: bool = Field(True, description="Valider les catégories")


class SectorExport(BaseModel):
    """Schéma pour l'export de secteurs"""
    format: str = Field("json", pattern="^(json|csv|xlsx)$", description="Format d'export")
    include_stats: bool = Field(False, description="Inclure les statistiques")
    include_users: bool = Field(False, description="Inclure les utilisateurs")
    filters: Optional[SectorFilter] = None


class SectorValidation(BaseModel):
    """Schéma pour la validation de secteur"""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    sector_type: str = Field(..., description="Type de secteur")
    email: Optional[str] = None
    manager_email: Optional[str] = None
    
    @validator('code')
    def validate_code_uniqueness(cls, v):
        """Validation d'unicité du code (à implémenter)"""
        # TODO: Vérifier l'unicité en base de données
        return v.upper()


class SectorWorkload(BaseModel):
    """Schéma pour la charge de travail de secteur"""
    sector_id: int
    sector_name: str
    current_workload: int
    max_capacity: int
    utilization_percentage: float
    pending_signals: int
    in_progress_signals: int
    overdue_signals: int
    avg_processing_time_current: float
    estimated_completion_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class SectorIntegration(BaseModel):
    """Schéma pour l'intégration de secteur"""
    sector_id: int
    system_name: str
    integration_type: str
    configuration: Dict[str, Any]
    is_active: bool
    last_sync: Optional[datetime]
    sync_status: str
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class SectorContact(BaseModel):
    """Schéma pour les contacts de secteur"""
    sector_id: int
    contact_type: str
    contact_value: str
    is_primary: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
