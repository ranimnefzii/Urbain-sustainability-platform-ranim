import factory
from datetime import datetime, timezone
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category, CategoryType, CategoryStatus
from app.models.priority import Priority, PriorityLevel, SeverityLevel, UrgencyLevel, ImpactLevel
from app.models.signal import Signal, SignalStatus, SignalSource, VerificationStatus
from app.models.sector import Sector, SectorType, SectorStatus
from app.models.report import Report, ReportType, ReportStatus, ReportFrequency
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationPriority, NotificationStatus


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    hashed_password = "$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5JqPf5OYpGkfYOBpJFxG1kq"
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = "+21612345678"
    role = UserRole.CITIZEN
    status = UserStatus.ACTIVE
    is_email_verified = True
    is_phone_verified = False
    email_notifications_enabled = True
    sms_notifications_enabled = False
    push_notifications_enabled = True
    preferred_language = "fr"
    country = "Tunisia"
    total_signals_created = 0
    total_signals_processed = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        citizen = factory.Trait(
            role=UserRole.CITIZEN,
            is_email_verified=True
        )
        admin = factory.Trait(
            role=UserRole.ADMIN,
            email=factory.Sequence(lambda n: f"admin{n}@urbain.tn"),
            username=factory.Sequence(lambda n: f"admin{n}")
        )
        sector_user = factory.Trait(
            role=UserRole.SECTOR,
            email=factory.Sequence(lambda n: f"sector{n}@urbain.tn"),
            username=factory.Sequence(lambda n: f"sector_user{n}"),
            sector_id=factory.Sequence(lambda n: n + 1)
        )
        unverified = factory.Trait(
            is_email_verified=False,
            status=UserStatus.PENDING_VERIFICATION
        )
        inactive = factory.Trait(
            status=UserStatus.INACTIVE
        )


class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Category {n}")
    code = factory.Sequence(lambda n: f"CAT{n:03d}")
    description = factory.Faker("sentence")
    parent_id = None
    level = 1
    sort_order = 0
    category_type = CategoryType.INFRASTRUCTURE
    status = CategoryStatus.ACTIVE
    default_priority_level = 3
    default_severity_level = 2
    ai_confidence_threshold = 70
    requires_image_verification = False
    default_processing_time_hours = 24
    auto_assignment_enabled = True
    requires_approval = False
    auto_notify_citizen = True
    auto_notify_sector = True
    total_signals = 0
    avg_resolution_time_hours = 0
    satisfaction_rate = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class PriorityFactory(factory.Factory):
    class Meta:
        model = Priority

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Priority {n}")
    code = factory.Sequence(lambda n: f"PRI{n:03d}")
    description = factory.Faker("sentence")
    priority_level = PriorityLevel.MEDIUM
    severity_level = SeverityLevel.MODERATE
    urgency_level = UrgencyLevel.NORMAL
    impact_level = ImpactLevel.LOCAL
    max_response_time_minutes = 120
    max_resolution_time_hours = 48
    escalation_time_hours = 24
    ai_weight = 5
    auto_assignment_threshold = 80
    requires_human_review = False
    notification_frequency = "normal"
    escalation_enabled = True
    requires_approval = False
    can_be_reassigned = True
    requires_photo_evidence = False
    total_signals = 0
    avg_resolution_time_hours = 0
    escalation_rate = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        critical = factory.Trait(
            name="Critical",
            code="CRIT",
            priority_level=PriorityLevel.CRITICAL,
            severity_level=SeverityLevel.EXTREME,
            urgency_level=UrgencyLevel.IMMEDIATE,
            impact_level=ImpactLevel.WIDESPREAD,
            max_response_time_minutes=15,
            max_resolution_time_hours=4,
            escalation_time_hours=1
        )
        high = factory.Trait(
            name="High",
            code="HIGH",
            priority_level=PriorityLevel.HIGH,
            severity_level=SeverityLevel.SEVERE,
            urgency_level=UrgencyLevel.URGENT,
            impact_level=ImpactLevel.NEIGHBORHOOD,
            max_response_time_minutes=60,
            max_resolution_time_hours=24,
            escalation_time_hours=4
        )
        low = factory.Trait(
            name="Low",
            code="LOW",
            priority_level=PriorityLevel.LOW,
            severity_level=SeverityLevel.MINOR,
            urgency_level=UrgencyLevel.LOW,
            impact_level=ImpactLevel.INDIVIDUAL,
            max_response_time_minutes=480,
            max_resolution_time_hours=168,
            escalation_time_hours=72
        )


