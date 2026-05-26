"""
Multi-Object Tracking Module — ByteTrack / DeepSORT abstraction.
Falls back to a simple IoU tracker if neither is installed.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np


@dataclass
class Track:
    track_id: int
    bbox: Tuple[int, int, int, int]
    class_name: str
    center: Tuple[float, float] = (0.0, 0.0)
    history: List[Tuple[float, float]] = field(default_factory=list)


def _iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter + 1e-6)


class SimpleIoUTracker:
    """
    Lightweight IoU-based tracker used when DeepSORT / ByteTrack
    are not installed.  Good enough for demo & low-density scenes.
    """

    def __init__(self, iou_threshold: float = 0.3, max_lost: int = 30):
        self.iou_threshold = iou_threshold
        self.max_lost = max_lost
        self._next_id = 1
        self._tracks: Dict[int, dict] = {}

    def update(self, detections: list) -> List[Track]:
        """
        Match current detections to existing tracks via IoU.
        """
        det_bboxes = [d.bbox for d in detections]
        det_classes = [d.class_name for d in detections]

        matched_det = set()
        updated: Dict[int, dict] = {}

        # Greedy match existing tracks
        for tid, trk in self._tracks.items():
            best_iou, best_idx = 0.0, -1
            for i, db in enumerate(det_bboxes):
                if i in matched_det:
                    continue
                score = _iou(trk["bbox"], db)
                if score > best_iou:
                    best_iou, best_idx = score, i

            if best_iou >= self.iou_threshold and best_idx >= 0:
                matched_det.add(best_idx)
                cx = (det_bboxes[best_idx][0] + det_bboxes[best_idx][2]) / 2
                cy = (det_bboxes[best_idx][1] + det_bboxes[best_idx][3]) / 2
                history = trk["history"][-60:] + [(cx, cy)]
                updated[tid] = {
                    "bbox": det_bboxes[best_idx],
                    "class_name": det_classes[best_idx],
                    "center": (cx, cy),
                    "history": history,
                    "lost": 0,
                }
            else:
                trk["lost"] += 1
                if trk["lost"] < self.max_lost:
                    updated[tid] = trk

        # Create new tracks for unmatched detections
        for i, db in enumerate(det_bboxes):
            if i in matched_det:
                continue
            cx = (db[0] + db[2]) / 2
            cy = (db[1] + db[3]) / 2
            updated[self._next_id] = {
                "bbox": db,
                "class_name": det_classes[i],
                "center": (cx, cy),
                "history": [(cx, cy)],
                "lost": 0,
            }
            self._next_id += 1

        self._tracks = updated

        return [
            Track(
                track_id=tid,
                bbox=t["bbox"],
                class_name=t["class_name"],
                center=t["center"],
                history=list(t["history"]),
            )
            for tid, t in updated.items()
            if t["lost"] == 0
        ]
