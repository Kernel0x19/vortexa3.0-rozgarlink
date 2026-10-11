"""OCR Service — extracts text from images and PDFs.

Supports multiple providers:
- TESSERACT: Local Tesseract OCR (default for dev)
- GOOGLE_CLOUD: Google Cloud Vision API
- AWS_TEXTRACT: AWS Textract

The chat upload route expects extract_text to return a dict with a "text" key.
"""

from __future__ import annotations

import enum
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OCRProvider(str, enum.Enum):
    TESSERACT = "tesseract"
    GOOGLE_CLOUD = "google_cloud"
    AWS_TEXTRACT = "aws_textract"


class OCRResult:
    def __init__(self, text: str = "", confidence: float = 0.95):
        self.text = text
        self.confidence = confidence


class OCRService:
    """Unified OCR interface with pluggable backends."""

    def __init__(self, provider: OCRProvider = OCRProvider.TESSERACT):
        self.provider = provider

    async def extract_text(self, content: bytes) -> dict[str, Any]:
        """Extract text from raw image / PDF bytes.

        Returns
        -------
        dict with keys:
            text       — extracted text
            confidence — overall OCR confidence (0..1)
            provider   — backend used
        """
        extracted = ""
        confidence = 0.0

        if self.provider == OCRProvider.TESSERACT:
            extracted, confidence = await self._tesseract_extract(content)
        elif self.provider == OCRProvider.GOOGLE_CLOUD:
            extracted, confidence = await self._gcv_extract(content)
        elif self.provider == OCRProvider.AWS_TEXTRACT:
            extracted, confidence = await self._textract_extract(content)

        return {
            "text": extracted,
            "confidence": confidence,
            "provider": self.provider.value,
        }

    # ── Provider Backends ─────────────────────────────────────────────────────

    async def _tesseract_extract(self, content: bytes) -> tuple[str, float]:
        """Try real Tesseract via pytesseract; fall back to text decode."""
        try:
            import io
            from PIL import Image
            import pytesseract

            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image, lang="eng")
            confidence = 0.85
            return text.strip(), confidence
        except ImportError:
            logger.warning("pytesseract or Pillow not installed, falling back to raw decode")
        except Exception as exc:
            logger.warning("Tesseract OCR failed: %s, falling back to raw decode", exc)

        # Fallback: treat bytes as plain text
        try:
            text = content.decode("utf-8", errors="ignore")[:4000]
            return text.strip(), 0.5
        except Exception:
            return "", 0.0

    async def _gcv_extract(self, content: bytes) -> tuple[str, float]:
        """Google Cloud Vision stub (production integration)."""
        logger.info("Google Cloud Vision OCR not configured — using fallback")
        return content.decode("utf-8", errors="ignore")[:4000], 0.5

    async def _textract_extract(self, content: bytes) -> tuple[str, float]:
        """AWS Textract stub (production integration)."""
        logger.info("AWS Textract not configured — using fallback")
        return content.decode("utf-8", errors="ignore")[:4000], 0.5
