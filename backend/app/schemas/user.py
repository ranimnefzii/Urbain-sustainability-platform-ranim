"""
User Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des utilisateurs
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur")
    first_name: str = Field(..., min_length=2, max_length=100, description="Prénom")
    last_name: str = Field(..., min_length=2, max_length=100, description="Nom")
    phone_number: Optional[str] = Field(None, max_length=20, description="Numéro de téléphone")
    
    @validator('username')
    def validate_username(cls, v):
        """Validation du format du nom d'utilisateur"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Le nom d\'utilisateur ne doit contenir que des lettres, chiffres et underscores')
        return v.lower()
    
    @validator('phone_number')
    def validate_phone(cls, v):
        """Validation du format du numéro de téléphone"""
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Format de numéro de téléphone invalide')
        return v


class UserCreate(UserBase):
    """Schéma pour la création d'utilisateur"""
    password: str = Field(..., min_length=8, max_length=128, description="Mot de passe")
    confirm_password: str = Field(..., description="Confirmation du mot de passe")
    address: Optional[str] = Field(None, max_length=500, description="Adresse")
    city: Optional[str] = Field(None, max_length=100, description="Ville")
    postal_code: Optional[str] = Field(None, max_length=20, description="Code postal")
    preferred_language: str = Field("fr", max_length=10, description="Langue préférée")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Vérification que les mots de passe correspondent"""
        if 'password' in values and v != values['password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validation de la force du mot de passe"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'utilisateur"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    profile_picture_url: Optional[str] = Field(None, max_length=500)
    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    push_notifications_enabled: Optional[bool] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Format de numéro de téléphone invalide')
        return v


class UserLogin(BaseModel):
    """Schéma pour la connexion utilisateur"""
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="Mot de passe")
    remember_me: bool = Field(False, description="Se souvenir de moi")


class UserRegister(UserCreate):
    """Schéma pour l'inscription utilisateur"""
    agree_terms: bool = Field(..., description="Acceptation des conditions d'utilisation")
    privacy_policy: bool = Field(..., description="Acceptation de la politique de confidentialité")
    
    @validator('agree_terms', 'privacy_policy')
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError('Vous devez accepter les conditions')
        return v


class UserProfile(BaseModel):
    """Schéma pour le profil utilisateur"""
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    profile_picture_url: Optional[str]
    role: str
    status: str
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    country: str
    email_notifications_enabled: bool
    sms_notifications_enabled: bool
    push_notifications_enabled: bool
    preferred_language: str
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    total_signals_created: int
    total_signals_processed: int
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schéma de réponse pour les utilisateurs"""
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    profile_picture_url: Optional[str]
    role: str
    status: str
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """Schéma pour les statistiques utilisateur"""
    total_signals_created: int
    total_signals_processed: int
    avg_resolution_time_hours: float
    citizen_satisfaction_rate: float
    signals_by_status: dict
    signals_by_category: dict
    recent_activity: List[dict]
    
    class Config:
        from_attributes = True


class UserPasswordChange(BaseModel):
    """Schéma pour le changement de mot de passe"""
    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nouveau mot de passe")
    confirm_new_password: str = Field(..., description="Confirmation du nouveau mot de passe")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v


class UserEmailVerification(BaseModel):
    """Schéma pour la vérification email"""
    email: EmailStr = Field(..., description="Email à vérifier")
    verification_code: str = Field(..., min_length=6, max_length=6, description="Code de vérification")


class UserPhoneVerification(BaseModel):
    """Schéma pour la vérification téléphone"""
    phone_number: str = Field(..., description="Numéro de téléphone")
    verification_code: str = Field(..., min_length=6, max_length=6, description="Code de vérification")


class UserPasswordReset(BaseModel):
    """Schéma pour la réinitialisation du mot de passe"""
    email: EmailStr = Field(..., description="Email pour la réinitialisation")


class UserPasswordResetConfirm(BaseModel):
    """Schéma pour la confirmation de réinitialisation"""
    token: str = Field(..., description="Token de réinitialisation")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nouveau mot de passe")
    confirm_password: str = Field(..., description="Confirmation du mot de passe")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v
