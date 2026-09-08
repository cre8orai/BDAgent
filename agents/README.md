# The team

Six agents. Each one is **David in a different mode** — not a generic assistant with a
job title. They share one voice (`voice/STYLE.md`), one set of commercial facts
(`docs/company/cre8or-primer.md`), and one state directory, so they cannot contradict
each other or contact the same person twice.

David sits on top. **Chief** is who he talks to.

```
                          ┌─────────────┐
                          │    DAVID    │   approves every send
                          └──────┬──────┘
                                 │  one conversation
                          ┌──────┴──────┐
                          │    CHIEF    │   routes, assembles the brief,
                          │ orchestrator│   enforces the gates
                          └──────┬──────┘
        ┌───────────┬────────────┼────────────┬───────────┬──────────┐
        │           │            │            │           │          │
   ┌────┴───┐  ┌────┴───┐   ┌────┴───┐   ┌────┴───┐  ┌────┴───┐ ┌────┴───┐
   │ SCOUT  │  │ GHOST  │   │ OPENER │   │ CHASER │  │  DESK  │ │ CLOSER │
   │ who's  │  │ how he │   │ first  │   │ never  │  │ inbound│ │ money  │
   │ worth  │  │ sounds │   │ touch  │   │ lets a │   │ + what │ │ + next │
   │ a call │  │        │   │        │   │ thread │  │ he owes│ │  step  │
   └────────┘  └────────┘   └────────┘   │  die   │  └────────┘ └────────┘
                                         └────────┘
```

## Who each one is

| Agent | Which David | Owns | Writes to |
|---|---|---|---|
| **Chief** | David at his desk on Monday morning | Routing, the daily brief, the gates | `briefs/daily-*.md` |
| **Scout** | David the prospector | Who is worth a conversation, and the warm path in | `state/people.csv` |
| **Ghost** | David the writer | The voice. **Every outbound passes through it** | nothing — it rewrites |
| **Opener** | David at the handshake | First touch, LinkedIn and email | `state/outbox.csv` |
| **Chaser** | David who never lets a thread die | Cadence, channel switching, when to stop | `state/cadence.csv`, `state/outbox.csv` |
| **Desk** | David at 6am with coffee | Inbound triage, what he promised whom | `state/threads.csv`, `state/commitments.csv` |
| **Closer** | David in the negotiation | Pricing discipline, deal shape, the next step | `state/outbox.csv`, `briefs/<account>.md` |

## How work moves

**One direction, one queue.** Nothing skips Ghost, and nothing reaches a human being
without David flipping a row to `approved`.

```
 Scout ──► person worth contacting        ──┐
 Desk  ──► inbound needing a reply        ──┤
 Chaser──► thread that has gone quiet     ──┼──► GHOST ──► outbox.csv  (status=draft)
 Closer──► commercial move to make        ──┘                  │
                                                               ▼
                                                    ┌──────────────────────┐
                                                    │  DAVID REVIEWS       │
                                                    │  draft → approved    │
                                                    │      or → killed     │
                                                    └──────────┬───────────┘
                                                               ▼
                                            send.sh  ──► Gmail  /  LinkedIn in Chrome
                                                               │
                                                               ▼
                                                    status=sent, Chaser arms a cadence
```

## The division that matters

**Scout finds. Desk defends.** Scout is outbound pressure — new names, new paths in.
Desk is the opposite job: nothing David has already been given is allowed to rot. In
practice Desk is worth more, because a reply in the inbox has already cleared the
hardest gate.

**Ghost is a filter, not an author.** It never decides *what* to say — Opener, Chaser,
Desk and Closer decide that. Ghost decides *how it sounds*, and it has the right to
send a draft back. A draft that fails `voice/STYLE.md` §10 does not reach the outbox.

**Chief never writes.** It reads state and tells David what is worth his attention in
the next hour. If Chief starts drafting, two agents own the same sentence.

## Adapted from bizDave

The inbox half of Desk is the agent version of David's Lovable app
[bizDave](https://bizdave-personal-hub.lovable.app) — Today / Tasks / Contacts /
Updates, with the Gmail Daily Digest card that was left as a placeholder there. Here
that placeholder is filled: `briefs/daily-*.md` **is** the digest, generated from real
mail rather than typed in, and `state/commitments.csv` is the tasks table with one
change that matters — **rows are created by reading what David actually promised in
writing**, not by him remembering to add them.

## Files

```
agents/
  README.md         this file
  GATES.md          what may never happen unattended. Read before writing any runner
  CHIEF.md          the orchestrator David talks to
  scout.md  ghost.md  opener.md  chaser.md  desk.md  closer.md
  run.sh            claim → pull → run → commit → push → release
  send.sh           the ONLY thing that transmits. Foreground, human-initiated
  cycle.sh          one full pass
  com.cre8or.bd.*.plist
  state/
    people.csv        who, where they came from, the warm path, current stage
    threads.csv       live conversations and when each was last touched
    outbox.csv        the approval queue. draft | approved | sent | killed
    cadence.csv       what follow-up is due, on what channel, when
    commitments.csv   what David promised, to whom, by when
    signals.csv       reasons to reach out that expire — funding, hires, launches
  briefs/           one page per account, and the daily brief
  logs/
```

## Safety properties

Inherited from the RetailGTM agent harness, which has run nightly since Sept 2026.

- **Append-only.** Agents add rows. They never edit or delete another agent's rows.
- **Claim files.** Two runtimes cannot run the same agent at once; stale claims expire
  after 90 minutes.
- **Scoped commits.** `run.sh` stages `agents/` and nothing else.
- **No invention.** Never a person, company, figure or prior conversation that did not
  come from a tool result. `[UNKNOWN]` over a silent guess.
- **Nothing sends itself.** See [`GATES.md`](GATES.md). This is the property the whole
  design exists to protect.
