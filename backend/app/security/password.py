"""
TRUSTLENS AI - Password Hashing & Verification
Uses bcrypt to guarantee passwords are never stored or compared in plaintext.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """Hashes plaintext password using bcrypt with automatic salt generation."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False
