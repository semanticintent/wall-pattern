# Adapters — design note

**Status: proposed, not implemented.** Nothing in this note exists in the renderer yet. It records a direction so that it can be built, or rejected, on purpose.

## The question

Today a wall's numbers are shaped at the source. A script, scheduled job or endpoint next to the data writes `wall.feed.json`, and the renderer only reads that one schema. Many processes already have an API, though: a ticket tracker, a repository host, a status endpoint. Could a wall read those endpoints directly and map their data in the page, without anything new to host?

## What server-side shaping gives today

- **One contract.** The renderer knows the feed schema and nothing else. That boundary is also the security boundary: config and feed values are checked before anything reaches the page.
- **No secrets in the browser.** Exporters read private files and call APIs with tokens that never leave the server.
- **Works with old systems.** A scheduled export into a shared folder needs no API at all.

## What mapping in the browser would add, and its limits

It would add pointing a wall at an existing endpoint with nothing written or hosted. The limits are hard ones:

1. **Authentication.** Anything the browser uses to sign a request is readable by anyone who opens the page. Browser mapping only fits public endpoints, or endpoints on the wall's own origin.
2. **CORS.** Most APIs don't allow other websites to read them from a browser. Some do (GitHub's public REST API, for example), usually with low unauthenticated rate limits.
3. **Code safety.** A mapping written as JavaScript and loaded from a URL would run someone else's code on the wall. Mappings referenced by a config must stay declarative, and real code should load only from the wall's own origin.
4. **Memory for flows.** A flow ("+3 moved") needs to know what was already seen. In a browser that memory lives in local storage: fine for one wall screen, lost on another device or a cleared browser.

## The proposal: one adapter, two hosts

An adapter is a small ES module with one job: turn endpoint responses into a feed.

```js
// adapters/github-repo.js — illustrative
export default {
  // Endpoints to fetch on each refresh. {params} come from the wall URL or config.
  sources: {
    pulls: "https://api.github.com/repos/{repo}/pulls?state=all&per_page=100",
  },
  // Responses (+ memory of seen keys) in, a wall.feed.json object out.
  map({ pulls }, memory, params) {
    return {
      values: { /* indicator id → number */ },
      flows: { /* connector id → { sinceLastUpdate, sinceShiftStart } */ },
      exceptions: [ /* { id, type, step, text } */ ],
    };
  },
};
```

The same file runs in either place:

| Host | When | Memory | Secrets |
|---|---|---|---|
| **Browser** | Public, CORS-enabled endpoints | local storage, per screen | none allowed |
| **Edge** (a small Worker template) | Anything that needs a token | KV, shared by every screen | stay server-side; the Worker publishes an ordinary feed URL |

Rules that keep the renderer's boundary intact:

- The renderer loads adapter modules **only from its own origin** (`?adapter=adapters/github-repo.js`), never from an arbitrary URL.
- An adapter's output is validated exactly like a fetched feed. The renderer still knows only the feed schema.
- The first run records what it sees and reports `0` for every flow, as the skill already requires of exporters.

A declarative mapping (paths, counts, filters, no code) could be added later for people who don't write JavaScript, and is the only kind a config could safely reference from elsewhere.

## A first proof, if this is built

A wall for **any public GitHub repository** (opened → in review → merged → released), running entirely in the browser on the demo site: `?adapter=github-repo&repo=owner/name`. GitHub's unauthenticated limit is 60 requests an hour, so it would refresh every few minutes rather than every 10 seconds.

## Spreadsheets, without writing code

Adapters still assume someone writes JavaScript. Many people who would want a wall write none, but already keep a spreadsheet: a team lead updating counts at standup, a supervisor exporting a report at the end of a shift.

The smallest bridge to them is a **two-column CSV** that the renderer accepts next to JSON:

```csv
id,value
picked,42
packed,17
oldest-order-hours,6
```

- The person keeps a "wall" tab in Excel or a shared sheet, with one row per indicator id from the config, and saves it as CSV into the folder the wall watches.
- Deltas still work. Each save is a snapshot, and the wall already compares snapshots.
- Validation is unchanged: ids must exist in the config and values must be numbers, or the row is ignored and reported.

Two further steps would follow only if people actually show up:

- **Typing numbers into the page.** An edit panel over the existing indicators, with snapshots kept in the browser or downloaded. It turns the wall into a whiteboard that remembers.
- **A config builder.** Naming steps and indicators in a form instead of JSON.

**The honest limit:** cells hold totals, so a spreadsheet wall shows counts, ages and deltas but no **flows**. Flows need memory of individual items, which means exporting one row per item (id, step, entered-at) and a converter with a state file, as described above.

## An agent that does the setup

Today the gap between "I have data" and "I have a wall" is closed by a person working with an AI assistant: it reads the skill, looks at the data, drafts the config and writes the exporter. That works, but it needs someone who already works that way. A dedicated agent could offer the same help to someone who doesn't.

**What it would do:**

1. **Look at the data.** The person points it at a spreadsheet, an export or a folder.
2. **Propose a wall.** It suggests steps, indicators and exceptions in plain language ("orders move Picked → Packed → Shipped; anything in Packed for over 4 hours is an exception") and shows a preview rendered from the person's real numbers.
3. **Write the exporter.** A small script that turns the export into `wall.feed.json`, keeps the state file for flows, and seeds with `0` on its first run.
4. **Schedule and hand over.** It sets the exporter to run after each export, then gives the person the wall URL or the file to watch.
5. **Repair it.** When an export's columns change and the feed stops updating, the person asks the agent again and it fixes the mapping.

**The rule that matters most: the agent builds the exporter; it does not run inside it.** The refresh that runs every hour or every shift stays a plain, deterministic script. A model in that loop would cost money on every refresh, could give different numbers for the same input, and would put numbers on the wall that nobody can trace back to a source. The agent is there for the work a person would otherwise need help with (designing, writing, fixing), not for the routine.

**Ways it could be built:**

| Option | What it is | Fits when |
|---|---|---|
| **The existing skill** in Claude Code or the Claude apps | No new software; the person runs the skill in a conversation | They already have Claude, but not a coding habit |
| **Claude Agent SDK** | The Claude Code harness as a library, with built-in file, shell and web tools; you host it | A small local "wall setup" app or CLI that works on files on the person's machine or share |
| **Claude Managed Agents** | Anthropic hosts the agent loop and a per-session workspace; agents can run on a schedule, with credentials kept in a vault | A hosted service for many people, or an agent that checks walls on a schedule |

The Agent SDK is the closest match to the spreadsheet-on-a-shared-drive case, because the data and the exporter stay on the person's machine.

**What it could add beyond setup:**

- **Explaining a wall.** "Why is Packed amber?" answered from the config and the last few snapshots. This would extend the `?` overlay, which explains the encoding, to explain the current state.
- **A shift summary.** A short note at the end of a shift about what moved, what stalled and what cleared. This must respect the pattern: grey is normal, so a quiet shift gets a one-line summary, not a report.

## Open questions

- Should the browser host exist at all, or should adapters run only at the edge, keeping the browser a pure renderer?
- Where does a declarative mapping end and an adapter begin?
- How does a wall screen show that its numbers come from an adapter, not a feed it can audit?
- Is the two-column CSV worth adding to the renderer before anyone asks for it?
- Should a setup agent be a separate tool, or is the skill plus a short "getting started with Claude" page enough?
- If an agent writes summaries or explanations, how does the wall keep them visibly separate from the numbers it can audit?
