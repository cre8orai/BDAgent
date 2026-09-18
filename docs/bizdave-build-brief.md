# bizDave build brief — the tracker

One message to paste into the Lovable chat for
[bizDave](https://lovable.dev/projects/425cdf7c-3348-45f2-a9f7-4176a0a1c808).

One message is deliberate. Lovable charges per agent turn, so a complete brief that
lands in one pass costs less than five rounds of refinement. **This is where David's
credits actually go** — the running app costs nothing.

## What changed, and why this brief replaces the last one

David, 2026-09-18: *"BizDave is not supposed to be something that burns through all of
my credits. This is just something to help me stay on track. I don't need to draft
emails for me — I'll do that all individually."*

So the draft-review surface briefed earlier is **cancelled**. `reply_radar_drafts` is
legacy; nothing should be built for it.

## The finding that makes this cheap

`user_settings.ai_enabled` has been **false** since 2026-08-15, and `ai_provider_status`
was last checked the same afternoon. **bizDave has not made a model call in a month.**
It is not burning credits at runtime, and it should never start.

That also explains the frozen queue: `ReplyRadarCard` renders only when
`googleConnected && aiEnabled`, so with AI off it never drew. The twelve drafts were not
ignored — they were invisible. Which no longer matters, because drafting is out.

**The rule this sets: every number on every screen comes from a SQL query, never a
model.** A view that groups, sorts, counts and flags is free and runs forever. A model
call costs on every page load. Nothing below needs AI.

---

## The message to paste

> Three changes. All are plain database reads against tables that already exist — no new
> tables, no migrations, no integrations, and **no AI calls of any kind**. `ai_enabled`
> is false and stays false, so nothing may be gated behind it or depend on it.
>
> **1. Rebuild the top of the Today screen as three columns: Late / You / Them.**
>
> Scope every query to the signed-in `user_id`.
>
> - **Late** — `tasks` where `status='todo'` and `due_date < current_date`, plus `deals`
>   where `status='open'` and `next_step_date < current_date`. Sort oldest first and show
>   how many days over, as a red badge reading e.g. "11 days late".
> - **Waiting on you** — `deals` where `status='open'` and `waiting_until` is null and
>   `next_step_date >= current_date`. These are his move.
> - **Waiting on them** — `deals` where `status='open'` and `waiting_until >= current_date`.
>   Show the date. He is not blocked on these; they are here so nothing goes quiet.
>
> Each row shows the deal or task title, the company, and `next_step` (or the task
> description's first line), and links to the deal detail page. Keep rows to two lines.
> The whole point is that he can read this in ten seconds and know what today is.
>
> **2. Add a "Needs you" card directly under that.**
>
> Nothing in the app reads `pending_actions`, so rows written there are invisible.
>
> List `pending_actions` where `status='pending'` and `expires_at` is in the future,
> newest first, scoped to the user. Show `summary`, plus a small muted line with
> `payload->>'agent'` when present.
>
> Each row gets a textarea and a **Save answer** button. Saving writes the text into
> `payload` under an `answer` key, sets an `answered_at` key inside the same payload, and
> sets `status='done'`. No email, no generation — the answer is read back from the
> database by an external process. Title it "Needs you" with a count badge. Empty state:
> "Nothing waiting on your decision."
>
> **3. Add a Channels card to the Deals page.**
>
> `deals.source` carries the go-to-market channel after the colon — values look like
> `BDAgent:brand-operator`, `BDAgent:investor`, `BDAgent:beauty-platform`,
> `BDAgent:creator-platform`. Treat the part after the colon as the channel, and group
> anything without one as "Direct".
>
> For each channel show: number of open deals, how many are late (`next_step_date <
> current_date`), and the date of the oldest `last_activity_at`. Sort by open deals
> descending. Clicking a channel filters the deals list to it.
>
> This is the only GTM view he needs in the app: which motion is actually moving, and
> which has gone quiet. Do not add charts, forecasts, weighted values or projections —
> deal values are deliberately empty and must not be estimated or defaulted.
>
> **Constraints for all three:** match existing card, badge and button styling exactly;
> do not restyle anything else; do not touch other routes; do not add any AI, model,
> summarisation or "ask" feature; do not add a Send button anywhere.

---

## After it builds

1. The three columns reconcile with the database — Nate Cooper's materials should show
   as the oldest late item.
2. An answer saved under "Needs you" comes back in `payload->>'answer'`.
3. The Channels card totals match the number of open deals.

Then: **stop sending build messages.** The app is a tracker. New information arrives by
`agents/sync_bizdave.py` writing rows, which costs nothing. A build message should only
ever be needed when the *shape* of the screen is wrong, not when the data changes.
