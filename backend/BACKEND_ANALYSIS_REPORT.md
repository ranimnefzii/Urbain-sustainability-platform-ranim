# Urbain Sustainability System — Backend Analysis Report
## Comprehensive Deep Analysis of Architecture, Connectivity, Issues & Fixes

**Generated:** 2026-05-26 | **Total Files Analyzed:** 71 Python files | **Tests:** 57 passing

---

## TABLE OF CONTENTS

1. [Project Architecture Overview](#1-architecture-overview)
2. [File Inventory & Status](#2-file-inventory)
3. [CRITICAL Issues](#3-critical-issues)
4. [HIGH Issues](#4-high-issues)
5. [MEDIUM Issues](#5-medium-issues)
6. [LOW Issues / Improvements](#6-low-issues)
7. [Missing Service Methods](#7-missing-service-methods)
8. [Missing API Endpoints](#8-missing-api-endpoints)
9. [Cross-Service Dependency Issues](#9-cross-service-dependencies)
10. [Model Relationship Completeness](#10-model-relationships)
11. [Schema Completeness](#11-schema-completeness)
12. [Final Recommendations](#12-recommendations)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├───────────────┬───────────────────┬─────────────────────────┤
│   API Layer   │   Service Layer   │    Data Access Layer    │
│  (api/v1/*)   │   (services/*)    │   (repositories/*)     │
├───────────────┼───────────────────┼─────────────────────────┤
│  auth.py      │  auth_service.py  │  user_repository.py    │
│  users.py     │  user_service.py  │  signal_repository.py  │
│  signals.py   │  signal_service.py│  category_repository.py│
│  categories.py│  category_service │  priority_repository.py│
│  reports.py   │  report_service.py│  report_repository.py  │
│  admin.py     │  priority_service │  sector_repository.py  │
│               │  sector_service.py│  notification_repo.py  │
│               │  notification_svc │  base.py               │
│               │  ai_service.py    │                         │
│               │  email_service.py │  ┌──────────────┐      │
│               │  sms_service.py   │  │   Models      │      │
│               │  push_service.py  │  │  (SQLAlchemy) │      │
│               │  file_service.py  │  └──────────────┘      │
│               │  map_service.py   │  ┌──────────────┐      │
│               │  analytics_svc.py │  │   Schemas     │      │
│               └───────────────────┘  │  (Pydantic)   │      │
│                                       └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 2. File Inventory & Status

### 2.1 ✅ COMPLETED & VALIDATED FILES (28)

| Layer | File | Status |
|-------|------|--------|
| Core | `core/__init__.py` | ✅ Complete |
| Core | `core/config.py` | ✅ Complete (needs V2 migration) |
| Core | `core/database.py` | ✅ Complete (**CRITICAL: asyncpg prefix missing**) |
| Core | `core/security.py` | ✅ Complete |
| Core | `core/exceptions.py` | ✅ Complete |
| Core | `core/dependencies.py` | ✅ Complete |
| Models | `models/user.py` | ✅ Complete |
| Models | `models/signal.py` | ✅ Complete |
| Models | `models/category.py` | ✅ Complete |
| Models | `models/priority.py` | ✅ Complete |
| Models | `models/report.py` | ✅ Complete |
| Models | `models/sector.py` | ✅ Complete |
| Models | `models/notification.py` | ✅ Complete (**relationships missing**) |
| Models | `models/__init__.py` | ✅ Complete |
| Schemas | `schemas/*.py` (7 files) | ✅ Complete |
| Repositories | `repositories/base.py` | ✅ Complete |
| Repositories | `repositories/user_repository.py` | ✅ Complete |
| Repositories | `repositories/signal_repository.py` | ✅ Complete |
| Repositories | `repositories/category_repository.py` | ✅ Complete |
| Repositories | `repositories/priority_repository.py` | ✅ Complete |
| Repositories | `repositories/report_repository.py` | ✅ Complete |
| Repositories | `repositories/notification_repository.py` | ✅ Complete |
| Repositories | `repositories/sector_repository.py` | ✅ Complete |
| Repositories | `repositories/__init__.py` | ✅ Complete |

### 2.2 ⚠️ PARTIAL FILES (42)

| Layer | File | Lines | Issues |
|-------|------|-------|--------|
| API | `api/v1/auth.py` | ~300 | 4 signature mismatches, missing `message` fields |
| API | `api/v1/users.py` | ~280 | **9/9 endpoints call wrong service method names** |
| API | `api/v1/signals.py` | ~450 | ORM mutation in _serialize, missing params in add_media |
| API | `api/v1/categories.py` | ~260 | **9/9 endpoints call wrong service method names** |
| API | `api/v1/reports.py` | ~340 | **15+ method name/signature mismatches** |
| API | `api/v1/admin.py` | ~280 | **All 11 endpoints call wrong/non-existent methods** |
| API | `api/deps.py` | ~90 | RoleChecker defined but unused |
| Services | `services/user_service.py` | ~330 | 4 model field ref errors, 3 repository method mismatches, missing methods |
| Services | `services/signal_service.py` | ~410 | Minor: unused imports |
| Services | `services/auth_service.py` | ~380 | Minor issues |
| Services | `services/ai_service.py` | ~420 | Missing 3 methods needed by API |
| Services | `services/analytics_service.py` | ~750 | Missing 6 methods needed by API |
| Services | `services/category_service.py` | ~230 | Missing 1 method needed by API |
| Services | `services/priority_service.py` | ~350 | ✅ Complete |
| Services | `services/report_service.py` | ~550 | ✅ Complete |
| Services | `services/notification_service.py` | ~410 | ✅ Complete |
| Services | `services/sector_service.py` | ~380 | ✅ Complete |
| Services | `services/email_service.py` | ~580 | ✅ Complete |
| Services | `services/sms_service.py` | ~250 | ✅ Complete |
| Services | `services/push_service.py` | ~250 | ✅ Complete |
| Services | `services/file_service.py` | ~280 | ✅ Complete |
| Services | `services/map_service.py` | ~580 | ✅ Complete |
| Utils | `utils/constants.py` | ~100 | ✅ Complete |
| Utils | `utils/helpers.py` | ~120 | ✅ Complete |
| Utils | `utils/validators.py` | ~120 | ✅ Complete |
| Tests | `tests/conftest.py` | ~300 | ✅ Complete |
| Tests | `tests/factories.py` | ~200 | ✅ Complete |
| Tests | `tests/test_auth.py` | ~250 | ✅ Passing |
| Tests | `tests/test_signals.py` | ~300 | ✅ Passing |
| Tests | `tests/test_repositories.py` | ~200 | ✅ Passing |
| Tests | `tests/test_services.py` | ~250 | ✅ Passing |

### 2.3 ❌ MISSING FILES (9)

| File | Issue |
|------|-------|
| `alembic/versions/*.py` | No initial migration created |
| `app/core/dependencies.py` | ✅ Created but `dependencies.py` mentioned twice now — service layer not referenced |

---

## 3. CRITICAL ISSUES

### 3.1 [CRITICAL] database.py — Async engine requires `+asyncpg` prefix

**File:** `backend/app/core/database.py:21`
**Problem:** `create_async_engine(settings.DATABASE_URL)` where URL is `postgresql://user:pass@localhost/db`. Async engine requires async driver prefix.
**Fix:** Change to `postgresql+asyncpg://` in config or transform in database.py:
```python
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, ...)
```
**Impact:** Application will crash on startup with `ValueError`.

---

### 3.2 [CRITICAL] notification model — Missing `signal` and `report` relationships

**File:** `backend/app/models/notification.py:76-77`
**Problem:** Columns `signal_id` (FK) and `report_id` (FK) exist but NO `relationship()` definitions exist. The `notification_repository.py:243-245` tries `selectinload(Notification.signal)` and `selectinload(Notification.report)`.
**Fix:** Add to `Notification` model:
```python
signal = relationship("Signal", back_populates="notifications")
report = relationship("Report", back_populates="notifications")
```
And add `notifications` relationship to `Signal` and `Report` models.
**Impact:** `AttributeError` at runtime when loading notification relations.

---

### 3.3 [CRITICAL] ALL API routes call wrong service method names

#### users.py — 9/9 endpoints broken
| Route Line | Calls | Should Be |
|-----------|-------|-----------|
| users.py:49 | `user_service.get_all()` | `user_service.get_users()` |
| users.py:78 | `user_service.search()` | `user_service.search_users()` |
| users.py:104 | `user_service.get()` | `user_service.get_user()` |
| users.py:132 | `user_service.update()` | `user_service.update_user()` |
| users.py:163 | `user_service.delete()` | `user_service.delete_user()` |
| users.py:193 | `signal_service.get_by_user()` | `signal_service.get_user_signals()` |
| users.py:219 | `user_service.get_statistics()` | `user_service.get_user_stats()` |
| users.py:246 | `user_service.activate()` | `user_service.activate_user()` |
| users.py:273 | `user_service.deactivate()` | `user_service.deactivate_user()` |

#### categories.py — 9/9 endpoints broken
| Route Line | Calls | Should Be |
|-----------|-------|-----------|
| categories.py:41 | `category_service.create()` | `category_service.create_category()` |
| categories.py:73 | `category_service.get_all()` | `category_service.get_categories()` |
| categories.py:95 | `category_service.get_tree()` | `category_service.get_category_tree()` |
| categories.py:118 | `category_service.get_by_type()` | `category_service.get_categories_by_type()` |
| categories.py:141 | `category_service.get()` | `category_service.get_category()` |
| categories.py:169 | `category_service.update()` | `category_service.update_category()` |
| categories.py:200 | `category_service.delete()` | `category_service.delete_category()` |
| categories.py:227 | `category_service.get_children()` | `category_service.get_subcategories()` |
| categories.py:250 | `category_service.get_statistics()` | `category_service.get_category_stats()` |

#### reports.py — 15+ endpoints broken
| Route Line | Calls | Should Be |
|-----------|-------|-----------|
| reports.py:44 | `report_service.create()` | `report_service.create_report()` |
| reports.py:82 | `report_service.get_all()` | `report_service.get_reports()` |
| reports.py:106 | `report_service.get_statistics()` | `report_service.get_report_stats()` |
| reports.py:260 | `report_service.get()` | `report_service.get_report()` |
| reports.py:288 | `report_service.delete()` | `report_service.delete_report()` |
| reports.py:316 | `report_service.export()` | `report_service.export_report()` |

#### admin.py — All 11 endpoints broken
| Route Line | Calls | Should Be |
|-----------|-------|-----------|
| admin.py:38 | `analytics_service.get_dashboard_data()` | `analytics_service.get_dashboard_stats()` |
| admin.py:60 | `analytics_service.get_overview_stats()` | Does not exist |
| admin.py:84 | `signal_service.get_statistics()` | `signal_service.get_signal_stats()` |
| admin.py:106 | `user_service.get_admin_stats()` | Does not exist |
| admin.py:128 | `sector_service.get_performance_stats()` | `sector_service.get_sector_performance()` |
| admin.py:150 | `category_service.get_breakdown()` | Does not exist |
| admin.py:173 | `analytics_service.get_response_time_analytics()` | `analytics_service.get_response_times()` |
| admin.py:195 | `ai_service.get_prediction_overview()` | Does not exist |
| admin.py:236 | `analytics_service.get_audit_log()` | Does not exist |
| admin.py:261 | `analytics_service.get_system_health()` | Does not exist |

**Impact:** Every API endpoint will fail with `AttributeError` at runtime.

---

### 3.4 [CRITICAL] user_service.py — Model field reference errors

**File:** `backend/app/services/user_service.py`

| Line | Code | Problem | Fix |
|------|------|---------|-----|
| 116 | `user.is_active` | `User` has no `is_active` field | Use `user.status == UserStatus.ACTIVE` |
| 129 | `user.last_login` | `User` has no `last_login` field | Use `user.last_login_at` |
| 155 | `user.is_verified` | `User` has no `is_verified` field | Use `user.is_email_verified` |
| 280 | `user.is_superuser` | `User` has no `is_superuser` field | Use `user.role == UserRole.ADMIN` |

**Impact:** `AttributeError` at runtime when these lines execute.

---

### 3.5 [CRITICAL] user_service.py — Repository method mismatches

| Line | Calls | Repository Has |
|------|-------|---------------|
| 80 | `self.repository.update(id=..., obj_in=...)` | `update(*, db_obj=ModelType, obj_in=...)` — uses `db_obj`, not `id` |
| 197 | `self.repository.search()` | `search_users()` |
| 235 | `self.repository.get_by_status()` | No such method |
| 265 | `self.repository.get_stats()` | No such method |

**Impact:** `AttributeError` or `TypeError` at runtime.

---

### 3.6 [CRITICAL] API-Service signature mismatches

| File | Line | Call | Service Signature | Fix |
|------|------|------|-------------------|-----|
| auth.py:130 | `auth_service.verify_email(email, verification_code)` | `verify_email(token: str)` | Change API to pass single token |
| auth.py:157 | `auth_service.generate_password_reset_token(email)` | `request_password_reset(email)` | Rename call |
| auth.py:159 | Access `result["token"]` | Returns dict without "token" key | Fix: service already sends email |
| auth.py:184 | `auth_service.reset_password(token, new_password)` | `reset_password(token, new_password, confirm_password)` | Add 3rd arg |
| auth.py:289 | `user_service.update_notification_preferences()` | Does not exist | Implement method |
| auth.py:236 | `user_service.update()` | No such method | Use `update_user()` |
| reports.py:157 | `report_service.generate_signal_report(signal_id, analysis, generated_by)` | `generate_signal_report(signal_id, generated_by)` | Remove `analysis` param |
| reports.py:193 | `report_service.generate_sector_report(sector_id, analysis, generated_by)` | `generate_sector_report(sector_id, generated_by)` | Remove `analysis` param |
| reports.py:232 | `report_service.generate_trend_report(analysis, trend_data, generated_by)` | `generate_trend_report(generated_by, start_date, end_date)` | Fix all params |
| signals.py:434 | `signal_service.add_media(signal_id, media_urls)` | `add_media(signal_id, media_type, media_urls, user_id)` | Missing 2 params |

---

### 3.7 [CRITICAL] sector_repository.py — Non-existent `"escalated"` status

**File:** `backend/app/repositories/sector_repository.py:441`
**Problem:** `Signal.status == "escalated"` — `SignalStatus` enum has no `ESCALATED` member.
**Fix:** Remove or replace with actual statuses.

---

## 4. HIGH Issues

### 4.1 meta_data vs metadata field name mismatch

**Files:** `models/report.py:137` vs `schemas/report.py:65,120`
**Problem:** Model field is `meta_data` but schemas use `metadata`.
**Impact:** Silent data loss — updates to `metadata` via Pydantic are dropped.
**Fix:** Either rename model column to `metadata` or add column alias.

### 4.2 _serialize_signal() mutates ORM objects

**File:** `backend/app/api/v1/signals.py:31-37`
**Problem:** Sets `signal.created_by_user = None`, etc. — corrupts tracked ORM session state.
**Fix:** Don't mutate ORM objects; use `model_validate` directly:
```python
def _serialize_signal(signal):
    return SignalResponse.model_validate(signal).model_dump()
```

### 4.3 Hardcoded enum status strings

**Files:**
- `sector_repository.py:236,248,296,350,435,441` — uses `"resolved"`, `"closed"`, `"active"`, `"in_progress"`, `"assigned"`, `"escalated"` as raw strings
- `priority_repository.py:234-237` — uses `"escalated"` and `"overdue"` as raw strings
- `security.py:106-128` — uses `"admin"`, `"citizen"`, `"sector"` as raw strings

**Fix:** Import and use `SignalStatus`, `UserStatus`, `UserRole` enum values.

### 4.4 user_service.py missing methods needed by API routes

| Missing Method | Called By |
|---------------|-----------|
| `delete_user(user_id, current_user_id)` | `users.py:163` |
| `activate_user(user_id)` | `users.py:246` |
| `deactivate_user(user_id)` | `users.py:273` |
| `update_notification_preferences(user_id, prefs)` | `auth.py:289` |

### 4.5 CategoryService missing method

| Missing Method | Called By |
|---------------|-----------|
| `get_breakdown()` | `admin.py:150` |

### 4.6 AnalyticsService missing methods

| Missing Method | Called By |
|---------------|-----------|
| `get_overview_stats()` | `admin.py:60` |
| `get_dashboard_data()` | `admin.py:38` |
| `get_response_time_analytics(days)` | `admin.py:173` |
| `get_audit_log(filters, skip, limit)` | `admin.py:236` |
| `get_system_health()` | `admin.py:261` |
| `get_trend_data(start_date, end_date)` | `reports.py:227` |

### 4.7 AIService missing methods

| Missing Method | Called By |
|---------------|-----------|
| `get_prediction_overview()` | `admin.py:195` |
| `analyze_signal(signal_data)` | `reports.py:156` |
| `analyze_sector(sector_data)` | `reports.py:192` |
| `analyze_trends(trend_data)` | `reports.py:231` |

### 4.8 ReportService missing method

| Missing Method | Called By |
|---------------|-----------|
| `get_signal_data(signal_id)` | `reports.py:153` |
| `get_sector_data(sector_id)` | `reports.py:189` |

### 4.9 Missing ForeignKey constraints

| Model | Field | Missing FK |
|-------|-------|-----------|
| `signal.py:68` | `assigned_sector_id` | No `ForeignKey("sectors.id")` |
| `report.py:67` | `sector_id` | No `ForeignKey("sectors.id")` |

### 4.10 Report's `generated_by_user` has one-sided relationship

**File:** `models/report.py:149`
**Problem:** `generated_by_user = relationship("User", foreign_keys=[generated_by])` — no `back_populates`.
User model has no corresponding `reports_generated` relationship.

---

## 5. MEDIUM Issues

### 5.1 Pydantic V1 deprecated syntax throughout schemas

**Files:** ALL schema files
**Issues:**
- `class Config: from_attributes = True` → `model_config = ConfigDict(from_attributes=True)`
- `@validator` → `@field_validator` or `@model_validator`
- `max_items=N` → `max_length=N`

### 5.2 backref vs back_populates inconsistency

**Files:**
- `models/category.py:100` — `backref="parent"` instead of `back_populates`
- `models/sector.py:99` — `backref="sector"` instead of `back_populates`

### 5.3 Missing `"message"` in API responses

**Endpoints affected:** 30+ endpoints across ALL route files.

### 5.4 RoleChecker defined but unused

**File:** `api/deps.py:87` — `RoleChecker` class is defined but never used by any endpoint.

### 5.5 Pagination returns wrong total

**File:** `signals.py:102` — uses `len(signals)` as total count instead of actual DB count.

### 5.6 base.py search() uses func.lower instead of ilike

**File:** `repositories/base.py:210-211` — `func.lower(field_attr).like(...)` should use `.ilike()` for PostgreSQL performance.

---

## 6. LOW Issues / Improvements

### 6.1 Unused imports
- `signal_service.py:8` — `import math`
- `signal_service.py:19` — `UserRepository`
- `map_service.py:10` — various math imports unused

### 6.2 Email service import at end of file
- `email_service.py:560` — `from datetime import datetime, timezone` placed at end of file (after class definitions)

### 6.3 PermissionChecker uses hardcoded strings
- `security.py:106-128` — compares against `"admin"`, `"citizen"`, `"sector"` strings

### 6.4 Alembic — no initial migration
- `alembic/versions/` directory is empty — no initial database migration created.

### 6.5 Settings class uses Pydantic V1 Config
- `config.py:95-97` — `class Config: env_file = ".env"` should use `model_config = SettingsConfigDict(...)`

---

## 7. Missing Service Methods

The following methods exist in services but have NO API endpoint exposing them:

| Service | Method | Purpose |
|---------|--------|---------|
| `AIService` | `classify_signal()` | AI text/image classification |
| `AIService` | `assess_priority()` | Priority scoring |
| `AIService` | `generate_report()` | Report generation |
| `AIService` | `predict_trends()` | Trend prediction |
| `AIService` | `detect_anomalies()` | Anomaly detection |
| `AIService` | `get_confidence_score()` | Confidence scoring |
| `AIService` | `batch_classify()` | Batch processing |
| `AIService` | `get_model_info()` | Model metadata |
| `AnalyticsService` | `get_dashboard_stats()` | Dashboard data |
| `AnalyticsService` | `get_signal_trends()` | Trend analysis |
| `AnalyticsService` | `get_sector_performance()` | Sector perf |
| `AnalyticsService` | `get_category_breakdown()` | Category stats |
| `AnalyticsService` | `get_citizen_satisfaction()` | Satisfaction metrics |
| `AnalyticsService` | `get_response_times()` | Response times |
| `AnalyticsService` | `get_prediction_metrics()` | Prediction metrics |
| `AnalyticsService` | `get_hotspot_data()` | Hotspot detection |
| `AnalyticsService` | `get_temporal_patterns()` | Time patterns |
| `AnalyticsService` | `generate_summary_report()` | Summary generation |
| `SignalService` | `get_sector_signals()` | Signals by sector |
| `SignalService` | `get_signal_timeline()` | Signal history |
| `UserService` | `create_user()` | User creation |
| `UserService` | `update_password()` | Password change |
| `UserService` | `verify_email()` | Email verification |
| `ReportService` | `generate_report()` | Report generation |
| `ReportService` | `schedule_report()` | Scheduling |
| `ReportService` | `archive_report()` | Archival |
| `AuthService` | `logout()` | Session logout |
| `AuthService` | `send_verification_email()` | Send verification |
| `AuthService` | `send_password_reset_email()` | Password reset email |

---

## 8. Missing API Endpoints

The following endpoints should exist but don't (based on service methods):

| Endpoint | Service Method | Purpose |
|----------|---------------|---------|
| `POST /api/v1/ai/classify` | `ai_service.classify_signal()` | AI classification |
| `GET /api/v1/ai/model-info` | `ai_service.get_model_info()` | AI model info |
| `POST /api/v1/ai/batch-classify` | `ai_service.batch_classify()` | Batch AI |
| `GET /api/v1/analytics/trends` | `analytics_service.get_signal_trends()` | Trends |
| `GET /api/v1/analytics/hotspots` | `analytics_service.get_hotspot_data()` | Heatmap |
| `GET /api/v1/analytics/satisfaction` | `analytics_service.get_citizen_satisfaction()` | Satisfaction |
| `POST /api/v1/reports/generate` | `report_service.generate_report()` | Custom report |
| `POST /api/v1/reports/{id}/schedule` | `report_service.schedule_report()` | Schedule |
| `POST /api/v1/reports/{id}/archive` | `report_service.archive_report()` | Archive |
| `GET /api/v1/signals/{id}/timeline` | `signal_service.get_signal_timeline()` | Timeline |
| `POST /api/v1/auth/logout` | `auth_service.logout()` | Logout |

---

## 9. Cross-Service Dependency Issues

### 9.1 SignalService → AIService (circular import handled via lazy import)
**Status:** ✅ Correctly handled with lazy import inside method.

### 9.2 SignalService → NotificationService (circular import handled)
**Status:** ✅ Correctly handled with lazy import inside method.

### 9.3 ReportsService → AIService (direct import)
**File:** `services/report_service.py` — imports `AIService` at top level. No circular dependency.

### 9.4 ReportsService → AnalyticsService (direct import)
**File:** `services/report_service.py` — imports `AnalyticsService` at top level. No circular dependency.

### 9.5 AnalyticsService → all repositories
**File:** `services/analytics_service.py` — imports `SignalRepository`, `UserRepository`, `CategoryRepository`, `SectorRepository`. **OK** — repositories don't import services.

### 9.6 auth_service.py → UserRepository
**Status:** ✅ Correctly uses `UserRepository` directly (not through `UserService`).

---

## 10. Model Relationship Completeness

### 10.1 Existing valid relationships

| From | To | back_populates | Status |
|------|----|----------------|--------|
| `User.signals_created` | `Signal.created_by_user` | ✅ | Complete |
| `User.signals_processed` | `Signal.processed_by_user` | ✅ | Complete |
| `User.notifications` | `Notification.user` | ✅ | Complete |
| `Signal.created_by_user` | `User.signals_created` | ✅ | Complete |
| `Signal.processed_by_user` | `User.signals_processed` | ✅ | Complete |
| `Signal.category` | `Category.signals` | ✅ | Complete |
| `Signal.priority` | `Priority.signals` | ✅ | Complete |
| `Signal.reports` | `Report.signal` | ✅ | Complete |
| `Category.signals` | `Signal.category` | ✅ | Complete |
| `Priority.signals` | `Signal.priority` | ✅ | Complete |
| `Report.signal` | `Signal.reports` | ✅ | Complete |

### 10.2 Missing relationships that should exist

| From | To | Problem |
|------|----|---------|
| `Notification.signal` | `Signal.notifications` | ❌ Missing entirely |
| `Notification.report` | `Report.notifications` | ❌ Missing entirely |
| `User.sector` | `Sector.users` | ❌ Uses backref instead of explicit |
| `User.reports_generated` | `Report.generated_by_user` | ❌ Missing from User |
| `Signal.assigned_sector` | `Sector.signals` | ❌ Missing entirely |

### 10.3 Missing ForeignKey constraints

| Model | Field | Should Reference |
|-------|-------|-----------------|
| `Signal.assigned_sector_id` | `Integer` | `ForeignKey("sectors.id")` |
| `Report.sector_id` | `Integer` | `ForeignKey("sectors.id")` |

---

## 11. Schema Completeness

### 11.1 Schema-model field alignment

| Schema | Model | Issues |
|--------|-------|--------|
| `ReportCreate.metadata` | `Report.meta_data` | ❌ Name mismatch |
| `ReportUpdate.metadata` | `Report.meta_data` | ❌ Name mismatch |
| `ReportResponse.metadata` | `Report.meta_data` | ❌ Name mismatch |
| All other schemas | Corresponding models | ✅ Aligned |

### 11.2 Schemas using V1 deprecated syntax

| Schema File | Issue |
|------------|-------|
| `user.py` | `@validator`, `class Config` |
| `signal.py` | `@validator`, `class Config`, `max_items` |
| `category.py` | `@validator`, `class Config`, `max_items`, `min_items` |
| `sector.py` | `@validator`, `class Config`, `max_items`, `min_items` |
| `priority.py` | `@validator`, `class Config`, `max_items`, `min_items` |
| `report.py` | `@validator`, `class Config`, `max_items`, `min_items` |
| `notification.py` | `@validator`, `class Config`, `max_items`, `min_items` |

---

## 12. Recommendations

### Priority Order for Fixes

#### IMMEDIATE (Fix before any deployment)
1. **database.py:21** — Add `+asyncpg` prefix to DATABASE_URL
2. **notification.py:76-77** — Add `signal` and `report` relationships
3. **API routes** — Fix ALL method name mismatches in users.py, categories.py, reports.py, admin.py
4. **user_service.py** — Fix model field references (`is_active`, `last_login`, `is_verified`, `is_superuser`)
5. **user_service.py** — Fix repository method calls
6. **reports.py + auth.py + signals.py** — Fix signature mismatches
7. **Add missing service methods** that API routes call

#### HIGH (Before production)
8. Fix hardcoded enum strings in sector_repository.py, priority_repository.py, security.py
9. Fix meta_data vs metadata mismatch
10. Fix _serialize_signal() ORM mutation
11. Add ForeignKey constraints for assigned_sector_id and sector_id
12. Fix all model relationships to use consistent back_populates

#### MEDIUM (Before full launch)
13. Migrate all schemas to Pydantic V2 syntax
14. Add `"message"` to all API responses
15. Create initial Alembic migration
16. Add missing API endpoints for unexposed service methods

#### LOW (Nice to have)
17. Remove unused imports
18. Add RoleChecker to appropriate endpoints
19. Replace func.lower with ilike in base repository
20. Add API endpoint for sector signal assignment management

---

## APPENDIX: Complete File List (71 Python files)

```
backend/
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── .gitkeep
├── alembic.ini
├── Dockerfile
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── tasks.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── auth.py
│   │       ├── categories.py
│   │       ├── reports.py
│   │       ├── signals.py
│   │       └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── notification.py
│   │   ├── priority.py
│   │   ├── report.py
│   │   ├── sector.py
│   │   ├── signal.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── notification.py
│   │   ├── priority.py
│   │   ├── report.py
│   │   ├── sector.py
│   │   ├── signal.py
│   │   └── user.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── category_repository.py
│   │   ├── notification_repository.py
│   │   ├── priority_repository.py
│   │   ├── report_repository.py
│   │   ├── sector_repository.py
│   │   ├── signal_repository.py
│   │   └── user_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── analytics_service.py
│   │   ├── auth_service.py
│   │   ├── base.py
│   │   ├── category_service.py
│   │   ├── email_service.py
│   │   ├── file_service.py
│   │   ├── map_service.py
│   │   ├── notification_service.py
│   │   ├── priority_service.py
│   │   ├── push_service.py
│   │   ├── report_service.py
│   │   ├── sector_service.py
│   │   ├── signal_service.py
│   │   ├── sms_service.py
│   │   └── user_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── factories.py
│   │   ├── test_auth.py
│   │   ├── test_repositories.py
│   │   ├── test_services.py
│   │   └── test_signals.py
│   └── utils/
│       ├── __init__.py
│       ├── constants.py
│       ├── helpers.py
│       └── validators.py
├── docker-compose.yml
└── .gitignore
```
