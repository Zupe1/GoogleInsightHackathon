"""
scrape.py  —  Team USA API → raw_athletes.json
===============================================
Hits the teamusa.com JSON API directly (same as the working CSV script).
Two fixes from original:
  1. Removed dropna(subset=["height_cm"]) — was silently dropping athletes
  2. Dropped height_cm / weight_kg / age / classification — not needed
  3. Outputs JSON instead of CSV

Output shape:
{
  "hometown": "Lake Stevens, WA",
  "state":    "WA",
  "sport":    "Sitting Volleyball",
  "category": "Paralympian"
}

Run:  pip install requests pandas
      python scrape.py
"""

import requests
import json
import time
import re
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────

API       = "https://www.teamusa.com/api/athletes"
HEADERS   = {
    "User-Agent": "TeamUSAParityResearch/0.1 (educational; hackathon project)",
    "Accept":     "application/json",
}
PAGE_SIZE   = 200
OUTPUT_FILE = "raw_athletes.json"

VALID_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC",
}


# ── API fetching (unchanged from original — it works) ────────────────────────

def fetch_page(skip: int) -> dict:
    params = {
        "skip":                    skip,
        "limit":                   PAGE_SIZE,
        "matchAllTags":            "false",
        "filtersStatusSports":     "true",
        "showTopAthletesAtTheTop": "false",
        "query":                   "",
        "sortField":               "last_name.keyword",
    }
    for attempt in range(1, 4):
        try:
            r = requests.get(API, params=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError("Failed after 3 retries")


def get_all_entries() -> list[dict]:
    entries_all = []
    seen  = set()
    skip  = 0
    total = None

    while True:
        page = fetch_page(skip)

        if total is None:
            total = int(page.get("total", 0))
            print(f"Total athletes reported by API: {total}")

        entries = page.get("entries") or []
        if not entries:
            break

        for e in entries:
            uid = e.get("uid")
            if uid and uid not in seen:
                seen.add(uid)
                entries_all.append(e)

        print(f"  skip={skip} | collected: {len(entries_all)}")
        skip += PAGE_SIZE

        if skip >= total:
            break

        time.sleep(0.3)

    print(f"Done — {len(entries_all)} unique athletes fetched")
    return entries_all


# ── Parse state from "City, ST" ───────────────────────────────────────────────

def parse_state(hometown: str) -> str | None:
    if not hometown:
        return None
    parts = hometown.rsplit(",", 1)
    if len(parts) == 2:
        state = parts[1].strip().upper().replace(".", "")
        if state in VALID_STATES:
            return state
    return None


# ── Extract only what we need ─────────────────────────────────────────────────

def extract(entry: dict) -> dict:
    qf   = (entry.get("bio") or {}).get("quick_facts") or {}
    home = qf.get("hometown") or {}

    # Build "City, ST" from the API's city/state fields
    city  = home.get("city", "").strip()
    state = home.get("state", "").strip()
    if city and state:
        hometown = f"{city}, {state}"
    elif city:
        hometown = city
    else:
        hometown = None

    # Sport: take first sport title
    sports   = entry.get("sport") or []
    sport    = sports[0].get("title", "") if sports else None

    # Category: Olympian / Paralympian / Team USA
    category = entry.get("olympic_paralympic", "").strip() or None

    return {
        "hometown": hometown,
        "state":    parse_state(hometown),
        "sport":    sport,
        "category": category,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching all athletes from Team USA API...")
    entries = get_all_entries()

    athletes = []
    errors   = 0

    for i, entry in enumerate(entries):
        try:
            athletes.append(extract(entry))
        except Exception as e:
            print(f"  Error on entry {i}: {e}")
            errors += 1

    # ── Stats ──
    total        = len(athletes)
    with_state   = sum(1 for a in athletes if a["state"])
    no_hometown  = sum(1 for a in athletes if not a["hometown"])
    olympians    = sum(1 for a in athletes if a["category"] == "Olympian")
    paralympians = sum(1 for a in athletes if a["category"] == "Paralympian")

    # ── Save ──
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(athletes, f, indent=2, ensure_ascii=False)

    print(f"\nSaved → {OUTPUT_FILE}")
    print(f"  Total athletes : {total}")
    print(f"  Olympians      : {olympians}")
    print(f"  Paralympians   : {paralympians}")
    print(f"  With state     : {with_state} / {total}")
    print(f"  Missing hometown: {no_hometown}")
    print(f"  Parse errors   : {errors}")

    print("\n── Sample (first 5) ──")
    for a in athletes[:5]:
        print(json.dumps(a, indent=2))


if __name__ == "__main__":
    main()
