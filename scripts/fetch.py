"""Log in with a saved Instaloader session, read who I follow, keep the KC event-posting
accounts, and pull their recent posts into data/raw.json.

Session setup (once, locally): instaloader --login=YOUR_USERNAME
Env: INSTAGRAM_USER, optional INSTAGRAM_SESSION_FILE (defaults to instaloader's own location).
"""
import json, os, time
from datetime import datetime, timedelta, timezone
import instaloader
from claude_cli import ask_json

DAYS = 7
USER = os.environ["INSTAGRAM_USER"]
CACHE = "data/accounts.json"  # {handle: true/false} decided once per account

def loader():
    return instaloader.Instaloader(download_pictures=False, download_videos=False,
                                   save_metadata=False, quiet=True)

# Logged-in session is used for one thing only: reading who I follow.
# Everything else (bios, posts) goes through an anonymous session.
anon = loader()
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

try:
    mine = loader()
    mine.load_session_from_file(USER, os.environ.get("INSTAGRAM_SESSION_FILE"))
    following = [p.username for p in
                 instaloader.Profile.from_username(mine.context, USER).get_followees()]
except Exception as e:
    print(f"could not read following list ({e}); using cached accounts")
    following = []

new = {}
for h in following:
    if h in cache:
        continue
    try:
        p = instaloader.Profile.from_username(anon.context, h)
        new[h] = f"{p.full_name} — {p.biography}".replace("\n", " ")
    except Exception as e:
        print(f"skip bio {h}: {e}")
    time.sleep(5)
if new:
    listing = "\n".join(f"@{h}: {bio[:200]}" for h, bio in new.items())
    keep = ask_json(f"""Below are Instagram accounts with their name and bio. Reply with ONLY a JSON
list of the handles (no @) that are likely to post about upcoming public events in the
Kansas City, MO metro area: venues, bars, promoters, festivals, galleries, teams, markets,
community orgs. Exclude personal friends, celebrities, brands, and non-KC accounts.

{listing}""")
    for h in new:
        cache[h] = h in keep
    json.dump(cache, open(CACHE, "w"), indent=1, sort_keys=True)

accounts = [h for h, ok in cache.items() if ok]
print(f"{len(accounts)} event accounts of {len(cache)} followed")

cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS)
posts = []
for name in accounts:
    try:
        for p in instaloader.Profile.from_username(anon.context, name).get_posts():
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
