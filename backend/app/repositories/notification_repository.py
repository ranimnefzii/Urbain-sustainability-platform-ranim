"""
Notification Repository - Urbain Sustainability System
Repository pour la gestion des notifications
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus, NotificationPriority
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationUpdate]):
    """
    Repository pour les opérations CRUD sur les notifications
    """
    
    async def get_by_code(self, *, notification_code: str) -> Optional[Notification]:
        """
        Récupère une notification par son code
        """
        result = await self.db.execute(
            select(Notification).where(Notification.notification_code == notification_code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """
        Récupère les notifications d'un utilisateur
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_type(
        self, 
        *, 
        notification_type: NotificationType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """
        Récupère les notifications par type
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.notification_type == notification_type)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_channel(
        self, 
        *, 
        channel: NotificationChannel, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """
        Récupère les notifications par canal
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.channel == channel)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(
        self, 
        *, 
        status: NotificationStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """
        Récupère les notifications par statut
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.status == status)
            .order_by(desc(Notification.created_at))
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
    ) -> List[Notification]:
        """
        Récupère les notifications associées à un signal
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.signal_id == signal_id)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_pending_notifications(self, *, limit: int = 100) -> List[Notification]:
        """
        Récupère les notifications en attente d'envoi
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.status == NotificationStatus.PENDING)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_failed_notifications(self, *, limit: int = 100) -> List[Notification]:
        """
        Récupère les notifications échouées
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.status == NotificationStatus.FAILED)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_notifications(
        self, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """
        Recherche des notifications par titre ou message
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(Notification)
            .where(
                or_(
                    func.lower(Notification.title).like(search_pattern),
                    func.lower(Notification.message).like(search_pattern)
                )
            )
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_notifications_with_filters(
        self, 
        *, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[Notification]:
        """
        Récupère les notifications avec filtres multiples
        """
        query = select(Notification)
        
        # Application des filtres
        if "notification_type" in filters:
            if isinstance(filters["notification_type"], list):
                query = query.where(Notification.notification_type.in_(filters["notification_type"]))
            else:
                query = query.where(Notification.notification_type == filters["notification_type"])
        
        if "channel" in filters:
            if isinstance(filters["channel"], list):
                query = query.where(Notification.channel.in_(filters["channel"]))
            else:
                query = query.where(Notification.channel == filters["channel"])
        
        if "status" in filters:
            if isinstance(filters["status"], list):
                query = query.where(Notification.status.in_(filters["status"]))
            else:
                query = query.where(Notification.status == filters["status"])
        
        if "user_id" in filters:
            query = query.where(Notification.user_id == filters["user_id"])
        
        if "signal_id" in filters:
            query = query.where(Notification.signal_id == filters["signal_id"])
        
        if "start_date" in filters:
            query = query.where(Notification.created_at >= filters["start_date"])
        
        if "end_date" in filters:
            query = query.where(Notification.created_at <= filters["end_date"])
        
        if "requires_action" in filters:
            query = query.where(Notification.requires_action == filters["requires_action"])
        
        # Application du tri
        if hasattr(Notification, order_by):
            order_column = getattr(Notification, order_by)
            if order_direction == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_notification_with_relations(self, *, notification_id: int) -> Optional[Notification]:
        """
        Récupère une notification avec toutes ses relations
        """
        result = await self.db.execute(
            select(Notification)
            .options(
                selectinload(Notification.user),
                selectinload(Notification.signal),
                selectinload(Notification.report)
            )
            .where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def get_unread_notifications(self, *, user_id: int, limit: int = 50) -> List[Notification]:
        """
        Récupère les notifications non lues d'un utilisateur
        """
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status.in_([
                        NotificationStatus.SENT,
                        NotificationStatus.DELIVERED
                    ])
                )
            )
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_notifications_for_retry(self, *, max_retries: int = 3) -> List[Notification]:
        """
        Récupère les notifications qui peuvent être réessayées
        """
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.status == NotificationStatus.FAILED,
                    Notification.retry_count < max_retries
                )
            )
            .order_by(desc(Notification.created_at))
            .limit(100)
        )
        return result.scalars().all()
    
    async def get_notification_statistics(self, *, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calcule les statistiques des notifications
        """
        base = select(Notification)
        
        # Application des filtres pour les statistiques
        if filters:
            if "user_id" in filters:
                base = base.where(Notification.user_id == filters["user_id"])
            if "notification_type" in filters:
                if isinstance(filters["notification_type"], list):
                    base = base.where(Notification.notification_type.in_(filters["notification_type"]))
                else:
                    base = base.where(Notification.notification_type == filters["notification_type"])
            
            if "start_date" in filters:
                base = base.where(Notification.created_at >= filters["start_date"])
            
            if "end_date" in filters:
                base = base.where(Notification.created_at <= filters["end_date"])
        
        subq = base.subquery()
        
        # Statistiques par type
        type_result = await self.db.execute(
            select(subq.c.notification_type, func.count(subq.c.id).label("count"))
            .group_by(subq.c.notification_type)
        )
        type_stats = {}
        for row in type_result:
            type_stats[row.notification_type.value if hasattr(row.notification_type, 'value') else row.notification_type] = row.count
        
        # Statistiques par canal
        channel_result = await self.db.execute(
            select(subq.c.channel, func.count(subq.c.id).label("count"))
            .group_by(subq.c.channel)
        )
        channel_stats = {}
        for row in channel_result:
            channel_stats[row.channel.value if hasattr(row.channel, 'value') else row.channel] = row.count
        
        # Statistiques par statut
        status_result = await self.db.execute(
            select(subq.c.status, func.count(subq.c.id).label("count"))
            .group_by(subq.c.status)
        )
        status_stats = {}
        for row in status_result:
            status_stats[row.status.value if hasattr(row.status, 'value') else row.status] = row.count
        
        # Statistiques générales
        total_result = await self.db.execute(select(func.count(subq.c.id)))
        total_notifications = total_result.scalar()
        
        # Temps moyen de livraison (no group by needed - single aggregate)
        delivery_time_result = await self.db.execute(
            select(func.avg(
                func.extract("epoch", subq.c.delivered_at) - func.extract("epoch", subq.c.sent_at)
            ).label("avg_delivery_time_seconds"))
            .where(subq.c.status == NotificationStatus.DELIVERED)
        )
        avg_delivery_time = delivery_time_result.scalar()
        
        return {
            "total_notifications": total_notifications,
            "notifications_by_type": type_stats,
            "notifications_by_channel": channel_stats,
            "notifications_by_status": status_stats,
            "avg_delivery_time_minutes": float(avg_delivery_time / 60) if avg_delivery_time else 0,
            "filters_applied": filters or {}
        }
    
    async def update_status(self, *, notification_id: int, status: NotificationStatus, error_message: Optional[str] = None) -> bool:
        """
        Met à jour le statut d'une notification
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.status = status
            notification.updated_at = datetime.now()
            
            if status == NotificationStatus.SENT:
                notification.sent_at = datetime.now()
            elif status == NotificationStatus.DELIVERED:
                notification.delivered_at = datetime.now()
            elif status == NotificationStatus.READ:
                notification.read_at = datetime.now()
            elif status == NotificationStatus.FAILED and error_message:
                notification.failed_at = datetime.now()
                notification.error_message = error_message
            
            await self.db.commit()
            return True
        return False
    
    async def increment_retry_count(self, *, notification_id: int) -> bool:
        """
        Incrémente le compteur de retry
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.retry_count += 1
            notification.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def mark_as_read(self, *, notification_id: int) -> bool:
        """
        Marque une notification comme lue
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if notification and notification.status != NotificationStatus.READ:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.now()
            notification.updated_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def bulk_update_status(
        self, 
        *, 
        notification_ids: List[int], 
        status: NotificationStatus
    ) -> int:
        """
        Met à jour le statut de plusieurs notifications
        """
        from datetime import datetime
        from sqlalchemy import update
        
        stmt = (
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .values(
                status=status,
                updated_at=datetime.now()
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def cleanup_old_notifications(self, *, days: int = 30) -> int:
        """
        Supprime les anciennes notifications
        """
        from datetime import datetime, timedelta
        from sqlalchemy import delete
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        stmt = (
            delete(Notification)
            .where(
                and_(
                    Notification.created_at < cutoff_date,
                    Notification.status.in_([
                        NotificationStatus.READ,
                        NotificationStatus.CANCELLED
                    ])
                )
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def get_notifications_by_recipient(
        self, 
        *, 
        recipient_email: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """
        Récupère les notifications par email de destinataire
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.recipient_email == recipient_email)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_scheduled_notifications(self, *, limit: int = 100) -> List[Notification]:
        """
        Récupère les notifications planifiées
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.scheduled_at > datetime.now(),
                    Notification.status == NotificationStatus.PENDING
                )
            )
            .order_by(Notification.scheduled_at)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_expired_notifications(self, *, limit: int = 100) -> List[Notification]:
        """
        Récupère les notifications expirées
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.expires_at < datetime.now(),
                    Notification.status.in_([
                        NotificationStatus.PENDING,
                        NotificationStatus.SENT
                    ])
                )
            )
            .order_by(desc(Notification.expires_at))
            .limit(limit)
        )
        return result.scalars().all()
