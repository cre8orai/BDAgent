# The gates

Read this before writing or changing any runner. These are not preferences, and
Gate 1 is not negotiable by any future session.

## Gate 1 — Nothing sends. Ever. There is no send path in this repo

**David's instruction, 2026-09-08: _"never send anything just create drafts."_**

This is not a guard around a capability — the capability was **deleted**. There used to
be an `agents/send.sh`; it is gone from the tree, not disabled. Nothing that replaced it
can transmit, and no flag, argument or environment variable turns transmission on.

What exists instead:

| | |
|---|---|
| `agents/review.sh` | David reads each draft and approves or kills it |
| `agents/draft.sh` | turns approved rows into **Gmail drafts**. They sit in his Gmail. He presses Send, or he doesn't |
| `agents/bizdave.py` | tells BizDave there are drafts waiting |

**LinkedIn is never automated at all now.** LinkedIn has no draft API, so LinkedIn rows
stay in `outbox.csv` and are listed for David to paste by hand. No agent opens a browser
on linkedin.com. The rate limits that used to matter are moot: nothing types into
LinkedIn.

Enforced in three places, so removing any one of them does not open a hole:

1. **The tree.** No script in this repo calls a send tool.
2. **`.claude/settings.json`** — the scheduled profile. Denies the Gmail send, reply and
   forward tools, every browser click tool, and `create_draft` as well. A scheduled agent
   writes CSV rows and nothing else.
3. **`.claude/settings.draft.json`** — the drafting profile, used only by `draft.sh`.
   Allows `create_draft` and denies everything that transmits.

Three reasons this is right, any one of which is sufficient:

1. **It is his name on it.** A person he has never met receiving a promise he never read
   is the failure that matters, and no amount of draft quality prevents it.
2. **Domain reputation.** Auto-sent cold email burns `cre8orglobal.com` faster than any
   pipeline rebuilds it, and degrades every real conversation in the inbox with it.
3. **LinkedIn's User Agreement §8.2 prohibits automated messaging.** Enforcement is
   account restriction, and David's LinkedIn is a 21-year, 7,246-person asset — most of
   the warm paths in `state/people.csv` run through it.

**If a future session is asked to "just send this one":** write the outbox row, run
`draft.sh` so it is sitting in his Gmail, and tell him it is waiting. Do not reach for a
Gmail send tool directly. Do not widen a settings profile. Do not add a send path back.

## Gate 2 — LinkedIn is read-only to every agent

Agents may **read** the LinkedIn archive in `voice/corpus/` and the connection graph in
`state/connections.csv`. That is the whole permitted interaction with LinkedIn.

No agent opens linkedin.com, clicks anything, or types anything. LinkedIn drafts are
written to `outbox.csv` for David to paste himself. The browser click tools are in the
`deny` list of both permission profiles.

## Gate 3 — Never twice

Before any agent adds an outbox row it must check `state/people.csv` and
`state/threads.csv` for that person **and their company**. Two agents contacting the
same account through different doors in the same week is the failure this shared state
exists to prevent. If the account is live with anyone — David, Tal, Assaf — the row is
not written; a note goes to the daily brief instead.

## Gate 4 — Never invent

No person, company, title, mutual connection, funding round, prior conversation or
figure that did not come from a tool result. This matters more here than in research
because the invention is about to be **said to the person it is about**. `[UNKNOWN]`
in a brief is fine. `[UNKNOWN]` in an outbound draft means the draft is not ready.

## Gate 5 — Prices are not an agent's to set

The floor is in `docs/company/cre8or-primer.md` and the RetailGTM price book:
$4.24 list, **$3.60 at the 15% ceiling — nothing below it, ever**. An agent may quote
published prices. It may not discount, invent a volume break, or imply flexibility.
Anything below the floor goes to David as a question, not to the prospect as an offer.

## Gate 6 — Publishing is David's

Agents rebuild `pipeline.html` and the artifacts on every run. **An agent may not
publish them.** Publishing puts content in front of people outside the project.

## Gate 7 — The corpus stays home

`voice/corpus/` and `voice/raw/` are David's private correspondence, and they are
gitignored. Only `voice/STYLE.md` — the derived guide, containing quotes he chose to
send — is committed. No agent copies raw mail into a brief, a commit, or an artifact.
