"""
Notification Schemas - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des notifications
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class NotificationBase(BaseModel):
    """Schéma de base pour les notifications"""
    title: str = Field(..., min_length=2, max_length=200, description="Titre de la notification")
    message: str = Field(..., min_length=5, max_length=2000, description="Message de la notification")
    notification_type: str = Field(..., description="Type de notification")
    channel: str = Field(..., description="Canal de notification")
    priority: str = Field("normal", description="Priorité de la notification")
    
    @validator('title')
    def validate_title(cls, v):
        """Validation du titre"""
        if not v.strip():
            raise ValueError('Le titre ne peut pas être vide')
        return v.strip()


class NotificationCreate(NotificationBase):
    """Schéma pour la création de notification"""
    user_id: Optional[int] = Field(None, ge=0, description="ID de l'utilisateur")
    signal_id: Optional[int] = Field(None, ge=0, description="ID du signal")
    report_id: Optional[int] = Field(None, ge=0, description="ID du rapport")
    recipient_email: Optional[str] = Field(None, description="Email du destinataire")
    recipient_phone: Optional[str] = Field(None, description="Téléphone du destinataire")
    recipient_device_token: Optional[str] = Field(None, max_length=500, description="Token device")
    recipient_webhook_url: Optional[str] = Field(None, max_length=500, description="URL webhook")
    template_name: Optional[str] = Field(None, max_length=100, description="Nom du template")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Variables du template")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Données personnalisées")
    scheduled_at: Optional[datetime] = Field(None, description="Date d'envoi planifiée")
    max_retries: int = Field(3, ge=0, le=10, description="Nombre max de tentatives")
    retry_delay_minutes: int = Field(5, ge=1, le=1440, description="Délai entre tentatives")
    requires_action: bool = Field(False, description="Action requise")
    action_url: Optional[str] = Field(None, max_length=500, description="URL d'action")
    action_button_text: Optional[str] = Field(None, max_length=100, description="Texte bouton action")
    expires_at: Optional[datetime] = Field(None, description="Date d'expiration")
    
    @validator('recipient_email')
    def validate_email(cls, v):
        """Validation de l'email"""
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format d\'email invalide')
        return v
    
    @validator('recipient_phone')
    def validate_phone(cls, v):
        """Validation du téléphone"""
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Format de téléphone invalide')
        return v


class NotificationSend(NotificationCreate):
    """Schéma pour l'envoi de notification (avec destinataire)"""
    recipient_type: Optional[str] = Field(None, description="Type de destinataire (all_citizens, all_admins, all_sector_users, custom_email, custom_phone)")
    sector_id: Optional[int] = Field(None, ge=0, description="ID du secteur pour les destinataires du secteur")


