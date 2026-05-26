import { useState, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, Camera, AlertTriangle, CheckCircle, IndianRupee, Car, Shield, ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";

interface Violation {
  violation_type: string;
  severity: "Low" | "Medium" | "High";
  penalty_amount: number;
  description: string;
  location_in_image: string;
}

interface AnalysisResult {
  violations: Violation[];
  summary: string;
  total_penalty: number;
  vehicle_count: number;
}

const severityConfig = {
  Low: { color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30", icon: "🟡" },
  Medium: { color: "bg-orange-500/20 text-orange-400 border-orange-500/30", icon: "🟠" },
  High: { color: "bg-red-500/20 text-red-400 border-red-500/30", icon: "🔴" },
};

export default function ViolationDetector() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const { toast } = useToast();

  const processFile = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) {
      toast({ title: "Invalid file", description: "Please upload an image file.", variant: "destructive" });
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast({ title: "File too large", description: "Max 10MB allowed.", variant: "destructive" });
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      setImagePreview(dataUrl);
      setImageBase64(dataUrl.split(",")[1]);
      setResult(null);
    };
    reader.readAsDataURL(file);
  }, [toast]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  const analyzeImage = async () => {
    if (!imageBase64) return;
    setLoading(true);
    setResult(null);

    try {
      const { data, error } = await supabase.functions.invoke("detect-violations", {
        body: { imageBase64 },
      });

      if (error) throw error;
      setResult(data as AnalysisResult);
      toast({
        title: data.violations.length > 0 ? "Violations Detected!" : "No Violations Found",
        description: data.summary,
        variant: data.violations.length > 0 ? "destructive" : "default",
      });
    } catch (err: any) {
      console.error(err);
      toast({ title: "Analysis Failed", description: err.message || "Please try again.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-6">
      {/* Header */}
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button>
          </Link>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-2">
              <Shield className="h-7 w-7 text-primary" /> Traffic Violation Detector
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Upload a traffic image to detect violations and view penalties
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="space-y-4">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Camera className="h-4 w-4" /> Upload Image
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
                    dragOver ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById("file-input")?.click()}
                >
                  <input
                    id="file-input"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) processFile(file);
                    }}
                  />
                  <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
                  <p className="font-medium">Drop image here or click to upload</p>
                  <p className="text-xs text-muted-foreground mt-1">PNG, JPG, WEBP • Max 10MB</p>
                </div>
              </CardContent>
            </Card>

            {imagePreview && (
              <Card className="bg-card border-border overflow-hidden">
                <CardContent className="p-2">
                  <img src={imagePreview} alt="Traffic" className="w-full rounded-lg object-contain max-h-[400px]" />
                </CardContent>
              </Card>
            )}

            {imagePreview && (
              <Button
                onClick={analyzeImage}
                disabled={loading}
                className="w-full h-12 text-base font-semibold"
                size="lg"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                    Analyzing...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" /> Detect Violations
                  </span>
                )}
              </Button>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-4">
            {!result && !loading && (
              <Card className="bg-card border-border h-full flex items-center justify-center min-h-[300px]">
                <CardContent className="text-center text-muted-foreground">
                  <Car className="h-16 w-16 mx-auto mb-4 opacity-30" />
                  <p className="text-lg font-medium">No analysis yet</p>
                  <p className="text-sm mt-1">Upload an image to start detecting violations</p>
                </CardContent>
              </Card>
            )}

            {loading && (
              <Card className="bg-card border-border h-full flex items-center justify-center min-h-[300px]">
                <CardContent className="text-center">
                  <span className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full inline-block mb-4" />
                  <p className="text-lg font-medium">Analyzing traffic image...</p>
                  <p className="text-sm text-muted-foreground mt-1">AI is scanning for violations</p>
                </CardContent>
              </Card>
            )}

            {result && (
              <>
                {/* Summary Card */}
                <Card className={`border ${result.violations.length > 0 ? "border-destructive/50 bg-destructive/5" : "border-primary/50 bg-primary/5"}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {result.violations.length > 0 ? (
                        <AlertTriangle className="h-6 w-6 text-destructive shrink-0 mt-0.5" />
                      ) : (
                        <CheckCircle className="h-6 w-6 text-primary shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className="font-semibold text-lg">
                          {result.violations.length > 0
                            ? `${result.violations.length} Violation${result.violations.length > 1 ? "s" : ""} Detected`
                            : "No Violations Detected"}
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">{result.summary}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-3">
                  <Card className="bg-card border-border">
                    <CardContent className="p-3 text-center">
                      <p className="text-2xl font-bold text-primary">{result.vehicle_count}</p>
                      <p className="text-xs text-muted-foreground">Vehicles</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-3 text-center">
                      <p className="text-2xl font-bold text-destructive">{result.violations.length}</p>
                      <p className="text-xs text-muted-foreground">Violations</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-3 text-center">
                      <p className="text-2xl font-bold text-accent flex items-center justify-center">
                        <IndianRupee className="h-5 w-5" />{result.total_penalty.toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground">Total Fine</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Violations List */}
                {result.violations.map((v, i) => (
                  <Card key={i} className="bg-card border-border">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">{severityConfig[v.severity].icon}</span>
                            <h3 className="font-bold text-base">{v.violation_type}</h3>
                            <Badge variant="outline" className={severityConfig[v.severity].color}>
                              {v.severity}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{v.description}</p>
                          <p className="text-xs text-muted-foreground mt-1">📍 {v.location_in_image}</p>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="text-xl font-bold text-destructive flex items-center">
                            <IndianRupee className="h-4 w-4" />{v.penalty_amount.toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">Penalty</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
