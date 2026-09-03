# Working notes for AI sessions

## What this repo is

Business development workspace for Cre8or. Not code — strategy, research, and
GTM work products. Optimise for a human reading these files in six months and
still being able to tell what was known, what was assumed, and what was decided.

## Ground rules

1. **Read `docs/company/cre8or-primer.md` before writing any GTM argument.**
   Cre8or's differentiation is specific (on-demand beauty manufacturing, 12–50,000
   unit runs, owned factories, POS-connected inventory OS). Generic "we help brands
   grow" positioning is wrong and will be rejected.

2. **Separate research from strategy.** `01-research/` holds what is true, with
   sources. `02-strategy/` holds what we've decided to do about it. Never let an
   inference drift into the research folder unsourced.

3. **Mark unknowns.** Use `[ASSUMPTION]` inline for anything not verified, and
   `[OPEN]` for questions that need David's input. Don't quietly invent numbers —
   margins, MOQs, lead times, and partner economics are all things we either know
   or must ask.

4. **Every claim about a partner gets a file** in `01-research/partners/`, named
   after the company, with a source log at the bottom.

5. **Artifacts are generated, never hand-maintained twice.** If a deck or page is
   published, record its URL and its source file in `04-artifacts/README.md`.
   Update the markdown, then regenerate — don't edit the artifact and let the repo
   drift.

6. **Commit meaningful units of work** with a message that says what changed and why.

## Voice

Direct, commercial, specific. Written for people who buy and sell for a living.
No filler, no adjectives doing the work that numbers should do.

## Session logging

Every working session gets a file in `sessions/` — what changed, what was decided, what's
still open, what's next. Add a row to the table in `sessions/README.md`. Write it before
finishing, not from memory later.
