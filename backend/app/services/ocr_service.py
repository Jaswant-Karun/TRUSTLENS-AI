"""
TRUSTLENS AI - Screenshot OCR & Image Processing Service
Extracts digital text from uploaded screenshot evidence with robust size and format validation.
"""

import io
import re
from typing import Dict, Any, Tuple
from fastapi import UploadFile, HTTPException, status
from PIL import Image

from backend.app.config.settings import settings
from backend.app.core.logging import logger

try:
    import pytesseract
except ImportError:
    pytesseract = None


class ScreenshotOCRService:
    """Safely ingests and extracts communication text from screenshot images."""

    async def validate_and_read_image(self, file: UploadFile) -> Tuple[bytes, Image.Image]:
        """Validates file MIME type, size limit, and PIL image decoding."""
        # 1. Content Type Check
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file format '{file.content_type}'. Allowed formats: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
            )

        # 2. Size Limit Check
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Uploaded image exceeds maximum allowable limit of {max_mb} MB.",
            )

        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes).",
            )

        # 3. PIL Image Validation
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()  # Verify file integrity
            # Reopen because verify() consumes image stream
            image = Image.open(io.BytesIO(contents))
            return contents, image
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or corrupted image payload: {e}",
            )

    def extract_text(self, image: Image.Image) -> Dict[str, Any]:
        """Extracts text using pytesseract if available, or returns graceful inconclusive status."""
        extracted_text = ""
        ocr_confidence = 0.0

        if pytesseract is not None:
            try:
                # Convert to RGB if needed
                if image.mode not in ("L", "RGB"):
                    image = image.convert("RGB")
                extracted_text = pytesseract.image_to_string(image).strip()
                ocr_confidence = 0.85 if len(extracted_text) > 10 else 0.20
            except Exception as e:
                logger.warning(f"Tesseract OCR execution error: {e}")
                extracted_text = ""
                ocr_confidence = 0.0

        # Clean whitespace
        cleaned_text = re.sub(r"\s+", " ", extracted_text).strip()

        return {
            "extracted_text": cleaned_text,
            "ocr_confidence": ocr_confidence,
            "has_readable_text": bool(len(cleaned_text) >= 5),
        }


ocr_service = ScreenshotOCRService()

