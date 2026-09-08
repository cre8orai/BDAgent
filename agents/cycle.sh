#!/bin/bash
# One full pass. Order matters: inbound before outbound, voice before queue.
# Sends nothing.
set -uo pipefail
cd "$(dirname "$0")"
for A in desk scout closer opener chaser chief; do
  echo "=== $A ==="
  bash run.sh "$A"
done
echo
echo "Drafts awaiting your approval:"
python3 - <<'PY'
import csv
rows=[r for r in csv.DictReader(open('state/outbox.csv')) if r['status']=='draft']
print(f"  {len(rows)} draft(s) in agents/state/outbox.csv")
for r in rows[:10]:
    print(f"  [{r['id']}] {r['channel']:18} {r['person']} ({r['company']}) — {r['subject'][:50]}")
PY
echo
echo "Review them:   bash agents/review.sh"
echo "Then draft:    bash agents/draft.sh   (Gmail drafts — nothing is sent)"
echo "Tell BizDave:  python3 agents/bizdave.py"
