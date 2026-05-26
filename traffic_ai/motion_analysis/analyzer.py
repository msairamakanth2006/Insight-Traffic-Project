"""
Motion Analysis Module — speed, acceleration, direction.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math


@dataclass
class MotionProfile:
    speed: float  # px/frame → converted to km/h with calibration
    acceleration: float
    direction: float  # degrees
    direction_change: float  # degrees since last frame
    sudden_brake: bool
    zigzag: bool


class MotionAnalyzer:
    """
    Computes per-vehicle motion metrics from tracking history.

    Parameters
    ----------
    fps : float
        Video frames per second.
    px_per_meter : float
        Pixel-to-metre calibration factor.
    brake_threshold : float
        Deceleration (m/s²) considered "sudden braking".
    zigzag_window : int
        Number of frames to look back for zig-zag detection.
    zigzag_angle : float
        Minimum cumulative direction change (°) over the window.
    """

    def __init__(
        self,
        fps: float = 30.0,
        px_per_meter: float = 8.0,
        brake_threshold: float = 6.0,
        zigzag_window: int = 10,
        zigzag_angle: float = 90.0,
    ):
        self.fps = fps
        self.px_per_meter = px_per_meter
        self.brake_threshold = brake_threshold
        self.zigzag_window = zigzag_window
        self.zigzag_angle = zigzag_angle
        self._prev: Dict[int, dict] = {}

    def analyze(self, track_id: int, history: List[Tuple[float, float]]) -> MotionProfile:
        """Compute motion profile from a track's position history."""
        if len(history) < 2:
            return MotionProfile(0, 0, 0, 0, False, False)

        dx = history[-1][0] - history[-2][0]
        dy = history[-1][1] - history[-2][1]
        dist_px = math.hypot(dx, dy)
        dist_m = dist_px / self.px_per_meter
        speed_ms = dist_m * self.fps
        speed_kmh = speed_ms * 3.6

        direction = math.degrees(math.atan2(dy, dx)) % 360

        prev = self._prev.get(track_id, {"speed_ms": 0.0, "direction": direction})
        accel = (speed_ms - prev["speed_ms"]) * self.fps  # m/s²
        dir_change = abs(direction - prev["direction"])
        if dir_change > 180:
            dir_change = 360 - dir_change

        sudden_brake = accel < -self.brake_threshold

        # Zig-zag: large cumulative direction change over recent frames
        zigzag = False
        if len(history) >= self.zigzag_window + 2:
            total_change = 0.0
            for i in range(-self.zigzag_window + 1, 0):
                ddx = history[i][0] - history[i - 1][0]
                ddy = history[i][1] - history[i - 1][1]
                d = math.degrees(math.atan2(ddy, ddx)) % 360
                pdx = history[i - 1][0] - history[i - 2][0]
                pdy = history[i - 1][1] - history[i - 2][1]
                pd = math.degrees(math.atan2(pdy, pdx)) % 360
                ch = abs(d - pd)
                if ch > 180:
                    ch = 360 - ch
                total_change += ch
            zigzag = total_change >= self.zigzag_angle

        self._prev[track_id] = {"speed_ms": speed_ms, "direction": direction}

        return MotionProfile(
            speed=round(speed_kmh, 1),
            acceleration=round(accel, 2),
            direction=round(direction, 1),
            direction_change=round(dir_change, 1),
            sudden_brake=sudden_brake,
            zigzag=zigzag,
        )
