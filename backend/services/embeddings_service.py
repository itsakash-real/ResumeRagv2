

import logging
import time

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

logger.info("Loading sentence-transformer model: all-MiniLM-L6-v2 ...")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Embedding model loaded successfully.")

EMBEDDING_DIM = 384


def embed_text(text: str) -> np.ndarray:
    """
    Embeds a single string into a normalized 384-dim float32 vector.

    Args:
        text: Input string to embed (e.g., the resume summary).

    Returns:
        np.ndarray of shape (384,), dtype float32, L2-normalized.
    """
    start = time.perf_counter()

    vector: np.ndarray = model.encode(
        text,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    elapsed = time.perf_counter() - start
    logger.info(
        "embed_text — shape=%s, dtype=%s, elapsed=%.3fs",
        vector.shape,
        vector.dtype,
        elapsed,
    )

    return vector.astype(np.float32)


def embed_batch(texts: list[str]) -> np.ndarray:
    """
    Embeds a list of strings into a normalized (N, 384) float32 matrix.

    Args:
        texts: List of strings to embed (e.g., job descriptions).

    Returns:
        np.ndarray of shape (N, 384), dtype float32, each row L2-normalized.
    """
    start = time.perf_counter()

    vectors: np.ndarray = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    elapsed = time.perf_counter() - start
    logger.info(
        "embed_batch — n=%d, shape=%s, dtype=%s, elapsed=%.3fs",
        len(texts),
        vectors.shape,
        vectors.dtype,
        elapsed,
    )

    return vectors.astype(np.float32)