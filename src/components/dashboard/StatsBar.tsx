import { Card, CardContent } from "@/components/ui/card";
import { Activity, Car, Gauge, ShieldAlert } from "lucide-react";
import type { PipelineStats } from "@/data/mockTrafficData";

interface Props {
  stats: PipelineStats;
}

export default function StatsBar({ stats }: Props) {
  const cards = [
    {
      label: "Vehicles",
      value: stats.total_vehicles,
      icon: Car,
      accent: "text-primary",
    },
    {
      label: "Avg Speed",
      value: `${stats.avg_speed.toFixed(0)} km/h`,
      icon: Gauge,
      accent: "text-info",
    },
    {
      label: "Avg Risk",
      value: stats.avg_risk.toFixed(0),
      icon: ShieldAlert,
      accent: stats.avg_risk < 50 ? "text-destructive" : stats.avg_risk < 80 ? "text-accent" : "text-primary",
    },
    {
      label: "FPS",
      value: stats.fps.toFixed(1),
      icon: Activity,
      accent: "text-muted-foreground",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((c) => (
        <Card key={c.label} className="bg-card border-border">
          <CardContent className="p-4 flex items-center gap-3">
            <c.icon className={`h-8 w-8 ${c.accent} shrink-0`} />
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground">{c.label}</p>
              <p className="text-xl font-bold">{c.value}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
