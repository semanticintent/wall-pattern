# Picking up a feed: live, shared and offline — design note

**Status: proposed, not implemented,** except where a line says "works today". It records a direction so that it can be built, or rejected, on purpose. It sits beside [adapters.md](adapters.md), which is about *making* a feed; this note is about *reaching* one.

## Three ways to reach a feed

| Mode | Source | Updates | Who can see it |
|---|---|---|---|
| **Live** | a URL (`?feed=`) | every refresh | whoever can reach the URL; see below |
| **Watched file** | a local or synced file | when the file changes | the file system's own permissions |
| **Offline wall** | embedded in one HTML file | never: a frozen moment | whoever holds the file |

Live and watched file **work today**. So does saving the current snapshot (**Source & settings → download feed**). The offline wall is the new proposal.

## Live: who may read the feed

### First choice: serve the page next to the feed

The renderer is one HTML file with no build step. If the server that holds the data also serves `index.html`:

- **There is no CORS.** The page and the feed share an origin.
- **The server's own login applies.** The browser sends the person's existing session with the page's requests, so the wall sees what that person may see. No token is in the page, the config or the URL.

This is the boring answer, and the best one whenever the data's owner can host one file.

### When the page can't live next to the data

1. **An edge relay.** A small Worker holds the credential, fetches the data, and publishes a plain feed with CORS headers. This is the edge host in [adapters.md](adapters.md).
2. **A capability URL.** The URL itself is the permission: `…/feed.json?key=<long random value>`. Anyone holding the link can read the feed, as with a shared-document "anyone with the link" setting or a webhook URL.

### Capability URLs, in more detail

The key can be short-lived (minutes, a day) for sharing one wall once, or **standing**: the application behind it keeps rewriting the feed, and the same URL keeps working. A standing URL is what a wall on a screen wants. It is also the riskiest kind, so it needs:

- **Revocation.** The server keeps a list of issued keys and can cancel one without changing anything else. A key derived from a fixed secret, which can't be cancelled alone, is not enough for a standing URL.
- **A narrow scope.** One key reads one feed, read-only. It never also reaches the data behind the feed.
- **Rotation.** Issue a new key from time to time, and when someone who had the link leaves.
- **Summary-level content.** The feed should already be safe to show on a screen in a corridor. A leaked link then exposes exactly that and no more.

**Where a URL leaks, and how much it matters:**

| Where | How significant | Mitigation |
|---|---|---|
| Browser history, and history synced to the person's other devices | Low on a person's own machine; real on a shared or kiosk machine | Kiosk browser profile with history off |
| The address bar on a wall screen, in screenshots or screen shares | Real: walls are on screens people photograph | Kiosk / full-screen mode hides the bar |
| Copy-paste into chat or email | Real, and by design: that's how the link is shared | Treat sharing the link as sharing the feed |
| Server and proxy logs (query strings are logged; corporate proxies that inspect traffic log full URLs) | Moderate: the feed server's own logs are usually fine; third-party logs are not | Rotation and revocation |
| `Referer` sent to other sites | Low today: browsers send only the origin to other sites by default, and the renderer has no outgoing links | Add `<meta name="referrer" content="no-referrer">` to the renderer anyway; it costs nothing |

**One cheap improvement:** let the renderer take the feed URL from the **fragment**, `index.html#feed=…`, as well as from the query. The part after `#` is never sent to the server that hosts the page and never appears in `Referer`. The key still travels to the feed server, which owns it anyway. This removes the page host's logs from the list above. It doesn't help with history, screens or copy-paste.

### CORS: what it is for

CORS is not a recommendation, and it is not protection for the server's data. **It protects the person using the browser.** Without it, any web page that person visits could quietly read responses from other sites, using their logged-in sessions and their position inside a company network. The browser enforces it strictly. But only the browser enforces it: the server still answers, and anything that isn't a browser page can read the answer.

That is why tools like Postman, `curl` or a script never meet CORS. They don't carry the person's sessions, and no stranger's page is running inside them. The legitimate ways through are therefore the ones that move the fetch out of the page, or that let the server say yes:

- **The server says yes.** It sends `Access-Control-Allow-Origin` naming the wall's origin, or `*`. For a feed protected by a capability URL rather than by cookies, `*` is safe: no session travels with the request, so there is nothing for a stranger's page to borrow. **Capability URLs and `*` go well together.**
- **Same origin:** serve the page next to the feed, as above.
- **A relay:** the edge Worker fetches server to server, where CORS doesn't apply, and republishes the feed.

What to avoid: starting the browser with web security turned off, or using a browser extension that removes CORS. Both switch off the protection for everything else that browser opens, not just the wall.

## Offline wall: a wall you can take with you

The new proposal is one self-contained HTML file containing:

- the renderer;
- the config;
- the last few feed snapshots.

Opened anywhere, with no network, it shows the wall as it was at that moment.

- **It replays what changed.** With several snapshots inside, it can step through them, so deltas and "What changed" still mean something offline.
- **It says it is frozen.** The status reads "Snapshot of 14:05, 16 Nov", never Live, and never Stale.
- **It can be emailed, attached to a report or opened on a plane.** An automated pipeline could write one at the end of each shift or week as its record.
- **The same idea as a Mere package** (`.mp.html`): a document that carries its own data and its own viewer.

**What it would take in the renderer:**

- A **Save as offline wall** action that writes a copy of the page with the config and the snapshots in `<script type="application/json">` tags.
- On load, read those tags if they are present, and ignore `?feed=` and the watched file.
- The same validation as any other feed. An offline wall is checked like a fetched one.

**Its limit:** whoever holds the file can read everything in it, forever. It has no revocation. Only summary-level content belongs in it, which is already the rule for feeds.

## Open questions

- Should an offline wall carry a fixed number of snapshots, or everything since the start of the current window?
- Should a standing capability URL be built into a reference exporter, or left to each server?
- Is reading the feed URL from the fragment worth a second way to pass parameters, or does it just confuse people?
