"""
User Repository - Urbain Sustainability System
Repository pour la gestion des utilisateurs
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repository pour les opérations CRUD sur les utilisateurs
    """
    
    async def get_by_email(self, *, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email
        """
        result = await self.db.execute(
            select(User).where(
                and_(
                    func.lower(User.email) == email.lower(),
                    User.status != UserStatus.INACTIVE
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, *, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur
        """
        result = await self.db.execute(
            select(User).where(
                and_(
                    func.lower(User.username) == username.lower(),
                    User.status != UserStatus.INACTIVE
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email_or_username(self, *, email: str, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par email ou nom d'utilisateur
        """
        result = await self.db.execute(
            select(User).where(
                and_(
                    or_(
                        func.lower(User.email) == email.lower(),
                        func.lower(User.username) == username.lower()
                    ),
                    User.status != UserStatus.INACTIVE
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_verification_token(self, *, token: str) -> Optional[User]:
        """
        Récupère un utilisateur par son token de vérification email
        """
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.email_verification_token == token,
                    User.is_email_verified == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_reset_token(self, *, token: str) -> Optional[User]:
        """
        Récupère un utilisateur par son token de réinitialisation
        """
        result = await self.db.execute(
            select(User).where(User.password_reset_token == token)
        )
        return result.scalar_one_or_none()
    
    async def get_by_role(
        self, 
        *, 
        role: UserRole, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs par rôle
        """
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.role == role,
                    User.status == UserStatus.ACTIVE
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_active_users(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs actifs
        """
        result = await self.db.execute(
            select(User)
            .where(User.status == UserStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    async def search_users(
        self, 
        *, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Recherche des utilisateurs par nom, email ou username
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    or_(
                        func.lower(User.first_name).like(search_pattern),
                        func.lower(User.last_name).like(search_pattern),
                        func.lower(User.email).like(search_pattern),
                        func.lower(User.username).like(search_pattern)
                    ),
                    User.status != UserStatus.INACTIVE
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(User.first_name, User.last_name)
        )
        return result.scalars().all()
    
    async def get_users_by_city(
        self, 
        *, 
        city: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs par ville
        """
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    func.lower(User.city) == city.lower(),
                    User.status == UserStatus.ACTIVE
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    async def check_email_exists(self, *, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un email existe déjà
        """
        query = select(func.count(User.id)).where(
            func.lower(User.email) == email.lower()
        )
        
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def check_username_exists(self, *, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un nom d'utilisateur existe déjà
        """
        query = select(func.count(User.id)).where(
            func.lower(User.username) == username.lower()
        )
        
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def create_with_verification(
        self, 
        *, 
        obj_in: UserCreate, 
        verification_token: str
    ) -> User:
        """
        Crée un utilisateur avec token de vérification
        """
        obj_data = obj_in.model_dump()
        obj_data["email_verification_token"] = verification_token
        obj_data["is_email_verified"] = False
        
        db_obj = User(**obj_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_last_login(self, *, user_id: int) -> bool:
        """
        Met à jour la date de dernière connexion
        """
        from datetime import datetime
        
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.last_login_at = datetime.now()
            await self.db.commit()
            return True
        return False
    
    async def update_verification_status(self, *, user_id: int) -> bool:
        """
        Met à jour le statut de vérification email
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_email_verified = True
            user.email_verification_token = None
            await self.db.commit()
            return True
        return False
    
    async def update_password_reset_token(
        self, 
        *, 
        user_id: int, 
        token: str, 
        expires_hours: int = 24
    ) -> bool:
        """
        Met à jour le token de réinitialisation de mot de passe
        """
        from datetime import datetime, timedelta
        
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.password_reset_token = token
            user.password_reset_expires = datetime.now() + timedelta(hours=expires_hours)
            await self.db.commit()
            return True
        return False
    
    async def clear_password_reset_token(self, *, user_id: int) -> bool:
        """
        Efface le token de réinitialisation de mot de passe
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.password_reset_token = None
            user.password_reset_expires = None
            await self.db.commit()
            return True
        return False
    
    async def update_password(self, *, user_id: int, hashed_password: str) -> bool:
        """
        Met à jour le mot de passe d'un utilisateur
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.hashed_password = hashed_password
            user.password_reset_token = None
            user.password_reset_expires = None
            await self.db.commit()
            return True
        return False
    
    async def update_phone_verification(
        self, 
        *, 
        user_id: int, 
        is_verified: bool = True
    ) -> bool:
        """
        Met à jour le statut de vérification téléphone
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_phone_verified = is_verified
            user.phone_verification_code = None
            await self.db.commit()
            return True
        return False
    
    async def get_user_statistics(self, *, user_id: int) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un utilisateur
        """
        from app.models.signal import Signal
        from app.models.notification import Notification
        
        # Statistiques de base
        user = await self.get(id=user_id)
        if not user:
            return {}
        
        # Statistiques des signalements
        signals_query = select(func.count(Signal.id)).where(Signal.created_by == user_id)
        signals_result = await self.db.execute(signals_query)
        total_signals = signals_result.scalar()
        
        # Statistiques des notifications
        notifications_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        notifications_result = await self.db.execute(notifications_query)
        total_notifications = notifications_result.scalar()
        
        return {
            "user_id": user_id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "is_email_verified": user.is_email_verified,
            "is_phone_verified": user.is_phone_verified,
            "total_signals_created": user.total_signals_created,
            "total_signals_processed": user.total_signals_processed,
            "calculated_total_signals": total_signals,
            "total_notifications": total_notifications,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at
        }
    
    async def get_user_activity(
        self, 
        *, 
        user_id: int, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Récupère l'activité récente d'un utilisateur
        """
        from datetime import datetime, timedelta
        from app.models.signal import Signal
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Signalements récents
        signals_query = (
            select(Signal)
            .where(
                and_(
                    Signal.created_by == user_id,
                    Signal.created_at >= start_date
                )
            )
            .order_by(Signal.created_at.desc())
        )
        
        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()
        
        activity = []
        for signal in signals:
            activity.append({
                "type": "signal_created",
                "signal_id": signal.id,
                "title": signal.title,
                "status": signal.status.value,
                "created_at": signal.created_at.isoformat(),
                "description": "Signal created"
            })
        
        return activity
    
    async def bulk_update_status(
        self, 
        *, 
        user_ids: List[int], 
        status: UserStatus
    ) -> int:
        """
        Met à jour le statut de plusieurs utilisateurs
        """
        from sqlalchemy import update
        
        stmt = (
            update(User)
            .where(User.id.in_(user_ids))
            .values(status=status)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def get_users_by_sector(
        self, 
        *, 
        sector_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs d'un secteur
        """
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.sector_id == sector_id,
                    User.status == UserStatus.ACTIVE
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(User.first_name, User.last_name)
        )
        return result.scalars().all()
    
    async def deactivate_inactive_users(self, *, days: int = 365) -> int:
        """
        Désactive les utilisateurs inactifs depuis X jours
        """
        from datetime import datetime, timedelta
        from sqlalchemy import update
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        stmt = (
            update(User)
            .where(
                and_(
                    User.last_login_at < cutoff_date,
                    User.status == UserStatus.ACTIVE
                )
            )
            .values(status=UserStatus.INACTIVE)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
