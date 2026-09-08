#!/bin/bash
# Read the drafts waiting for you, one screen at a time, and approve or kill each.
#   bash agents/review.sh
cd "$(dirname "$0")/.."
python3 - <<'PY'
import csv, sys
P = 'agents/state/outbox.csv'
rows = list(csv.DictReader(open(P)))
fields = list(rows[0].keys()) if rows else []
drafts = [r for r in rows if r['status'] == 'draft']
if not drafts:
    print("No drafts waiting. Run:  bash agents/cycle.sh")
    sys.exit()
print(f"{len(drafts)} draft(s).   [a]pprove   [k]ill   [s]kip   [q]uit\n")
for i, r in enumerate(drafts, 1):
    print("=" * 72)
    print(f"{i}/{len(drafts)}   {r['agent']}  ->  {r['person']} ({r['company']})")
    print(f"channel:  {r['channel']}      not before: {r['send_after'] or 'now'}")
    if r['notes']:
        print(f"notes:    {r['notes']}")
    print(f"subject:  {r['subject']}")
    print("-" * 72)
    print(r['body'].replace('\\n', '\n'))
    print("-" * 72)
    c = input("[a/k/s/q] ").strip().lower()
    if c == 'q':
        break
    if c == 'a':
        r['status'] = 'approved'
        r['approved_by'] = 'david'
    elif c == 'k':
        r['status'] = 'killed'
with open(P, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
n = sum(1 for r in rows if r['status'] == 'approved')
print(f"\n{n} approved.  Next:  bash agents/send.sh")
PY
