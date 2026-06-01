"""
Sector Service - Urbain Sustainability System
Service métier pour la gestion des secteurs municipaux
"""

import structlog
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_

from app.services.base import BaseService
from app.models.sector import Sector, SectorType, SectorStatus
from app.models.signal import Signal, SignalStatus
from app.models.user import User
from app.schemas.sector import SectorCreate, SectorUpdate
from app.repositories import SectorRepository
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    BusinessLogicError, ConflictError
)

logger = structlog.get_logger()


class SectorService(BaseService[Sector, SectorCreate, SectorUpdate]):
    """
    Service métier pour la gestion des secteurs municipaux
    Gère l'assignation automatique, la capacité, et les performances
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = SectorRepository(db, Sector)

    async def _check_capacity(self, sector: Sector) -> Tuple[bool, int]:
        from app.models.signal import Signal

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        count_query = select(func.count(Signal.id)).where(
            and_(
                Signal.assigned_sector_id == sector.id,
                Signal.created_at >= today_start
            )
        )
        count_result = await self.db.execute(count_query)
        today_count = count_result.scalar() or 0

        return today_count < sector.max_daily_signals, today_count

    async def create_sector(self, obj_in: SectorCreate) -> Sector:
        try:
            code_exists = await self.repository.check_code_exists(code=obj_in.code)
            if code_exists:
                raise ConflictError(f"Sector code '{obj_in.code}' already exists")

            name_exists = await self.repository.check_name_exists(name=obj_in.name)
            if name_exists:
                raise ConflictError(f"Sector name '{obj_in.name}' already exists")

            try:
                st = SectorType(obj_in.sector_type)
            except ValueError:
                raise ValidationError(f"Invalid sector type: {obj_in.sector_type}")

            obj_data = obj_in.model_dump()
            obj_data["sector_type"] = st
            sector = Sector(**obj_data)
            sector.status = SectorStatus.ACTIVE

            self.db.add(sector)
            await self.db.commit()
            await self.db.refresh(sector)

            await self.log_operation("create_sector", {"sector_id": sector.id, "code": sector.code})
            return sector
        except (ConflictError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("create_sector", e)
            raise DatabaseError(f"Failed to create sector: {str(e)}")

    async def get_sector(self, sector_id: int) -> Sector:
        try:
            sector = await self.repository.get(id=sector_id)
            if not sector:
                raise NotFoundError(f"Sector with id {sector_id} not found")
            return sector
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_sector", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to get sector: {str(e)}")

    async def update_sector(self, sector_id: int, obj_in: SectorUpdate) -> Sector:
        try:
            sector = await self.get_sector(sector_id)
            update_data = obj_in.model_dump(exclude_unset=True)

            if "code" in update_data:
                code_exists = await self.repository.check_code_exists(
                    code=update_data["code"], exclude_id=sector_id
                )
                if code_exists:
                    raise ConflictError(f"Sector code '{update_data['code']}' already exists")

            if "name" in update_data:
                name_exists = await self.repository.check_name_exists(
                    name=update_data["name"], exclude_id=sector_id
                )
                if name_exists:
                    raise ConflictError(f"Sector name '{update_data['name']}' already exists")

            for field, value in update_data.items():
                if hasattr(sector, field):
                    setattr(sector, field, value)

            await self.db.commit()
            await self.db.refresh(sector)

            await self.log_operation("update_sector", {"sector_id": sector_id})
            return sector
        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            await self.log_error("update_sector", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to update sector: {str(e)}")

    async def delete_sector(self, sector_id: int) -> bool:
        try:
            sector = await self.get_sector(sector_id)

            from app.models.signal import Signal
            active_signals_query = select(func.count(Signal.id)).where(
                and_(
                    Signal.assigned_sector_id == sector_id,
                    Signal.status.in_([
                        SignalStatus.ASSIGNED, SignalStatus.IN_PROGRESS,
                        SignalStatus.UNDER_REVIEW, SignalStatus.SUBMITTED
                    ])
                )
            )
            active_result = await self.db.execute(active_signals_query)
            if active_result.scalar() > 0:
                raise BusinessLogicError(
                    "Cannot delete sector with active signals. Reassign signals first."
                )

            users_query = select(func.count(User.id)).where(User.sector_id == sector_id)
            users_result = await self.db.execute(users_query)
            if users_result.scalar() > 0:
                raise BusinessLogicError(
                    "Cannot delete sector with associated users. Reassign users first."
                )

            await self.repository.remove(id=sector_id)
            await self.log_operation("delete_sector", {"sector_id": sector_id})
            return True
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("delete_sector", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to delete sector: {str(e)}")

    async def get_sectors(self, skip: int = 0, limit: int = 100,
                           filters: Optional[Dict[str, Any]] = None) -> List[Sector]:
        try:
            return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)
        except Exception as e:
            await self.log_error("get_sectors", e)
            raise DatabaseError(f"Failed to get sectors: {str(e)}")

    async def get_sector_by_type(self, sector_type: str, skip: int = 0, limit: int = 100) -> List[Sector]:
        try:
            try:
                st = SectorType(sector_type)
            except ValueError:
                raise ValidationError(f"Invalid sector type: {sector_type}")
            return await self.repository.get_by_type(sector_type=st, skip=skip, limit=limit)
        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_sector_by_type", e, {"sector_type": sector_type})
            raise DatabaseError(f"Failed to get sector by type: {str(e)}")

    async def get_sector_stats(self, sector_id: int) -> Dict[str, Any]:
        try:
            sector = await self.get_sector(sector_id)
            stats = await self.repository.get_sector_statistics(sector_id=sector_id)

            has_capacity, today_count = await self._check_capacity(sector)
            stats["has_capacity"] = has_capacity
            stats["today_signal_count"] = today_count

            workload = await self.repository.get_sectors_workload(limit=100)
            for w in workload:
                if w["sector_id"] == sector_id:
                    stats["workload"] = w
                    break

            return stats
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_sector_stats", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to get sector stats: {str(e)}")

    async def assign_signal_to_sector(self, signal_id: int) -> Tuple[Optional[Sector], str]:
        try:
            from app.models.signal import Signal
            from app.models.category import Category

            signal_query = select(Signal).where(Signal.id == signal_id)
            signal_result = await self.db.execute(signal_query)
            signal = signal_result.scalar_one_or_none()

            if not signal:
                raise NotFoundError(f"Signal with id {signal_id} not found")

            category_query = select(Category).where(Category.id == signal.category_id)
            category_result = await self.db.execute(category_query)
            category = category_result.scalar_one_or_none()

            if category and not category.auto_assignment_enabled:
                return None, "Category does not allow auto-assignment"

            responsible_sector_ids = []
            if category and category.responsible_sectors:
                responsible_sector_ids = category.responsible_sectors

            if responsible_sector_ids:
                sectors_query = select(Sector).where(
                    and_(
                        Sector.id.in_(responsible_sector_ids),
                        Sector.status == SectorStatus.ACTIVE,
                        Sector.auto_assignment_enabled == True
                    )
                ).order_by(Sector.priority_level, Sector.avg_resolution_time_hours)
            else:
                sectors_query = select(Sector).where(
                    and_(
                        Sector.status == SectorStatus.ACTIVE,
                        Sector.auto_assignment_enabled == True
                    )
                ).order_by(Sector.priority_level, Sector.avg_resolution_time_hours)

            sectors_result = await self.db.execute(sectors_query)
            available_sectors = sectors_result.scalars().all()

            best_sector = None
            best_load = float('inf')

            for sector in available_sectors:
                if sector.can_handle_signal(signal.category_id):
                    has_capacity, today_count = await self._check_capacity(sector)

                    if not has_capacity and sector.priority_level > 2:
                        continue

                    if not has_capacity:
                        continue

                    if today_count < best_load:
                        best_load = today_count
                        best_sector = sector

            if best_sector:
                signal.assigned_sector_id = best_sector.id
                signal.status = SignalStatus.ASSIGNED
                signal.assigned_at = datetime.now(timezone.utc)
                await self.db.commit()

                await self.log_operation("assign_signal_to_sector", {
                    "signal_id": signal_id,
                    "sector_id": best_sector.id
                })
                return best_sector, f"Signal assigned to {best_sector.name}"

            return None, "No available sector found for automatic assignment"
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("assign_signal_to_sector", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to assign signal to sector: {str(e)}")

    async def get_available_sectors(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            if category_id:
                sectors = await self.repository.get_sectors_by_category_support(
                    category_id=category_id
                )
            else:
                result = await self.db.execute(
                    select(Sector).where(
                        and_(
                            Sector.status == SectorStatus.ACTIVE,
                            Sector.auto_assignment_enabled == True
                        )
                    ).order_by(Sector.priority_level, Sector.name)
                )
                sectors = result.scalars().all()

            available = []
            for sector in sectors:
                has_capacity, today_count = await self._check_capacity(sector)
                capacity_remaining = sector.max_daily_signals - today_count

                available.append({
                    "id": sector.id,
                    "name": sector.name,
                    "code": sector.code,
                    "sector_type": sector.sector_type.value,
                    "priority_level": sector.priority_level,
                    "avg_processing_time_hours": sector.avg_processing_time_hours,
                    "today_signals": today_count,
                    "max_daily_signals": sector.max_daily_signals,
                    "capacity_remaining": max(0, capacity_remaining),
                    "has_capacity": has_capacity,
                    "is_working_hours": sector.is_working_hours(datetime.now(timezone.utc)),
                    "city": sector.city,
                    "manager_name": sector.manager_name
                })

            available.sort(key=lambda x: (-x["has_capacity"], x["today_signals"], x["priority_level"]))
            return available
        except Exception as e:
            await self.log_error("get_available_sectors", e)
            raise DatabaseError(f"Failed to get available sectors: {str(e)}")

    async def get_sector_performance(self, sector_id: int, days: int = 30) -> Dict[str, Any]:
        try:
            sector = await self.get_sector(sector_id)
            performance = await self.repository.get_sector_performance(
                sector_id=sector_id, days=days
            )

            efficiency_score = 0
            if performance.get("resolution_rate", 0) > 0:
                resolution_rate = performance["resolution_rate"]
                escalation_rate = performance.get("escalation_rate", 0)
                efficiency_score = round(
                    (resolution_rate * 0.6) - (escalation_rate * 0.2) +
                    (max(0, 100 - (performance.get("avg_resolution_hours", 0) * 2)) * 0.2),
                    2
                )
                efficiency_score = max(0, min(100, efficiency_score))

            performance["sector_name"] = sector.name
            performance["sector_code"] = sector.code
            performance["sector_type"] = sector.sector_type.value
            performance["efficiency_score"] = efficiency_score
            performance["max_daily_signals"] = sector.max_daily_signals
            performance["priority_level"] = sector.priority_level

            return performance
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_sector_performance", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to get sector performance: {str(e)}")

    async def update_sector_metrics(self, sector_id: int) -> Sector:
        try:
            sector = await self.get_sector(sector_id)
            await self.repository.update_statistics(sector_id=sector_id)
            await self.db.refresh(sector)
            await self.log_operation("update_sector_metrics", {"sector_id": sector_id})
            return sector
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("update_sector_metrics", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to update sector metrics: {str(e)}")
