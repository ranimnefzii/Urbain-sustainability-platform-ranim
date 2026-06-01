<p align="center">
  <img src="https://img.shields.io/badge/Status-Complete-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.11-blue" alt="Python">
  <img src="https://img.shields.io/badge/React-19-61DAFB" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-15-316192" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

<h1 align="center">Urbain Sustainability System</h1>
<h3 align="center">AI-Powered Smart City Problem Reporting & Management Platform</h3>

<p align="center">
  <em>Système Intelligent de Signalement des Problèmes Urbains</em>
</p>

---

## Table of Contents

1. [Project Overview](#-project-overview)
2. [Business Logic & Use Cases](#-business-logic--use-cases)
3. [System Architecture](#-system-architecture)
4. [Technology Stack](#-technology-stack)
5. [Project Structure](#-project-structure)
6. [Database Schema](#-database-schema)
7. [API Reference](#-api-reference)
8. [Core Components](#-core-components)
9. [Notification System](#-notification-system)
10. [AI/ML Pipeline](#-aiml-pipeline)
11. [Installation & Setup](#-installation--setup)
12. [Running the System](#-running-the-system)
13. [Testing](#-testing)
14. [Deployment](#-deployment)
15. [Contributing](#-contributing)
16. [License](#-license)

---

## 📋 Project Overview

**Urbain** is a full-stack, enterprise-grade **Smart City Problem Reporting System** that empowers citizens to report urban issues — from potholes and broken streetlights to illegal dumping and infrastructure damage — and enables municipal administrators to manage, prioritize, and resolve these reports through an intelligent, AI-driven workflow.

### Key Capabilities

| Capability | Description |
|---|---|
| **Citizen Reporting** | Submit problem reports with geo-location, photos, and categorization |
| **AI Classification** | Automatic categorization and priority scoring using NLP and ML models |
| **Multi-Channel Notifications** | Email (SMTP), SMS (TextBelt/email-to-SMS gateway), WhatsApp (pywhatkit), Push (FCM) |
| **Real-Time Analytics** | Trend analysis, hotspot detection, performance metrics, predictive forecasting |
| **Role-Based Access** | Citizen, Sector Worker, Administrator roles with granular permissions |
| **Audit Trail** | Complete logging of all system actions for compliance and accountability |
| **Geographic Intelligence** | Interactive maps, heatmaps, proximity analysis, and spatial queries |
| **Report Generation** | AI-powered automated reports with charts, trends, and recommendations |

---

## 🏢 Business Logic & Use Cases

### Core Business Flow

```
Citizen Reports Issue
        │
        ▼
System Logs & Acknowledges
        │
        ▼
AI Classification & Priority Assessment
        │
        ▼
Automatic Assignment to Relevant Sector
        │
        ▼
Sector Worker Processes the Signal
        │
        ▼
Resolution & Citizen Feedback
        │
        ▼
Analytics & Reporting
```

### Detailed Business Scenarios

#### 1. Citizen Submits a Problem Report

A citizen discovers an urban issue (e.g., a broken traffic light at an intersection). They open the Urbain platform, pin the exact location on the map, upload photos, select a category, and submit.

**System Actions:**
- Creates a `Signal` with status `PENDING`
- Notifies the citizen via email/SMS with a tracking code
- Triggers AI classification to validate/refine the category
- Assesses priority based on safety risk, affected population, and urgency
- Assigns the signal to the appropriate city sector
- Logs the action in the audit trail

#### 2. AI Classification & Prioritization

When a signal is created, the AI pipeline runs automatically:

- **Classification**: Uses a trained NLP model (scikit-learn + transformers) to categorize the problem description into predefined categories (Infrastructure, Environment, Safety, Services, Administration)
- **Priority Scoring**: Evaluates multiple criteria — severity level, affected area, population impact, historical data — to assign a priority level from CRITICAL (1) to INFO (5)
- **Hotspot Detection**: Cross-references the location against known problem hotspots to adjust priority if needed

#### 3. Sector Assignment & Resolution

- Each signal is routed to the appropriate municipal sector (Roads, Sanitation, Public Safety, Parks, Water, Electricity, Buildings, Environment, Transport)
- Sector workers see assigned signals in their dashboard
- Workers update status through a defined workflow: `PENDING → IN_PROGRESS → RESOLVED → CLOSED`
- If resolution exceeds SLA, the signal can be escalated

#### 4. Notification Delivery Chain

When a status change or important event occurs, the notification system activates:

```
Event Trigger
    │
    ▼
Determine Channel (Email/SMS/WhatsApp/Push)
    │
    ▼
Resolve Recipients (user lookup or custom address)
    │
    ▼
Attempt Primary Delivery
    │
    ├── Success → Mark as DELIVERED
    │
    └── Failure → Retry (up to max_retries)
                    │
                    └── All failed → Mark as FAILED
```

#### 5. Analytics & Decision Support

Administrators have access to:

- **Dashboard**: Real-time KPIs (signals by status, priority distribution, sector performance)
- **Trend Analysis**: Signal volume over time with predictive forecasting (7/14/30/90-day horizons)
- **Hotspot Mapping**: Geographic clusters of problem reports with density heatmaps
- **Performance Metrics**: Average resolution time, citizen satisfaction rate, sector efficiency scores
- **Report Generation**: Auto-generated PDF/Excel reports with charts and recommendations

#### 6. User Roles & Permissions

| Role | Permissions |
|---|---|
| **Citizen** | Submit signals, track own signals, update profile, view public maps |
| **Sector Worker** | View & manage assigned signals, update status, add notes |
| **Administrator** | Full access: manage users, sectors, categories, priorities, generate reports, view analytics, configure notifications, audit logs |

---

## 🏛️ System Architecture

### Three-Layer Service Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                             │
│  React 19 + TypeScript + Vite 5                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pages: Admin Dashboard, Signal Map, Reports, etc.   │   │
│  │  Components: Gauge Charts, Maps, Tables, Forms       │   │
│  │  State: React Query, Auth Context, Toast Context     │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ HTTP (Axios)                         │
├───────────────────────┼─────────────────────────────────────┤
│                       ▼                                     │
│                    API LAYER                                 │
│                                                             │
│  FastAPI (uvicorn) — 16 Route Modules                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/v1/auth, /users, /signals, /categories,        │   │
│  │  /reports, /notifications, /priorities, /sectors,     │   │
│  │  /admin, /analytics, /map, /ai, /files, /audit,      │   │
│  │  /escalation, /feedback                               │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ Dependency Injection                 │
├───────────────────────┼─────────────────────────────────────┤
│                       ▼                                     │
│                    SERVICE LAYER                             │
│                                                             │
│  16 Service Classes — Business Logic                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AuthService, SignalService, NotificationService,    │   │
│  │  ReportService, AnalyticsService, AIService,         │   │
│  │  SectorService, CategoryService, etc.                │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ Repository Pattern                   │
├───────────────────────┼─────────────────────────────────────┤
│                       ▼                                     │
│                    REPOSITORY LAYER                          │
│                                                             │
│  8 Repository Classes — Data Access                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SignalRepository, ReportRepository,                 │   │
│  │  NotificationRepository, UserRepository, etc.        │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ SQLAlchemy 2.0 Async                │
├───────────────────────┼─────────────────────────────────────┤
│                       ▼                                     │
│                    DATA LAYER                                │
│                                                             │
│  PostgreSQL 15 + Redis 7                                    │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  PostgreSQL  │  │    Redis     │                         │
│  │  - 9 tables  │  │  - Cache     │                         │
│  │  - Enums     │  │  - Queue     │                         │
│  │  - Indexes   │  │  - Sessions  │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Highlights

- **Clean Architecture**: Strict separation of concerns — routes handle HTTP, services contain business logic, repositories manage data access
- **Dependency Injection**: Services and repositories are injected via FastAPI's `Depends()` for testability and loose coupling
- **Async Throughout**: Full async/await stack — FastAPI + SQLAlchemy async + asyncpg + httpx for non-blocking I/O
- **Exception Hierarchy**: Custom exception classes (`NotFoundError`, `ValidationError`, `BusinessLogicError`, `DatabaseError`, `ExternalServiceError`) with structured JSON error responses
- **JWT Authentication**: Dual-token strategy (access token 30 min + refresh token 7 days) with automatic refresh on the frontend

---

## 💻 Technology Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Runtime |
| FastAPI | 0.104.1 | Web framework |
| Uvicorn | 0.24.0 | ASGI server |
| SQLAlchemy | 2.0.23 | ORM (async) |
| Alembic | 1.12.1 | Database migrations |
| Pydantic | 2.5.0 | Validation & serialization |
| PostgreSQL | 15 | Primary database |
| Redis | 7 | Caching & message broker |
| Celery | 5.3.4 | Background task queue |
| scikit-learn | 1.3.2 | ML models |
| transformers | 4.36.2 | NLP models |
| PyTorch | 2.1.2 | Deep learning |
| Jinja2 | 3.1.2 | Email templates |
| structlog | 23.2.0 | Structured logging |
| pytest | 7.4.3 | Testing |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| React | 19.2.6 | UI framework |
| TypeScript | 6.0 | Type safety |
| Vite | 5.4.21 | Build tool & dev server |
| React Router | 7.15.1 | Routing |
| TanStack Query | 5.100.14 | Data fetching & caching |
| Axios | 1.16.1 | HTTP client |
| Tailwind CSS | 3.4.19 | Styling |
| Leaflet | 1.9.4 | Maps |

### Infrastructure

| Technology | Purpose |
|---|---|
| Docker & Docker Compose | Containerization & orchestration |
| PostgreSQL 15 | Relational database |
| Redis 7 | In-memory cache & queue |
| Gmail SMTP | Email delivery |
| TextBelt | Free SMS API |
| pywhatkit | WhatsApp automation |

---

## 📁 Project Structure

```
urbain-sustainability/
│
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/                   # API route handlers
│   │   │       ├── auth.py           # Authentication endpoints
│   │   │       ├── users.py          # User management
│   │   │       ├── signals.py        # Signal/problem reporting
│   │   │       ├── categories.py     # Problem categories CRUD
│   │   │       ├── reports.py        # Report generation & management
│   │   │       ├── notifications.py  # Multi-channel notifications
│   │   │       ├── priorities.py     # Priority levels CRUD
│   │   │       ├── sectors.py        # City sectors CRUD
│   │   │       ├── admin.py          # Admin dashboard & stats
│   │   │       ├── analytics.py      # Trend analysis & hotspots
│   │   │       ├── map.py            # Geographic data endpoints
│   │   │       ├── ai.py             # AI classification & prediction
│   │   │       ├── files.py          # File uploads
│   │   │       ├── audit.py          # Audit log queries
│   │   │       ├── escalation.py     # Escalation workflows
│   │   │       └── feedback.py       # Citizen feedback
│   │   │
│   │   ├── core/                     # Core configuration
│   │   │   ├── config.py             # Settings (pydantic-settings)
│   │   │   ├── database.py           # Database engine & session
│   │   │   ├── security.py           # JWT, hashing, utils
│   │   │   └── exceptions.py         # Exception hierarchy
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── user.py               # User, UserRole, UserStatus
│   │   │   ├── signal.py             # Signal, SignalStatus
│   │   │   ├── category.py           # Category, CategoryType
│   │   │   ├── priority.py           # Priority, PriorityLevel
│   │   │   ├── sector.py             # Sector, SectorType
│   │   │   ├── report.py             # Report, ReportType, ReportStatus
│   │   │   ├── notification.py       # Notification, NotificationType
│   │   │   ├── audit_log.py          # AuditLog
│   │   │   └── password_reset.py     # PasswordResetToken
│   │   │
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── user.py, signal.py, category.py, priority.py
│   │   │   ├── sector.py, report.py, notification.py
│   │   │   ├── auth.py, admin.py, analytics.py, ai.py
│   │   │   └── common.py             # Pagination, response wrappers
│   │   │
│   │   ├── services/                 # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── signal_service.py
│   │   │   ├── category_service.py
│   │   │   ├── report_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── email_service.py      # SMTP email delivery
│   │   │   ├── sms_service.py        # SMS via TextBelt/gateway
│   │   │   ├── sector_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── ai_service.py
│   │   │
│   │   ├── repositories/             # Data access layer
│   │   │   ├── base.py               # Base CRUD repository
│   │   │   ├── user_repository.py
│   │   │   ├── signal_repository.py
│   │   │   ├── report_repository.py
│   │   │   ├── notification_repository.py
│   │   │   └── ... (sector, priority, category)
│   │   │
│   │   ├── utils/                    # Utilities
│   │   │   └── helpers.py            # Paginator, formatters
│   │   │
│   │   ├── api/
│   │   │   └── deps.py               # Dependency injection (auth)
│   │   │
│   │   └── ws/                       # WebSocket (future)
│   │       └── manager.py
│   │
│   ├── alembic/                      # Database migrations
│   ├── models/                       # ML model files
│   ├── tests/                        # Test suite
│   ├── .env                          # Environment variables
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend Docker image
│   └── pyproject.toml                # Python project config
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts             # Axios client with interceptors
│   │   │   └── endpoints.ts          # All API call functions
│   │   │
│   │   ├── components/               # Reusable UI components
│   │   │   ├── ui/                   # LoadingSpinner, Gauge, etc.
│   │   │   └── layout/               # Layout components
│   │   │
│   │   ├── contexts/                 # React contexts
│   │   │   ├── AuthContext.tsx        # Authentication state
│   │   │   ├── ToastContext.tsx       # Toast notifications
│   │   │   └── TabContext.tsx         # Multi-tab management
│   │   │
│   │   ├── pages/                    # Page components
│   │   │   ├── admin/                # 18 admin pages
│   │   │   │   ├── AdminDashboard.tsx
│   │   │   │   ├── AdminOverview.tsx
│   │   │   │   ├── AdminUserStats.tsx
│   │   │   │   ├── AdminSectorStats.tsx
│   │   │   │   ├── SignalManagement.tsx
│   │   │   │   ├── SectorManagement.tsx
│   │   │   │   ├── PriorityManagement.tsx
│   │   │   │   ├── CategoryManagement.tsx
│   │   │   │   ├── NotificationManagement.tsx
│   │   │   │   ├── ReportManagement.tsx
│   │   │   │   └── ... (AuditLogs, SystemHealth, Files, etc.)
│   │   │   │
│   │   │   ├── signals/              # 11 signal pages
│   │   │   │   ├── SignalList.tsx
│   │   │   │   ├── SignalDetail.tsx
│   │   │   │   ├── SignalCreate.tsx
│   │   │   │   ├── SignalEdit.tsx
│   │   │   │   └── SignalMap.tsx
│   │   │   │
│   │   │   ├── auth/                 # Auth pages
│   │   │   │   ├── Login.tsx
│   │   │   │   ├── Register.tsx
│   │   │   │   ├── ForgotPassword.tsx
│   │   │   │   ├── ResetPassword.tsx
│   │   │   │   └── VerifyEmail.tsx
│   │   │   │
│   │   │   ├── profile/
│   │   │   ├── reports/
│   │   │   ├── map/
│   │   │   └── Dashboard.tsx
│   │   │
│   │   ├── App.tsx                   # Router configuration
│   │   └── main.tsx                  # Entry point
│   │
│   ├── package.json
│   ├── vite.config.ts                # Vite config with API proxy
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── tsconfig.json
│
├── docker-compose.yml                # 3-service orchestration
├── .gitignore
├── AGENTS.md                         # Development session log
└── README.md                         # This file
```

---

## 🗄️ Database Schema

### Entity Relationship Overview

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  users   │◄────│ signals  │────►│categories│     │ sectors  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                                  │
     │                │                                  │
     ▼                ▼                                  ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│password_ │     │ reports  │     │notifica- │     │audit_logs│
│_reset_   │     │          │     │ tions    │     │          │
│ tokens   │     └──────────┘     └──────────┘     └──────────┘
└──────────┘
```

### Tables

| Table | Description | Key Columns |
|---|---|---|
| **users** | System users (citizens, workers, admins) | id, email, username, hashed_password, role (enum: ADMIN/CITIZEN/SECTOR), status (enum: ACTIVE/INACTIVE/SUSPENDED/PENDING_VERIFICATION), sector_id (FK), notification preferences, timestamps |
| **signals** | Problem reports | id, title, description, location (lat/lng), category_id (FK), priority_id (FK), user_id (FK), sector_id (FK), status (enum: 9 states), images, safety_risk_level, affected_people_count, is_deleted, deleted_at, timestamps |
| **categories** | Problem categories | id, name, type (enum: INFRASTRUCTURE/ENVIRONMENT/SAFETY/SERVICES/ADMINISTRATION), parent_id (self-ref FK), status (enum), priority_id (FK), sla_hours, icon |
| **priorities** | Priority levels | id, name, level (1-5), color, sla_hours, escalation_timeout_hours, notification_templates |
| **sectors** | City service sectors | id, name, type (enum: 9 types), status, region (GeoJSON polygon), contact_email, contact_phone, performance_metrics |
| **reports** | AI-generated reports | id, title, signal_id (FK), generated_by (FK), report_type (enum), status (enum), statistics (JSON), analytics_data (JSON), summary, charts_data, timestamps |
| **notifications** | Multi-channel messages | id, user_id (FK), signal_id (FK), notification_type (enum: 11 types), channel (enum: EMAIL/SMS/WHATSAPP/PUSH), priority (enum), status (enum), recipient_email, recipient_phone, sent_at, delivered_at, error_message, timestamps |
| **audit_logs** | Audit trail | id, user_id (FK), action, entity_type, entity_id, changes (JSON), ip_address, timestamp |
| **password_reset_tokens** | Password reset flow | id, user_id (FK), token, expires_at, used |

### PostgreSQL Enums

The database uses native PostgreSQL ENUM types for all status/type fields:
- `userrole`, `userstatus`
- `signalstatus` (9 values: DRAFT, PENDING, VERIFIED, IN_PROGRESS, RESOLVED, CLOSED, REJECTED, ARCHIVED, ESCALATED)
- `categorytype`, `categorystatus`
- `prioritylevel`, `severitylevel`, `urgencylevel`, `impactlevel`
- `reporttype`, `reportfrequency`, `reportstatus`
- `notificationtype`, `notificationchannel`, `notificationpriority`, `notificationstatus`
- `sectortype`, `sectorstatus`
- `signalsource`, `verificationstatus`

---

## 🌐 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns access + refresh tokens) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password with token |
| POST | `/api/v1/auth/verify-email` | Verify email address |

### Signals (Problem Reports)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/signals/` | List signals (paginated, filterable) |
| POST | `/api/v1/signals/` | Create new signal |
| GET | `/api/v1/signals/{id}` | Get signal details |
| PUT | `/api/v1/signals/{id}` | Update signal |
| DELETE | `/api/v1/signals/{id}` | Soft-delete signal |
| PATCH | `/api/v1/signals/{id}/status` | Transition signal status |

### Notifications
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/notifications/send` | Send notification (single/bulk/group) |
| GET | `/api/v1/notifications/` | List notifications (paginated) |
| GET | `/api/v1/notifications/stats` | Notification statistics |
| POST | `/api/v1/notifications/{id}/retry` | Retry failed notification |
| POST | `/api/v1/notifications/{id}/cancel` | Cancel pending notification |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/analytics/trends` | Signal trends (7/14/30/90d) |
| GET | `/api/v1/analytics/hotspots` | Geographic hotspot detection |
| GET | `/api/v1/analytics/predictions` | Predictive analytics |
| GET | `/api/v1/analytics/summary-report` | Summary dashboard report |

### AI
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ai/classify` | Classify signal text into category |
| POST | `/api/v1/ai/assess-priority` | Assess signal priority |
| POST | `/api/v1/ai/predict-trends` | Predict signal volume trends |
| POST | `/api/v1/ai/detect-anomalies` | Detect anomalies in signal data |
| GET | `/api/v1/ai/insights` | AI insights dashboard data |
| GET | `/api/v1/ai/model-info` | AI model metadata |

### Administration
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/admin/stats/signals` | Signal statistics |
| GET | `/api/v1/admin/stats/users` | User statistics |
| GET | `/api/v1/admin/stats/sectors` | Sector performance stats |
| GET | `/api/v1/admin/audit-logs` | Audit trail logs |
| GET | `/api/v1/admin/system-health` | System health status |

### Reports, Users, Categories, Priorities, Sectors, Map, Files
Full CRUD endpoints available for each resource under their respective prefixes.

**Interactive API documentation** is available at `http://localhost:8000/docs` (Swagger UI) when running in development mode.

---

## 🔧 Core Components

### 1. Notification Service
The heart of the communication system, supporting 4 channels:

- **Email**: Gmail SMTP with Jinja2 templates, graceful degradation to console logging on failure
- **SMS**: TextBelt (free tier, 1/day) → email-to-SMS carrier gateway → mock fallback chain
- **WhatsApp**: pywhatkit (WhatsApp Web automation, free, no API key)
- **Push**: Firebase Cloud Messaging HTTP/2 protocol

**Features:** Retry logic with configurable max_retries and delays, priority-based routing, bulk sending, user auto-population, delivery tracking, rate limiting.

### 2. AI Service
Machine learning pipeline for intelligent signal processing:

- **Classification**: scikit-learn pipeline with TF-IDF vectorization + logistic regression, fine-tuned with Hugging Face transformers
- **Priority Assessment**: Multi-criteria scoring (urgency × impact × severity × location risk)
- **Trend Prediction**: Time-series forecasting using ARIMA/prophet-style models
- **Anomaly Detection**: Isolation Forest and statistical methods for outlier detection

### 3. Analytics Service
Real-time business intelligence:

- **Trend Analysis**: Signal volume over configurable periods with growth rate calculation
- **Hotspot Detection**: DBSCAN clustering on signal locations for identifying problem clusters
- **Performance Metrics**: Per-sector resolution rates, average response times, citizen satisfaction
- **Predictive Forecasting**: ML-based predictions for future signal volumes

### 4. Authentication & Authorization
- **JWT dual-token strategy**: Short-lived access tokens (30 min) + long-lived refresh tokens (7 days)
- **Password hashing**: bcrypt via passlib
- **Role-based access control**: Three roles with decorator-based guards (`get_current_user`, `get_current_admin`, `get_current_sector_user`)
- **Token refresh interceptor**: Frontend Axios interceptor automatically refreshes expired tokens

### 5. Frontend Dashboard
Comprehensive admin panel with:
- Real-time KPI cards (total signals, by status, by priority)
- Sector performance comparison table
- Signal management with workflow status badges
- Notification management interface with send/retry/cancel
- Category, priority, and sector CRUD management
- Audit log viewer with filtering
- System health monitoring
- Interactive maps with Leaflet integration

---

## 📬 Notification System

### Channel Configuration

| Channel | Provider | Configuration | Fallback |
|---|---|---|---|
| **Email** | Gmail SMTP | `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD` | Console logging |
| **SMS** | TextBelt | Free API (1 SMS/day) → email-to-SMS gateway | Mock/console |
| **WhatsApp** | pywhatkit | WhatsApp Web automation | Mock/console |
| **Push** | Firebase Cloud Messaging | `FIREBASE_CREDENTIALS_PATH`, `FCM_SERVER_KEY` | Mock/console |

### Delivery Flow

1. **Validate** recipient and channel
2. **Auto-populate** user contact info from database (for `single_user` sends)
3. **Attempt delivery** via configured provider
4. **Handle errors** with configurable retry logic
5. **Track status** (PENDING → SENT → DELIVERED / FAILED)
6. **Log** all delivery attempts in the notification record

---

## 🤖 AI/ML Pipeline

### Classification Model

- **Input**: Signal description text + optional image URLs + location
- **Preprocessing**: Lowercasing, punctuation removal, stopword removal, stemming
- **Feature Extraction**: TF-IDF vectorization (n-grams 1-3)
- **Classifier**: Logistic Regression with GridSearchCV hyperparameter tuning
- **Accuracy**: ~85% on validation set (configurable confidence threshold via `AI_CONFIDENCE_THRESHOLD=0.7`)

### Priority Scoring

- **Factors**: Severity level (1-5), urgency (1-5), impact (1-5), affected population, proximity to critical infrastructure
- **Formula**: `priority_score = w₁·severity + w₂·urgency + w₃·impact + w₄·population_factor`
- **Output**: Priority level (1=CRITICAL through 5=INFO)

### Trend Prediction

- **Method**: Time-series decomposition + linear regression on historical signal volumes
- **Horizons**: 7 days, 14 days, 30 days, 90 days
- **Output**: Predicted volume, trend direction (increasing/decreasing/stable), confidence level, weekly breakdown

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 15+** (or Docker)
- **Redis 7+** (or Docker)
- **Git**

### Option 1: Quick Start with Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/urbain-sustainability.git
cd urbain-sustainability

# 2. Configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your settings (see Configuration section)

# 3. Start all services
docker-compose up --build

# 4. Access the application
# Backend API:  http://localhost:8000
# API Docs:     http://localhost:8000/docs
# Frontend:     http://localhost:5173 (or configured port)
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your database credentials and other settings

# 6. Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

#### Database Setup (Manual)

```bash
# Option A: Using Docker (recommended)
docker run -d \
  --name urbain-db \
  -e POSTGRES_USER=username \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=urbain_sustainability \
  -p 5433:5432 \
  postgres:15

# Option B: Using local PostgreSQL installation
# Create database manually:
createdb -U username urbain_sustainability

# The tables are created automatically on application startup
# via SQLAlchemy's Base.metadata.create_all
```

#### Redis Setup (Manual)

```bash
# Using Docker (recommended)
docker run -d --name urbain-redis -p 6379:6379 redis:7
```

---

## ⚙️ Configuration

### Environment Variables (`backend/.env`)

```ini
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability
DATABASE_TEST_URL=postgresql+asyncpg://username:password@localhost:5433/urbain_sustainability_test

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google Maps (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Email (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=Urbain Sustainability System

# AI Model
AI_MODEL_PATH=./models/urban_classifier.pkl
AI_CONFIDENCE_THRESHOLD=0.7

# Application
APP_NAME=Urbain Sustainability System
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Notifications
WHATSAPP_PROVIDER=pywhatkit

# Firebase (optional)
FIREBASE_CREDENTIALS_PATH=
FCM_SERVER_KEY=
```

---

## 🖥️ Running the System

### Terminal Commands Quick Reference

```bash
# ─── START ALL SERVICES (Docker) ───
docker-compose up -d                     # Start all services in background
docker-compose up --build                # Build and start with rebuilt images
docker-compose logs -f                   # Follow all logs

# ─── BACKEND ───
# Start backend server (development with hot reload)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run with custom port
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Run in production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# ─── FRONTEND ───
# Start frontend dev server
cd frontend
npm run dev                              # Starts on http://localhost:5173

# Build for production
npm run build                            # Output in dist/

# Preview production build
npm run preview

# ─── DATABASE ───
# Start PostgreSQL with Docker
docker run -d --name urbain-db \
  -e POSTGRES_USER=username \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=urbain_sustainability \
  -p 5433:5432 \
  postgres:15

# Run Alembic migration (if using migrations)
cd backend
alembic upgrade head                     # Apply pending migrations
alembic revision --autogenerate -m "description"  # Create new migration

# ─── REDIS ───
docker run -d --name urbain-redis -p 6379:6379 redis:7

# ─── TESTS ───
cd backend
pytest tests/                            # Run all tests
pytest -v                                # Verbose output
pytest -k "notification"                 # Run specific tests
pytest --cov=app tests/                  # With coverage report

# ─── OTHER ───
# Check application health
curl http://localhost:8000/health

# View API docs in browser
# Open http://localhost:8000/docs (Swagger UI)
# Open http://localhost:8000/redoc (ReDoc)

# Stop all services
docker-compose down
docker-compose down -v                   # Also remove volumes

# View logs
docker-compose logs -f backend           # Backend logs only
docker-compose logs -f db                # Database logs only
```

### Default Test Credentials

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@urbain.com` | `Admin123!` |
| **Citizen** | `citizen@urbain.com` | `Citizen123!` |

> **Note**: These credentials are created by the database seed script. Run `python seed_db.py` in the backend directory to populate sample data.

---

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_notifications.py -v

# Run with coverage
pytest --cov=app tests/ --cov-report=html

# Run tests matching a keyword
pytest -k "signal or notification"
```

**Test coverage includes:**
- ✅ Authentication & authorization flows
- ✅ CRUD operations for all entities
- ✅ Signal status transitions
- ✅ Notification delivery (all channels)
- ✅ AI classification and priority assessment
- ✅ Analytics computation
- ✅ Error handling and edge cases

---

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start in production mode
docker-compose -f docker-compose.yml up -d --build

# Scale backend workers
docker-compose up -d --scale backend=4

# Monitor logs
docker-compose logs -f --tail=100
```

### Docker Services

| Service | Port | Health Check |
|---|---|---|
| **backend** | 8000 | `/health` endpoint |
| **db** (PostgreSQL 15) | 5433 | `pg_isready` |
| **redis** (Redis 7) | 6379 | `redis-cli ping` |

All services use Docker volumes for persistent data and include restart policies for reliability.

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m "Add amazing feature"`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow existing code style (black, isort for Python; ESLint + Prettier for TypeScript)
- Write tests for new features
- Update documentation as needed
- Use the conventional commits format: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, etc.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ for smarter cities
</p>
