"""
02_clean.py  —  Clean & Normalize
==================================
The API data is already pretty clean. This script:
  1. Drops rows where BOTH state and hometown are null
  2. Normalizes the small set of known messy state strings
  3. Keeps sport names exactly as-is (API already returns clean labels)
  4. Keeps all 3 categories: Olympian, Paralympian, Team USA
  5. Adds a sport_group field for map filtering (Summer / Winter / Para)

Input:  raw_athletes.json
Output: cleaned_athletes.json

Run: python 02_clean.py
"""

import json
from collections import Counter

INPUT_FILE  = "raw_athletes.json"
OUTPUT_FILE = "cleaned_athletes.json"

VALID_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC",
}

# Only the variants actually seen in the data
STATE_FIX = {
    "N.Y":"NY", "N.Y.":"NY",
    "N.J":"NJ", "N.J.":"NJ",
    "PENN":"PA", "PENN.":"PA",
    "CALIF":"CA", "CALIF.":"CA",
    "MASS":"MA", "MASS.":"MA",
    "CONN":"CT", "CONN.":"CT",
    "D.C":"DC",  "D.C.":"DC",
}

# Sport → group for map filter
# Every distinct sport name confirmed from inspect.py output
# Replace SPORT_GROUP in 02_clean.py with this

SPORT_GROUP = {

    # ── WINTER ───────────────────────────────────────────────────────
    # Olympic winter
    "Alpine Skiing":             "Winter",
    "Biathlon":                  "Winter",
    "Bobsled":                   "Winter",
    "Cross-Country Skiing":      "Winter",
    "Curling":                   "Winter",
    "Figure Skating":            "Winter",
    "Freestyle Skiing":          "Winter",
    "Ice Hockey":                "Winter",
    "Luge":                      "Winter",
    "Nordic Combined":           "Winter",
    "Short Track Speedskating":  "Winter",
    "Skeleton":                  "Winter",
    "Ski Jumping":               "Winter",
    "Ski Mountaineering":        "Winter",
    "Snowboarding":              "Winter",
    "Speedskating":              "Winter",
    # Paralympic winter (same snow/ice environments)
    "Para Alpine Skiing":        "Winter",
    "Para Biathlon":             "Winter",
    "Para Nordic Skiing":        "Winter",
    "Para Snowboarding":         "Winter",
    "Sled Hockey":               "Winter",
    "Wheelchair Curling":        "Winter",

    # ── SUMMER ───────────────────────────────────────────────────────
    # Olympic summer
    "Archery":                   "Summer",
    "Artistic Gymnastics":       "Summer",
    "Artistic Swimming":         "Summer",
    "Badminton":                 "Summer",
    "Baseball":                  "Summer",
    "Basketball":                "Summer",
    "Basque Pelota":             "Summer",
    "Beach Volleyball":          "Summer",
    "Bowling":                   "Summer",
    "Boxing":                    "Summer",
    "Breaking":                  "Summer",
    "Canoe/Kayak":               "Summer",
    "Cycling":                   "Summer",
    "Cycling - BMX":             "Summer",
    "Cycling - Mountain":        "Summer",
    "Cycling - Road":            "Summer",
    "Cycling - Track":           "Summer",
    "Diving":                    "Summer",
    "Equestrian":                "Summer",
    "Fencing":                   "Summer",
    "Field Hockey":              "Summer",
    "Golf":                      "Summer",
    "Handball":                  "Summer",
    "Judo":                      "Summer",
    "Karate":                    "Summer",
    "Marathon Swimming":         "Summer",
    "Modern Pentathlon":         "Summer",
    "Racquetball":               "Summer",
    "Rhythmic Gymnastics":       "Summer",
    "Roller Sports":             "Summer",
    "Rowing":                    "Summer",
    "Rugby Sevens":              "Summer",
    "Sailing":                   "Summer",
    "Shooting":                  "Summer",
    "Skateboarding":             "Summer",
    "Soccer":                    "Summer",
    "Softball":                  "Summer",
    "Sport Climbing":            "Summer",
    "Squash":                    "Summer",
    "Surfing":                   "Summer",
    "Swimming":                  "Summer",
    "Table Tennis":              "Summer",
    "Taekwondo":                 "Summer",
    "Team Handball":             "Summer",
    "Tennis":                    "Summer",
    "Triathlon":                 "Summer",
    "Volleyball":                "Summer",
    "Water Polo":                "Summer",
    "Waterski/Wakeboard":        "Summer",
    "Weightlifting":             "Summer",
    "Wrestling":                 "Summer",
    # Paralympic summer (same warm/indoor environments)
    "Boccia":                    "Summer",
    "Goalball":                  "Summer",
    "Para Archery":              "Summer",
    "Para Badminton":            "Summer",
    "Para Canoe/Kayak":          "Summer",
    "Para Cycling":              "Summer",
    "Para Equestrian":           "Summer",
    "Para Judo":                 "Summer",
    "Para Powerlifting":         "Summer",
    "Para Rowing":               "Summer",
    "Para Shooting":             "Summer",
    "Para Swimming":             "Summer",
    "Para Table Tennis":         "Summer",
    "Para Taekwondo":            "Summer",
    "Para Track and Field":      "Summer",
    "Para Triathlon":            "Summer",
    "Sitting Volleyball":        "Summer",
    "Wheelchair Basketball":     "Summer",
    "Wheelchair Fencing":        "Summer",
    "Wheelchair Rugby":          "Summer",
    "Wheelchair Tennis":         "Summer",
    "Track and Field":           "Summer",
    "3x3 Basketball":            "Summer",
    "Gymnastics":      "Summer",
    "Para-Cycling":    "Summer",
    "Para-Equestrian": "Summer",
    "Para-Rowing":     "Summer",
    "Paracanoe":       "Summer",
    "Paratriathlon":   "Summer",
    "Rifle Shooting":  "Summer",
    "Rugby":           "Summer",
    "Soccer 7-A-Side": "Summer",
}


