"""
Flask REST API — Exposes live traffic data from the pipeline.

Endpoints
---------
GET  /api/vehicles         → all tracked vehicles (current state)
GET  /api/vehicles/<id>    → single vehicle
GET  /api/stats            → aggregate stats
GET  /api/hotspots         → known hotspot zones
POST /api/reset            → clear vehicle state

Run
---
    python -m traffic_ai.api
"""

from __future__ import annotations

import threading
from flask import Flask, jsonify

# Shared state (populated by the pipeline in a background thread)
_vehicle_store: dict = {}
_hotspot_store: list = []
_lock = threading.Lock()

app = Flask(__name__)


# ── Helpers for pipeline integration ────────────────────────────

def update_vehicles(states: list):
    """Called by the pipeline after each frame."""
    with _lock:
        for s in states:
            _vehicle_store[s.track_id] = {
                "id": s.track_id,
                "class": s.class_name,
                "speed": s.speed,
                "acceleration": s.acceleration,
                "behavior": s.behavior,
                "behavior_score": s.behavior_score,
                "risk_score": s.risk_score,
                "risk_level": s.risk_level,
                "violations": s.violation_count,
                "in_hotspot": s.in_hotspot,
            }


def set_hotspots(hotspots: list):
    global _hotspot_store
    _hotspot_store = [
        {
            "cluster_id": h.cluster_id,
            "center": [h.center_lat, h.center_lon],
            "incidents": h.incident_count,
            "risk_level": h.risk_level,
            "avg_risk": h.avg_risk_score,
            "top_violations": h.top_violations,
        }
        for h in hotspots
    ]


# ── Routes ──────────────────────────────────────────────────────

@app.route("/api/vehicles")
def get_vehicles():
    with _lock:
        return jsonify(list(_vehicle_store.values()))


@app.route("/api/vehicles/<int:vid>")
def get_vehicle(vid: int):
    with _lock:
        v = _vehicle_store.get(vid)
    if v is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(v)


@app.route("/api/stats")
def get_stats():
    with _lock:
        vehicles = list(_vehicle_store.values())
    total = len(vehicles)
    if total == 0:
        return jsonify({"total": 0})
    return jsonify({
        "total": total,
        "avg_speed": round(sum(v["speed"] for v in vehicles) / total, 1),
        "avg_risk": round(sum(v["risk_score"] for v in vehicles) / total, 1),
        "behavior_counts": {
            "Safe": sum(1 for v in vehicles if v["behavior"] == "Safe"),
            "Moderate": sum(1 for v in vehicles if v["behavior"] == "Moderate"),
            "Aggressive": sum(1 for v in vehicles if v["behavior"] == "Aggressive"),
        },
        "risk_counts": {
            "Low": sum(1 for v in vehicles if v["risk_level"] == "Low"),
            "Medium": sum(1 for v in vehicles if v["risk_level"] == "Medium"),
            "High": sum(1 for v in vehicles if v["risk_level"] == "High"),
        },
    })


@app.route("/api/hotspots")
def get_hotspots():
    return jsonify(_hotspot_store)


@app.route("/api/reset", methods=["POST"])
def reset():
    with _lock:
        _vehicle_store.clear()
    return jsonify({"status": "cleared"})


# ── Standalone server ───────────────────────────────────────────

if __name__ == "__main__":
    print("[API] Starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
