# 2026-09-18 · bizDave efficiency review

David asked how to improve bizDave (his Lovable app) and make the whole service cheaper
to run, then asked for it as an interactive BD portal — assistant plus CRM, so he can see
where each conversation stands.

**The portal already existed. It was empty.** So the work was not building; it was
connecting. `agents/sync_bizdave.py` now does that, and the pipeline is live in the app.

## Done

Read the live state of the bizDave Supabase database directly (Lovable `query_database`,
which costs no Lovable credits and no model tokens beyond the call itself). Project
`425cdf7c-3348-45f2-a9f7-4176a0a1c808`, workspace `David's Lovable`, published, last
edited 2026-08-15.

Row counts and last-write times, 2026-09-18:

| Table | Rows | Last write | Reading |
|---|---|---|---|
| `leads` | 4,193 | 2026-07-04 | Loaded once, untouched for 10 weeks |
| `contacts` | 1,074 | 2026-07-03 | Same |
| `deals` | 1 | 2026-07-03 | No pipeline in the app |
| `activities` | 3 | 2026-08-15 | Nothing is being logged |
| `reply_radar_drafts` | 18 (**12 `proposed`**) | 2026-09-08 | BDAgent wrote once, 10 days ago |
| `pending_actions` | 8 (**5 `pending`**) | 2026-09-08 | Same batch, unreviewed |
| `inbox_action_items` | 22, all `proposed` | 2026-09-18 04:39 | App's own scan ran today |
| `tasks` | 21 (8 `todo`) | 2026-09-18 04:39 | Half from the scan, half from BDAgent |
| `zoom_meetings` | 119 | 2026-09-18 06:12 | Zoom sync is healthy |
| `updates`, `scheduled_emails` | 0 | — | Built, never used |

## Decided — the four findings

1. **The BDAgent → bizDave bridge has fired exactly once.** `agents/bizdave.py` only
   *prints* SQL; a human has to paste it into the Lovable connector. That is why 12
   drafts have sat at `proposed` since 8 September. The bridge is manual, so it doesn't
   run. Fix: write to Supabase directly from cron. Costs nothing per run.

2. **Two queues are doing the same job.** The app's own inbox scan produces
   `inbox_action_items`; BDAgent's Desk produces `reply_radar_drafts`. Both read the
   same Gmail, both classify it with a model, and David reviews neither because neither
   is the obvious one. This is the actual token burn — the same inbox paid for twice.

3. **The review gate contradicts Gate 4.** `GATES.md` says never ask David in a
   terminal, but `review.sh` *is* a terminal. bizDave is the screen he already opens.
   Approve/Kill/Edit and the `questions.csv` answers belong there.

4. **The CRM half is dead weight.** 4,193 leads, 1 deal, 3 activities. bizDave is
   currently a contact dump with a live inbox bolted on.

## Open

- `[OPEN]` Does David own the domain `bizdave.io`? If yes, point it at the Lovable
  project as a custom domain — free, and it makes the app a real destination.
- `[OPEN]` Should the app's own inbox scan be switched off in favour of Desk, or should
  Desk be retired in favour of the app's scan? One of them has to go. Desk is the better
  candidate to keep — it has the voice guide, the commitment extraction and the gates.
- `[OPEN]` Do the 4,193 leads still matter, or are they archive?
- `[ASSUMPTION]` Writes to `reply_radar_drafts` / `pending_actions` / `tasks` from cron
  are safe to automate. They are display-only rows — nothing in that path transmits —
  but it is still a write to his live app, so it needs his yes first.

## Built — `agents/sync_bizdave.py`

bizDave already has 17 routes (`today`, `deals` + detail, `contacts`, `companies`,
`tasks`, `meetings`, `prospecting`, `compose`, `ask`), an assistant with voice capture
and Telegram, and Zoom + Gmail wired in. Asking Lovable to build a BD portal would have
paid to rebuild what David already owns. The bridge was the missing piece:

