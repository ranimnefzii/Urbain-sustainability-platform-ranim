"""
Sector Model - Urbain Sustainability System
Modèle pour les secteurs municipaux (eau, routes, déchets, etc.)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SectorType(enum.Enum):
    """Types de secteurs municipaux"""
    WATER = "water"  # Eau et assainissement
    ROADS = "roads"  # Routes et transport
    WASTE = "waste"  # Déchets et propreté
    LIGHTING = "lighting"  # Éclairage public
    GREEN_SPACES = "green_spaces"  # Espaces verts
    BUILDINGS = "buildings"  # Bâtiments publics
    SAFETY = "safety"  # Sécurité et police municipale
    ENVIRONMENT = "environment"  # Environnement
    ADMINISTRATION = "administration"  # Administration générale


class SectorStatus(enum.Enum):
    """Statuts des secteurs"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class Sector(Base):
    """
    Modèle secteur pour la gestion des services municipaux
    Chaque secteur gère des types spécifiques de problèmes urbains
    """
    __tablename__ = "sectors"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Type et statut
    sector_type = Column(Enum(SectorType), nullable=False, index=True)
    status = Column(Enum(SectorStatus), default=SectorStatus.ACTIVE, nullable=False)
    
    # Contact et localisation
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Responsables
    manager_name = Column(String(100), nullable=True)
    manager_email = Column(String(255), nullable=True)
    manager_phone = Column(String(20), nullable=True)
    
    # Configuration du secteur
    working_hours = Column(JSON, nullable=True)  # {"monday": "08:00-17:00", ...}
    emergency_contact = Column(JSON, nullable=True)  # {"phone": "...", "email": "..."}
    
    # Capacités et contraintes
    max_daily_signals = Column(Integer, default=100, nullable=False)
    avg_processing_time_hours = Column(Integer, default=24, nullable=False)
    priority_level = Column(Integer, default=3, nullable=False)  # 1-5, 1 = haute priorité
    
    # Configuration notifications
    email_templates = Column(JSON, nullable=True)  # Templates d'emails personnalisés
    auto_assignment_enabled = Column(Boolean, default=True, nullable=False)
    escalation_enabled = Column(Boolean, default=True, nullable=False)
    
    # Configuration IA
    ai_confidence_threshold = Column(Integer, default=70, nullable=False)  # 0-100
    supported_categories = Column(JSON, nullable=True)  # IDs des catégories supportées
    
    # Intégrations externes
    external_systems = Column(JSON, nullable=True)  # Configuration systèmes externes
    api_endpoints = Column(JSON, nullable=True)  # Endpoints API pour intégration
    
    # Statistiques
    total_signals_processed = Column(Integer, default=0, nullable=False)
    avg_resolution_time_hours = Column(Integer, default=0, nullable=False)
    satisfaction_rate = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    users = relationship("User", backref="sector")
    
    def __repr__(self):
        return f"<Sector(id={self.id}, name={self.name}, type={self.sector_type.value})>"
    
    @property
    def is_active(self) -> bool:
        """Vérifie si le secteur est actif"""
        return self.status == SectorStatus.ACTIVE
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet avec type"""
        return f"{self.name} ({self.sector_type.value})"
    
    def can_handle_signal(self, category_id: int) -> bool:
        """Vérifie si le secteur peut gérer une catégorie"""
        if not self.supported_categories:
            return True  # Si pas de restriction, tout gérer
        return category_id in self.supported_categories
    
    def get_working_hours_for_day(self, day: str) -> Optional[str]:
        """Retourne les heures de travail pour un jour spécifique"""
        if not self.working_hours:
            return "08:00-17:00"  # Valeur par défaut
        return self.working_hours.get(day.lower())
    
    def is_working_hours(self, current_time: datetime) -> bool:
        """Vérifie si l'heure actuelle est dans les heures de travail"""
        if not self.working_hours:
            return True  # Si pas de restriction, toujours disponible
        
        day_name = current_time.strftime("%A").lower()
        working_hours = self.get_working_hours_for_day(day_name)
        
        if not working_hours:
            return False
        
        try:
            start_time, end_time = working_hours.split("-")
            current_hour = current_time.hour
            start_hour = int(start_time.split(":")[0])
            end_hour = int(end_time.split(":")[0])
            
            return start_hour <= current_hour <= end_hour
        except (ValueError, AttributeError):
            return True  # En cas d'erreur, considérer comme disponible
    
    def get_escalation_time_hours(self) -> int:
        """Retourne le temps avant escalation en heures"""
        base_time = self.avg_processing_time_hours
        return base_time * 2  # Escalation après 2x le temps normal
