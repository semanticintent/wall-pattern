# WALL Pattern: a guide for AI assistants

**For the person:** give this file to the chat assistant you already use (Microsoft Copilot, ChatGPT, Claude, Gemini or another). Paste it into the chat or attach it, then describe your process or share a sample of your data. If the assistant accepts more files, attach `schema/wall.config.schema.json` and `schema/wall.feed.schema.json` too. In an organisation, this file can be added as a knowledge file to a custom assistant (for example one built in Copilot Studio), so that nobody has to paste it.

**For the assistant:** everything below is addressed to you.

---

## What you are helping with

A WALL ("Workflow At-a-glance, Live & Legible") is a screen that answers two questions about a running process: **where is work stuck, and what changed since the last look?** Grey is normal; colour means look here.

It is made of three things:

| File | What it is | Who writes it |
|---|---|---|
| `wall.config.json` | The structure: steps, numbers, thresholds, handoffs. Changes rarely. | You, with the person |
| `wall.feed.json` | What is true **now**. Rewritten on every update. | A small converter or script, which you write |
| The renderer | A web page that draws any config and feed. | Already exists: https://semanticintent.github.io/wall-pattern/ |

Your job is to produce the first two, matching the format exactly, and to help the person get the feed updating.

**What you can't do, and how to work around it:**

- **You can't see the wall.** Ask the person to open the renderer, drop both files onto the page, and tell you what they see or paste any message it shows. The page checks both files and reports problems; use those messages to fix the files.
- **You can't run anything.** Give the person complete files and exact steps for running and scheduling them, in the tools they actually have.
- **Don't invent fields.** The renderer ignores or rejects anything not in the format below. If the person asks for something the format can't express, say so.

## Step 1: Understand the process (before writing any JSON)

Ask these, and use the person's own words:

1. **How many items are usually in flight at once?** A wall shows where *many* items are stuck. If there is usually one, every count is 0 or 1: suggest a wider unit (all orders, not one order) or a checklist instead.
2. **What are the steps, in order?** 3 to 6. More than 6 can't be read from across a room; merge some.
3. **For each step: "how do you know this step is OK?"** The number that answers is the step's main number (its `hero`). Usually a count waiting, an age, or a count past a limit. Not a total-ever.
4. **Which way is worse for each number?** Up is worse for queues and ages, down is worse for "done today" counts, and some numbers are neither.
5. **When should someone look, and when should someone act?** Ask for real values. If unsure, choose values so that **on an ordinary day everything is grey.** A wall that starts amber teaches people to ignore it.
6. **What moves between steps?** One word per handoff ("started", "approved", "shipped"). Does anything come back to an earlier step?
7. **What counts as an exception?** A named thing someone must deal with (an order stuck for a missing part), not a number. Up to 6 types.
8. **How is the process paced?** By shift (what time does it start?), by day, or by week. How often will the data be updated?
9. **Where does the data live, and in what form?** A spreadsheet, a regular export, a database, an API. This decides Step 4.

If the person doesn't know an answer, propose one, mark it as provisional, and move on.

## Step 2: Write `wall.config.json`

Required at the top level: `schemaVersion` (always `"1.0"`), `id`, `title`, `steps`, `connectors`.

**Ids** (for the wall, steps, indicators, connectors, exception types) start with a letter and use only letters, digits, `-` and `_`, up to 64 characters. Indicator ids must be unique across the whole wall, because they are the keys in the feed.

**Each step:**

| Field | Meaning |
|---|---|
| `id`, `name` | Required. Keep names short. |
| `hero` | Required. The step's main number, an indicator (below). |
| `indicators` | Up to 4 more numbers. |
| `age` | `{ "label": "Oldest", "targetHours": 48 }` shows the age of the oldest item. Only include it if the data records when items entered the step. |
| `subtitle` | Optional small line under the name. |

**Each indicator** (`hero` or in `indicators`):

| Field | Meaning |
|---|---|
| `id`, `label` | Required. |
| `goodDirection` | `"up"`, `"down"` or `"neutral"`: which way is better. Decides the colour of changes (blue better, orange worse). |
| `thresholds` | `{ "watch": 5, "act": 10 }`. Triggers when the value reaches or passes the number. Add `"direction": "below"` when *low* is bad. |
| `cumulative` | `true` for counters that only grow during the day or shift ("shipped today"). |
| `format`, `unit` | Optional: `"integer"` (default), `"decimal"`, `"percent"`, `"currency"`, `"duration"`; unit such as `"h"` or `"CAD"`. |
| `caption` | Optional small line under a hero, such as "of 1,302". |

**Each connector** (a handoff between steps): `id`, `from` (step id), `to` (step id), `caption` (the one word). Optional:

- `"stallWhen": { "step": "<receiving step id>", "stateAtLeast": "act" }` turns the handoff amber when the receiving step is in trouble, with `"stallCaption": "backing up"`.
- `"route": "outside"` for a return to an earlier step.
- `"showFlow": false` when the data can't say how many items moved (see Step 4).

Connect neighbouring steps only, except for returns.

**Exceptions:** `"exceptions": { "types": [ { "id": "parts", "label": "Parts overdue" } ], "thresholds": { "watch": 3, "act": 6 } }`. The thresholds apply to the total number open.

**Display** (optional): `"display": { "layout": "row", "refresh": { "staleAfterMinutes": 90 }, "delta": { "window": "day" } }`.

- `window` is `"shift"` (with `"shiftStart": "07:00"`), `"day"` or `"week"` (with `"weekStart": "monday"`).
- Set `staleAfterMinutes` a little above how often the data updates, so a broken update shows as **Stale**.
- Start with `"layout": "row"`.

## Step 3: The shape of `wall.feed.json`

```json
{
  "schemaVersion": "1.0",
  "wallId": "<the config's id>",
  "generatedAt": "2026-11-15T17:19:01-05:00",
  "sequence": 42,
  "values": { "<indicator id>": 12 },
  "ages": { "<step id>": { "oldestHours": 30 } },
  "flows": { "<connector id>": { "sinceLastUpdate": 3, "sinceShiftStart": 41 } },
  "exceptions": [ { "id": "<stable id>", "type": "<type id>", "step": "<step id>", "text": "R-1042 · screen 5d late" } ]
}
```

Rules that are easy to get wrong:

- **Report only what is true now. Never compute changes.** The wall keeps the previous snapshot and works out what changed by itself.
- **Every indicator in the config needs a value, and values are numbers.** Text and empty cells are dropped.
- **`generatedAt` includes the time-zone offset.** `sequence` goes up by one on every run.
- **Exception ids must be stable** from one run to the next. Derive them from the thing (`parts-R1042`), never from a row number. The wall treats a missing id as resolved and a new id as new.
- **Flows are optional and need memory.** A flow claims that items moved along a handoff. Totals can't tell you that: a count going from 10 to 12 could be 2 arrivals, or 5 arrivals and 3 departures. Only produce flows when the data has one row per item. Then keep a small state file of item ids already seen, count only new ones, and report `0` everywhere on the very first run. Otherwise leave `flows` out and set `"showFlow": false` on the connectors.
- **`ages` only** for steps that have an `age` in the config.
- **Keep exception text short** (about 30 to 40 characters), with the important part first. Anyone who can open the feed can read it: no personal data, no credentials.

## Step 4: Getting the data in

Pick the path that matches Step 1, question 9.

### A. The person keeps a spreadsheet (no flows)

This is the simplest path and needs no programming knowledge.

1. **Add a tab called `wall`** with two columns, `id` and `value`:
   - one row per indicator id, with formulas pulling the current numbers from the rest of the workbook (`COUNTIFS`, `MAX`, and so on);
   - optionally, a row `age:<step id>` with the oldest item's age in hours.

   Write the formulas for the person against their real column names.
2. **Optionally add an `exceptions` tab** with columns `id,type,step,text`, one row per open exception (for example with a `FILTER` formula).
3. **Save or export those tabs as CSV** after each update, into one folder.
4. **Run the converter** below to turn the CSVs into `wall.feed.json`. Python 3, standard library only. If the person can't run Python, translate it faithfully into what they have, such as PowerShell or a Power Automate flow, keeping every check.
5. **Schedule it** right after the export: Task Scheduler, cron, or a Power Automate step.

```python
#!/usr/bin/env python3
"""Turn a spreadsheet "wall" tab (saved as CSV) into wall.feed.json.

Python 3.8+, standard library only. Usage:
    python3 wall_tab_to_feed.py wall.config.json wall.csv wall.feed.json [exceptions.csv]
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
```

### B. The data is an export with one row per item

For example: item id, current step, time it entered the step. Write a converter that counts items per step, takes the oldest age per step, and builds exceptions from rows that meet a rule. Only on this path can you produce **flows**: keep a state file of item ids seen in each step, count new arrivals, and report `0` on the first run.

### C. The data is in a database or behind an API

Write the same kind of converter as a scheduled script in the person's language, reading through the libraries they already use. Keep credentials in the script's environment. Never put them in the feed or the config.

## Step 5: Show it, and test it with two snapshots

1. **Open the renderer.** Either the demo page above, or the person's own copy of `index.html` if their organisation doesn't allow outside sites. Drop `wall.config.json` and `wall.feed.json` onto the page together. Nothing is uploaded; it all stays in the browser. Ask the person what they see.
2. **Make a second snapshot.** Change a number in the spreadsheet, run the converter again, and drop the new feed. The changed number should pulse with an arrow (blue better, orange worse). A crossed threshold changes the step's colour, and **What changed** lists the change.
3. **Look at an ordinary day.** For every coloured thing, ask the person: is that really a problem? If not, fix the thresholds or the converter, not the wall.

