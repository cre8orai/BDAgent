# 2026-09-18 · bizDave efficiency review

David asked how to improve bizDave (his Lovable app) and make the whole service cheaper
to run. No code changed. This is the diagnosis and the ranked plan.

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

## Next

1. David reviews the 12 drafts and 5 notifications now sitting in bizDave from 8 Sept.
2. On his go-ahead: replace the print-SQL in `agents/bizdave.py` with a direct Supabase
   write, and put it at the end of `cycle.sh`. Highest leverage, smallest change.
3. Collapse the two inbox queues into one.
4. Build the approve/answer surface in bizDave so the terminal stops being the gate.

Nothing was sent. Gate 1 untouched.
