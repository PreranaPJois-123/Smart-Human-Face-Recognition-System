"""
recognition_utils.py
=====================
Orchestrates the real-time recognition pipeline:

    Face Detection -> Embedding Extraction -> Cosine Similarity -> Identity

Also implements temporal label smoothing so that per-frame detection
noise does not cause on-screen names/boxes to flicker between "Unknown"
and a known identity, or between two different known identities.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

import numpy as np

from app.config import AppConfig
from app.core.database_utils import FaceDatabase
from app.core.embedding_utils import best_match
from app.core.face_utils import DetectedFace, FaceAnalysisEngine

from collections import Counter


@dataclass
class RecognitionResult:
    bbox: Tuple[int, int, int, int]
    name: str
    similarity: float
    is_known: bool


class LabelSmoother:
    """Maintains a short rolling history of recognized names for a single
    tracked face and returns a majority-vote stabilized label, preventing
    flicker frame-to-frame."""

    def __init__(self, window: int):
        self._window = max(1, window)
        self._history: Deque[str] = deque(maxlen=self._window)

    def update(self, name: str) -> str:
        self._history.append(name)
        counts = Counter(self._history)
        return counts.most_common(1)[0][0]


class RecognitionEngine:
    """High-level façade combining face detection with database matching.
    Instantiated once per live session (Live Recognition / Robot Mode)."""

    def __init__(self, config: AppConfig, face_engine: FaceAnalysisEngine, database: FaceDatabase):
        self._config = config
        self._face_engine = face_engine
        self._database = database

    def recognize_frame(self, frame_bgr: np.ndarray) -> List[Tuple[DetectedFace, RecognitionResult]]:
        """Detect all faces in a frame and match each against the gallery.
        Returns a list pairing the raw DetectedFace with its RecognitionResult."""
        faces = self._face_engine.detect_faces(frame_bgr)
        gallery_embeddings, gallery_labels = self._database.stacked_gallery()
        threshold = self._config.recognition.similarity_threshold
        unknown_label = self._config.recognition.unknown_label

        output: List[Tuple[DetectedFace, RecognitionResult]] = []
        for face in faces:
            name, similarity = best_match(face.embedding, gallery_embeddings, gallery_labels)
            is_known = bool(name) and similarity >= threshold
            display_name = name if is_known else unknown_label
            output.append((
                face,
                RecognitionResult(
                    bbox=face.bbox,
                    name=display_name,
                    similarity=similarity,
                    is_known=is_known,
                ),
            ))
        return output
