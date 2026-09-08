#!/bin/bash
# Turns approved outbox rows into DRAFTS. It does not transmit, and there is no
# flag, environment variable or argument that makes it transmit.
#
# There used to be a send.sh here. David's instruction on 2026-09-08 was
# "never send anything just create drafts" — so the capability was deleted
# rather than guarded. See GATES.md gate 1.
#
#   bash agents/draft.sh            # push approved rows to Gmail drafts
#   bash agents/draft.sh --dry-run  # show the plan, touch nothing
#
# Email  -> a real Gmail draft, on the right thread, with the signature.
#           It sits in David's Gmail. He presses Send, or he doesn't.
# LinkedIn -> LinkedIn has no draft API. These stay in outbox.csv and are listed
#           for David to paste by hand. Nothing opens a browser.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
REPO=$(pwd)
CLAUDE="$HOME/.local/bin/claude"
DATE=$(date +%F)
LOG="agents/logs/draft-$DATE.log"
DRY=0
for a in "$@"; do [ "$a" = "--dry-run" ] && DRY=1; done

python3 agents/draft_plan.py | tee /tmp/bd-draft-plan.txt
COUNT=$(grep -c '^  ' /tmp/bd-draft-plan.txt 2>/dev/null || echo 0)
[ "$COUNT" = "0" ] && exit 0

if [ "$DRY" = "1" ]; then echo; echo "DRY RUN — nothing written."; exit 0; fi

PROMPT="Create Gmail DRAFTS for David Feuerstein. Read agents/GATES.md first.

ABSOLUTE RULE: you must not send anything. Use the Gmail create_draft tool and
nothing else. The send and reply tools are denied to you and you must not attempt
them, look for a way around them, or ask for them. If a row cannot become a draft,
leave it and report why.

1. Read agents/state/outbox.csv. Handle ONLY rows with status exactly 'approved'.
2. For each email row: create a Gmail draft from david@cre8orglobal.com. If
   thread_id is set, the draft belongs on that thread as a reply. Use the body
   exactly as approved — do not edit, shorten or improve it. Append the signature
   block from voice/STYLE.md section 11.
3. LinkedIn rows: do NOT open a browser. Leave them as they are and list them at
   the end so David can paste them himself.
4. After each draft is created set that row's status='drafted' and put the Gmail
   draft id in the notes column.
5. Report: N Gmail drafts created, N LinkedIn rows left for David, N failed and why."

"$CLAUDE" -p "$PROMPT" --add-dir "$REPO" --settings "$REPO/.claude/settings.draft.json" 2>&1 | tee -a "$LOG"

python3 agents/build_dashboard.py >>"$LOG" 2>&1 || true
echo
echo "Drafts are in your Gmail. Nothing was sent."
echo "Tell BizDave:  see agents/bizdave.py"
