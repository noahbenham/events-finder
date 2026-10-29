"""Thin wrapper around `claude -p` so scripts can use a Claude Pro login instead of an API key."""
import json, re, subprocess


def ask(prompt, allow_read=False):
    cmd = ["claude", "-p", "--output-format", "text"]
    if allow_read:
        cmd += ["--allowedTools", "Read"]
    out = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=600)
    if out.returncode:
        raise RuntimeError(out.stderr.strip())
    return out.stdout


def ask_json(prompt, allow_read=False):
    text = ask(prompt, allow_read)
    m = re.search(r"\[.*\]", text, re.S)  # tolerate prose or code fences around the list
    return json.loads(m.group(0)) if m else []
