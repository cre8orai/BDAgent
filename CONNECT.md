# Turning it on

Everything in this repo is inert until three connections exist. Two of them already
do. This page is the checklist and the honest status of each.

| | What it does | Status |
|---|---|---|
| **Gmail** | Reads the inbox, drafts, replies, sends as `david@cre8orglobal.com` | 🟢 **Already connected** |
| **GitHub** | Versions state so Mac and cloud runs can't duplicate each other | 🟢 **Already working** (SSH, as `cre8orai`) |
| **LinkedIn** | Reads profiles, sends messages and invites in Chrome | 🟡 **Needs one setting** — below |
| **Schedules** | Runs the agents while you sleep | ⚪ Ready to install, not installed |

---

## 1 · Email — already done, nothing to connect

**This is the part you asked about, and it is finished.** Gmail is connected to Claude
through the Gmail connector on your account. It is how `voice/STYLE.md` was built —
287 of your own sent messages were read out of it during this session.

The connector exposes both halves:

**Monitoring inbound** — `search_threads`, `get_thread`, `list_labels`. This is what
Desk runs on. It sweeps `in:inbox newer_than:3d`, classifies every thread, and pulls
out the promises you made in your own words.

**Sending as you** — `send_message`, `reply`, `create_draft`. Mail goes out from
`david@cre8orglobal.com`, on the real thread, with your signature. Not a relay, not a
different address, not a "sent via" footer. To the recipient it is you, because it is.

**How you tell it's working:**

```bash
claude -p "Using Gmail, how many threads in my inbox from the last 3 days are waiting on a reply from me? List the top 5 by age."
```

If that returns real threads, everything Desk needs is live.

### The thing to understand about sending

The connector *can* send unattended. **This repo deliberately does not let it.**
`run.sh` tells every agent it has no send tool, and the only script that transmits is
`send.sh`, which refuses to start without an interactive terminal:

```bash
if [ ! -t 0 ]; then echo "REFUSING: needs an interactive terminal."; exit 3; fi
```

That is a real guard, not a comment. See [`agents/GATES.md`](agents/GATES.md) for the
three reasons — domain reputation, LinkedIn's terms, and the fact that it is your name
on it.

### Your daily loop, end to end

```bash
bash agents/cycle.sh     # all six agents run. Drafts land in the outbox. Nothing goes out.
bash agents/review.sh    # read each draft, press a to approve, k to kill
bash agents/send.sh      # shows the plan, waits for you to type SEND, then transmits
```

Three commands. The middle one is the whole design.

---

## 2 · LinkedIn — one setting, then it works

LinkedIn has no API for this. The agents drive **the Chrome you are already logged
into**, so there are no credentials in this repo and nothing to store. Claude clicks
the same buttons you would.

### The setting

Claude's Chrome extension needs permission for `linkedin.com`:

1. Open the Claude extension in Chrome → **Settings → Site permissions**
2. Add `linkedin.com`
3. Make sure you are logged into LinkedIn in that Chrome profile

Then check it:

```bash
claude -p "Open linkedin.com in a new tab and tell me whose account is logged in. Don't click anything else."
```

### If you use Brave instead

Per your existing setup, Brave is driven over CDP and must be launched with the
debugging port open:

```bash
open -a "Brave Browser" --args --remote-debugging-port=9222
```

### The rules the code enforces

Not suggestions — [`agents/send.sh`](agents/send.sh) counts these, because a prompt
cannot be trusted to.

| | |
|---|---|
| Messages per session | 8 |
| Gap between them | 40–90 seconds, randomised |
| Sessions per day | 1 |
| Connection requests per week | 20 |
| Any captcha or checkpoint | **stop the run, don't retry, tell David** |

**Why the caution is not excessive.** LinkedIn's User Agreement §8.2 prohibits
automated messaging, and enforcement is account restriction. Your LinkedIn is a
20-year asset and most of the warm paths in `agents/state/people.csv` run through it.
Losing it would cost more than anything a campaign could earn. Hand-paced and approved
is not a limitation here — it is the only version worth building.

