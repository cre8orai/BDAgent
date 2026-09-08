#!/usr/bin/env python3
"""Rebuild pipeline.html from agents/state/*.csv.

Runs after every agent run so the published command centre can never drift from
the data behind it. An agent may rebuild this file; an agent may not publish it.
"""
import csv, os, datetime, html, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "agents", "state")
OUT = os.path.join(ROOT, "command-centre.html")


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
questions = read("questions.csv")
autonomy = read("autonomy.csv")
open_questions = [q for q in questions if not q["answer"]]

drafts = [r for r in outbox if r["status"] == "draft"]
approved = [r for r in outbox if r["status"] == "approved"]
overdue = [r for r in commits if r["status"].upper() == "OVERDUE"]
due = [r for r in cadence if r["status"] == "due"]

# The roster. count is what that agent is currently responsible for.
ROSTER = [
    ("Chief", "at his desk on Monday", "routes, briefs, asks you things", len(threads), "threads"),
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
    (len(open_questions), "questions for you", "agents are blocked on these",
     len(open_questions) > 0),
    (len(drafts), "drafts to decide", "approve, kill, or send back", len(drafts) > 0),
    (len(overdue), "you owe, overdue", "promises past the date you gave", len(overdue) > 0),
    (len(due), "follow-ups due", "threads past their cadence", len(due) > 0),
]
tiles_html = "".join(
    f'<div class="tile{" live" if live else ""}"><span class="tile-v">{v}</span>'
    f'<span class="tile-l">{esc(l)}</span><span class="tile-s">{esc(s)}</span></div>'
    for v, l, s, live in TILES)

def track_record(lane):
    """What has actually happened in this lane. Empty is an honest answer."""
    seen = [r for r in outbox if r.get("lane") == lane]
    done = [r for r in seen if r["status"] in ("approved", "killed", "sent", "drafted")]
    ok = [r for r in done if r["status"] in ("approved", "sent", "drafted")]
    return {
        "decided": len(done),
        "approved": len(ok),
        "killed": len([r for r in done if r["status"] == "killed"]),
        "waiting": len([r for r in seen if r["status"] == "draft"]),
    }


PAYLOAD = json.dumps({
    "generated": datetime.datetime.now().isoformat(timespec="minutes"),
    "questions": [{
        "id": q["id"], "agent": q["agent"], "about": q["about"],
        "question": q["question"], "why": q["why_it_matters"],
        "blocking": q["blocking"],
    } for q in open_questions],
    "drafts": [{
        "id": r["id"], "agent": r["agent"], "person": r["person"],
        "company": r["company"], "channel": r["channel"],
        "subject": r["subject"], "body": r["body"].replace("\\n", "\n"),
        "notes": r["notes"],
        "blocked_by": next((q["id"] for q in open_questions
                            if q["blocking"] == r["id"]), None),
    } for r in drafts],
    "agents": [a[0] for a in ROSTER],
    "lanes": [{
        "lane": a["lane"], "mode": a["mode"],
        "eligible": a["eligible_for_auto"] == "yes",
        "note": a["note"], "record": track_record(a["lane"]),
    } for a in autonomy if a["lane"] != "brief-to-david"],
}, ensure_ascii=False)

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
/* ---- the dialogue surface ---- */
.ask {{ background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--accent);
       border-radius:0 3px 3px 0; padding:17px 20px; margin-bottom:11px; }}
.ask.answered {{ border-left-color:var(--ok); opacity:.72; }}
.ask-who {{ font-family:var(--mono); font-size:10.5px; text-transform:uppercase;
           letter-spacing:.13em; color:var(--accent); }}
.ask-q {{ font-family:var(--display); font-weight:600; font-size:16.5px; margin:6px 0 0;
         letter-spacing:-.01em; text-wrap:balance; }}
.ask-why {{ font-family:var(--serif); font-size:14px; color:var(--mute); margin:7px 0 0;
           max-width:72ch; }}
.ask-blocks {{ font-family:var(--mono); font-size:11px; color:var(--warn);
              background:var(--warn-bg); display:inline-block; padding:2px 8px;
              border-radius:2px; margin-top:9px; }}
.reply {{ display:flex; gap:8px; margin-top:12px; flex-wrap:wrap; }}
textarea, input[type=text], select {{
  font-family:var(--display); font-size:14px; color:var(--ink); background:var(--ground);
  border:1px solid var(--line); border-radius:3px; padding:9px 11px; width:100%;
  resize:vertical; }}
