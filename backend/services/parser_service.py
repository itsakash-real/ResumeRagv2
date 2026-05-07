

import io
import re
import logging
import time

import pdfplumber

logger = logging.getLogger(__name__)

MIN_EXTRACTED_CHARS = 100


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extracts plain text from all pages of a PDF.

    Processing steps:
      - Opens the PDF from an in-memory bytes buffer (no disk writes).
      - Iterates all pages and collects text.
      - Collapses runs of blank lines into a single blank line.
      - Strips leading/trailing whitespace.

    Args:
        file_bytes: Raw bytes of a validated PDF file.

    Returns:
        Normalized plain-text string of the resume content.

    Raises:
        ValueError: If the extracted text is shorter than 100 chars,
                    indicating a scanned/image-only PDF.
    """
    start = time.perf_counter()

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        raw_pages: list[str] = []

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                raw_pages.append(text)

    full_text = "\n".join(raw_pages)

    # Normalize: collapse 3+ consecutive newlines → double newline
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)
    # Collapse multiple spaces/tabs on a single line into one space
    full_text = re.sub(r"[ \t]+", " ", full_text)
    full_text = full_text.strip()

    elapsed = time.perf_counter() - start
    char_count = len(full_text)

    logger.info(
        "PDF parsed — pages=%d, chars=%d, elapsed=%.3fs",
        page_count,
        char_count,
        elapsed,
    )

    if char_count < MIN_EXTRACTED_CHARS:
        raise ValueError(
            "Could not extract text — file may be a scanned image PDF."
        )

    return full_text