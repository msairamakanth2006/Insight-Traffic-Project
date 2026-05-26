import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Cpu, Eye, Zap, Brain, ShieldCheck, BarChart3 } from "lucide-react";

const stages = [
  { name: "Detection", desc: "YOLOv8 vehicle detection", icon: Eye, status: "active" },
  { name: "Tracking", desc: "IoU / DeepSORT tracker", icon: Cpu, status: "active" },
  { name: "Motion", desc: "Speed, accel, direction", icon: Zap, status: "active" },
  { name: "Behavior", desc: "Safe / Moderate / Aggressive", icon: Brain, status: "active" },
  { name: "Risk", desc: "0-100 score + level", icon: ShieldCheck, status: "active" },
  { name: "Hotspot", desc: "DBSCAN geo-clustering", icon: BarChart3, status: "active" },
];

export default function PipelineStatus() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">
          Pipeline Modules
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {stages.map((s, i) => (
            <div key={s.name} className="flex items-center gap-3">
              <div className="flex items-center justify-center w-7 h-7 rounded-md bg-primary/10">
                <s.icon className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold">{s.name}</p>
                <p className="text-xs text-muted-foreground truncate">{s.desc}</p>
              </div>
              <CheckCircle className="h-4 w-4 text-primary shrink-0" />
            </div>
          ))}
        </div>
        <div className="mt-4 pt-3 border-t border-border flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
          <span className="text-xs text-muted-foreground">All modules operational</span>
        </div>
      </CardContent>
    </Card>
  );
}
