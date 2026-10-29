"""Turn Instagram's "Download your information" export into data/accounts.txt.

Usage: python scripts/following_from_export.py path/to/following.json
"""
import json, sys

data = json.load(open(sys.argv[1]))
entries = data.get("relationships_following", data) if isinstance(data, dict) else data
names = sorted({e["string_list_data"][0]["value"] for e in entries})
open("data/accounts.txt", "w").write("\n".join(names) + "\n")
print(f"{len(names)} accounts -> data/accounts.txt (trim to local KC ones)")
