"""
Analytics Routes - Urbain Sustainability System
Analyse avancée, tendances, performances et métriques
"""

import structlog
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.services.analytics_service import AnalyticsService
from app.core.exceptions import ValidationError, DatabaseError

logger = structlog.get_logger()
router = APIRouter()


@router.get("/dashboard", summary="Get dashboard statistics",
            description="Aggregated KPIs for the main dashboard: total signals, resolution rate, active users, etc.")
async def get_dashboard_stats(
    days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_dashboard_stats(period=f"{days}d")
    return {"success": True, "message": "Dashboard stats retrieved", "data": result}


@router.get("/trends", summary="Get signal trends over time",
            description="Time-series analysis of signal volumes, categorized by status and priority")
async def get_signal_trends(
    days: int = Query(30, ge=1, le=365, description="Lookback period"),
    granularity: str = Query("day", pattern="^(day|week|month)$", description="Aggregation granularity"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_signal_trends(period=f"{days}d", granularity=granularity)
    return {"success": True, "message": "Signal trends retrieved", "data": result}


@router.get("/sector-performance", summary="Get sector performance metrics",
            description="Performance analytics per sector: response times, resolution rates, workload distribution")
async def get_sector_performance(
    days: int = Query(30, ge=1, le=365, description="Lookback period"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_sector_performance(period=f"{days}d")
    return {"success": True, "message": "Sector performance retrieved", "data": result}


@router.get("/category-breakdown", summary="Get category distribution",
            description="Breakdown of signals by category with percentage distribution and trends")
async def get_category_breakdown(
    days: int = Query(30, ge=1, le=365, description="Lookback period"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_category_breakdown(period=f"{days}d")
    return {"success": True, "message": "Category breakdown retrieved", "data": result}


@router.get("/satisfaction", summary="Get citizen satisfaction metrics",
            description="Aggregated citizen satisfaction scores, feedback analysis, and NPS")
async def get_citizen_satisfaction(
    days: int = Query(30, ge=1, le=365, description="Lookback period"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_citizen_satisfaction(period=f"{days}d")
    return {"success": True, "message": "Satisfaction metrics retrieved", "data": result}


@router.get("/response-times", summary="Get response time analytics",
            description="Average response and resolution times breakdown by priority, category, and sector")
async def get_response_times(
    days: int = Query(30, ge=1, le=365, description="Lookback period"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_response_times(period=f"{days}d")
    return {"success": True, "message": "Response times retrieved", "data": result}


@router.get("/predictions", summary="Get prediction metrics",
            description="AI-powered predictions for signal volumes, resource allocation, and trend forecasting")
async def get_prediction_metrics(
    days: int = Query(30, ge=1, le=90, description="Prediction horizon"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_prediction_metrics(period=f"{days}d")
    return {"success": True, "message": "Prediction metrics retrieved", "data": result}


@router.get("/hotspots", summary="Get signal hotspot data",
            description="Geographic hotspot analysis identifying high-density signal areas with cluster data")
async def get_hotspot_data(
    days: int = Query(30, ge=1, le=365, description="Lookback period"),
    min_density: float = Query(0.0, ge=0.0, description="Minimum density threshold"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_hotspot_data(period=f"{days}d", min_signals=int(min_density) if min_density > 0 else 3)
    return {"success": True, "message": "Hotspot data retrieved", "data": result}


@router.get("/temporal-patterns", summary="Get temporal patterns",
            description="Analysis of signal submission patterns by time of day, day of week, and seasonal trends")
async def get_temporal_patterns(
    days: int = Query(90, ge=7, le=365, description="Lookback period"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.get_temporal_patterns(period=f"{days}d")
    return {"success": True, "message": "Temporal patterns retrieved", "data": result}


@router.get("/summary-report", summary="Generate summary report",
            description="Generate a comprehensive summary report with key metrics, trends, and insights")
async def generate_summary_report(
    days: int = Query(30, ge=1, le=365, description="Report period"),
    include_charts: bool = Query(False, description="Include chart data in report"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    result = await service.generate_summary_report(period=f"{days}d")
    return {"success": True, "message": "Summary report generated", "data": result}
