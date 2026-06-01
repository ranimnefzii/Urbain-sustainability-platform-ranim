"""
Signal Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des signalements
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class SignalLocation(BaseModel):
    """Schéma pour la localisation des signalements"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    address: Optional[str] = Field(None, max_length=500, description="Adresse")
    postal_code: Optional[str] = Field(None, max_length=20, description="Code postal")
    city: Optional[str] = Field(None, max_length=100, description="Ville")
    country: str = Field("Tunisia", max_length=100, description="Pays")
    location_accuracy: Optional[float] = Field(None, ge=0, description="Précision GPS en mètres")
    location_description: Optional[str] = Field(None, max_length=1000, description="Description détaillée")


class SignalBase(BaseModel):
    """Schéma de base pour les signalements"""
    title: str = Field(..., min_length=5, max_length=200, description="Titre du signalement")
    description: str = Field(..., min_length=10, max_length=2000, description="Description détaillée")
    category_id: int = Field(..., gt=0, description="ID de la catégorie")
    location: SignalLocation = Field(..., description="Localisation du signalement")
    is_anonymous: bool = Field(False, description="Signalement anonyme")
    allow_contact: bool = Field(True, description="Autoriser le contact")
    
    @validator('title')
    def validate_title(cls, v):
        """Validation du titre"""
        if not v.strip():
            raise ValueError('Le titre ne peut pas être vide')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validation de la description"""
        if not v.strip():
            raise ValueError('La description ne peut pas être vide')
        return v.strip()


class SignalCreate(SignalBase):
    """Schéma pour la création de signalement"""
    images: Optional[List[str]] = Field(None, max_items=10, description="URLs des images")
    videos: Optional[List[str]] = Field(None, max_items=5, description="URLs des vidéos")
    documents: Optional[List[str]] = Field(None, max_items=5, description="URLs des documents")
    audio_files: Optional[List[str]] = Field(None, max_items=3, description="URLs des fichiers audio")
    estimated_damage_cost: Optional[float] = Field(None, ge=0, description="Coût estimé des dommages")
    affected_people_count: Optional[int] = Field(None, ge=0, description="Nombre de personnes affectées")
    affected_area_sqm: Optional[float] = Field(None, ge=0, description="Surface affectée en m²")
    safety_risk_level: Optional[int] = Field(None, ge=1, le=5, description="Niveau de risque de sécurité")


class SignalUpdate(BaseModel):
    """Schéma pour la mise à jour de signalement"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category_id: Optional[int] = Field(None, gt=0)
    location: Optional[SignalLocation] = None
    images: Optional[List[str]] = Field(None, max_items=10)
    videos: Optional[List[str]] = Field(None, max_items=5)
    documents: Optional[List[str]] = Field(None, max_items=5)
    audio_files: Optional[List[str]] = Field(None, max_items=3)
    estimated_damage_cost: Optional[float] = Field(None, ge=0)
    affected_people_count: Optional[int] = Field(None, ge=0)
    affected_area_sqm: Optional[float] = Field(None, ge=0)
    safety_risk_level: Optional[int] = Field(None, ge=1, le=5)
    is_anonymous: Optional[bool] = None
    allow_contact: Optional[bool] = None


