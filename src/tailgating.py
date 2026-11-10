"""Reproducible *proxy* measure from NVIDIA DLI assessment (not true road distance)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Box:
    left: float
    top: float
    width: float
    height: float
    label: str = "car"
    confidence: float = 0.0


def is_potential_tailgating(box: Box, frame_width: int, frame_height: int,
                             width_ratio: float = 0.30, bottom_ratio: float = 0.90,
                             car_only: bool = True) -> bool:
    """Heuristic: box width > 30% of frame and bottom > 90% of frame.

    Mirrors the assessment's bounding-box thresholds. This is NOT a distance,
    time headway, collision risk, or proof of unsafe driving.
    """
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError('Frame dimensions must be positive')
    if car_only and box.label.strip().lower() not in ('car', 'vehicle'):
        return False
    return box.width > frame_width * width_ratio and (box.top + box.height) > frame_height * bottom_ratio


def frame_flag(boxes, width: int, height: int, **kwargs) -> int:
    """Exactly one boolean signal per frame, regardless of object count."""
    return int(any(is_potential_tailgating(box, width, height, **kwargs) for box in boxes))
