"""
03_enrich.py  —  Enrichment & Hub Scoring
==========================================
Reads cleaned_athletes.json (all-time Team USA athletes)
Outputs:
  - state_hubs.json        → one record per state, powers the map
  - enriched_athletes.json → individual athletes with region added

Hub score formula (0-100):
  40% — total athletes from state (all-time volume)
  35% — athletes per million residents (per-capita punch)
  25% — sport diversity (unique sports represented)

Run: python 03_enrich.py
"""

import json
from collections import Counter, defaultdict

INPUT_FILE   = "cleaned_athletes.json"
OUT_HUBS     = "state_hubs.json"
OUT_ATHLETES = "enriched_athletes.json"

# ── Full state names ──────────────────────────────────────────────────────────
STATE_NAMES = {
    "AL":"Alabama",       "AK":"Alaska",        "AZ":"Arizona",
    "AR":"Arkansas",      "CA":"California",    "CO":"Colorado",
    "CT":"Connecticut",   "DE":"Delaware",      "FL":"Florida",
    "GA":"Georgia",       "HI":"Hawaii",        "ID":"Idaho",
    "IL":"Illinois",      "IN":"Indiana",       "IA":"Iowa",
    "KS":"Kansas",        "KY":"Kentucky",      "LA":"Louisiana",
    "ME":"Maine",         "MD":"Maryland",      "MA":"Massachusetts",
    "MI":"Michigan",      "MN":"Minnesota",     "MS":"Mississippi",
    "MO":"Missouri",      "MT":"Montana",       "NE":"Nebraska",
    "NV":"Nevada",        "NH":"New Hampshire", "NJ":"New Jersey",
    "NM":"New Mexico",    "NY":"New York",      "NC":"North Carolina",
    "ND":"North Dakota",  "OH":"Ohio",          "OK":"Oklahoma",
    "OR":"Oregon",        "PA":"Pennsylvania",  "RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota",  "TN":"Tennessee",
    "TX":"Texas",         "UT":"Utah",          "VT":"Vermont",
    "VA":"Virginia",      "WA":"Washington",    "WV":"West Virginia",
    "WI":"Wisconsin",     "WY":"Wyoming",       "DC":"Washington D.C.",
}

# ── US Census 2020 populations ────────────────────────────────────────────────
STATE_POP = {
    "AL":5024279,  "AK":733391,   "AZ":7151502,  "AR":3011524,
    "CA":39538223, "CO":5773714,  "CT":3605944,  "DE":989948,
    "FL":21538187, "GA":10711908, "HI":1455271,  "ID":1839106,
    "IL":12812508, "IN":6785528,  "IA":3190369,  "KS":2937880,
    "KY":4505836,  "LA":4657757,  "ME":1362359,  "MD":6177224,
    "MA":7029917,  "MI":10077331, "MN":5706494,  "MS":2961279,
    "MO":6154913,  "MT":1084225,  "NE":1961504,  "NV":3104614,
    "NH":1377529,  "NJ":9288994,  "NM":2117522,  "NY":20201249,
    "NC":10439388, "ND":779094,   "OH":11799448, "OK":3959353,
    "OR":4237256,  "PA":13002700, "RI":1097379,  "SC":5118425,
    "SD":886667,   "TN":6910840,  "TX":29145505, "UT":3271616,
    "VT":643077,   "VA":8631393,  "WA":7705281,  "WV":1793716,
    "WI":5893718,  "WY":576851,   "DC":689545,
}

# ── US Census regions ─────────────────────────────────────────────────────────
REGION = {
    "CT":"Northeast","ME":"Northeast","MA":"Northeast","NH":"Northeast",
    "NJ":"Northeast","NY":"Northeast","PA":"Northeast","RI":"Northeast","VT":"Northeast",
    "IL":"Midwest",  "IN":"Midwest",  "IA":"Midwest",  "KS":"Midwest",
    "MI":"Midwest",  "MN":"Midwest",  "MO":"Midwest",  "NE":"Midwest",
    "ND":"Midwest",  "OH":"Midwest",  "SD":"Midwest",  "WI":"Midwest",
    "AL":"South",    "AR":"South",    "DE":"South",    "FL":"South",
    "GA":"South",    "KY":"South",    "LA":"South",    "MD":"South",
    "MS":"South",    "NC":"South",    "OK":"South",    "SC":"South",
    "TN":"South",    "TX":"South",    "VA":"South",    "WV":"South",  "DC":"South",
    "AK":"West",     "AZ":"West",     "CA":"West",     "CO":"West",
    "HI":"West",     "ID":"West",     "MT":"West",     "NV":"West",
    "NM":"West",     "OR":"West",     "UT":"West",     "WA":"West",   "WY":"West",
}