textarea:focus, input:focus, select:focus {{ outline:2px solid var(--accent); outline-offset:1px; }}
button {{ font-family:var(--display); font-size:13px; font-weight:600; cursor:pointer;
         border:1px solid var(--line); background:var(--panel); color:var(--ink);
         border-radius:3px; padding:8px 15px; }}
button:hover {{ border-color:var(--accent); }}
button:focus-visible {{ outline:2px solid var(--accent); outline-offset:1px; }}
button.primary {{ background:var(--accent); border-color:var(--accent); color:var(--panel); }}
button.danger:hover {{ border-color:var(--bad); color:var(--bad); }}
button[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent); color:var(--panel); }}
.said-back {{ font-family:var(--serif); font-size:14.5px; margin:10px 0 0; padding:9px 13px;
             background:var(--ok-bg); color:var(--ok); border-radius:3px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:3px;
        padding:17px 20px; margin-bottom:11px; }}
.card.decided {{ opacity:.66; }}
.card-top {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px;
            flex-wrap:wrap; }}
.card-who {{ font-weight:600; font-size:15px; }}
.card-meta {{ font-family:var(--mono); font-size:11px; color:var(--mute); }}
.card-note {{ font-family:var(--mono); font-size:11.5px; color:var(--warn);
             background:var(--warn-bg); padding:6px 10px; border-radius:2px; margin:9px 0 0; }}
.card-body {{ font-family:var(--serif); font-size:15px; line-height:1.5; white-space:pre-wrap;
             margin:11px 0 0; padding:12px 15px; background:var(--ground);
             border-radius:3px; border:1px solid var(--line); }}
.verdict {{ font-family:var(--mono); font-size:11px; font-weight:600; padding:3px 9px;
           border-radius:2px; }}
.verdict.approve {{ background:var(--ok-bg); color:var(--ok); }}
.verdict.kill {{ background:var(--bad-bg); color:var(--bad); }}
.verdict.edit {{ background:var(--warn-bg); color:var(--warn); }}
.lane {{ display:grid; grid-template-columns:1fr auto; gap:10px 16px; align-items:center;
        background:var(--panel); border:1px solid var(--line); border-radius:3px;
        padding:14px 18px; margin-bottom:9px; }}
.lane.on {{ border-color:var(--accent); background:var(--accent-soft); }}
.lane.locked {{ opacity:.6; }}
.lane-name {{ font-family:var(--mono); font-size:12.5px; font-weight:600; letter-spacing:.02em; }}
.lane-note {{ font-size:12.5px; color:var(--mute); margin:3px 0 0; max-width:62ch;
             grid-column:1 / -1; }}
.lane-rec {{ font-family:var(--mono); font-size:11.5px; color:var(--mute); margin:5px 0 0;
            grid-column:1 / -1; }}
.lane-rec b {{ color:var(--ink); }}
.switch {{ display:inline-flex; border:1px solid var(--line); border-radius:99px; overflow:hidden; }}
.switch button {{ border:0; border-radius:0; padding:6px 15px; font-size:12px;
                 font-family:var(--mono); letter-spacing:.03em; }}
.switch button[aria-pressed="true"] {{ background:var(--accent); color:var(--panel); }}
.locked-tag {{ font-family:var(--mono); font-size:11px; color:var(--mute);
              background:var(--sunk); padding:4px 11px; border-radius:99px; }}
.offline {{ font-family:var(--mono); font-size:12px; color:var(--warn);
           background:var(--warn-bg); border-radius:3px; padding:11px 15px; margin:0 0 14px; }}
footer {{ margin-top:46px; padding-top:15px; border-top:1px solid var(--line);
         color:var(--mute); font-size:12.5px; font-family:var(--mono); line-height:1.8; }}
</style>

<div class="wrap">

