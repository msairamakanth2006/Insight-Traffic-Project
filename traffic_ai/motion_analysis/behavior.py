"""
Behavior Classification Module — rule-based scoring.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class BehaviorResult:
    label: str          # Safe / Moderate / Aggressive
    score: float        # 0-100 penalty score
    reasons: List[str]


class BehaviorClassifier:
    """
    Classify driving behaviour using a weighted penalty system.

    Thresholds
    ----------
    speed_limit : float   (km/h) — posted speed limit
    safe_max    : int     — max penalty for "Safe"
    moderate_max: int     — max penalty for "Moderate"
    """

    def __init__(
        self,
        speed_limit: float = 60.0,
        safe_max: int = 30,
        moderate_max: int = 60,
    ):
        self.speed_limit = speed_limit
        self.safe_max = safe_max
        self.moderate_max = moderate_max

    def classify(
        self,
        speed: float,
        acceleration: float,
        direction_change: float,
        sudden_brake: bool = False,
        zigzag: bool = False,
    ) -> BehaviorResult:
        penalty = 0.0
        reasons: List[str] = []

        # Speed penalty
        over = speed - self.speed_limit
        if over > 30:
            penalty += 35
            reasons.append("extreme_speed")
        elif over > 15:
            penalty += 25
            reasons.append("high_speed")
        elif over > 0:
            penalty += 10
            reasons.append("slight_overspeed")

        # Acceleration penalty
        if abs(acceleration) > 8:
            penalty += 25
            reasons.append("extreme_accel")
        elif abs(acceleration) > 4:
            penalty += 12
            reasons.append("hard_accel")

        # Direction change
        if direction_change > 45:
            penalty += 20
            reasons.append("sharp_turn")
        elif direction_change > 20:
            penalty += 8
            reasons.append("lane_drift")

        # Flags
        if sudden_brake:
            penalty += 10
            reasons.append("sudden_brake")
        if zigzag:
            penalty += 20
            reasons.append("zigzag_pattern")

        penalty = min(penalty, 100)

        if penalty <= self.safe_max:
            label = "Safe"
        elif penalty <= self.moderate_max:
            label = "Moderate"
        else:
            label = "Aggressive"

        return BehaviorResult(label=label, score=round(penalty, 1), reasons=reasons)


def classify_behavior(
    speed: float,
    acceleration: float,
    direction_change: float,
    sudden_brake: bool = False,
    zigzag: bool = False,
    speed_limit: float = 60.0,
) -> dict:
    """Convenience function returning a plain dict."""
    c = BehaviorClassifier(speed_limit=speed_limit)
    r = c.classify(speed, acceleration, direction_change, sudden_brake, zigzag)
    return {"label": r.label, "score": r.score, "reasons": r.reasons}
