# BDAgent

Business development for **Cre8or**, run by six agents that write as David.

**Status:** 🟢 Agent team built. Voice extracted from 287 sent messages. Nothing has
been sent — and nothing can be, without David approving it row by row.

```
DAVID  ──►  CHIEF  ──►  Scout · Ghost · Opener · Chaser · Desk · Closer
              ▲                            │
              └──────── outbox.csv ◄───────┘   status=draft
                             │
                    David approves ──► send.sh ──► Gmail / LinkedIn
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
bash agents/cycle.sh     # all six run. Drafts land in the outbox. Nothing goes out
bash agents/review.sh    # read each draft — a to approve, k to kill
bash agents/send.sh      # shows the plan, waits for you to type SEND
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

**No agent has a send tool.** They write drafts and stop. `send.sh` is the only thing
that transmits, it refuses to start without an interactive terminal, and it handles
only rows David has marked `approved`. LinkedIn is additionally capped at 8 messages a
session, 40–90 seconds apart, and any captcha stops the run instead of retrying it.

Three reasons, in [`agents/GATES.md`](agents/GATES.md): domain reputation, LinkedIn's
User Agreement, and the fact that it is David's name on every one of them.

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
