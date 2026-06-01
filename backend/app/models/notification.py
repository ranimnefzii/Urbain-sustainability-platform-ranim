"""
Notification Model - Urbain Sustainability System
Modèle pour les notifications et alertes système
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class NotificationType(enum.Enum):
    """Types de notifications"""
    SIGNAL_CREATED = "signal_created"            # Nouveau signalement
    SIGNAL_ASSIGNED = "signal_assigned"          # Signalement assigné
    SIGNAL_UPDATED = "signal_updated"            # Signalement mis à jour
    SIGNAL_RESOLVED = "signal_resolved"          # Signalement résolu
    SIGNAL_ESCALATED = "signal_escalated"      # Signalement escaladé
    SYSTEM_ALERT = "system_alert"                # Alerte système
    MAINTENANCE = "maintenance"                  # Maintenance
    REPORT_GENERATED = "report_generated"        # Rapport généré
    DEADLINE_APPROACHING = "deadline_approaching"  # Échéance approche
    PERFORMANCE_ISSUE = "performance_issue"      # Problème performance


class NotificationChannel(enum.Enum):
    """Canaux de notification"""
    EMAIL = "email"                            # Email
    SMS = "sms"                                # SMS (kept for backward compat)
    WHATSAPP = "whatsapp"                      # WhatsApp
    PUSH = "push"                              # Push notification
    IN_APP = "in_app"                          # Notification dans app
    WEBHOOK = "webhook"                        # Webhook
    SLACK = "slack"                            # Slack
    TELEGRAM = "telegram"                        # Telegram


class NotificationPriority(enum.Enum):
    """Priorités des notifications"""
    LOW = "low"                                # Basse
    NORMAL = "normal"                          # Normale
    HIGH = "high"                              # Élevée
    CRITICAL = "critical"                        # Critique


class NotificationStatus(enum.Enum):
    """Statuts des notifications"""
    PENDING = "pending"                        # En attente
    SENT = "sent"                              # Envoyée
    DELIVERED = "delivered"                    # Livrée
    READ = "read"                              # Lue
    FAILED = "failed"                           # Échouée
    CANCELLED = "cancelled"                      # Annulée


class Notification(Base):
    """
    Modèle notification pour gérer toutes les communications
    Supporte multiples canaux et types de notifications
    """
    __tablename__ = "notifications"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    title = Column(String(200), nullable=False, index=True)
    message = Column(Text, nullable=False)
    notification_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True, index=True)
    
    # Type et canal
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    
    # Destinataires
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_device_token = Column(String(500), nullable=True)  # Token push notification
    recipient_webhook_url = Column(String(500), nullable=True)
    
    # Contenu personnalisé
    template_name = Column(String(100), nullable=True)
    template_variables = Column(JSON, nullable=True)
    custom_data = Column(JSON, nullable=True)
    
    # Configuration envoi
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay_minutes = Column(Integer, default=5, nullable=False)
    
    # Suivi livraison
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Réponse et interaction
    requires_action = Column(Boolean, default=False, nullable=False)
    action_url = Column(String(500), nullable=True)
    action_button_text = Column(String(100), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées externes
    external_id = Column(String(100), nullable=True)  # ID externe (SMS provider, email service)
    delivery_receipt = Column(JSON, nullable=True)  # Preuve de livraison
    tracking_data = Column(JSON, nullable=True)  # Données tracking
    
    # Logs et erreurs
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    delivery_logs = Column(JSON, nullable=True)  # Logs de livraison détaillés
    
    # Configuration spécifique par canal
    email_config = Column(JSON, nullable=True)  # Configuration email
    sms_config = Column(JSON, nullable=True)  # Configuration SMS
    push_config = Column(JSON, nullable=True)  # Configuration push
    
    # Analytics
    open_rate = Column(Integer, default=0, nullable=False)  # Pourcentage ouverture
    click_rate = Column(Integer, default=0, nullable=False)  # Pourcentage clic
    response_rate = Column(Integer, default=0, nullable=False)  # Pourcentage réponse
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type.value}, channel={self.channel.value})>"
    
    @property
    def is_sent(self) -> bool:
        """Vérifie si la notification a été envoyée"""
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED, NotificationStatus.READ]
    
    @property
    def is_delivered(self) -> bool:
        """Vérifie si la notification a été livrée"""
        return self.status in [NotificationStatus.DELIVERED, NotificationStatus.READ]
    
    @property
    def is_read(self) -> bool:
        """Vérifie si la notification a été lue"""
        return self.status == NotificationStatus.READ
    
    @property
    def is_failed(self) -> bool:
        """Vérifie si la notification a échoué"""
        return self.status == NotificationStatus.FAILED
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la notification est expirée"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    @property
    def can_retry(self) -> bool:
        """Vérifie si la notification peut être réessayée"""
        return (self.is_failed and 
                self.retry_count < self.max_retries and
                not self.is_expired)
    
    @property
    def is_urgent(self) -> bool:
        """Vérifie si la notification est urgente"""
        return self.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]
    
    def generate_notification_code(self) -> str:
        """Génère un code de notification unique"""
        import random
        import string
        
        year = datetime.now().year
        month = datetime.now().month
        type_prefix = self.notification_type.value[:3].upper()
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"NOT-{type_prefix}-{year}{month:02d}-{random_chars}"
    
    def get_recipient_info(self) -> dict:
        """Retourne les informations du destinataire"""
        return {
            "user_id": self.user_id,
            "email": self.recipient_email,
            "phone": self.recipient_phone,
            "device_token": self.recipient_device_token,
            "webhook_url": self.recipient_webhook_url
        }
    
    def get_content_with_variables(self) -> dict:
        """Retourne le contenu avec variables substituées"""
        if not self.template_variables:
            return {
                "title": self.title,
                "message": self.message
            }
        
        # Substitution des variables dans le titre et message
        title = self.title
        message = self.message
        
        for key, value in self.template_variables.items():
            placeholder = f"{{{key}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        return {
            "title": title,
            "message": message
        }
    
    def get_channel_config(self) -> dict:
        """Retourne la configuration spécifique au canal"""
        config_map = {
            NotificationChannel.EMAIL: self.email_config or {},
            NotificationChannel.SMS: self.sms_config or {},
            NotificationChannel.WHATSAPP: self.sms_config or {},
            NotificationChannel.PUSH: self.push_config or {}
        }
        return config_map.get(self.channel, {})
    
    def calculate_next_retry_time(self) -> Optional[datetime]:
        """Calcule le prochain temps de retry avec backoff exponentiel"""
        if not self.can_retry:
            return None
        
        import math
        from datetime import timedelta
        
        # Backoff exponentiel: 5min, 15min, 45min
        delay_multiplier = math.pow(3, self.retry_count)
        delay_minutes = self.retry_delay_minutes * delay_multiplier
        
        return datetime.now() + timedelta(minutes=delay_minutes)
    
    def mark_as_sent(self, external_id: Optional[str] = None):
        """Marque la notification comme envoyée"""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now()
        if external_id:
            self.external_id = external_id
        self.updated_at = datetime.now()
    
    def mark_as_delivered(self, receipt_data: Optional[dict] = None):
        """Marque la notification comme livrée"""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.now()
        if receipt_data:
            self.delivery_receipt = receipt_data
        self.updated_at = datetime.now()
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.status = NotificationStatus.READ
        self.read_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_as_failed(self, error_message: str, error_code: Optional[str] = None):
        """Marque la notification comme échouée"""
        self.status = NotificationStatus.FAILED
        self.failed_at = datetime.now()
        self.error_message = error_message
        if error_code:
            self.error_code = error_code
        self.retry_count += 1
        self.updated_at = datetime.now()
    
    def add_delivery_log(self, log_entry: dict):
        """Ajoute une entrée au log de livraison"""
        if not self.delivery_logs:
            self.delivery_logs = []
        
        log_entry["timestamp"] = datetime.now().isoformat()
        self.delivery_logs.append(log_entry)
        self.updated_at = datetime.now()
    
    def update_analytics(self, event_type: str, data: Optional[dict] = None):
        """Met à jour les analytics de la notification"""
        if event_type == "open":
            self.open_rate = min(100, self.open_rate + 1)
        elif event_type == "click":
            self.click_rate = min(100, self.click_rate + 1)
        elif event_type == "response":
            self.response_rate = min(100, self.response_rate + 1)
        
        if data and not self.tracking_data:
            self.tracking_data = {}
        
        if data:
            self.tracking_data[event_type] = data
        
        self.updated_at = datetime.now()