def normalize_state(raw: str) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    # Check fix map first (preserves dots for matching)
    upper = s.upper()
    if upper in STATE_FIX:
        return STATE_FIX[upper]
    # Strip dots and spaces, check again
    cleaned = upper.replace(".", "").replace(" ", "")
    if cleaned in STATE_FIX:
        return STATE_FIX[cleaned]
    if cleaned in VALID_STATES:
        return cleaned
    return None


def normalize_category(raw: str) -> str | None:
    if not raw:
        return None
    mapping = {
        "olympian":    "Olympian",
        "paralympian": "Paralympian",
        "team usa":    "Team USA",
        "team_usa":    "Team USA",
    }
    return mapping.get(raw.strip().lower(), raw.strip())


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    print(f"Loaded {len(raw)} raw athletes")

    cleaned = []
    dropped = 0

    for entry in raw:
        # ── Normalize state ──
        state = normalize_state(entry.get("state"))

        # If still null try parsing from hometown
        if not state:
            ht = entry.get("hometown") or ""
            parts = ht.rsplit(",", 1)
            if len(parts) == 2:
                state = normalize_state(parts[1].strip())

        hometown = entry.get("hometown") or None

        # ── Drop if both null ──
        if not state and not hometown:
            dropped += 1
            continue

        sport    = (entry.get("sport") or "").strip() or None
        category = normalize_category(entry.get("category"))

        # ── Add sport_group for map filtering ──
        sport_group = SPORT_GROUP.get(sport) if sport else None

        cleaned.append({
            "hometown":    hometown,
            "state":       state,
            "sport":       sport,
            "sport_group": sport_group,
            "category":    category,
        })

    # ── Save ──
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    # ── Stats ──
    total        = len(cleaned)
    olympians    = sum(1 for a in cleaned if a["category"] == "Olympian")
    paralympians = sum(1 for a in cleaned if a["category"] == "Paralympian")
    teamusa      = sum(1 for a in cleaned if a["category"] == "Team USA")
    with_state   = sum(1 for a in cleaned if a["state"])
    other_group  = sum(1 for a in cleaned if a["sport_group"] == "Other")

    print(f"\nSaved → {OUTPUT_FILE}")
    print(f"  Total kept     : {total}")
    print(f"  Dropped        : {dropped}")
    print(f"  Olympians      : {olympians}")
    print(f"  Paralympians   : {paralympians}")
    print(f"  Team USA       : {teamusa}")
    print(f"  With state     : {with_state} / {total}")
    print(f"  sport_group=Other (unmapped sports): {other_group}")

    # ── State breakdown ──
    state_counts = Counter(a["state"] for a in cleaned if a["state"])
    print("\n── Top 15 states ──")
    for state, count in state_counts.most_common(15):
        print(f"  {state}: {count}")

    # ── Sport group breakdown ──
    group_counts = Counter(a["sport_group"] for a in cleaned)
    print("\n── Sport groups ──")
    for group, count in group_counts.most_common():
        print(f"  {group}: {count}")

    # ── Any unmapped sports ──
    other_sports = Counter(
        a["sport"] for a in cleaned
        if a["sport_group"] == "Other"
    )
    if other_sports:
        print(f"\n── Unmapped sports (add to SPORT_GROUP) ──")
        for sport, count in other_sports.most_common():
            print(f"  '{sport}': {count}")

    print("\n── Sample (first 3) ──")
    for a in cleaned[:3]:
        print(json.dumps(a, indent=2))


if __name__ == "__main__":
    main()
