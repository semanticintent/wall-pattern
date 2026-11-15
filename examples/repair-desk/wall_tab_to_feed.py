#!/usr/bin/env python3
"""Turn a spreadsheet "wall" tab (saved as CSV) into wall.feed.json.

Python 3.8+, standard library only. Usage:
    python3 wall_tab_to_feed.py wall.config.json wall.csv wall.feed.json [exceptions.csv]

wall.csv has two columns, id,value:
  - an indicator id from the config, with its current number
  - or age:<step id>, with the oldest item's age in hours
exceptions.csv (optional) has columns id,type,step,text: one row per open exception.

Cells hold totals, so this feed has no flows. Every run is a snapshot; the wall
works out what changed. A state file next to the feed keeps the sequence number.
"""
import csv, json, os, sys
from datetime import datetime


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:  # utf-8-sig: Excel adds a BOM
        return list(csv.DictReader(f))


def main(config_path, csv_path, feed_path, exceptions_path=None):
    config = json.load(open(config_path, encoding="utf-8"))
    steps = {s["id"]: s for s in config["steps"]}
    indicators = set()
    for s in config["steps"]:
        indicators.add(s["hero"]["id"])
        indicators.update(i["id"] for i in s.get("indicators", []))
    types = {t["id"] for t in config.get("exceptions", {}).get("types", [])}

    values, ages, problems, bad = {}, {}, [], set()
    for row in read_rows(csv_path):
        key, raw = (row.get("id") or "").strip(), (row.get("value") or "").strip()
        if not key:
            continue
        try:
            number = float(raw.replace(",", ""))
        except ValueError:
            problems.append(f"{key}: '{raw}' is not a number")
            bad.add(key)
            continue
        number = int(number) if number.is_integer() else number
        if key.startswith("age:"):
            step = key[4:]
            if step in steps and "age" in steps[step] and number >= 0:
                ages[step] = {"oldestHours": number}
            else:
                problems.append(f"{key}: no step with an age called '{step}'")
        elif key in indicators:
            values[key] = number
        else:
            problems.append(f"{key}: not an indicator id in the config")
    for missing in sorted(indicators - values.keys() - bad):
        problems.append(f"{missing}: no row in {os.path.basename(csv_path)}")

    exceptions = []
    if exceptions_path and os.path.exists(exceptions_path):
        for row in read_rows(exceptions_path):
            e = {k: (row.get(k) or "").strip() for k in ("id", "type", "step", "text")}
            if all(e.values()) and e["type"] in types and e["step"] in steps:
                exceptions.append(e)
            elif any(e.values()):
                problems.append(f"exception '{e['id']}': needs id, a known type, a known step and text")

    if not values:
        sys.exit("No usable values; feed not written.\n" + "\n".join(problems))

    state_path = feed_path + ".state.json"
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"sequence": 0}
    state["sequence"] += 1

    feed = {
        "schemaVersion": "1.0",
        "wallId": config["id"],
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sequence": state["sequence"],
        "values": values,
    }
    if ages:
        feed["ages"] = ages
    if exceptions_path:
        feed["exceptions"] = exceptions  # an empty list means everything was resolved

    tmp = feed_path + ".tmp"  # write then rename, so the wall never reads half a file
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    os.replace(tmp, feed_path)
    json.dump(state, open(state_path, "w"))

    print(f"Wrote {feed_path} (sequence {state['sequence']}, {len(values)} values, {len(exceptions)} exceptions)")
    for p in problems:
        print("  check:", p)


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        sys.exit(__doc__)
    main(*sys.argv[1:])
