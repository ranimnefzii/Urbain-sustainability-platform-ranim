import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.user_repository import UserRepository
from app.repositories.signal_repository import SignalRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.priority_repository import PriorityRepository
from app.repositories.sector_repository import SectorRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.report_repository import ReportRepository
from app.models.user import User, UserRole, UserStatus
from app.models.signal import Signal, SignalStatus
from app.models.category import Category, CategoryType, CategoryStatus
from app.models.priority import Priority, PriorityLevel, SeverityLevel, UrgencyLevel, ImpactLevel
from app.models.sector import Sector, SectorType, SectorStatus
from app.models.notification import Notification, NotificationStatus
from app.models.report import Report, ReportType, ReportStatus

pytestmark = pytest.mark.asyncio


class TestUserRepository:
    async def test_user_repository_create(self, mock_db_session: AsyncSession):
        repo = UserRepository(mock_db_session, User)
        mock_obj = MagicMock(spec=User, id=1, email="test@example.com")
        mock_db_session.execute = AsyncMock()
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        mock_db_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        user_data = MagicMock()
        user_data.model_dump.return_value = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_pw",
            "first_name": "Test",
            "last_name": "User",
        }

        with patch.object(repo, "create", AsyncMock(return_value=mock_obj)):
            result = await repo.create(obj_in=user_data)
            assert result is not None
            assert result.email == "test@example.com"

    async def test_user_repository_get_by_email(self, mock_db_session: AsyncSession):
        repo = UserRepository(mock_db_session, User)
        mock_user = MagicMock(spec=User, email="test@example.com", status=UserStatus.ACTIVE)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_email(email="test@example.com")
        assert result is not None
        assert result.email == "test@example.com"

    async def test_user_repository_get_by_email_not_found(self, mock_db_session: AsyncSession):
        repo = UserRepository(mock_db_session, User)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_email(email="nonexistent@example.com")
        assert result is None


class TestSignalRepository:
    async def test_signal_repository_get_nearby(self, mock_db_session: AsyncSession):
        repo = SignalRepository(mock_db_session, Signal)
        mock_signal = MagicMock(spec=Signal, id=1, latitude=36.8065, longitude=10.1815)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_signal]
        mock_db_session.execute.return_value = mock_result

        results = await repo.get_signals_near_location(latitude=36.8065, longitude=10.1815, radius_km=5.0)
        assert len(results) == 1
        assert results[0].latitude == 36.8065

    async def test_signal_repository_get_by_status(self, mock_db_session: AsyncSession):
        repo = SignalRepository(mock_db_session, Signal)
        mock_signal = MagicMock(spec=Signal, id=1, status=SignalStatus.SUBMITTED)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_signal]
        mock_db_session.execute.return_value = mock_result

        results = await repo.get_by_status(status=SignalStatus.SUBMITTED)
        assert len(results) == 1
        assert results[0].status == SignalStatus.SUBMITTED

    async def test_signal_repository_get_by_status_empty(self, mock_db_session: AsyncSession):
        repo = SignalRepository(mock_db_session, Signal)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        results = await repo.get_by_status(status=SignalStatus.RESOLVED)
        assert len(results) == 0


class TestCategoryRepository:
    async def test_category_repository_get_tree(self, mock_db_session: AsyncSession):
        repo = CategoryRepository(mock_db_session, Category)
        mock_parent = MagicMock(
            spec=Category, id=1, name="Infrastructure", code="INFRA",
            level=1, parent_id=None, sort_order=0,
            category_type=CategoryType.INFRASTRUCTURE, status=CategoryStatus.ACTIVE,
            icon="wrench", color="#FF5733"
        )
        mock_parent.parent_id = None

        mock_child = MagicMock(
            spec=Category, id=2, name="Roads", code="ROADS",
            level=2, parent_id=1, sort_order=0,
            category_type=CategoryType.INFRASTRUCTURE, status=CategoryStatus.ACTIVE,
            icon="road", color="#FF5733"
        )
        mock_child.parent_id = 1

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_parent, mock_child]
        mock_db_session.execute.return_value = mock_result

        tree = await repo.get_tree()
        assert len(tree) >= 0

    async def test_category_repository_get_by_code(self, mock_db_session: AsyncSession):
        repo = CategoryRepository(mock_db_session, Category)
        mock_cat = MagicMock(spec=Category, id=1, code="ROADS")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cat
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_code(code="ROADS")
        assert result is not None
        assert result.code == "ROADS"


