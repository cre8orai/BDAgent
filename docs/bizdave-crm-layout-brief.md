# bizDave — CRM-grade layout brief

Sent to the Lovable agent 2026-09-18 as the second build turn of the day. David's words:
*"It really needs to look professional like a Salesforce type of an environment or even
HubSpot type of an environment. Layout graphics."* Colour scheme stays.

This is layout, presentation and client-side aggregation only. Every existing dialog,
mutation, server function and integration stays as it is.

---

Make the app read like a modern CRM (HubSpot / Salesforce Lightning): dense data tables
with sortable columns and paging, record pages with a header band and side panels, a
pipeline board, KPI tiles with small charts, one consistent page header. Keep the existing
warm palette and tokens in `src/styles.css` exactly — no tailwind palette colours, no
shadows, no new dependencies (recharts and shadcn Table are already installed), no schema
changes, no AI, no send path, no invented numbers. Project knowledge applies throughout.
Empty states say what is true.

## 1. Shell

- Add a sticky top bar (h-12, `bg-card`, `border-b`) above the content on every
  authenticated page. Left: breadcrumb — section › page › record name (e.g. *Work › Deals
  › Front Row*). Centre: a search field that opens the existing command palette on focus
  or click, placeholder "Search contacts, companies, deals — ⌘K". Right: the existing
  QuickAddMenu as a "+ New" button, then the AI on/off indicator moved here from the
  sidebar footer.
- Sidebar: remove the "Quick jump" button (now in the top bar) and the AI indicator.
  Keep sections and items as they are. Sign out stays in the footer.
- Content container: `max-w-[1400px]`, `px-6 py-5`.
- `src/components/crm/page-header.tsx`: title (`text-xl font-semibold tracking-tight`),
  optional count pill, subtitle (`text-sm text-muted-foreground`), right-aligned actions.
  Every list page uses it.

## 2. Reusable primitives — `src/components/crm/`

- `data-table.tsx`: built on `ui/table`. Props: `columns` (`{ key, label, width?,
  sortable?, align?, render }`), `rows`, `rowKey`, `onRowClick`, `pageSize` (default 50),
  `selectable?` with `selected`/`onToggle`. Sticky header, click-to-sort with a caret,
  dense rows (`h-10 text-[13px]`), hover `bg-secondary/40`, pager reading "1–50 of 1,769"
  with previous / next. Hand-rolled — do not add TanStack Table. Wrap in
  `overflow-x-auto` so it scrolls on narrow screens.
- `filter-bar.tsx`: search input, zero or more `Select` filters, active-filter chips with
  a clear button, result count at the right.
- `kpi-tile.tsx`: label, value, optional delta text (only when computed from data, e.g.
  "+3 vs last week"), optional 8-point sparkline (recharts `LineChart`, 40px high, stroke
  `var(--chart-1)`, no axes, no tooltip), whole tile clickable.
- `record-header.tsx`: initials avatar (`rounded-md bg-secondary`, two letters),
  eyebrow (record type), title, meta line, chips, actions on the right.
- `property-list.tsx`: two-column key/value list (label `text-[12px]
  text-muted-foreground`, value `text-[13px]`), "—" for null.
- `empty-state.tsx`: icon, one line, optional action.
- `initials.ts`: helper for the avatar letters.

## 3. Today

- KPI row: four `KpiTile`s — Late, Waiting on you, Needs you, Awaiting reply — from the
  shared triage hook. No sparklines here (no history exists for these counts).
- Below the triage columns, a two-column layout at `lg` and up: left two-thirds = Needs
  you, Awaiting your reply, Tasks due; right one-third (sticky, `top-16`) = Next seven
  days, then Meetings. Stacks on narrow screens.

## 4. Overview

- KPI row, six tiles: Open deals, Late items, Contacts, Companies, Leads, Tasks completed
  this week. Sparklines only where history exists: tasks completed per week (from
  `updated_at` where status = done), deals activity per week (`last_activity_at`),
  activities per week (`activities.created_at`). Others render without a sparkline.
- Charts, using `ui/chart` with `--chart-1..5`, two per row:
  1. Open deals by channel — horizontal bar (channel from `deals.source` suffix).
  2. Leads by segment — horizontal bar, top 10 segments by count.
  3. Activity per week, last 12 weeks — bar: activities + tasks completed.
  4. Lead status — horizontal bar over new / contacted / replied / qualified / promoted.
- Two tables below: Stale deals (no activity 14+ days) and Late tasks, both `DataTable`.

## 5. Deals

- View toggle Table | Board (persist in `localStorage`).
- Table columns: Deal, Company, Channel, Status, Next step, Next date (late in
  `--priority-high`), Waiting until, Last activity, Value ("—" when null, never 0).
- Board: one column per channel (Direct plus each `BDAgent:` suffix present), cards
  showing name, company, next step and date, a "late" chip. Column header shows open
  count and late count. Clicking a card opens the deal.
- FilterBar: status, channel, "late only".

## 6. Contacts

- Replace the card grid with a `DataTable`: Name (avatar initials + name, title beneath
  in muted), Company, Category (the existing inline Select), Email, Last interaction,
  LinkedIn icon. `selectable` with the existing bulk-category bar. FilterBar: search,
  category, "has email". The two Gmail import buttons move into one "Import" dropdown in
  the header actions.

## 7. Companies

- `DataTable`: Company (initials + name, domain beneath), Segment chip (from
  `parseChannelBrief`), Motion, Contacts, Leads, Deals, Updated. The three counts come
  from three light queries selecting only `company_id` / `company` and are counted
  client-side by lower-cased name. FilterBar: search, segment, "has leads".

## 8. Record pages — contact, company, deal

- `RecordHeader` at the top. Deal: the Next step strip and the Waiting-on controls sit
  directly under the header as one highlighted band; status as a segmented Active / Won /
  Lost control.
- Three-column grid at `xl` and up: left `w-80` **About** (`PropertyList`; company pages
  also show the Channel Brief block); centre **Activity** with tabs Activity | Notes |
  Emails (existing ActivityTimeline, notes list and Gmail results — nothing new fetched);
  right `w-80` **Associations**: Contacts, Deals, Leads, Tasks cards with counts and the
  existing "+ Add" dialogs where one exists. Stacks below `xl`.

## 9. Prospecting

- Segments as a `DataTable`: Segment (name, red-rail flag when the audit note says DO
  NOT WORK / LABEL DOES NOT MATCH), Score (parse "Score 4.20" from notes; "—" if absent),
  Status text (the words after the score, e.g. "Model defined"), Accounts (companies whose
  Channel Brief segment matches), Leads, Worked (% of leads not in status `new`).
- Expanding a row shows its leads in a nested `DataTable`: Name, Title, Company, Email
  (+ "unverified" tag), Status (inline Select), actions (Contact, + Deal, delete) — the
  existing mutations.

## Order and reporting

Do it in the order above. If the turn runs long, land 1, 2, 3, 4, 5 and 7 first and
report exactly what is left. Finish by listing the files changed and anything skipped.
