"""
Report Repository - Urbain Sustainability System
Repository pour la gestion des rapports
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.report import Report, ReportType, ReportStatus, ReportFrequency
from app.schemas.report import ReportCreate, ReportUpdate


class ReportRepository(BaseRepository[Report, ReportCreate, ReportUpdate]):
    """
    Repository pour les opérations CRUD sur les rapports
    """
    
    async def get_by_code(self, *, report_code: str) -> Optional[Report]:
        """
        Récupère un rapport par son code
        """
        result = await self.db.execute(
            select(Report).where(Report.report_code == report_code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_type(
        self, 
        *, 
        report_type: ReportType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports par type
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.report_type == report_type)
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(
        self, 
        *, 
        status: ReportStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports par statut
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.status == status)
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_frequency(
        self, 
        *, 
        frequency: ReportFrequency, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports par fréquence
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.frequency == frequency)
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_user(
        self, 
        *, 
        generated_by: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports générés par un utilisateur
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.generated_by == generated_by)
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_signal(
        self, 
        *, 
        signal_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports associés à un signal
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.signal_id == signal_id)
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_sector(
        self, 
        *, 
        sector_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports d'un secteur
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.sector_id == sector_id)
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_reports(
        self, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Recherche des rapports par titre ou description
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(Report)
            .where(
                or_(
                    func.lower(Report.title).like(search_pattern),
                    func.lower(Report.description).like(search_pattern),
                    func.lower(Report.report_code).like(search_pattern)
                )
            )
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_reports_with_filters(
        self, 
        *, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[Report]:
        """
        Récupère les rapports avec filtres multiples
        """
        query = select(Report)
        
        # Application des filtres
        if "report_type" in filters:
            if isinstance(filters["report_type"], list):
                query = query.where(Report.report_type.in_(filters["report_type"]))
            else:
                query = query.where(Report.report_type == filters["report_type"])
        
        if "status" in filters:
            if isinstance(filters["status"], list):
                query = query.where(Report.status.in_(filters["status"]))
            else:
                query = query.where(Report.status == filters["status"])
        
        if "frequency" in filters:
            if isinstance(filters["frequency"], list):
                query = query.where(Report.frequency.in_(filters["frequency"]))
            else:
                query = query.where(Report.frequency == filters["frequency"])
        
        if "generated_by" in filters:
            query = query.where(Report.generated_by == filters["generated_by"])
        
        if "sector_id" in filters:
            query = query.where(Report.sector_id == filters["sector_id"])
        
        if "signal_id" in filters:
            query = query.where(Report.signal_id == filters["signal_id"])
        
        if "start_date" in filters:
            query = query.where(Report.created_at >= filters["start_date"])
        
        if "end_date" in filters:
            query = query.where(Report.created_at <= filters["end_date"])
        
        if "is_public" in filters:
            query = query.where(Report.is_public == filters["is_public"])
        
        # Application du tri
        if hasattr(Report, order_by):
            order_column = getattr(Report, order_by)
            if order_direction == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_report_with_relations(self, *, report_id: int) -> Optional[Report]:
        """
        Récupère un rapport avec toutes ses relations
        """
        result = await self.db.execute(
            select(Report)
            .options(
                selectinload(Report.generated_by_user),
                selectinload(Report.signal),
                selectinload(Report.reports)
            )
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_reports_by_date_range(
        self, 
        *, 
        start_date, 
        end_date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports dans une plage de dates
        """
        result = await self.db.execute(
            select(Report)
            .where(
                and_(
                    Report.created_at >= start_date,
                    Report.created_at <= end_date
                )
            )
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_completed_reports(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports terminés
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.status == ReportStatus.COMPLETED)
            .order_by(desc(Report.generated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_public_reports(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """
        Récupère les rapports publics
        """
        result = await self.db.execute(
            select(Report)
            .where(
                and_(
                    Report.is_public == True,
                    Report.status == ReportStatus.COMPLETED
                )
            )
            .order_by(desc(Report.generated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_report_statistics(self, *, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calcule les statistiques des rapports
        """
        query = select(Report)
        
        # Application des filtres pour les statistiques
        if filters:
            if "report_type" in filters:
                if isinstance(filters["report_type"], list):
                    query = query.where(Report.report_type.in_(filters["report_type"]))
                else:
                    query = query.where(Report.report_type == filters["report_type"])
            
            if "start_date" in filters:
                query = query.where(Report.created_at >= filters["start_date"])
            
            if "end_date" in filters:
                query = query.where(Report.created_at <= filters["end_date"])
        
        subq = query.subquery()
        
        # Statistiques par type
        type_query = select(
            subq.c.report_type,
            func.count(subq.c.id).label("count")
        ).select_from(subq).group_by(subq.c.report_type)
        
        type_result = await self.db.execute(type_query)
        type_stats = {row.report_type.value: row.count for row in type_result}
        
        # Statistiques par statut
        status_query = select(
            subq.c.status,
            func.count(subq.c.id).label("count")
        ).select_from(subq).group_by(subq.c.status)
        
        status_result = await self.db.execute(status_query)
        status_stats = {row.status.value: row.count for row in status_result}
        
        # Statistiques générales
        total_query = select(func.count(subq.c.id)).select_from(subq)
        total_result = await self.db.execute(total_query)
        total_reports = total_result.scalar()
        
        # Temps moyen de génération
        time_query = select(
            func.avg(
                func.extract("epoch", subq.c.generated_at) - 
                func.extract("epoch", subq.c.created_at)
            ).label("avg_generation_time_seconds")
        ).select_from(subq).where(subq.c.status == ReportStatus.COMPLETED)
        
        time_result = await self.db.execute(time_query)
        avg_generation_time = time_result.scalar()
        
        return {
            "total_reports": total_reports,
            "reports_by_type": type_stats,
            "reports_by_status": status_stats,
            "avg_generation_time_seconds": float(avg_generation_time) if avg_generation_time else 0,
            "filters_applied": filters or {}
        }
    
    async def update_status(self, *, report_id: int, status: ReportStatus, error_message: Optional[str] = None) -> bool:
        """
        Met à jour le statut d'un rapport
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if report:
            report.status = status
            report.updated_at = datetime.now()
            
            if status == ReportStatus.COMPLETED:
                report.generated_at = datetime.now()
            elif status == ReportStatus.FAILED and error_message:
                if not report.metadata:
                    report.metadata = {}
                report.metadata["error_message"] = error_message
                report.metadata["failed_at"] = datetime.now().isoformat()
            
            await self.db.commit()
            return True
        return False
    
    async def mark_as_completed(self, *, report_id: int, processing_time_ms: Optional[int] = None) -> bool:
        """
        Marque un rapport comme terminé
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if report:
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.now()
            report.updated_at = datetime.now()
            if processing_time_ms:
                report.ai_processing_time_ms = processing_time_ms
            
            await self.db.commit()
            return True
        return False
    
    async def mark_as_failed(self, *, report_id: int, error_message: str) -> bool:
        """
        Marque un rapport comme échoué
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if report:
            report.status = ReportStatus.FAILED
            report.updated_at = datetime.now()
            
            if not report.metadata:
                report.metadata = {}
            report.metadata["error_message"] = error_message
            report.metadata["failed_at"] = datetime.now().isoformat()
            
            await self.db.commit()
            return True
        return False
    
    async def get_reports_for_export(
        self, 
        *, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10000
    ) -> List[Report]:
        """
        Récupère les rapports pour export
        """
        query = select(Report)
        
        # Application des filtres
        if filters:
            if "report_type" in filters:
                query = query.where(Report.report_type == filters["report_type"])
            if "status" in filters:
                query = query.where(Report.status == filters["status"])
            if "start_date" in filters:
                query = query.where(Report.created_at >= filters["start_date"])
            if "end_date" in filters:
                query = query.where(Report.created_at <= filters["end_date"])
        
        query = query.order_by(desc(Report.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_most_accessed_reports(
        self, 
        *, 
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Récupère les rapports les plus accédés
        """
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                Report.id,
                Report.title,
                Report.report_code,
                Report.report_type,
                Report.status,
                Report.created_at,
                Report.last_accessed_at
            )
            .where(Report.last_accessed_at >= start_date)
            .order_by(desc(Report.last_accessed_at))
            .limit(limit)
        )
        
        return [
            {
                "id": row.id,
                "title": row.title,
                "report_code": row.report_code,
                "report_type": row.report_type.value,
                "status": row.status.value,
                "created_at": row.created_at,
                "last_accessed_at": row.last_accessed_at
            }
            for row in result
        ]
    
    async def update_access_time(self, *, report_id: int) -> bool:
        """
        Met à jour le temps d'accès d'un rapport
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if report:
            report.last_accessed_at = datetime.now()
            await self.db.commit()
            return True
        return False
