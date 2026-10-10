"""
Map Routes - Urbain Sustainability System
Routes cartographiques avec géocodage, heatmap, clusters et données de localisation
"""

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin, get_optional_user
from app.services.map_service import MapService
from app.core.exceptions import ValidationError, ExternalServiceError, NotFoundError
from app.schemas.map import GeocodeRequest, ReverseGeocodeRequest, HeatmapRequest, ClusterRequest

logger = structlog.get_logger()
router = APIRouter()


@router.post("/geocode", summary="Geocode address to coordinates",
             description="Convert an address string to latitude/longitude coordinates")
async def geocode_address(
    request: GeocodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        result = await service.geocode_address(request.address)
        return {"success": True, "message": "Address geocoded", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        await service.log_error("geocode_route", e) if hasattr(service, 'log_error') else None
        return {"success": False, "message": "Geocoding failed", "data": None}


@router.post("/reverse-geocode", summary="Reverse geocode coordinates to address",
             description="Convert latitude/longitude coordinates to a formatted address")
async def reverse_geocode(
    request: ReverseGeocodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        result = await service.reverse_geocode(request.latitude, request.longitude)
        return {"success": True, "message": "Coordinates reverse geocoded", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Reverse geocoding failed", "data": None}


@router.get("/heatmap", summary="Get heatmap data",
            description="Generate heatmap intensity grid for signals within given bounds")
async def get_heatmap(
    lat_min: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    lat_max: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    lng_min: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    lng_max: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
    grid_size: float = Query(0.01, ge=0.001, le=0.1, description="Grid cell size in degrees"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        bounds = {"lat_min": lat_min, "lat_max": lat_max, "lng_min": lng_min, "lng_max": lng_max}
        result = await service.get_heatmap_data(bounds, days=days, grid_size=grid_size)
        return {"success": True, "message": "Heatmap data generated", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Failed to generate heatmap", "data": None}


@router.get("/clusters", summary="Get cluster data",
            description="Generate signal clusters for map visualization at a given zoom level")
async def get_clusters(
    lat_min: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    lat_max: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    lng_min: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    lng_max: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    zoom_level: float = Query(12.0, ge=1.0, le=20.0, description="Map zoom level"),
    cluster_radius: int = Query(50, ge=20, le=200, description="Cluster radius in pixels"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        bounds = {"lat_min": lat_min, "lat_max": lat_max, "lng_min": lng_min, "lng_max": lng_max}
        result = await service.get_cluster_data(bounds, zoom_level=zoom_level, cluster_radius=cluster_radius)
        return {"success": True, "message": "Cluster data generated", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Failed to generate clusters", "data": None}


@router.get("/nearby", summary="Get nearby signals",
            description="Find signals within a radius of coordinates")
async def get_nearby(
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=100, description="Search radius in km"),
    status: Optional[str] = Query(None, description="Filter by status (comma-separated)"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        status_filter = [s.strip() for s in status.split(",")] if status else None
        result = await service.get_nearby_signals(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            status_filter=status_filter,
            limit=limit
        )
        return {"success": True, "message": "Nearby signals found", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Failed to find nearby signals", "data": None}


@router.get("/data", summary="Get combined map data",
            description="Get heatmap + clusters + nearby signals in one request for efficient map rendering")
async def get_map_data(
    lat: float = Query(..., ge=-90, le=90, description="Center latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Center longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=100, description="Search radius"),
    zoom_level: float = Query(12.0, ge=1.0, le=20.0, description="Zoom level"),
    days: int = Query(30, ge=1, le=365, description="Heatmap period"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        half = radius_km / 111.0
        bounds = {
            "lat_min": lat - half,
            "lat_max": lat + half,
            "lng_min": lng - half,
            "lng_max": lng + half
        }
        try:
            heatmap = await service.get_heatmap_data(bounds, days=days, grid_size=0.01)
        except Exception as e:
            logger.warning("Heatmap failed", error=str(e))
            heatmap = None
        try:
            clusters = await service.get_cluster_data(bounds, zoom_level=zoom_level, cluster_radius=50)
        except Exception as e:
            logger.warning("Clusters failed", error=str(e))
            clusters = None
        try:
            nearby = await service.get_nearby_signals(lat, lng, radius_km=radius_km, limit=100)
        except Exception as e:
            logger.warning("Nearby failed", error=str(e))
            nearby = None
        result = {
            "center": {"latitude": lat, "longitude": lng},
            "radius_km": radius_km,
            "bounds": bounds,
            "heatmap": heatmap,
            "clusters": clusters,
            "nearby": nearby,
        }
        return {"success": True, "message": "Map data retrieved", "data": result}
    except Exception as e:
        return {"success": False, "message": "Failed to get map data", "data": None}


@router.post("/places", summary="Search places",
             description="Search for places near a location")
async def search_places(
    query: str = Query(..., min_length=2, description="Search query"),
    latitude: Optional[float] = Query(None, description="Center latitude"),
    longitude: Optional[float] = Query(None, description="Center longitude"),
    radius: int = Query(5000, ge=100, le=50000, description="Search radius in meters"),
    place_type: Optional[str] = Query(None, description="Type of place"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        location = (latitude, longitude) if latitude and longitude else None
        result = await service.search_places(query, location=location, radius=radius, place_type=place_type)
        return {"success": True, "message": "Places found", "data": {"places": result}}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Places search failed", "data": None}


@router.post("/distance", summary="Calculate distance",
             description="Calculate distance and duration between two coordinates")
async def calculate_distance(
    origin_lat: float = Body(..., embed=True, description="Origin latitude"),
    origin_lng: float = Body(..., embed=True, description="Origin longitude"),
    dest_lat: float = Body(..., embed=True, description="Destination latitude"),
    dest_lng: float = Body(..., embed=True, description="Destination longitude"),
    mode: str = Body("driving", embed=True, description="Travel mode (driving/walking/bicycling/transit)"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        result = await service.calculate_distance(
            origin=(origin_lat, origin_lng),
            destination=(dest_lat, dest_lng),
            mode=mode
        )
        return {"success": True, "message": "Distance calculated", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Distance calculation failed", "data": None}


@router.post("/validate-address", summary="Validate an address",
             description="Validate and geocode an address, returning confidence score and any issues")
async def validate_address(
    request: GeocodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        result = await service.validate_address(request.address)
        return {"success": True, "message": "Address validated", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Address validation failed", "data": None}


@router.post("/route", summary="Get route directions",
             description="Get turn-by-turn directions between two points with optional waypoints")
async def get_route(
    origin_lat: float = Body(..., embed=True, description="Origin latitude"),
    origin_lng: float = Body(..., embed=True, description="Origin longitude"),
    dest_lat: float = Body(..., embed=True, description="Destination latitude"),
    dest_lng: float = Body(..., embed=True, description="Destination longitude"),
    mode: str = Body("driving", embed=True, description="Travel mode"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = MapService(db)
        result = await service.get_route(
            origin=(origin_lat, origin_lng),
            destination=(dest_lat, dest_lng),
            mode=mode
        )
        return {"success": True, "message": "Route calculated", "data": result}
    except ValidationError as e:
        return {"success": False, "message": str(e), "data": None}
    except Exception as e:
        return {"success": False, "message": "Route calculation failed", "data": None}
