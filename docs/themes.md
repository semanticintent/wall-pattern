# Themes — design note

**Status:** the per-wall accent **works today** (v0.2.5 and later). Everything else here is **proposed, not implemented**. It records a direction so that it can be built, or rejected, on purpose.

## The rule: a theme changes the frame, never the meaning

A wall's colours are a language that every wall shares:

| Colour | Means |
|---|---|
| grey | Calm: nothing to do |
| amber | Watch |
| red | Act |
| blue arrow | better |
| orange arrow | worse |

If one wall's theme turned "calm" green, or made "better" orange, anyone glancing between two walls would misread one of them. So a theme may change:

- background, surfaces, lines and text;
- the accent;
- fonts, chosen from an allowed list;

and may not change the state colours or the better/worse colours. Those stay fixed, per theme brightness (dark or light), on every wall. The config's own `states[].color` stays possible for people who need it, but the skill and the guides keep steering towards the defaults.

## Layer 1: a per-wall accent (works today)

```json
"display": { "accent": "#2EC4B6" }
```

- It colours the eyebrow, a thin band along the top edge of the wall, and the refresh line. That is enough to tell walls apart from across a room, and too little to compete with the blocks.
- It must be a hex colour. Anything else is ignored and the default look is used, so a config can't inject styles.
- **Pick a blue, teal, green or violet.** Amber, orange and red already mean Watch, Act and worse. The renderer logs a note in the browser console when an accent falls in that range; it doesn't refuse it.
- With no accent, a wall looks exactly as it did before.

## Layer 2: built-in themes (proposed)

`display.theme` takes `dark` (default) or `light` today. Candidates to add:

| Theme | For |
|---|---|
| `paper` | Offices and printed snapshots: warm off-white, softer contrast |
| `contrast` | Big rooms, older screens, far viewing distances: stronger lines, larger minimum text |
| `slate` | A mid-dark alternative for screens that bloom on pure black |

Each theme is a set of values for the renderer's existing CSS variables (about 25: background, surfaces, lines, text, accent, connectors, fonts). The meaning colours belong to the brightness (dark or light) the theme declares, not to the theme.

## Layer 3: theme files (proposed)

The VS Code idea, kept to data:

```json
{
  "schemaVersion": "1.0",
  "name": "Harbour",
  "base": "dark",
  "tokens": { "bg": "#0B1620", "surface": "#11202D", "line": "#1E3344", "text": "#E3ECF2", "accent": "#3FB8AF" },
  "fonts": { "head": "Space Grotesk", "body": "Inter" }
}
```

- Loaded as `#theme=themes/harbour.json`, or named in the config.
- **Values only, never code or CSS strings.** Every colour is checked as hex, token names come from a fixed list, fonts come from an allowed list. A theme file can't inject anything, so it can come from anywhere, as feeds can. (Code, by contrast, loads only from the wall's own origin: see [adapters.md](adapters.md).)
- `base` decides the meaning colours. A theme file can't override them.
- It gets its own JSON Schema. That is what lets an assistant write a valid theme from "make it look like our brand", and lets the renderer check it.

Complexity kept in data with a schema is cheap to reason about, for people and for AI. Complexity in code is what to avoid.

## Viewer setting: colour-blind-safe meaning colours (proposed)

Some people can't tell amber from red, or green from grey. The answer is **not** a theme, because then each wall would solve it differently. It is a setting of the **viewer**, stored in their browser and applied to every wall they open:

- an alternative palette for Calm / Watch / Act and better / worse, chosen to stay distinct for the common forms of colour blindness;
- plus shapes that don't depend on colour at all: the state chip already carries a word (Calm, Watch, Act) and arrows carry direction; this would add a distinct frame pattern for Act.

Walls never choose it; people do.

## Several walls on one screen: rotation (proposed)

The companion to accents:

```
index.html#walls=6d.config.json,ops.config.json&every=60&kiosk=1
```

- The screen cycles through the listed walls, `every` seconds each, with each wall's feed kept live in the background so deltas don't reset on every turn.
- The accent band tells people which wall is up. A small row of dots in the corner, one per wall in its accent, shows where in the rotation the screen is.
- A wall that turns Act could hold the screen until it is back to Watch, or be shown more often. That is a judgment for the owner, so it should be a setting, not a default.

## Open questions

- Which two built-in themes are worth adding first?
- Should a theme file be allowed to set the accent, or is the accent always the wall's own?
- Rotation: should an Act wall hold the screen by default?
