"""
Priority Model - Urbain Sustainability System
Modèle pour les niveaux de priorité et criticité
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class PriorityLevel(enum.Enum):
    """Niveaux de priorité"""
    CRITICAL = 1  # Critique - Intervention immédiate
    HIGH = 2      # Élevée - Intervention < 4h
    MEDIUM = 3    # Moyenne - Intervention < 24h
    LOW = 4       # Basse - Intervention < 72h
    INFO = 5      # Information - Pas d'intervention requise


class SeverityLevel(enum.Enum):
    """Niveaux de sévérité"""
    EXTREME = 1   # Extrême - Danger de vie
    SEVERE = 2    # Sévère - Impact majeur
    MODERATE = 3  # Modéré - Impact limité
    MINOR = 4     # Mineur - Impact faible
    NONE = 5      # Aucun - Pas d'impact


class UrgencyLevel(enum.Enum):
    """Niveaux d'urgence"""
    IMMEDIATE = 1  # Immédiat - < 1h
    URGENT = 2     # Urgent - < 4h
    NORMAL = 3     # Normal - < 24h
    LOW = 4        # Faible - < 72h
    DEFERRED = 5   # Différé - > 72h


class ImpactLevel(enum.Enum):
    """Niveaux d'impact"""
    WIDESPREAD = 1  # Étendu - Toute la ville
    NEIGHBORHOOD = 2 # Quartier - Plusieurs zones
    LOCAL = 3        # Local - Une zone
    INDIVIDUAL = 4   # Individuel - Une personne
    NONE = 5         # Aucun - Pas d'impact


class Priority(Base):
    """
    Modèle priorité pour évaluer et classifier les signalements
    Utilisé par l'IA pour calculer automatiquement les priorités
    """
    __tablename__ = "priorities"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Niveaux de priorité
    priority_level = Column(Enum(PriorityLevel), nullable=False, index=True)
    severity_level = Column(Enum(SeverityLevel), nullable=False, index=True)
    urgency_level = Column(Enum(UrgencyLevel), nullable=False, index=True)
    impact_level = Column(Enum(ImpactLevel), nullable=False, index=True)
    
    # Configuration temporelle
    max_response_time_minutes = Column(Integer, nullable=False)  # Temps max réponse
    max_resolution_time_hours = Column(Integer, nullable=False)  # Temps max résolution
    escalation_time_hours = Column(Integer, nullable=False)  # Temps avant escalation
    
    # Configuration visuelle
    color = Column(String(7), nullable=True)  # Code couleur hex
    icon = Column(String(50), nullable=True)  # Nom icône
    badge_style = Column(String(50), nullable=True)  # Style badge CSS
    
    # Configuration IA
    ai_weight = Column(Integer, default=1, nullable=False)  # Poids dans calcul IA
    auto_assignment_threshold = Column(Integer, default=80, nullable=False)  # Seuil assignation auto
    requires_human_review = Column(Boolean, default=False, nullable=False)
    
    # Configuration notification
    notification_frequency = Column(String(20), default="normal", nullable=False)  # immediate, normal, low
    escalation_enabled = Column(Boolean, default=True, nullable=False)
    auto_escalation_rules = Column(JSON, nullable=True)  # Règles d'escalation automatique
    
    # Configuration traitement
    requires_approval = Column(Boolean, default=False, nullable=False)
    can_be_reassigned = Column(Boolean, default=True, nullable=False)
    requires_photo_evidence = Column(Boolean, default=False, nullable=False)
    
    # Conditions spéciales
    weather_dependencies = Column(JSON, nullable=True)  # Dépendances météo
    time_restrictions = Column(JSON, nullable=True)  # Restrictions horaires
    location_restrictions = Column(JSON, nullable=True)  # Restrictions géographiques
    
    # Statistiques
    total_signals = Column(Integer, default=0, nullable=False)
    avg_resolution_time_hours = Column(Integer, default=0, nullable=False)
    escalation_rate = Column(Integer, default=0, nullable=False)  # Pourcentage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    signals = relationship("Signal", back_populates="priority")
    
    def __repr__(self):
        return f"<Priority(id={self.id}, name={self.name}, level={self.priority_level.value})>"
    
    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage avec icône"""
        icon_map = {
            PriorityLevel.CRITICAL: "🚨",
            PriorityLevel.HIGH: "⚠️",
            PriorityLevel.MEDIUM: "📋",
            PriorityLevel.LOW: "ℹ️",
            PriorityLevel.INFO: "📝"
        }
        icon = icon_map.get(self.priority_level, "📌")
        return f"{icon} {self.name}"
    
    @property
    def is_critical(self) -> bool:
        """Vérifie si la priorité est critique"""
        return self.priority_level == PriorityLevel.CRITICAL
    
    @property
    def is_high_priority(self) -> bool:
        """Vérifie si la priorité est élevée ou critique"""
        return self.priority_level in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]
    
    @property
    def requires_immediate_action(self) -> bool:
        """Vérifie si une action immédiate est requise"""
        return (self.priority_level == PriorityLevel.CRITICAL and 
                self.severity_level in [SeverityLevel.EXTREME, SeverityLevel.SEVERE])
    
    def get_response_deadline(self, created_at: datetime) -> datetime:
        """Calcule la date limite de réponse"""
        from datetime import timedelta
        return created_at + timedelta(minutes=self.max_response_time_minutes)
    
    def get_resolution_deadline(self, created_at: datetime) -> datetime:
        """Calcule la date limite de résolution"""
        from datetime import timedelta
        return created_at + timedelta(hours=self.max_resolution_time_hours)
    
    def get_escalation_deadline(self, created_at: datetime) -> datetime:
        """Calcule la date limite d'escalation"""
        from datetime import timedelta
        return created_at + timedelta(hours=self.escalation_time_hours)
    
    def calculate_priority_score(self, base_score: float) -> float:
        """Calcule le score de priorité final"""
        weight_multiplier = self.ai_weight / 10.0
        severity_multiplier = (6 - self.severity_level.value) / 5.0
        urgency_multiplier = (6 - self.urgency_level.value) / 5.0
        impact_multiplier = (6 - self.impact_level.value) / 5.0
        
        final_score = (base_score * weight_multiplier * 
                      severity_multiplier * urgency_multiplier * impact_multiplier)
        
        return min(10.0, max(0.0, final_score))
    
    def should_escalate(self, current_time: datetime, created_at: datetime) -> bool:
        """Détermine si le signalement doit être escaladé"""
        if not self.escalation_enabled:
            return False
        
        escalation_deadline = self.get_escalation_deadline(created_at)
        return current_time > escalation_deadline
    
    def get_notification_config(self) -> dict:
        """Retourne la configuration de notification"""
        return {
            "frequency": self.notification_frequency,
            "immediate": self.is_critical,
            "escalation": self.escalation_enabled,
            "auto_assign": self.auto_assignment_threshold
        }
    
    def meets_weather_conditions(self, current_weather: dict) -> bool:
        """Vérifie si les conditions météo sont appropriées"""
        if not self.weather_dependencies:
            return True
        
        # Logique de vérification des conditions météo
        # À implémenter selon les besoins spécifiques
        return True
    
    def meets_time_restrictions(self, current_time: datetime) -> bool:
        """Vérifie si les restrictions horaires sont respectées"""
        if not self.time_restrictions:
            return True
        
        # Logique de vérification des restrictions horaires
        # À implémenter selon les besoins spécifiques
        return True
