# The gates

Read this before writing or changing any runner. These are not preferences.

## Gate 1 — Nothing sends itself

**No agent has a send tool. Ever.** Agents write rows to `state/outbox.csv` with
`status=draft`. The only code that transmits is `send.sh`, it runs in the foreground,
a human starts it, and it processes **only rows David has flipped to `approved`**.

Three separate reasons, any one of which is sufficient:

1. **Domain reputation.** Auto-sent cold email burns `cre8orglobal.com` faster than any
   pipeline can rebuild it. Once Google classifies the domain, every real conversation
   in the inbox degrades too.
2. **LinkedIn's User Agreement prohibits automated messaging** (§8.2). Enforcement is
   account restriction or permanent ban, and David's LinkedIn is a 20-year asset —
   the warm paths in `state/people.csv` mostly run through it. Losing it costs more
   than any campaign it could run.
3. **It is his name on it.** An agent sending in David's name without David reading it
   is a person he has never met receiving a promise he never made.

## Gate 2 — LinkedIn is hand-paced, always

Even for approved rows:

| Limit | Value | Why |
|---|---|---|
| Messages per session | **8** | Above ~10–15/day LinkedIn's automation heuristics engage |
| Gap between sends | **40–90s, randomised** | Fixed intervals are the signal that gets caught |
| Sessions per day | **1** | |
| Connection requests/week | **20** | Well under the ~100 cap; acceptance rate matters more |
| On any CAPTCHA, checkpoint, or "unusual activity" | **STOP the run, do not retry, tell David** | Retrying is what converts a warning into a restriction |

`send.sh` enforces these in code, not in a prompt. A prompt cannot be relied on to
count.

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
