#!/bin/bash
# The gated send path. It exists because David asked for it, and it only ever
# acts on lanes HE has switched to auto in agents/state/autonomy.csv.
#
# Default for every lane is draft. This script does nothing at all until he
# flips a switch on the command centre, and one flip back stops it.
#
#   bash agents/autosend.sh            # act on lanes currently set to auto
#   bash agents/autosend.sh --dry-run  # show what would go, transmit nothing
#
# Everything NOT in an auto lane keeps the old path untouched: it becomes a
# Gmail draft via draft.sh and waits for him.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
REPO=$(pwd)
CLAUDE="$HOME/.local/bin/claude"
DATE=$(date +%F)
LOG="agents/logs/autosend-$DATE.log"
DRY=0
for a in "$@"; do [ "$a" = "--dry-run" ] && DRY=1; done

MAX_PER_DAY=12          # a hard ceiling regardless of what the queue holds
MIN_GAP=45              # seconds between sends, randomised upward

mkdir -p agents/logs
python3 agents/autosend_plan.py "$MAX_PER_DAY" | tee /tmp/bd-auto-plan.txt
grep -q '^SEND\b' /tmp/bd-auto-plan.txt || exit 0

if [ "$DRY" = "1" ]; then echo; echo "DRY RUN — nothing transmitted."; exit 0; fi

PROMPT="You are sending outreach that David has pre-authorised by switching a LANE to
auto in agents/state/autonomy.csv. Read agents/GATES.md gate 1 first.

STRICT RULES:
1. Read agents/state/autonomy.csv. A lane may be acted on ONLY if its mode is exactly
   'auto' AND its eligible_for_auto is 'yes'. Every other lane is untouchable here.
2. Read agents/state/outbox.csv. Send ONLY rows whose lane is an auto lane AND whose
   status is 'approved' or 'auto-approved', and whose send_after is empty or <= today.
   Ignore every other row — they are David's to decide.
3. Send the body EXACTLY as written. Do not edit, improve, shorten or personalise it
   further at send time. If a row contains a placeholder in square brackets, or any
   [UNKNOWN], SKIP it and say so — a bracket in a sent message is the worst outcome here.
4. Maximum ${MAX_PER_DAY} in this run. Wait a randomised ${MIN_GAP}+ seconds between each.
5. Never touch LinkedIn. Never open a browser. Email only.
6. After each send set status='sent', sent_at=now, and update threads.csv and
   cadence.csv per agents/chaser.md.
7. Append every send to agents/logs/sent-ledger.csv with columns
   sent_at,lane,person,company,subject,outbox_id — this is what David reviews.
8. Report: N sent, N skipped and why."

"$CLAUDE" -p "$PROMPT" --add-dir "$REPO" --settings "$REPO/.claude/settings.auto.json" 2>&1 | tee -a "$LOG"

python3 agents/build_dashboard.py >>"$LOG" 2>&1 || true
echo
echo "Sent on David's standing authorisation. Ledger: agents/logs/sent-ledger.csv"
echo "Tell him what went out:  python3 agents/bizdave.py --sent"
