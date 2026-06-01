"""
Category Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des catégories
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class CategoryBase(BaseModel):
    """Schéma de base pour les catégories"""
    name: str = Field(..., min_length=2, max_length=100, description="Nom de la catégorie")
    code: str = Field(..., min_length=2, max_length=50, description="Code unique")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    parent_id: Optional[int] = Field(None, ge=0, description="ID de la catégorie parente")
    level: int = Field(1, ge=1, le=5, description="Niveau hiérarchique")
    sort_order: int = Field(0, ge=0, description="Ordre de tri")
    category_type: str = Field(..., description="Type de catégorie")
    default_priority_level: int = Field(3, ge=1, le=5, description="Priorité par défaut")
    default_severity_level: int = Field(2, ge=1, le=5, description="Sévérité par défaut")
    
    @validator('code')
    def validate_code(cls, v):
        """Validation du code de catégorie"""
        if not v.isalnum() and '_' not in v:
            raise ValueError('Le code ne doit contenir que des lettres, chiffres et underscores')
        return v.upper()


class CategoryCreate(CategoryBase):
    """Schéma pour la création de catégorie"""
    icon: Optional[str] = Field(None, max_length=50, description="Icône")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Couleur hex")
    marker_icon: Optional[str] = Field(None, max_length=500, description="URL icône marqueur")
    ai_keywords: Optional[List[str]] = Field(None, max_items=20, description="Mots-clés IA")
    ai_confidence_threshold: int = Field(70, ge=0, le=100, description="Seuil confiance IA")
    requires_image_verification: bool = Field(False, description="Vérification image requise")
    default_processing_time_hours: int = Field(24, ge=1, le=8760, description="Temps traitement par défaut")
    auto_assignment_enabled: bool = Field(True, description="Assignation automatique")
    requires_approval: bool = Field(False, description="Approbation requise")
    responsible_sectors: Optional[List[int]] = Field(None, description="Secteurs responsables")
    escalation_sectors: Optional[List[int]] = Field(None, description="Secteurs escalation")
    auto_notify_citizen: bool = Field(True, description="Notification citoyen auto")
    auto_notify_sector: bool = Field(True, description="Notification secteur auto")
    required_fields: Optional[List[str]] = Field(None, description="Champs obligatoires")
    optional_fields: Optional[List[str]] = Field(None, description="Champs optionnels")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Règles validation")


class CategoryUpdate(BaseModel):
    """Schéma pour la mise à jour de catégorie"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[int] = Field(None, ge=0)
    sort_order: Optional[int] = Field(None, ge=0)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    marker_icon: Optional[str] = Field(None, max_length=500)
    default_priority_level: Optional[int] = Field(None, ge=1, le=5)
    default_severity_level: Optional[int] = Field(None, ge=1, le=5)
    ai_keywords: Optional[List[str]] = Field(None, max_items=20)
    ai_confidence_threshold: Optional[int] = Field(None, ge=0, le=100)
    requires_image_verification: Optional[bool] = None
    default_processing_time_hours: Optional[int] = Field(None, ge=1, le=8760)
    auto_assignment_enabled: Optional[bool] = None
    requires_approval: Optional[bool] = None
    responsible_sectors: Optional[List[int]] = None
    escalation_sectors: Optional[List[int]] = None
    auto_notify_citizen: Optional[bool] = None
    auto_notify_sector: Optional[bool] = None
    required_fields: Optional[List[str]] = None
    optional_fields: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class CategoryResponse(BaseModel):
    """Schéma de réponse pour les catégories"""
    id: int
    name: str
    code: str
    description: Optional[str]
    parent_id: Optional[int]
    level: int
    sort_order: int
    category_type: str
    status: str
    icon: Optional[str]
    color: Optional[str]
    marker_icon: Optional[str]
    default_priority_level: int
    default_severity_level: int
    ai_confidence_threshold: int
    requires_image_verification: bool
    default_processing_time_hours: int
    auto_assignment_enabled: bool
    requires_approval: bool
    responsible_sectors: Optional[List[int]]
    escalation_sectors: Optional[List[int]]
    auto_notify_citizen: bool
    auto_notify_sector: bool
    required_fields: Optional[List[str]]
    optional_fields: Optional[List[str]]
    validation_rules: Optional[Dict[str, Any]]
    total_signals: int
    avg_resolution_time_hours: int
    satisfaction_rate: int
    created_at: datetime
    updated_at: datetime
    
    # Relations
    subcategories: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True


class CategoryTree(BaseModel):
    """Schéma pour l'arborescence des catégories"""
    id: int
    name: str
    code: str
    level: int
    icon: Optional[str]
    color: Optional[str]
    children: List['CategoryTree'] = []
    
    class Config:
        from_attributes = True


class CategoryStats(BaseModel):
    """Schéma pour les statistiques de catégorie"""
    id: int
    name: str
    code: str
    total_signals: int
    active_signals: int
    resolved_signals: int
    avg_resolution_time_hours: float
    citizen_satisfaction_rate: float
    signals_by_priority: Dict[str, int]
    signals_by_status: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class CategoryFilter(BaseModel):
    """Schéma pour le filtrage des catégories"""
    category_type: Optional[str] = None
    status: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    has_children: Optional[bool] = None
    auto_assignment_enabled: Optional[bool] = None
    requires_approval: Optional[bool] = None


class CategoryBulkAction(BaseModel):
    """Schéma pour les actions en masse sur les catégories"""
    category_ids: List[int] = Field(..., min_items=1, max_items=50, description="IDs des catégories")
    action: str = Field(..., description="Action à effectuer")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres de l'action")


class CategoryImport(BaseModel):
    """Schéma pour l'import de catégories"""
    categories: List[CategoryCreate] = Field(..., min_items=1, description="Catégories à importer")
    overwrite_existing: bool = Field(False, description="Écraser les catégories existantes")
    validate_hierarchy: bool = Field(True, description="Valider la hiérarchie")


class CategoryExport(BaseModel):
    """Schéma pour l'export de catégories"""
    format: str = Field("json", pattern="^(json|csv|xlsx)$", description="Format d'export")
    include_stats: bool = Field(False, description="Inclure les statistiques")
    include_children: bool = Field(True, description="Inclure les sous-catégories")
    filters: Optional[CategoryFilter] = None


class CategoryValidation(BaseModel):
    """Schéma pour la validation de catégorie"""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    parent_id: Optional[int] = None
    
    @validator('code')
    def validate_code_uniqueness(cls, v):
        """Validation d'unicité du code (à implémenter)"""
        # TODO: Vérifier l'unicité en base de données
        return v.upper()


class CategoryHierarchy(BaseModel):
    """Schéma pour la hiérarchie des catégories"""
    category_id: int
    parent_id: Optional[int]
    path: str
    depth: int
    children_count: int
    
    class Config:
        from_attributes = True


class CategoryUsage(BaseModel):
    """Schéma pour l'utilisation des catégories"""
    category_id: int
    category_name: str
    usage_count: int
    last_used: Optional[datetime]
    popularity_score: float
    
    class Config:
        from_attributes = True


# Résolution des références circulaires pour CategoryTree
CategoryTree.model_rebuild()
