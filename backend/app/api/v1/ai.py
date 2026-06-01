"""
AI Routes - Urbain Sustainability System
Routes d'intelligence artificielle pour classification, priorisation et analyse
"""

import structlog
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.services.ai_service import AIService
from app.services.signal_service import SignalService
from app.core.exceptions import ValidationError, ExternalServiceError, NotFoundError, BusinessLogicError
from app.schemas.ai import (
    ClassifyRequest, AssessPriorityRequest, PredictTrendsRequest,
    DetectAnomaliesRequest, BatchClassifyRequest, GenerateReportRequest
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/classify", summary="Classify signal text into category",
             description="AI-powered classification of signal description into predefined categories")
async def classify_signal(
    request: ClassifyRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        result = await service.classify_signal(
            text=request.text,
            images=request.images,
            location=request.location
        )
        return {"success": True, "message": "Signal classified", "data": result}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/assess-priority", summary="Assess signal priority",
             description="AI-powered priority assessment based on severity, urgency, and impact")
async def assess_priority(
    request: AssessPriorityRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        signal_data = request.model_dump()
        result = await service.assess_priority(signal_data)
        return {"success": True, "message": "Priority assessed", "data": result}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/predict-trends", summary="Predict signal trends",
             description="AI-powered trend forecasting for signal volumes over time")
async def predict_trends(
    request: PredictTrendsRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        result = await service.predict_trends(
            category=request.category,
            days=request.days,
            historical_data=request.historical_data
        )
        return {"success": True, "message": "Trends predicted", "data": result}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/detect-anomalies", summary="Detect anomalies in signal data",
             description="AI-powered anomaly detection for signal descriptions and metadata")
async def detect_anomalies(
    request: DetectAnomaliesRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        result = await service.detect_anomalies(request.model_dump())
        return {"success": True, "message": "Anomalies detected", "data": result}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/analyze-severity", summary="Full severity analysis (classify + priority)",
             description="Combined AI analysis: classify, assess priority, and detect anomalies in one call")
async def analyze_severity(
    request: ClassifyRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        classification = await service.classify_signal(
            text=request.text,
            images=request.images,
            location=request.location
        )
        signal_data = {
            "description": request.text,
            "latitude": request.location.get("latitude", 36.8065) if request.location else 36.8065,
            "longitude": request.location.get("longitude", 10.1815) if request.location else 10.1815,
        }
        priority = await service.assess_priority(signal_data, classification)
        anomalies = await service.detect_anomalies({
            "description": request.text,
            "latitude": signal_data["latitude"],
            "longitude": signal_data["longitude"],
            "category": classification.get("predicted_category")
        })
        return {
            "success": True,
            "message": "Severity analysis complete",
            "data": {
                "classification": classification,
                "priority_assessment": priority,
                "anomalies": anomalies,
                "summary": {
                    "category": classification.get("predicted_category"),
                    "confidence": classification.get("confidence_score"),
                    "priority_level": priority.get("priority_level"),
                    "priority_score": priority.get("priority_score"),
                    "anomalies_detected": anomalies.get("anomalies_detected"),
                }
            }
        }
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/generate-report", summary="Generate full AI report for a signal",
             description="Generate comprehensive AI analysis report including classification, priority, trends, and anomalies")
async def generate_report(
    request: GenerateReportRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        signal_service = SignalService(db)
        signal = await signal_service.get_signal(request.signal_id)
        if not signal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found")

        ai_service = AIService(db)
        classification = await ai_service.classify_signal(
            text=signal.description or "",
            images=[img.url for img in (signal.images or [])][:5] if hasattr(signal, 'images') else None,
            location={"latitude": signal.latitude, "longitude": signal.longitude}
        )
        signal_dict = {
            "description": signal.description or "",
            "latitude": signal.latitude,
            "longitude": signal.longitude,
            "safety_risk_level": getattr(signal, 'safety_risk_level', None),
            "affected_people_count": getattr(signal, 'affected_people_count', None),
            "affected_area_sqm": getattr(signal, 'affected_area_sqm', None),
        }
        priority = await ai_service.assess_priority(signal_dict, classification)
        report = await ai_service.generate_report(signal, classification, priority)
        return {"success": True, "message": "AI report generated", "data": report}
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/batch-classify", summary="Batch classify multiple signals",
             description="AI-powered batch classification and priority assessment for up to 100 signals")
async def batch_classify(
    request: BatchClassifyRequest,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        signals_data = [item.model_dump(exclude_none=True) for item in request.signals]
        results = await service.batch_classify(signals_data)
        return {"success": True, "message": "Batch classification complete", "data": {"results": results}}
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.get("/model-info", summary="Get AI model information",
             description="Retrieve metadata about the current AI model including version, capabilities, and performance")
async def get_model_info(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        info = await service.get_model_info()
        return {"success": True, "message": "Model info retrieved", "data": info}
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.get("/insights", summary="Get AI insights dashboard data",
             description="Aggregated AI insights including trend predictions, category distribution, and model health")
async def get_ai_insights(
    days: int = Query(30, ge=1, le=365, description="Prediction horizon"),
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AIService(db)
        model_info = await service.get_model_info()
        trends = await service.predict_trends(days=days)
        return {
            "success": True,
            "message": "AI insights retrieved",
            "data": {
                "model": model_info,
                "trends": trends,
                "dashboard": {
                    "predicted_signals_next_30d": trends.get("predicted_total_signals", 0),
                    "trend_direction": trends.get("trend_direction", "stable"),
                    "confidence_level": trends.get("confidence_level", 0),
                    "weekly_breakdown": trends.get("weekly_breakdown", {}),
                }
            }
        }
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
