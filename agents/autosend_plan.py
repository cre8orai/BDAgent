#!/usr/bin/env python3
"""Decide what, if anything, autosend.sh may transmit. No side effects.

Prints SEND lines only for rows in a lane David has switched to auto. Anything
else is listed as held, with the reason, so the output doubles as an audit of
why a message did not go.
"""
import csv, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "agents", "state")
cap = int(sys.argv[1]) if len(sys.argv) > 1 else 12
today = datetime.date.today().isoformat()

lanes = {r["lane"]: r for r in csv.DictReader(open(os.path.join(S, "autonomy.csv")))}
rows = list(csv.DictReader(open(os.path.join(S, "outbox.csv"))))

# A lane is live only if David set it to auto AND it is eligible at all.
auto = {k for k, v in lanes.items()
        if v["mode"] == "auto" and v["eligible_for_auto"] == "yes" and k != "brief-to-david"}

PLACEHOLDER = re.compile(r"\[[^\]]{3,}\]")

send, held = [], []
for r in rows:
    lane = r.get("lane", "")
    if r["status"] not in ("approved", "auto-approved"):
        continue
    if lane not in auto:
        held.append((r, f"lane '{lane}' is set to draft — yours to decide"))
    elif r["send_after"] and r["send_after"] > today:
        held.append((r, f"not before {r['send_after']}"))
    elif PLACEHOLDER.search(r["body"]):
        held.append((r, "contains an unfilled placeholder — never send a bracket"))
    else:
        send.append(r)

over = send[cap:]
send = send[:cap]

if not auto:
    print("No lane is set to auto. Nothing here can send.")
    print("Every approved row becomes a Gmail draft instead:  bash agents/draft.sh")
else:
    print(f"Auto lanes: {', '.join(sorted(auto))}")

for r in send:
    print(f"SEND\t{r['id']}\t{r['lane']}\t{r['person']} ({r['company']})\t{r['subject'][:44]}")
for r in over:
    print(f"held\t{r['id']}\t{r['lane']}\t{r['person']}\tover the {cap}/day ceiling")
for r, why in held:
    print(f"held\t{r['id']}\t{r.get('lane','?')}\t{r['person']}\t{why}")

print(f"\n{len(send)} to send, {len(held) + len(over)} held.")
