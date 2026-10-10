"""
Signal Model - Urbain Sustainability System
Modèle principal pour les signalements de problèmes urbains
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base
from app.models.mixins import SoftDeleteMixin


class SignalStatus(enum.Enum):
    """Statuts des signalements"""
    DRAFT = "draft"                    # Brouillon
    SUBMITTED = "submitted"            # Soumis
    UNDER_REVIEW = "under_review"      # En cours d'examen
    ASSIGNED = "assigned"              # Assigné
    IN_PROGRESS = "in_progress"        # En cours de traitement
    RESOLVED = "resolved"              # Résolu
    CLOSED = "closed"                  # Fermé
    CANCELLED = "cancelled"            # Annulé
    REJECTED = "rejected"              # Rejeté


class SignalSource(enum.Enum):
    """Sources des signalements"""
    WEB = "web"                        # Application web
    MOBILE = "mobile"                  # Application mobile
    EMAIL = "email"                    # Email
    PHONE = "phone"                    # Appel téléphonique
    SOCIAL_MEDIA = "social_media"      # Réseaux sociaux
    OFFICIAL = "official"              # Signalement officiel
    AUTOMATIC = "automatic"            # Détection automatique


class VerificationStatus(enum.Enum):
    """Statuts de vérification"""
    PENDING = "pending"                # En attente
    VERIFIED = "verified"              # Vérifié
    REJECTED = "rejected"              # Rejeté
    NEEDS_INFO = "needs_info"          # Informations supplémentaires


class Signal(Base, SoftDeleteMixin):
    """
    Modèle principal pour les signalements de problèmes urbains
    Contient toutes les informations nécessaires pour le traitement IA
    """
    __tablename__ = "signals"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    reference_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relations
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=False, index=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_sector_id = Column(Integer, nullable=True, index=True)
    
    # Localisation
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(Text, nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Tunisia", nullable=False)
    location_accuracy = Column(Float, nullable=True)  # Précision GPS en mètres
    location_description = Column(Text, nullable=True)  # Description détaillée
    
    # Statuts
    status = Column(Enum(SignalStatus), default=SignalStatus.DRAFT, nullable=False, index=True)
    source = Column(Enum(SignalSource), default=SignalSource.WEB, nullable=False)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    
    # Médias
    images = Column(JSON, nullable=True)  # URLs des images
    videos = Column(JSON, nullable=True)  # URLs des vidéos
    documents = Column(JSON, nullable=True)  # URLs des documents
    audio_files = Column(JSON, nullable=True)  # URLs des fichiers audio
    
    # Données IA
    ai_confidence_score = Column(Float, nullable=True)  # Score de confiance IA (0-1)
    ai_classification = Column(JSON, nullable=True)  # Résultats classification IA
    ai_priority_score = Column(Float, nullable=True)  # Score de priorité IA
    ai_severity_score = Column(Float, nullable=True)  # Score de sévérité IA
    ai_urgency_score = Column(Float, nullable=True)  # Score d'urgence IA
    ai_processing_time_ms = Column(Integer, nullable=True)  # Temps traitement IA
    
    # Métadonnées
    ip_address = Column(String(45), nullable=True)  # IP du signalant
    user_agent = Column(Text, nullable=True)  # User agent navigateur
    device_info = Column(JSON, nullable=True)  # Informations appareil
    browser_info = Column(JSON, nullable=True)  # Informations navigateur
    
    # Température et conditions
    weather_at_report = Column(JSON, nullable=True)  # Météo au moment du signalement
    temperature_celsius = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    
    # Impact et dommages
    estimated_damage_cost = Column(Float, nullable=True)
    affected_people_count = Column(Integer, nullable=True)
    affected_area_sqm = Column(Float, nullable=True)
    safety_risk_level = Column(Integer, nullable=True)  # 1-5
    
    # Traitement
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    started_processing_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Résolution
    resolution_description = Column(Text, nullable=True)
    resolution_method = Column(String(100), nullable=True)
    resolution_cost = Column(Float, nullable=True)
    resolution_images = Column(JSON, nullable=True)  # Images après résolution
    
    # Feedback citoyen
    citizen_satisfaction = Column(Integer, nullable=True)  # 1-5
    citizen_feedback = Column(Text, nullable=True)
    citizen_response_time_hours = Column(Integer, nullable=True)
    
    # Notes internes
    internal_notes = Column(Text, nullable=True)
    escalation_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Configuration
    is_public = Column(Boolean, default=True, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    allow_contact = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="signals_created")
    processed_by_user = relationship("User", foreign_keys=[processed_by], back_populates="signals_processed")
    category = relationship("Category", back_populates="signals")
    priority = relationship("Priority", back_populates="signals")
    reports = relationship("Report", back_populates="signal")
    
    def __repr__(self):
        return f"<Signal(id={self.id}, ref={self.reference_number}, status={self.status.value})>"
    
    @property
    def is_active(self) -> bool:
        """Vérifie si le signalement est actif"""
        return self.status not in [SignalStatus.CLOSED, SignalStatus.CANCELLED, SignalStatus.REJECTED]
    
    @property
    def is_resolved(self) -> bool:
        """Vérifie si le signalement est résolu"""
        return self.status == SignalStatus.RESOLVED
    
    @property
    def needs_attention(self) -> bool:
        """Vérifie si le signalement nécessite une attention"""
        return (self.status in [SignalStatus.SUBMITTED, SignalStatus.UNDER_REVIEW] and 
                self.verification_status == VerificationStatus.PENDING)
    
    @property
    def is_overdue(self) -> bool:
        """Vérifie si le signalement est en retard"""
        if not self.priority or self.is_resolved:
            return False
        
        deadline = self.priority.get_resolution_deadline(self.created_at)
        return datetime.now() > deadline
    
    @property
    def processing_duration_hours(self) -> Optional[int]:
        """Calcule la durée de traitement en heures"""
        if not self.started_processing_at:
            return None
        
        end_time = self.resolved_at or datetime.now()
        duration = end_time - self.started_processing_at
        return int(duration.total_seconds() / 3600)
    
    @property
    def total_duration_hours(self) -> int:
        """Calcule la durée totale en heures"""
        end_time = self.resolved_at or datetime.now()
        duration = end_time - self.created_at
        return int(duration.total_seconds() / 3600)
    
    def generate_reference_number(self) -> str:
        """Génère un numéro de référence unique"""
        import random
        import string
        
        year = datetime.now().year
        month = datetime.now().month
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        return f"SIG-{year}{month:02d}-{random_chars}"
    
    def get_location_dict(self) -> dict:
        """Retourne les informations de localisation comme dictionnaire"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "accuracy": self.location_accuracy,
            "description": self.location_description
        }
    
    def get_media_urls(self) -> dict:
        """Retourne tous les URLs des médias"""
        return {
            "images": self.images or [],
            "videos": self.videos or [],
            "documents": self.documents or [],
            "audio_files": self.audio_files or []
        }
    
    def get_ai_scores(self) -> dict:
        """Retourne les scores IA"""
        return {
            "confidence": self.ai_confidence_score,
            "priority": self.ai_priority_score,
            "severity": self.ai_severity_score,
            "urgency": self.ai_urgency_score,
            "processing_time_ms": self.ai_processing_time_ms
        }
    
    def can_be_edited_by_user(self, user_id: int) -> bool:
        """Vérifie si l'utilisateur peut éditer le signalement"""
        return (self.created_by == user_id and 
                self.status in [SignalStatus.DRAFT, SignalStatus.SUBMITTED])
    
    def can_be_processed_by_user(self, user) -> bool:
        """Vérifie si l'utilisateur peut traiter le signalement"""
        return user.can_process_signals() and self.is_active
    
    def update_status(self, new_status: SignalStatus, user_id: Optional[int] = None, notes: Optional[str] = None):
        """Met à jour le statut du signalement"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        self.last_activity_at = datetime.now()
        
        if user_id:
            self.processed_by = user_id
        
        if notes:
            if not self.internal_notes:
                self.internal_notes = ""
            self.internal_notes += f"\n[{datetime.now().isoformat()}] Status changed: {old_status.value} → {new_status.value}\n{notes}"
        
        # Mise à jour des timestamps spécifiques
        if new_status == SignalStatus.ASSIGNED:
            self.assigned_at = datetime.now()
        elif new_status == SignalStatus.IN_PROGRESS:
            self.started_processing_at = datetime.now()
        elif new_status == SignalStatus.RESOLVED:
            self.resolved_at = datetime.now()
        elif new_status == SignalStatus.CLOSED:
            self.closed_at = datetime.now()
