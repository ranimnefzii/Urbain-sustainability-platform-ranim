"""
Category Repository - Urbain Sustainability System
Repository pour la gestion des catégories
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.category import Category, CategoryType, CategoryStatus
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    """
    Repository pour les opérations CRUD sur les catégories
    """
    
    async def get_by_code(self, *, code: str) -> Optional[Category]:
        """
        Récupère une catégorie par son code
        """
        result = await self.db.execute(
            select(Category).where(
                and_(
                    func.upper(Category.code) == code.upper(),
                    Category.status != CategoryStatus.ARCHIVED
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_type(
        self, 
        *, 
        category_type: CategoryType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """
        Récupère les catégories par type
        """
        result = await self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.category_type == category_type,
                    Category.status == CategoryStatus.ACTIVE
                )
            )
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_root_categories(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """
        Récupère les catégories racines (parent_id = NULL)
        """
        result = await self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.parent_id.is_(None),
                    Category.status == CategoryStatus.ACTIVE
                )
            )
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_children(
        self, 
        *, 
        parent_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """
        Récupère les sous-catégories d'une catégorie
        """
        result = await self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.parent_id == parent_id,
                    Category.status == CategoryStatus.ACTIVE
                )
            )
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_tree(self) -> List[Dict[str, Any]]:
        """
        Construit l'arborescence complète des catégories
        """
        # Récupérer toutes les catégories actives
        result = await self.db.execute(
            select(Category)
            .where(Category.status == CategoryStatus.ACTIVE)
            .order_by(Category.sort_order, Category.name)
        )
        categories = result.scalars().all()
        
        # Construire l'arbre
        def build_tree(items, parent_id=None):
            tree = []
            for item in items:
                if item.parent_id == parent_id:
                    children = build_tree(items, item.id)
                    tree.append({
                        "id": item.id,
                        "name": item.name,
                        "code": item.code,
                        "level": item.level,
                        "sort_order": item.sort_order,
                        "category_type": item.category_type.value,
                        "status": item.status.value,
                        "icon": item.icon,
                        "color": item.color,
                        "children": children
                    })
            return tree
        
        return build_tree(categories)
    
    async def search_categories(
        self, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """
        Recherche des catégories par nom ou description
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(Category)
            .where(
                and_(
                    or_(
                        func.lower(Category.name).like(search_pattern),
                        func.lower(Category.description).like(search_pattern),
                        func.lower(Category.code).like(search_pattern)
                    ),
                    Category.status != CategoryStatus.ARCHIVED
                )
            )
            .order_by(Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_categories_with_signals_count(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les catégories avec le nombre de signalements associés
        """
        from app.models.signal import Signal
        
        result = await self.db.execute(
            select(
                Category.id,
                Category.name,
                Category.code,
                Category.category_type,
                Category.level,
                Category.parent_id,
                func.count(Signal.id).label("signals_count")
            )
            .outerjoin(Signal, Category.id == Signal.category_id)
            .where(Category.status == CategoryStatus.ACTIVE)
            .group_by(Category.id)
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "code": row.code,
                "category_type": row.category_type.value,
                "level": row.level,
                "parent_id": row.parent_id,
                "signals_count": row.signals_count
            }
            for row in result
        ]
    
    async def check_code_exists(self, *, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un code de catégorie existe déjà
        """
        query = select(func.count(Category.id)).where(
            func.upper(Category.code) == code.upper()
        )
        
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def check_name_exists(self, *, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un nom de catégorie existe déjà
        """
        query = select(func.count(Category.id)).where(
            func.lower(Category.name) == name.lower()
        )
        
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def get_categories_by_level(
        self, 
        *, 
        level: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """
        Récupère les catégories par niveau
        """
        result = await self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.level == level,
                    Category.status == CategoryStatus.ACTIVE
                )
            )
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_sort_order(self, *, category_id: int, new_order: int) -> bool:
        """
        Met à jour l'ordre de tri d'une catégorie
        """
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if category:
            category.sort_order = new_order
            await self.db.commit()
            return True
        return False
    
    async def bulk_update_sort_order(self, *, updates: List[Dict[str, int]]) -> int:
        """
        Met à jour l'ordre de tri de plusieurs catégories
        """
        updated_count = 0
        for update in updates:
            if "id" in update and "sort_order" in update:
                result = await self.db.execute(
                    select(Category).where(Category.id == update["id"])
                )
                category = result.scalar_one_or_none()
                
                if category:
                    category.sort_order = update["sort_order"]
                    updated_count += 1
        
        if updated_count > 0:
            await self.db.commit()
        
        return updated_count
    
    async def get_category_statistics(self, *, category_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une catégorie
        """
        from app.models.signal import Signal
        
        # Statistiques de base
        category = await self.get(id=category_id)
        if not category:
            return {}
        
        # Statistiques des signalements
        signals_query = select(func.count(Signal.id)).where(Signal.category_id == category_id)
        signals_result = await self.db.execute(signals_query)
        total_signals = signals_result.scalar()
        
        # Statistiques par statut
        status_query = select(
            Signal.status,
            func.count(Signal.id).label("count")
        ).where(Signal.category_id == category_id).group_by(Signal.status)
        
        status_result = await self.db.execute(status_query)
        status_stats = {row.status.value: row.count for row in status_result}
        
        return {
            "category_id": category_id,
            "name": category.name,
            "code": category.code,
            "category_type": category.category_type.value,
            "level": category.level,
            "total_signals": total_signals,
            "signals_by_status": status_stats,
            "ai_confidence_threshold": category.ai_confidence_threshold,
            "default_priority_level": category.default_priority_level,
            "auto_assignment_enabled": category.auto_assignment_enabled,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }
    
    async def get_most_used_categories(
        self, 
        *, 
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Récupère les catégories les plus utilisées
        """
        from datetime import datetime, timedelta
        from app.models.signal import Signal
        
        start_date = datetime.now() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                Category.id,
                Category.name,
                Category.code,
                func.count(Signal.id).label("usage_count")
            )
            .join(Signal, Category.id == Signal.category_id)
            .where(
                and_(
                    Signal.created_at >= start_date,
                    Category.status == CategoryStatus.ACTIVE
                )
            )
            .group_by(Category.id)
            .order_by(desc("usage_count"))
            .limit(limit)
        )
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "code": row.code,
                "usage_count": row.usage_count
            }
            for row in result
        ]
    
    async def archive_category(self, *, category_id: int) -> bool:
        """
        Archive une catégorie (change le statut mais ne supprime pas)
        """
        from sqlalchemy import update
        
        stmt = (
            update(Category)
            .where(Category.id == category_id)
            .values(status=CategoryStatus.ARCHIVED)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def restore_category(self, *, category_id: int) -> bool:
        """
        Restaure une catégorie archivée
        """
        from sqlalchemy import update
        
        stmt = (
            update(Category)
            .where(Category.id == category_id)
            .values(status=CategoryStatus.ACTIVE)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def get_categories_for_sector(
        self, 
        *, 
        sector_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        """
        Récupère les catégories supportées par un secteur
        """
        # Utiliser une requête JSON pour vérifier si le secteur est dans supported_categories
        result = await self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.status == CategoryStatus.ACTIVE,
                    # Logic pour vérifier si sector_id est dans supported_categories
                    # (à adapter selon la structure JSON de SQLAlchemy)
                    func.jsonb_contains(Category.supported_categories, str(sector_id))
                )
            )
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
