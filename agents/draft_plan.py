#!/usr/bin/env python3
"""Print what draft.sh would turn into Gmail drafts. No side effects."""
import csv, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "agents", "state", "outbox.csv")
rows = list(csv.DictReader(open(P)))
appr = [r for r in rows if r["status"] == "approved"]
email = [r for r in appr if not r["channel"].startswith("linkedin")]
linked = [r for r in appr if r["channel"].startswith("linkedin")]

if not appr:
    d = sum(1 for r in rows if r["status"] == "draft")
    print("Nothing approved.")
    print(f"{d} draft(s) waiting — review them:  bash agents/review.sh" if d
          else "No drafts either. Generate some:  bash agents/cycle.sh")
    raise SystemExit

print(f"{len(email)} to become Gmail drafts:")
for r in email:
    where = f"reply on {r['thread_id']}" if r["thread_id"] else "new thread"
    print(f"  {r['id']}  {r['person']} ({r['company']})  [{where}]  {r['subject'][:44]}")
if linked:
    print(f"\n{len(linked)} LinkedIn — no draft API, listed for you to paste:")
    for r in linked:
        print(f"  {r['id']}  {r['person']} ({r['company']})")
print("\nNothing here sends. draft.sh has no send path.")
