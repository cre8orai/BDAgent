# Onboarding brief

Read this first — whether you're a new person joining the work or a fresh AI session
picking it up cold. It should take five minutes and leave you able to contribute.

## What this repo is

The business development workspace for **Cre8or**. Strategy, research, and go-to-market
work products, versioned so decisions are traceable and reusable. Not code.

It holds multiple projects under `projects/`. Today there is one: `retail-gtm`.

## What Cre8or is (the 30-second version)

A vertically integrated beauty and personal-care manufacturer with an AI operating system
attached. Cre8or **owns its factories** and built Cre8orOS to connect the factory floor to
the point of sale.

The differentiator, and the basis of every argument in this repo:

> On-demand production from **12 units to 50,000**, same supplier, with reorder volume
> driven by live POS data instead of a forecast made a quarter earlier.

Generic "we help beauty brands grow" positioning is wrong and will be rejected. The full
picture is in [`company/cre8or-primer.md`](company/cre8or-primer.md).

## What we're working on

**`projects/retail-gtm`** — the indirect motion. Cre8or's direct sales approach reaches
one brand owner at a time. This project designs how we sell *to* agencies, licensors and
merch aggregators, so that *they* build Cre8or-made product lines for their own clients.

The canonical deal shape: Fanatics buys from Cre8or and stands up a Taylor Swift beauty
line for a stadium tour. Cre8or never touches the artist; Fanatics never touches a factory.
Tours have hard dates and unknowable per-city demand, which is exactly the inventory bet
the 12-to-50,000 model removes.

Six intermediary segments are mapped in
[`../projects/retail-gtm/00-brief/channel-model.md`](../projects/retail-gtm/00-brief/channel-model.md).

## Where things live

```
docs/company/       what Cre8or is — shared factual base
projects/<name>/
  00-brief/         charter and the model being proposed
  01-research/      what's true, with sources
  02-strategy/      what we decided to do about it
  03-playbooks/     how the team executes
  04-artifacts/     published decks and pages
  05-pipeline/      named targets
sessions/           a log per working session — see sessions/README.md
```

## The state of play, honestly

The strategy is **structurally complete and factually unfinished**. The segment map,
positioning spine and operating model are drafted. The numbers underneath them are not.

Blocking unknowns, all marked `[OPEN]` in the files:

- **Unit economics at 12 / 500 / 5,000 / 50,000 units.** The single most important gap.
  If the margin stack only closes at high volume, "start at 12" is a demo feature rather
  than a business model, and the strategy changes.
- **Real lead times** — concept to first shipment, reorder to restock.
- **MoCRA liability** — who is the responsible person when product ships under a third
  party's brand. Most likely reason a licensing deal dies.
- **No reference programme yet.** Every partner asks "who else have you done this for?"
  on the first call. There is currently no answer.

These are answerable from documents and people Cre8or already has. See
[`../projects/retail-gtm/01-research/README.md`](../projects/retail-gtm/01-research/README.md),
section A.

## Source material not in this repo

Primary Cre8or documents live in `~/Attachments Cre8or` — Cre8orOS decks, "Logic to
Cre8orOS", "The Problem We Solve", "Cre8or & Aggregators", "The Cre8or & Agency
Revolution", partner decks.

`.docx` reads via `textutil -convert txt -stdout <file>`. **No PDF text extractor is
installed**, so the PDFs there are currently unread — including "The Cre8or & Agency
Revolution", which is directly relevant to agency positioning.

## How to work here

See [`../CLAUDE.md`](../CLAUDE.md). The short version: markdown is the source of truth,
research stays separate from strategy, and anything unverified is marked rather than
quietly invented.

**Log your session** in `sessions/` before you finish.
