"""
TRUSTLENS AI - Validation & Input Sanitization Utilities
"""

import re
from typing import Optional


def is_valid_email(email: str) -> bool:
    """Validates email format using standard regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def is_valid_url(url: str) -> bool:
    """Validates URL syntax without network lookup."""
    pattern = r"^(https?://|www\.)[a-zA-Z0-9\-\._~:/?#\[\]@!$&'\(\)\*\+,;=%]+$"
    return bool(re.match(pattern, url.strip(), re.IGNORECASE))


def sanitize_input_text(text: str) -> str:
    """Normalizes excessive whitespace and strips dangerous null bytes."""
    clean = text.replace("\x00", "")
    clean = re.sub(r"[ \t]+", " ", clean)
    return clean.strip()
