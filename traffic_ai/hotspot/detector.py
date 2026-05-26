"""
Accident Hotspot Detection Module
Uses DBSCAN clustering on geo-located violation/risk data.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
from sklearn.cluster import DBSCAN


@dataclass
class Incident:
    latitude: float
    longitude: float
    risk_score: float
    violation_type: str
    timestamp: str


@dataclass
class Hotspot:
    cluster_id: int
    center_lat: float
    center_lon: float
    incident_count: int
    avg_risk_score: float
    risk_level: str  # Low / Medium / High
    top_violations: List[str] = field(default_factory=list)


class HotspotDetector:
    """
    DBSCAN-based spatial clustering for accident hotspot detection.

    Parameters
    ----------
    eps_km : float
        Neighbourhood radius in kilometres (converted to radians for haversine).
    min_samples : int
        Minimum incidents to form a cluster.
    high_risk_threshold : float
        Average risk score above which a cluster is "High" risk.
    medium_risk_threshold : float
        Average risk score above which a cluster is "Medium" risk.
    """

    EARTH_RADIUS_KM = 6371.0

    def __init__(
        self,
        eps_km: float = 0.5,
        min_samples: int = 3,
        high_risk_threshold: float = 70.0,
        medium_risk_threshold: float = 40.0,
    ):
        self.eps_km = eps_km
        self.min_samples = min_samples
        self.high_thresh = high_risk_threshold
        self.med_thresh = medium_risk_threshold

    # ── public API ──────────────────────────────────────────────

    def detect(self, incidents: List[Incident]) -> List[Hotspot]:
        """Run DBSCAN and return a list of Hotspot objects."""
        if len(incidents) < self.min_samples:
            return []

        coords = np.radians(
            np.array([[i.latitude, i.longitude] for i in incidents])
        )

        db = DBSCAN(
            eps=self.eps_km / self.EARTH_RADIUS_KM,
            min_samples=self.min_samples,
            metric="haversine",
        )
        labels = db.fit_predict(coords)

        clusters: dict[int, list[int]] = {}
        for idx, label in enumerate(labels):
            if label == -1:
                continue
            clusters.setdefault(label, []).append(idx)

        hotspots: List[Hotspot] = []
        for cid, indices in clusters.items():
            lats = [incidents[i].latitude for i in indices]
            lons = [incidents[i].longitude for i in indices]
            scores = [incidents[i].risk_score for i in indices]
            violations = [incidents[i].violation_type for i in indices]

            avg_risk = float(np.mean(scores))
            risk_level = (
                "High" if avg_risk >= self.high_thresh
                else "Medium" if avg_risk >= self.med_thresh
                else "Low"
            )

            # Top violation types by frequency
            from collections import Counter
            top = [v for v, _ in Counter(violations).most_common(3)]

            hotspots.append(Hotspot(
                cluster_id=cid,
                center_lat=float(np.mean(lats)),
                center_lon=float(np.mean(lons)),
                incident_count=len(indices),
                avg_risk_score=round(avg_risk, 1),
                risk_level=risk_level,
                top_violations=top,
            ))

        hotspots.sort(key=lambda h: h.avg_risk_score, reverse=True)
        return hotspots


# ── Standalone helper ───────────────────────────────────────────

def detect_hotspots(
    data: List[dict],
    eps_km: float = 0.5,
    min_samples: int = 3,
) -> List[dict]:
    """Convenience function accepting raw dicts."""
    incidents = [Incident(**d) for d in data]
    detector = HotspotDetector(eps_km=eps_km, min_samples=min_samples)
    return [
        {
            "cluster_id": h.cluster_id,
            "center": (h.center_lat, h.center_lon),
            "incidents": h.incident_count,
            "avg_risk": h.avg_risk_score,
            "risk_level": h.risk_level,
            "top_violations": h.top_violations,
        }
        for h in detector.detect(incidents)
    ]
