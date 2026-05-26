import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { HotspotZone } from "@/data/mockTrafficData";
import { MapPin } from "lucide-react";

interface Props {
  hotspots: HotspotZone[];
}

const riskBg: Record<string, string> = {
  High: "glow-red border-destructive/40",
  Medium: "glow-amber border-accent/40",
  Low: "border-primary/40",
};

export default function HotspotPanel({ hotspots }: Props) {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <MapPin className="h-4 w-4 text-destructive" />
          Hotspot Zones
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {hotspots.map((h) => (
          <div
            key={h.cluster_id}
            className={`rounded-lg border bg-muted/30 p-3 ${riskBg[h.risk_level]}`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-sm font-bold">Zone #{h.cluster_id}</span>
              <Badge
                variant="outline"
                className={
                  h.risk_level === "High"
                    ? "bg-destructive/20 text-destructive border-destructive/30"
                    : h.risk_level === "Medium"
                    ? "bg-accent/20 text-accent border-accent/30"
                    : "bg-primary/20 text-primary border-primary/30"
                }
              >
                {h.risk_level}
              </Badge>
            </div>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>
                📍 {h.center[0].toFixed(4)}, {h.center[1].toFixed(4)}
              </p>
              <p>🚨 {h.incidents} incidents • Avg risk: {h.avg_risk}</p>
              <p>⚠ {h.top_violations.join(", ")}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
