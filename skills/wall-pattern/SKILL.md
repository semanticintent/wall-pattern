---
name: wall-pattern
description: Build a WALL Pattern process wall (Workflow At-a-glance, Live & Legible) for a real process — interview the process, write wall.config.json, write a feed exporter that produces wall.feed.json from the user's own data, then test it with two snapshots. Use whenever someone wants a wall, board, andon, status screen or "where is work stuck" view of a process; asks to turn a pipeline, queue, review cycle, ticket flow or order flow into a WALL; has a wall.config.json or wall.feed.json to write, fix or extend; or wants a script, job or endpoint that feeds an existing wall. Not for KPI dashboards or charts of trends over time.
---

# WALL Pattern

A wall answers two questions about a running process: **where is work stuck, and what changed since the last look?** Grey is normal; colour means look here. It is two JSON files and one HTML renderer:

- `wall.config.json` — the structure. Changes rarely. Schema: `schema/wall.config.schema.json`.
- `wall.feed.json` — what is true **now**. Rewritten on every update. Schema: `schema/wall.feed.schema.json`.
- `index.html` — renders any config + feed. Demo: https://semanticintent.github.io/wall-pattern/

Read both schemas before writing anything. `examples/` has two complete walls. The rest of this file is the judgment the schemas can't carry.

## 1. Interview the process first

Don't write JSON until you can answer these, in the user's words:

0. **Is a wall the right shape?** Ask how many items are usually in flight at once. A wall shows where *many* items are stuck. If there is usually one (one production, one deployment), every count will be 0 or 1: widen the unit (all productions, all releases this quarter) or suggest a checklist instead.
1. **The steps, in order.** 3–6 is right. More than 6 stops being readable from across a room; merge or drop. Check each step against real data before keeping it: a step the process doesn't really have (no items ever pass through it) is noise.
2. **For each step, one question: "is this step OK?"** The number that answers it is the step's `hero`. Usually a count waiting in the step, an age, or a count past some limit. Not a total-ever, not a percentage nobody acts on.
3. **What "worse" means for each number** → `goodDirection`: `down` for queues, ages, failures; `up` for done-today counters; `neutral` when neither direction is a problem.
4. **When someone should look, and when someone should act** → `thresholds.watch` and `thresholds.act`. Ask for real values. If unsure, set them so that on an ordinary day **everything is grey**. A wall that starts amber teaches people to ignore it.
5. **Handoffs between steps** → `connectors`. Ask what moves along each one (the `caption`: "packed", "approved", "came due") and whether anything comes back (a return loop: `route: "outside"`, plus a `loops` entry).
6. **What counts as an exception** (a named thing someone must deal with, not a number) and its types.
7. **How the process is paced** → `display.delta.window`: `shift` (with `shiftStart`), `day` or `week` (with `weekStart`). A process measured in days or weeks has no 07:00 shift; don't default to `shift` by habit. Also ask how often the feed will update, and set `display.refresh.staleAfterMinutes` to a bit more than that, so a dead exporter shows **Stale**.
8. **Where the data lives and who can read it.** This decides the feed exporter.

**No one to interview?** Answer each question from the sources (repo, docs, data), note where each answer came from and how sure you are, mark thresholds as provisional, and hand the owner a short list of the questions only they can answer. Don't present guessed thresholds as settled.

## 2. Write the config

- Ids match `^[A-Za-z][A-Za-z0-9_-]{0,63}$`. Each kind needs unique ids within itself: steps, connectors, loops, exception types. Indicator ids (heroes included) must be unique across the whole wall, because they are the keys of `feed.values`. A step and an exception type may share an id, but distinct ids read better.
- Per step: `hero`, up to 4 `indicators`, optional `age: { label, targetHours }` for the oldest item. Keep labels short; the wall is read from four metres.
- **Age needs an entry time.** If the source records when an item entered the step, age the oldest item. If it doesn't, age the *condition* instead (how long the render has been stale, from file times) and say so in the label. If neither exists, leave `age` out rather than inventing one. Over a portfolio (many repos, many accounts), one dormant item sets "oldest" forever and paints a permanent orange age line on a Calm step: age only the active items, or leave age out.
- `thresholds` trigger at `>=` by default. For a number where *low* is bad (throughput, coverage), add `"direction": "below"`.
- `cumulative: true` for counters that only grow during the window ("shipped today").
- `stallWhen` turns a connector amber: `{ "step": "<next step id>", "stateAtLeast": "act" }` when the receiving step is in trouble, or `{ "flowBelow": 1 }` when nothing moved. Give it a one-word `stallCaption` ("short", "slow", "backing up").
- Colours, if any, are hex (`#RRGGBB`). Anything else is ignored and the default colour is used.
- Start with `"layout": "row"`. Orbit suits 4–6 steps where exceptions are the story.
- **In Row, connect neighbouring steps only.** A connector between steps that aren't next to each other is drawn as a lane under the blocks, and its caption can end up behind the exceptions panel. Return loops (`route: "outside"`) are the exception.
- **Up to 6 exception types.** More than that wraps the panel off the bottom of a 1920×1080 screen; merge types instead.

## 3. Write the feed exporter

Write it in the user's stack, next to their data (a script, scheduled job or endpoint). Use the project's own parsers and libraries where they exist rather than re-implementing them. It produces one JSON object:

