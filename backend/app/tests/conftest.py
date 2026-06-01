import asyncio
import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, patch

# Test environment overrides - must be set before app imports
os.environ.setdefault("DEBUG", "True")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError, AuthorizationError, NotFoundError,
    ValidationError, ConflictError, BusinessLogicError, DatabaseError
)
from app.main import app
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category, CategoryType, CategoryStatus
from app.models.priority import Priority, PriorityLevel, SeverityLevel, UrgencyLevel, ImpactLevel
from app.models.signal import Signal, SignalStatus, SignalSource, VerificationStatus
from app.models.sector import Sector, SectorType, SectorStatus
from app.models.report import Report, ReportType, ReportStatus
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus

from .factories import (
    UserFactory, CategoryFactory, PriorityFactory, SignalFactory,
    SectorFactory, ReportFactory, NotificationFactory
)


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture
async def db_session():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_url = f"sqlite+aiosqlite:///{tmp.name}"
    engine = create_async_engine(
        db_url,
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    os.unlink(tmp.name)


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = UserFactory(
        id=1,
        email="citizen@test.com",
        username="citizen1",
        role=UserRole.CITIZEN,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
        hashed_password="$2b$12$Uvk.xXnzDEiPzR6GNSYbhOwFh71I9CHxrAfB53gnMD2VnugKgmB8i",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = UserFactory(
        id=2,
        email="admin@test.com",
        username="admin1",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sector_user(db_session: AsyncSession) -> User:
    user = UserFactory(
        id=3,
        email="sector@test.com",
        username="sector1",
        role=UserRole.SECTOR,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
        sector_id=1,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def unverified_user(db_session: AsyncSession) -> User:
    user = UserFactory(
        id=4,
        email="unverified@test.com",
        username="unverified1",
        role=UserRole.CITIZEN,
        status=UserStatus.PENDING_VERIFICATION,
        is_email_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession) -> Category:
    cat = CategoryFactory(
        id=1,
        name="Road Infrastructure",
        code="ROADS",
        category_type=CategoryType.INFRASTRUCTURE,
    )
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)
    return cat


@pytest_asyncio.fixture
async def test_priority(db_session: AsyncSession) -> Priority:
    pri = PriorityFactory(
        id=1,
        name="Medium",
        code="MED",
        priority_level=PriorityLevel.MEDIUM,
        severity_level=SeverityLevel.MODERATE,
        urgency_level=UrgencyLevel.NORMAL,
        impact_level=ImpactLevel.LOCAL,
    )
    db_session.add(pri)
    await db_session.commit()
    await db_session.refresh(pri)
    return pri


@pytest_asyncio.fixture
async def test_sector(db_session: AsyncSession) -> Sector:
    sec = SectorFactory(
        id=1,
        name="Roads Department",
        code="ROAD",
        sector_type=SectorType.ROADS,
    )
    db_session.add(sec)
    await db_session.commit()
    await db_session.refresh(sec)
    return sec


@pytest_asyncio.fixture
async def test_signal(db_session: AsyncSession, test_user: User, test_category: Category, test_priority: Priority) -> Signal:
    sig = SignalFactory(
        id=1,
        title="Pothole on Main Street",
        description="There is a large pothole on Main Street near the intersection.",
        reference_number="SIG-202505-000001",
        created_by=test_user.id,
        category_id=test_category.id,
        priority_id=test_priority.id,
        status=SignalStatus.SUBMITTED,
    )
    db_session.add(sig)
    await db_session.commit()
    await db_session.refresh(sig)
    return sig


@pytest_asyncio.fixture
async def test_report(db_session: AsyncSession, test_user: User) -> Report:
    rpt = ReportFactory(
        id=1,
        title="Monthly Analysis Report",
        report_code="RPT-SIG-202505-0001",
        generated_by=test_user.id,
        report_type=ReportType.SIGNAL_ANALYSIS,
        status=ReportStatus.COMPLETED,
    )
    db_session.add(rpt)
    await db_session.commit()
    await db_session.refresh(rpt)
    return rpt


@pytest.fixture
def citizen_token(test_user: User) -> str:
    return create_access_token(data={"sub": str(test_user.id), "role": test_user.role.value})


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(data={"sub": str(admin_user.id), "role": admin_user.role.value})


@pytest.fixture
def sector_token(sector_user: User) -> str:
    return create_access_token(data={"sub": str(sector_user.id), "role": sector_user.role.value})


@pytest.fixture
def unverified_token(unverified_user: User) -> str:
    return create_access_token(data={"sub": str(unverified_user.id), "role": unverified_user.role.value})


@pytest.fixture
def expired_token() -> str:
    from jose import jwt
    payload = {
        "sub": "1",
        "role": "citizen",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest.fixture
def refresh_token_str(test_user: User) -> str:
    return create_refresh_token(data={"sub": str(test_user.id), "role": test_user.role.value})


@pytest.fixture
def auth_headers(citizen_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {citizen_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sector_headers(sector_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {sector_token}"}


@pytest.fixture
def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = MagicMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_email_or_username = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.remove = AsyncMock()
    repo.count = AsyncMock()
    repo.search_users = AsyncMock()
    repo.check_email_exists = AsyncMock()
    repo.check_username_exists = AsyncMock()
    repo.update_last_login = AsyncMock()
    repo.update_password = AsyncMock()
    repo.update_verification_status = AsyncMock()
    repo.get_by_verification_token = AsyncMock()
    repo.get_by_reset_token = AsyncMock()
    repo.get_user_statistics = AsyncMock()
    repo.get_user_activity = AsyncMock()
    return repo


@pytest.fixture
def mock_signal_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.get_by_user = AsyncMock()
    repo.get_by_status = AsyncMock()
    repo.get_by_reference_number = AsyncMock()
    repo.search_signals = AsyncMock()
    repo.get_signals_near_location = AsyncMock()
    repo.get_signals_with_filters = AsyncMock()
    repo.get_signal_with_relations = AsyncMock()
    repo.assign_to_user = AsyncMock()
    repo.update_status = AsyncMock()
    repo.create = AsyncMock()
    repo.remove = AsyncMock()
    repo.get_signal_statistics = AsyncMock()
    return repo


@pytest.fixture
def mock_category_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.get_by_code = AsyncMock()
    repo.get_tree = AsyncMock()
    repo.get_root_categories = AsyncMock()
    repo.get_children = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.remove = AsyncMock()
    repo.get_category_statistics = AsyncMock()
    repo.check_code_exists = AsyncMock()
    repo.check_name_exists = AsyncMock()
    return repo


@pytest.fixture
def mock_priority_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.get_by_level = AsyncMock()
    repo.get_by_code = AsyncMock()
    repo.get_priority_statistics = AsyncMock()
    repo.get_priority_matrix = AsyncMock()
    repo.get_critical_priorities = AsyncMock()
    repo.get_high_priorities = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_sector_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.get_by_code = AsyncMock()
    repo.get_by_type = AsyncMock()
    repo.get_active_sectors = AsyncMock()
    repo.get_sectors_workload = AsyncMock()
    repo.get_sector_statistics = AsyncMock()
    repo.get_sector_performance = AsyncMock()
    repo.get_sectors_by_category_support = AsyncMock()
    repo.check_code_exists = AsyncMock()
    repo.check_name_exists = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.remove = AsyncMock()
    return repo


@pytest.fixture
def mock_notification_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.get_by_user = AsyncMock()
    repo.get_by_code = AsyncMock()
    repo.get_unread_notifications = AsyncMock()
    repo.get_notifications_with_filters = AsyncMock()
    repo.get_notification_with_relations = AsyncMock()
    repo.get_notification_statistics = AsyncMock()
    repo.mark_as_read = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.remove = AsyncMock()
    return repo


@pytest.fixture
def mock_report_repo():
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.get_by_code = AsyncMock()
    repo.get_reports_by_date_range = AsyncMock()
    repo.get_by_type = AsyncMock()
    repo.get_by_status = AsyncMock()
    repo.get_report_with_relations = AsyncMock()
    repo.get_report_statistics = AsyncMock()
    repo.mark_as_completed = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.remove = AsyncMock()
    return repo


@pytest.fixture
def mock_signal_service():
    svc = MagicMock()
    svc.create_signal = AsyncMock()
    svc.get_signal = AsyncMock()
    svc.get_signals = AsyncMock()
    svc.update_signal = AsyncMock()
    svc.delete_signal = AsyncMock()
    svc.search_signals = AsyncMock()
    svc.get_nearby_signals = AsyncMock()
    svc.assign_signal = AsyncMock()
    svc.process_signal = AsyncMock()
    svc.resolve_signal = AsyncMock()
    svc.cancel_signal = AsyncMock()
    return svc


@pytest.fixture
def mock_user_service():
    svc = MagicMock()
    svc.create_user = AsyncMock()
    svc.get_user = AsyncMock()
    svc.update_user = AsyncMock()
    svc.delete_user = AsyncMock()
    svc.get_users = AsyncMock()
    svc.search_users = AsyncMock()
    svc.get_user_stats = AsyncMock()
    svc.update_password = AsyncMock()
    return svc


@pytest.fixture
def mock_auth_service():
    svc = MagicMock()
    svc.register = AsyncMock()
    svc.login = AsyncMock()
    svc.refresh_token = AsyncMock()
    svc.verify_email = AsyncMock()
    svc.change_password = AsyncMock()
    svc.request_password_reset = AsyncMock()
    svc.reset_password = AsyncMock()
    return svc


@pytest.fixture
def mock_ai_service():
    svc = MagicMock()
    svc.classify_signal = AsyncMock()
    svc.assess_priority = AsyncMock()
    svc.generate_report = AsyncMock()
    svc.detect_anomalies = AsyncMock()
    svc.predict_trends = AsyncMock()
    return svc


@pytest.fixture
def mock_notification_service():
    svc = MagicMock()
    svc.create_notification = AsyncMock()
    svc.send_notification = AsyncMock()
    svc.get_notifications = AsyncMock()
    svc.get_user_notifications = AsyncMock()
    svc.mark_as_read = AsyncMock()
    svc.get_notification_stats = AsyncMock()
    return svc


@pytest.fixture
def mock_sector_service():
    svc = MagicMock()
    svc.create_sector = AsyncMock()
    svc.get_sector = AsyncMock()
    svc.get_sectors = AsyncMock()
    svc.update_sector = AsyncMock()
    svc.delete_sector = AsyncMock()
    svc.get_available_sectors = AsyncMock()
    svc.assign_signal_to_sector = AsyncMock()
    svc.get_sector_performance = AsyncMock()
    svc.get_sector_stats = AsyncMock()
    return svc


@pytest.fixture
def mock_analytics_service():
    svc = MagicMock()
    svc.get_dashboard_stats = AsyncMock()
    svc.get_signal_trends = AsyncMock()
    svc.get_sector_performance = AsyncMock()
    svc.get_category_breakdown = AsyncMock()
    svc.get_citizen_satisfaction = AsyncMock()
    svc.get_response_times = AsyncMock()
    svc.get_prediction_metrics = AsyncMock()
    svc.get_hotspot_data = AsyncMock()
    svc.get_temporal_patterns = AsyncMock()
    return svc
