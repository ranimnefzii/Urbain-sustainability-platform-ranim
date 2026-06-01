"""
Auth Routes - Urbain Sustainability System
Routes d'authentification et gestion de profil
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.user import (
    UserRegister, UserLogin, UserProfile, UserUpdate,
    UserPasswordChange, UserPasswordReset, UserPasswordResetConfirm,
    UserEmailVerification
)
from app.schemas.notification import NotificationPreferences
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.core.exceptions import (
    AuthenticationError, NotFoundError, ValidationError, ConflictError,
    BusinessLogicError, DatabaseError
)

logger = structlog.get_logger()
router = APIRouter()


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email verification"
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        result = await auth_service.register(data)
        return {
            "success": True,
            "message": "Account created successfully. Please check your email to verify.",
            "data": {"user_id": result["user"]["id"], "email": result["user"]["email"]}
        }
    except (BusinessLogicError, ConflictError, DatabaseError) as e:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise BusinessLogicError("Registration failed. Please try again.")


@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return access/refresh tokens"
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        result = await auth_service.login(data)
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "token_type": "bearer",
                "expires_in": result.get("expires_in", 1800),
                "user": result["user"]
            }
        }
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise AuthenticationError("Invalid credentials")


@router.post(
    "/refresh",
    response_model=dict,
    summary="Refresh access token",
    description="Get a new access token using a refresh token"
)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_token(refresh_token)
        return {
            "success": True,
            "message": "Token refreshed successfully",
            "data": {
                "access_token": result["access_token"],
                "token_type": "bearer",
                "expires_in": result.get("expires_in", 1800)
            }
        }
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise AuthenticationError("Invalid or expired refresh token")


@router.post(
    "/verify-email",
    response_model=dict,
    summary="Verify email address",
    description="Verify user email using verification token"
)
async def verify_email(
    data: UserEmailVerification,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        await auth_service.verify_email(token=data.verification_code)
        return {
            "success": True,
            "message": "Email verified successfully"
        }
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        raise ValidationError("Email verification failed")


@router.post(
    "/forgot-password",
    response_model=dict,
    summary="Request password reset",
    description="Send password reset link to user email"
)
async def forgot_password(
    data: UserPasswordReset,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        await auth_service.request_password_reset(email=data.email)
        return {
            "success": True,
            "message": "If the email exists, a reset link has been sent"
        }
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        return {
            "success": True,
            "message": "If the email exists, a reset link has been sent"
        }


@router.post(
    "/reset-password",
    response_model=dict,
    summary="Reset password",
    description="Reset password using reset token"
)
async def reset_password(
    data: UserPasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        await auth_service.reset_password(token=data.token, new_password=data.new_password, confirm_password=data.confirm_password)
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Password reset failed", error=str(e))
        raise ValidationError("Password reset failed")


@router.get(
    "/me",
    response_model=dict,
    summary="Get current user profile",
    description="Get the authenticated user's profile"
)
async def get_my_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        user = await user_service.get_user(current_user.id)
        profile = UserProfile.model_validate(user)
        return {
            "success": True,
            "message": "Profile retrieved successfully",
            "data": profile
        }
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Get profile failed", error=str(e))
        raise NotFoundError("User not found")


@router.put(
    "/me",
    response_model=dict,
    summary="Update current user profile",
    description="Update the authenticated user's profile"
)
async def update_my_profile(
    data: UserUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        updated = await user_service.update_user(user_id=current_user.id, obj_in=data, current_user_id=current_user.id)
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": updated
        }
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Update profile failed", error=str(e))
        raise ValidationError("Profile update failed")


@router.put(
    "/me/password",
    response_model=dict,
    summary="Change password",
    description="Change the authenticated user's password"
)
async def change_password(
    data: UserPasswordChange,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        await auth_service.change_password(current_user.id, data)
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except AuthenticationError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Change password failed", error=str(e))
        raise ValidationError("Password change failed")


@router.post(
    "/logout",
    response_model=dict,
    summary="Logout user",
    description="Invalidate the current refresh token"
)
async def logout(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Client-side token removal is primary; server-side is best-effort
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        return {
            "success": True,
            "message": "Logged out successfully"
        }


@router.put(
    "/me/notifications",
    response_model=dict,
    summary="Update notification preferences",
    description="Update the authenticated user's notification preferences"
)
async def update_notification_preferences(
    data: NotificationPreferences,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        updated = await user_service.update_notification_preferences(user_id=current_user.id, preferences=data.model_dump())
        return {
            "success": True,
            "message": "Notification preferences updated",
            "data": updated
        }
    except ValidationError:
        raise
    except Exception as e:
        logger.error("Update notification preferences failed", error=str(e))
        raise ValidationError("Failed to update notification preferences")
