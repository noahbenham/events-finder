"""Render data/events.json -> docs/index.html and docs/events.ics."""
import html, json
from datetime import datetime
from itertools import groupby

events = json.load(open("data/events.json"))

rows = []
for day, items in groupby(events, key=lambda e: e["start"][:10]):
    d = datetime.fromisoformat(day).strftime("%A, %b %-d")
    rows.append(f"<h2>{d}</h2>")
    for e in items:
        t = datetime.fromisoformat(e["start"]).strftime("%-I:%M %p") if "T" in e["start"] else ""
        meta = " · ".join(x for x in [t, e.get("venue"), e.get("price")] if x)
        rows.append(f'<div class="ev" data-cat="{html.escape(e.get("category","other"))}">'
                    f'<a href="{e["source"]}">{html.escape(e["title"])}</a>'
                    f'<div class="m">{html.escape(meta)} · @{e["account"]}</div>'
                    f'<div>{html.escape(e.get("summary") or "")}</div></div>')

page = f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content="noindex"><title>KC Events</title>
<style>body{{font:16px system-ui;max-width:640px;margin:1rem auto;padding:0 1rem}}
.ev{{padding:.6rem 0;border-bottom:1px solid #8884}}.m{{color:#888;font-size:.9rem}}
select{{font-size:1rem;margin:.5rem 0}}</style>
<h1>KC Events</h1>
<select onchange="document.querySelectorAll('.ev').forEach(e=>e.hidden=this.value&&e.dataset.cat!=this.value)">
<option value="">All</option><option>music</option><option>food</option><option>art</option>
<option>sports</option><option>community</option><option>other</option></select>
{''.join(rows)}
<p class=m><a href="events.ics">Subscribe (calendar)</a></p>"""
open("docs/index.html", "w").write(page)

def ics(s):
    return datetime.fromisoformat(s).strftime("%Y%m%dT%H%M%S")
cal = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//events-finder//EN"]
for i, e in enumerate(events):
    cal += ["BEGIN:VEVENT", f"UID:{i}-{e['start']}@events-finder", f"DTSTAMP:{ics(e['start'])}",
            f"DTSTART;TZID=America/Chicago:{ics(e['start'])}",
            f"SUMMARY:{e['title']}", f"LOCATION:{e.get('venue') or ''}",
            f"URL:{e['source']}", "END:VEVENT"]
cal.append("END:VCALENDAR")
open("docs/events.ics", "w").write("\r\n".join(cal))
print("built docs/")
