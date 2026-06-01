"""
Category Service - Urbain Sustainability System
Service métier pour la gestion des catégories
"""

import structlog
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.services.base import BaseService
from app.models.category import Category, CategoryType, CategoryStatus
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories import CategoryRepository
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    BusinessLogicError, ConflictError
)

logger = structlog.get_logger()


class CategoryService(BaseService[Category, CategoryCreate, CategoryUpdate]):
    """
    Service métier pour la gestion des catégories de signalements
    Gère la hiérarchie parent-enfant et les configurations par catégorie
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = CategoryRepository(db, Category)

    async def create_category(self, obj_in: CategoryCreate) -> Category:
        try:
            code_exists = await self.repository.check_code_exists(code=obj_in.code)
            if code_exists:
                raise ConflictError(f"Category code '{obj_in.code}' already exists")

            name_exists = await self.repository.check_name_exists(name=obj_in.name)
            if name_exists:
                raise ConflictError(f"Category name '{obj_in.name}' already exists")

            if obj_in.parent_id:
                parent = await self.repository.get(id=obj_in.parent_id)
                if not parent:
                    raise NotFoundError(f"Parent category with id {obj_in.parent_id} not found")
                if parent.status == CategoryStatus.ARCHIVED:
                    raise BusinessLogicError("Cannot create subcategory under an archived category")

            obj_data = obj_in.model_dump()
            obj_data["category_type"] = CategoryType(obj_in.category_type)

            if obj_in.parent_id:
                parent = await self.repository.get(id=obj_in.parent_id)
                obj_data["level"] = parent.level + 1 if parent else 1
            else:
                obj_data["level"] = 1

            category = Category(**obj_data)
            self.db.add(category)
            await self.db.commit()
            await self.db.refresh(category)

            await self.log_operation("create_category", {"category_id": category.id, "code": category.code})
            return category
        except (ConflictError, NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("create_category", e)
            raise DatabaseError(f"Failed to create category: {str(e)}")

    async def get_category(self, category_id: int) -> Category:
        try:
            category = await self.repository.get(id=category_id)
            if not category:
                raise NotFoundError(f"Category with id {category_id} not found")
            return category
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_category", e, {"category_id": category_id})
            raise DatabaseError(f"Failed to get category: {str(e)}")

    async def update_category(self, category_id: int, obj_in: CategoryUpdate) -> Category:
        try:
            category = await self.get_category(category_id)
            update_data = obj_in.model_dump(exclude_unset=True)

            if "code" in update_data:
                code_exists = await self.repository.check_code_exists(code=update_data["code"], exclude_id=category_id)
                if code_exists:
                    raise ConflictError(f"Category code '{update_data['code']}' already exists")

            if "name" in update_data:
                name_exists = await self.repository.check_name_exists(name=update_data["name"], exclude_id=category_id)
                if name_exists:
                    raise ConflictError(f"Category name '{update_data['name']}' already exists")

            if "parent_id" in update_data and update_data["parent_id"] is not None:
                if update_data["parent_id"] == category_id:
                    raise BusinessLogicError("Category cannot be its own parent")

                new_parent = await self.repository.get(id=update_data["parent_id"])
                if not new_parent:
                    raise NotFoundError(f"Parent category with id {update_data['parent_id']} not found")

                children_ids = await self._get_all_descendant_ids(category_id)
                if update_data["parent_id"] in children_ids:
                    raise BusinessLogicError("Cannot set a descendant as parent (circular reference)")

                update_data["level"] = new_parent.level + 1

            for field, value in update_data.items():
                if hasattr(category, field):
                    setattr(category, field, value)

            await self.db.commit()
            await self.db.refresh(category)

            await self.log_operation("update_category", {"category_id": category_id})
            return category
        except (NotFoundError, ConflictError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("update_category", e, {"category_id": category_id})
            raise DatabaseError(f"Failed to update category: {str(e)}")

    async def delete_category(self, category_id: int) -> bool:
        try:
            category = await self.get_category(category_id)

            children = await self.repository.get_children(parent_id=category_id)
            if children:
                raise BusinessLogicError(
                    f"Cannot delete category with {len(children)} subcategories. "
                    "Delete or reassign subcategories first."
                )

            from app.models.signal import Signal
            signal_count_query = select(func.count(Signal.id)).where(Signal.category_id == category_id)
            signal_count_result = await self.db.execute(signal_count_query)
            if signal_count_result.scalar() > 0:
                raise BusinessLogicError(
                    "Cannot delete category with associated signals. Archive it instead."
                )

            await self.repository.remove(id=category_id)
            await self.log_operation("delete_category", {"category_id": category_id})
            return True
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("delete_category", e, {"category_id": category_id})
            raise DatabaseError(f"Failed to delete category: {str(e)}")

    async def get_categories(self, skip: int = 0, limit: int = 100,
                              filters: Optional[Dict[str, Any]] = None) -> List[Category]:
        try:
            return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)
        except Exception as e:
            await self.log_error("get_categories", e)
            raise DatabaseError(f"Failed to get categories: {str(e)}")

    async def get_category_tree(self) -> List[Dict[str, Any]]:
        try:
            return await self.repository.get_tree()
        except Exception as e:
            await self.log_error("get_category_tree", e)
            raise DatabaseError(f"Failed to get category tree: {str(e)}")

    async def get_category_stats(self, category_id: int) -> Dict[str, Any]:
        try:
            category = await self.get_category(category_id)
            stats = await self.repository.get_category_statistics(category_id=category_id)
            children = await self.repository.get_children(parent_id=category_id)

            stats["subcategories_count"] = len(children)
            stats["children"] = [
                {"id": c.id, "name": c.name, "code": c.code, "level": c.level}
                for c in children
            ]
            return stats
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_category_stats", e, {"category_id": category_id})
            raise DatabaseError(f"Failed to get category stats: {str(e)}")

    async def get_subcategories(self, parent_id: int, skip: int = 0, limit: int = 100) -> List[Category]:
        try:
            parent = await self.get_category(parent_id)
            return await self.repository.get_children(parent_id=parent_id, skip=skip, limit=limit)
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_subcategories", e, {"parent_id": parent_id})
            raise DatabaseError(f"Failed to get subcategories: {str(e)}")

    async def get_parent_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        try:
            return await self.repository.get_root_categories(skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("get_parent_categories", e)
            raise DatabaseError(f"Failed to get parent categories: {str(e)}")

    async def get_categories_by_type(self, category_type: str, skip: int = 0, limit: int = 100) -> List[Category]:
        try:
            try:
                ct = CategoryType(category_type)
            except ValueError:
                raise ValidationError(f"Invalid category type: {category_type}")
            return await self.repository.get_by_type(category_type=ct, skip=skip, limit=limit)
        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("get_categories_by_type", e, {"category_type": category_type})
            raise DatabaseError(f"Failed to get categories by type: {str(e)}")

    async def _get_all_descendant_ids(self, category_id: int) -> List[int]:
        descendants = []
        children = await self.repository.get_children(parent_id=category_id)
        for child in children:
            descendants.append(child.id)
            grandchildren = await self._get_all_descendant_ids(child.id)
            descendants.extend(grandchildren)
        return descendants
