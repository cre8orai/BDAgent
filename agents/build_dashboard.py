#!/usr/bin/env python3
"""Rebuild pipeline.html from agents/state/*.csv.

Runs after every agent run so the published command centre can never drift from
the data behind it. An agent may rebuild this file; an agent may not publish it.
"""
import csv, os, datetime, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "agents", "state")
OUT = os.path.join(ROOT, "pipeline.html")


def read(name):
    p = os.path.join(STATE, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def esc(s):
    return html.escape(str(s or ""))


def days_since(d):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(d)).days
    except Exception:
        return None


people = read("people.csv")
threads = read("threads.csv")
outbox = read("outbox.csv")
cadence = read("cadence.csv")
commits = read("commitments.csv")
signals = read("signals.csv")

drafts = [r for r in outbox if r["status"] == "draft"]
approved = [r for r in outbox if r["status"] == "approved"]
sent = [r for r in outbox if r["status"] == "sent"]
overdue = [r for r in commits if r["status"].upper() == "OVERDUE"]
due = [r for r in cadence if r["status"] == "due"]
waiting_them = [r for r in threads if r["waiting_on"] == "them"]
needs_david = [r for r in threads if r["bucket"] == "needs-david"]

AGENTS = [
    ("Chief", "orchestrator", "routes, briefs, enforces the gates", len(threads)),
    ("Scout", "who is worth a call", "people + the warm path in", len(people)),
    ("Ghost", "the voice", "every outbound passes through it", len(outbox)),
    ("Opener", "first touch", "LinkedIn and email", len([r for r in outbox if r["agent"] == "opener"])),
    ("Chaser", "never lets a thread die", "cadence and channel switching", len(due)),
    ("Desk", "inbound", "triage and what David owes", len(commits)),
    ("Closer", "money and next step", "pricing discipline, deal shape", len(needs_david)),
]

rows_stat = [
    ("Awaiting your approval", len(drafts), "draft" if len(drafts) == 1 else "drafts in the outbox"),
    ("Approved, not yet out", len(approved), "ready for send.sh"),
    ("You owe, overdue", len(overdue), "promises past their date"),
    ("Follow-ups due", len(due), "threads past cadence"),
    ("Live conversations", len(threads), "tracked"),
    ("People sourced", len(people), "with a warm path where known"),
]


def table(headers, rows, empty="Nothing here yet."):
    if not rows:
        return f'<p class="empty">{empty}</p>'
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def pill(text, kind):
    return f'<span class="pill {kind}">{esc(text)}</span>'


commit_rows = []
for c in sorted(commits, key=lambda r: r["due"]):
    d = days_since(c["due"])
    late = d is not None and d > 0
    commit_rows.append([
        esc(c["person"]) + f' <span class="sub">{esc(c["company"])}</span>',
        esc(c["what"]),
        f'<span class="quote">“{esc(c["promised_words"])}”</span>',
        esc(c["due"]),
        pill(f"{d}d late" if late else "open", "bad" if late else "ok"),
    ])

thread_rows = []
for t in sorted(threads, key=lambda r: r["last_touched"]):
    d = days_since(t["last_touched"])
    thread_rows.append([
        esc(t["person"]) + f' <span class="sub">{esc(t["company"])}</span>',
        esc(t["subject"]),
        esc(t["channel"]),
        f"touch {esc(t['touch_number'])}",
        pill(t["waiting_on"], "warn" if t["waiting_on"] == "david" else "ok"),
        f'{d}d ago' if d is not None else "—",
    ])

people_rows = []
for p in sorted(people, key=lambda r: r["warm_path_rank"]):
    people_rows.append([
        esc(p["name"]) + f' <span class="sub">{esc(p["title"])}</span>',
        esc(p["company"]),
        pill(f"rank {p['warm_path_rank']}", "ok" if p["warm_path_rank"] in ("1", "2") else "warn"),
        esc(p["warm_path"]),
        esc(p["evidence"])[:120],
        pill(p["stage"], "ok"),
    ])

draft_rows = [[
    esc(r["agent"]), esc(r["person"]) + f' <span class="sub">{esc(r["company"])}</span>',
    esc(r["channel"]), esc(r["subject"]), esc(r["body"])[:90] + "…",
] for r in drafts]

signal_rows = [[
    esc(s["company"]), esc(s["signal"]), esc(s["source"]), esc(s["expires_on"]),
    pill(s["acted_on"], "ok" if s["acted_on"] == "yes" else "warn"),
] for s in signals]

agent_cards = "".join(
    f'<div class="agent"><h3>{esc(n)}</h3><p class="who">{esc(w)}</p>'
    f'<p class="does">{esc(d)}</p><p class="n">{c}</p></div>'
    for n, w, d, c in AGENTS)

stat_cards = "".join(
    f'<div class="stat{" alert" if (lbl.startswith("You owe") and v) else ""}">'
    f'<div class="v">{v}</div><div class="l">{esc(lbl)}</div>'
    f'<div class="s">{esc(sub)}</div></div>'
    for lbl, v, sub in rows_stat)

now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

