"""
Auth Service - Urbain Sustainability System
Service d'authentification avec gestion des tokens JWT
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import structlog

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    DatabaseError
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_user
)
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserLogin, UserRegister, UserPasswordChange
from app.utils.validators import validate_email, validate_password
from app.services.base import BaseService

logger = structlog.get_logger()


class AuthService(BaseService):
    """
    Service d'authentification et gestion des comptes utilisateurs
    Gère l'inscription, connexion, tokens JWT et vérification email
    """

    def __init__(self, db):
        super().__init__(db)
        self.user_repo = UserRepository(db, User)

    async def register(self, user_data: UserRegister) -> Dict[str, Any]:
        try:
            validated_email = validate_email(user_data.email)
            validate_password(user_data.password)

            existing = await self.user_repo.get_by_email_or_username(
                email=validated_email,
                username=user_data.username
            )
            if existing:
                if existing.email.lower() == validated_email.lower():
                    raise ConflictError("Email already registered")
                raise ConflictError("Username already taken")

            email_exists = await self.user_repo.check_email_exists(email=validated_email)
            if email_exists:
                raise ConflictError("Email already registered")

            username_exists = await self.user_repo.check_username_exists(username=user_data.username)
            if username_exists:
                raise ConflictError("Username already taken")

            hashed_pw = get_password_hash(user_data.password)
            verification_token = secrets.token_urlsafe(32)

            create_data = user_data.model_dump(exclude={"password", "confirm_password", "agree_terms", "privacy_policy"})
            create_data["hashed_password"] = hashed_pw
            create_data["email_verification_token"] = verification_token
            create_data["status"] = UserStatus.PENDING_VERIFICATION
            create_data["role"] = UserRole.CITIZEN

            user = self.user_repo.model(**create_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            await self.send_verification_email(user.email, verification_token, user.first_name)

            access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
            refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

            await self.audit_log(
                action="user_registered",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id,
                new_values={"email": user.email, "role": user.role.value}
            )

            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role.value,
                    "status": user.status.value,
                    "is_email_verified": user.is_email_verified,
                    "email_verification_token": verification_token,
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "message": "Account created. Please verify your email."
            }

        except (ConflictError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("register", e)
            await self.handle_database_error(e, "register")

    async def login(self, login_data: UserLogin) -> Dict[str, Any]:
        try:
            validated_email = validate_email(login_data.email)

            user = await self.user_repo.get_by_email(email=validated_email)
            if not user:
                raise AuthenticationError("Invalid email or password")

            if not verify_password(login_data.password, user.hashed_password):
                raise AuthenticationError("Invalid email or password")

            if user.status == UserStatus.SUSPENDED:
                raise AuthorizationError("Account has been suspended")

            if user.status == UserStatus.INACTIVE:
                raise AuthorizationError("Account is inactive")

            if user.status == UserStatus.PENDING_VERIFICATION and not login_data.remember_me:
                raise AuthorizationError("Please verify your email before logging in")

            await self.user_repo.update_last_login(user_id=user.id)

            access_token_expires = None
            if login_data.remember_me:
                access_token_expires = timedelta(days=7)

            access_token = create_access_token(
                data={"sub": str(user.id), "role": user.role.value},
                expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

            await self.audit_log(
                action="user_login",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id
            )

            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role.value,
                    "status": user.status.value,
                    "is_email_verified": user.is_email_verified,
                    "profile_picture_url": user.profile_picture_url
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }

        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            await self.log_error("login", e)
            raise AuthenticationError("Login failed")

    async def refresh_token(self, refresh_token_str: str) -> Dict[str, Any]:
        try:
            payload = verify_token(refresh_token_str, token_type="refresh")

            user_id = int(payload.get("sub"))
            user = await self.user_repo.get(id=user_id)
            if not user:
                raise AuthenticationError("User not found")

            if user.status != UserStatus.ACTIVE and user.status != UserStatus.PENDING_VERIFICATION:
                raise AuthorizationError("Account is not active")

            access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }

        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            await self.log_error("refresh_token", e)
            raise AuthenticationError("Token refresh failed")

    async def logout(self, user_id: int, refresh_token_str: Optional[str] = None) -> Dict[str, str]:
        try:
            user = await self.user_repo.get(id=user_id)
            if not user:
                raise NotFoundError("User not found")

            await self.invalidate_cache(f"user_session:{user_id}")

            await self.audit_log(
                action="user_logout",
                entity_type="user",
                entity_id=user_id,
                user_id=user_id
            )

            return {"message": "Successfully logged out"}

        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("logout", e)
            raise BusinessLogicError("Logout failed")

    async def verify_email(self, token: str) -> Dict[str, Any]:
        try:
            if not token:
                raise ValidationError("Verification token is required")

            user = await self.user_repo.get_by_verification_token(token=token)
            if not user:
                raise NotFoundError("Invalid or expired verification token")

            if user.is_email_verified:
                raise BusinessLogicError("Email already verified")

            success = await self.user_repo.update_verification_status(user_id=user.id)
            if not success:
                raise DatabaseError("Failed to update verification status")

            if user.status == UserStatus.PENDING_VERIFICATION:
                user.status = UserStatus.ACTIVE
                await self.db.commit()

            await self.audit_log(
                action="email_verified",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id,
                new_values={"is_email_verified": True}
            )

            access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})

            return {
                "message": "Email verified successfully",
                "access_token": access_token,
                "token_type": "bearer"
            }

        except (ValidationError, NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("verify_email", e)
            raise DatabaseError("Email verification failed")

    async def request_password_reset(self, email: str) -> Dict[str, str]:
        try:
            validated_email = validate_email(email)

            user = await self.user_repo.get_by_email(email=validated_email)
            if not user:
                return {"message": "If the email exists, a reset link has been sent"}

            reset_token = secrets.token_urlsafe(48)

            await self.user_repo.update_password_reset_token(
                user_id=user.id,
                token=reset_token,
                expires_hours=24
            )

            await self.send_password_reset_email(
                email=user.email,
                token=reset_token,
                first_name=user.first_name
            )

            await self.audit_log(
                action="password_reset_requested",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id
            )

            return {"message": "If the email exists, a reset link has been sent"}

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("request_password_reset", e)
            return {"message": "If the email exists, a reset link has been sent"}

    async def reset_password(self, token: str, new_password: str, confirm_password: str) -> Dict[str, str]:
        try:
            if not token:
                raise ValidationError("Reset token is required")

            if new_password != confirm_password:
                raise ValidationError("Passwords do not match")

            validate_password(new_password)

            user = await self.user_repo.get_by_reset_token(token=token)
            if not user:
                raise NotFoundError("Invalid or expired reset token")

            if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
                raise ValidationError("Reset token has expired")

            hashed_pw = get_password_hash(new_password)
            success = await self.user_repo.update_password(user_id=user.id, hashed_password=hashed_pw)
            if not success:
                raise DatabaseError("Failed to update password")

            await self.audit_log(
                action="password_reset",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id
            )

            return {"message": "Password reset successfully"}

        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            await self.log_error("reset_password", e)
            raise DatabaseError("Password reset failed")

    async def change_password(self, user_id: int, password_data: UserPasswordChange) -> Dict[str, str]:
        try:
            user = await self.user_repo.get(id=user_id)
            if not user:
                raise NotFoundError("User not found")

            if not verify_password(password_data.current_password, user.hashed_password):
                raise AuthenticationError("Current password is incorrect")

            validate_password(password_data.new_password)

            hashed_pw = get_password_hash(password_data.new_password)
            success = await self.user_repo.update_password(user_id=user_id, hashed_password=hashed_pw)
            if not success:
                raise DatabaseError("Failed to update password")

            await self.audit_log(
                action="password_changed",
                entity_type="user",
                entity_id=user_id,
                user_id=user_id
            )

            return {"message": "Password changed successfully"}

        except (NotFoundError, AuthenticationError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("change_password", e)
            raise DatabaseError("Password change failed")

    async def send_verification_email(self, email: str, token: str, first_name: str) -> None:
        try:
            await self.send_notification(
                notification_type="email_verification",
                recipients=[email],
                data={
                    "token": token,
                    "first_name": first_name,
                    "email": email,
                    "type": "email_verification"
                }
            )
            logger.info("Verification email sent", email=email)
        except Exception as e:
            logger.warning("Failed to send verification email", email=email, error=str(e))

    async def send_password_reset_email(self, email: str, token: str, first_name: str) -> None:
        try:
            await self.send_notification(
                notification_type="password_reset",
                recipients=[email],
                data={
                    "token": token,
                    "first_name": first_name,
                    "email": email,
                    "type": "password_reset"
                }
            )
            logger.info("Password reset email sent", email=email)
        except Exception as e:
            logger.warning("Failed to send password reset email", email=email, error=str(e))
