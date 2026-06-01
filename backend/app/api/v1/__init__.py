"""
API v1 Package - Urbain Sustainability System
Version 1 des endpoints API
"""

from . import auth
from . import users
from . import signals
from . import categories
from . import reports
from . import admin
from . import priorities
from . import sectors
from . import notifications
from . import analytics
from . import files
from . import map as map_module
from . import ai as ai_module

__all__ = ["auth", "users", "signals", "categories", "reports", "admin", "priorities", "sectors", "notifications", "analytics", "files", "map_module", "ai_module"]
