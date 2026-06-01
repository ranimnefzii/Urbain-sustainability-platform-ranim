from typing import Optional, List, Dict, Set, Tuple
from enum import Enum


class Permission(str, Enum):
    # Signal permissions
    SIGNAL_CREATE = "signal:create"
    SIGNAL_READ = "signal:read"
    SIGNAL_UPDATE = "signal:update"
    SIGNAL_DELETE = "signal:delete"
    SIGNAL_RESOLVE = "signal:resolve"
    SIGNAL_ASSIGN = "signal:assign"
    SIGNAL_ESCALATE = "signal:escalate"
    SIGNAL_FEEDBACK = "signal:feedback"
    SIGNAL_LIST_ALL = "signal:list_all"

    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"
    USER_ACTIVATE = "user:activate"

    # Notification permissions
    NOTIFICATION_CREATE = "notification:create"
    NOTIFICATION_SEND = "notification:send"
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_MANAGE = "notification:manage"

    # Report permissions
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_DELETE = "report:delete"
    REPORT_EXPORT = "report:export"

    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    ADMIN_STATS = "admin:stats"
    ADMIN_CONFIG = "admin:config"
    ADMIN_AUDIT = "admin:audit"

    # Category permissions
    CATEGORY_MANAGE = "category:manage"

    # Priority permissions
    PRIORITY_MANAGE = "priority:manage"

    # Sector permissions
    SECTOR_MANAGE = "sector:manage"

    # AI permissions
    AI_ANALYZE = "ai:analyze"
    AI_BATCH = "ai:batch"
    AI_INSIGHTS = "ai:insights"

    # File permissions
    FILE_UPLOAD = "file:upload"
    FILE_DELETE = "file:delete"


ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    "admin": {
        Permission.SIGNAL_CREATE, Permission.SIGNAL_READ, Permission.SIGNAL_UPDATE,
        Permission.SIGNAL_DELETE, Permission.SIGNAL_RESOLVE, Permission.SIGNAL_ASSIGN,
        Permission.SIGNAL_ESCALATE, Permission.SIGNAL_FEEDBACK, Permission.SIGNAL_LIST_ALL,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.USER_DELETE, Permission.USER_MANAGE_ROLES, Permission.USER_ACTIVATE,
        Permission.NOTIFICATION_CREATE, Permission.NOTIFICATION_SEND, Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_MANAGE,
        Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_DELETE,
        Permission.REPORT_EXPORT,
        Permission.ADMIN_ACCESS, Permission.ADMIN_STATS, Permission.ADMIN_CONFIG,
        Permission.ADMIN_AUDIT,
        Permission.CATEGORY_MANAGE, Permission.PRIORITY_MANAGE, Permission.SECTOR_MANAGE,
        Permission.AI_ANALYZE, Permission.AI_BATCH, Permission.AI_INSIGHTS,
        Permission.FILE_UPLOAD, Permission.FILE_DELETE,
    },
    "sector_user": {
        Permission.SIGNAL_CREATE, Permission.SIGNAL_READ, Permission.SIGNAL_UPDATE,
        Permission.SIGNAL_RESOLVE, Permission.SIGNAL_ASSIGN, Permission.SIGNAL_FEEDBACK,
        Permission.NOTIFICATION_READ, Permission.NOTIFICATION_CREATE,
        Permission.REPORT_CREATE, Permission.REPORT_READ,
        Permission.AI_ANALYZE,
        Permission.FILE_UPLOAD,
    },
    "citizen": {
        Permission.SIGNAL_CREATE, Permission.SIGNAL_READ,
        Permission.SIGNAL_FEEDBACK,
        Permission.NOTIFICATION_READ,
        Permission.FILE_UPLOAD,
    },
}


def get_user_permissions(role: str) -> Set[Permission]:
    return ROLE_PERMISSIONS.get(role.lower(), set())


def has_permission(role: str, permission: Permission) -> bool:
    return permission in get_user_permissions(role)


def require_permission(role: str, permission: Permission) -> bool:
    return has_permission(role, permission)


def get_role_hierarchy() -> Dict[str, int]:
    return {
        "citizen": 0,
        "sector_user": 1,
        "admin": 2,
    }


def is_role_at_least(user_role: str, minimum_role: str) -> bool:
    hierarchy = get_role_hierarchy()
    return hierarchy.get(user_role, -1) >= hierarchy.get(minimum_role, 0)
