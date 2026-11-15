# Changelog

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
