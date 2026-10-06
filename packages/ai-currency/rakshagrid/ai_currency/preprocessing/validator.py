# packages/ai-currency/rakshagrid/ai_currency/preprocessing/validator.py
"""File validation utilities: magic bytes, MIME types, upload size limits, and safe temp files."""

import io
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Tuple

from PIL import Image, UnidentifiedImageError

from rakshagrid.common.exceptions.base import ValidationException
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.ai_currency.validator")

# Known magic byte signatures for allowed image formats
MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "image/jpeg": [b"\xFF\xD8\xFF"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],  # WebP also has 'WEBP' at offset 8
}

MAX_ALLOWED_SIZE: int = 15 * 1024 * 1024  # 15 MB default


def detect_mime_from_magic_bytes(data: bytes) -> Optional[str]:
    """Inspects header bytes to detect genuine image MIME type."""
    if len(data) < 12:
        return None

    # JPEG check
    if data.startswith(b"\xFF\xD8\xFF"):
        return "image/jpeg"

    # PNG check
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    # WebP check (RIFF....WEBP)
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"

    return None


def validate_image_bytes(
    image_bytes: bytes,
    claimed_content_type: Optional[str] = None,
    max_size_bytes: int = MAX_ALLOWED_SIZE,
) -> Tuple[str, int, int]:
    """Validates raw image bytes for presence, size limits, magic bytes, and image decode integrity.

    Args:
        image_bytes: Raw binary content of the uploaded file.
        claimed_content_type: Optional MIME type from HTTP Content-Type header.
        max_size_bytes: Maximum permitted payload size in bytes.

    Returns:
        Tuple of (detected_mime_type, width, height).

    Raises:
        ValidationException: If file is empty, oversized, has invalid magic bytes, or is corrupt.
    """
    if not image_bytes or len(image_bytes) == 0:
        raise ValidationException("Uploaded currency image file is empty (0 bytes).")

    size = len(image_bytes)
    if size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        raise ValidationException(
            f"Uploaded file exceeds maximum allowed size of {max_mb:.1f} MB (received {actual_mb:.2f} MB)."
        )

    # Magic byte inspection
    detected_mime = detect_mime_from_magic_bytes(image_bytes)
    if detected_mime is None:
        raise ValidationException(
            "Invalid image file: magic bytes header does not match supported image formats (JPEG, PNG, WebP)."
        )

    # Claimed MIME type verification
    if claimed_content_type and claimed_content_type != "application/octet-stream":
        normalized_claimed = claimed_content_type.lower().split(";")[0].strip()
        if not normalized_claimed.startswith("image/"):
            raise ValidationException(
                f"Invalid Content-Type header '{claimed_content_type}'. Image file is required."
            )

    # Decode verification via PIL to detect truncated or corrupt image data
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()
            width, height = img.size
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValidationException(f"Uploaded file cannot be decoded as a valid image: {exc}") from exc

    return detected_mime, width, height


@contextmanager
def safe_temporary_image(image_bytes: bytes, suffix: str = ".jpg") -> Generator[Path, None, None]:
    """Context manager for safe temporary file creation with guaranteed cleanup.

    Ensures secure permissions, immediate flush, and deterministic deletion in all exit paths.
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_path = Path(temp_file.name)
    try:
        temp_file.write(image_bytes)
        temp_file.flush()
        temp_file.close()
        yield temp_path
    finally:
        try:
            if temp_path.exists():
                os.remove(temp_path)
        except OSError as exc:
            logger.warning("Could not delete temporary image file %s: %s", temp_path, exc)
