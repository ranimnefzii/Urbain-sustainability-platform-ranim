"""
Initial seed for a fresh database installation.

Run inside the backend container after `docker compose up`:

    docker compose exec backend python -m scripts.init_db_seed

Creates, only if missing:
  - default admin account   (admin@urbain.com / Admin123!)
  - demo citizen account    (citoyen@urbain.com / Citoyen123!)
  - the 5 priority levels
  - default urban-problem categories
  - the 9 municipal sectors
"""

import asyncio

from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category, CategoryType, CategoryStatus
from app.models.priority import Priority, PriorityLevel, SeverityLevel, UrgencyLevel, ImpactLevel
from app.models.sector import Sector, SectorType, SectorStatus

ADMIN_EMAIL = "admin@urbain.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"

CITIZEN_EMAIL = "citoyen@urbain.com"
CITIZEN_USERNAME = "citoyen"
CITIZEN_PASSWORD = "Citoyen123!"

PRIORITIES = [
    dict(name="Critique", code="CRITICAL", priority_level=PriorityLevel.CRITICAL,
         severity_level=SeverityLevel.EXTREME, urgency_level=UrgencyLevel.IMMEDIATE,
         impact_level=ImpactLevel.WIDESPREAD, max_response_time_minutes=15,
         max_resolution_time_hours=4, escalation_time_hours=1, color="#DC2626", ai_weight=5),
    dict(name="Haute", code="HIGH", priority_level=PriorityLevel.HIGH,
         severity_level=SeverityLevel.SEVERE, urgency_level=UrgencyLevel.URGENT,
         impact_level=ImpactLevel.NEIGHBORHOOD, max_response_time_minutes=60,
         max_resolution_time_hours=24, escalation_time_hours=4, color="#F59E0B", ai_weight=4),
    dict(name="Moyenne", code="MEDIUM", priority_level=PriorityLevel.MEDIUM,
         severity_level=SeverityLevel.MODERATE, urgency_level=UrgencyLevel.NORMAL,
         impact_level=ImpactLevel.LOCAL, max_response_time_minutes=1440,
         max_resolution_time_hours=72, escalation_time_hours=12, color="#3B82F6", ai_weight=3),
    dict(name="Basse", code="LOW", priority_level=PriorityLevel.LOW,
         severity_level=SeverityLevel.MINOR, urgency_level=UrgencyLevel.LOW,
         impact_level=ImpactLevel.INDIVIDUAL, max_response_time_minutes=4320,
         max_resolution_time_hours=168, escalation_time_hours=24, color="#10B981", ai_weight=2),
    dict(name="Information", code="INFO", priority_level=PriorityLevel.INFO,
         severity_level=SeverityLevel.NONE, urgency_level=UrgencyLevel.DEFERRED,
         impact_level=ImpactLevel.NONE, max_response_time_minutes=10080,
         max_resolution_time_hours=336, escalation_time_hours=48, color="#6B7280", ai_weight=1),
]

CATEGORIES = [
    dict(name="Voirie et Routes", code="ROADS", category_type=CategoryType.INFRASTRUCTURE, icon="road"),
    dict(name="Éclairage public", code="LIGHTING", category_type=CategoryType.INFRASTRUCTURE, icon="lightbulb"),
    dict(name="Eau et Assainissement", code="WATER", category_type=CategoryType.SERVICES, icon="water-drop"),
    dict(name="Déchets et Propreté", code="WASTE", category_type=CategoryType.ENVIRONMENT, icon="trash"),
    dict(name="Espaces verts", code="GREEN_SPACES", category_type=CategoryType.ENVIRONMENT, icon="tree"),
    dict(name="Sécurité", code="SAFETY", category_type=CategoryType.SAFETY, icon="shield"),
    dict(name="Bâtiments publics", code="BUILDINGS", category_type=CategoryType.ADMINISTRATION, icon="building"),
]

SECTORS = [
    dict(name="Eau et Assainissement", code="WATER", sector_type=SectorType.WATER),
    dict(name="Routes et Transport", code="ROADS", sector_type=SectorType.ROADS),
    dict(name="Déchets et Propreté", code="WASTE", sector_type=SectorType.WASTE),
    dict(name="Éclairage public", code="LIGHTING", sector_type=SectorType.LIGHTING),
    dict(name="Espaces verts", code="GREEN_SPACES", sector_type=SectorType.GREEN_SPACES),
    dict(name="Bâtiments publics", code="BUILDINGS", sector_type=SectorType.BUILDINGS),
    dict(name="Sécurité", code="SAFETY", sector_type=SectorType.SAFETY),
    dict(name="Environnement", code="ENVIRONMENT", sector_type=SectorType.ENVIRONMENT),
    dict(name="Administration", code="ADMINISTRATION", sector_type=SectorType.ADMINISTRATION),
]


async def exists(session, model, **kwargs) -> bool:
    stmt = select(func.count()).select_from(model)
    for col, value in kwargs.items():
        stmt = stmt.where(getattr(model, col) == value)
    result = await session.execute(stmt)
    return result.scalar_one() > 0


async def main() -> None:
    async with AsyncSessionLocal() as session:
        if not await exists(session, User, email=ADMIN_EMAIL):
            session.add(User(
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                first_name="Admin",
                last_name="Urbain",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                email_notifications_enabled=True,
            ))
            print(f"[seed] admin user created -> {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            print(f"[seed] admin user already exists ({ADMIN_EMAIL}) -> skipped")

        if not await exists(session, User, email=CITIZEN_EMAIL):
            session.add(User(
                email=CITIZEN_EMAIL,
                username=CITIZEN_USERNAME,
                hashed_password=get_password_hash(CITIZEN_PASSWORD),
                first_name="Citoyen",
                last_name="Test",
                role=UserRole.CITIZEN,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                email_notifications_enabled=True,
            ))
            print(f"[seed] demo citizen created -> {CITIZEN_EMAIL} / {CITIZEN_PASSWORD}")
        else:
            print(f"[seed] demo citizen already exists ({CITIZEN_EMAIL}) -> skipped")

        for data in PRIORITIES:
            if not await exists(session, Priority, code=data["code"]):
                session.add(Priority(**data))
                print(f"[seed] priority {data['code']} created")
            else:
                print(f"[seed] priority {data['code']} already exists -> skipped")

        for data in CATEGORIES:
            if not await exists(session, Category, code=data["code"]):
                session.add(Category(**data))
                print(f"[seed] category {data['code']} created")
            else:
                print(f"[seed] category {data['code']} already exists -> skipped")

        for data in SECTORS:
            if not await exists(session, Sector, code=data["code"]):
                session.add(Sector(**data))
                print(f"[seed] sector {data['code']} created")
            else:
                print(f"[seed] sector {data['code']} already exists -> skipped")

        await session.commit()
        print("Seeding complete. Frontend: http://localhost:5173 — admin login: admin@urbain.com / Admin123!")


if __name__ == "__main__":
    asyncio.run(main())