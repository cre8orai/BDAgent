#!/usr/bin/env python3
"""Push the repo's BD state into bizDave so the app shows the real pipeline.

bizDave (https://bizdave-personal-hub.lovable.app) is already a full BD portal —
Today, Deals, Contacts, Companies, Tasks, Meetings, Ask. What it has never had is
data. The pipeline lives in agents/state/*.csv; this is the bridge.

  people.csv       -> contacts   (who, and how to reach them)
  people+threads   -> deals      (the account, its stage, and the next step)
  threads.csv      -> activities (the last real touch, on the deal's timeline)
  commitments.csv  -> tasks      (what David promised, in his own words)
  questions.csv    -> pending_actions (Gate 4 — asked where he actually is)

Idempotent. Every row it writes is tagged `BDAgent`, and each run clears its own
previous rows before writing. Run it twice and nothing doubles; it never touches a
row David created himself.

  python3 agents/sync_bizdave.py             # print the SQL, change nothing
  python3 agents/sync_bizdave.py --execute   # apply it, needs BIZDAVE_DB_URL

This writes DISPLAY rows only. There is no send path here and it cannot create one.
See agents/GATES.md.
"""
import csv, os, sys, datetime

USER = "bb9fc520-a65a-4d2a-beb9-39ba6ca6b462"          # david@cre8orglobal.com
TAG = "BDAgent"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "agents", "state")

# How a thread's real history maps to a pipeline stage. 'lead' is contacted with no
# substantive reply; 'qualified' means they engaged — replied, met, or asked for
# something. Nothing here is guessed: each one is justified in people.csv evidence.
# bizDave constrains contacts.category to its own taxonomy, and contacts.source to
# 'manual' | 'gmail_import'. The repo's segment vocabulary is richer, so it is mapped
# here and kept verbatim in the contact's notes rather than lost.
CATEGORY = {
    "investor":         "Investors",
    "brand-operator":   "Potential Partners / Prospects",
    "beauty-platform":  "Potential Partners / Prospects",
    "creator-platform": "Potential Partners / Prospects",
}

STAGE = {
    "Nate Cooper":      ("qualified", "investor"),
    "Jesse Gerson":     ("lead",      "brand-operator"),
    "Noah Rosenblatt":  ("lead",      "beauty-platform"),
    "Monica Sultan":    ("qualified", "brand-operator"),
    "Judah Abraham":    ("qualified", "brand-operator"),
    "Ralph Azrak":      ("qualified", "brand-operator"),
    "Will Baumann":     ("lead",      "creator-platform"),
}

# The next step for each account, and when it is due. Taken from threads.csv,
# commitments.csv and the notes in people.csv — never invented.
NEXT = {
    "Nate Cooper":     ("Send the materials — promised 3 Sept, overdue", "2026-09-19"),
    "Jesse Gerson":    ("Decide the door: Jesse, or Matt Beer. Gate 3 — not both", "2026-09-19"),
    "Noah Rosenblatt": ("Cadence touch 2 if still silent", "2026-09-22"),
    "Monica Sultan":   ("Chase sample tracking; NYC November was mentioned", "2026-09-22"),
    "Judah Abraham":   ("Rebook the Zoom lost to a crossed wire in April", "2026-09-19"),
    "Ralph Azrak":     ("Confirm with David whether the clinical docs ever went", "2026-09-19"),
    "Will Baumann":    ("Needs a new reason, not a bump. 8 months cold", None),
}

def rows(name):
    with open(os.path.join(STATE, name)) as f:
        return list(csv.DictReader(f))

def q(s):
    """Single-quote for SQL, or NULL. [UNKNOWN] is a non-answer, so it is NULL too."""
    if s is None or s == "" or str(s).strip().upper().startswith("[UNKNOWN"):
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def d(s):
    """A date, or NULL."""
    return "NULL" if not s or "UNKNOWN" in str(s).upper() else f"'{s}'::date"