HTML = f"""<title>Cre8or BD Command Centre</title>
<style>
:root {{
  --bg:#faf9f7; --panel:#fff; --ink:#16130f; --mute:#6b6259; --line:#e6e1da;
  --accent:#b4531f; --ok:#2f6b4f; --warn:#a8761c; --bad:#a33232;
  --okbg:#e8f2ec; --warnbg:#faf0dc; --badbg:#f8e8e6;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#131110; --panel:#1c1917; --ink:#f0ebe4; --mute:#a09689; --line:#2e2925;
    --accent:#e08a4e; --ok:#7fc09c; --warn:#e0b062; --bad:#e08b80;
    --okbg:#1b2b23; --warnbg:#2e2617; --badbg:#2e1c1a;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#131110; --panel:#1c1917; --ink:#f0ebe4; --mute:#a09689; --line:#2e2925;
  --accent:#e08a4e; --ok:#7fc09c; --warn:#e0b062; --bad:#e08b80;
  --okbg:#1b2b23; --warnbg:#2e2617; --badbg:#2e1c1a;
}}
body {{ background:var(--bg); color:var(--ink); font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; margin:0; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:40px 22px 80px; }}
header {{ border-bottom:2px solid var(--ink); padding-bottom:18px; margin-bottom:34px; }}
h1 {{ font-size:31px; margin:0 0 6px; letter-spacing:-.02em; }}
.tag {{ color:var(--mute); font-size:14px; margin:0; }}
h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:.1em; color:var(--mute);
     margin:44px 0 14px; padding-bottom:7px; border-bottom:1px solid var(--line); }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(168px,1fr)); gap:12px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); border-radius:9px; padding:16px 18px; }}
.stat.alert {{ border-color:var(--bad); }}
.stat .v {{ font-size:30px; font-weight:640; letter-spacing:-.02em; }}
.stat .l {{ font-size:13px; font-weight:600; margin-top:3px; }}
.stat .s {{ font-size:12px; color:var(--mute); }}
.agents {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(158px,1fr)); gap:11px; }}
.agent {{ background:var(--panel); border:1px solid var(--line); border-radius:9px; padding:14px 15px; position:relative; }}
.agent h3 {{ margin:0; font-size:14px; letter-spacing:.02em; text-transform:uppercase; color:var(--accent); }}
.agent .who {{ margin:5px 0 0; font-size:13px; font-weight:600; }}
.agent .does {{ margin:3px 0 0; font-size:12px; color:var(--mute); }}
.agent .n {{ position:absolute; top:12px; right:14px; font-size:19px; font-weight:640; color:var(--mute); margin:0; }}
.scroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
table {{ width:100%; border-collapse:collapse; font-size:13.5px; background:var(--panel);
         border:1px solid var(--line); border-radius:9px; overflow:hidden; }}
th {{ text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.07em;
      color:var(--mute); padding:10px 13px; border-bottom:1px solid var(--line); white-space:nowrap; }}
td {{ padding:11px 13px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
.sub {{ color:var(--mute); font-size:12px; display:block; }}
.quote {{ color:var(--mute); font-style:italic; }}
.pill {{ display:inline-block; padding:2px 9px; border-radius:99px; font-size:11.5px; font-weight:600; white-space:nowrap; }}
.pill.ok {{ background:var(--okbg); color:var(--ok); }}
.pill.warn {{ background:var(--warnbg); color:var(--warn); }}
.pill.bad {{ background:var(--badbg); color:var(--bad); }}
.empty {{ color:var(--mute); font-size:13.5px; background:var(--panel); border:1px dashed var(--line);
          border-radius:9px; padding:20px; margin:0; }}
.gate {{ background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--accent);
         border-radius:0 9px 9px 0; padding:16px 20px; margin-top:14px; }}
.gate p {{ margin:0 0 8px; font-size:14px; }}
.gate p:last-child {{ margin:0; }}
code {{ background:var(--bg); border:1px solid var(--line); border-radius:4px; padding:1px 6px; font-size:12.5px; }}
footer {{ margin-top:52px; padding-top:16px; border-top:1px solid var(--line); color:var(--mute); font-size:12.5px; }}
</style>

<div class="wrap">
<header>
  <h1>Cre8or BD Command Centre</h1>
  <p class="tag">Six agents, one voice, nothing sent without David. Generated from
  <code>agents/state/</code> at {now} — never edited by hand.</p>
</header>

<h2>Where things stand</h2>
<div class="stats">{stat_cards}</div>

<h2>The team</h2>
<div class="agents">{agent_cards}</div>

<h2>What you owe</h2>
{table(["Person", "What", "Your words", "Due", ""], commit_rows,
       "No open commitments. Desk had nothing to catch.")}

<h2>Waiting for your approval</h2>
{table(["Agent", "Person", "Channel", "Subject", "Opens with"], draft_rows,
       "No drafts. Run <code>bash agents/cycle.sh</code> to generate some.")}

<h2>Live conversations</h2>
{table(["Person", "Thread", "Channel", "Touch", "Waiting on", "Last"], thread_rows)}

<h2>People and the way in</h2>
{table(["Person", "Company", "Path", "How", "Why them", "Stage"], people_rows)}

<h2>Reasons to reach out, before they go stale</h2>
{table(["Company", "Signal", "Source", "Expires", "Used"], signal_rows)}

<h2>The gate</h2>
<div class="gate">
  <p><strong>No agent here has a send tool.</strong> Every agent writes to
  <code>agents/state/outbox.csv</code> with <code>status=draft</code> and stops.</p>
  <p>David reviews with <code>bash agents/review.sh</code>, and only rows he marks
  <code>approved</code> are ever transmitted — by <code>agents/send.sh</code>, in the
  foreground, after he types <code>SEND</code>.</p>
  <p>LinkedIn is capped at 8 messages per session, 40–90 seconds apart, and any
  captcha or checkpoint stops the whole run rather than retrying.</p>
</div>

<footer>
  Built by <code>agents/build_dashboard.py</code> after every run ·
  <code>github.com/cre8orai/BDAgent</code> · voice derived from 287 of David's own
  sent messages, Feb 2025 – Sep 2026
</footer>
</div>
"""

with open(OUT, "w") as f:
    f.write(HTML)
print(f"pipeline.html rebuilt — {len(threads)} threads, {len(drafts)} drafts, "
      f"{len(overdue)} overdue commitments")
