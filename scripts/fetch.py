"""Anonymously (no login) pull recent posts from the KC event accounts.

Candidates come from data/accounts.txt. Each new handle's bio is checked once by Claude
to confirm it is a Kansas City account that posts events; the verdict is cached in
data/accounts.json so later runs only fetch posts.
"""
import json, os, time
from datetime import datetime, timedelta, timezone
import instaloader
from claude_cli import ask_json

DAYS = 7
CACHE = "data/accounts.json"  # {handle: true/false}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

L = instaloader.Instaloader(download_pictures=False, download_videos=False,
                            save_metadata=False, quiet=True, user_agent=UA)
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
candidates = [l.strip() for l in open("data/accounts.txt")
              if l.strip() and not l.startswith("#")]

# Classify handles we haven't seen before
new = {}
for h in candidates:
    if h in cache:
        continue
    try:
        p = instaloader.Profile.from_username(L.context, h)
        new[h] = f"{p.full_name} — {p.biography}".replace("\n", " ")
    except instaloader.exceptions.ProfileNotExistsException:
        cache[h] = False
        print(f"no such account: {h}")
    except Exception as e:
        print(f"bio fetch failed, will retry next run: {h}: {e}")
    time.sleep(8)
if new:
    listing = "\n".join(f"@{h}: {bio[:200]}" for h, bio in new.items())
    keep = ask_json(f"""Below are Instagram accounts with their name and bio. Reply with ONLY a JSON
list of the handles (no @) that are Kansas City metro accounts likely to post about upcoming
public events: music venues, galleries, markets, festivals, breweries, districts, local media.
Exclude personal accounts, non-KC accounts, and accounts that look unrelated to events.

{listing}""")
    for h in new:
        cache[h] = h in keep
json.dump(cache, open(CACHE, "w"), indent=1, sort_keys=True)

accounts = [h for h in candidates if cache.get(h)]
print(f"{len(accounts)} event accounts of {len(candidates)} candidates")

cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS)
posts = []
for name in accounts:
    try:
        for p in instaloader.Profile.from_username(L.context, name).get_posts():
            if p.date_utc.replace(tzinfo=timezone.utc) < cutoff and not p.is_pinned:
                break
            posts.append({"account": name, "url": f"https://instagram.com/p/{p.shortcode}",
                          "posted": p.date_utc.isoformat(), "caption": p.caption or "",
                          "image": p.url})
    except Exception as e:
        print(f"skip {name}: {e}")
    time.sleep(10)  # be gentle; avoids blocks
json.dump(posts, open("data/raw.json", "w"), indent=1)
print(f"{len(posts)} posts")
