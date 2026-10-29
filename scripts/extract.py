"""Have Claude turn raw posts (caption + flyer image) into structured events in data/events.json.
Posts are sent in batches to keep the number of `claude -p` calls small."""
import json, os, urllib.request
from datetime import date
from claude_cli import ask_json

BATCH = 8
IMG_DIR = os.path.abspath("data/images")
os.makedirs(IMG_DIR, exist_ok=True)

posts = json.load(open("data/raw.json"))
for p in posts:
    path = os.path.join(IMG_DIR, p["url"].rstrip("/").split("/")[-1] + ".jpg")
    if not os.path.exists(path):
        try:
            urllib.request.urlretrieve(p["image"], path)
        except Exception:
            path = None
    p["image_path"] = path

events = []
for i in range(0, len(posts), BATCH):
    batch = posts[i:i + BATCH]
    body = "\n\n".join(
        f"POST {p['url']} from @{p['account']} (posted {p['posted'][:10]})\n"
        f"Flyer image: {p['image_path'] or 'none'}\nCaption: {p['caption'][:2000]}"
        for p in batch)
    events += ask_json(f"""Today is {date.today()}. Below are Instagram posts from Kansas City, MO accounts.
Read each flyer image file with the Read tool when a path is given; the date and venue are often
only in the image.

For every upcoming public event announced, output an object with: title, start (ISO 8601,
America/Chicago), end (or null), venue, address (or null), price ("Free", "$15", or null),
category (music|food|art|sports|community|other), summary (<=15 words), source (the POST url),
account (the handle). Skip posts that are not upcoming events.
Reply with ONLY a JSON list.

{body}""", allow_read=True)

seen, out = set(), []
for e in sorted(events, key=lambda e: e.get("start") or ""):
    if not e.get("start") or e["start"][:10] < str(date.today()):
        continue
    key = (e["title"].lower(), e["start"][:10])
    if key not in seen:
        seen.add(key); out.append(e)
json.dump(out, open("data/events.json", "w"), indent=1)
print(f"{len(out)} events")