<header>
  <div>
    <h1>Cre8or BD Watch Board</h1>
    <p class="sub-title">Six agents work under David. They ask him when they are stuck and
    draft in his voice when they are not. He answers, decides, directs them — and sets
    which lanes are allowed to run on their own. All of it is read back before the next
    run.</p>
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

  <section id="asks-section">
    <h2>Your agents are asking you</h2>
    <div id="offline" class="offline" hidden>Read-only right now — answers can't be
    saved from this view. Everything below is still current.</div>
    <div id="asks"></div>
  </section>

  <section>
    <h2>Drafts — approve, kill, or send back</h2>
    <div id="drafts"></div>
  </section>

  <section>
    <h2>What runs on its own</h2>
    <p class="lane-note" style="margin:0 0 12px">Everything starts as a draft. Switch a
    lane to <strong>auto</strong> when you have seen enough of what it writes — and
    switch it back the moment you don't like something. Only lanes marked eligible can
    be switched at all.</p>
    <div id="lanes"></div>
  </section>

  <section>
    <h2>Tell an agent what to do</h2>
    <div class="card">
      <div class="reply">
        <select id="dir-agent" aria-label="Which agent" style="max-width:170px"></select>
        <input type="text" id="dir-text" style="flex:1;min-width:240px"
               placeholder="e.g. stop chasing Front Row entirely, or find me medspa franchisors in Texas">
        <button class="primary" id="dir-send">Send it</button>
      </div>
      <div id="dir-log"></div>
    </div>
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
  <h2>How this works</h2>
  <div class="gate">
    <h3>They ask. You decide. You choose what runs on its own.</h3>
    <p class="flow">Scout · Desk · Chaser · Closer          blocked? ──► a <b>QUESTION</b>
      └─► <b>GHOST</b> (the voice)                                    │
            └─► a <b>DRAFT</b> ─────────────────────┐                 │
                                                    ▼                 ▼
                                        <b>YOU</b>, on this page · BizDave · your email
                                                    │
                    approve ─┬─ kill ─┬─ send back ─┴─ or just tell an agent what to do
                             │        │
                             ▼        ▼
              a Gmail <b>DRAFT</b>    the agent rewrites it
              <b>you</b> press Send</p>
    <p><strong>This page is where the conversation happens.</strong> When an agent is
    blocked it asks rather than guesses, and the question appears at the top with the
    draft it is holding up. Answer it and the agent acts on the answer. Approve, kill or
    send a draft back with a note, or skip all of that and just tell an agent what to
    do — every one of those is read back before the next run.</p>
    <p><strong>Every lane starts as a draft</strong> — the agent writes, you press Send
    in Gmail. Switch a lane to <em>auto</em> above when you are comfortable with what it
    produces, and switch it back the moment you aren't. Replies, LinkedIn and anything
    commercial cannot be switched on at all, and two separate checks enforce that.</p>
    <p>Even in an auto lane: a message containing an unfilled <code>[placeholder]</code>
    is never sent, 12 a day is the ceiling, it is email only, and every send is written
    to a ledger and reported to you the same day. <strong>Automatic never means
    invisible.</strong> No agent may switch a lane on for you.</p>
    <p>Enforced in three places, so losing one opens no hole: no script calls a send
    tool; the scheduled permission profile denies sending <em>and</em> drafting, so a
    scheduled agent writes CSV and stops; the drafting profile allows only
    <code>create_draft</code>.</p>
    <p><strong>LinkedIn is read-only to every agent.</strong> The 2,558-message archive
    and the 7,246-person connection graph are read. Nothing opens linkedin.com, clicks,
    or types — LinkedIn drafts are listed for David to paste by hand.</p>
  </div>
</section>

<footer>
  regenerated by agents/build_dashboard.py after every run<br>
  voice derived from 287 of David's own sent messages · Feb 2025 – Sep 2026<br>
  github.com/cre8orai/BDAgent
</footer>
</div>

