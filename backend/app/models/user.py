"""
User Model - Urbain Sustainability System
Modèle utilisateur pour citoyens, administrateurs et secteurs
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    """Rôles utilisateurs"""
    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"
    SECTOR = "SECTOR"


class UserStatus(enum.Enum):
    """Statuts utilisateurs"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class User(Base):
    """
    Modèle utilisateur pour le système de signalement urbain
    Supporte les citoyens, administrateurs et utilisateurs sectoriels
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profil utilisateur
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    
    # Rôle et permissions
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Localisation
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Tunisia", nullable=False)
    
    # Préférences de notification
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    sms_notifications_enabled = Column(Boolean, default=False, nullable=False)
    push_notifications_enabled = Column(Boolean, default=True, nullable=False)
    preferred_language = Column(String(10), default="fr", nullable=False)
    
    # Secteur (pour les utilisateurs sectoriels)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True, index=True)
    
    # Vérification et sécurité
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    phone_verification_code = Column(String(10), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistiques
    total_signals_created = Column(Integer, default=0, nullable=False)
    total_signals_processed = Column(Integer, default=0, nullable=False)
    
    # Relations
    signals_created = relationship("Signal", back_populates="created_by_user", foreign_keys="Signal.created_by")
    signals_processed = relationship("Signal", back_populates="processed_by_user", foreign_keys="Signal.processed_by")
    notifications = relationship("Notification", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_active(self) -> bool:
        """Vérifie si l'utilisateur est actif"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_sector_user(self) -> bool:
        """Vérifie si l'utilisateur est sectoriel"""
        return self.role == UserRole.SECTOR
    
    @property
    def is_citizen(self) -> bool:
        """Vérifie si l'utilisateur est citoyen"""
        return self.role == UserRole.CITIZEN
    
    def can_create_signals(self) -> bool:
        """Vérifie si l'utilisateur peut créer des signalements"""
        return self.is_active and self.is_email_verified
    
    def can_process_signals(self) -> bool:
        """Vérifie si l'utilisateur peut traiter des signalements"""
        return self.is_active and (self.is_admin or self.is_sector_user)
    
    def can_view_analytics(self) -> bool:
        """Vérifie si l'utilisateur peut voir les analytics"""
        return self.is_active and (self.is_admin or self.is_sector_user)
