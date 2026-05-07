

import logging
import time

import faiss
import numpy as np

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384


def build_index(vectors: np.ndarray) -> faiss.IndexFlatIP:
    """
    Builds a flat inner-product FAISS index from a batch of normalized vectors.

    Because all vectors are L2-normalized (via sentence-transformers), inner
    product is equivalent to cosine similarity and scores fall in [0.0, 1.0].

    Args:
        vectors: np.ndarray of shape (N, 384), dtype float32.

    Returns:
        Populated faiss.IndexFlatIP ready for querying.

    Raises:
        ValueError: If vectors have wrong shape or dtype.
    """
    if vectors.ndim != 2 or vectors.shape[1] != EMBEDDING_DIM:
        raise ValueError(
            f"Expected shape (N, {EMBEDDING_DIM}), got {vectors.shape}."
        )
    if vectors.dtype != np.float32:
        vectors = vectors.astype(np.float32)

    start = time.perf_counter()
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(vectors)
    elapsed = time.perf_counter() - start

    logger.info(
        "FAISS index built — vectors=%d, elapsed=%.3fs", index.ntotal, elapsed
    )
    return index


def query_index(
    index: faiss.IndexFlatIP,
    query_vector: np.ndarray,
    k: int,
) -> list[tuple[int, float]]:
    """
    Queries the FAISS index for the top-k most similar vectors.

    Args:
        index: A populated faiss.IndexFlatIP instance.
        query_vector: np.ndarray of shape (1, 384), dtype float32.
        k: Number of nearest neighbors to return.

    Returns:
        List of (original_index, score) tuples sorted by score descending.
        Scores are in [0.0, 1.0] (cosine similarity).
    """
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)
    if query_vector.dtype != np.float32:
        query_vector = query_vector.astype(np.float32)

    # k cannot exceed the number of indexed vectors
    k = min(k, index.ntotal)

    start = time.perf_counter()
    scores, indices = index.search(query_vector, k)
    elapsed = time.perf_counter() - start

    logger.info(
        "FAISS query — k=%d, top_score=%.4f, elapsed=%.3fs",
        k,
        float(scores[0][0]) if k > 0 else 0.0,
        elapsed,
    )

    results: list[tuple[int, float]] = [
        (int(idx), float(score))
        for idx, score in zip(indices[0], scores[0])
        if idx != -1  # FAISS returns -1 for empty slots
    ]

    # Already sorted descending by FAISS, but enforce explicitly
    results.sort(key=lambda x: x[1], reverse=True)
    return results