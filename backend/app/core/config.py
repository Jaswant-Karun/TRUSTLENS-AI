"""
TRUSTLENS AI - Core Config Re-export
Maintains compatibility with backend.app.core.config while delegating to backend.app.config.settings.
"""

from backend.app.config.settings import settings, AppSettings

__all__ = ["settings", "AppSettings"]
