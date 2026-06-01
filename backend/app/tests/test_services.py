import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from datetime import datetime, timezone

from app.services.user_service import UserService
from app.services.signal_service import SignalService, SignalStatus, VALID_TRANSITIONS
from app.services.auth_service import AuthService
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService
from app.services.sector_service import SectorService
from app.services.analytics_service import AnalyticsService
from app.models.user import User, UserRole, UserStatus
from app.models.signal import Signal
from app.models.category import Category, CategoryType
from app.models.priority import Priority, PriorityLevel
from app.models.sector import Sector, SectorType, SectorStatus
from app.schemas.user import UserCreate, UserLogin, UserRegister, UserPasswordChange
from app.schemas.signal import SignalCreate, SignalUpdate, SignalLocation
from app.schemas.notification import NotificationCreate
from app.schemas.sector import SectorCreate
from app.core.exceptions import (
    AuthenticationError, ValidationError, NotFoundError,
    ConflictError, BusinessLogicError, AuthorizationError
)

pytestmark = pytest.mark.asyncio


class TestUserService:
    async def test_user_service_create(self, mock_db_session):
        service = UserService(mock_db_session)
        service.repository = AsyncMock()

        mock_user = MagicMock(spec=User, id=1, email="new@test.com", username="newuser")

        obj_in = MagicMock(spec=UserCreate)
        obj_in.model_dump.return_value = {
            "email": "new@test.com",
            "username": "newuser",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "New",
            "last_name": "User",
        }
        obj_in.email = "new@test.com"
        obj_in.username = "newuser"
        obj_in.password = "TestPass123!"

        service.repository.get_by_email_or_username.return_value = None
        service.repository.check_email_exists.return_value = False
        service.repository.check_username_exists.return_value = False

        with patch.object(service, "create_user", AsyncMock(return_value=mock_user)):
            result = await service.create_user(obj_in)
            assert result.email == "new@test.com"

    async def test_user_service_create_duplicate(self, mock_db_session):
        service = UserService(mock_db_session)
        service.repository = AsyncMock()

        existing_user = MagicMock(spec=User, email="dup@test.com", username="dupuser")

        obj_in = MagicMock(spec=UserCreate)
        obj_in.email = "dup@test.com"
        obj_in.username = "dupuser"
        obj_in.password = "TestPass123!"

        service.repository.get_by_email_or_username.return_value = existing_user

        with pytest.raises(ConflictError):
            await service.create_user(obj_in)


class TestSignalService:
    async def test_signal_service_create_with_ai(self, mock_db_session):
        service = SignalService(mock_db_session)
        service.repository = AsyncMock()

        location = SignalLocation(latitude=36.8065, longitude=10.1815)
        obj_in = MagicMock(spec=SignalCreate)
        obj_in.model_dump.return_value = {
            "title": "Test Signal",
            "description": "Test description for signal creation.",
            "category_id": 1,
            "location": location,
            "images": None,
            "videos": None,
            "documents": None,
            "audio_files": None,
            "is_anonymous": False,
            "allow_contact": True,
            "estimated_damage_cost": None,
            "affected_people_count": None,
            "affected_area_sqm": None,
            "safety_risk_level": None,
        }

        mock_signal = MagicMock(spec=Signal, id=1, title="Test Signal", reference_number="SIG-202505-TEST")

        with patch.object(service, "_generate_reference_number", AsyncMock(return_value="SIG-202505-TEST")):
            with patch.object(service, "_run_ai_classification", AsyncMock(return_value=mock_signal)):
                with patch.object(service, "create_signal", AsyncMock(return_value=mock_signal)):
                    result = await service.create_signal(obj_in, user_id=1)
                    assert result is not None
                    assert result.title == "Test Signal"

    async def test_signal_service_state_transition_valid(self, mock_db_session):
        service = SignalService(mock_db_session)
        service.repository = AsyncMock()

        mock_signal = MagicMock(spec=Signal, id=1, status=SignalStatus.DRAFT)

        new_status = SignalStatus.SUBMITTED
        is_valid = new_status in VALID_TRANSITIONS.get(mock_signal.status, [])
        assert is_valid is True

    async def test_signal_service_state_transition_invalid(self, mock_db_session):
        service = SignalService(mock_db_session)
        service.repository = AsyncMock()

        mock_signal = MagicMock(spec=Signal, id=1, status=SignalStatus.DRAFT)

        new_status = SignalStatus.RESOLVED
        is_valid = new_status in VALID_TRANSITIONS.get(mock_signal.status, [])
        assert is_valid is False


class TestAuthService:
    async def test_auth_service_login(self, mock_db_session, mock_user_repo):
        service = AuthService(mock_db_session)
        service.user_repo = mock_user_repo

        login_data = MagicMock(spec=UserLogin)
        login_data.email = "test@example.com"
        login_data.password = "TestPass123!"
        login_data.remember_me = False

        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.CITIZEN
        mock_user.status = UserStatus.ACTIVE
        mock_user.is_email_verified = True
        mock_user.hashed_password = "$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5JqPf5OYpGkfYOBpJFxG1kq"

        with patch("app.services.auth_service.validate_email", return_value="test@example.com"):
            with patch("app.services.auth_service.verify_password", return_value=True):
                mock_user_repo.get_by_email.return_value = mock_user
                mock_user_repo.get_by_email_or_username.return_value = None

                with patch.object(service, "login", AsyncMock(return_value={
                    "user": {"id": 1, "email": "test@example.com", "role": "citizen"},
                    "access_token": "fake_token",
                    "refresh_token": "fake_refresh",
                    "token_type": "bearer",
                    "expires_in": 1800,
                })):
                    result = await service.login(login_data)
                    assert result["token_type"] == "bearer"
                    assert "access_token" in result

    async def test_auth_service_login_invalid(self, mock_db_session, mock_user_repo):
        service = AuthService(mock_db_session)
        service.user_repo = mock_user_repo

        login_data = MagicMock(spec=UserLogin)
        login_data.email = "wrong@test.com"
        login_data.password = "WrongPass123!"
        login_data.remember_me = False

        mock_user_repo.get_by_email.return_value = None

        with patch("app.services.auth_service.validate_email", return_value="wrong@test.com"):
            with pytest.raises(AuthenticationError):
                await service.login(login_data)


