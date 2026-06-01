"""
Base Repository - Urbain Sustainability System
Repository de base implémentant le pattern Repository
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Repository de base avec méthodes CRUD génériques
    Implémente le pattern Repository pour l'accès aux données
    """
    
    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model
    
    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Crée un nouvel enregistrement
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get(self, id: int) -> Optional[ModelType]:
        """
        Récupère un enregistrement par son ID
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Récupère plusieurs enregistrements avec pagination et filtres
        """
        query = select(self.model)
        
        # Application des filtres
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        # Application du tri
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        
        # Application de la pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_all(self) -> List[ModelType]:
        """
        Récupère tous les enregistrements
        """
        result = await self.db.execute(select(self.model))
        return result.scalars().all()
    
    async def update(
        self, 
        *, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Met à jour un enregistrement
        """
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def remove(self, *, id: int) -> ModelType:
        """
        Supprime un enregistrement par son ID
        """
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
    
    async def delete(self, *, id: int) -> bool:
        """
        Supprime un enregistrement par son ID (retourne booléen)
        """
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Compte le nombre d'enregistrements avec filtres optionnels
        """
        query = select(func.count(self.model.id))
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def exists(self, *, id: int) -> bool:
        """
        Vérifie si un enregistrement existe
        """
        result = await self.db.execute(
            select(func.count(self.model.id)).where(self.model.id == id)
        )
        return result.scalar() > 0
    
    async def get_by_field(
        self, 
        *, 
        field_name: str, 
        field_value: Any
    ) -> Optional[ModelType]:
        """
        Récupère un enregistrement par un champ spécifique
        """
        if not hasattr(self.model, field_name):
            return None
        
        query = select(self.model).where(
            getattr(self.model, field_name) == field_value
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_with_relations(
        self, 
        *, 
        id: int, 
        relations: List[str] = None
    ) -> Optional[ModelType]:
        """
        Récupère un enregistrement avec ses relations chargées
        """
        query = select(self.model)
        
        if relations:
            for relation in relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))
        
        query = query.where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def search(
        self, 
        *, 
        search_term: str, 
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Recherche des enregistrements sur plusieurs champs
        """
        if not search_fields:
            return []
        
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                field_attr = getattr(self.model, field)
                search_conditions.append(
                    func.lower(field_attr).like(f"%{search_term.lower()}%")
                )
        
        if not search_conditions:
            return []
        
        query = select(self.model).where(or_(*search_conditions))
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def bulk_create(self, *, objects_in: List[CreateSchemaType]) -> List[ModelType]:
        """
        Crée plusieurs enregistrements en masse
        """
        db_objects = []
        for obj_in in objects_in:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db_objects.append(db_obj)
        
        self.db.add_all(db_objects)
        await self.db.commit()
        
        # Refresh tous les objets
        for db_obj in db_objects:
            await self.db.refresh(db_obj)
        
        return db_objects
    
    async def bulk_update(
        self, 
        *, 
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        Met à jour plusieurs enregistrements en masse
        """
        updated_count = 0
        for update_data in updates:
            if 'id' in update_data:
                query = (
                    update(self.model)
                    .where(self.model.id == update_data['id'])
                    .values(**{k: v for k, v in update_data.items() if k != 'id'})
                )
                result = await self.db.execute(query)
                updated_count += result.rowcount
        
        await self.db.commit()
        return updated_count
    
    async def bulk_delete(self, *, ids: List[int]) -> int:
        """
        Supprime plusieurs enregistrements en masse
        """
        result = await self.db.execute(
            delete(self.model).where(self.model.id.in_(ids))
        )
        await self.db.commit()
        return result.rowcount
    
    async def get_paginated(
        self,
        *,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Récupère des enregistrements paginés avec métadonnées
        """
        skip = (page - 1) * size
        
        # Compte total
        total = await self.count(filters)
        
        # Récupère les données
        items = await self.get_multi(
            skip=skip, 
            limit=size, 
            filters=filters, 
            order_by=order_by
        )
        
        pages = (total + size - 1) // size
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    
    async def get_latest(
        self, 
        *, 
        limit: int = 10,
        order_field: str = "created_at"
    ) -> List[ModelType]:
        """
        Récupère les derniers enregistrements
        """
        if not hasattr(self.model, order_field):
            order_field = "id"
        
        query = select(self.model).order_by(
            getattr(self.model, order_field).desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne des statistiques de base pour le modèle
        """
        total_count = await self.count()
        
        return {
            "total_count": total_count,
            "model_name": self.model.__name__,
            "table_name": self.model.__tablename__
        }
