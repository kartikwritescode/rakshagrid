# apps/api/src/core/upload_security.py
"""
Hardened File Upload Security Module.

Provides comprehensive validation against:
1. Oversized uploads (enforces 25 MB hard ceiling).
2. Malicious file types and deceptive Content-Type headers via magic bytes / file signatures.
3. Path traversal attacks and arbitrary filenames.
4. Uncontrolled temporary file leakage via robust context manager cleanup.
"""

import os
import re
import uuid
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Set, Tuple

from fastapi import UploadFile, HTTPException, status
from apps.api.src.config import settings
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.api.upload_security")

# Allowed extensions and magic byte signatures
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_AUDIO_EXTENSIONS: Set[str] = {".wav", ".mp3", ".ogg", ".opus", ".m4a", ".flac", ".aac"}

MAGIC_IMAGE_SIGNATURES = [
    (b"\xFF\xD8\xFF", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
]

MAGIC_AUDIO_SIGNATURES = [
    (b"OggS", "audio/ogg"),
    (b"ID3", "audio/mpeg"),
    (b"\xFF\xFB", "audio/mpeg"),
    (b"\xFF\xF3", "audio/mpeg"),
    (b"\xFF\xF2", "audio/mpeg"),
    (b"fLaC", "audio/flac"),
]


from rakshagrid.common.exceptions.base import ValidationException

def detect_magic_mime(header: bytes) -> Optional[str]:
    """Inspects magic header bytes to verify authentic MIME type without trusting client header."""
    if len(header) < 4:
        return None

    # 1. Images
    for sig, mime in MAGIC_IMAGE_SIGNATURES:
        if header.startswith(sig):
            return mime

    # WebP check vs WAV check (both start with RIFF)
    if header.startswith(b"RIFF"):
        if len(header) >= 12 and header[8:12] == b"WEBP":
            return "image/webp"
        return "audio/wav"

    # MP4 / M4A check: ....ftyp
    if len(header) >= 8 and header[4:8] == b"ftyp":
        return "audio/mp4"

    for sig, mime in MAGIC_AUDIO_SIGNATURES:
        if header.startswith(sig):
            return mime

    return None


def sanitize_filename(filename: Optional[str], default_name: str = "upload.bin") -> str:
    """
    Sanitizes file name to prevent path traversal and arbitrary filesystem overwrite.
    Rejects or neutralizes: '..', '/', '\\', null bytes, and non-printable characters.
    """
    if not filename or not filename.strip():
        return default_name

    raw_name = filename.strip()

    # Reject null bytes
    if "\x00" in raw_name:
        raise ValidationException("Invalid filename: null byte injection detected.")

    # Strip directory paths
    base_name = os.path.basename(raw_name)
    base_name = base_name.replace("/", "").replace("\\", "")

    # Sanitize characters: keep alphanumeric, dots, underscores, dashes
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", base_name)
    if not sanitized or sanitized in {".", ".."}:
        sanitized = default_name

    return sanitized


async def read_and_validate_upload(
    file: UploadFile,
    allowed_extensions: Set[str],
    allowed_mime_prefixes: Tuple[str, ...],
    max_size_bytes: Optional[int] = None,
) -> Tuple[bytes, str, str]:
    """
    Reads an uploaded file in memory while enforcing:
    1. Maximum size limit (streamed in chunks to prevent memory explosion).
    2. Extension whitelist check.
    3. Magic bytes inspection to detect genuine MIME type.
    
    Returns:
        Tuple of (file_bytes, safe_filename, detected_mime_type)
    """
    max_size = max_size_bytes or settings.MAX_UPLOAD_SIZE_BYTES
    safe_name = sanitize_filename(file.filename)
    ext = os.path.splitext(safe_name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationException(
            f"Unsupported file extension '{ext}'. Allowed extensions: {sorted(list(allowed_extensions))}"
        )

    # Stream read with size enforcement (1 MB chunks)
    CHUNK_SIZE = 1024 * 1024
    chunks: list[bytes] = []
    total_size = 0

    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload payload exceeds maximum allowed size of {max_mb:.0f} MB.",
            )
        chunks.append(chunk)

    file_bytes = b"".join(chunks)

    if len(file_bytes) == 0:
        raise ValidationException("Uploaded file is empty (0 bytes).")

    # Magic byte verification
    genuine_mime = detect_magic_mime(file_bytes[:32])
    if not genuine_mime:
        raise ValidationException(
            "File signature verification failed. The uploaded file does not match genuine binary formats."
        )

    if not any(genuine_mime.startswith(prefix) for prefix in allowed_mime_prefixes):
        raise ValidationException(
            f"File signature '{genuine_mime}' is not permitted for this endpoint."
        )

    return file_bytes, safe_name, genuine_mime



@contextmanager
def secure_temp_file(
    data: bytes,
    suffix: str = ".tmp",
    prefix: str = "rakshagrid_upload_",
) -> Generator[str, None, None]:
    """
    Context manager that safely writes data to a secure temporary file
    and guarantees immediate cleanup upon exiting the block, even if an exception occurs.
    """
    temp_dir = tempfile.gettempdir()
    temp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=temp_dir,
            prefix=prefix,
            suffix=suffix,
            delete=False,
        ) as tmp:
            tmp.write(data)
            tmp.flush()
            temp_path = tmp.name

        yield temp_path
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as err:
                logger.warning(f"Failed to clean temporary file {temp_path}: {err}")