class TestAIService:
    async def test_ai_service_classify(self, mock_db_session):
        service = AIService(mock_db_session)
        service.category_repo = MagicMock()
        service.priority_repo = MagicMock()

        result = await service.classify_signal(
            text="There is a large pothole on the main road causing traffic issues.",
            images=None,
            location={"latitude": 36.8065, "longitude": 10.1815},
        )

        assert result is not None
        assert "predicted_category" in result
        assert "confidence_score" in result
        assert "processing_time_ms" in result
        assert 0 <= result["confidence_score"] <= 1
        assert result["processing_time_ms"] >= 0

    async def test_ai_service_classify_short_text(self, mock_db_session):
        service = AIService(mock_db_session)

        with pytest.raises(ValidationError):
            await service.classify_signal(text="Short")


class TestNotificationService:
    async def test_notification_service_send(self, mock_db_session):
        service = NotificationService(mock_db_session)
        service.repository = MagicMock()

        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.status = "pending"

        obj_in = MagicMock(spec=NotificationCreate)
        obj_in.model_dump.return_value = {
            "title": "Test Notification",
            "message": "This is a test notification.",
            "notification_type": "signal_created",
            "channel": "in_app",
            "user_id": 1,
            "priority": "normal",
        }

        service.repository.create.return_value = mock_notification

        with patch.object(service, "create_notification", AsyncMock(return_value=mock_notification)):
            result = await service.create_notification(obj_in)
            assert result is not None

    async def test_notification_service_get_unread(self, mock_db_session):
        service = NotificationService(mock_db_session)
        service.repository = MagicMock()

        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.status = "delivered"

        service.repository.get_by_user = AsyncMock(return_value=[mock_notification])

        notifications = await service.get_user_notifications(user_id=1)
        assert len(notifications) == 1


class TestSectorService:
    async def test_sector_service_auto_assign(self, mock_db_session):
        service = SectorService(mock_db_session)
        service.repository = MagicMock()

        mock_sector = MagicMock(spec=Sector, id=1, name="Roads Dept", priority_level=1)
        mock_signal = MagicMock(spec=Signal, id=1, category_id=1)

        with patch.object(service, "assign_signal_to_sector", AsyncMock(return_value=(mock_sector, "Signal assigned to Roads Dept"))):
            result, message = await service.assign_signal_to_sector(signal_id=1)
            assert result is not None
            assert "assigned" in message.lower()

    async def test_sector_service_no_available_sectors(self, mock_db_session):
        service = SectorService(mock_db_session)
        service.repository = MagicMock()

        with patch.object(service, "assign_signal_to_sector", AsyncMock(return_value=(None, "No available sector found"))):
            result, message = await service.assign_signal_to_sector(signal_id=999)
            assert result is None
            assert "no available" in message.lower()


class TestAnalyticsService:
    async def test_analytics_service_dashboard(self, mock_db_session):
        service = AnalyticsService(mock_db_session)
        service.signal_repo = MagicMock()
        service.user_repo = MagicMock()
        service.category_repo = MagicMock()
        service.sector_repo = MagicMock()
        service.report_repo = MagicMock()
        service.notification_repo = MagicMock()

        mock_stats = {
            "overview": {
                "total_signals": 150,
                "total_users": 45,
                "total_categories": 8,
                "total_sectors": 5,
            },
            "period_stats": {
                "period": "month",
                "new_signals": 30,
                "resolved_signals": 20,
                "resolution_rate": 66.67,
                "avg_resolution_time_hours": 48.5,
                "citizen_satisfaction_avg": 3.8,
            },
            "daily_trend": {"2025-05-01": 5, "2025-05-02": 3},
        }

        with patch.object(service, "get_dashboard_stats", AsyncMock(return_value=mock_stats)):
            result = await service.get_dashboard_stats(period="month")
            assert result["overview"]["total_signals"] == 150
            assert result["period_stats"]["period"] == "month"
            assert result["period_stats"]["resolution_rate"] == 66.67

    async def test_analytics_service_dashboard_with_sector(self, mock_db_session):
        service = AnalyticsService(mock_db_session)
        service.signal_repo = MagicMock()

        mock_stats = {
            "overview": {
                "total_signals": 150,
                "total_users": 45,
                "total_categories": 8,
                "total_sectors": 5,
                "sector_signals": 25,
            },
            "period_stats": {
                "period": "week",
                "new_signals": 10,
                "resolved_signals": 8,
                "resolution_rate": 80.0,
            },
            "daily_trend": {},
            "filters_applied": {"sector_id": 1},
        }

        with patch.object(service, "get_dashboard_stats", AsyncMock(return_value=mock_stats)):
            result = await service.get_dashboard_stats(period="week", sector_id=1)
            assert result["overview"]["sector_signals"] == 25
            assert result["filters_applied"]["sector_id"] == 1
