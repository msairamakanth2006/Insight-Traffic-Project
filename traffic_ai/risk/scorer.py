"""
Risk Scoring & Prediction Module.
"""

from dataclasses import dataclass


@dataclass
class RiskAssessment:
    score: float       # 0-100 (100 = safest)
    level: str         # Low / Medium / High


class RiskScorer:
    """
    Deduction-based risk scorer.

    Starts at 100 and subtracts penalties for speeding,
    harsh manoeuvres, aggressive behaviour, and violations.
    """

    def __init__(
        self,
        speed_limit: float = 60.0,
        high_speed_penalty: float = 25.0,
        moderate_speed_penalty: float = 15.0,
        harsh_accel_penalty: float = 20.0,
        mild_accel_penalty: float = 10.0,
        aggressive_penalty: float = 25.0,
        moderate_behavior_penalty: float = 10.0,
        violation_penalty: float = 15.0,
    ):
        self.speed_limit = speed_limit
        self.high_speed_pen = high_speed_penalty
        self.mod_speed_pen = moderate_speed_penalty
        self.harsh_accel_pen = harsh_accel_penalty
        self.mild_accel_pen = mild_accel_penalty
        self.aggr_pen = aggressive_penalty
        self.mod_beh_pen = moderate_behavior_penalty
        self.viol_pen = violation_penalty

    def score(
        self,
        speed: float,
        acceleration: float,
        behavior_label: str,
        violation_count: int = 0,
    ) -> RiskAssessment:
        s = 100.0

        # Speed
        over = speed - self.speed_limit
        if over > 25:
            s -= self.high_speed_pen
        elif over > 0:
            s -= self.mod_speed_pen

        # Acceleration / braking
        if abs(acceleration) > 8:
            s -= self.harsh_accel_pen
        elif abs(acceleration) > 4:
            s -= self.mild_accel_pen

        # Behavior
        if behavior_label == "Aggressive":
            s -= self.aggr_pen
        elif behavior_label == "Moderate":
            s -= self.mod_beh_pen

        # Violations
        s -= self.viol_pen * violation_count

        s = max(0.0, min(100.0, s))

        if s >= 80:
            level = "Low"
        elif s >= 50:
            level = "Medium"
        else:
            level = "High"

        return RiskAssessment(score=round(s, 1), level=level)


def calculate_risk(
    speed: float,
    acceleration: float,
    behavior: str,
    violations: int = 0,
    speed_limit: float = 60.0,
) -> dict:
    """Convenience function returning a plain dict."""
    r = RiskScorer(speed_limit=speed_limit).score(speed, acceleration, behavior, violations)
    return {"risk_score": r.score, "risk_level": r.level}
