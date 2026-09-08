# The dialogue

**The agents do not just report to David. They talk to him, and he talks back.**

This is the half that was missing when the repo was first built. It had a clean
one-way pipe — agents draft, David approves — and no way for an agent to *ask* him
anything, or for him to direct an agent from where he actually works. Everything ended
up as questions in a terminal, which is the wrong place for all of it.

> **Never ask David a question in a terminal session.** He is not there. Raise it as a
> row in `state/questions.csv`, and it reaches him on the board, in BizDave, and in his
> morning email. He answers where he is, and the answer comes back to the agents.

---

## Where each thing goes

| Surface | What it is for | Who writes it |
|---|---|---|
| **[The command centre](https://claude.ai/code/artifact/a996dabf-6c6d-46ee-82a5-99a5b0e62e23)** | Where David actually decides. Answers questions, approves/kills/returns drafts, directs any agent | `build_dashboard.py`; David's replies go to the artifact's own store |
| **BizDave** | His existing daily surface — the notification lands where he already looks | `bizdave.py` |
| **His email** | The morning brief. One message, ordered by what he'd regret missing | Chief |
| **`state/questions.csv`** | The queue an agent writes to when it is blocked | any agent |
| **A terminal** | Nothing. Never a question | — |

---

## Raising a question

Any agent may. Append to `state/questions.csv`:

```
id,asked_at,agent,about,question,why_it_matters,blocking,answered_at,answer
```

- **`question`** — one sentence, answerable without opening anything else.
- **`why_it_matters`** — what you already tried, and what changes depending on his
  answer. This is the field that decides whether he answers today or in a week. Write
  it as if he has thirty seconds and no memory of the thread.
- **`blocking`** — the outbox row this holds up, if any. A blocked draft is shown to him
  greyed with the question above it, so he sees the cost of not answering.

**Ask only what he alone can answer.** Anything you could find by searching Gmail, the
LinkedIn corpus, `connections.csv`, or the repo is not a question — it is work you
have not done. Four open questions is a healthy queue; fifteen means the agents are
delegating their job back to him.

**Never invent an answer to an unanswered question.** If a fact is `[UNKNOWN]` and it
matters, the draft waits. The Ralph Azrak draft is the worked example: nothing in Gmail
or LinkedIn shows the clinical documentation going out — but **WhatsApp is invisible to
every agent here**, so the honest position is a question to David, not an accusation
that he dropped it.

---

## Reading his answers back

His decisions live in the command centre's own store, not in this repo. Chief pulls them
at the start of every run using the Artifact tool's `read_db` action against
`https://claude.ai/code/artifact/a996dabf-6c6d-46ee-82a5-99a5b0e62e23`:

| Collection | Shape | What to do with it |
|---|---|---|
| `answers` | `{questionId, text, at}` | Write `answer` and `answered_at` into `questions.csv`. Then **act on it** — unblock the draft, correct it, or drop it |
| `decisions` | `{draftId, verdict, note, at}` | `approve` → outbox `status=approved`. `kill` → `killed`. `edit` → back to `draft` with his note in `notes`, and the owning agent rewrites it |
| `directives` | `{agent, text, at, status}` | A standing instruction to one agent. Apply it, record it in that agent's log, and mark it `done` |
| `settings/autonomy` | `{lanes: {lane: "draft"\|"auto"}, at}` | Write each mode into `state/autonomy.csv`. **Only for lanes whose `eligible_for_auto` is `yes`** — ignore any other, even if present |

**His answer is the fact from then on.** Put it in the repo so no future run re-asks it,
and never re-open a question he has already settled.

**A `kill` is information, not just a no.** Three kills in a row from one agent means its
targeting or its voice is wrong — say so in the daily brief rather than queueing a
fourth.

---

## What runs without asking

He was explicit: *"automate everything under me, so that I get updates, I can act on
them, and I can make decisions as to whether or not they should be executed. Only
certain things run on automatic."*

**Automatic, no permission needed:**

- Sweeping the inbox, classifying it, extracting commitments
- Sourcing people, scoring accounts, building briefs
- Reading the LinkedIn corpus and the connection graph
- Writing drafts, computing cadence, rebuilding the board
- Raising questions, and telling him there is something to look at

**Automatic only when he has switched that lane on** — see GATES gate 1:

- `prospecting-email` and `followup-email` are eligible. Both ship as `draft`
- He flips them on the board when he is comfortable with what the agents write
- Every send is logged to `logs/sent-ledger.csv` and reported to him the same day.
  **Automatic never means invisible**

**Never automatic, whatever any setting says:**

- `reply-email`, `linkedin`, `commercial` — not eligible, and two checks enforce it
- A message containing a `[placeholder]` or `[UNKNOWN]`. Hard skip
- Publishing an artifact
- Answering a question he has been asked
- Overriding a decision he has already made
- **Switching a lane on for him.** Suggest it in the brief; the flip is his

### Earning the switch

He said *"until I get comfortable with the content and how the outreach is being done."*
That is a judgement he makes from evidence, so give him the evidence: the board shows,
per lane, how many drafts he has decided on and how many he approved versus killed. A
lane with two decisions is not a track record. When one has a real run of approvals,
**say so in the brief and let him decide** — never flip it yourself.

A run of kills is the more useful signal: three in a row means the targeting or the
voice is wrong, and that belongs in the brief before a fourth draft is written.

**Email to David himself is not "sending".** The morning brief goes to
`david@cre8orglobal.com` and needs no approval — he asked for it, and it is a report,
not outreach.

**The check before any message leaves**, in order:

1. Is the recipient David? → go.
2. Otherwise: is this row's lane set to `auto` **and** eligible? → `autosend.sh` may go.
3. Otherwise → a Gmail draft, and he presses Send.

If you cannot answer 2 from `state/autonomy.csv` without guessing, the answer is 3.
