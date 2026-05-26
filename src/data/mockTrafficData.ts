/**
 * Simulated vehicle data for the dashboard demo.
 * In production, this would come from the Flask API.
 */

export interface Vehicle {
  id: number;
  class_name: string;
  speed: number;
  acceleration: number;
  behavior: "Safe" | "Moderate" | "Aggressive";
  behavior_score: number;
  risk_score: number;
  risk_level: "Low" | "Medium" | "High";
  violations: number;
  in_hotspot: boolean;
  lat: number;
  lon: number;
}

export interface HotspotZone {
  cluster_id: number;
  center: [number, number];
  incidents: number;
  risk_level: "Low" | "Medium" | "High";
  avg_risk: number;
  top_violations: string[];
}

export interface PipelineStats {
  fps: number;
  total_vehicles: number;
  avg_speed: number;
  avg_risk: number;
  behavior_counts: { Safe: number; Moderate: number; Aggressive: number };
  risk_counts: { Low: number; Medium: number; High: number };
  uptime_seconds: number;
}

// Simulated vehicles
const MOCK_VEHICLES: Vehicle[] = [
  { id: 1, class_name: "car", speed: 52, acceleration: 1.2, behavior: "Safe", behavior_score: 8, risk_score: 92, risk_level: "Low", violations: 0, in_hotspot: false, lat: 28.6139, lon: 77.2090 },
  { id: 2, class_name: "truck", speed: 88, acceleration: -6.5, behavior: "Aggressive", behavior_score: 72, risk_score: 35, risk_level: "High", violations: 2, in_hotspot: true, lat: 28.6155, lon: 77.2105 },
  { id: 3, class_name: "motorcycle", speed: 43, acceleration: 0.8, behavior: "Safe", behavior_score: 5, risk_score: 100, risk_level: "Low", violations: 0, in_hotspot: false, lat: 28.6180, lon: 77.2120 },
  { id: 4, class_name: "bus", speed: 71, acceleration: 3.2, behavior: "Moderate", behavior_score: 38, risk_score: 65, risk_level: "Medium", violations: 1, in_hotspot: false, lat: 28.6200, lon: 77.2080 },
  { id: 5, class_name: "car", speed: 95, acceleration: 8.1, behavior: "Aggressive", behavior_score: 82, risk_score: 28, risk_level: "High", violations: 3, in_hotspot: true, lat: 28.6145, lon: 77.2098 },
  { id: 6, class_name: "car", speed: 58, acceleration: -1.0, behavior: "Safe", behavior_score: 12, risk_score: 88, risk_level: "Low", violations: 0, in_hotspot: false, lat: 28.6220, lon: 77.2150 },
  { id: 7, class_name: "motorcycle", speed: 110, acceleration: 9.5, behavior: "Aggressive", behavior_score: 90, risk_score: 18, risk_level: "High", violations: 4, in_hotspot: true, lat: 28.6150, lon: 77.2095 },
  { id: 8, class_name: "truck", speed: 62, acceleration: 2.0, behavior: "Moderate", behavior_score: 30, risk_score: 72, risk_level: "Medium", violations: 0, in_hotspot: false, lat: 28.6170, lon: 77.2130 },
];

const MOCK_HOTSPOTS: HotspotZone[] = [
  { cluster_id: 0, center: [28.6150, 77.2098], incidents: 14, risk_level: "High", avg_risk: 78.3, top_violations: ["overspeeding", "signal_jump", "wrong_lane"] },
  { cluster_id: 1, center: [28.6200, 77.2150], incidents: 7, risk_level: "Medium", avg_risk: 52.1, top_violations: ["overspeeding", "lane_violation"] },
];

export function getVehicles(): Vehicle[] {
  // Add slight random variation to simulate real-time updates
  return MOCK_VEHICLES.map(v => ({
    ...v,
    speed: Math.max(0, v.speed + (Math.random() - 0.5) * 6),
    acceleration: v.acceleration + (Math.random() - 0.5) * 1.5,
    risk_score: Math.max(0, Math.min(100, v.risk_score + (Math.random() - 0.5) * 4)),
  }));
}

export function getHotspots(): HotspotZone[] {
  return MOCK_HOTSPOTS;
}

export function getStats(vehicles: Vehicle[]): PipelineStats {
  const total = vehicles.length;
  return {
    fps: 28 + Math.random() * 4,
    total_vehicles: total,
    avg_speed: total ? vehicles.reduce((s, v) => s + v.speed, 0) / total : 0,
    avg_risk: total ? vehicles.reduce((s, v) => s + v.risk_score, 0) / total : 0,
    behavior_counts: {
      Safe: vehicles.filter(v => v.behavior === "Safe").length,
      Moderate: vehicles.filter(v => v.behavior === "Moderate").length,
      Aggressive: vehicles.filter(v => v.behavior === "Aggressive").length,
    },
    risk_counts: {
      Low: vehicles.filter(v => v.risk_level === "Low").length,
      Medium: vehicles.filter(v => v.risk_level === "Medium").length,
      High: vehicles.filter(v => v.risk_level === "High").length,
    },
    uptime_seconds: Math.floor(Date.now() / 1000) % 86400,
  };
}
