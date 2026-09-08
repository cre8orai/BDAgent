# BDAgent

Business development for **Cre8or**, run by six agents that write as David.

**Status:** 🟢 Agent team built. Voice extracted from 287 sent messages. Nothing has
been sent — and nothing can be, without David approving it row by row.

```
DAVID  ──►  CHIEF  ──►  Scout · Ghost · Opener · Chaser · Desk · Closer
              ▲                            │
              └──────── outbox.csv ◄───────┘   status=draft
                             │
                    David approves (review.sh)
                             │
              draft.sh ──► a Gmail DRAFT sitting in his Gmail
                             │
                    he presses Send. or he doesn't.

              bizdave.py ──► BizDave says "drafts waiting" 
```

## Start here

| | |
|---|---|
| [`CONNECT.md`](CONNECT.md) | **How to turn it on.** Email is already connected; LinkedIn needs one setting |
| [`agents/README.md`](agents/README.md) | The six agents, who each one is, how work moves |
| [`agents/GATES.md`](agents/GATES.md) | What may never happen unattended, and why |
| [`voice/STYLE.md`](voice/STYLE.md) | How David writes, with the evidence |
| [`pipeline.html`](pipeline.html) | The command centre. Rebuilt after every run |

## The three commands

```bash
bash agents/cycle.sh          # all six run. Drafts land in the outbox
bash agents/review.sh         # read each draft — a to approve, k to kill
bash agents/draft.sh          # approved rows become Gmail drafts. NOTHING IS SENT
python3 agents/bizdave.py     # tell BizDave there are drafts waiting
```

## The six

| Agent | Which David | Owns |
|---|---|---|
| **Scout** | the prospector | Who is worth a call, and the warm path in |
| **Ghost** | the writer | The voice. Every outbound passes through it |
| **Opener** | at the handshake | First touch, LinkedIn and email |
| **Chaser** | who never lets a thread die | Cadence, channel switching, when to stop |
| **Desk** | at 6am with coffee | Inbound triage, and what he owes whom |
| **Closer** | in the negotiation | Pricing discipline, deal shape, the next step |

**Chief** sits above them and is who David talks to.

## The one rule

**Nothing here sends. There is no send path in the repo at all.**

Agents write rows. Approved rows become **Gmail drafts** that sit in David's Gmail until
he presses Send himself. LinkedIn is read-only to every agent — the archive and the
connection graph are read, nothing is ever typed into linkedin.com, and LinkedIn drafts
are listed for David to paste by hand.

Enforced in three places: no script calls a send tool; the scheduled permission profile
denies sending *and* drafting; the drafting profile allows `create_draft` and denies
everything else. See [`agents/GATES.md`](agents/GATES.md).

## It tells BizDave

When drafts are waiting, `agents/bizdave.py` writes them into
[bizDave](https://bizdave-personal-hub.lovable.app)'s own tables — `reply_radar_drafts`
as `proposed`, a `pending_actions` notification, and high-priority `tasks` on Today. No
new tables; BizDave already had the right ones.

## Related repos

- [`RetailGTM`](https://github.com/cre8orai/RetailGTM) — sources and scores *accounts*.
  BDAgent starts where it stops: turning a qualified account into a conversation.

## Shared context

- [`docs/company/cre8or-primer.md`](docs/company/cre8or-primer.md) — what Cre8or is.
  Read before writing any commercial argument
- [`docs/ONBOARDING.md`](docs/ONBOARDING.md) — five-minute orientation
- [`sessions/`](sessions/) — what each working session changed and decided

## Conventions

- Markdown is the source of truth; artifacts are generated from it
- Research stays separate from strategy
- Unverified claims are `[ASSUMPTION]`; questions needing David are `[OPEN]`
- Status: 🟢 done · 🟡 in progress · ⚪ not started · 🔴 blocked

See [`CLAUDE.md`](CLAUDE.md) for how AI sessions work here.
