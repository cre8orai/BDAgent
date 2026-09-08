# The gates

Read this before writing or changing any runner. These are not preferences, and
Gate 1 is not negotiable by any future session.

## Gate 1 — The mode is David's to set, and the default is draft

**This gate changed on 2026-09-08 and the history matters.** It first said "nothing
sends, ever", after his instruction *"never send anything just create drafts."* He then
said:

> *"prospecting emails are ok to automate but put them at first in drafts and notify me
> until I get comfortable with the content and how the outreach is being done, and
> always give me the option to automate and send."*

So a send path exists again — **but only for a lane he has personally switched on**, and
he can switch it off in one click. Do not read the old absolute rule back into this file.

### How it works

`state/autonomy.csv` holds one row per lane with a `mode` of `draft` or `auto`.
**Every lane ships as `draft`.** David changes a mode on the command centre; Chief reads
it back and writes it into the CSV.

| Lane | Eligible for auto? | Why |
|---|---|---|
| `prospecting-email` | **yes** | First touch to someone new. The lane he named |
| `followup-email` | **yes** | Chaser touches 2–4 on a silent thread. Earn prospecting's trust first |
| `reply-email` | **no** | A wrong reply damages a relationship that already exists |
| `linkedin` | **no** | No API, and automated messaging breaches LinkedIn's UA. He pastes these |
| `commercial` | **no** | Price, terms, commitments. Gate 6 |
| `brief-to-david` | auto already | Email to David is not outreach. He asked for it |

**A lane marked `eligible_for_auto=no` cannot be switched on at all** — the board offers
no control, and `autosend_plan.py` refuses it even if the CSV is edited by hand. Two
independent checks, because a mis-set flag should not be able to send a reply.

### The three paths

| Script | Acts on | Result |
|---|---|---|
| `review.sh` | drafts | David approves, kills, or sends back |
| `draft.sh` | approved rows in **draft** lanes | a Gmail draft. He presses Send |
| `autosend.sh` | approved rows in **auto** lanes | sent, logged to `logs/sent-ledger.csv` |

`run.sh` still cannot do any of it: the scheduled profile denies sending *and*
`create_draft`. Scheduled agents write CSV rows, nothing more.

### What auto mode still refuses

Even in a lane he has switched on:

- **A message containing `[brackets]` or `[UNKNOWN]` is never sent.** A placeholder
  reaching a real person is the worst outcome this system can produce, and it is a hard
  skip, not a warning.
- **12 a day, ceiling**, regardless of queue depth. Randomised gaps.
- **Email only.** No browser, no LinkedIn, ever.
- **Every send is written to `logs/sent-ledger.csv`** and reported to him. Automatic
  never means invisible — he sees what went out in his name the same day.

### The rule for a future session

**Never switch a lane to `auto` on David's behalf, and never widen `eligible_for_auto`.**
Both are his decisions, made on the board. If outreach is going well and a lane looks
ready, *say so in the brief* and let him flip it. If something goes wrong in an auto
lane, switch it back to `draft` immediately and tell him why — that direction needs no
permission.

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

## Gate 4 — Ask David where he is, never in a terminal

He does not read terminal sessions, and a question asked there is a question never
answered. Anything needing his judgement becomes a row in `state/questions.csv`, which
reaches him on the command centre, in BizDave, and in his morning email. He answers
there; Chief reads it back. See [`DIALOGUE.md`](DIALOGUE.md).

Ask only what he alone can answer. If it could be found in Gmail, the LinkedIn corpus,
`connections.csv` or the repo, it is not a question — it is work not yet done.

## Gate 5 — Never invent

No person, company, title, mutual connection, funding round, prior conversation or
figure that did not come from a tool result. This matters more here than in research
because the invention is about to be **said to the person it is about**. `[UNKNOWN]`
in a brief is fine. `[UNKNOWN]` in an outbound draft means the draft is not ready.

## Gate 6 — Prices are not an agent's to set

The floor is in `docs/company/cre8or-primer.md` and the RetailGTM price book:
$4.24 list, **$3.60 at the 15% ceiling — nothing below it, ever**. An agent may quote
published prices. It may not discount, invent a volume break, or imply flexibility.
Anything below the floor goes to David as a question, not to the prospect as an offer.

## Gate 7 — Publishing is David's

Agents rebuild `pipeline.html` and the artifacts on every run. **An agent may not
publish them.** Publishing puts content in front of people outside the project.

## Gate 8 — The corpus stays home

`voice/corpus/` and `voice/raw/` are David's private correspondence, and they are
gitignored. Only `voice/STYLE.md` — the derived guide, containing quotes he chose to
send — is committed. No agent copies raw mail into a brief, a commit, or an artifact.
