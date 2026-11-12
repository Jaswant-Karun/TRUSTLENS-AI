"""
TRUSTLENS AI - Core Database Re-export
Delegates to backend.app.database.manager while maintaining compatibility.
"""

from backend.app.database.manager import db_manager, get_db

__all__ = ["db_manager", "get_db"]