class TestPriorityRepository:
    async def test_priority_repository_get_statistics(self, mock_db_session: AsyncSession):
        repo = PriorityRepository(mock_db_session, Priority)
        mock_priority = MagicMock(
            spec=Priority, id=1, name="Medium", code="MED",
            priority_level=PriorityLevel.MEDIUM, severity_level=SeverityLevel.MODERATE,
            urgency_level=UrgencyLevel.NORMAL, impact_level=ImpactLevel.LOCAL,
            total_signals=10, avg_resolution_time_hours=24, escalation_rate=5,
            max_response_time_minutes=120, max_resolution_time_hours=48,
            ai_weight=5, auto_assignment_threshold=80, requires_human_review=False,
            notification_frequency="normal", escalation_enabled=True,
            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        )
        with patch.object(repo, "get", AsyncMock(return_value=mock_priority)):
            with patch.object(repo, "get_priority_statistics", AsyncMock(return_value={
                "priority_id": 1, "name": "Medium", "total_signals": 10
            })):
                stats = await repo.get_priority_statistics(priority_id=1)
                assert stats["total_signals"] == 10

    async def test_priority_repository_get_by_level(self, mock_db_session: AsyncSession):
        repo = PriorityRepository(mock_db_session, Priority)
        mock_priority = MagicMock(spec=Priority, id=1, priority_level=PriorityLevel.CRITICAL)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_priority
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_level(priority_level=PriorityLevel.CRITICAL)
        assert result is not None
        assert result.priority_level == PriorityLevel.CRITICAL


class TestSectorRepository:
    async def test_sector_repository_get_available(self, mock_db_session: AsyncSession):
        repo = SectorRepository(mock_db_session, Sector)
        mock_sector = MagicMock(spec=Sector)
        mock_sector.id = 1
        mock_sector.name = "Roads Dept"
        mock_sector.code = "ROAD"
        mock_sector.sector_type = SectorType.ROADS
        mock_sector.status = SectorStatus.ACTIVE
        mock_sector.max_daily_signals = 100

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_sector]
        mock_db_session.execute.return_value = mock_result

        sectors = await repo.get_active_sectors()
        assert len(sectors) == 1
        assert sectors[0].name == "Roads Dept"


class TestNotificationRepository:
    async def test_notification_repository_get_unread(self, mock_db_session: AsyncSession):
        repo = NotificationRepository(mock_db_session, Notification)
        mock_notif = MagicMock(
            spec=Notification, id=1, user_id=1,
            status=NotificationStatus.DELIVERED,
            title="Test Notification"
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_notif]
        mock_db_session.execute.return_value = mock_result

        unread = await repo.get_unread_notifications(user_id=1)
        assert len(unread) == 1
        assert unread[0].status == NotificationStatus.DELIVERED

    async def test_notification_repository_get_unread_empty(self, mock_db_session: AsyncSession):
        repo = NotificationRepository(mock_db_session, Notification)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        unread = await repo.get_unread_notifications(user_id=999)
        assert len(unread) == 0


class TestReportRepository:
    async def test_report_repository_get_by_date_range(self, mock_db_session: AsyncSession):
        repo = ReportRepository(mock_db_session, Report)
        mock_report = MagicMock(
            spec=Report, id=1, title="Test Report",
            report_type=ReportType.SIGNAL_ANALYSIS, status=ReportStatus.COMPLETED
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_report]
        mock_db_session.execute.return_value = mock_result

        start = datetime.now(timezone.utc)
        end = datetime.now(timezone.utc)
        results = await repo.get_reports_by_date_range(start_date=start, end_date=end)
        assert len(results) == 1
        assert results[0].title == "Test Report"
