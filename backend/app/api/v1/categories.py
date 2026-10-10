"""
Categories Routes - Urbain Sustainability System
Routes de gestion des catégories de signalements
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryTree, CategoryStats
)
from app.services.category_service import CategoryService
from app.core.exceptions import (
    NotFoundError, ValidationError, DatabaseError
)
from app.utils.helpers import Paginator

logger = structlog.get_logger()
router = APIRouter()


def _serialize_category(cat) -> Dict[str, Any]:
    cols = ["id", "name", "code", "description", "parent_id", "level", "sort_order",
            "icon", "color", "marker_icon", "default_priority_level", "default_severity_level",
            "ai_confidence_threshold", "requires_image_verification", "default_processing_time_hours",
            "auto_assignment_enabled", "requires_approval", "responsible_sectors",
            "escalation_sectors", "auto_notify_citizen", "auto_notify_sector",
            "required_fields", "optional_fields", "validation_rules",
            "total_signals", "avg_resolution_time_hours", "satisfaction_rate",
            "created_at", "updated_at"]
    result = {}
    for c in cols:
        val = getattr(cat, c, None)
        if hasattr(val, 'value'):
            val = val.value
        result[c] = val
    result["category_type"] = cat.category_type.value if hasattr(cat.category_type, 'value') else cat.category_type
    result["status"] = cat.status.value if hasattr(cat.status, 'value') else cat.status
    return result


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new signal category (admin only)"
)
async def create_category(
    data: CategoryCreate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        result = await category_service.create_category(obj_in=data)
        return {
            "success": True,
            "message": f"Category '{result.name}' created successfully",
            "data": _serialize_category(result)
        }
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Create category failed", error=str(e))
        raise ValidationError("Failed to create category")


@router.get(
    "",
    response_model=dict,
    summary="List all categories",
    description="Get all categories with optional filtering"
)
async def list_categories(
    category_type: Optional[str] = Query(None, description="Filter by type"),
    parent_id: Optional[int] = Query(None, description="Filter by parent"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        filters = {}
        if category_type:
            filters["category_type"] = category_type
        if parent_id is not None:
            filters["parent_id"] = parent_id
        categories = await category_service.get_categories(skip=0, limit=100, filters=filters)
        return {
            "success": True,
            "message": "Categories retrieved successfully",
            "data": [_serialize_category(c) for c in categories]
        }
    except Exception as e:
        logger.error("List categories failed", error=str(e))
        raise DatabaseError("Failed to retrieve categories")


@router.get(
    "/tree",
    response_model=dict,
    summary="Get category hierarchy tree",
    description="Get the full hierarchical tree of categories"
)
async def get_category_tree(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        tree = await category_service.get_category_tree()
        return {
            "success": True,
            "message": "Category tree retrieved",
            "data": tree
        }
    except Exception as e:
        logger.error("Get category tree failed", error=str(e))
        raise DatabaseError("Failed to retrieve category tree")


@router.get(
    "/by-type/{category_type}",
    response_model=dict,
    summary="Get categories by type",
    description="Get all categories of a specific type"
)
async def get_categories_by_type(
    category_type: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        categories = await category_service.get_categories_by_type(category_type=category_type)
        return {
            "success": True,
            "message": f"Categories of type {category_type} retrieved",
            "data": [_serialize_category(c) for c in categories]
        }
    except Exception as e:
        logger.error("Get categories by type failed", error=str(e))
        raise DatabaseError("Failed to retrieve categories by type")


@router.get(
    "/{category_id}",
    response_model=dict,
    summary="Get category details",
    description="Get detailed information about a specific category"
)
async def get_category(
    category_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        category = await category_service.get_category(category_id=category_id)
        if not category:
            raise NotFoundError(f"Category with id {category_id} not found")
        return {
            "success": True,
            "message": "Category retrieved successfully",
            "data": _serialize_category(category)
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get category failed", error=str(e))
        raise NotFoundError(f"Category with id {category_id} not found")


@router.put(
    "/{category_id}",
    response_model=dict,
    summary="Update category",
    description="Update a category's details (admin only)"
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        updated = await category_service.update_category(category_id=category_id, obj_in=data)
        if not updated:
            raise NotFoundError(f"Category with id {category_id} not found")
        return {
            "success": True,
            "message": "Category updated successfully",
            "data": _serialize_category(updated)
        }
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Update category failed", error=str(e))
        raise ValidationError("Failed to update category")


@router.delete(
    "/{category_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete category",
    description="Delete a category (admin only)"
)
async def delete_category(
    category_id: int,
    current_user = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        deleted = await category_service.delete_category(category_id=category_id)
        if not deleted:
            raise NotFoundError(f"Category with id {category_id} not found")
        return {
            "success": True,
            "message": "Category deleted successfully"
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Delete category failed", error=str(e))
        raise NotFoundError(f"Category with id {category_id} not found")


@router.get(
    "/{category_id}/subcategories",
    response_model=dict,
    summary="Get subcategories",
    description="Get all direct subcategories of a category"
)
async def get_subcategories(
    category_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        subcategories = await category_service.get_subcategories(parent_id=category_id)
        return {
            "success": True,
            "message": "Subcategories retrieved successfully",
            "data": [_serialize_category(s) for s in subcategories]
        }
    except Exception as e:
        logger.error("Get subcategories failed", error=str(e))
        raise DatabaseError("Failed to retrieve subcategories")


@router.get(
    "/{category_id}/stats",
    response_model=dict,
    summary="Get category statistics",
    description="Get statistics for a specific category"
)
async def get_category_stats(
    category_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        category_service = CategoryService(db)
        stats = await category_service.get_category_stats(category_id=category_id)
        if not stats:
            raise NotFoundError(f"Category with id {category_id} not found")
        return {
            "success": True,
            "message": "Category statistics retrieved",
            "data": stats
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get category stats failed", error=str(e))
        raise DatabaseError("Failed to retrieve category statistics")
