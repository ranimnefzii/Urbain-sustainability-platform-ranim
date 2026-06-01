import structlog
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, desc

from app.models.audit_log import AuditLog
from app.core.exceptions import DatabaseError

logger = structlog.get_logger()


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        severity: str = "info",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_id: Optional[str] = None,
        parent_type: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> AuditLog:
        try:
            entry = AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                resource_id=resource_id,
                parent_type=parent_type,
                parent_id=parent_id,
                user_id=user_id,
                old_values=old_values,
                new_values=new_values,
                log_metadata=metadata,
                severity=severity,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.add(entry)
            await self.db.commit()
            await self.db.refresh(entry)
            return entry
        except Exception as e:
            logger.error("Audit log write failed", error=str(e))

    async def log_state_change(
        self,
        entity_type: str,
        entity_id: int,
        from_state: str,
        to_state: str,
        user_id: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        return await self.log(
            action=f"{entity_type}.state_change",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_values={"status": from_state},
            new_values={"status": to_state},
            metadata=metadata,
            severity="warning" if to_state in ["cancelled", "rejected", "failed"] else "info",
        )

    async def log_entity_crud(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        user_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        return await self.log(
            action=f"{entity_type}.{action}",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
        )

    async def get_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[AuditLog]:
        try:
            query = select(AuditLog).order_by(desc(AuditLog.created_at))
            if entity_type:
                query = query.where(AuditLog.entity_type == entity_type)
            if entity_id:
                query = query.where(AuditLog.entity_id == entity_id)
            if action:
                query = query.where(AuditLog.action == action)
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            if start_date:
                query = query.where(AuditLog.created_at >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.where(AuditLog.created_at <= datetime.fromisoformat(end_date))
            if severity:
                query = query.where(AuditLog.severity == severity)
            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error("Audit log query failed", error=str(e))
            raise DatabaseError("Failed to query audit logs")

    async def count_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> int:
        try:
            query = select(func.count(AuditLog.id))
            if entity_type:
                query = query.where(AuditLog.entity_type == entity_type)
            if entity_id:
                query = query.where(AuditLog.entity_id == entity_id)
            if action:
                query = query.where(AuditLog.action == action)
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar() or 0
        except Exception as e:
            logger.error("Audit log count failed", error=str(e))
            return 0

    async def get_entity_history(self, entity_type: str, entity_id: int) -> List[AuditLog]:
        return await self.get_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=500,
        )

    async def get_recent_activity(self, user_id: int, limit: int = 20) -> List[AuditLog]:
        return await self.get_logs(user_id=user_id, limit=limit)
