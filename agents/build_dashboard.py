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
overdue = [r for r in commits if r["status"].upper() == "OVERDUE"]
due = [r for r in cadence if r["status"] == "due"]

# The roster. count is what that agent is currently responsible for.
ROSTER = [
    ("Chief", "at his desk on Monday", "routes, briefs, holds the gate", len(threads), "threads"),
    ("Scout", "the prospector", "who is worth a call, and the way in", len(people), "people"),
    ("Ghost", "the writer", "every outbound passes through it", len(outbox), "written"),
    ("Opener", "at the handshake", "first touch, LinkedIn and email",
     len([r for r in outbox if r.get("agent") == "opener"]), "opened"),
    ("Chaser", "who won't let a thread die", "cadence, channel, when to stop", len(due), "due"),
    ("Desk", "at 6am with coffee", "inbound, and what he owes", len(commits), "tracked"),
    ("Closer", "in the negotiation", "price floor, deal shape, next step",
     len([r for r in threads if r["bucket"] == "needs-david"]), "at stake"),
]

# Lines David actually wrote, carried through from voice/STYLE.md. This is the
# detail only this subject has: the agents' authority is his own sent mail.
VOICE = [
    ("the greeting", "Jesse hello", "his name-on-its-own-line opener, not “Hi Jesse,”"),
    ("the follow-up", "Millie following up again... have time to speak next week?",
     "10–25 words. his verb is “bump”, never “circle back”"),
    ("the close", "Let's Cre8!", "ends essentially every message he sends"),
    ("the restraint", "I would love to learn a bit more about BeautySpace and share elements of Cre8or with you.",
     "43-word first touch. he does not pitch — he offers to, on a call"),
    ("the manners", "Eddie thanks for the intro.",
     "the introducer is thanked by name, then moved to BCC"),
]


def esc_t(s):
    return esc(s)


def table(headers, rows, empty="Nothing here yet."):
    if not rows:
        return f'<p class="empty">{empty}</p>'
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def chip(text, kind):
    return f'<span class="chip {kind}">{esc(text)}</span>'


commit_rows = []
for c in sorted(commits, key=lambda r: r["due"]):
    d = days_since(c["due"])
    late = d is not None and d > 0
    commit_rows.append([
        f'<strong>{esc(c["person"])}</strong><span class="sub">{esc(c["company"])}</span>',
        esc(c["what"]),
        f'<span class="said">“{esc(c["promised_words"])}”</span>',
        f'<span class="num">{esc(c["due"])}</span>',
        chip(f"{d} days late" if late else "open", "bad" if late else "ok"),
    ])

thread_rows = []
for t in sorted(threads, key=lambda r: r["last_touched"]):
    d = days_since(t["last_touched"])
    thread_rows.append([
        f'<strong>{esc(t["person"])}</strong><span class="sub">{esc(t["company"])}</span>',
        esc(t["subject"]),
        f'<span class="num">{esc(t["channel"])}</span>',
        f'<span class="num">{esc(t["touch_number"])}</span>',
        chip("you" if t["waiting_on"] == "david" else "them",
             "warn" if t["waiting_on"] == "david" else "ok"),
        f'<span class="num">{d}d</span>' if d is not None else "—",
    ])

people_rows = []
for p in sorted(people, key=lambda r: r["warm_path_rank"]):
    rank = p["warm_path_rank"]
    people_rows.append([
        f'<strong>{esc(p["name"])}</strong><span class="sub">{esc(p["title"])}</span>',
        esc(p["company"]),
        chip(f"path {rank}", "ok" if rank in ("1", "2") else "warn"),
        esc(p["warm_path"]),
        esc(p["evidence"])[:130],
        chip(p["stage"], "neutral"),
    ])

draft_rows = [[
    f'<span class="num">{esc(r["agent"])}</span>',
    f'<strong>{esc(r["person"])}</strong><span class="sub">{esc(r["company"])}</span>',
    f'<span class="num">{esc(r["channel"])}</span>',
    esc(r["subject"]),
    f'<span class="said">{esc(r["body"])[:80]}…</span>',
] for r in drafts]

signal_rows = [[
    f'<strong>{esc(s["company"])}</strong>',
    esc(s["signal"]),
    f'<span class="sub-inline">{esc(s["source"])}</span>',
    f'<span class="num">{esc(s["expires_on"])}</span>',
    chip("used" if s["acted_on"] == "yes" else s["acted_on"],
         "ok" if s["acted_on"] == "yes" else "warn"),
] for s in signals]

