"""
AI Schemas - Urbain Sustainability System
Schémas Pydantic pour les données IA et ML
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Signal description text")
    images: Optional[List[str]] = Field(None, description="Optional image URLs")
    location: Optional[Dict[str, float]] = Field(None, description="Optional {latitude, longitude}")


class AssessPriorityRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Signal description")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    safety_risk_level: Optional[int] = Field(None, ge=0, le=5)
    affected_people_count: Optional[int] = Field(None, ge=0)
    affected_area_sqm: Optional[float] = Field(None, ge=0)
    category_id: Optional[int] = None


class PredictTrendsRequest(BaseModel):
    category: Optional[str] = Field(None, description="Category code to filter")
    days: int = Field(30, ge=1, le=365, description="Prediction horizon in days")
    historical_data: Optional[List[Dict[str, Any]]] = None


class DetectAnomaliesRequest(BaseModel):
    description: str = Field(..., min_length=3, description="Signal description")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: Optional[str] = Field(None, description="Assigned category code")


class BatchClassifyItem(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    text: Optional[str] = None
    images: Optional[List[str]] = None
    location: Optional[Dict[str, float]] = None


class BatchClassifyRequest(BaseModel):
    signals: List[BatchClassifyItem] = Field(..., min_length=1, max_length=100)


class GenerateReportRequest(BaseModel):
    signal_id: int = Field(..., description="Signal ID to analyze")
