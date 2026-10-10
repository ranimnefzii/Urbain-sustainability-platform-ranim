"""
Reports Routes - Urbain Sustainability System
Routes de gestion des rapports et analyses
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin, get_current_sector_user
from app.schemas.report import (
    ReportCreate, ReportUpdate, ReportResponse, ReportList,
    ReportAnalytics, ReportSummary
)
from app.services.report_service import ReportService
from app.services.signal_service import SignalService
from app.services.sector_service import SectorService
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService
from app.core.exceptions import (
    NotFoundError, ValidationError, AuthorizationError,
    DatabaseError, BusinessLogicError
)
from app.utils.helpers import Paginator

logger = structlog.get_logger()
router = APIRouter()


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create report",
    description="Create a new report (admin/sector only)"
)
async def create_report(
    data: ReportCreate,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        result = await report_service.create_report(obj_in=data)
        return {
            "success": True,
            "message": f"Report '{result.title}' created successfully",
            "data": _serialize_report(result)
        }
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Create report failed", error=str(e))
        raise ValidationError("Failed to create report")


def _serialize_report(report) -> Dict[str, Any]:
    cols = [
        "id", "title", "description", "report_code", "signal_id", "generated_by",
        "sector_id", "report_type", "status", "frequency", "start_date", "end_date",
        "analysis_period_hours", "ai_model_version", "ai_confidence_score",
        "ai_processing_time_ms", "ai_parameters", "summary", "key_findings",
        "recommendations", "insights", "total_signals_analyzed",
        "critical_signals_count", "high_priority_count", "avg_resolution_time_hours",
        "citizen_satisfaction_rate", "category_breakdown", "priority_breakdown",
        "sector_performance", "geographic_hotspots", "temporal_patterns",
        "predicted_signals_next_period", "trend_analysis", "seasonal_patterns",
        "anomaly_detection", "system_performance", "resource_utilization",
        "bottleneck_identification", "charts_data", "map_visualization",
        "dashboard_config", "export_formats", "sharing_settings", "access_permissions",
        "is_public", "auto_share_enabled", "notification_enabled", "file_urls",
        "thumbnail_url", "tags", "meta_data", "version", "created_at", "updated_at",
        "generated_at", "expires_at", "last_accessed_at"
    ]
    result = {}
    for c in cols:
        val = getattr(report, c, None)
        if hasattr(val, 'value'):
            val = val.value
        result[c] = val
    return result


@router.get(
    "",
    response_model=dict,
    summary="List reports",
    description="Get paginated list of reports with optional filters"
)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    report_type: Optional[str] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sector_id: Optional[int] = Query(None, description="Filter by sector"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        paginator = Paginator(page, size)
        report_service = ReportService(db)
        filters = {}
        if report_type:
            filters["report_type"] = report_type
        if status:
            filters["status"] = status
        if sector_id:
            filters["sector_id"] = sector_id
        reports = await report_service.get_reports(skip=paginator.skip, limit=paginator.size, filters=filters)
        total = len(reports)
        return {
            "success": True,
            "message": "Reports retrieved successfully",
            "data": {
                "items": [_serialize_report(r) for r in reports],
                **paginator.get_metadata(total)
            }
        }
    except Exception as e:
        logger.error("List reports failed", error=str(e))
        raise DatabaseError("Failed to retrieve reports")


@router.get(
    "/stats",
    response_model=dict,
    summary="Get report statistics",
    description="Get aggregate statistics for reports"
)
async def get_report_stats(
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        stats = await report_service.get_report_stats()
        return {
            "success": True,
            "message": "Report statistics retrieved",
            "data": stats
        }
    except Exception as e:
        logger.error("Get report stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve report statistics")


@router.get(
    "/dashboard",
    response_model=dict,
    summary="Get admin dashboard data",
    description="Get aggregated dashboard data for administrators"
)
async def get_dashboard_data(
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
        logger.error("Get dashboard data failed", error=str(e))
        raise DatabaseError("Failed to retrieve dashboard data")


@router.put(
    "/{report_id}",
    response_model=dict,
    summary="Update report",
    description="Update a report's metadata (admin/sector only). Cannot update completed or archived reports."
)
async def update_report(
    report_id: int,
    data: ReportUpdate,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        result = await report_service.update_report(report_id=report_id, obj_in=data)
        return {
            "success": True,
            "message": "Report updated successfully",
            "data": _serialize_report(result)
        }
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Update report failed", error=str(e))
        raise BusinessLogicError("Failed to update report")


@router.post(
    "/{report_id}/archive",
    response_model=dict,
    summary="Archive report",
    description="Soft-archive a report (admin only)"
)
async def archive_report(
    report_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        result = await report_service.archive_report(report_id=report_id)
        return {
            "success": True,
            "message": "Report archived successfully",
            "data": _serialize_report(result)
        }
    except (NotFoundError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error("Archive report failed", error=str(e))
        raise BusinessLogicError("Failed to archive report")


@router.post(
    "/schedule",
    response_model=dict,
    summary="Schedule report",
    description="Schedule an existing report for recurring generation"
)
async def schedule_report(
    report_id: int = Body(..., embed=True),
    frequency: str = Body("DAILY", embed=True),
    schedule_config: Dict[str, Any] = Body({}, embed=True),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        result = await report_service.schedule_report(
            report_id=report_id,
            frequency=frequency,
            schedule_config=schedule_config
        )
        return {
            "success": True,
            "message": "Report scheduled successfully",
            "data": _serialize_report(result)
        }
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error("Schedule report failed", error=str(e))
        raise BusinessLogicError("Failed to schedule report")


@router.post(
    "/generate/performance",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate performance report",
    description="Generate system-wide performance metrics report"
)
async def generate_performance_report(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        report = await report_service.generate_performance_report(
            generated_by=current_user.id,
            start_date=start,
            end_date=end
        )
        return {
            "success": True,
            "message": "Performance report generated successfully",
            "data": _serialize_report(report)
        }
    except Exception as e:
        logger.error("Generate performance report failed", error=str(e))
        raise BusinessLogicError("Failed to generate performance report")


@router.post(
    "/generate/citizen-feedback",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate citizen feedback report",
    description="Generate aggregated citizen satisfaction and feedback report"
)
async def generate_citizen_feedback_report(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        report = await report_service.generate_citizen_feedback_report(
            generated_by=current_user.id,
            start_date=start,
            end_date=end
        )
        return {
            "success": True,
            "message": "Citizen feedback report generated successfully",
            "data": _serialize_report(report)
        }
    except Exception as e:
        logger.error("Generate citizen feedback report failed", error=str(e))
        raise BusinessLogicError("Failed to generate citizen feedback report")


@router.post(
    "/generate/priority-assessment",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate priority assessment",
    description="Generate priority distribution assessment across sectors or levels"
)
async def generate_priority_assessment(
    sector_id: Optional[int] = Query(None, description="Filter by sector ID"),
    priority_level: Optional[int] = Query(None, description="Filter by priority level"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        report = await report_service.generate_priority_assessment(
            generated_by=current_user.id,
            sector_id=sector_id,
            priority_level=priority_level,
            start_date=start,
            end_date=end
        )
        return {
            "success": True,
            "message": "Priority assessment generated successfully",
            "data": _serialize_report(report)
        }
    except Exception as e:
        logger.error("Generate priority assessment failed", error=str(e))
        raise BusinessLogicError("Failed to generate priority assessment")


@router.post(
    "/generate/signal/{signal_id}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI report for signal",
    description="Generate an AI-powered analysis report for a specific signal"
)
async def generate_signal_report(
    signal_id: int,
    current_user = Depends(get_current_sector_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        signal_service = SignalService(db)
        ai_service = AIService(db)
        signal = await signal_service.get_signal(signal_id=signal_id)
        if not signal:
            raise NotFoundError(f"Signal with id {signal_id} not found")
        ai_analysis = await ai_service.classify_signal(text=signal.description or "")
        report = await report_service.generate_signal_report(
            signal_id=signal_id,
            generated_by=current_user.id
        )
        return {
            "success": True,
            "message": "Signal report generated successfully",
            "data": _serialize_report(report)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Generate signal report failed", error=str(e))
        raise BusinessLogicError("Failed to generate signal report")


@router.post(
    "/generate/sector/{sector_id}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate sector report",
    description="Generate an AI-powered performance report for a sector"
)
async def generate_sector_report(
    sector_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        sector_service = SectorService(db)
        ai_service = AIService(db)
        sector = await sector_service.get_sector(sector_id=sector_id)
        if not sector:
            raise NotFoundError(f"Sector with id {sector_id} not found")
        ai_analysis = await ai_service.predict_trends(category=sector.name, days=30)
        report = await report_service.generate_sector_report(
            sector_id=sector_id,
            generated_by=current_user.id
        )
        return {
            "success": True,
            "message": "Sector report generated successfully",
            "data": _serialize_report(report)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Generate sector report failed", error=str(e))
        raise BusinessLogicError("Failed to generate sector report")


@router.post(
    "/generate/trends",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate trend analysis",
    description="Generate an AI-powered trend analysis report"
)
async def generate_trend_report(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        analytics_service = AnalyticsService(db)
        trend_data = await analytics_service.get_signal_trends(period="month")
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        report = await report_service.generate_trend_report(
            generated_by=current_user.id,
            start_date=start,
            end_date=end
        )
        return {
            "success": True,
            "message": "Trend report generated successfully",
            "data": _serialize_report(report)
        }
    except Exception as e:
        logger.error("Generate trend report failed", error=str(e))
        raise BusinessLogicError("Failed to generate trend report")


@router.get(
    "/{report_id}",
    response_model=dict,
    summary="Get report details",
    description="Get detailed information about a specific report"
)
async def get_report(
    report_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        report = await report_service.get_report(report_id=report_id)
        if not report:
            raise NotFoundError(f"Report with id {report_id} not found")
        return {
            "success": True,
            "message": "Report retrieved successfully",
            "data": _serialize_report(report)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get report failed", error=str(e))
        raise NotFoundError(f"Report with id {report_id} not found")


@router.delete(
    "/{report_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete report",
    description="Delete a report (admin only)"
)
async def delete_report(
    report_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        deleted = await report_service.delete_report(report_id=report_id)
        if not deleted:
            raise NotFoundError(f"Report with id {report_id} not found")
        return {
            "success": True,
            "message": "Report deleted successfully"
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Delete report failed", error=str(e))
        raise NotFoundError(f"Report with id {report_id} not found")


@router.get(
    "/{report_id}/export",
    response_model=dict,
    summary="Export report",
    description="Export a report in the specified format"
)
async def export_report(
    report_id: int,
    export_format: str = Query("pdf", pattern="^(pdf|xlsx|csv|json)$", description="Export format"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        report_service = ReportService(db)
        export_data = await report_service.export_report(report_id=report_id, export_format=export_format)
        if not export_data:
            raise NotFoundError(f"Report with id {report_id} not found")
        return {
            "success": True,
            "message": "Report exported successfully",
            "data": export_data
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Export report failed", error=str(e))
        raise BusinessLogicError("Failed to export report")
