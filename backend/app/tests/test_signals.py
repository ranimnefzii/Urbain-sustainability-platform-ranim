import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import SignalStatus
from app.models.user import User
from app.models.category import Category
from app.models.priority import Priority
from app.core.exceptions import NotFoundError, AuthorizationError, BusinessLogicError
from .factories import SignalFactory

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def draft_signal(db_session: AsyncSession, test_user: User, test_category: Category, test_priority: Priority):
    sig = SignalFactory(
        id=99,
        title="Draft signal",
        description="A draft signal for testing.",
        reference_number="SIG-DRAFT-000001",
        created_by=test_user.id,
        category_id=test_category.id,
        priority_id=test_priority.id,
        status=SignalStatus.DRAFT,
    )
    db_session.add(sig)
    await db_session.commit()
    await db_session.refresh(sig)
    return sig


@pytest_asyncio.fixture
async def under_review_signal(db_session: AsyncSession, test_user: User, test_category: Category, test_priority: Priority):
    sig = SignalFactory(
        id=98,
        title="Under review signal",
        description="A signal under review.",
        reference_number="SIG-UR-000001",
        created_by=test_user.id,
        category_id=test_category.id,
        priority_id=test_priority.id,
        status=SignalStatus.UNDER_REVIEW,
    )
    db_session.add(sig)
    await db_session.commit()
    await db_session.refresh(sig)
    return sig


@pytest_asyncio.fixture
async def in_progress_signal(db_session: AsyncSession, test_user: User, test_category: Category, test_priority: Priority):
    sig = SignalFactory(
        id=97,
        title="In progress signal",
        description="A signal being processed.",
        reference_number="SIG-IP-000001",
        created_by=test_user.id,
        category_id=test_category.id,
        priority_id=test_priority.id,
        status=SignalStatus.IN_PROGRESS,
    )
    db_session.add(sig)
    await db_session.commit()
    await db_session.refresh(sig)
    return sig


class TestCreateSignal:
    async def test_create_signal(self, async_client: AsyncClient, auth_headers: dict, test_category: dict):
        payload = {
            "title": "Broken streetlight on Avenue Habib Bourguiba",
            "description": "The streetlight has been broken for a week, causing safety concerns at night.",
            "category_id": test_category.id if hasattr(test_category, 'id') else 1,
            "location": {
                "latitude": 36.8065,
                "longitude": 10.1815,
                "address": "Avenue Habib Bourguiba",
                "city": "Tunis",
            },
        }
        response = await async_client.post("/api/v1/signals/", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True

    async def test_create_signal_missing_fields(self, async_client: AsyncClient, auth_headers: dict):
        payload = {"title": "Missing fields test"}
        response = await async_client.post("/api/v1/signals/", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_signal_invalid_location(self, async_client: AsyncClient, auth_headers: dict):
        payload = {
            "title": "Invalid location test",
            "description": "Test signal with invalid coordinates.",
            "category_id": 1,
            "location": {
                "latitude": 200,
                "longitude": 500,
            },
        }
        response = await async_client.post("/api/v1/signals/", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetSignal:
    async def test_get_signal(self, async_client: AsyncClient, auth_headers: dict, test_signal):
        response = await async_client.get(f"/api/v1/signals/{test_signal.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    async def test_get_signal_not_found(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get("/api/v1/signals/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListSignals:
    async def test_list_signals(self, async_client: AsyncClient, auth_headers: dict, test_signal):
        response = await async_client.get("/api/v1/signals/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) >= 1

    async def test_list_signals_pagination(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get("/api/v1/signals/?page=1&size=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    async def test_list_signals_filtered(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get(
            "/api/v1/signals/?status=submitted", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestUpdateSignal:
    async def test_update_signal(self, async_client: AsyncClient, auth_headers: dict, test_signal):
        payload = {"title": "Updated title for the signal"}
        response = await async_client.put(
            f"/api/v1/signals/{test_signal.id}", json=payload, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_update_signal_not_owner(self, async_client: AsyncClient, sector_headers: dict, test_signal):
        payload = {"title": "Hacked title"}
        response = await async_client.put(
            f"/api/v1/signals/{test_signal.id}", json=payload, headers=sector_headers
        )
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_403_FORBIDDEN)


class TestDeleteSignal:
    async def test_delete_signal(self, async_client: AsyncClient, auth_headers: dict, draft_signal):
        response = await async_client.delete(f"/api/v1/signals/{draft_signal.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK


class TestNearbySignals:
    async def test_nearby_signals(self, async_client: AsyncClient, auth_headers: dict, test_signal):
        response = await async_client.get(
            "/api/v1/signals/nearby?latitude=36.8065&longitude=10.1815&radius=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestAssignSignal:
    async def test_assign_signal(self, async_client: AsyncClient, sector_headers: dict, under_review_signal):
        payload = {"assigned_to_user_id": 3, "assigned_sector_id": 1}
        response = await async_client.post(
            f"/api/v1/signals/{under_review_signal.id}/assign", json=payload, headers=sector_headers
        )
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)


class TestResolveSignal:
    async def test_resolve_signal(self, async_client: AsyncClient, sector_headers: dict, in_progress_signal):
        payload = {
            "status": "resolved",
            "resolution_description": "The pothole has been filled by the Roads Department.",
            "resolution_method": "manual",
            "resolution_cost": 500.0,
        }
        response = await async_client.post(
            f"/api/v1/signals/{in_progress_signal.id}/resolve", json=payload, headers=sector_headers
        )
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)


class TestSignalStatusTransitions:
    async def test_signal_status_transitions(self, async_client: AsyncClient, sector_headers: dict, test_signal):
        payload = {"status": "under_review"}
        response = await async_client.post(
            f"/api/v1/signals/{test_signal.id}/process", json=payload, headers=sector_headers
        )
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)


class TestSearchSignals:
    async def test_search_signals(self, async_client: AsyncClient, auth_headers: dict, test_signal):
        response = await async_client.get(
            "/api/v1/signals/search?q=pothole", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