## Step 6: Keep it updating

- **No server (most spreadsheet setups):** the converter writes `wall.feed.json` into a folder. On the wall screen, in Chrome or Edge, use **Source & settings → Pick a feed file to watch** and choose that file. The page re-reads it and updates when it changes. After a browser restart, one click resumes watching.
- **Synced folders** (OneDrive, Google Drive, a mapped network drive) work, if the file is a real local file. Set "always keep on this device" for that folder, or the browser may read a placeholder.
- **Served from a web server:** open `index.html#config=<url>&feed=<url>&kiosk=1`. The page checks the feed every 10 seconds. Use `#` rather than `?`, so a key in the feed URL never reaches the server that hosts the page.
- **How fresh the wall is depends on the export.** If the spreadsheet is saved hourly, the wall changes hourly.

## Worked example: a repair desk fed from a spreadsheet

Three steps, a day window, two exception types, no flows. The full files are in `examples/repair-desk/` in the repository.

`wall.config.json`:

```json
{
  "schemaVersion": "1.0",
  "id": "repair-desk",
  "title": "Repair Desk",
  "eyebrow": "WALL PATTERN · FED FROM A SPREADSHEET",
  "display": {
    "layout": "row",
    "refresh": { "mode": "live", "staleAfterMinutes": 90 },
    "delta": { "window": "day" }
  },
  "steps": [
    {
      "id": "received",
      "name": "Received",
      "hero": { "id": "waiting", "label": "Waiting to start", "goodDirection": "down",
                "thresholds": { "watch": 15, "act": 25 } },
      "indicators": [
        { "id": "received-today", "label": "Received today", "goodDirection": "neutral", "cumulative": true }
      ]
    },
    {
      "id": "repair",
      "name": "In repair",
      "hero": { "id": "in-repair", "label": "On the bench", "goodDirection": "neutral" },
      "indicators": [
        { "id": "waiting-parts", "label": "Waiting for parts", "goodDirection": "down",
          "thresholds": { "watch": 3, "act": 6 } }
      ],
      "age": { "label": "Oldest on bench", "targetHours": 48 }
    },
    {
      "id": "ready",
      "name": "Ready for pickup",
      "hero": { "id": "ready-count", "label": "Ready", "goodDirection": "neutral" },
      "indicators": [
        { "id": "picked-up-today", "label": "Picked up today", "goodDirection": "up", "cumulative": true },
        { "id": "uncollected", "label": "Uncollected 7d+", "goodDirection": "down",
          "thresholds": { "watch": 2, "act": 5 } }
      ]
    }
  ],
  "connectors": [
    { "id": "received-repair", "from": "received", "to": "repair", "caption": "started", "showFlow": false,
      "stallWhen": { "step": "repair", "stateAtLeast": "act" }, "stallCaption": "backing up" },
    { "id": "repair-ready", "from": "repair", "to": "ready", "caption": "fixed", "showFlow": false }
  ],
  "exceptions": {
    "types": [
      { "id": "parts", "label": "Parts overdue" },
      { "id": "customer", "label": "Customer unreachable" }
    ],
    "thresholds": { "watch": 3, "act": 6 }
  }
}
```

The `wall` tab, saved as `wall.csv`:

```csv
id,value
waiting,9
received-today,14
in-repair,11
waiting-parts,2
age:repair,30
ready-count,6
picked-up-today,8
uncollected,1
```

The `exceptions` tab, saved as `exceptions.csv`:

```csv
id,type,step,text
parts-R1042,parts,repair,R-1042 · screen 5d late
cust-R0988,customer,ready,R-0988 · 3 calls no answer
```

Running `python3 wall_tab_to_feed.py wall.config.json wall.csv wall.feed.json exceptions.csv` writes a feed with seven values, the bench age and both exceptions. With these numbers every step is grey.

Then suppose that, later in the day, "Waiting for parts" reaches 6 and the customer for R-0988 calls back. The next run turns **In repair** to Act and marks the "started" handoff "backing up". **What changed** then shows the parts count rising and R-0988 resolved.

## Before you hand over

- [ ] Every indicator id in the config has a row in the `wall` tab (the converter lists any that are missing).
- [ ] The feed's `wallId` equals the config's `id`.
- [ ] Every connector's `from` and `to` are real step ids.
- [ ] Thresholds keep an ordinary day grey, and any you guessed are marked as provisional.
- [ ] No flows unless the data has one row per item and a state file.
- [ ] No personal data or credentials in exception text.
- [ ] The person knows how to schedule the converter and how to point the wall at the feed.
