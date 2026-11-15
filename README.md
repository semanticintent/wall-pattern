# WALL Pattern

*Workflow At-a-glance, Live & Legible*

**A process wall you can read from across the room.**
One HTML file, one config, one feed. Any process becomes a live wall of connected steps: what is calm, what needs eyes, and what changed since you last looked.

`PATTERN · FORMAT · RENDERER` · MIT · 2026 · [Semantic Intent](https://semanticintent.dev)

---

## Why

Most dashboards answer *"how are we doing?"* with KPI tiles and charts. People who run a process ask something else: *"where is work stuck, and what changed?"*

WALL Pattern answers that second question, as an open pattern:

- **Show the flow, not just the numbers.** Steps are joined by connectors that carry counts.
- **Grey is normal.** Colour appears only when a step needs attention.
- **Show change, not just state.** Every update pulses what moved and shows ↑↓ deltas, coloured by meaning.
- **Arranged once, then fixed.** You can arrange the layout like a diagram, then pin it so the wall stays stable.

## Quick start

**Live demo:** [semanticintent.github.io/wall-pattern](https://semanticintent.github.io/wall-pattern/) · [as a wall screen](https://semanticintent.github.io/wall-pattern/?kiosk=1) (press **K** for controls)

Or locally:

```
open index.html
```

That's it. The wall opens on the **Fernhill Provisions** example, a fictional food wholesaler, with simulated data:
Orders → Inventory → Fulfilment → Shipping → Invoicing, with backordered lines looping back to Orders.

To use your own process, open **Source & settings**, or drop a `wall.config.json` or `wall.feed.json` anywhere on the page.

## The two files

WALL Pattern separates **structure** from **numbers**.

| File | Changes | Describes |
|---|---|---|
| `wall.config.json` | rarely | steps, indicators, thresholds, connectors, loops, exceptions, display |
| `wall.feed.json` | every update | current values, flows, ages of oldest items, open exceptions |

The feed carries **no deltas**. The wall computes them by comparing each snapshot with the previous one, or with the shift baseline. A source system only has to report what is true *now*.

Schemas: [`schema/wall.config.schema.json`](schema/wall.config.schema.json) · [`schema/wall.feed.schema.json`](schema/wall.feed.schema.json) (JSON Schema 2020-12)

### Minimal config

```json
{
  "schemaVersion": "1.0",
  "id": "orders",
  "title": "Order Fulfilment",
  "steps": [
    { "id": "picked", "name": "Picked", "hero": { "id": "picked_n", "label": "Waiting to pack" } },
    { "id": "packed", "name": "Packed", "hero": { "id": "packed_n", "label": "Waiting to ship",
      "goodDirection": "down", "thresholds": { "watch": 40, "act": 80 } } }
  ],
  "connectors": [ { "id": "c1", "from": "picked", "to": "packed", "caption": "packed" } ]
}
```

### Minimal feed

```json
{
  "schemaVersion": "1.0",
  "wallId": "orders",
  "generatedAt": "2026-11-14T13:53:56-05:00",
  "values": { "picked_n": 112, "packed_n": 46 },
  "flows": { "c1": { "sinceLastUpdate": 3, "sinceShiftStart": 58 } }
}
```

## Anatomy of a block

Each step is the same reusable unit:

1. **Step & name**, numbered, so the order reads at a glance.
2. **State chip**: Calm, Watch or Act. Colour and a glowing frame appear only above Calm.
3. **Hero number**: the one figure that answers "is this step OK?"
4. **Delta badge**: ↑/↓ coloured by *meaning* (`goodDirection`), not by direction. Blue is better, orange is worse. It pulses once, then fades.
5. **Indicator rows**: supporting counts, each with its own threshold dot.
6. **Age vs target**: how long the oldest item has waited.
7. **Exception badge**: exceptions show where they happen, not only in their own panel.

## Rules for the wall

- Readable from four metres: big numbers, few words.
- Grey is normal; colour means "look here".
- Draw the flow: connectors carry counts and turn amber when a handoff stalls (`stallWhen`).
- Show it's alive: a heartbeat and an "updated" time. A missing feed shows **Stale** (`staleAfterMinutes`).
- Fix the Δ baseline: since the last update, or since shift start.
- Gentle motion: one pulse per change, and reduced-motion settings are respected.

## Layouts

| Layout | What it is |
|---|---|
| **Row** | Steps in a line. Return loops sweep underneath. Exceptions and "What changed" panels sit below. |
| **Orbit** | Steps on a ring with **Exceptions as the hub**. Spokes show exceptions per step (thicker means more), and dots flow along curved connectors, faster with more volume. Drag to arrange, then **Pin**. The layout is saved per wall in the browser. |

## Wall-screen links

```
index.html?config=CONFIG_URL&feed=FEED_URL&layout=orbit&pin=1&kiosk=1
```

| Param | Effect |
|---|---|
| `config` | load a config from a URL (falls back to the built-in example) |
| `feed` | poll a feed URL: every 10 s in Live mode, or on the chosen interval |
| `layout` | `row` or `orbit` |
| `pin=1` | lock block positions |
| `kiosk=1` | hide the controls (press **K** to toggle) |

Keys: **K** shows or hides the controls · **F** toggles full screen · **Esc** closes settings.

## Feeding it from a business system

The renderer only reads JSON, so the integration can be as light as a scheduled export.

| Setup | How | Notes |
|---|---|---|
| **Same server** | Serve `index.html` next to `wall-feed.json` | Simplest for a wall screen. No cross-site issues. |
| **Shared folder** | The system writes `wall-feed.json` on a schedule; a static web server shares the folder | No API work at all. Good fit for older systems. |
| **Feed API** | Point `?feed=` at an endpoint returning the feed JSON | If the HTML is hosted elsewhere, or opened from a local drive, the endpoint must send a CORS header (`Access-Control-Allow-Origin`). |
| **Watch a local file** | **Source & settings → Pick a feed file to watch**. The business system overwrites `wall-feed.json` on a schedule (for example in a shared folder) | No server, no CORS. The wall re-reads the file on every refresh (Live = every 5 s) and only updates when it changed. Nothing is uploaded. Remembered across reloads: click **Resume watching**. Chrome and Edge only (File System Access API). |
| **Files by hand** | Drop snapshots onto the page | Any browser. Drop two in a row to see what changed. |

**Data and security**
- Expose summary numbers and short exception texts only. Anyone who can open the feed can read all of it.
- Never put credentials or API keys in the HTML. Protect the feed on the server side, for example by making it reachable only on the internal network.
- The page sends nothing anywhere. It only fetches the feed and config you point it at. Fonts load from Google Fonts and fall back to system fonts when offline.

## Repository layout

```
index.html                       the renderer: self-contained, no build step
schema/
  wall.config.schema.json        structure of a wall
  wall.feed.schema.json          one live snapshot
examples/
  fernhill-provisions/           order to cash: five steps, backorder loop, exceptions hub
  hiring-pipeline/               four steps, light theme, return loop
README.md
LICENSE
```

## Status

v0.1 is a working renderer and a schema-validated contract. Honest gaps:

| Item | State |
|---|---|
| Row and Orbit layouts, deltas, stall rules, exceptions, change log, kiosk, URL params | working |
| `display.layout: "free"` | rendered as Orbit, using each step's `position` |
| `exceptions.placement: "satellites"` | in the schema; renders as hub (Orbit) or panel (Row) |
| `step.drillUrl` | in the schema; not wired to clicks yet |
| Custom `states` beyond three | labels and colours work; thresholds only define `watch` and `act` |
| Watch a local feed file (re-read on each refresh, no server) | working in Chrome and Edge; other browsers fall back to drop-in files |
| Schema validation in the page | basic checks, plus id and colour patterns enforced before anything reaches the page; the schemas are the source of truth |

All company, customer, product and carrier names in the examples are fictional.

## Origin

WALL Pattern comes from years of building tiered business systems on .NET, where the same shape kept coming back: structured input goes in, structured output comes out, admin screens are rendered from a declared structure rather than built by hand one at a time, and a cache layer holds the last known state in between.

The wall is that shape pointed at a screen on the wall:

| Tiered system | WALL Pattern |
|---|---|
| Declared structure the admin UI renders from | `wall.config.json` |
| Structured output from the business tier | `wall.feed.json` |
| Cache layer holding the last known state | the renderer's previous snapshot and shift baseline, which is where the deltas come from |
| Rendered UI | `index.html` |

Rebuilt in 2026 as an open pattern, format and renderer, with Claude.

## Licence

MIT © 2026 [Michael Shatny](https://semanticintent.dev) · [Semantic Intent](https://github.com/semanticintent)
