"""
User Service - Urbain Sustainability System
Service métier pour la gestion des utilisateurs
"""

import structlog
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.services.base import BaseService
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserPasswordChange, UserPasswordReset, UserEmailVerification
from app.repositories.user_repository import UserRepository
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, BusinessLogicError, DatabaseError, AuthorizationError
from app.core.security import get_password_hash, verify_password

logger = structlog.get_logger()


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    Service métier pour la gestion des utilisateurs
    Gère l'authentification, les profils et les préférences
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = UserRepository(db, User)

    async def create_user(self, obj_in: UserCreate) -> User:
        try:
            existing = await self.repository.get_by_email_or_username(
                email=obj_in.email, username=obj_in.username
            )
            if existing:
                if existing.email.lower() == obj_in.email.lower():
                    raise ConflictError("Email already registered")
                raise ConflictError("Username already taken")

            obj_data = obj_in.model_dump(exclude={"confirm_password", "password"})
            obj_data["hashed_password"] = get_password_hash(obj_in.password)
            obj_data["email_verification_token"] = str(uuid.uuid4())
            obj_data["is_email_verified"] = False
            obj_data["status"] = UserStatus.PENDING_VERIFICATION

            user = User(**obj_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("create_user", {"user_id": user.id, "email": user.email})
            return user
        except ConflictError:
            raise
        except Exception as e:
            await self.log_error("create_user", e)
            raise DatabaseError(f"Failed to create user: {str(e)}")

    async def get_user(self, user_id: int) -> User:
        try:
            user = await self.repository.get(id=user_id)
            if not user:
                raise NotFoundError(f"User with id {user_id} not found")
            return user
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_user", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to get user: {str(e)}")

    async def update_user(self, user_id: int, obj_in: UserUpdate, current_user_id: int) -> User:
        try:
            user = await self.get_user(user_id)

            if current_user_id != user_id:
                current_user = await self.get_user(current_user_id)
                if current_user.role != UserRole.ADMIN:
                    raise AuthorizationError("Not authorized to update this user")

            update_data = obj_in.model_dump(exclude_unset=True)

            if "email" in update_data:
                if update_data["email"].lower() != user.email.lower():
                    exists = await self.repository.check_email_exists(email=update_data["email"], exclude_id=user_id)
                    if exists:
                        raise ConflictError("Email already in use")
                    update_data["is_email_verified"] = False
                    update_data["email_verification_token"] = str(uuid.uuid4())

            if "phone_number" in update_data and update_data["phone_number"]:
                update_data["is_phone_verified"] = False

            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("update_user", {"user_id": user_id})
            return user
        except (NotFoundError, AuthorizationError, ConflictError):
            raise
        except Exception as e:
            await self.log_error("update_user", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to update user: {str(e)}")

    async def delete_user(self, user_id: int, current_user_id: int) -> bool:
        try:
            user = await self.get_user(user_id)

            if current_user_id != user_id:
                current_user = await self.get_user(current_user_id)
                if current_user.role != UserRole.ADMIN:
                    raise AuthorizationError("Not authorized to delete this user")

            if user.role == UserRole.ADMIN:
                admin_count = await self.db.execute(
                    select(func.count(User.id)).where(User.role == UserRole.ADMIN, User.status == UserStatus.ACTIVE)
                )
                if admin_count.scalar() <= 1:
                    raise BusinessLogicError("Cannot delete the last active admin")

            await self.repository.remove(id=user_id)
            await self.log_operation("delete_user", {"user_id": user_id})
            return True
        except (NotFoundError, AuthorizationError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("delete_user", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to delete user: {str(e)}")

    async def get_users(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[User]:
        try:
            return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)
        except Exception as e:
            await self.log_error("get_users", e)
            raise DatabaseError(f"Failed to get users: {str(e)}")

    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            return await self.repository.search_users(search_term=search_term, skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("search_users", e, {"search_term": search_term})
            raise DatabaseError(f"Failed to search users: {str(e)}")

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        try:
            user = await self.get_user(user_id)
            stats = await self.repository.get_user_statistics(user_id=user_id)

            from app.models.signal import Signal, SignalStatus

            signals_by_status_query = select(
                Signal.status, func.count(Signal.id).label("count")
            ).where(
                Signal.created_by == user_id
            ).group_by(Signal.status)
            status_result = await self.db.execute(signals_by_status_query)
            signals_by_status = {row.status.value: row.count for row in status_result}

            signals_by_category_query = select(
                Signal.category_id, func.count(Signal.id).label("count")
            ).where(
                Signal.created_by == user_id
            ).group_by(Signal.category_id)
            category_result = await self.db.execute(signals_by_category_query)
            signals_by_category = {row.category_id: row.count for row in category_result}

            activity = await self.repository.get_user_activity(user_id=user_id)

            stats.update({
                "signals_by_status": signals_by_status,
                "signals_by_category": signals_by_category,
                "recent_activity": activity
            })
            return stats
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_user_stats", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to get user stats: {str(e)}")

    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            return await self.repository.get_by_role(role=role, skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("get_by_role", e, {"role": role.value if hasattr(role, 'value') else str(role)})
            raise DatabaseError(f"Failed to get users by role: {str(e)}")

    async def get_by_status(self, status: UserStatus, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            return await self.repository.get_multi(skip=skip, limit=limit, filters={"status": status})
        except Exception as e:
            await self.log_error("get_by_status", e, {"status": status.value if hasattr(status, 'value') else str(status)})
            raise DatabaseError(f"Failed to get users by status: {str(e)}")

    async def verify_email(self, token: str) -> User:
        try:
            user = await self.repository.get_by_verification_token(token=token)
            if not user:
                raise ValidationError("Invalid or expired verification token")

            user.is_email_verified = True
            user.email_verification_token = None
            if user.status == UserStatus.PENDING_VERIFICATION:
                user.status = UserStatus.ACTIVE
            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("verify_email", {"user_id": user.id})
            return user
        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("verify_email", e)
            raise DatabaseError(f"Failed to verify email: {str(e)}")

    async def update_password(self, user_id: int, current_password: str, new_password: str) -> User:
        try:
            user = await self.get_user(user_id)

            if not verify_password(current_password, user.hashed_password):
                raise ValidationError("Current password is incorrect")

            if len(new_password) < 8:
                raise ValidationError("Password must be at least 8 characters")

            user.hashed_password = get_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("update_password", {"user_id": user_id})
            return user
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("update_password", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to update password: {str(e)}")

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            return await self.repository.get_by_email(email=email)
        except Exception as e:
            await self.log_error("get_by_email", e, {"email": email})
            raise DatabaseError(f"Failed to get user by email: {str(e)}")

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            return await self.repository.get_by_username(username=username)
        except Exception as e:
            await self.log_error("get_by_username", e, {"username": username})
            raise DatabaseError(f"Failed to get user by username: {str(e)}")

    async def update_notification_preferences(self, user_id: int, preferences: Dict[str, Any]) -> User:
        try:
            user = await self.get_user(user_id)

            if "email_notifications_enabled" in preferences:
                user.email_notifications_enabled = preferences["email_notifications_enabled"]
            if "sms_notifications_enabled" in preferences:
                user.sms_notifications_enabled = preferences["sms_notifications_enabled"]
            if "push_notifications_enabled" in preferences:
                user.push_notifications_enabled = preferences["push_notifications_enabled"]
            if "preferred_language" in preferences:
                user.preferred_language = preferences["preferred_language"]

            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("update_notification_preferences", {"user_id": user_id})
            return user
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("update_notification_preferences", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to update notification preferences: {str(e)}")

    async def activate_user(self, user_id: int) -> User:
        try:
            user = await self.get_user(user_id)
            if user.status == UserStatus.ACTIVE:
                raise BusinessLogicError("User is already active")

            user.status = UserStatus.ACTIVE
            user.is_email_verified = True
            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("activate_user", {"user_id": user_id})
            return user
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("activate_user", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to activate user: {str(e)}")

    async def deactivate_user(self, user_id: int) -> User:
        try:
            user = await self.get_user(user_id)
            if user.status == UserStatus.INACTIVE:
                raise BusinessLogicError("User is already inactive")

            if user.role == UserRole.ADMIN:
                admin_count = await self.db.execute(
                    select(func.count(User.id)).where(User.role == UserRole.ADMIN, User.status == UserStatus.ACTIVE)
                )
                if admin_count.scalar() <= 1:
                    raise BusinessLogicError("Cannot deactivate the last active admin")

            user.status = UserStatus.INACTIVE
            await self.db.commit()
            await self.db.refresh(user)

            await self.log_operation("deactivate_user", {"user_id": user_id})
            return user
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("deactivate_user", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to deactivate user: {str(e)}")

    async def get_user_signals(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Any]:
        try:
            user = await self.get_user(user_id)
            from app.repositories import SignalRepository
            from app.models.signal import Signal
            signal_repo = SignalRepository(self.db, Signal)
            return await signal_repo.get_by_user(user_id=user_id, skip=skip, limit=limit)
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_user_signals", e, {"user_id": user_id})
            raise DatabaseError(f"Failed to get user signals: {str(e)}")
