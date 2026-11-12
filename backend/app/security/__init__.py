"""
TRUSTLENS AI - Security Package
"""

from backend.app.security.password import hash_password, verify_password
from backend.app.security.jwt import create_access_token, decode_access_token
from backend.app.security.dependencies import (
    get_current_user,
    get_optional_current_user,
    require_role,
    require_analyst_or_admin,
    require_admin,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_optional_current_user",
    "require_role",
    "require_analyst_or_admin",
    "require_admin",
]
