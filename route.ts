import { NextRequest, NextResponse } from "next/server";

const CLIMATE: Record<string, { coastal: boolean; cold_winters: boolean; high_elevation: boolean; snow_sport_tradition: boolean }> = {
  "AK":{"coastal":true,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "AL":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "AZ":{"coastal":false,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":false},
  "AR":{"coastal":false,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "CA":{"coastal":true,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":true},
  "CO":{"coastal":false,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "CT":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "DE":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "FL":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "GA":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "HI":{"coastal":true,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":false},
  "ID":{"coastal":false,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "IL":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "IN":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "IA":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "KS":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "KY":{"coastal":false,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "LA":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "ME":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":true},
  "MD":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "MA":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "MI":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":true},
  "MN":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":true},
  "MS":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "MO":{"coastal":false,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "MT":{"coastal":false,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "NE":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "NV":{"coastal":false,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":false},
  "NH":{"coastal":true,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "NJ":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "NM":{"coastal":false,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":false},
  "NY":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":true},
  "NC":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "ND":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "OH":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "OK":{"coastal":false,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "OR":{"coastal":true,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":true},
  "PA":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "RI":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "SC":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "SD":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "TN":{"coastal":false,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "TX":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "UT":{"coastal":false,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "VT":{"coastal":false,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "VA":{"coastal":true,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
  "WA":{"coastal":true,"cold_winters":false,"high_elevation":true,"snow_sport_tradition":true},
  "WV":{"coastal":false,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":false},
  "WI":{"coastal":true,"cold_winters":true,"high_elevation":false,"snow_sport_tradition":true},
  "WY":{"coastal":false,"cold_winters":true,"high_elevation":true,"snow_sport_tradition":true},
  "DC":{"coastal":false,"cold_winters":false,"high_elevation":false,"snow_sport_tradition":false},
};

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { state, state_name, total, per_capita, top_sports, sport_group, region, winter, summer, olympians, paralympians, unique_sports } = body;

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      console.error("No GEMINI_API_KEY found");
      return NextResponse.json({ insight: "API key missing." });
    }

    const climate = CLIMATE[state] || {};
    const climateTraits = [
      climate.coastal              && "coastal access",
      climate.cold_winters         && "cold winters",
      climate.high_elevation       && "high elevation terrain",
      climate.snow_sport_tradition && "a snow sport tradition",
    ].filter(Boolean).join(", ") || "varied geography";

    const nationalTotal = 5467;
    const sharePercent  = Math.round((total / nationalTotal) * 100);

    const prompt = `You are an analyst for the Hometown Success Engine, a tool exploring how American geography could help find Team USA talent.

Write 2-3 sentences about ${state_name} as a potential Team USA hub. Use ONLY conditional language. Never say geography guarantees results.

Facts about ${state_name}:
- Region: ${region}
- Geographic traits: ${climateTraits}
- Total all-time Team USA athletes: ${total} out of ${nationalTotal} nationally (~${sharePercent}% of all Team USA athletes)
- Breakdown: ${olympians} Olympians, ${paralympians} Paralympians
- Athletes per million residents: ${per_capita}/M
- Sport diversity: ${unique_sports} out of 71 sports represented
- Dominant season: ${sport_group} (${winter} winter athletes, ${summer} summer athletes)
- Top sports: ${top_sports.join(", ")}

Rules:
- Reference the geographic traits (terrain, climate) specifically
- Mention at least 2 specific numbers from the facts above
- Use conditional phrasing only: "could help", "may support", "might foster"
- Keep it to 2-3 sentences
- Treat Olympic and Paralympic athletes with equal prominence
- Never mention specific athlete names`;

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            maxOutputTokens: 500,
            temperature: 0.7,
            thinkingConfig: {
              thinkingBudget: 0,
            },
          },
        }),
      }
    );

    const data = await response.json();
    console.log("Status:", response.status);
    console.log("Gemini data:", JSON.stringify(data).slice(0, 300));

    const text = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "Insight unavailable.";
    return NextResponse.json({ insight: text });

  } catch (err) {
    console.error("Insight error:", err);
    return NextResponse.json({ insight: "Error generating insight." });
  }
}