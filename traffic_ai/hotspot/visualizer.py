"""
Folium-based map visualization for hotspots.
"""

from typing import List
import folium
from folium.plugins import HeatMap
from .detector import Hotspot, Incident


RISK_COLORS = {"High": "red", "Medium": "orange", "Low": "green"}


def create_hotspot_map(
    hotspots: List[Hotspot],
    incidents: List[Incident] | None = None,
    output_path: str = "hotspot_map.html",
) -> folium.Map:
    """
    Generate an interactive Folium map with:
      - Heatmap layer from raw incidents
      - CircleMarker for each hotspot centre (colour-coded by risk)
    """
    if not hotspots:
        centre = [28.6139, 77.2090]  # default: New Delhi
    else:
        centre = [hotspots[0].center_lat, hotspots[0].center_lon]

    m = folium.Map(location=centre, zoom_start=13, tiles="cartodbpositron")

    # ── Heatmap layer (raw incidents) ──
    if incidents:
        heat_data = [[i.latitude, i.longitude, i.risk_score / 100] for i in incidents]
        HeatMap(heat_data, radius=18, blur=15, name="Incident heatmap").add_to(m)

    # ── Hotspot markers ──
    for h in hotspots:
        colour = RISK_COLORS.get(h.risk_level, "gray")
        popup_html = (
            f"<b>Hotspot #{h.cluster_id}</b><br>"
            f"Incidents: {h.incident_count}<br>"
            f"Avg risk: {h.avg_risk_score}<br>"
            f"Level: <b>{h.risk_level}</b><br>"
            f"Top violations: {', '.join(h.top_violations)}"
        )
        folium.CircleMarker(
            location=[h.center_lat, h.center_lon],
            radius=10 + h.incident_count * 2,
            color=colour,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{h.risk_level} risk zone",
        ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(output_path)
    return m