| Repo | bizDave |
|---|---|
| `people.csv` + threads-only accounts | `contacts` |
| people + `threads.csv` | `deals` — stage, next step, who is waiting |
| `threads.csv` | `activities` — history on each deal page |
| `commitments.csv` | `tasks` — carrying David's verbatim promised words |
| `questions.csv` | `pending_actions` — Gate 4, answered where he is |

Applied 2026-09-18: **7 deals, 8 contacts, 4 activities, 5 tasks (4 overdue), 4
questions.** Every deal is linked to its contact. `value` and `probability` are NULL
throughout — Gate 5; a number nobody has agreed is not worth showing.

Idempotent by construction: each run deletes its own `BDAgent`-tagged rows before
writing, so re-running cannot double up and rows David created himself are untouched.
Display rows only — no send path, and it cannot grow one.

Two constraints in the app shaped the mapping, both worth knowing for future sessions:
`contacts.category` is restricted to bizDave's own taxonomy (the repo's segment is kept
verbatim in the notes instead), and `contacts.source` accepts only `manual` or
`gmail_import`.

## Later the same day — the tracker turn

David: *"BizDave is not supposed to be something that burns through all of my credits.
This is just something to help me stay on track. I don't need to draft emails for me."*

So the draft-review work is cancelled and `reply_radar_drafts` is legacy. The finding
that settles the credit question: **`user_settings.ai_enabled` has been `false` since
2026-08-15**, and `ai_provider_status` was last checked the same afternoon. bizDave has
not made a model call in a month. **It is not burning credits at runtime — the spend is
Lovable chat turns.** That also explains the frozen queue: `ReplyRadarCard` renders only
when `googleConnected && aiEnabled`, so with AI off it never drew. The drafts were never
ignored; they were invisible.

**Leads reconciled.** Correction to a number stated earlier in this file: 2,107 leads
have no email address, not 540 — the 540 was leads missing *both* company and email.
Matching the no-email leads against contacts by name and LinkedIn URL linked **41** of
them via `leads.contact_id`. The overlap is small, which is itself the answer: these are
genuinely new names, not duplicates of people David knows.

**The GTM picture — and a correction that matters more than anything else here.**

All 4,193 leads were already segmented into 15 `prospect_segments`. My first pass read
the *labels* and reported the reachability split, calling the 1,567-name "Indie and DTC
beauty brands, US" the largest and most on-strategy list and framing the missing emails
as a sourcing decision. **That was wrong, and it was the expensive kind of wrong.** I
described a list I had not opened.

Audited on 2026-09-18 by reading the rows:

| Segment | Leads | Email | What is actually in it |
|---|---|---|---|
| Indie and DTC beauty brands, US | 1,567 | 0 | **Scrape residue.** 7 beauty companies. 373 at twenty named mega-caps. 427 large-cap CEOs and chairs — Nadella, Fink, Dell, Bill Gates. ~half not US. Every LinkedIn value an obfuscated `ACoAA` member id |
| Israel beauty directors and VPs | 1,000 | 1,000 | **Mislabelled.** Companies are disney.com, oracle.com, theatlantic.com. 7 beauty, few Israeli |
| US cosmetics manufacturers and co-packers | 300 | 300 | On-label. 69 beauty companies. But co-packers compete with Cre8or's own factories as often as they partner |
| RPG decision makers | 286 | 286 | On-label; promotional products and signage, not beauty |
| Beauty decision makers | 150 | 150 | On-label. 48 beauty companies |
| Agency decision makers | 150 | 150 | On-label. Agencies assemble brands and outsource making — the Front Row pattern |
| Israel beauty and wellness | 87 | 87 | **Best list in the database.** Ahava Dead Sea Laboratories, Spa Cosmetics, Aviv Scientific |
| Israel beauty owners | 67 | 67 | Mixed; several bare domains |
| US cosmetics and packaging | 46 | 46 | Thin, mostly one company |
| Founders / BD partnerships | 40 | 0 | All 40 already Contacts |
| Israel beauty founders | 500 | 0 | Not re-audited — assume the same doubt as the other no-email list |
| 4 starter templates | 0 | — | Never populated |

