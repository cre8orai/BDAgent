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

# Push the pipeline itself into bizDave — deals, contacts, activities, commitments
# and open questions. Costs no Lovable credits and no model tokens: it is a plain
# database write. Without BIZDAVE_DB_URL it prints the SQL and changes nothing.
if [ -n "${BIZDAVE_DB_URL:-}" ]; then
  python3 sync_bizdave.py --execute && echo "bizDave pipeline updated."
  psql "$BIZDAVE_DB_URL" -q -f link_companies.sql && echo "bizDave companies linked."
else
  echo "Sync bizDave: export BIZDAVE_DB_URL, then"
  echo "               python3 agents/sync_bizdave.py --execute"
  echo "               psql \"\$BIZDAVE_DB_URL\" -f agents/link_companies.sql"
fi
