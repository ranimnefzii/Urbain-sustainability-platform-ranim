"""
Priority Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des priorités
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class PriorityBase(BaseModel):
    """Schéma de base pour les priorités"""
    name: str = Field(..., min_length=2, max_length=100, description="Nom de la priorité")
    code: str = Field(..., min_length=2, max_length=50, description="Code unique")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    priority_level: int = Field(..., ge=1, le=5, description="Niveau de priorité (1-5)")
    severity_level: int = Field(..., ge=1, le=5, description="Niveau de sévérité (1-5)")
    urgency_level: int = Field(..., ge=1, le=5, description="Niveau d'urgence (1-5)")
    impact_level: int = Field(..., ge=1, le=5, description="Niveau d'impact (1-5)")
    
    @validator('code')
    def validate_code(cls, v):
        """Validation du code de priorité"""
        if not v.isalnum() and '_' not in v:
            raise ValueError('Le code ne doit contenir que des lettres, chiffres et underscores')
        return v.upper()


class PriorityCreate(PriorityBase):
    """Schéma pour la création de priorité"""
    max_response_time_minutes: int = Field(..., ge=1, le=10080, description="Temps max réponse en minutes")
    max_resolution_time_hours: int = Field(..., ge=1, le=8760, description="Temps max résolution en heures")
    escalation_time_hours: int = Field(..., ge=1, le=8760, description="Temps avant escalation en heures")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Couleur hex")
    icon: Optional[str] = Field(None, max_length=50, description="Icône")
    badge_style: Optional[str] = Field(None, max_length=50, description="Style badge CSS")
    ai_weight: int = Field(1, ge=1, le=10, description="Poids dans calcul IA")
    auto_assignment_threshold: int = Field(80, ge=0, le=100, description="Seuil assignation auto")
    requires_human_review: bool = Field(False, description="Revue humaine requise")
    notification_frequency: str = Field("normal", pattern="^(immediate|normal|low)$", description="Fréquence notification")
    escalation_enabled: bool = Field(True, description="Escalation activée")
    auto_escalation_rules: Optional[Dict[str, Any]] = Field(None, description="Règles escalation auto")
    requires_approval: bool = Field(False, description="Approbation requise")
    can_be_reassigned: bool = Field(True, description="Réassignation possible")
    requires_photo_evidence: bool = Field(False, description="Preuve photo requise")
    weather_dependencies: Optional[Dict[str, Any]] = Field(None, description="Dépendances météo")
    time_restrictions: Optional[Dict[str, Any]] = Field(None, description="Restrictions horaires")
    location_restrictions: Optional[Dict[str, Any]] = Field(None, description="Restrictions géographiques")


class PriorityUpdate(BaseModel):
    """Schéma pour la mise à jour de priorité"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    severity_level: Optional[int] = Field(None, ge=1, le=5)
    urgency_level: Optional[int] = Field(None, ge=1, le=5)
    impact_level: Optional[int] = Field(None, ge=1, le=5)
    max_response_time_minutes: Optional[int] = Field(None, ge=1, le=10080)
    max_resolution_time_hours: Optional[int] = Field(None, ge=1, le=8760)
    escalation_time_hours: Optional[int] = Field(None, ge=1, le=8760)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    badge_style: Optional[str] = Field(None, max_length=50)
    ai_weight: Optional[int] = Field(None, ge=1, le=10)
    auto_assignment_threshold: Optional[int] = Field(None, ge=0, le=100)
    requires_human_review: Optional[bool] = None
    notification_frequency: Optional[str] = Field(None, pattern="^(immediate|normal|low)$")
    escalation_enabled: Optional[bool] = None
    auto_escalation_rules: Optional[Dict[str, Any]] = None
    requires_approval: Optional[bool] = None
    can_be_reassigned: Optional[bool] = None
    requires_photo_evidence: Optional[bool] = None
    weather_dependencies: Optional[Dict[str, Any]] = None
    time_restrictions: Optional[Dict[str, Any]] = None
    location_restrictions: Optional[Dict[str, Any]] = None