### Your archive — done

Ingested 2026-09-08 from `Basic_LinkedInDataExport_09-07-2026`. It gave four things:

| | |
|---|---|
| **2,558 LinkedIn messages** you sent, 2005–2026 | Rewrote `voice/STYLE.md` §12 from evidence — it is no longer `[ASSUMPTION]` |
| **38 connection notes** | Your real median is **34 characters**, not the 300 limit |
| **7,246 connections** | `agents/state/connections.csv` — Scout's first-degree graph |
| **Confirmation** | `Let's Cre8!` appears **0 times** in 2,558 LinkedIn messages. The email close does not belong there |

It was worth far more than the voice work. Cross-referencing those connections against
RetailGTM's 122 TAKE accounts found seven with a first-degree contact already in place —
including three live threads that were dropped rather than rejected. See the watch board.

A future export just goes in `voice/raw/` and `python3 voice/ingest.py --stats` again.

---

## 3 · GitHub — already working

I tested it this session. SSH authenticates as `cre8orai` and `origin/main` is
reachable. Earlier notes saying credentials were missing were out of date.

Every agent run commits its state and pushes. That is what lets the same agents run on
your Mac and in the cloud without contacting the same person twice — **the repository
is the state, not the agent.**

---

## 4 · Schedules — ready, not yet installed

The agents run on `launchd` while the Mac is awake. Install:

```bash
cp ~/GitHub/BDAgent/agents/com.cre8or.bd.*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cre8or.bd.desk.plist
launchctl load ~/Library/LaunchAgents/com.cre8or.bd.chaser.plist
launchctl load ~/Library/LaunchAgents/com.cre8or.bd.scout.plist
launchctl load ~/Library/LaunchAgents/com.cre8or.bd.chief.plist
```

| Agent | When | Why then |
|---|---|---|
| Desk | 05:45 daily | Overnight US mail is in before you wake |
| Chaser | 06:10 daily | Cadence recalculated against what Desk just found |
| Scout | 02:30 Mon/Thu | Twice a week is enough; quality over volume |
| Chief | 06:30 daily | Writes the brief last, once the others have finished |

**Nothing scheduled can send.** `send.sh` is not in any plist and refuses to run
without a terminal.

Stop them:

```bash
launchctl unload ~/Library/LaunchAgents/com.cre8or.bd.*.plist
```

Test one by hand first:

```bash
DRY_RUN=1 bash ~/GitHub/BDAgent/agents/run.sh desk   # no Claude call, checks the plumbing
bash ~/GitHub/BDAgent/agents/run.sh desk             # the real thing
```

---

## 5 · The permission allowlist

Unattended runs can't answer permission prompts, so the tools each agent needs are
pre-approved in [`.claude/settings.json`](.claude/settings.json). **Gmail's send tools
are deliberately absent from it** — an unattended agent cannot reach them even if it
tries.

One thing that will silently break everything if it's missing: the workspace has to be
trusted. If logs say *"has not been trusted"*, run `claude` once interactively in the
repo and accept, or set `projects["/Users/david/GitHub/BDAgent"].hasTrustDialogAccepted
= true` in `~/.claude.json`.

---

## What is not connected, and would be worth it

| | Why |
|---|---|
| **Calendar** | Chaser should not queue a follow-up for a day you're already with that person. The connector exists; nothing reads it yet |
| **WhatsApp** | A real channel for you (`wa.me/+972544409813`) and completely invisible to this system |
| **Phone/Zoom notes** | Wispr Flow is connected and holds meeting transcripts. Desk could turn a call into commitment rows automatically instead of waiting for you to write the recap |

None of these block anything. Say the word on any of them.

---

## The shortest possible version

```bash
# once
#   add linkedin.com to the Claude Chrome extension's site permissions
cp ~/GitHub/BDAgent/agents/com.cre8or.bd.*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cre8or.bd.*.plist

# every morning
open ~/GitHub/BDAgent/pipeline.html   # or the published artifact
bash agents/review.sh                 # a / k on each draft
bash agents/send.sh                   # type SEND
```
