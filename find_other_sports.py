"""
find_other_sports.py
Prints every distinct sport where sport_group == "Other"
Ignores null sports entirely.

Run: python find_other_sports.py
"""

import json
from collections import Counter

with open("cleaned_athletes.json", encoding="utf-8") as f:
    data = json.load(f)

other_sports = Counter(
    a["sport"]
    for a in data
    if a.get("sport_group") == "Other" and a.get("sport")
)

print(f"Distinct sports with group=Other: {len(other_sports)}\n")
for sport, count in sorted(other_sports.items()):
    print(f"  {count:>4}  '{sport}'")
