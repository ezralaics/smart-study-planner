"""Authentication utilities module.
Re-exports login_required and role_required from core.auth for backward compatibility.
"""
from core.auth import login_required, role_required

__all__ = ['login_required', 'role_required']
