"""
Integrated Real-Time Traffic AI Pipeline
=========================================

Frame → Detection → Tracking → Motion → Behavior → Risk → Overlay + Log

Usage
-----
    python -m traffic_ai.pipeline --source video.mp4
    python -m traffic_ai.pipeline --source 0          # webcam
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# ── Internal modules ────────────────────────────────────────────
from traffic_ai.detection.detector import VehicleDetector
from traffic_ai.tracking.tracker import SimpleIoUTracker, Track
from traffic_ai.motion_analysis.analyzer import MotionAnalyzer, MotionProfile
from traffic_ai.motion_analysis.behavior import BehaviorClassifier, BehaviorResult
from traffic_ai.risk.scorer import RiskScorer, RiskAssessment
from traffic_ai.hotspot.detector import HotspotDetector, Hotspot, Incident


# ── Vehicle state ───────────────────────────────────────────────

@dataclass
class VehicleState:
    track_id: int
    class_name: str = ""
    speed: float = 0.0
    acceleration: float = 0.0
    behavior: str = "Safe"
    behavior_score: float = 0.0
    risk_score: float = 100.0
    risk_level: str = "Low"
    violation_count: int = 0
    in_hotspot: bool = False
    last_seen: float = 0.0


# ── Colours ─────────────────────────────────────────────────────

COLORS = {
    "Safe":       (0, 200, 0),
    "Moderate":   (0, 180, 255),
    "Aggressive": (0, 0, 255),
    "Low":        (0, 200, 0),
    "Medium":     (0, 180, 255),
    "High":       (0, 0, 255),
}


# ── Pipeline ────────────────────────────────────────────────────

class TrafficPipeline:
    """
    End-to-end real-time traffic monitoring pipeline.

    Parameters
    ----------
    model_path : str
        YOLOv8 weights file.
    speed_limit : float
        Posted speed limit (km/h) for behaviour & risk thresholds.
    fps : float
        Source video FPS (used for motion calculations).
    log_dir : str
        Directory for CSV / JSON output logs.
    hotspots : list[Hotspot] | None
        Pre-computed hotspot zones (from historical data).
    hotspot_radius_km : float
        Distance threshold to flag a vehicle as "inside" a hotspot.
    """

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        speed_limit: float = 60.0,
        fps: float = 30.0,
        log_dir: str = "output",
        hotspots: Optional[List[Hotspot]] = None,
        hotspot_radius_km: float = 0.3,
        device: str = "cpu",
    ):
        self.detector = VehicleDetector(model_path, device=device)
        self.tracker = SimpleIoUTracker()
        self.motion = MotionAnalyzer(fps=fps)
        self.behavior = BehaviorClassifier(speed_limit=speed_limit)
        self.risk = RiskScorer(speed_limit=speed_limit)

        self.hotspots = hotspots or []
        self.hotspot_radius_km = hotspot_radius_km

        self.vehicles: Dict[int, VehicleState] = {}
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self._csv_path = os.path.join(log_dir, "vehicle_log.csv")
        self._init_csv()

        self._frame_count = 0
        self._fps_display = 0.0

    # ── CSV logger ──────────────────────────────────────────────

    def _init_csv(self):
        with open(self._csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp", "frame", "vehicle_id", "class",
                "speed_kmh", "acceleration", "behavior", "behavior_score",
                "risk_score", "risk_level", "violation_count", "in_hotspot",
            ])

    def _log(self, vs: VehicleState):
        with open(self._csv_path, "a", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                datetime.now().isoformat(timespec="milliseconds"),
                self._frame_count,
                vs.track_id,
                vs.class_name,
                vs.speed,
                vs.acceleration,
                vs.behavior,
                vs.behavior_score,
                vs.risk_score,
                vs.risk_level,
                vs.violation_count,
                vs.in_hotspot,
            ])

    # ── Hotspot proximity check ─────────────────────────────────

    @staticmethod
    def _haversine_km(lat1, lon1, lat2, lon2) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) *
             math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _check_hotspot(self, lat: float, lon: float) -> bool:
        for h in self.hotspots:
            if self._haversine_km(lat, lon, h.center_lat, h.center_lon) <= self.hotspot_radius_km:
                return True
        return False

    # ── Core per-frame pipeline ─────────────────────────────────

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[VehicleState]]:
        """
        Run the full pipeline on a single frame.

        Returns annotated frame and list of current vehicle states.
        """
        t0 = time.perf_counter()
        self._frame_count += 1

        # 1. Detect
        detections = self.detector.detect(frame)

        # 2. Track
        tracks = self.tracker.update(detections)

        # 3-6. Analyse each track
        active: List[VehicleState] = []
        for trk in tracks:
            # Motion
            motion = self.motion.analyze(trk.track_id, trk.history)

            # Behavior
            beh = self.behavior.classify(
                motion.speed, motion.acceleration,
                motion.direction_change, motion.sudden_brake, motion.zigzag,
            )

            # Risk
            vs = self.vehicles.get(trk.track_id, VehicleState(track_id=trk.track_id))
            risk = self.risk.score(
                motion.speed, motion.acceleration,
                beh.label, vs.violation_count,
            )

            # Update state
            vs.class_name = trk.class_name
            vs.speed = motion.speed
            vs.acceleration = motion.acceleration
            vs.behavior = beh.label
            vs.behavior_score = beh.score
            vs.risk_score = risk.score
            vs.risk_level = risk.level
            vs.last_seen = time.time()
            self.vehicles[trk.track_id] = vs

            # Draw overlay
            self._draw_overlay(frame, trk, vs)

            # Log
            self._log(vs)
            active.append(vs)

        # FPS counter
        elapsed = time.perf_counter() - t0
        self._fps_display = 1.0 / max(elapsed, 1e-6)
        cv2.putText(
            frame,
            f"FPS: {self._fps_display:.1f}  |  Vehicles: {len(active)}",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
        )

        return frame, active

    # ── Drawing helpers ─────────────────────────────────────────

    def _draw_overlay(self, frame: np.ndarray, trk: Track, vs: VehicleState):
        x1, y1, x2, y2 = trk.bbox
        color = COLORS.get(vs.behavior, (200, 200, 200))

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Info lines
        lines = [
            f"ID:{trk.track_id} {vs.class_name}",
            f"Spd:{vs.speed:.0f}km/h  {vs.behavior}",
            f"Risk:{vs.risk_score:.0f} ({vs.risk_level})",
        ]

        if vs.in_hotspot:
            lines.append("!! HIGH RISK AREA !!")

        for i, txt in enumerate(lines):
            y = y1 - 10 - (len(lines) - 1 - i) * 18
            cv2.putText(frame, txt, (x1, max(y, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    # ── Main loop ───────────────────────────────────────────────

    def run(self, source: str, output_path: Optional[str] = None, show: bool = True):
        """
        Process a video file or webcam stream.

        Parameters
        ----------
        source : str
            Path to video or ``"0"`` for webcam.
        output_path : str | None
            If set, save annotated video to this path.
        show : bool
            Display live preview window.
        """
        cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {source}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        print(f"[Pipeline] Source: {source}  |  {w}x{h} @ {fps:.0f} FPS")
        print(f"[Pipeline] Logging to {self._csv_path}")
        print("[Pipeline] Press 'q' to quit\n")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                annotated, states = self.process_frame(frame)

                if writer:
                    writer.write(annotated)

                if show:
                    cv2.imshow("Traffic AI", annotated)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
        finally:
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()

        # Summary
        self._write_summary()

    def _write_summary(self):
        summary = {
            "total_frames": self._frame_count,
            "unique_vehicles": len(self.vehicles),
            "vehicles": [
                {
                    "id": v.track_id,
                    "class": v.class_name,
                    "last_speed": v.speed,
                    "behavior": v.behavior,
                    "risk_score": v.risk_score,
                    "risk_level": v.risk_level,
                    "violations": v.violation_count,
                }
                for v in self.vehicles.values()
            ],
        }
        path = os.path.join(self.log_dir, "summary.json")
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n[Pipeline] Summary → {path}")


# ── CLI entry-point ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Traffic AI — Real-Time Pipeline")
    ap.add_argument("--source", default="0", help="Video path or '0' for webcam")
    ap.add_argument("--model", default="yolov8n.pt", help="YOLOv8 weights")
    ap.add_argument("--speed-limit", type=float, default=60.0)
    ap.add_argument("--output", default=None, help="Save annotated video")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"])
    ap.add_argument("--no-show", action="store_true", help="Headless mode")
    args = ap.parse_args()

    pipeline = TrafficPipeline(
        model_path=args.model,
        speed_limit=args.speed_limit,
        device=args.device,
    )
    pipeline.run(args.source, output_path=args.output, show=not args.no_show)


if __name__ == "__main__":
    main()