# ── Climate indicators ────────────────────────────────────────────────────────
CLIMATE = {
    "AK":{"coastal":True, "cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "AL":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "AZ":{"coastal":False,"cold_winters":False,"high_elevation":True, "snow_sport_tradition":False},
    "AR":{"coastal":False,"cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "CA":{"coastal":True, "cold_winters":False,"high_elevation":True, "snow_sport_tradition":True},
    "CO":{"coastal":False,"cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "CT":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "DE":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "FL":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "GA":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "HI":{"coastal":True, "cold_winters":False,"high_elevation":True, "snow_sport_tradition":False},
    "ID":{"coastal":False,"cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "IL":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "IN":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "IA":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "KS":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "KY":{"coastal":False,"cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "LA":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "ME":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":True},
    "MD":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "MA":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "MI":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":True},
    "MN":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":True},
    "MS":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "MO":{"coastal":False,"cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "MT":{"coastal":False,"cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "NE":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "NV":{"coastal":False,"cold_winters":False,"high_elevation":True, "snow_sport_tradition":False},
    "NH":{"coastal":True, "cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "NJ":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "NM":{"coastal":False,"cold_winters":False,"high_elevation":True, "snow_sport_tradition":False},
    "NY":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":True},
    "NC":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "ND":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "OH":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "OK":{"coastal":False,"cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "OR":{"coastal":True, "cold_winters":False,"high_elevation":True, "snow_sport_tradition":True},
    "PA":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "RI":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "SC":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "SD":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "TN":{"coastal":False,"cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "TX":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "UT":{"coastal":False,"cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "VT":{"coastal":False,"cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "VA":{"coastal":True, "cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
    "WA":{"coastal":True, "cold_winters":False,"high_elevation":True, "snow_sport_tradition":True},
    "WV":{"coastal":False,"cold_winters":True, "high_elevation":False,"snow_sport_tradition":False},
    "WI":{"coastal":True, "cold_winters":True, "high_elevation":False,"snow_sport_tradition":True},
    "WY":{"coastal":False,"cold_winters":True, "high_elevation":True, "snow_sport_tradition":True},
    "DC":{"coastal":False,"cold_winters":False,"high_elevation":False,"snow_sport_tradition":False},
}


# ── Insight generator ─────────────────────────────────────────────────────────

def build_insight(state, total, per_capita, top_sports, sport_group, climate):
    """
    Conditional all-time insight text.
    Never implies geography guarantees results.
    Uses full state name throughout.
    """
    c         = climate or {}
    full_name = STATE_NAMES.get(state, state)

    # Top sports string
    if len(top_sports) >= 3:
        sports_str = f"{top_sports[0]}, {top_sports[1]}, and {top_sports[2]}"
    elif len(top_sports) == 2:
        sports_str = f"{top_sports[0]} and {top_sports[1]}"
    elif len(top_sports) == 1:
        sports_str = top_sports[0]
    else:
        sports_str = "various sports"

    # Line 1: geography + sport association
    if sport_group == "Winter" and c.get("snow_sport_tradition"):
        line1 = (
            f"Over the years, {full_name}'s cold winters and mountain terrain "
            f"could help explain its historical association with disciplines "
            f"like {sports_str}."
        )
    elif sport_group == "Winter" and c.get("cold_winters"):
        line1 = (
            f"Historically, {full_name}'s cold climate has commonly been associated "
            f"with pathways toward winter sports like {sports_str}."
        )
    elif sport_group == "Summer" and c.get("coastal"):
        line1 = (
            f"Across Team USA's history, {full_name}'s coastal access and climate "
            f"could help explain strong representation in sports like {sports_str}."
        )
    elif sport_group == "Summer" and c.get("high_elevation"):
        line1 = (
            f"Over time, {full_name}'s varied terrain and climate could help support "
            f"athlete development in disciplines like {sports_str}."
        )
    else:
        line1 = (
            f"Across Team USA's history, {full_name}'s geography and infrastructure "
            f"could help support athletes in disciplines like {sports_str}."
        )

    # Line 2: volume context
    if total >= 500:
        line2 = (
            f"With {total} athletes represented all-time, {full_name} has historically "
            f"been one of the most prominent contributors to Team USA."
        )
    elif total >= 200:
        line2 = (
            f"With {total} athletes represented all-time, {full_name} could be "
            f"considered a consistent contributor to Team USA's pipeline."
        )
    else:
        line2 = (
            f"With {total} athletes represented all-time, {full_name} could be "
            f"an emerging contributor to Team USA's talent pipeline."
        )

    # Line 3: per capita (only if notable)
    if per_capita >= 8:
        line3 = (
            f"At {per_capita:.1f} athletes per million residents, {full_name} could "
            f"be punching significantly above its weight historically."
        )
    elif per_capita >= 4:
        line3 = (
            f"At {per_capita:.1f} athletes per million residents, {full_name} has "
            f"historically shown strong per-capita representation on Team USA."
        )
    else:
        line3 = None

    parts = [line1, line2]
    if line3:
        parts.append(line3)

    return " ".join(parts)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        athletes = json.load(f)

    print(f"Loaded {len(athletes)} cleaned athletes")

    # Aggregate by state
    by_state = defaultdict(list)
    for a in athletes:
        if a.get("state"):
            by_state[a["state"]].append(a)

    # Add region to individual athletes
    for a in athletes:
        a["region"] = REGION.get(a.get("state"))

    # Build state hub records
    state_records = []

    for state, group in by_state.items():
        total        = len(group)
        olympians    = sum(1 for a in group if a["category"] == "Olympian")
        paralympians = sum(1 for a in group if a["category"] == "Paralympian")
        teamusa      = sum(1 for a in group if a["category"] == "Team USA")
        winter       = sum(1 for a in group if a.get("sport_group") == "Winter")
        summer       = sum(1 for a in group if a.get("sport_group") == "Summer")

        pop        = STATE_POP.get(state, 1)
        per_capita = round((total / pop) * 1_000_000, 1)

        sports        = [a["sport"] for a in group if a.get("sport")]
        unique_sports = len(set(sports))
        top_sports    = [s for s, _ in Counter(sports).most_common(5)]
        top_sport     = top_sports[0] if top_sports else "various sports"
        sport_group   = "Winter" if winter > summer else "Summer"

        state_records.append({
            "state":         state,
            "state_name":    STATE_NAMES.get(state, state),
            "region":        REGION.get(state),
            "total":         total,
            "olympians":     olympians,
            "paralympians":  paralympians,
            "teamusa":       teamusa,
            "winter":        winter,
            "summer":        summer,
            "per_capita":    per_capita,
            "unique_sports": unique_sports,
            "top_sports":    top_sports,
            "top_sport":     top_sport,
            "sport_group":   sport_group,
            "_climate":      CLIMATE.get(state, {}),
        })

    # Normalize & compute hub score
    max_total     = max(r["total"]         for r in state_records)
    max_capita    = max(r["per_capita"]    for r in state_records)
    max_diversity = max(r["unique_sports"] for r in state_records)

    for r in state_records:
        score_total     = (r["total"]         / max_total)     * 40
        score_capita    = (r["per_capita"]    / max_capita)    * 35
        score_diversity = (r["unique_sports"] / max_diversity) * 25
        r["hub_score"]  = round(score_total + score_capita + score_diversity, 1)

        r["insight"] = build_insight(
            r["state"], r["total"], r["per_capita"],
            r["top_sports"], r["sport_group"], r["_climate"],
        )
        del r["_climate"]

    # Sort by hub score
    state_records.sort(key=lambda r: r["hub_score"], reverse=True)

    # Save
    with open(OUT_HUBS, "w", encoding="utf-8") as f:
        json.dump(state_records, f, indent=2, ensure_ascii=False)

    with open(OUT_ATHLETES, "w", encoding="utf-8") as f:
        json.dump(athletes, f, indent=2, ensure_ascii=False)

    # Stats
    print(f"\nSaved → {OUT_HUBS}  ({len(state_records)} states)")
    print(f"Saved → {OUT_ATHLETES}  ({len(athletes)} athletes)")

    print(f"\n── Top 10 hubs ──")
    for r in state_records[:10]:
        print(
            f"  {r['state']}  score:{r['hub_score']:>5}  "
            f"total:{r['total']:>4}  "
            f"per_capita:{r['per_capita']:>5}  "
            f"sports:{r['unique_sports']:>2}  "
            f"dominant:{r['sport_group']}"
        )

    print(f"\n── Sample record ──")
    print(json.dumps(state_records[0], indent=2))


if __name__ == "__main__":
    main()
