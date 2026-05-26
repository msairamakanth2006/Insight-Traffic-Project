"""
Standalone demo — runs all pipeline modules without OpenCV/YOLO dependencies.
Simulates vehicle data and prints the full analysis output.
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traffic_ai.motion_analysis.analyzer import MotionAnalyzer
from traffic_ai.motion_analysis.behavior import BehaviorClassifier, classify_behavior
from traffic_ai.risk.scorer import RiskScorer, calculate_risk
from traffic_ai.hotspot.detector import HotspotDetector, Incident

# ── Simulated vehicle trajectories ──────────────────────────────

VEHICLES = {
    1: {
        "class": "car",
        "history": [(100+i*8, 200+i*2) for i in range(20)],  # steady, moderate speed
        "violations": 0,
    },
    2: {
        "class": "truck",
        "history": [(300+i*15, 200 + (i%3)*10 - 10) for i in range(20)],  # fast, zigzag
        "violations": 2,
    },
    3: {
        "class": "motorcycle",
        "history": [(500+i*3, 400+i*1) for i in range(20)],  # slow, safe
        "violations": 0,
    },
    4: {
        "class": "bus",
        "history": [(200+i*12, 300 + (-1)**i * 8) for i in range(20)],  # moderate swerve
        "violations": 1,
    },
}


def run_demo():
    print("=" * 70)
    print("  AI-Powered Traffic Monitoring — Full Pipeline Demo")
    print("=" * 70)

    motion = MotionAnalyzer(fps=30.0, px_per_meter=8.0)
    behavior = BehaviorClassifier(speed_limit=60.0)
    risk = RiskScorer(speed_limit=60.0)

    results = []

    for vid, data in VEHICLES.items():
        # Feed history incrementally to build up motion state
        for i in range(2, len(data["history"])):
            m = motion.analyze(vid, data["history"][:i+1])

        # Final motion profile
        m = motion.analyze(vid, data["history"])

        # Behavior classification
        b = behavior.classify(m.speed, m.acceleration, m.direction_change, m.sudden_brake, m.zigzag)

        # Risk scoring
        r = risk.score(m.speed, m.acceleration, b.label, data["violations"])

        result = {
            "vehicle_id": vid,
            "class": data["class"],
            "speed_kmh": m.speed,
            "acceleration": m.acceleration,
            "direction_change": m.direction_change,
            "sudden_brake": m.sudden_brake,
            "zigzag": m.zigzag,
            "behavior": b.label,
            "behavior_score": b.score,
            "behavior_reasons": b.reasons,
            "risk_score": r.score,
            "risk_level": r.level,
            "violations": data["violations"],
        }
        results.append(result)

        print(f"\n{'─' * 50}")
        print(f"  Vehicle #{vid} ({data['class']})")
        print(f"{'─' * 50}")
        print(f"  Speed:            {m.speed:.1f} km/h")
        print(f"  Acceleration:     {m.acceleration:.2f} m/s²")
        print(f"  Direction Change: {m.direction_change:.1f}°")
        print(f"  Sudden Brake:     {m.sudden_brake}")
        print(f"  Zig-Zag:          {m.zigzag}")
        print(f"  ──────────────────────────────────")
        print(f"  Behavior:         {b.label} (score: {b.score})")
        print(f"  Reasons:          {', '.join(b.reasons) if b.reasons else 'none'}")
        print(f"  ──────────────────────────────────")
        print(f"  Risk Score:       {r.score}")
        print(f"  Risk Level:       {r.level}")
        print(f"  Violations:       {data['violations']}")

    # ── Hotspot Detection ───────────────────────────────────────
    print(f"\n\n{'=' * 70}")
    print("  Hotspot Detection (DBSCAN on simulated incidents)")
    print(f"{'=' * 70}")

    incidents = [
        Incident(28.6139 + i*0.001, 77.2090 + i*0.001, 75.0 + i, "overspeeding", f"2025-01-0{i+1}T10:00:00")
        for i in range(5)
    ] + [
        Incident(28.6139 + i*0.001, 77.2090 + i*0.0008, 60.0, "signal_jump", f"2025-01-0{i+1}T11:00:00")
        for i in range(4)
    ] + [
        Incident(28.7000, 77.3000, 30.0, "wrong_lane", "2025-01-01T12:00:00"),
    ]

    detector = HotspotDetector(eps_km=0.5, min_samples=3)
    hotspots = detector.detect(incidents)

    if hotspots:
        for h in hotspots:
            print(f"\n  Cluster #{h.cluster_id}")
            print(f"    Center:       ({h.center_lat:.4f}, {h.center_lon:.4f})")
            print(f"    Incidents:    {h.incident_count}")
            print(f"    Avg Risk:     {h.avg_risk_score}")
            print(f"    Risk Level:   {h.risk_level}")
            print(f"    Top Violations: {', '.join(h.top_violations)}")
    else:
        print("  No hotspots detected (all points too sparse)")

    # ── Convenience function demo ───────────────────────────────
    print(f"\n\n{'=' * 70}")
    print("  Convenience Function Tests")
    print(f"{'=' * 70}")

    test_cases = [
        {"speed": 45, "acceleration": 1.5, "direction_change": 5},
        {"speed": 85, "acceleration": -7.0, "direction_change": 35},
        {"speed": 120, "acceleration": 10.0, "direction_change": 60, "sudden_brake": True, "zigzag": True},
    ]

    for tc in test_cases:
        b = classify_behavior(**tc)
        r = calculate_risk(tc["speed"], tc["acceleration"], b["label"])
        print(f"\n  Input: {tc}")
        print(f"  → Behavior: {b['label']} | Risk: {r['risk_score']} ({r['risk_level']})")

    print(f"\n{'=' * 70}")
    print("  ✅ Pipeline demo complete!")
    print(f"{'=' * 70}")

    return results


if __name__ == "__main__":
    run_demo()