def build():
    people = rows("people.csv")
    threads = {r["person"]: r for r in rows("threads.csv")}

    # A live thread whose person never made it into people.csv is still a live
    # account. Monica Sultan (IWorld) is one today. Carry it rather than lose it,
    # and leave the unknown fields genuinely blank.
    known = {p["name"] for p in people}
    for name, t in threads.items():
        if name in known:
            continue
        people.append({"name": name, "title": "", "company": t["company"], "domain": "",
                       "linkedin_url": "", "email": "", "segment": "brand-operator",
                       "warm_path": "", "evidence": f"Live thread: {t['subject']}",
                       "notes": t["notes"] + "  [not yet in people.csv]"})
    commits = rows("commitments.csv")
    questions = [r for r in rows("questions.csv") if not r["answered_at"]]
    out = []
    w = out.append

    w(f"-- bizDave <- BDAgent, generated {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    w("-- Display rows only. Nothing here sends anything.\n")
    w("begin;\n")

    w(f"-- Clear this bridge's own previous rows so a re-run cannot double up.")
    w(f"delete from activities where user_id = {q(USER)} and meta->>'source' = {q(TAG)};")
    w(f"delete from tasks      where user_id = {q(USER)} and description like '%[{TAG}]%';")
    w(f"delete from deals      where user_id = {q(USER)} and source like {q(TAG + '%')};")
    w(f"delete from pending_actions where user_id = {q(USER)} and channel = 'bdagent' and status = 'pending';\n")

    # --- contacts -----------------------------------------------------------
    w("-- Contacts. Matched on email where there is one, else name + company.")
    for p in people:
        name, company = p["name"], p["company"]
        w("insert into contacts (user_id, name, company, title, role, email, linkedin, "
          "notes, category, source, created_at, updated_at)")
        seg = p["segment"]
        note = (p["notes"] or "")
        note = (note + f"\n\n[{TAG}] segment: {seg}").strip()
        w(f"select {q(USER)}, {q(name)}, {q(company)}, {q(p['title'])}, {q(p['title'])}, "
          f"{q(p['email'])}, {q(p['linkedin_url'])}, {q(note)}, "
          f"{q(CATEGORY.get(seg, 'Uncategorized'))}, "
          f"{q('gmail_import' if p.get('email') else 'manual')}, now(), now()")
        # `c.email = NULL` is never true, so a person with no address must be
        # matched on name + company alone or the row duplicates on every run.
        match = (f"c.email = {q(p['email'])} or " if p.get("email") else "")
        w(f"where not exists (select 1 from contacts c where c.user_id = {q(USER)} "
          f"and ({match}(c.name = {q(name)} and c.company = {q(company)})));")
    w("")

    # --- deals --------------------------------------------------------------
    w("-- Deals. One per live account. Value and probability stay NULL — Gate 5:")
    w("-- a number nobody has agreed is not a number worth showing.")
    for p in people:
        name = p["name"]
        if name not in STAGE:
            continue
        stage, seg = STAGE[name]
        step, step_due = NEXT.get(name, (None, None))
        t = threads.get(name)
        waiting = t["waiting_on"] if t else None
        note = (p["evidence"] or "") + ("\n\n" + p["notes"] if p["notes"] else "")
        w("insert into deals (user_id, name, contact_id, company, stage, status, currency, "
          "next_step, next_step_date, notes, source, created_at, updated_at, last_activity_at, waiting_until)")
        w(f"select {q(USER)}, {q(p['company'] + ' — ' + name)}, "
          f"(select id from contacts where user_id = {q(USER)} and name = {q(name)} limit 1), "
          f"{q(p['company'])}, '{stage}', 'open', 'USD', {q(step)}, {d(step_due)}, {q(note)}, "
          f"{q(TAG + ':' + seg)}, now(), now(), "
          f"{d(t['last_touched']) if t else 'NULL'}, "
          f"{d(step_due) if waiting == 'them' else 'NULL'};")
    w("")

    # --- activities ---------------------------------------------------------
    w("-- Activities. The last real touch on each thread, so a deal page has a history.")
    for name, t in threads.items():
        w("insert into activities (user_id, contact_id, deal_id, kind, body, meta, occurred_at, created_at, updated_at)")
        w(f"select {q(USER)}, "
          f"(select id from contacts where user_id = {q(USER)} and name = {q(name)} limit 1), "
          f"(select id from deals where user_id = {q(USER)} and company = {q(t['company'])} "
          f"and source like {q(TAG + '%')} limit 1), "
          f"'email', {q(t['subject'] + ' — ' + t['notes'])}, "
          f"jsonb_build_object('source', {q(TAG)}, 'thread_id', {q(t['thread_id'])}, "
          f"'touch', {q(t['touch_number'])}, 'waiting_on', {q(t['waiting_on'])}), "
          f"{d(t['last_touched'])}, now(), now();")
    w("")

    # --- tasks from commitments --------------------------------------------
    w("-- Tasks. What David promised, in his own words — the phrase is the point.")
    for c in commits:
        overdue = c["status"].upper() == "OVERDUE"
        title = f"{c['what']} — {c['person']}" + (f" ({c['company']})" if c["company"] else "")
        desc = (f"[{TAG}] Promised {c['promised_on']}: \"{c['promised_words']}\"\n"
                f"Due {c['due']}." + (" OVERDUE." if overdue else ""))
        w("insert into tasks (user_id, title, description, due_date, status, priority, source, "
          "deal_id, created_at, updated_at)")
        w(f"select {q(USER)}, {q(title)}, {q(desc)}, {d(c['due'])}, 'todo', "
          f"'{'high' if overdue else 'medium'}', 'email', "
          + (f"(select id from deals where user_id = {q(USER)} and company = {q(c['company'])} "
             f"and source like {q(TAG + '%')} limit 1)" if q(c["company"]) != "NULL" else "NULL")
          + ", now(), now();")
    w("")

    # --- questions ----------------------------------------------------------
    w("-- Gate 4: questions reach him where he actually is, not in a terminal.")
    for x in questions:
        summary = f"{x['about']} — {x['question']}"
        payload = (f'{{"source":"{TAG}","question_id":"{x["id"]}","agent":"{x["agent"]}",'
                   f'"blocking":"{x["blocking"]}"}}')
        w("insert into pending_actions (user_id, channel, action_type, payload, summary, status, expires_at, created_at)")
        w(f"values ({q(USER)}, 'bdagent', 'answer_question', {q(payload)}::jsonb, "
          f"{q(summary)}, 'pending', now() + interval '30 days', now());")
    w("")
    w("commit;")

    counts = (len(people), len([p for p in people if p['name'] in STAGE]),
              len(threads), len(commits), len(questions))
    w(f"\n-- {counts[0]} contacts, {counts[1]} deals, {counts[2]} activities, "
      f"{counts[3]} tasks, {counts[4]} questions. Nothing was sent.")
    return "\n".join(out)


def main():
    sql = build()
    if "--execute" not in sys.argv:
        print(sql)
        return
    url = os.environ.get("BIZDAVE_DB_URL")
    if not url:
        sys.exit("BIZDAVE_DB_URL is not set. Without it this script only prints SQL.\n"
                 "Get the connection string from the Supabase project behind bizDave.")
    import psycopg2
    with psycopg2.connect(url) as conn, conn.cursor() as cur:
        cur.execute(sql)
    print("bizDave updated.")


if __name__ == "__main__":
    main()