class SectorFactory(factory.Factory):
    class Meta:
        model = Sector

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Sector {n}")
    code = factory.Sequence(lambda n: f"SEC{n:03d}")
    description = factory.Faker("sentence")
    sector_type = SectorType.ROADS
    status = SectorStatus.ACTIVE
    email = factory.Sequence(lambda n: f"sector{n}@urbain.tn")
    phone = "+21612345678"
    address = factory.Faker("address")
    city = "Tunis"
    max_daily_signals = 100
    avg_processing_time_hours = 24
    priority_level = 3
    auto_assignment_enabled = True
    escalation_enabled = True
    ai_confidence_threshold = 70
    total_signals_processed = 0
    avg_resolution_time_hours = 0
    satisfaction_rate = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class SignalFactory(factory.Factory):
    class Meta:
        model = Signal

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Sequence(lambda n: f"Signal {n}")
    description = factory.Faker("paragraph")
    reference_number = factory.Sequence(lambda n: f"SIG-202505-{n:06d}")
    created_by = 1
    category_id = 1
    priority_id = 1
    processed_by = None
    assigned_sector_id = None
    latitude = 36.8065
    longitude = 10.1815
    address = "123 Rue Example"
    city = "Tunis"
    country = "Tunisia"
    status = SignalStatus.SUBMITTED
    source = SignalSource.WEB
    verification_status = VerificationStatus.PENDING
    is_public = True
    is_anonymous = False
    allow_contact = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    last_activity_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        draft = factory.Trait(
            status=SignalStatus.DRAFT
        )
        under_review = factory.Trait(
            status=SignalStatus.UNDER_REVIEW
        )
        assigned = factory.Trait(
            status=SignalStatus.ASSIGNED,
            processed_by=2,
            assigned_sector_id=1,
            assigned_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        in_progress = factory.Trait(
            status=SignalStatus.IN_PROGRESS,
            processed_by=2,
            assigned_sector_id=1,
            assigned_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
            started_processing_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        resolved = factory.Trait(
            status=SignalStatus.RESOLVED,
            processed_by=2,
            resolution_description="Issue has been fixed",
            resolved_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        closed = factory.Trait(
            status=SignalStatus.CLOSED,
            processed_by=2,
            resolved_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
            closed_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        cancelled = factory.Trait(
            status=SignalStatus.CANCELLED
        )
        rejected = factory.Trait(
            status=SignalStatus.REJECTED,
            rejection_reason="Not applicable"
        )
        with_ai = factory.Trait(
            ai_confidence_score=0.85,
            ai_priority_score=0.75,
            ai_severity_score=0.6,
            ai_urgency_score=0.7,
            ai_processing_time_ms=150
        )


class ReportFactory(factory.Factory):
    class Meta:
        model = Report

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Sequence(lambda n: f"Report {n}")
    description = factory.Faker("sentence")
    report_code = factory.Sequence(lambda n: f"RPT-SIG-202505-{n:04d}")
    signal_id = None
    generated_by = 1
    sector_id = None
    report_type = ReportType.SIGNAL_ANALYSIS
    status = ReportStatus.COMPLETED
    frequency = ReportFrequency.ON_DEMAND
    is_public = False
    auto_share_enabled = False
    notification_enabled = True
    total_signals_analyzed = 0
    critical_signals_count = 0
    high_priority_count = 0
    version = 1
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class NotificationFactory(factory.Factory):
    class Meta:
        model = Notification

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Sequence(lambda n: f"Notification {n}")
    message = factory.Faker("sentence")
    notification_code = factory.Sequence(lambda n: f"NOT-SIG-202505-{n:04d}")
    user_id = 1
    signal_id = None
    report_id = None
    notification_type = NotificationType.SIGNAL_CREATED
    channel = NotificationChannel.IN_APP
    priority = NotificationPriority.NORMAL
    status = NotificationStatus.PENDING
    requires_action = False
    retry_count = 0
    max_retries = 3
    retry_delay_minutes = 5
    open_rate = 0
    click_rate = 0
    response_rate = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        sent = factory.Trait(
            status=NotificationStatus.SENT,
            sent_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        delivered = factory.Trait(
            status=NotificationStatus.DELIVERED,
            sent_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
            delivered_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        read = factory.Trait(
            status=NotificationStatus.READ,
            sent_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
            delivered_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
            read_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )
        failed = factory.Trait(
            status=NotificationStatus.FAILED,
            failed_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
            error_message="Delivery failed"
        )
