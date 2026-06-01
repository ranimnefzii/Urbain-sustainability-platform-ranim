"""
Schemas Package - Urbain Sustainability System
Pydantic schemas pour validation et sérialisation des données
"""

from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse, 
    UserLogin, UserRegister, UserProfile, UserStats
)
from .category import (
    CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryTree, CategoryStats
)
from .signal import (
    SignalBase, SignalCreate, SignalUpdate, SignalResponse,
    SignalList, SignalAnalytics, SignalLocation
)
from .priority import (
    PriorityBase, PriorityCreate, PriorityUpdate, PriorityResponse,
    PriorityStats, PriorityAssessment
)
from .report import (
    ReportBase, ReportCreate, ReportUpdate, ReportResponse,
    ReportList, ReportAnalytics, ReportSummary
)
from .notification import (
    NotificationBase, NotificationCreate, NotificationSend, NotificationUpdate, NotificationResponse,
    NotificationList, NotificationStats
)
from .sector import (
    SectorBase, SectorCreate, SectorUpdate, SectorResponse,
    SectorStats, SectorPerformance
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "UserLogin", "UserRegister", "UserProfile", "UserStats",
    
    # Category schemas
    "CategoryBase", "CategoryCreate", "CategoryUpdate", "CategoryResponse",
    "CategoryTree", "CategoryStats",
    
    # Signal schemas
    "SignalBase", "SignalCreate", "SignalUpdate", "SignalResponse",
    "SignalList", "SignalAnalytics", "SignalLocation",
    
    # Priority schemas
    "PriorityBase", "PriorityCreate", "PriorityUpdate", "PriorityResponse",
    "PriorityStats", "PriorityAssessment",
    
    # Report schemas
    "ReportBase", "ReportCreate", "ReportUpdate", "ReportResponse",
    "ReportList", "ReportAnalytics", "ReportSummary",
    
    # Notification schemas
    "NotificationBase", "NotificationCreate", "NotificationSend", "NotificationUpdate", "NotificationResponse",
    "NotificationList", "NotificationStats",
    
    # Sector schemas
    "SectorBase", "SectorCreate", "SectorUpdate", "SectorResponse",
    "SectorStats", "SectorPerformance"
]
