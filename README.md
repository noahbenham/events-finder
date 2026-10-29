# events-finder

Personal Kansas City events feed built from the Instagram accounts I follow.

- `scripts/fetch.py` — reads my following list (logged in), picks KC event accounts, pulls recent posts anonymously
- `scripts/extract.py` — Claude reads captions and flyers, writes `data/events.json`
- `scripts/build.py` — renders `docs/index.html` and `docs/events.ics`
- `.github/workflows/build.yml` — runs it all daily and commits the result

Local: `INSTAGRAM_USER=... ./run.sh`
