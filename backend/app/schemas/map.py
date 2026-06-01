"""
Map Schemas - Urbain Sustainability System
Schémas Pydantic pour les données cartographiques
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GeocodeRequest(BaseModel):
    address: str = Field(..., min_length=3, description="Address to geocode")


class ReverseGeocodeRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")


class HeatmapRequest(BaseModel):
    lat_min: float = Field(..., ge=-90, le=90)
    lat_max: float = Field(..., ge=-90, le=90)
    lng_min: float = Field(..., ge=-180, le=180)
    lng_max: float = Field(..., ge=-180, le=180)
    days: int = Field(30, ge=1, le=365)
    grid_size: float = Field(0.01, ge=0.001, le=0.1)


class ClusterRequest(BaseModel):
    lat_min: float = Field(..., ge=-90, le=90)
    lat_max: float = Field(..., ge=-90, le=90)
    lng_min: float = Field(..., ge=-180, le=180)
    lng_max: float = Field(..., ge=-180, le=180)
    zoom_level: int = Field(12, ge=1, le=20)
    cluster_radius: int = Field(50, ge=20, le=200)