class PriorityResponse(BaseModel):
    """Schéma de réponse pour les priorités"""
    id: int
    name: str
    code: str
    description: Optional[str]
    priority_level: int
    severity_level: int
    urgency_level: int
    impact_level: int
    max_response_time_minutes: int
    max_resolution_time_hours: int
    escalation_time_hours: int
    color: Optional[str]
    icon: Optional[str]
    badge_style: Optional[str]
    ai_weight: int
    auto_assignment_threshold: int
    requires_human_review: bool
    notification_frequency: str
    escalation_enabled: bool
    auto_escalation_rules: Optional[Dict[str, Any]]
    requires_approval: bool
    can_be_reassigned: bool
    requires_photo_evidence: bool
    weather_dependencies: Optional[Dict[str, Any]]
    time_restrictions: Optional[Dict[str, Any]]
    location_restrictions: Optional[Dict[str, Any]]
    total_signals: int
    avg_resolution_time_hours: int
    escalation_rate: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PriorityStats(BaseModel):
    """Schéma pour les statistiques de priorité"""
    id: int
    name: str
    code: str
    priority_level: int
    total_signals: int
    active_signals: int
    resolved_signals: int
    avg_resolution_time_hours: float
    escalation_rate: float
    citizen_satisfaction_rate: float
    signals_by_status: Dict[str, int]
    signals_by_category: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class PriorityAssessment(BaseModel):
    """Schéma pour l'évaluation de priorité"""
    signal_id: int
    current_priority: Optional[str]
    suggested_priority: str
    suggested_priority_id: int
    confidence_score: float
    assessment_factors: Dict[str, Any]
    reasoning: str
    recommended_action: str
    estimated_resolution_time_hours: int
    requires_escalation: bool
    
    class Config:
        from_attributes = True


class PriorityFilter(BaseModel):
    """Schéma pour le filtrage des priorités"""
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    severity_level: Optional[int] = Field(None, ge=1, le=5)
    urgency_level: Optional[int] = Field(None, ge=1, le=5)
    impact_level: Optional[int] = Field(None, ge=1, le=5)
    requires_human_review: Optional[bool] = None
    escalation_enabled: Optional[bool] = None
    requires_approval: Optional[bool] = None


class PriorityMatrix(BaseModel):
    """Schéma pour la matrice de priorité"""
    severity: int
    urgency: int
    impact: int
    calculated_priority: int
    priority_name: str
    response_time_minutes: int
    resolution_time_hours: int
    escalation_hours: int
    
    class Config:
        from_attributes = True


class PriorityThreshold(BaseModel):
    """Schéma pour les seuils de priorité"""
    priority_level: int
    threshold_type: str
    threshold_value: float
    comparison_operator: str
    action_triggered: str
    is_active: bool
    
    class Config:
        from_attributes = True


class PriorityEscalation(BaseModel):
    """Schéma pour les règles d'escalation"""
    priority_id: int
    escalation_condition: str
    time_threshold_hours: int
    escalation_priority_id: int
    notification_recipients: List[str]
    auto_escalate: bool
    escalation_notes_template: Optional[str]
    
    class Config:
        from_attributes = True


class PriorityBulkAction(BaseModel):
    """Schéma pour les actions en masse sur les priorités"""
    priority_ids: List[int] = Field(..., min_items=1, max_items=50, description="IDs des priorités")
    action: str = Field(..., description="Action à effectuer")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres de l'action")


class PriorityImport(BaseModel):
    """Schéma pour l'import de priorités"""
    priorities: List[PriorityCreate] = Field(..., min_items=1, description="Priorités à importer")
    overwrite_existing: bool = Field(False, description="Écraser les priorités existantes")
    validate_matrix: bool = Field(True, description="Valider la matrice de priorité")


class PriorityExport(BaseModel):
    """Schéma pour l'export de priorités"""
    format: str = Field("json", pattern="^(json|csv|xlsx)$", description="Format d'export")
    include_stats: bool = Field(False, description="Inclure les statistiques")
    include_matrix: bool = Field(True, description="Inclure la matrice")
    filters: Optional[PriorityFilter] = None


class PriorityValidation(BaseModel):
    """Schéma pour la validation de priorité"""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    priority_level: int = Field(..., ge=1, le=5)
    severity_level: int = Field(..., ge=1, le=5)
    urgency_level: int = Field(..., ge=1, le=5)
    impact_level: int = Field(..., ge=1, le=5)
    
    @validator('code')
    def validate_code_uniqueness(cls, v):
        """Validation d'unicité du code (à implémenter)"""
        # TODO: Vérifier l'unicité en base de données
        return v.upper()


class PriorityUsage(BaseModel):
    """Schéma pour l'utilisation des priorités"""
    priority_id: int
    priority_name: str
    usage_count: int
    last_used: Optional[datetime]
    effectiveness_score: float
    avg_resolution_time_vs_target: float
    
    class Config:
        from_attributes = True