**So roughly 2,567 of 4,193 rows — 61% — are in the two segments whose labels do not
describe their contents, and those were the two I recommended.** The genuinely workable
list is far smaller and better: about 490 names across Beauty decision makers, Agency
decision makers, Israel beauty and wellness, and the co-packers, plus 40 warm ones he
already knows.

A methodological note worth keeping: the audit itself produced a false positive first.
Searching titles for `hair` matched **Chair**man, which briefly made 88 Fortune 500 CEOs
look like beauty contacts. Word boundaries matter when the answer is a business decision.

Each segment now carries its audited reading in `notes`, visible on the Prospecting
screen. The two bad lists are marked **DO NOT WORK THIS LIST** and **LABEL DOES NOT MATCH
CONTENTS** so the label cannot mislead a future session the way it misled this one.

## The build — shipped

`mcp__Lovable__send_message` returned late in the session and the three tracker cards were
built in **one agent turn** (commit `be4d74f9`): `today-triage.tsx` (Late / Waiting on you
/ Waiting on them plus the Needs-you card) and `deal-channels-card.tsx`, wired into
`today.tsx`, `dashboard.tsx` and `deals.index.tsx`.

**Correction to this file.** It said earlier that deal values and probabilities were left
NULL per Gate 5. That was wrong. `deals.probability` was `NOT NULL` with a **column default
of 10**, so omitting it did not produce NULL — it stamped an unassessed 10% on all seven
deals. The schema had nowhere to record "unknown". Fixed at the root: default dropped,
column made nullable, the seven set to NULL, and the app now renders NULL as "—".

The build found a second invented-number source nobody had flagged: `probabilityForStage()`
in `voice-command-fab.tsx` auto-assigned a probability from the deal stage. Removed, along
with the hardcoded `probability: 10` in `promoteLead`.

Reviewed the diff rather than trusting it. Nothing was gated behind `aiEnabled`, no send
path appeared, and the one weighted-pipeline line in the diff is pre-existing — the agent
only made it null-safe, which it had to once the column became nullable.

**Verified by running the cards' own queries.** They populate correctly, and doing so
surfaced two of David's own tasks late for a month: Nick Cannon / Wild N Out materials (33
days) and the bank paperwork for Gidi's account access (29 days). Four tasks from the 8 Sept
run were superseded duplicates and are closed with a note saying so.

**Still open:** with every `value` NULL, the pre-existing weighted-pipeline figure on Today
renders as **$0**, which reads as "no pipeline" rather than "not yet valued". Cosmetic, and
one more agent turn to fix — David's call whether that is worth a credit.

## Next

1. **David: the four questions and five overdue commitments are in bizDave now.** Nate
   Cooper's materials are 11 days late and Avery Schwartz started without an address.
2. Set `BIZDAVE_DB_URL` (the Supabase connection string) so `cycle.sh` runs the sync
   unattended. Until then it prints SQL and changes nothing.
3. Build the three tracker cards — see `docs/bizdave-build-brief.md`. Blocked here:
   `mcp__Lovable__send_message` was unavailable for most of this session, and it is the
   only way to change the app's code. The brief is one paste-ready message.
4. `[OPEN]` Where did the two bad lists come from? Both are `source='vibe'`, imported
   2026-07-04. If that import tool produced 2,567 rows that do not match their requested
   filters, that is worth knowing before buying more data from it.
5. `[OPEN]` Work the 87-name Israel beauty and wellness list first? It is small, all
   emailed, and genuinely on-label — the opposite of the lists volume suggested.
5. `[OPEN]` `promoteLead` writes `probability: 10` onto every new deal. That is an
   invented number reaching a screen David reads. Worth removing.

Nothing was sent. Gate 1 untouched.
