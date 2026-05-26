#!/usr/bin/env python3
"""
Demo: Accident Hotspot Detection
Generates synthetic incident data around New Delhi, clusters it,
and produces an interactive map.
"""

import random, json
from hotspot.detector import HotspotDetector, Incident
from hotspot.visualizer import create_hotspot_map

random.seed(42)

# ── Synthetic dataset: 3 clusters around New Delhi ──────────
CLUSTERS = [
    {"lat": 28.6139, "lon": 77.2090, "label": "Connaught Place",  "n": 25, "risk_range": (60, 95)},
    {"lat": 28.5355, "lon": 77.3910, "label": "Noida Sec-18",     "n": 15, "risk_range": (40, 70)},
    {"lat": 28.6692, "lon": 77.4538, "label": "Ghaziabad",        "n": 10, "risk_range": (20, 50)},
]
VIOLATIONS = ["signal_jump", "overspeeding", "no_helmet", "wrong_lane", "rash_driving"]

incidents: list[Incident] = []
for c in CLUSTERS:
    for i in range(c["n"]):
        incidents.append(Incident(
            latitude=c["lat"] + random.gauss(0, 0.003),
            longitude=c["lon"] + random.gauss(0, 0.003),
            risk_score=random.uniform(*c["risk_range"]),
            violation_type=random.choice(VIOLATIONS),
            timestamp=f"2025-06-{random.randint(1,30):02d}T{random.randint(0,23):02d}:00:00",
        ))

# Add scattered noise (should NOT form clusters)
for _ in range(8):
    incidents.append(Incident(
        latitude=28.5 + random.uniform(0, 0.3),
        longitude=77.1 + random.uniform(0, 0.5),
        risk_score=random.uniform(10, 40),
        violation_type=random.choice(VIOLATIONS),
        timestamp="2025-06-15T12:00:00",
    ))

# ── Detect hotspots ─────────────────────────────────────────
detector = HotspotDetector(eps_km=0.8, min_samples=5)
hotspots = detector.detect(incidents)

print(f"\n{'='*60}")
print(f"  HOTSPOT DETECTION RESULTS")
print(f"  Total incidents: {len(incidents)}")
print(f"  Clusters found:  {len(hotspots)}")
print(f"{'='*60}\n")

for h in hotspots:
    print(f"  Hotspot #{h.cluster_id}")
    print(f"    Centre     : ({h.center_lat:.4f}, {h.center_lon:.4f})")
    print(f"    Incidents  : {h.incident_count}")
    print(f"    Avg Risk   : {h.avg_risk_score}")
    print(f"    Risk Level : {h.risk_level}")
    print(f"    Top Issues : {', '.join(h.top_violations)}")
    print()

# ── Generate map ────────────────────────────────────────────
MAP_PATH = "/mnt/documents/hotspot_map.html"
create_hotspot_map(hotspots, incidents, output_path=MAP_PATH)
print(f"  Map saved → {MAP_PATH}")

# ── Save JSON report ────────────────────────────────────────
report = [
    {
        "cluster_id": int(h.cluster_id),
        "center": [round(h.center_lat, 5), round(h.center_lon, 5)],
        "incidents": h.incident_count,
        "avg_risk": h.avg_risk_score,
        "risk_level": h.risk_level,
        "top_violations": h.top_violations,
    }
    for h in hotspots
]
REPORT_PATH = "/mnt/documents/hotspot_report.json"
with open(REPORT_PATH, "w") as f:
    json.dump(report, f, indent=2)
print(f"  Report saved → {REPORT_PATH}\n")
