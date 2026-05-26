import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { imageBase64 } = await req.json();
    if (!imageBase64) {
      return new Response(JSON.stringify({ error: "No image provided" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    const systemPrompt = `You are a traffic violation detection AI. Analyze the provided traffic image and detect ALL traffic violations visible.

For each violation found, return:
- violation_type: specific type (e.g. "Red Light Running", "No Helmet", "Wrong Way Driving", "Over Speeding", "No Seatbelt", "Triple Riding", "Illegal Parking", "Lane Violation", "Using Mobile Phone", "Drunk Driving Suspected", "No Number Plate", "Overloading", "Zebra Crossing Violation")
- severity: "Low", "Medium", or "High"
- penalty_amount: fine amount in INR (Indian Rupees)
- description: brief description of what you see
- location_in_image: where in the image (e.g. "center", "left side", "top right")

If NO violations are detected, return an empty violations array with a message saying traffic rules are being followed.

Common Indian traffic penalties (use these as reference):
- Red Light Jumping: ₹1,000 - ₹5,000
- No Helmet: ₹1,000
- No Seatbelt: ₹1,000
- Over Speeding: ₹1,000 - ₹2,000
- Using Mobile Phone: ₹1,000 - ₹5,000
- Wrong Way Driving: ₹1,000 - ₹5,000
- Triple Riding: ₹1,000
- Illegal Parking: ₹500 - ₹1,500
- No Number Plate: ₹5,000
- Overloading: ₹2,000 - ₹20,000
- Drunk Driving: ₹10,000
- Lane Violation: ₹500 - ₹1,000
- Zebra Crossing Violation: ₹500`;

    const response = await fetch(
      "https://ai.gateway.lovable.dev/v1/chat/completions",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${LOVABLE_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "google/gemini-2.5-flash",
          messages: [
            { role: "system", content: systemPrompt },
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "Analyze this traffic image for violations. Return results as JSON.",
                },
                {
                  type: "image_url",
                  image_url: { url: `data:image/jpeg;base64,${imageBase64}` },
                },
              ],
            },
          ],
          tools: [
            {
              type: "function",
              function: {
                name: "report_violations",
                description: "Report detected traffic violations",
                parameters: {
                  type: "object",
                  properties: {
                    violations: {
                      type: "array",
                      items: {
                        type: "object",
                        properties: {
                          violation_type: { type: "string" },
                          severity: {
                            type: "string",
                            enum: ["Low", "Medium", "High"],
                          },
                          penalty_amount: { type: "number" },
                          description: { type: "string" },
                          location_in_image: { type: "string" },
                        },
                        required: [
                          "violation_type",
                          "severity",
                          "penalty_amount",
                          "description",
                          "location_in_image",
                        ],
                      },
                    },
                    summary: { type: "string" },
                    total_penalty: { type: "number" },
                    vehicle_count: { type: "number" },
                  },
                  required: [
                    "violations",
                    "summary",
                    "total_penalty",
                    "vehicle_count",
                  ],
                },
              },
            },
          ],
          tool_choice: {
            type: "function",
            function: { name: "report_violations" },
          },
        }),
      }
    );

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ error: "Rate limit exceeded. Please try again shortly." }),
          { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ error: "AI credits exhausted. Please add funds." }),
          { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      const errText = await response.text();
      console.error("AI gateway error:", response.status, errText);
      throw new Error("AI analysis failed");
    }

    const data = await response.json();
    const toolCall = data.choices?.[0]?.message?.tool_calls?.[0];

    if (!toolCall) {
      throw new Error("No analysis returned from AI");
    }

    const result = JSON.parse(toolCall.function.arguments);

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("detect-violations error:", e);
    return new Response(
      JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