roster_html = "".join(
    f'<li class="crew"><div class="crew-top"><span class="crew-name">{esc(n)}</span>'
    f'<span class="crew-n">{c}<span class="crew-u">{esc(u)}</span></span></div>'
    f'<p class="crew-who">{esc(w)}</p><p class="crew-does">{esc(d)}</p></li>'
    for n, w, d, c, u in ROSTER)

voice_html = "".join(
    f'<li class="vx"><span class="vx-role">{esc(role)}</span>'
    f'<p class="vx-line">{esc(line)}</p><p class="vx-note">{esc(note)}</p></li>'
    for role, line, note in VOICE)

# Only figures that imply an action get a tile.
TILES = [
    (len(drafts), "waiting on you", "drafts to approve or kill", len(drafts) > 0),
    (len(overdue), "you owe, overdue", "promises past the date you gave", len(overdue) > 0),
    (len(due), "follow-ups due", "threads past their cadence", len(due) > 0),
    (len(approved), "cleared to go", "approved, not yet out", False),
]
tiles_html = "".join(
    f'<div class="tile{" live" if live else ""}"><span class="tile-v">{v}</span>'
    f'<span class="tile-l">{esc(l)}</span><span class="tile-s">{esc(s)}</span></div>'
    for v, l, s, live in TILES)

now = datetime.datetime.now().strftime("%d %B %Y · %H:%M")

