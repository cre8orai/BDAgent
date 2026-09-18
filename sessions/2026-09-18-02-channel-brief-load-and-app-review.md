# 2026-09-18 · Channel Brief into bizDave, and an app review

Two asks from David: get the Channel Brief (17 segments, 875 accounts, 1,462 contacts)
into bizDave's backend, and review the Lovable app to make it more professional and
functional. GitHub write access was also fixed mid-session; the 11 unpushed commits went up.

## Done

**The load, and why the first pass was short.** The previous session's CSV import stopped
at 951 contacts and 712 companies. Root cause was not the CSV: both files were valid RFC
4180 (segment names such as "Event planners, venues, platforms & associations" are quoted
correctly). The Lovable agent had deduplicated the contacts against *every* lead in the
table, and **509 of the 1,462 Channel Brief contacts already existed as `source='vibe'`
rows** — the same people, in the mislabelled lists audited in session 01. It skipped them.
The 163 "missing" companies likewise already existed from the domain-derived
`[BDAgent]` import.

Finished it directly against the database with `query_database` (no Lovable credits):

| What | Before | After | Note |
|---|---|---|---|
| `leads` with `source='channel-brief'` | 952 | **1,461** | 1,357 distinct emails + 104 with no email = every unique row in the CSV |
| … linked to a segment | all | all | 16 of 17 segments have contacts; "Corporate gifting platforms" has accounts only |
| `companies` carrying a `[Channel Brief]` line | 712 | **899** | 187 existing BDAgent companies had the segment / signal / gap / motion appended to their notes rather than being duplicated |

Every insert was idempotent (`NOT EXISTS` on lower-cased email, or name + company where
there is no email), so re-running any batch is safe. The one Lovable build message spent
on the load did a delete-and-reload of its own first; the final counts above are verified
by query, not by the agent's report.

Fixed CSVs and the SQL batches are in the session scratchpad only — they carry 1,357
personal email addresses and do not belong in git.

**App review — sent as one build turn** (message `umsg_01m2t4xnssffvsza4b30y7wcn3`).
Read every route that matters before writing it. What was wrong, and what the brief asks
for:

- *Today* had two calendar cards (a seven-day timeline and a today-only Google list), a
  "Tasks due" card repeating the Late column, a stat strip counting lifetime Zoom meetings
  and Google tasks, an unused `PipelineCard`, and "Inbox zero. Enjoy it." copy that the
  project knowledge explicitly forbids. Brief: one calendar, stat strip = Late / Waiting on
  you / Needs you / Awaiting reply from a shared hook, Needs you above the calendar.
- *Overview* showed **$0 weighted pipeline** (every value is NULL by design) and a
  "Contacts" stat with a won/lost hint. Brief: "—" with "No deal values entered"; bars by
  count when there is no value; tokens instead of rose/emerald/indigo/amber.
- *Companies* rendered 1,769 rows as one flat list. Brief: parse the Channel Brief line
  into segment / signal / gap / motion, chip + filter on the index, a Leads card on the
  detail page, 60 rows at a time. Also a real bug: the deals query built a PostgREST
  filter string from the company name, which breaks on "IZEA Worldwide, Inc.".
- *Prospecting* did **not** show `prospect_segments.notes` on the cards — so the
  "DO NOT WORK THIS LIST" flags written in session 01 were invisible. Session 01's log said
  they were visible; it was wrong. Brief: show the first line, red-rail the flagged ones.
- H1 sizes ranged from 2xl to 4xl across pages; standardised.

## Decided

- Do not delete the 509 vibe duplicates of Channel Brief contacts. The channel-brief row
  is the better one (correct segment, verification flag) but the vibe row is what the
  earlier audit notes point at. Both stay; `[OPEN]` below.
- Existing companies get the Channel Brief line *appended*, not a second row. One company,
  one page.
- Data work goes through `query_database`, not the Lovable agent. The agent's load cost
  1.4 credits and reported "done" on a partial result; SQL costs nothing and can be
  verified with a count.

## Open

- `[OPEN]` 509 people exist twice in `leads` (vibe + channel-brief). Merge or leave?
  Leaving is harmless for the segment view; merging needs a rule for which row wins.
- `[OPEN]` "Corporate gifting platforms" has 56 accounts and no contacts. Enrich, or
  work it at company level?
- `[OPEN]` Should `channel_accounts.csv` (no PII — company, segment, signal, gap,
  motion) live in `01-research/`? It is the sourced account list behind the segment
  strategy and currently exists only in the artifact and the bizDave database.
- `[OPEN]` LinkedIn company pages for the 875 accounts are still not populated. Needs a
  tool choice (SuperClaud `company_search` vs Vibe `enrich-business`) and a budget.

## Next

1. Verify the build diff (`get_diff` on the message above) — nothing gated behind
   `aiEnabled`, no send path, tokens only — and republish.
2. David: open Prospecting, confirm the red-railed segments read correctly.
3. Pick the LinkedIn enrichment tool.

Nothing was sent. Gate 1 untouched.
