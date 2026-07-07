"""
distance_utils.py
==================
Monocular distance estimation using the classic "similar triangles"
approach: given a known real-world face width and a calibrated focal
length (in pixels), the distance to the camera can be recovered from
the apparent pixel width of the detected face.

    distance_cm = (known_face_width_cm * focal_length_px) / face_pixel_width

The focal length itself is a one-time calibration constant stored in
config.yaml (`distance.focal_length_px`). It can be re-derived by
measuring a face of known width at a known distance:

    focal_length_px = (face_pixel_width * distance_cm) / known_face_width_cm
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from app.config import AppConfig


class DistanceZone(Enum):
    TOO_CLOSE = "TOO_CLOSE"
    IDEAL = "IDEAL"
    TOO_FAR = "TOO_FAR"
    OUT_OF_RANGE = "OUT_OF_RANGE"


@dataclass
class DistanceReading:
    distance_cm: float
    zone: DistanceZone
    label: str
    color_hex: str


# Zone -> (display label, indicator color) mapping.
_ZONE_DISPLAY = {
    DistanceZone.TOO_CLOSE: ("TOO CLOSE", "#E74C3C"),      # red
    DistanceZone.IDEAL: ("IDEAL DISTANCE", "#2ECC71"),     # green
    DistanceZone.TOO_FAR: ("TOO FAR", "#F1C40F"),          # yellow
    DistanceZone.OUT_OF_RANGE: ("OUT OF RANGE", "#5D6D7E"),  # dark gray
}


def estimate_distance_cm(face_pixel_width: float, config: AppConfig) -> float:
    """Estimate distance (cm) from the camera to a detected face given
    its bounding-box pixel width."""
    if face_pixel_width <= 0:
        return -1.0
    known_width = config.distance.known_face_width_cm
    focal_length = config.distance.focal_length_px
    return (known_width * focal_length) / face_pixel_width


def classify_distance(distance_cm: float, config: AppConfig) -> DistanceReading:
    """Classify a distance reading into one of four zones with an
    associated display label and indicator color."""
    thresholds = config.distance

    if distance_cm < 0:
        zone = DistanceZone.OUT_OF_RANGE
    elif distance_cm <= thresholds.too_close_max_cm:
        zone = DistanceZone.TOO_CLOSE
    elif distance_cm <= thresholds.ideal_max_cm:
        zone = DistanceZone.IDEAL
    elif distance_cm <= thresholds.too_far_max_cm:
        zone = DistanceZone.TOO_FAR
    else:
        zone = DistanceZone.OUT_OF_RANGE

    label, color = _ZONE_DISPLAY[zone]
    return DistanceReading(distance_cm=distance_cm, zone=zone, label=label, color_hex=color)


def bbox_pixel_width(bbox: Tuple[int, int, int, int]) -> float:
    """Extract pixel width from an (x1, y1, x2, y2) bounding box."""
    x1, _, x2, _ = bbox
    return float(x2 - x1)


def calibrate_focal_length(face_pixel_width: float, known_distance_cm: float, known_face_width_cm: float) -> float:
    """Utility to derive a new focal length constant from a single
    calibration measurement (exposed for a future calibration wizard)."""
    if face_pixel_width <= 0:
        raise ValueError("face_pixel_width must be positive")
    return (face_pixel_width * known_distance_cm) / known_face_width_cm