```json
{ "schemaVersion": "1.0", "wallId": "<config id>", "generatedAt": "<ISO time with offset>", "sequence": 42,
  "values": { "<indicator id>": 12 },
  "ages":   { "<step id>": { "oldestHours": 30 } },
  "flows":  { "<connector id>": { "sinceLastUpdate": 3, "sinceShiftStart": 41 } },
  "exceptions": [ { "id": "<stable id>", "type": "<type id>", "step": "<step id>", "text": "UC-083 · 2d overdue" } ] }
```

Rules that are easy to get wrong:

- **Report only what is true now.** No deltas. The wall keeps the previous snapshot and works out what changed. A source that knows only the present is enough.
- **Values are numbers.** Strings, `null` and `NaN` are dropped by the renderer.
- **Exception ids must be stable** across runs (derive them from the thing: `overdue-083`, not a counter). The wall treats a missing id as resolved and a new id as new.
- **Flows need memory, and the first run must not invent them.** A flow claims that something moved. Keep a small state file of the keys already seen (item ids, `id@date` pairs) and count only new keys. On the very first run, record the keys and report `0` everywhere; otherwise the wall announces the whole backlog as "new" on day one.
- **Pick flow keys for what the event really is.** Key on a content hash when a new *result* is the event (a render that is byte-identical to the last one did not move anything). Key on id plus modified time when *redoing* the same item is the event (a re-recorded take).
- **Use the wall's time zone for windows.** The renderer starts a day or week in the local time of the browser showing the wall; compute `sinceShiftStart` and `baseline.at` in that same zone, and write `generatedAt` with its offset.
- **At a window boundary,** reset only the running totals (`sinceShiftStart`, which holds the total for the current shift, day or week). Keep the seen keys, or everything is "new" again the next morning.
- Keep `sequence` in the state file and add one per run.
- **`baseline` is optional.** Send `{ "at": <window start>, "values": {...} }` if the exporter knows the values at the start of the window; otherwise the wall takes its own from the first snapshot it sees in each window.
- `ages` only for steps with an `age` in the config, and only when there is an oldest item.
- Optional `messages: [{ "text", "tone": "better"|"worse"|"neutral" }]` for news numbers can't express ("Shipment received").
- Keep exception text short: a tile shows about 40 characters with three types and about 30 with four or more, so put the part that matters first ("2d overdue · UC-083" when item names are long, "UC-083 · 2d overdue" when they're short). Summary-level only. Anyone who can open the feed can read all of it: no credentials, no personal data (watch for names in approval or audit records), and no private project or repo names unless everyone who can see the wall may know them.

## 4. Test with two snapshots

1. Validate both files against the schemas with whatever validator the project has. At minimum, check that every indicator id has a value in the feed, every connector's `from` and `to` name real steps, every flow key is a connector id, and the feed's `wallId` matches the config's `id`.
2. Open the demo (or `index.html` locally) and drop the config and the feed onto the page together. Nothing leaves the browser.
3. **Run the exporter twice with a real change in between** and drop the second feed. Check that: the changed number pulses with an arrow coloured by meaning (blue better, orange worse); a threshold crossing changes the step's chip and frame; a moved connector shows `+n · total` while quiet ones stay muted; "What changed" lists the number that moved, any new or resolved exception, and one "Moved ·" line for the connectors. Thresholds set for a grey ordinary day often won't be crossed by one realistic change; if so, lower one threshold in a *copy* of the config to see the chip and frame change, then throw the copy away. Pressing **?** on the wall numbers the parts of the first block, which helps when showing the owner how to read it.
4. Look at it on an ordinary day. For every coloured thing, including orange age lines, ask whether it is **true**. If it is, the wall is working: tell the owner what it found. If it isn't, look at the exporter's definitions first (is it counting bookkeeping as work, e.g. a DOI or changelog commit after every release as "unreleased work"?), then at the thresholds. Fix the exporter or the config, not the renderer.

## 5. Serving it

- Simplest: serve `index.html`, the config and the feed from one place and open `index.html?config=<url>&feed=<url>&kiosk=1` on the screen. The page polls the feed every 10 s in Live mode.
- A feed on another origin needs `Access-Control-Allow-Origin`.
- No server: the exporter writes `wall.feed.json` to a folder, and the wall watches the file (**Source & settings → Pick a feed file to watch**, Chrome and Edge).
- Older systems: a scheduled export to a shared folder is enough. No API work.

## Worked example: a case-review cycle

A library of published analyses, each with a date when it must be re-checked. The existing tool was a command that listed overdue reviews and only spoke when someone ran it.

- Steps: **Library** (published) → **Scheduled** (review date beyond 30 days) → **Due** (within 30 days or past) → **Reviewed**, with a return loop Reviewed → Scheduled ("next review set").
- Heroes: cases published (`up`, cumulative); reviews scheduled (`neutral`); due or overdue (`down`, watch 6, act 10) with "Overdue" as an indicator at watch 1; reviewed in the last 90 days (`up`).
- `age` on Due: "Most overdue", target 24 h. Exceptions: one per overdue review, id `overdue-<case>`, plus one per disagreeing copy of the review record.
- Window `day`: reviews move by the day, not by the shift.
- Flows from a state file of seen keys: `<case>` for published, `<case>@<due date>` for "came due" and "next review set", `<case>@<reviewed date>` for reviewed. The first run only seeded it.
- The exporter called the same function the existing command used, so the wall never disagrees with it. Prefer reusing the source of truth over a second copy of its rules, but check that what it returns is stable across versions of the tool. A hash or revision id that changes when the tool is upgraded, with the data untouched, becomes a permanent false alarm.

On the first run three steps were grey and Due was amber, holding one review two days overdue: the command's first line, visible from across a room.
