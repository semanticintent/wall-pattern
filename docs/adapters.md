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

## Open questions

- Should the browser host exist at all, or should adapters run only at the edge, keeping the browser a pure renderer?
- Where does a declarative mapping end and an adapter begin?
- How does a wall screen show that its numbers come from an adapter, not a feed it can audit?
