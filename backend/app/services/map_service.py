"""
Map Service - Urbain Sustainability System
Service cartographique avec intégration Google Maps et géocodage
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from math import radians, sin, cos, sqrt, atan2

import structlog

from app.core.exceptions import (
    ExternalServiceError,
    ValidationError,
    ServiceUnavailableError,
    NotFoundError
)
from app.core.config import settings
from app.repositories.signal_repository import SignalRepository
from app.models.signal import Signal, SignalStatus
from app.services.base import BaseService
from app.utils.validators import validate_coordinates_range
from app.utils.helpers import calculate_distance

logger = structlog.get_logger()


class MapService(BaseService):
    """
    Service cartographique pour la gestion des localisations
    Intègre Google Maps API avec cache et fallback
    """

    def __init__(self, db):
        super().__init__(db)
        self.signal_repo = SignalRepository(db, Signal)
        self._maps_client = None
        self._geocode_cache: Dict[str, Any] = {}

    async def _get_maps_client(self):
        if self._maps_client is None:
            if settings.GOOGLE_MAPS_API_KEY:
                try:
                    import googlemaps
                    self._maps_client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                except ImportError:
                    logger.warning("googlemaps library not installed - using simulation")
                    self._maps_client = None
                except Exception as e:
                    logger.error("Failed to initialize Google Maps client", error=str(e))
                    self._maps_client = None
            else:
                logger.info("No Google Maps API key configured - using simulation")
        return self._maps_client

    def _cache_key(self, prefix: str, *args) -> str:
        key = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(key.encode()).hexdigest()

    async def _get_cached_or_fetch(self, cache_key: str, fetch_func, ttl: int = 3600) -> Any:
        cached = await self.get_cached_result(cache_key)
        if cached:
            return cached
        result = await fetch_func()
        if result:
            await self.cache_result(cache_key, result, ttl=ttl)
        return result

    async def geocode_address(self, address: str) -> Dict[str, Any]:
        try:
            if not address or len(address.strip()) < 3:
                raise ValidationError("Address must be at least 3 characters")

            cache_key = self._cache_key("geocode", address.strip().lower())

            if cache_key in self._geocode_cache:
                return self._geocode_cache[cache_key]

            client = await self._get_maps_client()
            if client:
                try:
                    result = client.geocode(address)
                    if result and len(result) > 0:
                        location = result[0]["geometry"]["location"]
                        formatted = result[0].get("formatted_address", address)
                        components = {}
                        for comp in result[0].get("address_components", []):
                            for comp_type in comp["types"]:
                                components[comp_type] = comp["long_name"]

                        geocode_result = {
                            "latitude": location["lat"],
                            "longitude": location["lng"],
                            "formatted_address": formatted,
                            "components": components,
                            "place_id": result[0].get("place_id"),
                            "source": "google_maps",
                            "accuracy": result[0].get("geometry", {}).get("location_type", "APPROXIMATE")
                        }
                        self._geocode_cache[cache_key] = geocode_result
                        return geocode_result
                except Exception as e:
                    logger.warning("Google Maps geocoding failed", error=str(e))

            simulated = await self._simulate_geocode(address)
            simulated["source"] = "simulated"
            self._geocode_cache[cache_key] = simulated
            return simulated

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("geocode_address", e)
            raise ExternalServiceError("Geocoding failed")

    async def _simulate_geocode(self, address: str) -> Dict[str, Any]:
        address_lower = address.lower()

        city_coords = {
            "tunis": (36.8065, 10.1815),
            "sfax": (34.7473, 10.7662),
            "sousse": (35.8256, 10.6364),
            "nabeul": (36.4517, 10.7352),
            "bizerte": (37.2745, 9.8736),
            "gabes": (33.8889, 10.0984),
            "kairouan": (35.6781, 10.0965),
            "monastir": (35.7643, 10.8115),
            "kebili": (33.7050, 8.9650)
        }

        lat, lon = 36.8065, 10.1815
        for city, coords in city_coords.items():
            if city in address_lower:
                lat, lon = coords
                break

        lat += (hash(address) % 100) / 1000.0
        lon += (hash(address[::-1]) % 100) / 1000.0

        return {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "formatted_address": address,
            "components": {
                "route": address.split(",")[0] if "," in address else address,
                "locality": "Tunis",
                "country": "Tunisia"
            },
            "accuracy": "SIMULATED"
        }

    async def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        try:
            validate_coordinates_range(latitude, longitude)

            cache_key = self._cache_key("reverse_geocode", latitude, longitude)

            client = await self._get_maps_client()
            if client:
                try:
                    result = client.reverse_geocode((latitude, longitude))
                    if result and len(result) > 0:
                        components = {}
                        for comp in result[0].get("address_components", []):
                            for comp_type in comp["types"]:
                                components[comp_type] = comp["long_name"]

                        return {
                            "latitude": latitude,
                            "longitude": longitude,
                            "formatted_address": result[0].get("formatted_address", ""),
                            "components": components,
                            "place_id": result[0].get("place_id"),
                            "source": "google_maps"
                        }
                except Exception as e:
                    logger.warning("Reverse geocoding failed", error=str(e))

            return {
                "latitude": latitude,
                "longitude": longitude,
                "formatted_address": f"{latitude:.4f}, {longitude:.4f}",
                "components": {
                    "country": "Tunisia"
                },
                "source": "simulated"
            }

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("reverse_geocode", e)
            raise ExternalServiceError("Reverse geocoding failed")

    async def search_places(
        self,
        query: str,
        location: Optional[Tuple[float, float]] = None,
        radius: int = 5000,
        place_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            if not query or len(query.strip()) < 2:
                raise ValidationError("Search query must be at least 2 characters")

            client = await self._get_maps_client()
            if client:
                try:
                    params = {"query": query, "radius": radius}
                    if location:
                        params["location"] = location
                    if place_type:
                        params["type"] = place_type

                    result = client.places(**params)
                    places = []
                    for place in result.get("results", []):
                        places.append({
                            "place_id": place.get("place_id"),
                            "name": place.get("name"),
                            "formatted_address": place.get("formatted_address"),
                            "latitude": place["geometry"]["location"]["lat"],
                            "longitude": place["geometry"]["location"]["lng"],
                            "rating": place.get("rating"),
                            "types": place.get("types", []),
                            "icon": place.get("icon")
                        })
                    return places
                except Exception as e:
                    logger.warning("Places search failed", error=str(e))

            simulated = []
            base_lat, base_lon = location or (36.8065, 10.1815)
            for i in range(5):
                simulated.append({
                    "place_id": f"sim_{i}",
                    "name": f"{query} Location {i + 1}",
                    "formatted_address": f"{query}, Tunis, Tunisia",
                    "latitude": base_lat + (i - 2) * 0.01,
                    "longitude": base_lon + (i - 2) * 0.01,
                    "rating": round(3.0 + (i % 3) * 0.5, 1),
                    "types": [place_type] if place_type else ["point_of_interest"],
                    "source": "simulated"
                })
            return simulated

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("search_places", e)
            raise ExternalServiceError("Places search failed")

    async def calculate_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "driving"
    ) -> Dict[str, Any]:
        try:
            validate_coordinates_range(origin[0], origin[1])
            validate_coordinates_range(destination[0], destination[1])

            valid_modes = ["driving", "walking", "bicycling", "transit"]
            if mode not in valid_modes:
                raise ValidationError(f"Invalid mode. Must be one of: {valid_modes}")

            client = await self._get_maps_client()
            if client:
                try:
                    result = client.distance_matrix(
                        origins=[origin],
                        destinations=[destination],
                        mode=mode,
                        units="metric"
                    )
                    if result["rows"] and result["rows"][0]["elements"]:
                        element = result["rows"][0]["elements"][0]
                        if element["status"] == "OK":
                            return {
                                "distance_km": element["distance"]["value"] / 1000,
                                "distance_text": element["distance"]["text"],
                                "duration_minutes": element["duration"]["value"] / 60,
                                "duration_text": element["duration"]["text"],
                                "origin": {"latitude": origin[0], "longitude": origin[1]},
                                "destination": {"latitude": destination[0], "longitude": destination[1]},
                                "mode": mode,
                                "source": "google_maps"
                            }
                except Exception as e:
                    logger.warning("Distance matrix API failed", error=str(e))

            haversine_km = calculate_distance(origin[0], origin[1], destination[0], destination[1])
            estimated_minutes = haversine_km / (50 if mode == "driving" else 5)

            return {
                "distance_km": round(haversine_km, 2),
                "distance_text": f"{haversine_km:.1f} km",
                "duration_minutes": round(estimated_minutes),
                "duration_text": f"{int(estimated_minutes)} mins",
                "origin": {"latitude": origin[0], "longitude": origin[1]},
                "destination": {"latitude": destination[0], "longitude": destination[1]},
                "mode": mode,
                "source": "haversine"
            }

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("calculate_distance", e)
            raise ExternalServiceError("Distance calculation failed")

    async def get_nearby_signals(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        status_filter: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        try:
            validate_coordinates_range(latitude, longitude)

            if radius_km <= 0 or radius_km > 100:
                raise ValidationError("Radius must be between 0.1 and 100 km")

            signals = await self.signal_repo.get_signals_near_location(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                limit=limit
            )

            if status_filter:
                signals = [s for s in signals if s.status.value in status_filter]

            nearby = []
            for signal in signals:
                distance = calculate_distance(latitude, longitude, signal.latitude, signal.longitude)
                if distance <= radius_km:
                    img = signal.images
                    first_image = img[0] if isinstance(img, list) and len(img) > 0 else (img if isinstance(img, str) else None)
                    nearby.append({
                        "id": signal.id,
                        "reference_number": signal.reference_number,
                        "title": signal.title,
                        "status": signal.status.value,
                        "latitude": signal.latitude,
                        "longitude": signal.longitude,
                        "distance_km": round(distance, 2),
                        "category_id": signal.category_id,
                        "priority_id": signal.priority_id,
                        "created_at": signal.created_at.isoformat() if signal.created_at else None,
                        "images": signal.images or None
                    })

            nearby.sort(key=lambda x: x["distance_km"])

            result = {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km,
                "total_nearby": len(nearby),
                "signals": nearby,
                "filters_applied": {
                    "status": status_filter,
                    "limit": limit
                }
            }

            await self.log_operation("get_nearby_signals", {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km,
                "found": len(nearby)
            })

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_nearby_signals", e)
            raise ExternalServiceError("Failed to get nearby signals")

    async def get_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        try:
            validate_coordinates_range(origin[0], origin[1])
            validate_coordinates_range(destination[0], destination[1])

            client = await self._get_maps_client()
            if client:
                try:
                    params = {
                        "origin": origin,
                        "destination": destination,
                        "mode": mode,
                        "units": "metric"
                    }
                    if waypoints:
                        params["waypoints"] = waypoints

                    result = client.directions(**params)
                    if result:
                        route = result[0]
                        steps = []
                        for leg in route.get("legs", []):
                            for step in leg.get("steps", []):
                                steps.append({
                                    "instruction": step.get("html_instructions", ""),
                                    "distance": step.get("distance", {}).get("text"),
                                    "duration": step.get("duration", {}).get("text"),
                                    "start_location": step.get("start_location"),
                                    "end_location": step.get("end_location")
                                })

                        return {
                            "distance_km": route["legs"][0]["distance"]["value"] / 1000,
                            "distance_text": route["legs"][0]["distance"]["text"],
                            "duration_minutes": route["legs"][0]["duration"]["value"] / 60,
                            "duration_text": route["legs"][0]["duration"]["text"],
                            "steps": steps,
                            "origin": {"latitude": origin[0], "longitude": origin[1]},
                            "destination": {"latitude": destination[0], "longitude": destination[1]},
                            "mode": mode,
                            "source": "google_maps"
                        }
                except Exception as e:
                    logger.warning("Directions API failed", error=str(e))

            distance = calculate_distance(origin[0], origin[1], destination[0], destination[1])
            return {
                "distance_km": round(distance, 2),
                "distance_text": f"{distance:.1f} km",
                "duration_minutes": round(distance / 0.8),
                "duration_text": f"{round(distance / 0.8)} mins",
                "steps": [],
                "origin": {"latitude": origin[0], "longitude": origin[1]},
                "destination": {"latitude": destination[0], "longitude": destination[1]},
                "mode": mode,
                "source": "haversine"
            }

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_route", e)
            raise ExternalServiceError("Route calculation failed")

    async def get_heatmap_data(
        self,
        bounds: Dict[str, float],
        days: int = 30,
        grid_size: float = 0.01
    ) -> Dict[str, Any]:
        try:
            required = ["lat_min", "lat_max", "lng_min", "lng_max"]
            missing = [f for f in required if f not in bounds]
            if missing:
                raise ValidationError(f"Missing bounds: {missing}")

            validate_coordinates_range(bounds["lat_min"], bounds["lng_min"])
            validate_coordinates_range(bounds["lat_max"], bounds["lng_max"])

            from datetime import datetime, timedelta, timezone
            start_date = datetime.now(timezone.utc) - timedelta(days=days)

            signals = await self.signal_repo.get_by_location_bounds(
                lat_min=bounds["lat_min"],
                lat_max=bounds["lat_max"],
                lng_min=bounds["lng_min"],
                lng_max=bounds["lng_max"],
                limit=5000
            )

            signals = [s for s in signals if s.created_at and s.created_at >= start_date]

            heatmap_points = []
            grid_counts = {}

            for signal in signals:
                lat_grid = round(signal.latitude / grid_size) * grid_size
                lng_grid = round(signal.longitude / grid_size) * grid_size
                cell_key = f"{lat_grid},{lng_grid}"

                if cell_key not in grid_counts:
                    grid_counts[cell_key] = {
                        "latitude": lat_grid + grid_size / 2,
                        "longitude": lng_grid + grid_size / 2,
                        "count": 0,
                        "total_priority": 0,
                        "signals": []
                    }

                grid_counts[cell_key]["count"] += 1
                grid_counts[cell_key]["total_priority"] += signal.ai_priority_score or 0
                grid_counts[cell_key]["signals"].append({
                    "id": signal.id,
                    "latitude": signal.latitude,
                    "longitude": signal.longitude,
                    "priority": signal.ai_priority_score
                })

            for cell_key, cell_data in grid_counts.items():
                heatmap_points.append({
                    "latitude": cell_data["latitude"],
                    "longitude": cell_data["longitude"],
                    "intensity": min(1.0, cell_data["count"] / 20),
                    "count": cell_data["count"],
                    "avg_priority": round(cell_data["total_priority"] / max(1, cell_data["count"]), 4),
                    "signals": cell_data["signals"]
                })

            heatmap_points.sort(key=lambda x: x["count"], reverse=True)

            result = {
                "bounds": bounds,
                "grid_size": grid_size,
                "period_days": days,
                "total_signals": len(signals),
                "grid_cells": len(heatmap_points),
                "heatmap_points": heatmap_points[:200],
                "max_intensity": max((p["count"] for p in heatmap_points), default=0)
            }

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_heatmap_data", e)
            raise ExternalServiceError("Failed to generate heatmap data")

    async def get_cluster_data(
        self,
        bounds: Dict[str, float],
        zoom_level: float = 12.0,
        cluster_radius: int = 50
    ) -> Dict[str, Any]:
        try:
            required = ["lat_min", "lat_max", "lng_min", "lng_max"]
            missing = [f for f in required if f not in bounds]
            if missing:
                raise ValidationError(f"Missing bounds: {missing}")

            signals = await self.signal_repo.get_by_location_bounds(
                lat_min=bounds["lat_min"],
                lat_max=bounds["lat_max"],
                lng_min=bounds["lng_min"],
                lng_max=bounds["lng_max"],
                limit=10000
            )

            from math import cos
            lat_spread = bounds["lat_max"] - bounds["lat_min"]
            lng_spread = bounds["lng_max"] - bounds["lng_min"]
            grid_cols = max(1, int(lng_spread / (cluster_radius / 111000.0 / cos((bounds["lat_min"] + bounds["lat_max"]) / 2))))
            grid_rows = max(1, int(lat_spread / (cluster_radius / 111000.0)))
            total_cells = grid_cols * grid_rows

            if total_cells > 10000:
                grid_cols = int(sqrt(10000 * grid_cols / grid_rows))
                grid_rows = total_cells // grid_cols

            clusters = {}
            for signal in signals:
                col = int((signal.longitude - bounds["lng_min"]) / lng_spread * grid_cols)
                row = int((signal.latitude - bounds["lat_min"]) / lat_spread * grid_rows)
                col = min(col, grid_cols - 1)
                row = min(row, grid_rows - 1)
                cell_key = f"{col}_{row}"

                if cell_key not in clusters:
                    clusters[cell_key] = {
                        "cluster_id": cell_key,
                        "center_latitude": bounds["lat_min"] + (row + 0.5) / grid_rows * lat_spread,
                        "center_longitude": bounds["lng_min"] + (col + 0.5) / grid_cols * lng_spread,
                        "signal_count": 0,
                        "signals": []
                    }

                clusters[cell_key]["signal_count"] += 1
                clusters[cell_key]["signals"].append({
                    "id": signal.id,
                    "reference_number": signal.reference_number,
                    "title": signal.title[:50],
                    "status": signal.status.value,
                    "latitude": signal.latitude,
                    "longitude": signal.longitude
                })

            result = {
                "bounds": bounds,
                "zoom_level": zoom_level,
                "cluster_radius_pixels": cluster_radius,
                "total_signals": len(signals),
                "total_clusters": len(clusters),
                "clusters": [
                    {
                        "cluster_id": c["cluster_id"],
                        "center": {
                            "latitude": c["center_latitude"],
                            "longitude": c["center_longitude"]
                        },
                        "signal_count": c["signal_count"],
                        "radius_meters": cluster_radius,
                        "signals": c["signals"][:10]
                    }
                    for c in sorted(clusters.values(), key=lambda x: x["signal_count"], reverse=True)
                ]
            }

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_cluster_data", e)
            raise ExternalServiceError("Failed to generate cluster data")

    async def validate_address(self, address: str) -> Dict[str, Any]:
        try:
            if not address or len(address.strip()) < 5:
                raise ValidationError("Address must be at least 5 characters")

            geocode_result = await self.geocode_address(address)

            validation = {
                "address": address,
                "is_valid": True,
                "geocoded": geocode_result,
                "confidence": "high" if geocode_result.get("source") == "google_maps" else "medium",
                "issues": []
            }

            if not geocode_result.get("components", {}).get("country"):
                validation["issues"].append("Country not identified")
                validation["is_valid"] = False

            lat = geocode_result.get("latitude", 0)
            lon = geocode_result.get("longitude", 0)
            if lat == 0 and lon == 0:
                validation["issues"].append("Could not determine coordinates")
                validation["is_valid"] = False

            if not geocode_result.get("formatted_address"):
                validation["issues"].append("Could not format address")
                validation["is_valid"] = validation["is_valid"] and False

            validation["confidence"] = "low" if len(validation["issues"]) > 2 else validation["confidence"]

            await self.log_operation("validate_address", {
                "address": address[:50],
                "is_valid": validation["is_valid"],
                "issues_count": len(validation["issues"])
            })

            return validation

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("validate_address", e)
            raise ExternalServiceError("Address validation failed")
