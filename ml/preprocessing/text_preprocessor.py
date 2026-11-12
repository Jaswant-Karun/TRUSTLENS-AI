"""
TRUSTLENS AI - Multilingual Text Preprocessor
Performs Unicode normalization, PII sanitization with token preservation,
URL extraction, and script-aware language classification (English, Hindi, Hinglish).
"""

import re
import unicodedata
from typing import Dict, Any, List, Tuple


# Regex patterns for PII and entity extraction
URL_REGEX = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(r"(?:\+?91[\-\s]?)?[6-9]\d{9}\b|\b\d{5}[\-\s]?\d{5}\b")
OTP_REGEX = re.compile(r"\b\d{4,6}\b(?=\s*(?:is your|as your|otp|verification code|pin))", re.IGNORECASE)
UPI_REGEX = re.compile(r"\b[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|paytm|ybl|apl|upi)\b", re.IGNORECASE)

# Hinglish vocabulary markers
HINGLISH_KEYWORDS = {
    "aapka", "karein", "turant", "paisa", "khata", "sampark", "kare", "hai",
    "bheje", "band", "hoga", "shukriya", "dhyan", "karo", "karen", "sakte",
    "par", "nahi", "raha", "gaya", "kripya", "jaldi", "inam", "jeet", "crore",
    "lakh", "paaye", "bhejo", "paas", "liye", "bhi", "sirf", "aaj"
}


class MultilingualTextPreprocessor:
    """Preprocesses multilingual messages while preserving critical social engineering cues."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Applies NFKC normalization to resolve Devanagari ligatures and composite characters."""
        if not text:
            return ""
        return unicodedata.normalize("NFKC", str(text))

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Collapses duplicate spaces/tabs while preserving overall message structure."""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        return text.strip()

    @staticmethod
    def extract_urls(text: str) -> Tuple[str, List[str]]:
        """Extracts URLs into a distinct feature list and replaces them with a normalized token."""
        urls = URL_REGEX.findall(text)
        sanitized = URL_REGEX.sub("[URL]", text)
        return sanitized, urls

    @staticmethod
    def mask_pii(text: str) -> str:
        """
        Masks personal identifiers (phone numbers, emails, OTPs) to protect privacy,
        while preserving technical tokens so downstream models detect the presence of credential requests.
        """
        text = EMAIL_REGEX.sub("[EMAIL]", text)
        text = UPI_REGEX.sub("[UPI_ID]", text)
        text = OTP_REGEX.sub("[OTP]", text)
        text = PHONE_REGEX.sub("[PHONE]", text)
        return text

    @staticmethod
    def identify_language(text: str) -> str:
        """
        Classifies message into English, Hindi (Devanagari), or Romanized Hinglish.
        """
        # 1. Devanagari script detection
        devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
        if devanagari_chars >= 3:
            return "Hindi"

        # 2. Romanized Hinglish token detection
        tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
        hinglish_matches = tokens & HINGLISH_KEYWORDS
        if len(hinglish_matches) >= 2 or (len(hinglish_matches) == 1 and len(tokens) <= 6):
            return "Hinglish"

        return "English"

    def preprocess(self, raw_text: str, mask_personal_data: bool = True) -> Dict[str, Any]:
        """
        Executes full preprocessing pipeline on a message.
        Returns a dictionary containing the cleaned text, extracted entities, and language tag.
        """
        if not raw_text or pd_isna(raw_text):
            return {
                "cleaned_text": "",
                "extracted_urls": [],
                "language": "Unknown",
                "char_length": 0,
                "word_count": 0,
            }

        # Step 1: Unicode Normalization
        text = self.normalize_unicode(str(raw_text))

        # Step 2: URL Extraction
        text_with_url_token, urls = self.extract_urls(text)

        # Step 3: PII Masking (optional, preserves tokens)
        processed_text = self.mask_pii(text_with_url_token) if mask_personal_data else text_with_url_token

        # Step 4: Whitespace cleanup
        cleaned_text = self.normalize_whitespace(processed_text)

        # Step 5: Language identification
        lang = self.identify_language(text)

        return {
            "cleaned_text": cleaned_text,
            "extracted_urls": urls,
            "language": lang,
            "char_length": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
        }


def pd_isna(val: Any) -> bool:
    """Helper to detect NaN or None values safely without external dependency."""
    if val is None:
        return True
    if isinstance(val, float) and val != val:
        return True
    return False


text_preprocessor = MultilingualTextPreprocessor()
