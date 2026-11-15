# Repair desk: a wall fed from a spreadsheet

Three steps, a day window, two exception types, no flows (cells hold totals, not item movements).

| File | What it is |
|---|---|
| `wall.config.json` | The wall's structure. |
| `wall.csv` | The spreadsheet's `wall` tab, saved as CSV: `id,value`, one row per indicator, plus `age:<step id>` rows. |
| `exceptions.csv` | Optional `exceptions` tab: `id,type,step,text`, one row per open exception. |
| `wall_tab_to_feed.py` | Python 3.8+, standard library only. Turns the CSVs into `wall.feed.json` and reports anything that doesn't match the config. |
| `wall.feed.json` | The converter's output for these CSVs. |

```
python3 wall_tab_to_feed.py wall.config.json wall.csv wall.feed.json exceptions.csv
```

Run it after each export (Task Scheduler, cron or a Power Automate step) and point the wall at `wall.feed.json`: **Source & settings → Pick a feed file to watch** in Chrome or Edge. It keeps its sequence number in `wall.feed.json.state.json` beside the feed.

The full walkthrough, written for any chat assistant, is [`docs/for-assistants.md`](../../docs/for-assistants.md).
