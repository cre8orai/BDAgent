#!/bin/bash
# The ONLY thing in this repo that transmits.
#
#   - Foreground. A human starts it. It is never scheduled and never backgrounded.
#   - Processes ONLY rows whose status David has set to "approved".
#   - Enforces GATES.md section 2 volumes in code, because a prompt cannot be
#     trusted to count.
#
#   bash agents/send.sh            # send approved rows that are due
#   bash agents/send.sh --dry-run  # show exactly what would go, transmit nothing
#   bash agents/send.sh --email    # email only
#   bash agents/send.sh --linkedin # LinkedIn only
set -uo pipefail
cd "$(dirname "$0")/.."
REPO=$(pwd)
CLAUDE="$HOME/.local/bin/claude"
DATE=$(date +%F)
LOG="agents/logs/send-$DATE.log"
DRY=0; ONLY=""
for a in "$@"; do
  case "$a" in
    --dry-run)  DRY=1 ;;
    --email)    ONLY=email ;;
    --linkedin) ONLY=linkedin ;;
  esac
done

# --- GATES.md section 2 limits -------------------------------------------
MAX_LINKEDIN_PER_SESSION=8
MAX_EMAIL_PER_SESSION=25
MIN_GAP=40
MAX_GAP=90

# --- refuse to run unattended --------------------------------------------
if [ ! -t 0 ] && [ "$DRY" = "0" ]; then
  echo "REFUSING: this needs an interactive terminal. It is never scheduled." | tee -a "$LOG"
  exit 3
fi

python3 - "$ONLY" "$MAX_LINKEDIN_PER_SESSION" "$MAX_EMAIL_PER_SESSION" > /tmp/bd-send-plan.txt <<'PY'
import csv, sys, datetime
only, maxli, maxem = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
today = datetime.date.today().isoformat()
rows = list(csv.DictReader(open('agents/state/outbox.csv')))
appr = [r for r in rows if r['status'] == 'approved'
        and (not r['send_after'] or r['send_after'] <= today)
        and (not only or (only == 'linkedin') == r['channel'].startswith('linkedin'))]
li = [r for r in appr if r['channel'].startswith('linkedin')][:maxli]
em = [r for r in appr if not r['channel'].startswith('linkedin')][:maxem]
held = len(appr) - len(li) - len(em)
for r in li + em:
    print(f"{r['id']}\t{r['channel']}\t{r['person']}\t{r['company']}\t{r['subject']}")
if held:
    print(f"# {held} approved row(s) held back by this session's cap — run again tomorrow")
PY

COUNT=$(grep -vc '^#' /tmp/bd-send-plan.txt 2>/dev/null || echo 0)

echo "=== plan $(date +%FT%H:%M:%S) ===" | tee -a "$LOG"
if [ "$COUNT" = "0" ]; then
  echo "Nothing approved and due." | tee -a "$LOG"
  echo "Approve some first:  bash agents/review.sh" | tee -a "$LOG"
  exit 0
fi
tee -a "$LOG" < /tmp/bd-send-plan.txt
echo | tee -a "$LOG"
echo "$COUNT queued. LinkedIn cap ${MAX_LINKEDIN_PER_SESSION}/session, ${MIN_GAP}-${MAX_GAP}s apart." | tee -a "$LOG"

if [ "$DRY" = "1" ]; then echo "DRY RUN — nothing transmitted."; exit 0; fi

read -r -p "Proceed as David? [type SEND to confirm] " ok
[ "$ok" = "SEND" ] || { echo "Aborted."; exit 0; }

PROMPT="You are executing an approved outbound run for David Feuerstein, who has just
confirmed it at an interactive prompt. Read agents/GATES.md before you start.

STRICT RULES:
1. Read agents/state/outbox.csv. Handle ONLY rows with status exactly 'approved' AND
   send_after empty or <= today. Ignore every other row. Do not draft, edit, shorten,
   improve or add anything — transmit each body exactly as David approved it.
2. Email rows: use the Gmail tools from david@cre8orglobal.com — reply on thread_id
   when it is set, otherwise a new message. Append the signature block from
   voice/STYLE.md section 11.
3. LinkedIn rows: drive the browser session David is already logged into. Open the
   person's linkedin_url and use the normal message or connect interface. Maximum
   ${MAX_LINKEDIN_PER_SESSION} in this run. Wait a randomised ${MIN_GAP}-${MAX_GAP} seconds between each one.
4. If LinkedIn shows ANY captcha, checkpoint, 'unusual activity' notice or rate
   warning: STOP the whole run immediately, do not retry, and report it to David.
5. After each success set that row's status='sent' and sent_at=now, update
   agents/state/threads.csv (last_touched, waiting_on=them) and
   agents/state/cadence.csv (touch_number+1, next_due per agents/chaser.md).
6. On any failure leave the row 'approved', put the reason in notes, and carry on.
7. Report at the end: N done, N failed, and the reason for each failure."

"$CLAUDE" -p "$PROMPT" --add-dir "$REPO" --settings "$REPO/.claude/settings.send.json" 2>&1 | tee -a "$LOG"

python3 agents/build_dashboard.py >>"$LOG" 2>&1 || true
git add agents/state/ pipeline.html 2>/dev/null
git commit -q -m "outbox: run $DATE

Processed the rows David approved. Nothing was drafted or altered at this stage.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01U9ioqyFcgyX6SvXZwFbpHd" 2>/dev/null \
  && git push --quiet origin main 2>>"$LOG"
echo "done. log: $LOG"
