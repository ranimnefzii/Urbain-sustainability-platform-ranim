"""
Analytics Service - Urbain Sustainability System
Service d'analyse et de reporting avec agrégation de données complexes
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple

import structlog
from sqlalchemy import select, func, and_, case, extract, text

from app.core.exceptions import (
    DatabaseError,
    ValidationError,
    BusinessLogicError
)
from app.core.config import settings
from app.repositories.signal_repository import SignalRepository
from app.repositories.user_repository import UserRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.priority_repository import PriorityRepository
from app.repositories.sector_repository import SectorRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.notification_repository import NotificationRepository
from app.models.signal import Signal, SignalStatus
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category, CategoryType
from app.models.priority import Priority, PriorityLevel
from app.models.sector import Sector, SectorType
from app.models.report import Report, ReportType
from app.models.notification import Notification, NotificationChannel
from app.services.base import BaseService

logger = structlog.get_logger()


class AnalyticsService(BaseService):
    """
    Service d'analytics avancé avec agrégation multi-repository
    Analyse des tendances, performances, hotspots et métriques
    """

    def __init__(self, db):
        super().__init__(db)
        self.signal_repo = SignalRepository(db, Signal)
        self.user_repo = UserRepository(db, User)
        self.category_repo = CategoryRepository(db, Category)
        self.priority_repo = PriorityRepository(db, Priority)
        self.sector_repo = SectorRepository(db, Sector)
        self.report_repo = ReportRepository(db, Report)
        self.notification_repo = NotificationRepository(db, Notification)

    async def _get_date_range(
        self,
        period: str = "month",
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None
    ) -> Tuple[datetime, datetime]:
        now = datetime.now(timezone.utc)
        if custom_start and custom_end:
            return custom_start, custom_end

        if period.endswith("d") and period[:-1].isdigit():
            return now - timedelta(days=int(period[:-1])), now
        periods = {
            "day": timedelta(days=1),
            "week": timedelta(weeks=1),
            "month": timedelta(days=30),
            "quarter": timedelta(days=90),
            "year": timedelta(days=365)
        }
        delta = periods.get(period, timedelta(days=30))
        return now - delta, now

    async def get_dashboard_stats(
        self,
        period: str = "month",
        sector_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            total_signals = await self.signal_repo.count()
            total_users = await self.user_repo.count()
            total_categories = await self.category_repo.count()
            total_sectors = await self.sector_repo.count()

            period_signals = await self.signal_repo.count(
                filters={"created_at": start_date} if False else None
            )
            period_signals_count = 0
            period_signals_result = await self.db.execute(
                select(func.count(Signal.id)).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                )
            )
            period_signals_count = period_signals_result.scalar() or 0

            resolved_count = 0
            resolved_result = await self.db.execute(
                select(func.count(Signal.id)).where(
                    and_(
                        Signal.status.in_([SignalStatus.RESOLVED, SignalStatus.CLOSED]),
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                )
            )
            resolved_count = resolved_result.scalar() or 0

            avg_resolution = None
            avg_result = await self.db.execute(
                select(func.avg(
                    func.extract("epoch", Signal.resolved_at) -
                    func.extract("epoch", Signal.created_at)
                )).where(
                    and_(
                        Signal.resolved_at.isnot(None),
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                )
            )
            avg_seconds = avg_result.scalar()
            if avg_seconds:
                avg_resolution = round(avg_seconds / 3600, 2)

            satisfaction_avg = None
            sat_result = await self.db.execute(
                select(func.avg(Signal.citizen_satisfaction)).where(
                    and_(
                        Signal.citizen_satisfaction.isnot(None),
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                )
            )
            sat_val = sat_result.scalar()
            if sat_val:
                satisfaction_avg = round(float(sat_val), 2)

            signals_by_day = {}
            day_result = await self.db.execute(
                select(
                    func.date(Signal.created_at).label("day"),
                    func.count(Signal.id).label("count")
                ).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                ).group_by(text("day")).order_by(text("day"))
            )
            for row in day_result:
                signals_by_day[str(row.day)] = row.count

            # ------- Flat fields expected by the admin dashboard UI -------
            active_users_result = await self.db.execute(
                select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
            )
            active_users = active_users_result.scalar() or 0

            terminal_statuses = [SignalStatus.RESOLVED, SignalStatus.CLOSED]
            resolved_all_result = await self.db.execute(
                select(func.count(Signal.id)).where(Signal.status.in_(terminal_statuses))
            )
            resolved_signals = resolved_all_result.scalar() or 0

            open_all_result = await self.db.execute(
                select(func.count(Signal.id)).where(
                    Signal.status.notin_(terminal_statuses + [
                        SignalStatus.CANCELLED, SignalStatus.REJECTED, SignalStatus.DRAFT
                    ])
                )
            )
            open_signals = open_all_result.scalar() or 0

            avg_all_result = await self.db.execute(
                select(func.avg(
                    func.extract("epoch", Signal.resolved_at) -
                    func.extract("epoch", Signal.created_at)
                )).where(Signal.resolved_at.isnot(None))
            )
            avg_all_seconds = avg_all_result.scalar()
            avg_resolution_all = round(float(avg_all_seconds) / 3600, 2) if avg_all_seconds else 0

            sat_all_result = await self.db.execute(
                select(func.avg(Signal.citizen_satisfaction)).where(Signal.citizen_satisfaction.isnot(None))
            )
            sat_all_value = sat_all_result.scalar()
            citizen_satisfaction_all = round(float(sat_all_value), 2) if sat_all_value else 0

            signals_by_status: Dict[str, int] = {}
            status_all_result = await self.db.execute(
                select(Signal.status, func.count(Signal.id)).group_by(Signal.status)
            )
            for row in status_all_result:
                signals_by_status[row[0].name] = row[1]

            signals_by_category: Dict[str, int] = {}
            top_categories: List[Dict[str, Any]] = []
            category_all_result = await self.db.execute(
                select(Category.id, Category.name, func.count(Signal.id).label("count"))
                .join(Category, Category.id == Signal.category_id)
                .group_by(Category.id, Category.name)
                .order_by(func.count(Signal.id).desc())
            )
            for row in category_all_result:
                signals_by_category[row.name] = row.count
                top_categories.append({"id": row.id, "name": row.name, "count": row.count})

            signals_by_priority: Dict[str, int] = {}
            priority_all_result = await self.db.execute(
                select(Priority.priority_level, func.count(Signal.id))
                .join(Priority, Priority.id == Signal.priority_id)
                .group_by(Priority.priority_level)
            )
            for row in priority_all_result:
                signals_by_priority[row[0].name] = row[1]

            sector_performance: List[Dict[str, Any]] = []
            sector_perf_result = await self.db.execute(
                select(
                    Sector.id,
                    Sector.name,
                    func.count(Signal.id).label("total"),
                    func.sum(case((Signal.status == SignalStatus.RESOLVED, 1), else_=0)).label("resolved"),
                    func.avg(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("avg_time")
                )
                .select_from(Sector)
                .outerjoin(Signal, Signal.assigned_sector_id == Sector.id)
                .group_by(Sector.id, Sector.name)
            )
            for row in sector_perf_result:
                sector_performance.append({
                    "sector_id": row.id,
                    "sector_name": row.name,
                    "resolved": int(row.resolved or 0),
                    "avg_time": round(float(row.avg_time) / 3600, 2) if row.avg_time else 0
                })

            recent_signals: List[Dict[str, Any]] = []
            recent_result = await self.db.execute(
                select(Signal).order_by(Signal.created_at.desc()).limit(6)
            )
            for s in recent_result.scalars().all():
                recent_signals.append({
                    "id": s.id,
                    "title": s.title,
                    "reference_number": s.reference_number,
                    "status": s.status.name,
                    "category_id": s.category_id,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                })

            stats = {
                "overview": {
                    "total_signals": total_signals,
                    "total_users": total_users,
                    "total_categories": total_categories,
                    "total_sectors": total_sectors
                },
                "period_stats": {
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "new_signals": period_signals_count,
                    "resolved_signals": resolved_count,
                    "resolution_rate": round((resolved_count / max(period_signals_count, 1)) * 100, 2),
                    "avg_resolution_time_hours": avg_resolution,
                    "citizen_satisfaction_avg": satisfaction_avg
                },
                "daily_trend": signals_by_day,
                "filters_applied": {
                    "sector_id": sector_id
                },
                # Flat dashboard fields
                "total_signals": total_signals,
                "total_users": total_users,
                "total_categories": total_categories,
                "total_sectors": total_sectors,
                "active_users": active_users,
                "resolved_signals": resolved_signals,
                "open_signals": open_signals,
                "avg_resolution_time_hours": avg_resolution_all,
                "citizen_satisfaction_rate": citizen_satisfaction_all,
                "signals_by_status": signals_by_status,
                "signals_by_category": signals_by_category,
                "signals_by_priority": signals_by_priority,
                "sector_performance": sector_performance,
                "top_categories": top_categories,
                "recent_signals": recent_signals,
                "recent_activity": []
            }

            if sector_id:
                sector_signals = await self.signal_repo.count(
                    filters={"assigned_sector_id": sector_id}
                )
                stats["overview"]["sector_signals"] = sector_signals

            await self.log_operation("get_dashboard_stats", {
                "period": period,
                "sector_id": sector_id
            })

            return stats

        except Exception as e:
            await self.log_error("get_dashboard_stats", e)
            raise DatabaseError("Failed to retrieve dashboard statistics")

    async def get_signal_trends(
        self,
        period: str = "month",
        granularity: str = "day",
        category_id: Optional[int] = None,
        sector_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            group_expr = func.date(Signal.created_at)
            if granularity == "week":
                group_expr = func.date_trunc("week", Signal.created_at)
            elif granularity == "month":
                group_expr = func.date_trunc("month", Signal.created_at)

            conditions = [
                Signal.created_at >= start_date,
                Signal.created_at <= end_date
            ]
            if category_id:
                conditions.append(Signal.category_id == category_id)
            if sector_id:
                conditions.append(Signal.assigned_sector_id == sector_id)

            trend_result = await self.db.execute(
                select(
                    group_expr.label("period"),
                    func.count(Signal.id).label("total"),
                    func.sum(case((Signal.status == SignalStatus.RESOLVED, 1), else_=0)).label("resolved"),
                    func.sum(case((Signal.status == SignalStatus.SUBMITTED, 1), else_=0)).label("submitted"),
                    func.sum(case((Signal.status == SignalStatus.IN_PROGRESS, 1), else_=0)).label("in_progress"),
                    func.avg(Signal.ai_priority_score).label("avg_priority")
                ).where(and_(*conditions))
                .group_by(text("period"))
                .order_by(text("period"))
            )

            trends = []
            for row in trend_result:
                trends.append({
                    "period": str(row.period),
                    "total": row.total,
                    "resolved": row.resolved or 0,
                    "submitted": row.submitted or 0,
                    "in_progress": row.in_progress or 0,
                    "avg_priority": round(float(row.avg_priority), 2) if row.avg_priority else 0
                })

            total_trend = sum(t["total"] for t in trends)
            prev_start = start_date - (end_date - start_date)
            prev_result = await self.db.execute(
                select(func.count(Signal.id))
                .where(
                    and_(
                        Signal.created_at >= prev_start,
                        Signal.created_at < start_date
                    )
                )
            )
            prev_count = prev_result.scalar() or 0
            change_pct = round(((total_trend - prev_count) / max(prev_count, 1)) * 100, 2)

            result = {
                "period": period,
                "granularity": granularity,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_signals": total_trend,
                "previous_period_signals": prev_count,
                "change_percentage": change_pct,
                "trend_direction": "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable",
                "trends": trends,
                "filters": {
                    "category_id": category_id,
                    "sector_id": sector_id
                }
            }

            return result

        except Exception as e:
            await self.log_error("get_signal_trends", e)
            raise DatabaseError("Failed to retrieve signal trends")

    async def get_sector_performance(
        self,
        period: str = "month",
        sector_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            conditions = [
                Signal.created_at >= start_date,
                Signal.created_at <= end_date
            ]
            if sector_id:
                conditions.append(Signal.assigned_sector_id == sector_id)

            sector_perf = {}
            sectors_query = select(Sector)
            if sector_id:
                sectors_query = sectors_query.where(Sector.id == sector_id)
            sectors = await self.db.execute(sectors_query)
            sectors_list = sectors.scalars().all()

            for sector in sectors_list:
                sig_conditions = conditions + [Signal.assigned_sector_id == sector.id]
                stats = await self.db.execute(
                    select(
                        func.count(Signal.id).label("total"),
                        func.sum(case((Signal.status == SignalStatus.RESOLVED, 1), else_=0)).label("resolved"),
                        func.sum(case((Signal.status.in_([SignalStatus.ASSIGNED, SignalStatus.IN_PROGRESS]), 1), else_=0)).label("active"),
                        func.avg(
                            func.extract("epoch", Signal.resolved_at) -
                            func.extract("epoch", Signal.created_at)
                        ).label("avg_time"),
                        func.avg(Signal.citizen_satisfaction).label("avg_satisfaction")
                    ).where(and_(*sig_conditions))
                )
                row = stats.first()

                total = row.total or 0
                resolved = row.resolved or 0
                active = row.active or 0
                avg_time = float(row.avg_time) / 3600 if row.avg_time else 0
                satisfaction = float(row.avg_satisfaction) if row.avg_satisfaction else 0

                resolution_rate = round((resolved / max(total, 1)) * 100, 2)
                workload_pct = round((active / max(sector.max_daily_signals, 1)) * 100, 2)
                efficiency = round(
                    (resolution_rate * 0.4) +
                    (satisfaction * 20 * 0.3) +
                    (max(0, 100 - avg_time) * 0.3),
                    2
                )

                sector_perf[sector.id] = {
                    "sector_id": sector.id,
                    "sector_name": sector.name,
                    "sector_type": sector.sector_type.value,
                    "total_signals": total,
                    "resolved_signals": resolved,
                    "active_signals": active,
                    "resolution_rate": resolution_rate,
                    "avg_resolution_time_hours": round(avg_time, 2),
                    "citizen_satisfaction": round(satisfaction, 2),
                    "workload_percentage": workload_pct,
                    "efficiency_score": efficiency,
                    "performance_level": "high" if efficiency >= 70 else "medium" if efficiency >= 40 else "low"
                }

            sorted_perf = sorted(
                sector_perf.values(),
                key=lambda x: x["efficiency_score"],
                reverse=True
            )

            avg_efficiency = round(
                sum(s["efficiency_score"] for s in sorted_perf) / max(len(sorted_perf), 1),
                2
            )

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_sectors": len(sorted_perf),
                "average_efficiency_score": avg_efficiency,
                "highest_performer": sorted_perf[0] if sorted_perf else None,
                "lowest_performer": sorted_perf[-1] if sorted_perf else None,
                "sectors": sorted_perf
            }

            return result

        except Exception as e:
            await self.log_error("get_sector_performance", e)
            raise DatabaseError("Failed to retrieve sector performance")

    async def get_category_breakdown(
        self,
        period: str = "month"
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            breakdown = await self.db.execute(
                select(
                    Category.id,
                    Category.name,
                    Category.code,
                    Category.category_type,
                    func.count(Signal.id).label("total"),
                    func.sum(case((Signal.status == SignalStatus.RESOLVED, 1), else_=0)).label("resolved"),
                    func.sum(case((Signal.status == SignalStatus.SUBMITTED, 1), else_=0)).label("pending"),
                    func.avg(Signal.ai_priority_score).label("avg_priority"),
                    func.avg(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("avg_resolution_time"),
                    func.avg(Signal.citizen_satisfaction).label("avg_satisfaction")
                ).outerjoin(Signal, and_(
                    Category.id == Signal.category_id,
                    Signal.created_at >= start_date,
                    Signal.created_at <= end_date
                )).group_by(Category.id, Category.name, Category.code, Category.category_type)
                .order_by(func.count(Signal.id).desc())
            )

            categories = []
            total_signals = 0
            for row in breakdown:
                total = row.total or 0
                total_signals += total
                avg_time = float(row.avg_resolution_time) / 3600 if row.avg_resolution_time else 0
                categories.append({
                    "category_id": row.id,
                    "name": row.name,
                    "code": row.code,
                    "type": row.category_type.value,
                    "total_signals": total,
                    "resolved_signals": row.resolved or 0,
                    "pending_signals": row.pending or 0,
                    "resolution_rate": round((row.resolved or 0) / max(total, 1) * 100, 2),
                    "avg_priority_score": round(float(row.avg_priority), 2) if row.avg_priority else 0,
                    "avg_resolution_time_hours": round(avg_time, 2),
                    "avg_satisfaction": round(float(row.avg_satisfaction), 2) if row.avg_satisfaction else 0
                })

            type_breakdown = {}
            for cat in categories:
                cat_type = cat["type"]
                if cat_type not in type_breakdown:
                    type_breakdown[cat_type] = {
                        "type": cat_type,
                        "total": 0,
                        "categories": []
                    }
                type_breakdown[cat_type]["total"] += cat["total_signals"]
                type_breakdown[cat_type]["categories"].append(cat)

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_signals": total_signals,
                "total_categories": len(categories),
                "type_breakdown": list(type_breakdown.values()),
                "categories": categories,
                "most_popular_category": categories[0] if categories else None,
                "best_performing_category": max(categories, key=lambda c: c["resolution_rate"]) if categories else None
            }

            return result

        except Exception as e:
            await self.log_error("get_category_breakdown", e)
            raise DatabaseError("Failed to retrieve category breakdown")

    async def get_citizen_satisfaction(
        self,
        period: str = "month",
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            conditions = [
                Signal.citizen_satisfaction.isnot(None),
                Signal.created_at >= start_date,
                Signal.created_at <= end_date
            ]
            if category_id:
                conditions.append(Signal.category_id == category_id)

            stats = await self.db.execute(
                select(
                    func.avg(Signal.citizen_satisfaction).label("avg_satisfaction"),
                    func.count(Signal.id).label("total_feedback"),
                    func.sum(case((Signal.citizen_satisfaction >= 4, 1), else_=0)).label("satisfied"),
                    func.sum(case((Signal.citizen_satisfaction == 3, 1), else_=0)).label("neutral"),
                    func.sum(case((Signal.citizen_satisfaction <= 2, 1), else_=0)).label("dissatisfied")
                ).where(and_(*conditions))
            )
            row = stats.first()

            total = row.total_feedback or 0
            avg_sat = float(row.avg_satisfaction) if row.avg_satisfaction else 0
            satisfied = row.satisfied or 0
            neutral = row.neutral or 0
            dissatisfied = row.dissatisfied or 0

            satisfaction_dist = {}
            dist_result = await self.db.execute(
                select(
                    Signal.citizen_satisfaction,
                    func.count(Signal.id).label("count")
                ).where(and_(*conditions))
                .group_by(Signal.citizen_satisfaction)
                .order_by(Signal.citizen_satisfaction)
            )
            for dist_row in dist_result:
                satisfaction_dist[f"rating_{dist_row.citizen_satisfaction}"] = dist_row.count

            monthly_trend = {}
            trend_result = await self.db.execute(
                select(
                    func.date_trunc("month", Signal.created_at).label("month"),
                    func.avg(Signal.citizen_satisfaction).label("avg_rating"),
                    func.count(Signal.id).label("count")
                ).where(and_(*conditions))
                .group_by(text("month"))
                .order_by(text("month"))
            )
            for trend_row in trend_result:
                monthly_trend[str(trend_row.month)] = {
                    "avg_rating": round(float(trend_row.avg_rating), 2) if trend_row.avg_rating else 0,
                    "count": trend_row.count
                }

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "average_satisfaction": round(avg_sat, 2),
                "total_feedback": total,
                "satisfaction_rate": round((satisfied / max(total, 1)) * 100, 2),
                "distribution": {
                    "satisfied": satisfied,
                    "neutral": neutral,
                    "dissatisfied": dissatisfied,
                    "detailed": satisfaction_dist
                },
                "monthly_trend": monthly_trend,
                "filters": {"category_id": category_id}
            }

            return result

        except Exception as e:
            await self.log_error("get_citizen_satisfaction", e)
            raise DatabaseError("Failed to retrieve citizen satisfaction")

    async def get_response_times(
        self,
        period: str = "month",
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            conditions = [
                Signal.resolved_at.isnot(None),
                Signal.created_at >= start_date,
                Signal.created_at <= end_date
            ]
            if category_id:
                conditions.append(Signal.category_id == category_id)

            stats = await self.db.execute(
                select(
                    func.avg(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("avg_total_time"),
                    func.avg(
                        func.extract("epoch", Signal.started_processing_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("avg_response_time"),
                    func.avg(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.started_processing_at)
                    ).label("avg_processing_time"),
                    func.min(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("min_time"),
                    func.max(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("max_time"),
                    func.count(Signal.id).label("total_resolved")
                ).where(and_(*conditions))
            )
            row = stats.first()

            def seconds_to_hours(seconds):
                return round(float(seconds) / 3600, 2) if seconds else 0

            priority_breakdown = {}
            pb_result = await self.db.execute(
                select(
                    Priority.id,
                    Priority.name,
                    func.avg(
                        func.extract("epoch", Signal.resolved_at) -
                        func.extract("epoch", Signal.created_at)
                    ).label("avg_time"),
                    func.count(Signal.id).label("count")
                ).join(Signal, Signal.priority_id == Priority.id)
                .where(and_(
                    Signal.resolved_at.isnot(None),
                    Signal.created_at >= start_date,
                    Signal.created_at <= end_date
                ))
                .group_by(Priority.id, Priority.name)
            )
            for pb_row in pb_result:
                priority_breakdown[pb_row.name] = {
                    "avg_resolution_hours": seconds_to_hours(pb_row.avg_time),
                    "count": pb_row.count
                }

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_resolved_signals": row.total_resolved or 0,
                "average_total_time_hours": seconds_to_hours(row.avg_total_time),
                "average_response_time_hours": seconds_to_hours(row.avg_response_time),
                "average_processing_time_hours": seconds_to_hours(row.avg_processing_time),
                "min_resolution_time_hours": seconds_to_hours(row.min_time),
                "max_resolution_time_hours": seconds_to_hours(row.max_time),
                "priority_breakdown": priority_breakdown,
                "filters": {"category_id": category_id}
            }

            return result

        except Exception as e:
            await self.log_error("get_response_times", e)
            raise DatabaseError("Failed to retrieve response times")

    async def get_prediction_metrics(
        self,
        period: str = "month"
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            total_stats = await self.db.execute(
                select(
                    func.count(Signal.id).label("total"),
                    func.count(case((Signal.ai_confidence_score.isnot(None), 1))).label("with_ai"),
                    func.avg(Signal.ai_confidence_score).label("avg_confidence"),
                    func.avg(Signal.ai_priority_score).label("avg_priority"),
                    func.avg(Signal.ai_severity_score).label("avg_severity"),
                    func.avg(Signal.ai_urgency_score).label("avg_urgency")
                ).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                )
            )
            row = total_stats.first()

            accuracy_data = await self.db.execute(
                select(
                    func.count(Signal.id).label("total"),
                    func.sum(case((Signal.citizen_satisfaction >= 3, 1), else_=0)).label("accurate")
                ).where(
                    and_(
                        Signal.citizen_satisfaction.isnot(None),
                        Signal.ai_confidence_score.isnot(None),
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                )
            )
            acc_row = accuracy_data.first()
            accuracy = round(((acc_row.accurate or 0) / max(acc_row.total or 0, 1)) * 100, 2) if acc_row else 0

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_signals_analyzed": row.total or 0,
                "signals_with_ai": row.with_ai or 0,
                "ai_coverage_rate": round(((row.with_ai or 0) / max(row.total or 0, 1)) * 100, 2),
                "average_metrics": {
                    "confidence_score": round(float(row.avg_confidence), 4) if row.avg_confidence else 0,
                    "priority_score": round(float(row.avg_priority), 4) if row.avg_priority else 0,
                    "severity_score": round(float(row.avg_severity), 4) if row.avg_severity else 0,
                    "urgency_score": round(float(row.avg_urgency), 4) if row.avg_urgency else 0
                },
                "prediction_accuracy": accuracy,
                "model_version": "urbain-classifier-v1.0.0"
            }

            return result

        except Exception as e:
            await self.log_error("get_prediction_metrics", e)
            raise DatabaseError("Failed to retrieve prediction metrics")

    async def get_hotspot_data(
        self,
        period: str = "month",
        min_signals: int = 3
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            grid_size = 0.01
            lat_grid = func.floor(Signal.latitude / grid_size) * grid_size
            lng_grid = func.floor(Signal.longitude / grid_size) * grid_size

            hotspots_query = await self.db.execute(
                select(
                    lat_grid.label("lat_grid"),
                    lng_grid.label("lng_grid"),
                    func.count(Signal.id).label("signal_count"),
                    func.avg(Signal.ai_priority_score).label("avg_priority"),
                    func.avg(Signal.ai_severity_score).label("avg_severity"),
                    func.max(Signal.safety_risk_level).label("max_risk"),
                    func.count(case((Signal.status == SignalStatus.RESOLVED, 1))).label("resolved_count")
                ).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                ).group_by(
                    text("lat_grid"),
                    text("lng_grid")
                ).having(
                    func.count(Signal.id) >= min_signals
                ).order_by(
                    func.count(Signal.id).desc()
                ).limit(50)
            )

            hotspots = []
            for row in hotspots_query:
                intensity = "high" if row.signal_count >= 10 else "medium" if row.signal_count >= 5 else "low"
                hotspots.append({
                    "latitude": float(row.lat_grid) + grid_size / 2,
                    "longitude": float(row.lng_grid) + grid_size / 2,
                    "signal_count": row.signal_count,
                    "avg_priority": round(float(row.avg_priority), 2) if row.avg_priority else 0,
                    "avg_severity": round(float(row.avg_severity), 2) if row.avg_severity else 0,
                    "max_risk_level": row.max_risk or 0,
                    "resolution_rate": round((row.resolved_count / max(row.signal_count, 1)) * 100, 2),
                    "intensity": intensity
                })

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "grid_size": grid_size,
                "min_signals_threshold": min_signals,
                "total_hotspots": len(hotspots),
                "hotspots": hotspots,
                "high_intensity_count": sum(1 for h in hotspots if h["intensity"] == "high"),
                "medium_intensity_count": sum(1 for h in hotspots if h["intensity"] == "medium"),
                "low_intensity_count": sum(1 for h in hotspots if h["intensity"] == "low")
            }

            return result

        except Exception as e:
            await self.log_error("get_hotspot_data", e)
            raise DatabaseError("Failed to retrieve hotspot data")

    async def get_temporal_patterns(
        self,
        period: str = "month"
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            hourly = await self.db.execute(
                select(
                    func.extract("hour", Signal.created_at).label("hour"),
                    func.count(Signal.id).label("count")
                ).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                ).group_by(text("hour"))
                .order_by(text("hour"))
            )
            hourly_pattern = {}
            for row in hourly:
                hourly_pattern[int(row.hour)] = row.count

            daily = await self.db.execute(
                select(
                    func.extract("dow", Signal.created_at).label("day_of_week"),
                    func.count(Signal.id).label("count")
                ).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                ).group_by(text("day_of_week"))
                .order_by(text("day_of_week"))
            )
            daily_pattern = {}
            day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            for row in daily:
                idx = int(row.day_of_week)
                daily_pattern[day_names[idx] if idx < 7 else str(idx)] = row.count

            monthly = await self.db.execute(
                select(
                    func.date_trunc("month", Signal.created_at).label("month"),
                    func.count(Signal.id).label("count"),
                    func.avg(Signal.ai_priority_score).label("avg_priority")
                ).where(
                    and_(
                        Signal.created_at >= start_date,
                        Signal.created_at <= end_date
                    )
                ).group_by(text("month"))
                .order_by(text("month"))
            )
            monthly_pattern = []
            for row in monthly:
                monthly_pattern.append({
                    "month": str(row.month),
                    "count": row.count,
                    "avg_priority": round(float(row.avg_priority), 2) if row.avg_priority else 0
                })

            peak_hour = max(hourly_pattern, key=hourly_pattern.get) if hourly_pattern else None
            peak_day = max(daily_pattern, key=daily_pattern.get) if daily_pattern else None

            result = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "hourly_pattern": hourly_pattern,
                "daily_pattern": daily_pattern,
                "monthly_trend": monthly_pattern,
                "peak_hour": {"hour": peak_hour, "count": hourly_pattern.get(peak_hour, 0)} if peak_hour else None,
                "peak_day": {"day": peak_day, "count": daily_pattern.get(peak_day, 0)} if peak_day else None,
                "busiest_time": "morning" if peak_hour and 6 <= peak_hour <= 12 else
                               "afternoon" if peak_hour and 12 < peak_hour <= 18 else "night"
            }

            return result

        except Exception as e:
            await self.log_error("get_temporal_patterns", e)
            raise DatabaseError("Failed to retrieve temporal patterns")

    async def generate_summary_report(
        self,
        period: str = "month",
        title: Optional[str] = None,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        try:
            start_date, end_date = await self._get_date_range(period)

            default_sections = ["overview", "trends", "sectors", "categories", "satisfaction", "hotspots", "predictions"]
            sections = include_sections or default_sections

            report_data = {
                "title": title or f"Urbain Sustainability Report - {period.title()}",
                "period": period,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "sections": {}
            }

            if "overview" in sections:
                dashboard = await self.get_dashboard_stats(period)
                report_data["sections"]["overview"] = dashboard.get("overview", {})
                report_data["sections"]["overview"]["period_stats"] = dashboard.get("period_stats", {})

            if "trends" in sections:
                trends = await self.get_signal_trends(period)
                report_data["sections"]["trends"] = {
                    "total_signals": trends.get("total_signals"),
                    "change_percentage": trends.get("change_percentage"),
                    "trend_direction": trends.get("trend_direction"),
                    "daily_breakdown": trends.get("trends", [])
                }

            if "sectors" in sections:
                sectors = await self.get_sector_performance(period)
                report_data["sections"]["sectors"] = {
                    "total_sectors": sectors.get("total_sectors"),
                    "average_efficiency": sectors.get("average_efficiency_score"),
                    "highest_performer": sectors.get("highest_performer"),
                    "lowest_performer": sectors.get("lowest_performer")
                }

            if "categories" in sections:
                cats = await self.get_category_breakdown(period)
                report_data["sections"]["categories"] = {
                    "total_categories": cats.get("total_categories"),
                    "total_signals": cats.get("total_signals"),
                    "type_breakdown": cats.get("type_breakdown", []),
                    "most_popular": cats.get("most_popular_category"),
                    "best_performing": cats.get("best_performing_category")
                }

            if "satisfaction" in sections:
                sat = await self.get_citizen_satisfaction(period)
                report_data["sections"]["citizen_satisfaction"] = {
                    "average": sat.get("average_satisfaction"),
                    "rate": sat.get("satisfaction_rate"),
                    "total_feedback": sat.get("total_feedback"),
                    "distribution": sat.get("distribution")
                }

            if "hotspots" in sections:
                hotspots = await self.get_hotspot_data(period)
                report_data["sections"]["hotspots"] = {
                    "total_hotspots": hotspots.get("total_hotspots"),
                    "high_intensity": hotspots.get("high_intensity_count"),
                    "hotspots": hotspots.get("hotspots", [])[:10]
                }

            if "predictions" in sections:
                pred = await self.get_prediction_metrics(period)
                report_data["sections"]["predictions"] = {
                    "ai_coverage": pred.get("ai_coverage_rate"),
                    "avg_confidence": pred.get("average_metrics", {}).get("confidence_score"),
                    "prediction_accuracy": pred.get("prediction_accuracy")
                }

            report_data["summary"] = self._generate_summary_text(report_data["sections"])

            await self.log_operation("generate_summary_report", {
                "period": period,
                "sections_count": len(sections)
            })

            return report_data

        except Exception as e:
            await self.log_error("generate_summary_report", e)
            raise DatabaseError("Failed to generate summary report")

    def _generate_summary_text(self, sections: Dict[str, Any]) -> str:
        summary_parts = []
        overview = sections.get("overview", {})
        if overview:
            total = overview.get("total_signals", 0)
            users = overview.get("total_users", 0)
            summary_parts.append(f"Total signals: {total:,}, Total users: {users:,}")

        trends = sections.get("trends", {})
        if trends:
            direction = trends.get("trend_direction", "stable")
            change = trends.get("change_percentage", 0)
            summary_parts.append(f"Trend: {direction} ({change:+.1f}%)")

        sat = sections.get("citizen_satisfaction", {})
        if sat:
            avg = sat.get("average", 0)
            rate = sat.get("rate", 0)
            summary_parts.append(f"Citizen satisfaction: {avg}/5 ({rate:.1f}%)")

        sectors_data = sections.get("sectors", {})
        if sectors_data:
            eff = sectors_data.get("average_efficiency", 0)
            summary_parts.append(f"Average sector efficiency: {eff:.1f}")

        predictions = sections.get("predictions", {})
        if predictions:
            acc = predictions.get("prediction_accuracy", 0)
            summary_parts.append(f"AI prediction accuracy: {acc:.1f}%")

        return " | ".join(summary_parts) if summary_parts else "Report summary not available"
