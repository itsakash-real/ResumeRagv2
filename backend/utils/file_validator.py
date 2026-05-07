

import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
PDF_MAGIC_BYTES = b"%PDF"               # 0x25 0x50 0x44 0x46


def validate_pdf(file_bytes: bytes) -> None:
    """
    Validates that the given bytes represent a valid, size-compliant PDF.

    Checks are performed in this order:
      1. Size: rejects anything over 5 MB.
      2. Magic bytes: first 4 bytes must be %PDF (25 50 44 46).

    Args:
        file_bytes: Raw bytes of the uploaded file.

    Raises:
        HTTPException 413: If file exceeds 5 MB.
        HTTPException 400: If magic bytes do not match PDF signature.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        logger.warning(
            "File rejected — size %d bytes exceeds 5 MB limit.", len(file_bytes)
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large — 5MB maximum.",
        )

    if not file_bytes[:4] == PDF_MAGIC_BYTES:
        logger.warning(
            "File rejected — magic bytes %r do not match PDF signature.", file_bytes[:4]
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type — only PDF allowed.",
        )