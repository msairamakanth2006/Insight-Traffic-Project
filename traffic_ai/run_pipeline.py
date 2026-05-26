"""
Full-stack launcher — runs Pipeline + Flask API together.

Usage
-----
    python -m traffic_ai.run_pipeline --source video.mp4
    python -m traffic_ai.run_pipeline --source 0 --with-api
"""

from __future__ import annotations

import argparse
import threading

from traffic_ai.pipeline import TrafficPipeline
from traffic_ai.api import app as flask_app, update_vehicles, set_hotspots


def start_api(port: int = 5000):
    """Launch Flask in a daemon thread."""
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


class PipelineWithAPI(TrafficPipeline):
    """Extends the base pipeline to push state to the Flask API."""

    def process_frame(self, frame):
        annotated, states = super().process_frame(frame)
        update_vehicles(states)
        return annotated, states


def main():
    ap = argparse.ArgumentParser(description="Traffic AI — Pipeline + API")
    ap.add_argument("--source", default="0")
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--speed-limit", type=float, default=60.0)
    ap.add_argument("--output", default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--no-show", action="store_true")
    ap.add_argument("--with-api", action="store_true", help="Start Flask API server")
    ap.add_argument("--api-port", type=int, default=5000)
    args = ap.parse_args()

    if args.with_api:
        print(f"[Launcher] Starting API on port {args.api_port}")
        t = threading.Thread(target=start_api, args=(args.api_port,), daemon=True)
        t.start()

    pipeline = PipelineWithAPI(
        model_path=args.model,
        speed_limit=args.speed_limit,
        device=args.device,
    )
    pipeline.run(args.source, output_path=args.output, show=not args.no_show)


if __name__ == "__main__":
    main()
