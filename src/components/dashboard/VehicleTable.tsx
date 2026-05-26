import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Vehicle } from "@/data/mockTrafficData";

interface Props {
  vehicles: Vehicle[];
}

const behaviorColor: Record<string, string> = {
  Safe: "bg-primary/20 text-primary border-primary/30",
  Moderate: "bg-accent/20 text-accent border-accent/30",
  Aggressive: "bg-destructive/20 text-destructive border-destructive/30",
};

const riskColor: Record<string, string> = {
  Low: "text-primary",
  Medium: "text-accent",
  High: "text-destructive",
};

export default function VehicleTable({ vehicles }: Props) {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">
          Live Vehicle Feed
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-muted-foreground text-xs uppercase tracking-wider">
                <th className="px-4 py-2 text-left">ID</th>
                <th className="px-4 py-2 text-left">Class</th>
                <th className="px-4 py-2 text-right">Speed</th>
                <th className="px-4 py-2 text-center">Behavior</th>
                <th className="px-4 py-2 text-right">Risk</th>
                <th className="px-4 py-2 text-center">Level</th>
                <th className="px-4 py-2 text-right">Violations</th>
                <th className="px-4 py-2 text-center">Hotspot</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.map((v) => (
                <tr
                  key={v.id}
                  className={`border-b border-border/50 hover:bg-muted/40 transition-colors ${
                    v.risk_level === "High" ? "bg-destructive/5" : ""
                  }`}
                >
                  <td className="px-4 py-2.5 font-mono font-bold">#{v.id}</td>
                  <td className="px-4 py-2.5 capitalize">{v.class_name}</td>
                  <td className="px-4 py-2.5 text-right font-mono">
                    {v.speed.toFixed(0)} <span className="text-muted-foreground text-xs">km/h</span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <Badge variant="outline" className={behaviorColor[v.behavior]}>
                      {v.behavior}
                    </Badge>
                  </td>
                  <td className={`px-4 py-2.5 text-right font-mono font-bold ${riskColor[v.risk_level]}`}>
                    {v.risk_score.toFixed(0)}
                  </td>
                  <td className={`px-4 py-2.5 text-center font-semibold ${riskColor[v.risk_level]}`}>
                    {v.risk_level}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono">
                    {v.violations > 0 ? (
                      <span className="text-destructive">{v.violations}</span>
                    ) : (
                      <span className="text-muted-foreground">0</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    {v.in_hotspot && (
                      <span className="inline-flex items-center gap-1 text-destructive text-xs font-bold animate-pulse">
                        ⚠ ALERT
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