class SignalResponse(BaseModel):
    """Schéma de réponse pour les signalements"""
    id: int
    reference_number: str
    title: str
    description: str
    status: str
    source: str
    verification_status: str
    latitude: float
    longitude: float
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    country: str
    location_accuracy: Optional[float]
    location_description: Optional[str]
    images: Optional[List[str]]
    videos: Optional[List[str]]
    documents: Optional[List[str]]
    audio_files: Optional[List[str]]
    ai_confidence_score: Optional[float]
    ai_priority_score: Optional[float]
    ai_severity_score: Optional[float]
    ai_urgency_score: Optional[float]
    estimated_damage_cost: Optional[float]
    affected_people_count: Optional[int]
    affected_area_sqm: Optional[float]
    safety_risk_level: Optional[int]
    assigned_at: Optional[datetime]
    started_processing_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    resolution_description: Optional[str]
    resolution_method: Optional[str]
    resolution_cost: Optional[float]
    resolution_images: Optional[List[str]]
    citizen_satisfaction: Optional[int]
    citizen_feedback: Optional[str]
    citizen_response_time_hours: Optional[int]
    is_public: bool
    is_anonymous: bool
    allow_contact: bool
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    
    # Relations
    created_by_user: Optional[Dict[str, Any]]
    processed_by_user: Optional[Dict[str, Any]]
    category: Optional[Dict[str, Any]]
    priority: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class SignalList(BaseModel):
    """Schéma pour la liste des signalements"""
    items: List[SignalResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True


class SignalAnalytics(BaseModel):
    """Schéma pour les analytics des signalements"""
    total_signals: int
    signals_by_status: Dict[str, int]
    signals_by_category: Dict[str, int]
    signals_by_priority: Dict[str, int]
    avg_resolution_time_hours: float
    citizen_satisfaction_rate: float
    signals_by_month: Dict[str, int]
    geographic_hotspots: List[Dict[str, Any]]
    recent_trends: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class SignalFilter(BaseModel):
    """Schéma pour le filtrage des signalements"""
    status: Optional[List[str]] = None
    category_id: Optional[List[int]] = None
    priority_id: Optional[List[int]] = None
    created_by: Optional[int] = None
    assigned_sector_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    latitude_min: Optional[float] = None
    latitude_max: Optional[float] = None
    longitude_min: Optional[float] = None
    longitude_max: Optional[float] = None
    is_anonymous: Optional[bool] = None
    has_images: Optional[bool] = None
    ai_confidence_min: Optional[float] = Field(None, ge=0, le=1)
    citizen_satisfaction_min: Optional[int] = Field(None, ge=1, le=5)


class SignalStatusUpdate(BaseModel):
    """Schéma pour la mise à jour du statut"""
    status: str = Field(..., description="Nouveau statut")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes internes")
    resolution_description: Optional[str] = Field(None, max_length=2000, description="Description de la résolution")
    resolution_method: Optional[str] = Field(None, max_length=100, description="Méthode de résolution")
    resolution_cost: Optional[float] = Field(None, ge=0, description="Coût de résolution")
    resolution_images: Optional[List[str]] = Field(None, max_items=10, description="Images après résolution")


class SignalAssignment(BaseModel):
    """Schéma pour l'assignation de signalement"""
    assigned_to_user_id: int = Field(..., gt=0, description="ID de l'utilisateur assigné")
    assigned_sector_id: Optional[int] = Field(None, gt=0, description="ID du secteur assigné")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes d'assignation")


class SignalFeedback(BaseModel):
    """Schéma pour le feedback citoyen"""
    citizen_satisfaction: int = Field(..., ge=1, le=5, description="Satisfaction (1-5)")
    citizen_feedback: Optional[str] = Field(None, max_length=1000, description="Feedback détaillé")
    
    @validator('citizen_satisfaction')
    def validate_satisfaction(cls, v):
        if v < 1 or v > 5:
            raise ValueError('La satisfaction doit être entre 1 et 5')
        return v


class SignalSearch(BaseModel):
    """Schéma pour la recherche de signalements"""
    query: str = Field(..., min_length=2, max_length=100, description="Requête de recherche")
    filters: Optional[SignalFilter] = None
    sort_by: Optional[str] = Field("created_at", description="Champ de tri")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Ordre de tri")
    page: int = Field(1, ge=1, description="Page")
    size: int = Field(20, ge=1, le=100, description="Taille de la page")


class SignalBulkAction(BaseModel):
    """Schéma pour les actions en masse sur les signalements"""
    signal_ids: List[int] = Field(..., min_items=1, max_items=100, description="IDs des signalements")
    action: str = Field(..., description="Action à effectuer")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres de l'action")


class SignalExport(BaseModel):
    """Schéma pour l'export des signalements"""
    format: str = Field("csv", pattern="^(csv|xlsx|pdf|json)$", description="Format d'export")
    filters: Optional[SignalFilter] = None
    fields: Optional[List[str]] = Field(None, description="Champs à inclure")
    include_media: bool = Field(False, description="Inclure les médias")


class SignalMapData(BaseModel):
    """Schéma pour les données cartographiques"""
    id: int
    reference_number: str
    title: str
    status: str
    priority_level: Optional[str]
    category_name: Optional[str]
    latitude: float
    longitude: float
    created_at: datetime
    citizen_satisfaction: Optional[int]
    
    class Config:
        from_attributes = True


class SignalCluster(BaseModel):
    """Schéma pour les clusters de signalements"""
    cluster_id: str
    center_latitude: float
    center_longitude: float
    signal_count: int
    signals: List[SignalMapData]
    radius_meters: float
    
    class Config:
        from_attributes = True