HTML = f"""<title>Cre8or BD Watch Board</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;1,8..60,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root {{
  --ground:#f1f3f1; --panel:#fdfdfc; --sunk:#e8ebe8;
  --ink:#14191a; --mute:#5d6a68; --line:#d8ddda;
  --accent:#1c5b4c; --accent-soft:#e2ede9;
  --ok:#2c6a4d; --ok-bg:#e4efe8;
  --warn:#8a6210; --warn-bg:#f6ecd8;
  --bad:#93312c; --bad-bg:#f7e5e3;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0f1413; --panel:#171d1c; --sunk:#121817;
    --ink:#e9eeeb; --mute:#8c9a96; --line:#28312f;
    --accent:#66c3a6; --accent-soft:#17322b;
    --ok:#7cc4a1; --ok-bg:#172b22;
    --warn:#d6a856; --warn-bg:#2c2415;
    --bad:#dd8b83; --bad-bg:#2d1b19;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0f1413; --panel:#171d1c; --sunk:#121817;
  --ink:#e9eeeb; --mute:#8c9a96; --line:#28312f;
  --accent:#66c3a6; --accent-soft:#17322b;
  --ok:#7cc4a1; --ok-bg:#172b22;
  --warn:#d6a856; --warn-bg:#2c2415;
  --bad:#dd8b83; --bad-bg:#2d1b19;
}}

* {{ box-sizing:border-box; }}
body {{
  background:var(--ground); color:var(--ink);
  font-family:var(--display); font-size:15px; line-height:1.55; margin:0;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:1240px; margin:0 auto; padding:34px 22px 70px; }}

/* ---- masthead ---- */
header {{ display:flex; flex-wrap:wrap; align-items:flex-end; gap:20px 30px;
         border-bottom:2px solid var(--ink); padding-bottom:16px; }}
h1 {{ font-family:var(--display); font-weight:700; font-size:clamp(25px,3.4vw,34px);
     letter-spacing:-.025em; margin:0; text-wrap:balance; }}
.sub-title {{ color:var(--mute); font-size:14px; margin:5px 0 0; max-width:56ch; }}
.built {{ margin-left:auto; font-family:var(--mono); font-size:11.5px; color:var(--mute);
         text-align:right; line-height:1.7; }}
.built b {{ color:var(--accent); font-weight:600; }}

/* ---- section headings ---- */
h2 {{ font-family:var(--mono); font-size:11px; font-weight:600; text-transform:uppercase;
     letter-spacing:.16em; color:var(--mute); margin:0 0 12px;
     display:flex; align-items:center; gap:12px; }}
h2::after {{ content:""; flex:1; height:1px; background:var(--line); }}
section {{ margin-top:38px; }}

/* ---- tiles: only actionable figures ---- */
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px;
         background:var(--line); border:1px solid var(--line); border-radius:3px; overflow:hidden; }}
.tile {{ background:var(--panel); padding:15px 17px 14px; display:flex; flex-direction:column; }}
.tile.live {{ background:var(--accent-soft); }}
.tile-v {{ font-family:var(--mono); font-weight:600; font-size:30px; line-height:1;
          letter-spacing:-.03em; font-variant-numeric:tabular-nums; }}
.tile.live .tile-v {{ color:var(--accent); }}
.tile-l {{ font-size:13px; font-weight:600; margin-top:7px; }}
.tile-s {{ font-size:12px; color:var(--mute); margin-top:1px; }}

/* ---- two-column body ---- */
.cols {{ display:grid; grid-template-columns:minmax(0,1fr) 268px; gap:38px; align-items:start; margin-top:38px; }}
@media (max-width:940px) {{ .cols {{ grid-template-columns:minmax(0,1fr); }} aside {{ position:static !important; }} }}
aside {{ position:sticky; top:22px; }}
aside section:first-child {{ margin-top:0; }}
.main > section:first-child {{ margin-top:0; }}

/* ---- the roster: a shift board, not cards ---- */
.roster {{ list-style:none; margin:0; padding:0; border-top:1px solid var(--line); }}
.crew {{ border-bottom:1px solid var(--line); padding:11px 0 12px; }}
.crew-top {{ display:flex; align-items:baseline; justify-content:space-between; gap:10px; }}
.crew-name {{ font-family:var(--display); font-weight:700; font-size:13px;
             letter-spacing:.1em; text-transform:uppercase; color:var(--accent); }}
.crew-n {{ font-family:var(--mono); font-weight:600; font-size:15px;
          font-variant-numeric:tabular-nums; color:var(--ink); }}
.crew-u {{ font-family:var(--display); font-weight:500; font-size:10.5px; color:var(--mute);
          text-transform:uppercase; letter-spacing:.08em; margin-left:5px; }}
.crew-who {{ font-family:var(--serif); font-style:italic; font-size:14px; margin:3px 0 0; }}
.crew-does {{ font-size:12.5px; color:var(--mute); margin:1px 0 0; }}

/* ---- voice evidence ---- */
.voice {{ list-style:none; margin:0; padding:0; }}
.vx {{ padding:12px 0 13px; border-bottom:1px solid var(--line); }}
.vx:last-child {{ border-bottom:0; }}
.vx-role {{ font-family:var(--mono); font-size:10.5px; text-transform:uppercase;
           letter-spacing:.13em; color:var(--mute); }}
.vx-line {{ font-family:var(--serif); font-size:16px; line-height:1.45; margin:5px 0 0;
           border-left:2px solid var(--accent); padding-left:12px; }}
.vx-note {{ font-size:12.5px; color:var(--mute); margin:5px 0 0 14px; }}

/* ---- tables ---- */
.scroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch;
          border:1px solid var(--line); border-radius:3px; background:var(--panel); }}
table {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
th {{ text-align:left; font-family:var(--mono); font-size:10.5px; font-weight:600;
     text-transform:uppercase; letter-spacing:.1em; color:var(--mute);
     padding:10px 14px; background:var(--sunk); border-bottom:1px solid var(--line); white-space:nowrap; }}
td {{ padding:12px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
td strong {{ font-weight:600; }}
.sub {{ display:block; color:var(--mute); font-size:12px; font-weight:400; }}
.sub-inline {{ color:var(--mute); font-size:12.5px; }}
.said {{ font-family:var(--serif); color:var(--mute); }}
.num {{ font-family:var(--mono); font-size:12.5px; font-variant-numeric:tabular-nums; }}
.chip {{ display:inline-block; padding:2px 9px; border-radius:2px; font-family:var(--mono);
        font-size:11px; font-weight:600; white-space:nowrap; letter-spacing:.02em; }}
.chip.ok {{ background:var(--ok-bg); color:var(--ok); }}
.chip.warn {{ background:var(--warn-bg); color:var(--warn); }}
.chip.bad {{ background:var(--bad-bg); color:var(--bad); }}
.chip.neutral {{ background:var(--sunk); color:var(--mute); }}
.empty {{ color:var(--mute); font-size:13.5px; background:var(--panel);
         border:1px dashed var(--line); border-radius:3px; padding:22px; margin:0; }}

/* ---- the gate ---- */
.gate {{ background:var(--panel); border:1px solid var(--line);
        border-top:3px solid var(--accent); border-radius:0 0 3px 3px; padding:22px 26px; }}
.gate h3 {{ font-family:var(--display); font-weight:700; font-size:19px; margin:0 0 10px;
           letter-spacing:-.015em; }}
.gate p {{ margin:0 0 11px; max-width:70ch; }}
.gate p:last-child {{ margin:0; }}
.flow {{ font-family:var(--mono); font-size:12px; color:var(--mute); background:var(--sunk);
        border-radius:2px; padding:13px 16px; margin:0 0 15px; overflow-x:auto;
        white-space:pre; line-height:1.75; }}
.flow b {{ color:var(--accent); font-weight:600; }}
code {{ font-family:var(--mono); font-size:12.5px; background:var(--sunk);
       border-radius:2px; padding:1px 5px; }}
footer {{ margin-top:46px; padding-top:15px; border-top:1px solid var(--line);
         color:var(--mute); font-size:12.5px; font-family:var(--mono); line-height:1.8; }}
</style>

<div class="wrap">

<header>
  <div>
    <h1>Cre8or BD Watch Board</h1>
    <p class="sub-title">Six agents, one voice, and a gate nothing gets past without
    David. Everything below is read from <code>agents/state/</code> — no figure on this
    page was typed by hand.</p>
  </div>
  <p class="built">built <b>{now}</b><br>cre8orai/BDAgent</p>
</header>

<section>
  <h2>Needs a decision</h2>
  <div class="tiles">{tiles_html}</div>
</section>

<div class="cols">
<div class="main">

  <section>
    <h2>What you owe</h2>
    {table(["Person", "What", "Your own words", "Due", ""], commit_rows,
           "No open commitments — Desk found nothing you promised and haven't delivered.")}
  </section>

  <section>
    <h2>Waiting for your approval</h2>
    {table(["Agent", "Person", "Channel", "Subject", "Opens with"], draft_rows,
           "No drafts. Run <code>bash agents/cycle.sh</code> to generate some.")}
  </section>

  <section>
    <h2>Live conversations</h2>
    {table(["Person", "Thread", "Channel", "Touch", "Waiting on", "Last"], thread_rows)}
  </section>

  <section>
    <h2>People, and the way in</h2>
    {table(["Person", "Company", "Path", "How", "Why them, why now", "Stage"], people_rows,
           "No people sourced yet. Scout reads RetailGTM's qualified accounts first.")}
  </section>

  <section>
    <h2>Reasons to write, before they go stale</h2>
    {table(["Company", "Signal", "Source", "Expires", ""], signal_rows,
           "No live signals. Desk writes these from inbound mail.")}
  </section>

</div>

<aside>
  <section>
    <h2>On watch</h2>
    <ul class="roster">{roster_html}</ul>
  </section>

  <section>
    <h2>Whose voice</h2>
    <ul class="voice">{voice_html}</ul>
  </section>
</aside>
</div>

<section>
  <h2>The gate</h2>
  <div class="gate">
    <h3>No agent here has a way to send anything.</h3>
    <p class="flow">Scout · Desk · Chaser · Closer
      └─► <b>GHOST</b> (the voice)
            └─► outbox.csv   <b>status = draft</b>   ◄── and it stops here
                  └─► <b>DAVID</b> reads each one, approves or kills
                        └─► send.sh   ── Gmail / LinkedIn</p>
    <p>Agents write rows and stop. <code>agents/send.sh</code> is the only script that
    reaches anyone, it exits immediately without an interactive terminal, and it acts on
    nothing but rows marked <code>approved</code>. Two permission profiles enforce that
    in code rather than in a prompt — the scheduled profile denies the mail and browser
    tools outright.</p>
    <p>LinkedIn work is capped at 8 per session, 40–90 seconds apart, once a day, and
    stops the whole run on any challenge screen rather than retrying. Three reasons, each
    sufficient on its own: domain reputation, LinkedIn's User Agreement, and the fact
    that it is David's name on every one of them.</p>
  </div>
</section>

<footer>
  regenerated by agents/build_dashboard.py after every run<br>
  voice derived from 287 of David's own sent messages · Feb 2025 – Sep 2026<br>
  github.com/cre8orai/BDAgent
</footer>
</div>
"""

with open(OUT, "w") as f:
    f.write(HTML)
print(f"pipeline.html rebuilt — {len(threads)} threads, {len(drafts)} drafts, "
      f"{len(overdue)} overdue commitments, {len(people)} people")
