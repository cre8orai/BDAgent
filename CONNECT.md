# Turning it on

Everything in this repo is inert until its connections exist. Most already do.

**Read this first: nothing here sends anything.** Agents draft; you press Send. The
send capability was removed from the repo on 2026-09-08, not merely disabled.

| | What it does | Status |
|---|---|---|
| **Gmail** | Reads the inbox, drafts, replies, sends as `david@cre8orglobal.com` | 🟢 **Already connected** |
| **GitHub** | Versions state so Mac and cloud runs can't duplicate each other | 🟢 **Already working** (SSH, as `cre8orai`) |
| **LinkedIn** | Archive + 7,246-connection graph, read-only | 🟢 **Ingested.** No browser automation, none needed |
| **BizDave** | Tells you drafts are waiting | 🟢 **Wired** — writes to its own tables |
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

**Drafting as you** — `create_draft`. A real Gmail draft, on the right thread, from
`david@cre8orglobal.com`, with your signature. It appears in your Gmail like anything
you started typing yourself. **The send tools are denied to every profile in this repo.**

**How you tell it's working:**

```bash
claude -p "Using Gmail, how many threads in my inbox from the last 3 days are waiting on a reply from me? List the top 5 by age."
```

If that returns real threads, everything Desk needs is live.

### Nothing sends, and there is no way to make it send

The connector *can* send. **Nothing in this repo is allowed to reach that.** Per your
instruction on 2026-09-08, the capability was removed rather than guarded — `send.sh` is
deleted from the tree, not disabled.

Enforced in three places, so removing one does not open a hole:

1. **The tree.** No script here calls a send tool.
2. **`.claude/settings.json`** — the scheduled profile. Denies send, reply, forward,
   every browser click tool, *and* `create_draft`. A scheduled agent writes CSV and stops.
3. **`.claude/settings.draft.json`** — used only by `draft.sh`. Allows `create_draft`,
   denies everything that transmits.

### Your daily loop, end to end

```bash
bash agents/cycle.sh          # all six agents run. Rows land in the outbox
bash agents/review.sh         # read each one — a to approve, k to kill
bash agents/draft.sh          # approved rows become Gmail drafts. NOTHING IS SENT
python3 agents/bizdave.py     # tell BizDave there are drafts waiting
```

You press Send in Gmail. That is the only place a message leaves.

---

## 2 · LinkedIn — read-only, and staying that way

**No agent opens linkedin.com.** Nothing clicks, nothing types, nothing logs in. The
Chrome permission I asked you for in the first pass is **not needed** — don't bother
adding it.

What the agents actually use is your export, already ingested and sitting on this
machine:

| | |
|---|---|
| 2,558 of your LinkedIn messages | rewrote `voice/STYLE.md` §12 from evidence |
| 38 connection notes | your real median is 34 characters, not the 300 limit |
| **7,246 connections** | `agents/state/connections.csv` — Scout's warm-path graph |

That graph is what found Judah Abraham, Ralph Azrak and Matt Beer — three live threads
that had been dropped rather than rejected, inside accounts RetailGTM had already scored
TAKE. Reading the archive turned out to be worth far more than automating the site ever
would have been.

LinkedIn has no draft API, so LinkedIn messages stay in `outbox.csv` and in BizDave
marked `[LinkedIn — paste by hand]`. You copy them across yourself.

A newer export just goes in `voice/raw/`, then `python3 voice/ingest.py --stats`.

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

**Nothing scheduled can send or even draft.** `draft.sh` is not in any plist, and the
scheduled permission profile denies `create_draft` outright.

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
cp ~/GitHub/BDAgent/agents/com.cre8or.bd.*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cre8or.bd.*.plist

# every morning — or just open BizDave, which now tells you
bash agents/review.sh         # a / k on each draft
bash agents/draft.sh          # they appear as Gmail drafts
python3 agents/bizdave.py     # push the notification to BizDave
```

Nothing in that list sends anything. You press Send in Gmail.
