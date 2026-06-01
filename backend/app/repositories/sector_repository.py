"""
Sector Repository - Urbain Sustainability System
Repository pour la gestion des secteurs
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.sector import Sector, SectorType, SectorStatus
from app.schemas.sector import SectorCreate, SectorUpdate


class SectorRepository(BaseRepository[Sector, SectorCreate, SectorUpdate]):
    """
    Repository pour les opérations CRUD sur les secteurs
    """
    
    async def get_by_code(self, *, code: str) -> Optional[Sector]:
        """
        Récupère un secteur par son code
        """
        result = await self.db.execute(
            select(Sector).where(
                and_(
                    func.upper(Sector.code) == code.upper(),
                    Sector.status != SectorStatus.INACTIVE
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_type(
        self, 
        *, 
        sector_type: SectorType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sector]:
        """
        Récupère les secteurs par type
        """
        result = await self.db.execute(
            select(Sector)
            .where(
                and_(
                    Sector.sector_type == sector_type,
                    Sector.status == SectorStatus.ACTIVE
                )
            )
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_sectors(self, *, skip: int = 0, limit: int = 100) -> List[Sector]:
        """
        Récupère les secteurs actifs
        """
        result = await self.db.execute(
            select(Sector)
            .where(Sector.status == SectorStatus.ACTIVE)
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_sectors(self, *, search_term: str, skip: int = 0, limit: int = 100) -> List[Sector]:
        """
        Recherche des secteurs par nom ou description
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(Sector)
            .where(
                and_(
                    or_(
                        func.lower(Sector.name).like(search_pattern),
                        func.lower(Sector.description).like(search_pattern),
                        func.lower(Sector.code).like(search_pattern)
                    ),
                    Sector.status != SectorStatus.INACTIVE
                )
            )
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_sectors_by_city(
        self, 
        *, 
        city: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sector]:
        """
        Récupère les secteurs par ville
        """
        result = await self.db.execute(
            select(Sector)
            .where(
                and_(
                    func.lower(Sector.city) == city.lower(),
                    Sector.status == SectorStatus.ACTIVE
                )
            )
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_sectors_by_priority_level(
        self, 
        *, 
        priority_level: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sector]:
        """
        Récupère les secteurs par niveau de priorité
        """
        result = await self.db.execute(
            select(Sector)
            .where(
                and_(
                    Sector.priority_level == priority_level,
                    Sector.status == SectorStatus.ACTIVE
                )
            )
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_sectors_with_users(self, *, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les secteurs avec leurs utilisateurs
        """
        result = await self.db.execute(
            select(Sector)
            .options(selectinload(Sector.users))
            .where(Sector.status == SectorStatus.ACTIVE)
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        sectors = result.scalars().all()
        
        return [
            {
                "id": sector.id,
                "name": sector.name,
                "code": sector.code,
                "sector_type": sector.sector_type.value,
                "status": sector.status.value,
                "city": sector.city,
                "manager_name": sector.manager_name,
                "manager_email": sector.manager_email,
                "priority_level": sector.priority_level,
                "max_daily_signals": sector.max_daily_signals,
                "avg_processing_time_hours": sector.avg_processing_time_hours,
                "total_signals_processed": sector.total_signals_processed,
                "avg_resolution_time_hours": sector.avg_resolution_time_hours,
                "satisfaction_rate": sector.satisfaction_rate,
                "users_count": len(sector.users) if sector.users else 0,
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.value,
                        "status": user.status.value
                    }
                    for user in (sector.users or [])
                ]
            }
            for sector in sectors
        ]
    
    async def check_code_exists(self, *, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un code de secteur existe déjà
        """
        query = select(func.count(Sector.id)).where(
            func.upper(Sector.code) == code.upper()
        )
        
        if exclude_id:
            query = query.where(Sector.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def check_name_exists(self, *, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un nom de secteur existe déjà
        """
        query = select(func.count(Sector.id)).where(
            func.lower(Sector.name) == name.lower()
        )
        
        if exclude_id:
            query = query.where(Sector.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def get_sector_statistics(self, *, sector_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un secteur
        """
        from app.models.signal import Signal
        from app.models.user import User
        
        # Statistiques de base
        sector = await self.get(id=sector_id)
        if not sector:
            return {}
        
        # Statistiques des signalements
        signals_query = select(func.count(Signal.id)).where(
            and_(
                Signal.assigned_sector_id == sector_id,
                Signal.status.in_([
                    "resolved",  # À adapter selon les statuts réels
                    "closed"
                ])
            )
        )
        signals_result = await self.db.execute(signals_query)
        total_signals_processed = signals_result.scalar()
        
        # Statistiques des utilisateurs
        users_query = select(func.count(User.id)).where(
            and_(
                User.sector_id == sector_id,
                User.status == "active"  # À adapter selon les statuts réels
            )
        )
        users_result = await self.db.execute(users_query)
        total_users = users_result.scalar()
        
        return {
            "sector_id": sector_id,
            "name": sector.name,
            "code": sector.code,
            "sector_type": sector.sector_type.value,
            "status": sector.status.value,
            "city": sector.city,
            "manager_name": sector.manager_name,
            "manager_email": sector.manager_email,
            "priority_level": sector.priority_level,
            "max_daily_signals": sector.max_daily_signals,
            "avg_processing_time_hours": sector.avg_processing_time_hours,
            "total_signals_processed": sector.total_signals_processed,
            "avg_resolution_time_hours": sector.avg_resolution_time_hours,
            "satisfaction_rate": sector.satisfaction_rate,
            "total_users": total_users,
            "auto_assignment_enabled": sector.auto_assignment_enabled,
            "escalation_enabled": sector.escalation_enabled,
            "ai_confidence_threshold": sector.ai_confidence_threshold,
            "created_at": sector.created_at,
            "updated_at": sector.updated_at
        }
    
    async def get_sectors_workload(self, *, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Analyse la charge de travail des secteurs
        """
        from app.models.signal import Signal
        from datetime import datetime, timedelta
        
        # Période d'analyse (derniers 7 jours)
        start_date = datetime.now() - timedelta(days=7)
        
        result = await self.db.execute(
            select(
                Sector.id,
                Sector.name,
                Sector.code,
                Sector.max_daily_signals,
                func.count(Signal.id).label("current_signals"),
                func.count(
                    func.case(
                        (Signal.status.in_(["in_progress", "assigned"]), 1),
                        else_=0
                    )
                ).label("active_signals"),
                func.count(
                    func.case(
                        (Signal.created_at >= start_date, 1),
                        else_=0
                    )
                ).label("recent_signals")
            )
            .outerjoin(Signal, Sector.id == Signal.assigned_sector_id)
            .where(Sector.status == SectorStatus.ACTIVE)
            .group_by(Sector.id, Sector.name, Sector.code, Sector.max_daily_signals)
            .order_by(Sector.name)
            .limit(limit)
        )
        
        workload_data = []
        for row in result:
            current_workload = row.current_signals or 0
            max_capacity = row.max_daily_signals
            utilization_percentage = (current_workload / max_capacity * 100) if max_capacity > 0 else 0
            
            workload_data.append({
                "sector_id": row.id,
                "sector_name": row.name,
                "sector_code": row.code,
                "current_workload": current_workload,
                "max_capacity": max_capacity,
                "utilization_percentage": round(utilization_percentage, 2),
                "active_signals": row.active_signals or 0,
                "recent_signals": row.recent_signals or 0,
                "workload_status": "high" if utilization_percentage > 80 else "medium" if utilization_percentage > 50 else "low"
            })
        
        return workload_data
    
    async def update_statistics(self, *, sector_id: int) -> bool:
        """
        Met à jour les statistiques d'un secteur
        """
        from app.models.signal import Signal
        
        # Calculer les nouvelles statistiques
        signals_query = select(
            func.count(Signal.id).label("total_processed"),
            func.avg(
                func.extract("epoch from", Signal.resolved_at) - 
                func.extract("epoch from", Signal.created_at)
            ).label("avg_resolution_time")
        ).where(
            and_(
                Signal.assigned_sector_id == sector_id,
                Signal.status == "resolved"  # À adapter
            )
        )
        
        result = await self.db.execute(signals_query)
        stats = result.first()
        
        if stats:
            sector = await self.get(id=sector_id)
            if sector:
                sector.total_signals_processed = stats.total_processed or 0
                sector.avg_resolution_time_hours = int(stats.avg_resolution_time / 3600) if stats.avg_resolution_time else 0
                
                await self.db.commit()
                return True
        
        return False
    
    async def get_sectors_by_category_support(
        self, 
        *, 
        category_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sector]:
        """
        Récupère les secteurs qui supportent une catégorie
        """
        # Utiliser une requête JSON pour vérifier si category_id est dans supported_categories
        result = await self.db.execute(
            select(Sector)
            .where(
                and_(
                    Sector.status == SectorStatus.ACTIVE,
                    # Logic pour vérifier si category_id est dans supported_categories
                    # (à adapter selon la structure JSON de SQLAlchemy)
                    func.jsonb_contains(Sector.supported_categories, str(category_id))
                )
            )
            .order_by(Sector.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def bulk_update_status(
        self, 
        *, 
        sector_ids: List[int], 
        status: SectorStatus
    ) -> int:
        """
        Met à jour le statut de plusieurs secteurs
        """
        from sqlalchemy import update
        
        stmt = (
            update(Sector)
            .where(Sector.id.in_(sector_ids))
            .values(status=status)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def get_sector_performance(
        self, 
        *, 
        sector_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyse la performance d'un secteur
        """
        from app.models.signal import Signal
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Statistiques de performance
        result = await self.db.execute(
            select(
                func.count(Signal.id).label("total_signals"),
                func.count(
                    func.case(
                        (Signal.status == "resolved", 1),
                        else_=0
                    )
                ).label("resolved_signals"),
                func.count(
                    func.case(
                        (Signal.status == "escalated", 1),
                        else_=0
                    )
                ).label("escalated_signals"),
                func.avg(
                    func.extract("epoch", Signal.resolved_at) - func.extract("epoch", Signal.created_at)
                ).label("avg_resolution_hours")
            )
            .where(
                and_(
                    Signal.assigned_sector_id == sector_id,
                    Signal.created_at >= start_date
                )
            )
        )
        
        stats = result.first()
        
        if stats:
            resolution_rate = (stats.resolved_signals / stats.total_signals * 100) if stats.total_signals > 0 else 0
            escalation_rate = (stats.escalated_signals / stats.total_signals * 100) if stats.total_signals > 0 else 0
            
            return {
                "sector_id": sector_id,
                "period_days": days,
                "total_signals": stats.total_signals,
                "resolved_signals": stats.resolved_signals,
                "escalated_signals": stats.escalated_signals,
                "resolution_rate": round(resolution_rate, 2),
                "escalation_rate": round(escalation_rate, 2),
                "avg_resolution_hours": float(stats.avg_resolution_hours) if stats.avg_resolution_hours else 0,
                "performance_score": self._calculate_performance_score(resolution_rate, escalation_rate)
            }
        
        return {}
    
    def _calculate_performance_score(self, resolution_rate: float, escalation_rate: float) -> float:
        """
        Calcule un score de performance pour un secteur
        """
        # Score basé sur le taux de résolution (70%) et le taux d'escalation (-30%)
        score = (resolution_rate * 0.7) - (escalation_rate * 0.3)
        return max(0, min(100, score))
