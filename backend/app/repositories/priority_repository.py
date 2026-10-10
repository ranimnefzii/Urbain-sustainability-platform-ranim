"""
Priority Repository - Urbain Sustainability System
Repository pour la gestion des priorités
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.priority import Priority, PriorityLevel, SeverityLevel, UrgencyLevel, ImpactLevel
from app.schemas.priority import PriorityCreate, PriorityUpdate


class PriorityRepository(BaseRepository[Priority, PriorityCreate, PriorityUpdate]):
    """
    Repository pour les opérations CRUD sur les priorités
    """
    
    async def get_by_level(self, *, priority_level: PriorityLevel) -> Optional[Priority]:
        """
        Récupère une priorité par son niveau
        """
        result = await self.db.execute(
            select(Priority).where(Priority.priority_level == priority_level)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, *, code: str) -> Optional[Priority]:
        """
        Récupère une priorité par son code
        """
        result = await self.db.execute(
            select(Priority).where(func.upper(Priority.code) == code.upper())
        )
        return result.scalar_one_or_none()
    
    async def get_by_severity(self, *, severity_level: SeverityLevel) -> Optional[Priority]:
        """
        Récupère une priorité par son niveau de sévérité
        """
        result = await self.db.execute(
            select(Priority).where(Priority.severity_level == severity_level)
        )
        return result.scalar_one_or_none()
    
    async def get_by_urgency(self, *, urgency_level: UrgencyLevel) -> Optional[Priority]:
        """
        Récupère une priorité par son niveau d'urgence
        """
        result = await self.db.execute(
            select(Priority).where(Priority.urgency_level == urgency_level)
        )
        return result.scalar_one_or_none()
    
    async def get_by_impact(self, *, impact_level: ImpactLevel) -> Optional[Priority]:
        """
        Récupère une priorité par son niveau d'impact
        """
        result = await self.db.execute(
            select(Priority).where(Priority.impact_level == impact_level)
        )
        return result.scalar_one_or_none()
    
    async def get_critical_priorities(self) -> List[Priority]:
        """
        Récupère les priorités critiques
        """
        result = await self.db.execute(
            select(Priority)
            .where(Priority.priority_level == PriorityLevel.CRITICAL)
            .order_by(Priority.severity_level, Priority.urgency_level, Priority.impact_level)
        )
        return result.scalars().all()
    
    async def get_high_priorities(self) -> List[Priority]:
        """
        Récupère les priorités élevées
        """
        result = await self.db.execute(
            select(Priority)
            .where(Priority.priority_level == PriorityLevel.HIGH)
            .order_by(Priority.severity_level, Priority.urgency_level, Priority.impact_level)
        )
        return result.scalars().all()
    
    async def search_priorities(
        self, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Priority]:
        """
        Recherche des priorités par nom ou description
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(Priority)
            .where(
                or_(
                    func.lower(Priority.name).like(search_pattern),
                    func.lower(Priority.description).like(search_pattern),
                    func.lower(Priority.code).like(search_pattern)
                )
            )
            .order_by(Priority.priority_level, Priority.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_priorities_by_matrix(
        self, 
        *, 
        severity: SeverityLevel, 
        urgency: UrgencyLevel
    ) -> List[Priority]:
        """
        Récupère les priorités selon une matrice sévérité/urgence
        """
        result = await self.db.execute(
            select(Priority)
            .where(
                and_(
                    Priority.severity_level == severity,
                    Priority.urgency_level == urgency
                )
            )
            .order_by(Priority.priority_level)
        )
        return result.scalars().all()
    
    async def get_priority_matrix(self) -> List[Dict[str, Any]]:
        """
        Construit la matrice complète des priorités
        """
        result = await self.db.execute(
            select(Priority).order_by(
                Priority.severity_level,
                Priority.urgency_level,
                Priority.impact_level,
                Priority.priority_level
            )
        )
        priorities = result.scalars().all()
        
        matrix = []
        for priority in priorities:
            matrix.append({
                "id": priority.id,
                "name": priority.name,
                "code": priority.code,
                "priority_level": priority.priority_level.value,
                "severity_level": priority.severity_level.value,
                "urgency_level": priority.urgency_level.value,
                "impact_level": priority.impact_level.value,
                "max_response_time_minutes": priority.max_response_time_minutes,
                "max_resolution_time_hours": priority.max_resolution_time_hours,
                "escalation_time_hours": priority.escalation_time_hours,
                "ai_weight": priority.ai_weight,
                "auto_assignment_threshold": priority.auto_assignment_threshold,
                "requires_human_review": priority.requires_human_review,
                "notification_frequency": priority.notification_frequency,
                "escalation_enabled": priority.escalation_enabled,
                "color": priority.color,
                "icon": priority.icon,
                "badge_style": priority.badge_style
            })
        
        return matrix
    
    async def check_code_exists(self, *, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un code de priorité existe déjà
        """
        query = select(func.count(Priority.id)).where(
            func.upper(Priority.code) == code.upper()
        )
        
        if exclude_id:
            query = query.where(Priority.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def check_name_exists(self, *, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un nom de priorité existe déjà
        """
        query = select(func.count(Priority.id)).where(
            func.lower(Priority.name) == name.lower()
        )
        
        if exclude_id:
            query = query.where(Priority.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def get_priority_statistics(self, *, priority_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une priorité
        """
        from app.models.signal import Signal
        
        # Statistiques de base
        priority = await self.get(id=priority_id)
        if not priority:
            return {}
        
        # Statistiques des signalements
        signals_query = select(func.count(Signal.id)).where(Signal.priority_id == priority_id)
        signals_result = await self.db.execute(signals_query)
        total_signals = signals_result.scalar()
        
        # Statistiques par statut
        status_query = select(
            Signal.status,
            func.count(Signal.id).label("count")
        ).where(Signal.priority_id == priority_id).group_by(Signal.status)
        
        status_result = await self.db.execute(status_query)
        status_stats = {row.status.value: row.count for row in status_result}
        
        # Taux d'escalation
        escalation_query = select(
            func.count(Signal.id)
        ).where(
            and_(
                Signal.priority_id == priority_id,
                Signal.status.in_([
                    "escalated",  # À adapter selon les statuts réels
                    "overdue"
                ])
            )
        )
        escalation_result = await self.db.execute(escalation_query)
        escalation_count = escalation_result.scalar()
        
        escalation_rate = (escalation_count / total_signals * 100) if total_signals > 0 else 0
        
        return {
            "priority_id": priority_id,
            "name": priority.name,
            "code": priority.code,
            "priority_level": priority.priority_level.value,
            "severity_level": priority.severity_level.value,
            "urgency_level": priority.urgency_level.value,
            "impact_level": priority.impact_level.value,
            "total_signals": total_signals,
            "signals_by_status": status_stats,
            "escalation_count": escalation_count,
            "escalation_rate": round(escalation_rate, 2),
            "avg_resolution_time_hours": priority.avg_resolution_time_hours,
            "max_response_time_minutes": priority.max_response_time_minutes,
            "max_resolution_time_hours": priority.max_resolution_time_hours,
            "ai_weight": priority.ai_weight,
            "auto_assignment_threshold": priority.auto_assignment_threshold,
            "requires_human_review": priority.requires_human_review,
            "notification_frequency": priority.notification_frequency,
            "escalation_enabled": priority.escalation_enabled,
            "created_at": priority.created_at,
            "updated_at": priority.updated_at
        }
    
    async def get_priorities_by_weight(self, *, min_weight: int = 1, max_weight: int = 10) -> List[Priority]:
        """
        Récupère les priorités par plage de poids IA
        """
        result = await self.db.execute(
            select(Priority)
            .where(
                and_(
                    Priority.ai_weight >= min_weight,
                    Priority.ai_weight <= max_weight
                )
            )
            .order_by(Priority.ai_weight.desc(), Priority.name)
        )
        return result.scalars().all()
    
    async def get_priorities_for_assignment(
        self, 
        *, 
        confidence_score: float,
        requires_human_review: bool = False
    ) -> List[Priority]:
        """
        Récupère les priorités éligibles pour l'assignation automatique
        """
        result = await self.db.execute(
            select(Priority)
            .where(
                and_(
                    Priority.auto_assignment_threshold <= confidence_score,
                    or_(
                        Priority.requires_human_review == False,
                        requires_human_review == True
                    )
                )
            )
            .order_by(Priority.priority_level)
        )
        return result.scalars().all()
    
    async def get_overdue_priorities(self) -> List[Priority]:
        """
        Récupère les priorités avec beaucoup de signalements en retard
        """
        from app.models.signal import Signal
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(hours=24)
        
        # Sous-requête pour compter les signalements en retard par priorité
        overdue_signals = select(
            Signal.priority_id,
            func.count(Signal.id).label("overdue_count")
        ).where(
            and_(
                Signal.created_at < cutoff_date,
                Signal.status.in_([
                    SignalStatus.SUBMITTED,
                    SignalStatus.UNDER_REVIEW,
                    SignalStatus.ASSIGNED,
                    SignalStatus.IN_PROGRESS
                ])
            )
        ).group_by(Signal.priority_id)
        
        overdue_result = await self.db.execute(overdue_signals)
        overdue_counts = {row.priority_id: row.overdue_count for row in overdue_result}
        
        # Récupérer les priorités avec signalements en retard
        if overdue_counts:
            result = await self.db.execute(
                select(Priority)
                .where(Priority.id.in_(list(overdue_counts.keys())))
                .order_by(Priority.priority_level)
            )
            return result.scalars().all()
        
        return []
    
    async def update_ai_weights(self, *, updates: List[Dict[str, Any]]) -> int:
        """
        Met à jour les poids IA de plusieurs priorités
        """
        from sqlalchemy import update
        
        updated_count = 0
        for update_data in updates:
            if "id" in update_data and "ai_weight" in update_data:
                stmt = (
                    update(Priority)
                    .where(Priority.id == update_data["id"])
                    .values(ai_weight=update_data["ai_weight"])
                )
                result = await self.db.execute(stmt)
                updated_count += result.rowcount
        
        if updated_count > 0:
            await self.db.commit()
        
        return updated_count
    
    async def get_priority_effectiveness(self, *, days: int = 30) -> List[Dict[str, Any]]:
        """
        Analyse l'effectivité des priorités
        """
        from app.models.signal import Signal
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Requête complexe pour analyser l'effectivité
        result = await self.db.execute(
            select(
                Priority.id,
                Priority.name,
                Priority.priority_level,
                func.count(Signal.id).label("total_signals"),
                func.avg(
                    func.extract("epoch from", Signal.resolved_at) - 
                    func.extract("epoch from", Signal.created_at)
                ).label("avg_resolution_hours")
            )
            .join(Signal, Priority.id == Signal.priority_id)
            .where(Signal.created_at >= start_date)
            .group_by(Priority.id, Priority.name, Priority.priority_level)
            .order_by(Priority.priority_level)
        )
        
        return [
            {
                "priority_id": row.id,
                "name": row.name,
                "priority_level": row.priority_level.value,
                "total_signals": row.total_signals,
                "avg_resolution_hours": float(row.avg_resolution_hours) if row.avg_resolution_hours else 0,
                "effectiveness_score": self._calculate_effectiveness_score(
                    row.total_signals, 
                    float(row.avg_resolution_hours) if row.avg_resolution_hours else 0
                )
            }
            for row in result
        ]
    
    def _calculate_effectiveness_score(self, total_signals: int, avg_resolution_hours: float) -> float:
        """
        Calcule un score d'effectivité pour une priorité
        Plus le score est élevé, plus la priorité est effective
        """
        if total_signals == 0:
            return 0.0
        
        # Score basé sur le nombre de signalements et le temps de résolution moyen
        volume_score = min(100, total_signals / 10)  # Max 100 points pour 1000+ signalements
        speed_score = max(0, 100 - (avg_resolution_hours * 2))  # Max 100 points pour < 50h résolution
        
        return (volume_score + speed_score) / 2  # Moyenne des deux scores
