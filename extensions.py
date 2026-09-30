"""Database extensions module.
Re-exports the core database instance and GUID type for backward compatibility.
"""
from core.database import db, GUID

__all__ = ['db', 'GUID']
