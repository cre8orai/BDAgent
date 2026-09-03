# BDAgent

Business development workspace for **Cre8or** — strategy, research, and go-to-market
work products, versioned so they can be revisited, diffed, and reused.

This repo holds multiple projects. Each lives under `projects/<name>/` and is
self-contained: brief, research, strategy, playbooks, and published artifacts.

## Projects

| Project | Status | Description |
|---|---|---|
| [`retail-gtm`](projects/retail-gtm/) | 🟡 Scaffolded — research next | Retail / indirect go-to-market: selling *through* agencies, licensors, and merch aggregators who build product lines for their own clients. |

## Shared context

- [`docs/company/cre8or-primer.md`](docs/company/cre8or-primer.md) — what Cre8or is,
  what it sells, and the capabilities every GTM argument rests on. Read this first.

## Conventions

- Markdown is the source of truth. Decks and visual artifacts are *generated from* it.
- One idea per file. Prefer many small files over one long document.
- Anything asserted about a market, a partner, or a number carries a source
  (see each project's `01-research/sources.md`). Unsourced claims are marked `[ASSUMPTION]`.
- Status markers: 🟢 done · 🟡 in progress · ⚪ not started · 🔴 blocked

See [`CLAUDE.md`](CLAUDE.md) for how AI sessions should work in this repo.
