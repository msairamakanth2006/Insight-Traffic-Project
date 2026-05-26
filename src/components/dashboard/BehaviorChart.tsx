import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import type { PipelineStats } from "@/data/mockTrafficData";

interface Props {
  stats: PipelineStats;
}

const BEHAVIOR_COLORS = ["hsl(160,84%,40%)", "hsl(38,92%,55%)", "hsl(0,72%,55%)"];
const RISK_COLORS = ["hsl(160,84%,40%)", "hsl(38,92%,55%)", "hsl(0,72%,55%)"];

export default function BehaviorChart({ stats }: Props) {
  const behaviorData = [
    { name: "Safe", value: stats.behavior_counts.Safe },
    { name: "Moderate", value: stats.behavior_counts.Moderate },
    { name: "Aggressive", value: stats.behavior_counts.Aggressive },
  ].filter(d => d.value > 0);

  const riskData = [
    { name: "Low", value: stats.risk_counts.Low },
    { name: "Medium", value: stats.risk_counts.Medium },
    { name: "High", value: stats.risk_counts.High },
  ].filter(d => d.value > 0);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      <Card className="bg-card border-border">
        <CardHeader className="pb-1">
          <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">
            Behavior Distribution
          </CardTitle>
        </CardHeader>
        <CardContent className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={behaviorData} dataKey="value" cx="50%" cy="50%" outerRadius={65} strokeWidth={0}>
                {behaviorData.map((_, i) => (
                  <Cell key={i} fill={BEHAVIOR_COLORS[["Safe","Moderate","Aggressive"].indexOf(behaviorData[i].name)]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(220,18%,10%)", border: "1px solid hsl(220,14%,18%)", borderRadius: 8, color: "#fff" }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="bg-card border-border">
        <CardHeader className="pb-1">
          <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">
            Risk Level Distribution
          </CardTitle>
        </CardHeader>
        <CardContent className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={riskData} dataKey="value" cx="50%" cy="50%" outerRadius={65} strokeWidth={0}>
                {riskData.map((_, i) => (
                  <Cell key={i} fill={RISK_COLORS[["Low","Medium","High"].indexOf(riskData[i].name)]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(220,18%,10%)", border: "1px solid hsl(220,14%,18%)", borderRadius: 8, color: "#fff" }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
