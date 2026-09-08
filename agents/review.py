#!/usr/bin/env python3
"""Read the drafts waiting for approval, one at a time, and approve or kill each.

Invoked by agents/review.sh. Kept as its own file rather than a heredoc inside the
shell script: a heredoc occupies stdin, so input() would have nothing to read from
and the prompt would crash with EOFError on the first keypress.
"""
import csv, os, sys

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "agents", "state", "outbox.csv")

rows = list(csv.DictReader(open(P)))
fields = list(rows[0].keys()) if rows else []
drafts = [r for r in rows if r["status"] == "draft"]

if not drafts:
    approved = sum(1 for r in rows if r["status"] == "approved")
    print("No drafts waiting.")
    if approved:
        print(f"{approved} already approved — next:  bash agents/draft.sh")
    else:
        print("Generate some:  bash agents/cycle.sh")
    sys.exit()

print(f"{len(drafts)} draft(s).   [a]pprove   [k]ill   [s]kip   [q]uit\n")

for i, r in enumerate(drafts, 1):
    print("=" * 72)
    print(f"{i}/{len(drafts)}   {r['agent']}  ->  {r['person']} ({r['company']})")
    print(f"channel:  {r['channel']}      not before: {r['send_after'] or 'now'}")
    if r["notes"]:
        print(f"notes:    {r['notes']}")
    if r["subject"]:
        print(f"subject:  {r['subject']}")
    print("-" * 72)
    print(r["body"].replace("\\n", "\n"))
    print("-" * 72)
    try:
        c = input("[a/k/s/q] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nStopped. Nothing changed for the remaining drafts.")
        break
    if c == "q":
        break
    if c == "a":
        r["status"], r["approved_by"] = "approved", "david"
        print("  → approved\n")
    elif c == "k":
        r["status"] = "killed"
        print("  → killed\n")
    else:
        print("  → skipped, still a draft\n")

with open(P, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

n = sum(1 for r in rows if r["status"] == "approved")
left = sum(1 for r in rows if r["status"] == "draft")
print(f"\n{n} approved, {left} still waiting.")
if n:
    print("Next:  bash agents/draft.sh   (creates Gmail drafts — nothing is sent)")
