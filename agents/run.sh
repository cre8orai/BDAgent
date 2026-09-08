#!/bin/bash
# Runs one BD agent unattended: claim -> pull -> run -> commit -> push -> release.
# Usage: run.sh scout | ghost | opener | chaser | desk | closer | chief
#
# This script CANNOT send OR draft anything. Agents write rows to state/outbox.csv
# and stop. Drafting is draft.sh, which a human starts, and which only ever creates
# Gmail drafts. There is no send path anywhere in this repo. See GATES.md gate 1.
set -uo pipefail
AGENT="${1:-}"
REPO="$HOME/GitHub/BDAgent"
CLAUDE="$HOME/.local/bin/claude"
[ -z "$AGENT" ] && { echo "usage: run.sh <scout|ghost|opener|chaser|desk|closer|chief>"; exit 2; }

# agent files are lowercase except CHIEF.md
SPEC="$REPO/agents/$AGENT.md"
[ -f "$SPEC" ] || SPEC="$REPO/agents/$(echo "$AGENT" | tr '[:lower:]' '[:upper:]').md"
[ -f "$SPEC" ] || { echo "no such agent: $AGENT"; exit 2; }

cd "$REPO" || exit 1
mkdir -p agents/logs agents/state agents/briefs
DATE=$(date +%F)
STAMP=$(date +%FT%H:%M:%S)
LOG="agents/logs/run-$AGENT-$DATE.log"
CLAIM="agents/state/.claim-$AGENT"

# --- claim ----------------------------------------------------------------
if [ -f "$CLAIM" ]; then
  AGE=$(( $(date +%s) - $(stat -f %m "$CLAIM" 2>/dev/null || echo 0) ))
  if [ "$AGE" -lt 5400 ]; then
    echo "[$STAMP] $AGENT claimed ${AGE}s ago by $(cat "$CLAIM"). Skipping." | tee -a "$LOG"; exit 0
  fi
  echo "[$STAMP] stale claim (${AGE}s), taking over" | tee -a "$LOG"
fi
echo "$(hostname -s) $STAMP" > "$CLAIM"
trap 'rm -f "$CLAIM"' EXIT

# --- sync -----------------------------------------------------------------
STASHED=0
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  git stash push --quiet -m "bd-autostash-$STAMP" 2>>"$LOG" && STASHED=1
fi
git pull --rebase --quiet origin main 2>>"$LOG" || echo "[$STAMP] pull failed, working offline" >>"$LOG"
[ "$STASHED" = "1" ] && { git stash pop --quiet 2>>"$LOG" || echo "[$STAMP] WARNING: autostash not restored — 'git stash list'" | tee -a "$LOG"; }

echo "[$STAMP] starting $AGENT" | tee -a "$LOG"

# --- run ------------------------------------------------------------------
PROMPT="Read agents/$(basename "$SPEC"), agents/GATES.md and voice/STYLE.md, then carry out that agent's run for today ($DATE).
Follow its rules exactly. Never invent a person, company, figure or prior conversation.
You have NO send tool and you must not attempt to send anything: every outbound goes to
agents/state/outbox.csv with status=draft and stops there."

if [ "${DRY_RUN:-0}" = "1" ]; then
  echo "[$STAMP] DRY RUN — skipping the Claude call" | tee -a "$LOG"; RC=0
else
  [ -x "$CLAUDE" ] || { echo "[$STAMP] FATAL: claude not at $CLAUDE" | tee -a "$LOG"; exit 127; }
  "$CLAUDE" -p "$PROMPT" \
    --permission-mode acceptEdits \
    --settings "$REPO/.claude/settings.json" \
    --add-dir "$REPO" --add-dir "$HOME/GitHub/RetailGTM" \
    < /dev/null >>"$LOG" 2>&1
  RC=$?
  [ $RC -ne 0 ] && echo "[$(date +%FT%H:%M:%S)] AGENT FAILED rc=$RC — see above." | tee -a "$LOG"
  grep -qi "has not been trusted" "$LOG" && echo "[$(date +%FT%H:%M:%S)] WORKSPACE NOT TRUSTED — set projects[\"$REPO\"].hasTrustDialogAccepted=true in ~/.claude.json" | tee -a "$LOG"
  grep -qi "haven.t granted it yet\|requested permissions" "$LOG" && echo "[$(date +%FT%H:%M:%S)] TOOL REFUSED — not in .claude/settings.json allow list" | tee -a "$LOG"
fi
echo "[$(date +%FT%H:%M:%S)] $AGENT exited $RC" | tee -a "$LOG"

# --- guard: nothing may have pre-approved itself --------------------------
BAD=$(awk -F, 'NR>1 && $11!="draft" && $11!="approved" && $11!="sent" && $11!="killed" {print}' agents/state/outbox.csv 2>/dev/null | wc -l | tr -d ' ')
if [ "$BAD" != "0" ]; then
  echo "[$(date +%FT%H:%M:%S)] GATE VIOLATION: $BAD outbox rows with an illegal status" | tee -a "$LOG"
fi

# --- rebuild the dashboard so it cannot drift -----------------------------
python3 agents/build_dashboard.py >>"$LOG" 2>&1 || echo "[$(date +%FT%H:%M:%S)] dashboard build failed (non-fatal)" >>"$LOG"

# --- commit ---------------------------------------------------------------
SCOPE="agents/ pipeline.html"
if [ -n "$(git status --porcelain $SCOPE)" ]; then
  git add $SCOPE
  git commit -q -m "agents: $AGENT run $DATE

Automated run, changes limited to agents/. Nothing was sent — drafts are in
agents/state/outbox.csv awaiting approval.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01U9ioqyFcgyX6SvXZwFbpHd"
  git push --quiet origin main 2>>"$LOG" && echo "[$(date +%FT%H:%M:%S)] pushed" | tee -a "$LOG" \
    || echo "[$(date +%FT%H:%M:%S)] PUSH FAILED — committed locally only" | tee -a "$LOG"
else
  echo "[$(date +%FT%H:%M:%S)] no changes" | tee -a "$LOG"
fi
exit $RC
