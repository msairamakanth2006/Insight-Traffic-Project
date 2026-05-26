"""
Vehicle Detection Module — YOLOv8 wrapper.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


@dataclass
class Detection:
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    class_id: int
    class_name: str


# COCO vehicle class IDs
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


class VehicleDetector:
    """
    Wraps YOLOv8 for vehicle-only detection.

    Parameters
    ----------
    model_path : str
        Path to a YOLOv8 weights file (e.g. ``yolov8n.pt``).
    confidence : float
        Minimum detection confidence.
    device : str
        ``'cpu'``, ``'cuda'``, or ``'mps'``.
    """

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence: float = 0.4,
        device: str = "cpu",
    ):
        if YOLO is None:
            raise ImportError("pip install ultralytics")
        self.model = YOLO(model_path)
        self.model.to(device)
        self.confidence = confidence

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Return vehicle detections for a single frame."""
        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        detections: List[Detection] = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detections.append(
                Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=float(box.conf[0]),
                    class_id=cls_id,
                    class_name=VEHICLE_CLASSES[cls_id],
                )
            )
        return detections