class NotificationUpdate(BaseModel):
    """Schéma pour la mise à jour de notification"""
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    message: Optional[str] = Field(None, min_length=5, max_length=2000)
    scheduled_at: Optional[datetime] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_minutes: Optional[int] = Field(None, ge=1, le=1440)
    requires_action: Optional[bool] = None
    action_url: Optional[str] = Field(None, max_length=500)
    action_button_text: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None
    template_variables: Optional[Dict[str, Any]] = None
    custom_data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schéma de réponse pour les notifications"""
    id: int
    title: str
    message: str
    notification_code: str
    notification_type: str
    channel: str
    priority: str
    status: str
    user_id: Optional[int]
    signal_id: Optional[int]
    report_id: Optional[int]
    recipient_email: Optional[str]
    recipient_phone: Optional[str]
    recipient_device_token: Optional[str]
    recipient_webhook_url: Optional[str]
    template_name: Optional[str]
    template_variables: Optional[Dict[str, Any]]
    custom_data: Optional[Dict[str, Any]]
    scheduled_at: Optional[datetime]
    retry_count: int
    max_retries: int
    retry_delay_minutes: int
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    failed_at: Optional[datetime]
    requires_action: bool
    action_url: Optional[str]
    action_button_text: Optional[str]
    expires_at: Optional[datetime]
    external_id: Optional[str]
    delivery_receipt: Optional[Dict[str, Any]]
    tracking_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    error_code: Optional[str]
    delivery_logs: Optional[List[Dict[str, Any]]]
    email_config: Optional[Dict[str, Any]]
    whatsapp_config: Optional[Dict[str, Any]]
    push_config: Optional[Dict[str, Any]]
    open_rate: int
    click_rate: int
    response_rate: int
    created_at: datetime
    updated_at: datetime
    
    # Relations
    user: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    """Schéma pour la liste des notifications"""
    items: List[NotificationResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """Schéma pour les statistiques de notifications"""
    total_notifications: int
    notifications_by_status: Dict[str, int]
    notifications_by_type: Dict[str, int]
    notifications_by_channel: Dict[str, int]
    avg_delivery_time_minutes: float
    success_rate: float
    open_rate: float
    click_rate: float
    response_rate: float
    notifications_by_hour: Dict[str, int]
    recent_trends: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class NotificationFilter(BaseModel):
    """Schéma pour le filtrage des notifications"""
    notification_type: Optional[str] = None
    channel: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None
    signal_id: Optional[int] = None
    report_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    requires_action: Optional[bool] = None
    is_expired: Optional[bool] = None


class NotificationTemplate(BaseModel):
    """Schéma pour les modèles de notification"""
    name: str = Field(..., min_length=2, max_length=100, description="Nom du template")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    notification_type: str = Field(..., description="Type de notification")
    channel: str = Field(..., description="Canal")
    subject_template: Optional[str] = Field(None, max_length=200, description="Template sujet")
    message_template: str = Field(..., max_length=2000, description="Template message")
    variables: List[str] = Field(..., description="Variables utilisées")
    default_variables: Optional[Dict[str, Any]] = Field(None, description="Variables par défaut")
    is_default: bool = Field(False, description="Template par défaut")
    is_active: bool = Field(True, description="Template actif")
    
    class Config:
        from_attributes = True


class NotificationBulkAction(BaseModel):
    """Schéma pour les actions en masse sur les notifications"""
    notification_ids: List[int] = Field(..., min_items=1, max_items=100, description="IDs des notifications")
    action: str = Field(..., description="Action à effectuer")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres de l'action")


class NotificationSchedule(BaseModel):
    """Schéma pour la planification de notifications"""
    notification_type: str = Field(..., description="Type de notification")
    channel: str = Field(..., description="Canal")
    recipients: List[str] = Field(..., description="Destinataires")
    schedule_pattern: str = Field(..., description="Pattern de planification")
    template_name: str = Field(..., description="Nom du template")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Variables du template")
    is_active: bool = Field(True, description="Planification active")
    next_run: Optional[datetime] = Field(None, description="Prochaine exécution")
    
    class Config:
        from_attributes = True


class NotificationTest(BaseModel):
    """Schéma pour le test de notification"""
    notification_type: str = Field(..., description="Type de notification")
    channel: str = Field(..., description="Canal")
    recipient: str = Field(..., description="Destinataire de test")
    template_name: Optional[str] = Field(None, description="Template à tester")
    test_variables: Optional[Dict[str, Any]] = Field(None, description="Variables de test")
    send_immediately: bool = Field(True, description="Envoyer immédiatement")


class NotificationPreferences(BaseModel):
    """Schéma pour les préférences de notification"""
    user_id: int = Field(..., ge=0, description="ID de l'utilisateur")
    email_enabled: bool = Field(True, description="Notifications email activées")
    whatsapp_enabled: bool = Field(False, description="Notifications WhatsApp activées")
    push_enabled: bool = Field(True, description="Notifications push activées")
    in_app_enabled: bool = Field(True, description="Notifications in-app activées")
    notification_types: Dict[str, bool] = Field(..., description="Préférences par type")
    quiet_hours: Optional[Dict[str, Any]] = Field(None, description="Heures de silence")
    frequency_limits: Optional[Dict[str, int]] = Field(None, description="Limites de fréquence")
    
    class Config:
        from_attributes = True


class NotificationAnalytics(BaseModel):
    """Schéma pour les analytics de notifications"""
    notification_id: int
    sent_at: datetime
    delivery_time_ms: int
    open_time_ms: Optional[int]
    click_time_ms: Optional[int]
    device_type: Optional[str]
    platform: Optional[str]
    location: Optional[Dict[str, Any]]
    user_agent: Optional[str]
    
    class Config:
        from_attributes = True


class NotificationValidation(BaseModel):
    """Schéma pour la validation de notification"""
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=5, max_length=2000)
    notification_type: str = Field(..., description="Type de notification")
    channel: str = Field(..., description="Canal")
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    
    @validator('recipient_email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format d\'email invalide')
        return v
    
    @validator('recipient_phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Format de téléphone invalide')
        return v


class NotificationRetry(BaseModel):
    """Schéma pour la retry de notification"""
    notification_id: int = Field(..., gt=0, description="ID de la notification")
    retry_reason: str = Field(..., description="Raison de la retry")
    custom_variables: Optional[Dict[str, Any]] = Field(None, description="Variables personnalisées")
    force_retry: bool = Field(False, description="Forcer la retry")
    
    class Config:
        from_attributes = True
