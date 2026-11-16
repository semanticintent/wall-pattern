# How WALL Pattern compares

WALL Pattern is not a new idea. Boards that show a running process to the people running it are decades old. This page places WALL among them: what it inherits, where it differs, and where something else is the better choice.

The comparisons are with **kinds** of tools, not with products. Products named in a row are examples of the kind, described only by what that kind typically does.

## The family it belongs to

| Kind | What it shows | Who watches it | What WALL takes from it |
|---|---|---|---|
| **Andon board** (lean manufacturing) | A light per station; it turns on when a station needs help | Line workers and supervisors | Colour means "come and look". Off, or grey, is normal |
| **Visual management / obeya room** | Walls of charts and boards for a plant or programme | Team leads, managers walking the floor | The state of the work should be readable without asking anyone |
| **Kanban board** | Work items as cards in columns, often with limits per column | Delivery and software teams | Work is shaped as steps, and queues between steps are where it gets stuck |
| **Call-centre wallboard** | Queue length, wait times, agents available | Agents and team leads, all shift | A screen for the shift, refreshed continuously |
| **Operations-centre wall** (IT, networks, logistics) | Status, alarms and maps on big screens, often cycling | Operators on shift, incident leads | Read from across a room; several walls on one screen |
| **Information radiator** (agile software) | Build status, deployments, incidents on a team TV | Engineering teams | Put the state where people already are, so nobody has to go and look for it |
| **Value stream map** | The flow of a process, with wait times between steps | Improvement teams, in workshops | Steps and handoffs drawn as a flow, including what loops back |

## Where WALL is different

### 1. Shaped like the process, not like a grid

Most wallboards and dashboards are a **grid of tiles**: one metric per tile, arranged to fit the screen. WALL draws the **process**: steps in order, the handoffs between them, and the loops where work comes back. A stall reads as a place in the flow ("the handoff into Packing is backing up"), not as one tile among twenty.

A value stream map has this shape too, but it is usually drawn once, in a workshop. WALL is that map, live.

### 2. Grey is normal

Many boards colour everything: green for fine, amber, red. A screen that is mostly green still asks to be read, and a board that starts amber teaches people to ignore it. WALL's default state is **grey**. Colour appears only where a step crosses a threshold someone chose, and thresholds are meant to be set so that **an ordinary day is entirely grey**. Then any colour is news.

### 3. What changed, not only what is

Most dashboards show the current state, and leave it to the viewer to remember what it was an hour ago. WALL keeps the previous snapshot and the baseline for the shift, day or week, and shows:

- **deltas** on every number, coloured by meaning (blue better, orange worse), not by direction;
- a **"What changed" list** for each update, with the most important changes first;
- **flows** along handoffs (+3 moved since the last update).

The source only reports what is true now. The wall works out the rest.

### 4. One number per step

A WALL step has one **hero** number that answers "is this step OK?", plus up to four supporting ones. That limit is deliberate: it forces the question "what does OK mean here?" to be answered when the wall is designed, not left to whoever is looking at it.

### 5. An open format, not a product

| | WALL Pattern | A typical wallboard or BI product |
|---|---|---|
| What you get | Two JSON files with published schemas, and one HTML file | An application, an account and a data connector |
| Hosting | Any static file host, a shared folder, or nothing (drop files in a browser) | The vendor's service or a server you run |
| Data in | Anything that can write a JSON file | The product's connectors |
| Lock-in | None: the format is documented and MIT-licensed | The boards live in the product |
| Cost | Free | Usually per seat or per screen |

Because the format is small and written down, an AI assistant can design a wall and write its feed exporter from a short description. The repository includes a skill and a guide for that ([`skills/wall-pattern/`](../skills/wall-pattern/SKILL.md), [`for-assistants.md`](for-assistants.md)).

### 6. Meaning colours are the same on every wall

Walls can be told apart by an accent colour, and themes can change the frame. But grey, amber and red always mean Calm, Watch and Act, and blue and orange always mean better and worse, on every wall. Someone who learns to read one wall can read all of them. See [themes.md](themes.md).

## Where something else is the better choice

| If you need | Use instead |
|---|---|
| **Trends over weeks or months**, targets, forecasts | A KPI dashboard or BI tool. WALL shows the present and recent change, not history |
| **Drilling into individual records**, filtering, ad hoc questions | The source system or a BI tool. WALL shows counts and short exception lines only |
| **Moving work** (assigning, dragging cards, updating status) | A kanban or ticketing tool. WALL is read-only |
| **Alerting someone who isn't looking** (pages, messages, escalation) | A monitoring or alerting system. WALL assumes someone is looking |
| **Many metrics with no flow between them** (server health, sales by region) | A tile-based wallboard. With no steps and handoffs, WALL's shape adds nothing |
| **A process with usually one item in flight** | A checklist. Every count would be 0 or 1 |
| **Ready-made connectors** with no setup | A commercial wallboard product. WALL needs a small exporter per data source |

## Who it is for

- **People running a flow during the day:** shift leads, supervisors, operators, delivery and support teams. Their question is "where do I look right now?"
- **People walking past:** managers and neighbouring teams, who get the state in a few seconds without asking.
- **People who already have the data but not the screen:** a spreadsheet, an export or a script output, and no budget or appetite for a dashboard product.

It is **not** aimed at executive reporting, analysts, or anyone whose question is "how have we done this quarter?".

## In one sentence

Most boards answer *"how are we doing?"* with tiles. WALL answers *"where is work stuck, and what changed?"* with the shape of the process, in grey, with colour only where someone should look.
