"""
Signal Repository - Urbain Sustainability System
Repository pour la gestion des signalements
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.signal import Signal, SignalStatus, SignalSource, VerificationStatus
from app.schemas.signal import SignalCreate, SignalUpdate


class SignalRepository(BaseRepository[Signal, SignalCreate, SignalUpdate]):
    """
    Repository pour les opérations CRUD sur les signalements
    """
    
    async def get_by_reference_number(self, *, reference_number: str) -> Optional[Signal]:
        """
        Récupère un signalement par son numéro de référence
        """
        result = await self.db.execute(
            select(Signal).where(Signal.reference_number == reference_number)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements d'un utilisateur
        """
        result = await self.db.execute(
            select(Signal)
            .where(Signal.created_by == user_id)
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(
        self, 
        *, 
        status: SignalStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements par statut
        """
        result = await self.db.execute(
            select(Signal)
            .where(Signal.status == status)
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_category(
        self, 
        *, 
        category_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements par catégorie
        """
        result = await self.db.execute(
            select(Signal)
            .where(Signal.category_id == category_id)
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_priority(
        self, 
        *, 
        priority_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements par priorité
        """
        result = await self.db.execute(
            select(Signal)
            .where(Signal.priority_id == priority_id)
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_location_bounds(
        self, 
        *, 
        lat_min: float, 
        lat_max: float, 
        lng_min: float, 
        lng_max: float,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements dans une zone géographique
        """
        result = await self.db.execute(
            select(Signal)
            .where(
                and_(
                    Signal.latitude >= lat_min,
                    Signal.latitude <= lat_max,
                    Signal.longitude >= lng_min,
                    Signal.longitude <= lng_max
                )
            )
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_signals(
        self, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Recherche des signalements par titre ou description
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(Signal)
            .where(
                or_(
                    func.lower(Signal.title).like(search_pattern),
                    func.lower(Signal.description).like(search_pattern),
                    func.lower(Signal.address).like(search_pattern)
                )
            )
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_overdue_signals(self, *, skip: int = 0, limit: int = 100) -> List[Signal]:
        """
        Récupère les signalements en retard
        """
        from datetime import datetime, timedelta
        from app.models.priority import Priority
        
        # Requête complexe pour trouver les signalements en retard
        # basée sur leur priorité et date de création
        result = await self.db.execute(
            select(Signal)
            .join(Priority)
            .where(
                and_(
                    Signal.status.in_([
                        SignalStatus.SUBMITTED,
                        SignalStatus.UNDER_REVIEW,
                        SignalStatus.ASSIGNED,
                        SignalStatus.IN_PROGRESS
                    ]),
                    # Logique pour déterminer si en retard
                    # (à simplifier avec la logique métier réelle)
                    Signal.created_at < datetime.now() - timedelta(hours=24)
                )
            )
            .order_by(desc(Priority.priority_level), desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_signals_with_filters(
        self, 
        *, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[Signal]:
        """
        Récupère les signalements avec filtres multiples
        """
        query = select(Signal)
        
        # Application des filtres
        if "status" in filters:
            if isinstance(filters["status"], list):
                query = query.where(Signal.status.in_(filters["status"]))
            else:
                query = query.where(Signal.status == filters["status"])
        
        if "category_id" in filters:
            if isinstance(filters["category_id"], list):
                query = query.where(Signal.category_id.in_(filters["category_id"]))
            else:
                query = query.where(Signal.category_id == filters["category_id"])
        
        if "priority_id" in filters:
            if isinstance(filters["priority_id"], list):
                query = query.where(Signal.priority_id.in_(filters["priority_id"]))
            else:
                query = query.where(Signal.priority_id == filters["priority_id"])
        
        if "created_by" in filters:
            query = query.where(Signal.created_by == filters["created_by"])
        
        if "assigned_sector_id" in filters:
            query = query.where(Signal.assigned_sector_id == filters["assigned_sector_id"])
        
        if "start_date" in filters:
            query = query.where(Signal.created_at >= filters["start_date"])
        
        if "end_date" in filters:
            query = query.where(Signal.created_at <= filters["end_date"])
        
        if "is_anonymous" in filters:
            query = query.where(Signal.is_anonymous == filters["is_anonymous"])
        
        # Filtres géographiques
        if "latitude_min" in filters:
            query = query.where(Signal.latitude >= filters["latitude_min"])
        if "latitude_max" in filters:
            query = query.where(Signal.latitude <= filters["latitude_max"])
        if "longitude_min" in filters:
            query = query.where(Signal.longitude >= filters["longitude_min"])
        if "longitude_max" in filters:
            query = query.where(Signal.longitude <= filters["longitude_max"])
        
        # Filtres IA
        if "ai_confidence_min" in filters:
            query = query.where(Signal.ai_confidence_score >= filters["ai_confidence_min"])
        
        # Application du tri
        if hasattr(Signal, order_by):
            order_column = getattr(Signal, order_by)
            if order_direction == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_signal_with_relations(self, *, signal_id: int) -> Optional[Signal]:
        """
        Récupère un signalement avec toutes ses relations
        """
        result = await self.db.execute(
            select(Signal)
            .options(
                selectinload(Signal.created_by_user),
                selectinload(Signal.processed_by_user),
                selectinload(Signal.category),
                selectinload(Signal.priority),
                selectinload(Signal.reports)
            )
            .where(Signal.id == signal_id)
        )
        return result.scalar_one_or_none()
    
    async def get_signals_by_date_range(
        self, 
        *, 
        start_date, 
        end_date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements dans une plage de dates
        """
        result = await self.db.execute(
            select(Signal)
            .where(
                and_(
                    Signal.created_at >= start_date,
                    Signal.created_at <= end_date
                )
            )
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_signals_near_location(
        self, 
        *, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 5.0,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Signal]:
        """
        Récupère les signalements près d'une localisation
        """
        # Formule de Haversine simplifiée pour la distance
        # En pratique, on utiliserait PostGIS ou une extension géospatiale
        lat_delta = radius_km / 111.0  # Approximation
        lng_delta = radius_km / (111.0 * abs(latitude))
        
        result = await self.db.execute(
            select(Signal)
            .where(
                and_(
                    Signal.latitude >= (latitude - lat_delta),
                    Signal.latitude <= (latitude + lat_delta),
                    Signal.longitude >= (longitude - lng_delta),
                    Signal.longitude <= (longitude + lng_delta)
                )
            )
            .order_by(desc(Signal.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_signal_statistics(self, *, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calcule les statistiques des signalements
        """
        query = select(Signal)
        
        # Application des filtres pour les statistiques
        if filters:
            if "status" in filters:
                if isinstance(filters["status"], list):
                    query = query.where(Signal.status.in_(filters["status"]))
                else:
                    query = query.where(Signal.status == filters["status"])
            
            if "start_date" in filters:
                query = query.where(Signal.created_at >= filters["start_date"])
            
            if "end_date" in filters:
                query = query.where(Signal.created_at <= filters["end_date"])
        
        # Statistiques par statut
        subq = query.subquery()
        status_query = select(
            subq.c.status,
            func.count(subq.c.id).label("count")
        ).select_from(subq).group_by(subq.c.status)
        
        status_result = await self.db.execute(status_query)
        status_stats = {}
        for row in status_result:
            s = row.status
            if hasattr(s, 'value'):
                s = s.value
            status_stats[s] = row.count
        
        # Statistiques par catégorie
        category_query = select(
            subq.c.category_id,
            func.count(subq.c.id).label("count")
        ).select_from(subq).group_by(subq.c.category_id)
        
        category_result = await self.db.execute(category_query)
        category_stats = {row.category_id: row.count for row in category_result}
        
        # Statistiques générales
        total_query = select(func.count(subq.c.id)).select_from(subq)
        total_result = await self.db.execute(total_query)
        total_signals = total_result.scalar()
        
        return {
            "total_signals": total_signals,
            "signals_by_status": status_stats,
            "signals_by_category": category_stats,
            "filters_applied": filters or {}
        }
    
    async def update_status(self, *, signal_id: int, status: SignalStatus, notes: Optional[str] = None) -> bool:
        """
        Met à jour le statut d'un signalement
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Signal).where(Signal.id == signal_id)
        )
        signal = result.scalar_one_or_none()
        
        if signal:
            signal.status = status
            signal.updated_at = datetime.now()
            signal.last_activity_at = datetime.now()
            
            if notes:
                if not signal.internal_notes:
                    signal.internal_notes = ""
                signal.internal_notes += f"\n[{datetime.now().isoformat()}] Status update: {notes}"
            
            await self.db.commit()
            return True
        return False
    
    async def assign_to_user(self, *, signal_id: int, user_id: int, sector_id: Optional[int] = None) -> bool:
        """
        Assigne un signalement à un utilisateur
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Signal).where(Signal.id == signal_id)
        )
        signal = result.scalar_one_or_none()
        
        if signal:
            signal.processed_by = user_id
            signal.assigned_sector_id = sector_id
            signal.assigned_at = datetime.now()
            signal.status = SignalStatus.ASSIGNED
            signal.updated_at = datetime.now()
            signal.last_activity_at = datetime.now()
            
            await self.db.commit()
            return True
        return False
    
    async def bulk_update_status(
        self, 
        *, 
        signal_ids: List[int], 
        status: SignalStatus
    ) -> int:
        """
        Met à jour le statut de plusieurs signalements
        """
        from datetime import datetime
        from sqlalchemy import update
        
        stmt = (
            update(Signal)
            .where(Signal.id.in_(signal_ids))
            .values(
                status=status,
                updated_at=datetime.now(),
                last_activity_at=datetime.now()
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def get_signals_for_map(
        self, 
        *, 
        bounds: Optional[Dict[str, float]] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Récupère les signalements pour affichage sur carte
        """
        query = select(
            Signal.id,
            Signal.reference_number,
            Signal.title,
            Signal.status,
            Signal.latitude,
            Signal.longitude,
            Signal.created_at,
            Signal.category_id,
            Signal.priority_id
        )
        
        # Application des filtres
        if filters:
            if "status" in filters:
                if isinstance(filters["status"], list):
                    query = query.where(Signal.status.in_(filters["status"]))
                else:
                    query = query.where(Signal.status == filters["status"])
        
        # Filtres géographiques
        if bounds:
            query = query.where(
                and_(
                    Signal.latitude >= bounds["lat_min"],
                    Signal.latitude <= bounds["lat_max"],
                    Signal.longitude >= bounds["lng_min"],
                    Signal.longitude <= bounds["lng_max"]
                )
            )
        
        query = query.order_by(desc(Signal.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "reference_number": row.reference_number,
                "title": row.title,
                "status": row.status.value,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "created_at": row.created_at,
                "category_id": row.category_id,
                "priority_id": row.priority_id
            }
            for row in rows
        ]
    
    async def get_hotspots(self, *, days: int = 30, grid_size: float = 0.01) -> List[Dict[str, Any]]:
        """
        Identifie les points chauds (clusters de signalements)
        """
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Regroupement par zone géographique (grid)
        lat_grid = func.floor(Signal.latitude / grid_size) * grid_size
        lng_grid = func.floor(Signal.longitude / grid_size) * grid_size
        
        query = select(
            lat_grid.label("lat_grid"),
            lng_grid.label("lng_grid"),
            func.count(Signal.id).label("signal_count"),
            func.avg(Signal.ai_priority_score).label("avg_priority")
        ).where(
            Signal.created_at >= start_date
        ).group_by(
            lat_grid,
            lng_grid
        ).having(
            func.count(Signal.id) >= 3  # Minimum 3 signalements pour être un hotspot
        ).order_by(
            desc("signal_count")
        ).limit(50)
        
        result = await self.db.execute(query)
        
        return [
            {
                "latitude": float(row.lat_grid) + grid_size / 2,
                "longitude": float(row.lng_grid) + grid_size / 2,
                "signal_count": row.signal_count,
                "avg_priority": float(row.avg_priority) if row.avg_priority else 0,
                "intensity": "high" if row.signal_count >= 10 else "medium"
            }
            for row in result
        ]
