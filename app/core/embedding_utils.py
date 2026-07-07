"""
embedding_utils.py
==================
Pure-math helpers for embedding normalization and similarity scoring.
Kept separate from face_utils.py (model inference) and database_utils.py
(persistence) so the linear-algebra logic is independently testable.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np


def l2_normalize(embedding: np.ndarray) -> np.ndarray:
    """L2-normalize a 1-D embedding vector so cosine similarity reduces
    to a simple dot product. Guards against division by zero."""
    norm = np.linalg.norm(embedding)
    if norm < 1e-10:
        return embedding.astype(np.float32)
    return (embedding / norm).astype(np.float32)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two (assumed L2-normalized)
    embedding vectors."""
    a = l2_normalize(vec_a)
    b = l2_normalize(vec_b)
    return float(np.dot(a, b))


def batch_cosine_similarity(query: np.ndarray, gallery: np.ndarray) -> np.ndarray:
    """Vectorized cosine similarity between one query embedding and an
    (N, D) matrix of gallery embeddings. Returns an (N,) similarity array.
    """
    if gallery.size == 0:
        return np.empty((0,), dtype=np.float32)
    q = l2_normalize(query)
    norms = np.linalg.norm(gallery, axis=1, keepdims=True)
    norms[norms < 1e-10] = 1e-10
    normalized_gallery = gallery / norms
    return normalized_gallery @ q


def best_match(
    query: np.ndarray, gallery_embeddings: np.ndarray, gallery_labels: List[str]
) -> Tuple[str, float]:
    """Find the single best-matching label for a query embedding against
    a stacked gallery of (possibly many-per-person) embeddings.

    Because every enrolled image's embedding is stored individually
    (never averaged), the match is determined by the single closest
    embedding in the entire gallery, which is the recommended InsightFace
    matching strategy for multi-image enrollment.
    """
    if gallery_embeddings.shape[0] == 0:
        return "", -1.0
    similarities = batch_cosine_similarity(query, gallery_embeddings)
    best_idx = int(np.argmax(similarities))
    return gallery_labels[best_idx], float(similarities[best_idx])
