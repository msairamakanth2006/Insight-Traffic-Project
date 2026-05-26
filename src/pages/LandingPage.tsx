import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Shield, Activity, MapPin, Camera, Eye, Brain, Zap,
  Car, BarChart3, AlertTriangle, ArrowRight
} from "lucide-react";

const features = [
  {
    icon: Eye,
    title: "Real-Time Detection",
    description: "YOLOv8-powered vehicle detection processes live traffic feeds with 30+ FPS accuracy.",
  },
  {
    icon: Brain,
    title: "Behavior Analysis",
    description: "AI classifies driving patterns as Safe, Moderate, or Aggressive in real-time.",
  },
  {
    icon: Shield,
    title: "Risk Scoring",
    description: "Each vehicle gets a 0-100 risk score based on speed, acceleration, and behavior.",
  },
  {
    icon: MapPin,
    title: "Hotspot Detection",
    description: "DBSCAN clustering identifies accident-prone zones from historical data.",
  },
  {
    icon: Camera,
    title: "Violation Detection",
    description: "Upload traffic images to detect violations like signal jumping, no helmet, and more.",
  },
  {
    icon: BarChart3,
    title: "Live Dashboard",
    description: "Monitor all vehicles, risk levels, and hotspots from a centralized command center.",
  },
];

const stats = [
  { label: "Vehicles Tracked", value: "10K+", icon: Car },
  { label: "Violations Detected", value: "2.5K+", icon: AlertTriangle },
  { label: "Hotspots Identified", value: "150+", icon: MapPin },
  { label: "System Uptime", value: "99.9%", icon: Activity },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="border-b border-border/50 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Zap className="h-5 w-5 text-primary" />
            </div>
            <span className="text-lg font-bold tracking-tight">TrafficAI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/dashboard">
              <Button variant="ghost" size="sm">Dashboard</Button>
            </Link>
            <Link to="/detect">
              <Button variant="ghost" size="sm">Violation Detector</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 relative">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm text-primary mb-6">
              <Activity className="h-3.5 w-3.5 animate-pulse" />
              AI-Powered Traffic Intelligence
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
              Smart Traffic
              <span className="text-primary"> Detection</span> &
              <span className="text-accent"> Safety</span> System
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Real-time vehicle monitoring, AI-powered violation detection, risk scoring,
              and accident hotspot prediction — all in one intelligent platform.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/dashboard">
                <Button size="lg" className="h-12 px-8 text-base gap-2">
                  <BarChart3 className="h-5 w-5" /> Get Started
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border/50 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <s.icon className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-3xl font-bold">{s.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight">
            Complete Traffic Intelligence Suite
          </h2>
          <p className="text-muted-foreground mt-3 max-w-xl mx-auto">
            Six integrated modules working together to make roads safer.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <Card key={f.title} className="bg-card border-border hover:border-primary/30 transition-colors group">
              <CardContent className="p-6">
                <div className="h-11 w-11 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <f.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-muted-foreground">
          <p>© 2026 TrafficAI — Smart Traffic Detection & Safety System</p>
        </div>
      </footer>
    </div>
  );
}
