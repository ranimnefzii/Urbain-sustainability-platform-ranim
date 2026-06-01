"""
Admin Routes - Urbain Sustainability System
Routes d'administration et tableaux de bord
"""

from typing import Optional
from datetime import datetime
import enum
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from sqlalchemy import func, select

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.services.analytics_service import AnalyticsService
from app.services.signal_service import SignalService
from app.services.user_service import UserService
from app.services.sector_service import SectorService
from app.services.category_service import CategoryService
from app.services.ai_service import AIService
from app.models.user import User, UserStatus
from app.models.signal import Signal
from app.models.sector import Sector
from app.core.exceptions import DatabaseError, NotFoundError
from app.utils.helpers import Paginator

logger = structlog.get_logger()
router = APIRouter()


@router.get(
    "/dashboard",
    response_model=dict,
    summary="Main admin dashboard",
    description="Get the main administration dashboard data"
)
async def get_dashboard(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service = AnalyticsService(db)
        dashboard = await analytics_service.get_dashboard_stats()
        return {
            "success": True,
            "message": "Dashboard data retrieved",
            "data": dashboard
        }
    except Exception as e:
        logger.error("Get dashboard failed", error=str(e))
        raise DatabaseError("Failed to retrieve dashboard data")


@router.get(
    "/stats/overview",
    response_model=dict,
    summary="System overview stats",
    description="Get overall system statistics"
)
async def get_overview_stats(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_dashboard_stats()
        return {
            "success": True,
            "message": "Overview statistics retrieved",
            "data": stats
        }
    except Exception as e:
        logger.error("Get overview stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve overview statistics")


@router.get(
    "/stats/signals",
    response_model=dict,
    summary="Signal statistics",
    description="Get detailed signal statistics"
)
async def get_signal_stats(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        stats = await signal_service.get_signal_stats()
        return {
            "success": True,
            "message": "Signal statistics retrieved",
            "data": stats
        }
    except Exception as e:
        logger.error("Get signal stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve signal statistics")


@router.get(
    "/stats/users",
    response_model=dict,
    summary="User statistics",
    description="Get user registration and activity statistics"
)
async def get_user_stats(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        total_users = await db.execute(select(func.count(User.id)))
        active_users = await db.execute(select(func.count(User.id)).where(User.status == UserStatus.ACTIVE))
        stats = {
            "total_users": total_users.scalar() or 0,
            "active_users": active_users.scalar() or 0
        }
        return {
            "success": True,
            "message": "User statistics retrieved",
            "data": stats
        }
    except Exception as e:
        logger.error("Get user stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve user statistics")


@router.get(
    "/stats/sectors",
    response_model=dict,
    summary="Sector performance",
    description="Get sector performance metrics"
)
async def get_sector_performance(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service = AnalyticsService(db)
        performance = await analytics_service.get_sector_performance()
        return {
            "success": True,
            "message": "Sector performance retrieved",
            "data": performance
        }
    except Exception as e:
        logger.error("Get sector performance failed", error=str(e))
        raise DatabaseError("Failed to retrieve sector performance")


@router.get(
    "/stats/categories",
    response_model=dict,
    summary="Category breakdown",
    description="Get category usage and performance breakdown"
)
async def get_category_breakdown(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service = AnalyticsService(db)
        breakdown = await analytics_service.get_category_breakdown()
        return {
            "success": True,
            "message": "Category breakdown retrieved",
            "data": breakdown
        }
    except Exception as e:
        logger.error("Get category breakdown failed", error=str(e))
        raise DatabaseError("Failed to retrieve category breakdown")


@router.get(
    "/stats/response-times",
    response_model=dict,
    summary="Response time analytics",
    description="Get signal response and resolution time analytics"
)
async def get_response_time_analytics(
    days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_response_times(period=f"{days}d")
        return {
            "success": True,
            "message": "Response time analytics retrieved",
            "data": analytics
        }
    except Exception as e:
        logger.error("Get response time analytics failed", error=str(e))
        raise DatabaseError("Failed to retrieve response time analytics")


@router.get(
    "/stats/predictions",
    response_model=dict,
    summary="AI predictions overview",
    description="Get AI prediction metrics and accuracy overview"
)
async def get_prediction_overview(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        ai_service = AIService(db)
        predictions = await ai_service.predict_trends(days=30)
        return {
            "success": True,
            "message": "Prediction overview retrieved",
            "data": predictions
        }
    except Exception as e:
        logger.error("Get prediction overview failed", error=str(e))
        raise DatabaseError("Failed to retrieve prediction overview")


@router.get(
    "/audit-log",
    response_model=dict,
    summary="System audit log",
    description="Get paginated system audit log entries"
)
async def get_audit_log(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Page size"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        analytics_service = AnalyticsService(db)
        filters = {}
        if action:
            filters["action"] = action
        if entity_type:
            filters["entity_type"] = entity_type
        if user_id:
            filters["user_id"] = user_id
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        from app.models.audit_log import AuditLog
        logs_query = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(paginator.skip).limit(paginator.size)
        logs_result = await db.execute(logs_query)
        logs = logs_result.scalars().all()
        serialized = []
        for log in logs:
            entry = {c.name: getattr(log, c.name) for c in log.__table__.columns}
            for k, v in entry.items():
                if isinstance(v, enum.Enum):
                    entry[k] = v.value
                elif isinstance(v, datetime):
                    entry[k] = v.isoformat() if v else None
            serialized.append(entry)
        return {
            "success": True,
            "message": "Audit log retrieved",
            "data": {
                "items": serialized,
                **paginator.get_metadata(len(logs))
            }
        }
    except Exception as e:
        logger.error("Get audit log failed", error=str(e))
        raise DatabaseError("Failed to retrieve audit log")


@router.get(
    "/health",
    response_model=dict,
    summary="Detailed system health check",
    description="Get detailed health status of all system components"
)
async def get_system_health(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_service = AnalyticsService(db)
        db_status = "healthy"
        try:
            await db.execute(select(func.count(Signal.id)).limit(1))
        except Exception:
            db_status = "degraded"
        health = {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0"
        }
        return {
            "success": True,
            "message": "System health status retrieved",
            "data": health
        }
    except Exception as e:
        logger.error("Get system health failed", error=str(e))
        raise DatabaseError("Failed to retrieve system health status")


@router.get(
    "/system/config",
    response_model=dict,
    summary="Get system configuration",
    description="Get current system configuration (admin only)"
)
async def get_system_config(
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.core.config import settings
        config = {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
            "ai_confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
            "max_file_size": settings.MAX_FILE_SIZE,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "allowed_origins": settings.ALLOWED_ORIGINS
        }
        return {
            "success": True,
            "message": "System configuration retrieved",
            "data": config
        }
    except Exception as e:
        logger.error("Get system config failed", error=str(e))
        raise DatabaseError("Failed to retrieve system configuration")