<script id="bd-data" type="application/json">{PAYLOAD}</script>
<script>
(function () {{
  const DATA = JSON.parse(document.getElementById("bd-data").textContent);
  const asksEl = document.getElementById("asks");
  const draftsEl = document.getElementById("drafts");
  const dirAgent = document.getElementById("dir-agent");
  const dirText = document.getElementById("dir-text");
  const dirSend = document.getElementById("dir-send");
  const dirLog = document.getElementById("dir-log");
  const lanesEl = document.getElementById("lanes");
  const offline = document.getElementById("offline");

  let db = null;                       // set if this view can persist
  const answers = new Map();           // questionId -> {{text, at}}
  const verdicts = new Map();          // draftId    -> {{verdict, note, at}}
  const directives = [];
  const modes = new Map(DATA.lanes.map((l) => [l.lane, l.mode]));

  const esc = (t) => {{ const d = document.createElement("div"); d.textContent = t ?? ""; return d.innerHTML; }};
  const when = (iso) => {{ try {{ return new Date(iso).toLocaleString(undefined,
      {{month:"short", day:"numeric", hour:"2-digit", minute:"2-digit"}}); }} catch {{ return ""; }} }};

  DATA.agents.forEach((a) => {{
    const o = document.createElement("option"); o.value = a; o.textContent = a; dirAgent.append(o);
  }});

  // ---------- render ----------
  function renderAsks() {{
    if (!DATA.questions.length) {{
      asksEl.innerHTML = '<p class="empty">Nothing blocked. Your agents have everything they need.</p>';
      return;
    }}
    asksEl.innerHTML = DATA.questions.map((q) => {{
      const a = answers.get(q.id);
      return `<div class="ask ${{a ? "answered" : ""}}">
        <span class="ask-who">${{esc(q.agent)}} &middot; ${{esc(q.about)}}</span>
        <p class="ask-q">${{esc(q.question)}}</p>
        <p class="ask-why">${{esc(q.why)}}</p>
        ${{q.blocking ? `<span class="ask-blocks">holding draft ${{esc(q.blocking)}}</span>` : ""}}
        ${{a
          ? `<p class="said-back">You said: ${{esc(a.text)}}<br><span class="card-meta">${{when(a.at)}}</span></p>`
          : `<div class="reply">
               <textarea rows="2" data-q="${{esc(q.id)}}" placeholder="Answer in your own words — the agent reads this and acts on it"></textarea>
               <button class="primary" data-answer="${{esc(q.id)}}">Answer</button>
             </div>`}}
      </div>`;
    }}).join("");
  }}

  function renderDrafts() {{
    if (!DATA.drafts.length) {{
      draftsEl.innerHTML = '<p class="empty">No drafts waiting.</p>';
      return;
    }}
    draftsEl.innerHTML = DATA.drafts.map((d) => {{
      const v = verdicts.get(d.id);
      const blocked = d.blocked_by && !answers.has(d.blocked_by);
      return `<div class="card ${{v ? "decided" : ""}}">
        <div class="card-top">
          <span class="card-who">${{esc(d.person)}} <span class="card-meta">${{esc(d.company)}}</span></span>
          <span class="card-meta">${{esc(d.agent)}} &middot; ${{esc(d.channel)}} &middot; ${{esc(d.id)}}</span>
        </div>
        ${{d.notes ? `<p class="card-note">${{esc(d.notes)}}</p>` : ""}}
        ${{blocked ? `<p class="card-note">Waiting on your answer above before this is safe to use.</p>` : ""}}
        <div class="card-body">${{esc(d.body)}}</div>
        ${{v
          ? `<p class="said-back"><span class="verdict ${{v.verdict}}">${{esc(v.verdict)}}</span>
               ${{v.note ? " &mdash; " + esc(v.note) : ""}}
               <br><span class="card-meta">${{when(v.at)}}</span></p>`
          : `<div class="reply">
               <button class="primary" data-verdict="approve" data-id="${{esc(d.id)}}">Approve</button>
               <button data-verdict="edit" data-id="${{esc(d.id)}}">Send back</button>
               <button class="danger" data-verdict="kill" data-id="${{esc(d.id)}}">Kill</button>
               <input type="text" data-note="${{esc(d.id)}}" style="flex:1;min-width:200px"
                      placeholder="Optional — what to change, or why">
             </div>`}}
      </div>`;
    }}).join("");
  }}

  function renderLanes() {{
    lanesEl.innerHTML = DATA.lanes.map((l) => {{
      const mode = modes.get(l.lane);
      const on = mode === "auto";
      const r = l.record;
      const rec = r.decided
        ? `you have decided on <b>${{r.decided}}</b> in this lane &mdash;
           <b>${{r.approved}}</b> approved, <b>${{r.killed}}</b> killed`
        : `nothing decided in this lane yet &mdash; no track record to judge it on`;
      return `<div class="lane ${{on ? "on" : ""}} ${{l.eligible ? "" : "locked"}}">
        <span class="lane-name">${{esc(l.lane)}}</span>
        ${{l.eligible
          ? `<span class="switch">
               <button data-lane="${{esc(l.lane)}}" data-mode="draft" aria-pressed="${{!on}}">draft</button>
               <button data-lane="${{esc(l.lane)}}" data-mode="auto" aria-pressed="${{on}}">auto</button>
             </span>`
          : `<span class="locked-tag">always a draft</span>`}}
        <p class="lane-note">${{esc(l.note)}}</p>
        <p class="lane-rec">${{rec}}${{r.waiting ? ` &middot; ${{r.waiting}} waiting on you now` : ""}}</p>
      </div>`;
    }}).join("");
  }}

  function renderDirectives() {{
    dirLog.innerHTML = directives.length
      ? directives.map((d) => `<p class="said-back"><strong>${{esc(d.agent)}}</strong> &mdash;
          ${{esc(d.text)}}<br><span class="card-meta">${{when(d.at)}}</span></p>`).join("")
      : "";
  }}

  renderAsks(); renderDrafts(); renderLanes();

  // ---------- persistence ----------
  async function save(path, body) {{
    if (!db) return false;
    try {{ await db.doc(path).set(body); return true; }}
    catch (e) {{ console.warn("save failed", path, e && e.code); return false; }}
  }}

  asksEl.addEventListener("click", async (ev) => {{
    const btn = ev.target.closest("[data-answer]");
    if (!btn) return;
    const id = btn.dataset.answer;
    const box = asksEl.querySelector(`textarea[data-q="${{id}}"]`);
    const text = (box && box.value || "").trim();
    if (!text) {{ box && box.focus(); return; }}
    const rec = {{ questionId: id, text, at: new Date().toISOString() }};
    answers.set(id, rec); renderAsks(); renderDrafts();
    await save("answers/" + id, rec);
  }});

  draftsEl.addEventListener("click", async (ev) => {{
    const btn = ev.target.closest("[data-verdict]");
    if (!btn) return;
    const id = btn.dataset.id;
    const noteEl = draftsEl.querySelector(`input[data-note="${{id}}"]`);
    const rec = {{ draftId: id, verdict: btn.dataset.verdict,
                  note: (noteEl && noteEl.value || "").trim(),
                  at: new Date().toISOString() }};
    verdicts.set(id, rec); renderDrafts();
    await save("decisions/" + id, rec);
  }});

  lanesEl.addEventListener("click", async (ev) => {{
    const btn = ev.target.closest("[data-lane]");
    if (!btn) return;
    const lane = btn.dataset.lane, mode = btn.dataset.mode;
    if (modes.get(lane) === mode) return;
    modes.set(lane, mode); renderLanes();
    await save("settings/autonomy", {{
      lanes: Object.fromEntries(modes),
      at: new Date().toISOString(),
    }});
  }});

  dirSend.addEventListener("click", async () => {{
    const text = dirText.value.trim();
    if (!text) {{ dirText.focus(); return; }}
    const rec = {{ agent: dirAgent.value, text, at: new Date().toISOString(), status: "new" }};
    directives.unshift(rec); dirText.value = ""; renderDirectives();
    await save("directives/" + Date.now().toString(36), rec);
  }});

  // ---------- come alive if the store is there ----------
  (async () => {{
    db = (window.claude && claude.use) ? await claude.use("db") : null;
    if (!db) {{ offline.hidden = false; return; }}
    try {{
      const [ans, dec, dir] = await Promise.all([
        db.collection("answers").get(),
        db.collection("decisions").get(),
        db.collection("directives").orderBy("at", "desc").limit(20).get(),
      ]);
      ans.docs.forEach((d) => {{ const v = d.data(); if (v && v.questionId) answers.set(v.questionId, v); }});
      dec.docs.forEach((d) => {{ const v = d.data(); if (v && v.draftId) verdicts.set(v.draftId, v); }});
      dir.docs.forEach((d) => directives.push(d.data()));
      renderAsks(); renderDrafts(); renderLanes(); renderDirectives();
    }} catch (e) {{ console.warn("load failed", e && e.code); }}
  }})();
}})();
</script>
"""

with open(OUT, "w") as f:
    f.write(HTML)
print(f"command-centre.html rebuilt — {len(threads)} threads, {len(drafts)} drafts, "
      f"{len(overdue)} overdue commitments, {len(people)} people")
