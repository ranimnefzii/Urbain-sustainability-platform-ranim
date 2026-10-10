"""
Category Model - Urbain Sustainability System
Modèle pour les catégories de problèmes urbains
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class CategoryType(enum.Enum):
    """Types principaux de catégories"""
    INFRASTRUCTURE = "infrastructure"
    ENVIRONMENT = "environment"
    SAFETY = "safety"
    SERVICES = "services"
    ADMINISTRATION = "administration"


class CategoryStatus(enum.Enum):
    """Statuts des catégories"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Category(Base):
    """
    Modèle catégorie pour classifier les problèmes urbains
    Structure hiérarchique pour organisation logique
    """
    __tablename__ = "categories"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Hiérarchie
    parent_id = Column(Integer, nullable=True, index=True)  # Pour sous-catégories
    level = Column(Integer, default=1, nullable=False)  # Niveau hiérarchique
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Type et statut
    category_type = Column(Enum(CategoryType), nullable=False, index=True)
    status = Column(Enum(CategoryStatus), default=CategoryStatus.ACTIVE, nullable=False)
    
    # Configuration visuelle
    icon = Column(String(50), nullable=True)  # Nom icône (ex: "water-drop")
    color = Column(String(7), nullable=True)  # Code couleur hex (ex: "#FF5733")
    marker_icon = Column(String(100), nullable=True)  # URL icône pour carte
    
    # Priorité par défaut
    default_priority_level = Column(Integer, default=3, nullable=False)  # 1-5
    default_severity_level = Column(Integer, default=2, nullable=False)  # 1-5
    
    # Configuration IA
    ai_keywords = Column(JSON, nullable=True)  # Mots-clés pour classification IA
    ai_confidence_threshold = Column(Integer, default=70, nullable=False)  # 0-100
    requires_image_verification = Column(Boolean, default=False, nullable=False)
    
    # Configuration traitement
    default_processing_time_hours = Column(Integer, default=24, nullable=False)
    auto_assignment_enabled = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    
    # Secteurs responsables
    responsible_sectors = Column(JSON, nullable=True)  # IDs des secteurs responsables
    escalation_sectors = Column(JSON, nullable=True)  # IDs des secteurs pour escalation
    
    # Configuration notification
    notification_templates = Column(JSON, nullable=True)  # Templates personnalisés
    auto_notify_citizen = Column(Boolean, default=True, nullable=False)
    auto_notify_sector = Column(Boolean, default=True, nullable=False)
    
    # Configuration formulaire
    required_fields = Column(JSON, nullable=True)  # Champs obligatoires
    optional_fields = Column(JSON, nullable=True)  # Champs optionnels
    validation_rules = Column(JSON, nullable=True)  # Règles de validation
    
    # Statistiques
    total_signals = Column(Integer, default=0, nullable=False)
    avg_resolution_time_hours = Column(Integer, default=0, nullable=False)
    satisfaction_rate = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    signals = relationship("Signal", back_populates="category")
    # subcategories relationship disabled - needs FK constraint on parent_id
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, type={self.category_type.value})>"
    
    @property
    def is_active(self) -> bool:
        """Vérifie si la catégorie est active"""
        return self.status == CategoryStatus.ACTIVE
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet"""
        return self.name
    
    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage avec icône"""
        icon_prefix = f"🔧" if self.icon else "📌"
        return f"{icon_prefix} {self.name}"
    
    def can_be_assigned_to_sector(self, sector_id: int) -> bool:
        """Vérifie si la catégorie peut être assignée à un secteur"""
        if not self.responsible_sectors:
            return True  # Si pas de restriction, tous les secteurs
        return sector_id in self.responsible_sectors
    
    def get_escalation_sectors(self) -> list:
        """Retourne la liste des secteurs d'escalation"""
        return self.escalation_sectors or []
    
    def get_required_fields_list(self) -> list:
        """Retourne la liste des champs obligatoires"""
        default_fields = ["title", "description", "location"]
        if self.required_fields:
            return list(set(default_fields + self.required_fields))
        return default_fields
    
    def get_validation_rules_dict(self) -> dict:
        """Retourne les règles de validation comme dictionnaire"""
        default_rules = {
            "title": {"min_length": 5, "max_length": 200},
            "description": {"min_length": 10, "max_length": 1000},
            "location": {"required": True}
        }
        if self.validation_rules:
            default_rules.update(self.validation_rules)
        return default_rules
    
    def calculate_priority_score(self, severity: int, urgency: int) -> int:
        """Calcule le score de priorité basé sur sévérité et urgence"""
        base_score = (severity * 0.6) + (urgency * 0.4)
        category_weight = self.default_priority_level * 0.2
        return min(5, max(1, int(base_score + category_weight)))
    
    def get_ai_keywords_list(self) -> list:
        """Retourne la liste des mots-clés IA"""
        if not self.ai_keywords:
            return [self.name.lower(), self.code.lower()]
        return self.ai_keywords
