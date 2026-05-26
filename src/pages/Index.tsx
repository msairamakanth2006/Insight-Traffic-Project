import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getVehicles, getHotspots, getStats } from "@/data/mockTrafficData";
import StatsBar from "@/components/dashboard/StatsBar";
import VehicleTable from "@/components/dashboard/VehicleTable";
import BehaviorChart from "@/components/dashboard/BehaviorChart";
import HotspotPanel from "@/components/dashboard/HotspotPanel";
import PipelineStatus from "@/components/dashboard/PipelineStatus";
import { Badge } from "@/components/ui/badge";
import { Radio, Shield, ArrowLeft, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const [vehicles, setVehicles] = useState(getVehicles());
  const hotspots = getHotspots();
  const stats = getStats(vehicles);

  useEffect(() => {
    const interval = setInterval(() => {
      setVehicles(getVehicles());
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Top nav */}
      <nav className="border-b border-border/50 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Zap className="h-4 w-4 text-primary" />
              </div>
              <h1 className="text-lg font-bold tracking-tight">Command Center</h1>
            </div>
          </div>
          <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 gap-1.5 py-1">
            <Radio className="h-3 w-3 animate-pulse" />
            LIVE
          </Badge>
        </div>
      </nav>

      {/* Dashboard content */}
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Stats row */}
        <StatsBar stats={stats} />

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: table + charts */}
          <div className="lg:col-span-2 space-y-6">
            <VehicleTable vehicles={vehicles} />
            <BehaviorChart stats={stats} />
          </div>

          {/* Right sidebar */}
          <div className="space-y-6">
            <PipelineStatus />
            <HotspotPanel hotspots={hotspots} />
          </div>
        </div>
      </div>
    </div>
  );
}
