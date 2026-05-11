"""
inspect.py  —  Print every distinct value from raw_athletes.json
================================================================
Paste the full output back to Claude.
That's all that's needed to write a perfect 02_clean.py.

Run: python inspect.py
"""

import json
from collections import Counter

INPUT_FILE = "raw_athletes.json"

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

print(f"Total records: {len(data)}\n")

# ── Every distinct value for each field ──────────────────────────────────────

fields = ["sport", "category", "state", "hometown"]

for field in fields:
    values = [a.get(field) for a in data]
    counts = Counter(values)

    print("=" * 50)
    print(f"FIELD: {field}  ({len(counts)} distinct values)")
    print("=" * 50)

    # Sort by count descending
    for val, count in counts.most_common():
        label = repr(val)  # shows None as None, strings with quotes
        print(f"  {count:>5}  {label}")

    print()
