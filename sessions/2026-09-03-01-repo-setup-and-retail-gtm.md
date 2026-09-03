# 2026-09-03 · Session 01 — Repo setup and retail GTM scaffold

## Done

- Created `~/GitHub/` as the local root and cloned `cre8orai/BDAgent` (the repo existed
  but was completely empty — zero commits, and the only repo on the account).
- Set the repo up as a **multi-project** workspace (`projects/<name>/`), since BD was
  described as "one of many" projects.
- Drafted `projects/retail-gtm/` — the indirect motion. Six intermediary segments,
  positioning spine, commercial and operating model frames, playbooks, pipeline stubs.
- Wrote `docs/company/cre8or-primer.md` by reading the internal decks in
  `~/Attachments Cre8or` rather than writing generic GTM material.
- Wrote `docs/ONBOARDING.md` and started this session log.
- Installed browser automation: Node v24 → `~/.local/node`, `playwright-mcp` registered
  as an MCP server against Brave over CDP on port 9222.
- Generated an SSH key, David registered it on GitHub, pushed `main`.

## Decided

- **Retail GTM lives inside BDAgent** as a project folder, not its own repo. Reversible.
- **Markdown is the source of truth**; artifacts get generated from it, never maintained
  in parallel.
- **Research stays separate from strategy**, and unverified claims are marked `[OPEN]` /
  `[ASSUMPTION]` rather than invented. Applied throughout — the strategy is deliberately
  full of gaps rather than plausible-sounding numbers.
- **Browser attaches to David's real Brave profile**, not an isolated one. He chose this
  after being shown it makes every logged-in session actionable.
- **SSH over a personal access token** for GitHub, so no secret passes through chat.

## Open

- **Unit economics at 12 / 500 / 5,000 / 50,000 units** — the blocking unknown. If the
  margin stack only closes at volume, the "start at 12" pitch isn't a business model and
  the strategy changes. David owns this.
- Real lead times; MoCRA responsible-person liability; no reference programme yet.
- "The Cre8or & Agency Revolution" PDF is unread — no PDF text extractor installed, and
  it's directly relevant to agency positioning.
- Browser tools need a Claude Code restart to load; not yet exercised.
- Whether `cre8or_extension` (on the Desktop, six copies) deserves its own repo.

## Next

Research phase — `projects/retail-gtm/01-research/README.md` section A. Those are
answerable from documents and people Cre8or already has, and they unblock everything else.
