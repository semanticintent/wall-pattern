# Changelog

## Unreleased

- **Light theme is easier to read.** State chips darken their colour for text in the light theme instead of lightening it, so an amber Watch chip's text measures 5.1:1 against white instead of 1.4:1. The accent's eyebrow text is darkened the same way in light: a teal accent goes from about 2:1 to 5.1:1 (the band keeps the exact colour).
- **`#theme=dark|light`** in a wall link overrides the config's theme, to check a wall in the other look without editing it.

## 0.2.5 — 2026-11-16

Telling walls apart. The only schema change is one optional field, `display.accent`.

- **Per-wall accent:** `display.accent` (hex) colours the eyebrow, a thin band along the top edge and the refresh line, so several walls can be told apart across a room. It never changes the meaning colours. An invalid value is ignored; an accent that looks like a warning colour logs a note in the browser console.
- **Design note:** `docs/themes.md` (themes change the frame, never the meaning; built-in themes, theme files, a viewer-level colour-blind mode, wall rotation).

## 0.2.4 — 2026-11-16

Safer links. The schemas are unchanged.

- **Parameters in the fragment.** `index.html#config=…&feed=…&kiosk=1` is now the documented form. The part after `#` never reaches the server that hosts the page, so a key in a feed URL stays out of its logs. Older `?…` links still work and are moved into the fragment in the address bar. Editing the fragment reloads the wall.
- **Keys never appear on screen.** Error messages and the status label show a feed URL without its query or fragment.
- **`Referrer-Policy: no-referrer`** via a meta tag.
- **Design note:** `docs/sharing-and-offline.md` (reaching a feed, capability URLs, CORS, offline walls).

## 0.2.3 — 2026-11-15

For people who don't write code, or who use a chat assistant other than Claude. The renderer and schemas are unchanged.

- **A guide for any chat assistant:** `docs/for-assistants.md`. One self-contained file for Microsoft Copilot, ChatGPT, Gemini or Claude: paste it in or attach it, and the assistant can interview the process, write the config, write spreadsheet formulas and a converter, and help schedule the update. It can also be a knowledge file for an organisation's custom assistant.
- **A wall fed from a spreadsheet:** `examples/repair-desk/`. A `wall` tab saved as CSV (`id,value`, plus `age:<step>` rows and an optional exceptions tab) is turned into a feed by `wall_tab_to_feed.py`, standard-library Python, which reports anything that doesn't match the config. Cells hold totals, so this path has no flows.
- **Design notes, proposed and not implemented:** `docs/adapters.md` covers adapters that map an existing endpoint to a feed (in the browser or at the edge), a two-column CSV read directly by the renderer, and a setup agent that builds the exporter but never runs inside it.

## 0.2.2 — 2026-11-15

- **`?` explains the wall.** Press **?** (or **How to read** in the header) and the wall puts numbered markers on its own first block, with a short guide to the seven parts, connectors, the Δ window, "What changed" and Stale. Esc closes it. Hidden in kiosk mode until the key is pressed.
- **Anatomy page:** `anatomy.html`, also on the demo site, and its image in the README. The example is a code-review step; the "same pattern" rows are software delivery, order fulfilment, hiring and case reviews.
- **"What changed" keeps what matters when an update is busy.** Exceptions first, then hero changes, then other numbers, then connector movement and messages; the log is trimmed from the bottom. Before, a busy update could trim away the hero change and the resolved exception.
- **Skill**, from a second test on a portfolio of repositories: check steps against real data, ages over a portfolio, Row connects neighbours only, the wall's time zone for windows, shorter exception text with four or more types, private names, testing a threshold crossing in a copy of the config, and "if it isn't true, check the exporter's definitions before the thresholds".

## 0.2.1 — 2026-11-15

Fixes found by testing the skill on a real process (an IntentCut video production pipeline), with a fresh agent that had only the skill and the repos.

- **"What changed" now shows connector movement.** One line per update, e.g. *Moved · recorded +1, packed +3*, so it can't crowd out number changes. Before, flows never appeared in the log.
- **The exceptions panel fits up to six types on one row.** Five types used to wrap a tile onto a second row and push "Where they sit" off a 1920×1080 screen.
- **Skill** (`skills/wall-pattern/SKILL.md`): asks first whether a wall is the right shape (how many items are in flight); a way to work when no owner can be interviewed; colour that is *true* means the wall is working; ages when entry times aren't recorded; flow keys by content hash or by id and time; what resets at a window boundary; `sequence`, `staleAfterMinutes`, exception text length, which ids must be unique; check that a reused source-of-truth function is stable across tool versions.

## 0.2.0 — 2026-11-15

Quieter, and no longer tied to shifts. All changes are additive: v0.1 configs and feeds work unchanged, and `schemaVersion` stays `"1.0"`.

- **Delta window.** `display.delta.window` is `"shift"` (default, from `shiftStart`), `"day"` (from local midnight) or `"week"` (from `weekStart`, default Monday). The "since" toggle reads *Shift 07:00*, *Today* or *This week*. Found on the first real wall, a case-review cycle that has no 07:00.
- **The wall resets its own baseline.** Without a `baseline` in the feed, the wall now takes a fresh one from the first snapshot of each new window. In v0.1 it kept the first snapshot it ever saw.
- **Quiet connector labels.** A connector where something moved shows `+3 · 50` and pulses once. One where nothing moved this update shows only its window total, muted. One where nothing moved at all shows only its caption. "+0 · 0" no longer appears.
- **Stall label on its own line.** The stall word (`stallCaption`) sits under the caption as an amber pill instead of being squeezed beside it.
- **Fuller exceptions panel.** Each type tile lists its newest exceptions (up to three, or two and "+N more") instead of only the latest one.
- **Orbit: no redundant ring line.** The faint ring line from the last step to the first is skipped when a return loop already reaches the first step.

## 0.1.0 — 2026-11-15

First release: renderer, config and feed schemas, two examples, drop-in and watched feeds, the lit-brick mark. DOI [10.5281/zenodo.24244635](https://doi.org/10.5281/zenodo.24244635) (concept).
