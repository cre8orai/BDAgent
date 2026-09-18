# bizDave build brief — the review surface

Paste the block below into the Lovable chat for
[bizDave](https://lovable.dev/projects/425cdf7c-3348-45f2-a9f7-4176a0a1c808).

It is one message, deliberately. Lovable charges per agent turn, so a complete brief
that lands in one pass costs less than five rounds of refinement.

## Why this and not something else

`GATES.md` gate 4 says never ask David in a terminal, because a question asked there is
a question never answered. But `agents/review.sh` **is** a terminal. That contradiction
is why twelve drafts sat at `proposed` for ten days.

Two specific things are missing in the app, both verified against the live code and
database on 2026-09-18:

1. **`reply_radar_drafts.draft_subject` and `draft_body` are never displayed.**
   `ReplyRadarCard` in `src/routes/_authenticated/today.tsx` renders `from_name`,
   `subject`, `snippet` and `reason`, and offers exactly two actions — "Reply in Gmail"
   (an outbound link) and "Dismiss". The draft written in David's voice is invisible.
2. **`pending_actions` has no UI anywhere.** There is no `pending-actions` module in
   `src/lib/` and no reference in `today.tsx`. Rows written there — including every
   question an agent needs David to answer — are never seen by anyone.

The card is also gated behind `googleConnected && aiEnabled`, so if either flag drops,
the queue disappears rather than degrading.

## The gate this must not break

**Approve means `status='approved'`. It must never send.** `draft.sh` turns approved
rows into Gmail drafts that wait in David's Gmail until he presses Send himself. If the
build adds a Send button, it has broken the rule the whole system rests on — see
`agents/GATES.md` gate 1.

---

## The message to paste

> Two changes to the Today screen. Both are read/write against tables that already
> exist — no new tables, no migrations, no new integrations.
>
> **1. Make Reply Radar a draft review queue.**
>
> `ReplyRadarCard` in `src/routes/_authenticated/today.tsx` currently shows only the
> sender, subject and snippet. The `reply_radar_drafts` table also holds `draft_subject`
> and `draft_body` — a reply already composed — and those are never shown.
>
> For any row where `draft_body` is not null, show the draft body in a collapsible block
> (collapsed to about four lines, expandable), and add three actions:
>
> - **Approve** — sets `status = 'approved'`. Nothing else. After it saves, show a toast
>   reading "Approved. Run draft.sh to put it in your Gmail." **Do not send the email, do
>   not call Gmail, do not add a Send button anywhere.** An external script turns approved
>   rows into Gmail drafts that wait for him to press Send. This is a hard rule.
> - **Edit** — opens the `draft_body` and `draft_subject` in a textarea, saves back to the
>   same row, leaves `status` at `proposed`.
> - **Kill** — sets `status = 'dismissed'` (keep the existing Dismiss behaviour).
>
> Keep "Reply in Gmail" for rows that have no `draft_body`.
>
> If `reason` starts with "BDAgent", show it as a small muted badge so he can see the
> draft came from the agent rather than the inbox scan. A row whose `subject` begins
> "[LinkedIn" cannot be emailed — for those, replace Approve with a **Copy** button that
> copies `draft_body` to the clipboard, and label it "Paste into LinkedIn yourself".
>
> Finally, this card is currently rendered only when `googleConnected && aiEnabled`.
> Change it so the card still renders when there are rows with a `draft_body`, even if
> those flags are false — the drafts come from outside the app and do not depend on
> either. Show the existing empty state when there is genuinely nothing.
>
> **2. Add a "Needs you" card above Reply Radar.**
>
> Nothing in the app reads `pending_actions`, so rows written there are invisible.
>
> Add a card listing `pending_actions` where `status = 'pending'` and `expires_at` is in
> the future, newest first, scoped to the signed-in user. For each row show `summary`,
> and a small muted line with `payload->>'agent'` when present.
>
> Each row gets a textarea and a **Save answer** button. Saving writes the text into
> `payload` as an `answer` key, sets `answered_at` to now inside the same payload, and
> sets `status = 'done'`. Nothing is sent and no email is generated — the answer is read
> back from the database by an external agent.
>
> Title the card "Needs you" with a count badge. Empty state: "Nothing waiting on your
> decision." Give it the same visual weight as Reply Radar — these are the questions
> blocking work.
>
> Match the existing card, badge and button styling exactly. Do not restyle anything else
> on the page, and do not touch any other route.

---

## After it builds

Check three things before trusting it:

1. The twelve rows at `status='proposed'` appear with their draft text visible.
2. Approve changes the status and **no mail leaves**. Confirm the Gmail Sent folder is
   untouched.
3. The four questions appear under "Needs you", and an answer written there comes back in
   `payload->>'answer'`.

Then update `agents/review.sh` to point at the app rather than the terminal, and record
the change in `sessions/`.
