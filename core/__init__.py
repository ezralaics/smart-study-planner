"""Life Planner OS (OmniLife) — Core Architectural Package.
Exposes foundational database, authentication, and module registry primitives.
"""
from core.database import db, GUID
from core.auth import login_required, role_required
from core.registry import (
    LifePlannerModule,
    registry,
    get_registered_modules,
    get_workspaces_list,
    get_module
)

__all__ = [
    'db',
    'GUID',
    'login_required',
    'role_required',
    'LifePlannerModule',
    'registry',
    'get_registered_modules',
    'get_workspaces_list',
    'get_module'
]
