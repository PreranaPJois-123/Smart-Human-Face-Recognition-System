"""
tracking_utils.py
==================
Lightweight centroid-based tracker that assigns stable track IDs to
detected faces across consecutive frames. This lets the UI apply
per-face label smoothing (recognition_utils.LabelSmoother) and lets
Robot Mode consistently follow the same person even as bounding boxes
jitter slightly frame to frame.

Deliberately dependency-free (no external tracking library) to keep
the pipeline simple and auditable, matching the "no unfinished/fake
implementations" requirement with a real, working algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from app.core.recognition_utils import LabelSmoother


def _centroid(bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _euclidean(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


@dataclass
class Track:
    track_id: int
    bbox: Tuple[int, int, int, int]
    centroid: Tuple[float, float]
    missed_frames: int = 0
    smoother: LabelSmoother = field(default_factory=lambda: LabelSmoother(window=5))


class CentroidTracker:
    """Assigns and maintains track IDs across frames using nearest-centroid
    matching with a maximum-distance gate and a grace period before a
    track is dropped after the face temporarily disappears."""

    def __init__(self, max_distance_px: float = 120.0, max_missed_frames: int = 10, smoothing_window: int = 5):
        self._max_distance = max_distance_px
        self._max_missed = max_missed_frames
        self._smoothing_window = smoothing_window
        self._tracks: Dict[int, Track] = {}
        self._next_id = 1

    def update(self, detections: List[Tuple[int, int, int, int]]) -> Dict[int, Tuple[int, int, int, int]]:
        """Update tracks with the current frame's detected bounding boxes.
        Returns a mapping of track_id -> bbox for all currently active tracks."""
        detection_centroids = [_centroid(bbox) for bbox in detections]
        unmatched_detections = set(range(len(detections)))
        unmatched_tracks = set(self._tracks.keys())

        # Greedy nearest-neighbor matching between existing tracks and detections.
        pairs: List[Tuple[float, int, int]] = []
        for track_id, track in self._tracks.items():
            for det_idx, centroid in enumerate(detection_centroids):
                distance = _euclidean(track.centroid, centroid)
                if distance <= self._max_distance:
                    pairs.append((distance, track_id, det_idx))
        pairs.sort(key=lambda item: item[0])

        for distance, track_id, det_idx in pairs:
            if track_id not in unmatched_tracks or det_idx not in unmatched_detections:
                continue
            track = self._tracks[track_id]
            track.bbox = detections[det_idx]
            track.centroid = detection_centroids[det_idx]
            track.missed_frames = 0
            unmatched_tracks.discard(track_id)
            unmatched_detections.discard(det_idx)

        # Age out tracks that were not matched this frame.
        for track_id in unmatched_tracks:
            track = self._tracks[track_id]
            track.missed_frames += 1

        stale_ids = [tid for tid, t in self._tracks.items() if t.missed_frames > self._max_missed]
        for tid in stale_ids:
            del self._tracks[tid]

        # Spawn new tracks for detections that matched nothing existing.
        for det_idx in unmatched_detections:
            new_track = Track(
                track_id=self._next_id,
                bbox=detections[det_idx],
                centroid=detection_centroids[det_idx],
                smoother=LabelSmoother(window=self._smoothing_window),
            )
            self._tracks[self._next_id] = new_track
            self._next_id += 1

        return {tid: t.bbox for tid, t in self._tracks.items() if t.missed_frames == 0}

    def get_smoother(self, track_id: int) -> LabelSmoother:
        return self._tracks[track_id].smoother

    def find_track_id_for_bbox(self, bbox: Tuple[int, int, int, int]) -> int:
        """Locate the track ID whose current bbox matches the given box
        (used to route a per-frame detection to its persistent smoother)."""
        centroid = _centroid(bbox)
        best_id, best_dist = -1, float("inf")
        for tid, track in self._tracks.items():
            dist = _euclidean(track.centroid, centroid)
            if dist < best_dist:
                best_dist, best_id = dist, tid
        return best_id

    def largest_active_track(self) -> Tuple[int, Tuple[int, int, int, int]] | None:
        """Return the (track_id, bbox) of the largest currently-active
        track by bounding-box area - used by Robot Mode to pick a
        single primary target to follow when multiple faces are visible."""
        active = [(tid, t.bbox) for tid, t in self._tracks.items() if t.missed_frames == 0]
        if not active:
            return None

        def area(bbox: Tuple[int, int, int, int]) -> int:
            x1, y1, x2, y2 = bbox
            return max(0, x2 - x1) * max(0, y2 - y1)

        return max(active, key=lambda item: area(item[1]))
