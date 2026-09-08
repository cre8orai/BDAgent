#!/usr/bin/env python3
"""Emit the SQL that tells BizDave there are drafts waiting for David.

BizDave (https://bizdave-personal-hub.lovable.app) already has the right tables,
so nothing new is invented here:

  reply_radar_drafts   BizDave's own draft review queue. status='proposed' is
                       the state its UI shows for "waiting on you".
  pending_actions      its notification / approval inbox.
  tasks                what surfaces on the Today dashboard.

This script only PRINTS SQL. It holds no credentials and touches no database.
The SQL is executed through the Lovable connector by whoever is running the
agent — so every write to David's live app is visible before it happens.

  python3 agents/bizdave.py            # SQL for every draft awaiting review
  python3 agents/bizdave.py --summary  # just the notification row
"""
import csv, os, sys, datetime

PROJECT = "425cdf7c-3348-45f2-a9f7-4176a0a1c808"
USER = "bb9fc520-a65a-4d2a-beb9-39ba6ca6b462"          # david@cre8orglobal.com
GOOGLE_ACCOUNT = "4ab71d07-d760-49c6-8ca1-153099b56db5"
APP = "https://bizdave-personal-hub.lovable.app"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTBOX = os.path.join(ROOT, "agents", "state", "outbox.csv")
COMMITS = os.path.join(ROOT, "agents", "state", "commitments.csv")


def q(s):
    """Single-quote for SQL, or NULL."""
    if s is None or s == "":
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def body(s):
    return (s or "").replace("\\n", "\n")


def main():
    drafts = [r for r in csv.DictReader(open(OUTBOX)) if r["status"] == "draft"]
    commits = list(csv.DictReader(open(COMMITS)))
    overdue = [c for c in commits if c["status"].upper() == "OVERDUE"]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if not drafts:
        print("-- no drafts waiting; nothing to tell BizDave")
        return

    # Urgency drives rank. BizDave sorts ascending, so lower is more urgent.
    def rank(r):
        n = (r["notes"] or "").upper()
        if "URGENT" in n:
            return 10
        if "OVERDUE" in n or "INVESTOR" in n:
            return 20
        if "CONFIRM" in n or "CHECK WITH DAVID" in n:
            return 30
        return 60

    print("-- BizDave: drafts awaiting review, from BDAgent")
    print(f"-- project {PROJECT}")
    print(f"-- generated {now}\n")

    if "--summary" not in sys.argv:
        print("-- 1. the drafts themselves, into BizDave's own review queue")
        vals = []
        for r in sorted(drafts, key=rank):
            reason = f"BDAgent · {r['agent']}" + (f" · {r['notes'][:90]}" if r["notes"] else "")
            linkedin = r["channel"].startswith("linkedin")
            # from_email stays NULL unless it is a genuine address. BizDave can send
            # from this table, and a company name sitting in an address field is how
            # a draft misfires. NULL fails loudly instead.
            subject = r["subject"] or ""
            if linkedin:
                subject = f"[LinkedIn — paste by hand] {r['person']}"
            # gmail_thread_id is NOT NULL in BizDave. LinkedIn and new-thread rows
            # get a synthetic id so they are obviously not Gmail threads.
            tid = r["thread_id"] or f"bdagent-{r['channel']}-{r['id']}"
            vals.append(
                f"  ({q(USER)}, {q(GOOGLE_ACCOUNT)}, {q(tid)}, "
                f"{q(r['person'] + ' · ' + r['company'])}, NULL, {q(subject)}, "
                f"{q((r['notes'] or '')[:180])}, {q('' if linkedin else subject)}, "
                f"{q(body(r['body']))}, "
                f"{rank(r)}, {q(reason)}, 'proposed', now(), now())")
        print("insert into reply_radar_drafts\n"
              "  (user_id, google_account_id, gmail_thread_id, from_name, from_email,\n"
              "   subject, snippet, draft_subject, draft_body, rank, reason, status,\n"
              "   generated_at, updated_at)\nvalues\n" + ",\n".join(vals) + ";\n")

    urgent = [r for r in drafts if "URGENT" in (r["notes"] or "").upper()]
    headline = (f"{len(drafts)} drafts waiting for review"
                + (f" — {urgent[0]['person']} is time-critical" if urgent else ""))
    detail = " · ".join(f"{r['person']} ({r['company']})" for r in sorted(drafts, key=rank)[:6])

    print("-- 2. the notification")
    payload = (f'{{"source":"BDAgent","drafts":{len(drafts)},'
               f'"overdue_commitments":{len(overdue)},'
               f'"repo":"cre8orai/BDAgent",'
               f'"board":"https://claude.ai/code/artifact/575aee6a-a365-4d22-a3b8-4d05c3a3cc9e"}}')
    print("insert into pending_actions\n"
          "  (user_id, channel, action_type, payload, summary, status, expires_at, created_at)\n"
          f"values ({q(USER)}, 'bdagent', 'review_drafts', {q(payload)}::jsonb,\n"
          f"        {q(headline + ' — ' + detail)}, 'pending', now() + interval '7 days', now());\n")

    print("-- 3. so it shows on Today")
    print("insert into tasks (user_id, title, description, due_date, status, priority, source)\n"
          f"values ({q(USER)}, {q(headline)},\n"
          f"        {q(detail + chr(10) + chr(10) + 'Open the board: ' + APP)},\n"
          f"        current_date, 'todo', {q('high' if urgent else 'medium')}, 'manual');")

    print(f"\n-- {len(drafts)} drafts, {len(overdue)} overdue commitments. Nothing was sent.")


if __name__ == "__main__":
    main()
