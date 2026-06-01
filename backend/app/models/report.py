"""
Report Model - Urbain Sustainability System
Modèle pour les rapports générés par l'IA et les analytics
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ReportType(enum.Enum):
    """Types de rapports"""
    SIGNAL_ANALYSIS = "signal_analysis"      # Analyse de signalement
    PRIORITY_ASSESSMENT = "priority_assessment"  # Évaluation priorité
    TREND_ANALYSIS = "trend_analysis"        # Analyse tendances
    PERFORMANCE_METRICS = "performance_metrics"  # Métriques performance
    SECTOR_SUMMARY = "sector_summary"        # Résumé secteur
    CITIZEN_FEEDBACK = "citizen_feedback"    # Feedback citoyens
    PREDICTIVE_ANALYSIS = "predictive_analysis"  # Analyse prédictive
    ESCALATION_REPORT = "escalation_report"  # Rapport escalation


class ReportStatus(enum.Enum):
    """Statuts des rapports"""
    GENERATING = "generating"              # En cours de génération
    COMPLETED = "completed"                # Terminé
    FAILED = "failed"                     # Échec
    SCHEDULED = "scheduled"                # Planifié
    ARCHIVED = "archived"                  # Archivé


class ReportFrequency(enum.Enum):
    """Fréquences des rapports"""
    REAL_TIME = "real_time"               # Temps réel
    HOURLY = "hourly"                     # Horaire
    DAILY = "daily"                       # Quotidien
    WEEKLY = "weekly"                     # Hebdomadaire
    MONTHLY = "monthly"                   # Mensuel
    QUARTERLY = "quarterly"               # Trimestriel
    YEARLY = "yearly"                     # Annuel
    ON_DEMAND = "on_demand"               # Sur demande


class Report(Base):
    """
    Modèle rapport pour les analyses IA et statistiques
    Contient les résultats des traitements IA et les métriques
    """
    __tablename__ = "reports"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    report_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relations
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True, index=True)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sector_id = Column(Integer, nullable=True, index=True)
    
    # Type et fréquence
    report_type = Column(Enum(ReportType), nullable=False, index=True)
    frequency = Column(Enum(ReportFrequency), nullable=False, default=ReportFrequency.ON_DEMAND)
    
    # Contenu du rapport
    statistics = Column(JSON, nullable=True)  # Statistiques générales
    analytics_data = Column(JSON, nullable=True)  # Données d'analyse
    report_metadata = Column("metadata", JSON, nullable=True)  # Métadonnées additionnelles
    
    # Catégories et priorités
    category_distribution = Column(JSON, nullable=True)
    priority_distribution = Column(JSON, nullable=True)
    sector_distribution = Column(JSON, nullable=True)
    timeline_data = Column(JSON, nullable=True)
    geographic_data = Column(JSON, nullable=True)
    
    # Indicateurs de performance
    total_signals_analyzed = Column(Integer, default=0, nullable=False)
    critical_signals_count = Column(Integer, default=0, nullable=False)
    high_priority_count = Column(Integer, default=0, nullable=False)
    avg_resolution_time_hours = Column(Integer, default=0, nullable=False)
    
    # Paramètres de génération
    date_range_start = Column(DateTime(timezone=True), nullable=True)
    date_range_end = Column(DateTime(timezone=True), nullable=True)
    filters_applied = Column(JSON, nullable=True)
    sort_config = Column(JSON, nullable=True)
    
    # Configuration partage
    shared_with_users = Column(JSON, nullable=True)
    shared_with_sectors = Column(JSON, nullable=True)
    auto_share_enabled = Column(Boolean, default=False, nullable=False)
    notification_enabled = Column(Boolean, default=True, nullable=False)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    parent_report_id = Column(Integer, nullable=True)
    change_log = Column(JSON, nullable=True)
    
    # Statut et validation
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.GENERATING)
    validated_by = Column(Integer, nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Analytics des rapports
    view_count = Column(Integer, default=0, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    average_rating = Column(Integer, default=0, nullable=False)
    feedback_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    generator = relationship("User", foreign_keys=[generated_by])
    signal = relationship("Signal", back_populates="reports", foreign_keys=[signal_id])
    
    def __repr__(self):
        return f"<Report(id={self.id}, code={self.report_code}, type={self.report_type.value})>"
    
    @property
    def is_completed(self) -> bool:
        """Vérifie si le rapport est terminé"""
        return self.status == ReportStatus.COMPLETED
    
    @property
    def is_validated(self) -> bool:
        """Vérifie si le rapport est validé"""
        return self.status == ReportStatus.VALIDATED
    
    @property
    def duration_hours(self) -> Optional[float]:
        """Calcule la durée de génération en heures"""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() / 3600
        return None
    
    def add_feedback(self, rating: int, comment: Optional[str] = None):
        """Ajoute un feedback au rapport"""
        if not self.feedback_list:
            self.feedback_list = []
        self.feedback_list.append({
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now().isoformat()
        })
        if rating > 0:
            total_ratings = len(self.feedback_list)
            self.average_rating = sum(f["rating"] for f in self.feedback_list) / total_ratings
    
    def update_analytics(self, analytics_data: dict):
        """Met à jour les analytics du rapport"""
        if not self.analytics_data:
            self.analytics_data = {}
        self.analytics_data.update(analytics_data)
        self.updated_at = datetime.now()
    
    def add_change_log(self, change_description: str, changed_by: Optional[str] = None):
        """Ajoute une entrée au journal des modifications"""
        if not self.change_log:
            self.change_log = []
        self.change_log.append({
            "description": change_description,
            "changed_by": changed_by,
            "changed_at": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def mark_as_error(self, error_message: str):
        """Marque le rapport comme en erreur"""
        self.status = ReportStatus.ERROR
        self.error_message = error_message
        if not self.report_metadata:
            self.report_metadata = {}
        self.report_metadata["error_message"] = error_message
        self.report_metadata["failed_at"] = datetime.now().isoformat()
        self.updated_at = datetime.now()
    
    def mark_as_completed(self, processing_time_ms: Optional[int] = None):
        """Marque le rapport comme terminé"""
        self.status = ReportStatus.COMPLETED
        self.generated_at = datetime.now()
        if processing_time_ms:
            self.ai_processing_time_ms = processing_time_ms
        self.updated_at = datetime.now()
    
    def mark_as_failed(self, error_message: str):
        """Marque le rapport comme échoué"""
        self.status = ReportStatus.FAILED
        if not self.metadata:
            self.metadata = {}
        self.metadata["error_message"] = error_message
        self.metadata["failed_at"] = datetime.now().isoformat()
        self.updated_at = datetime.now()
