#!/usr/bin/env python3
"""Turn raw Gmail JSON and a LinkedIn data export into a clean corpus of David's
own prose.

Reads whatever is in voice/raw/:

  * Gmail tool-result JSON  (*.txt / *.json from the Gmail MCP tools)
  * messages.csv            from a LinkedIn "Get a copy of your data" export
  * Invitations.csv         from the same export — outgoing connection notes
  * Connections.csv         from the same export — becomes the warm-path graph

Keeps only messages David actually sent, strips signature blocks and quoted
replies, and writes one JSON file per message to voice/corpus/.

The corpus is gitignored. Only the derived voice/STYLE.md is committed — the
raw mail and the archive never leave this machine.

  python3 voice/ingest.py            # ingest, report
  python3 voice/ingest.py --stats    # ingest, then print style statistics
"""
import csv, glob, hashlib, html, io, json, os, re, sys

ME_EMAIL = "david@cre8orglobal.com"
ME_NAME = "David Feuerstein"

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
RAW, CORPUS = os.path.join(ROOT, "raw"), os.path.join(ROOT, "corpus")

csv.field_size_limit(10 ** 7)

# Everything from here down is signature, not voice.
SIG = re.compile(
    r"(Let'?s Cre8!|\[image: David\]|David Feuerstein\s*\n\s*Founder|"
    r"Meeting Button|\+972-54-440-9813|\[image: __tpx__\])", re.I)
QUOTE = re.compile(
    r"(^On .{0,120}wrote:$|^-{2,}\s*Forwarded message|^From: .+@|"
    r"^_{5,}$|^\s*>{1,}\s)", re.M)


def clean(body):
    body = html.unescape(body or "")
    for pat in (SIG, QUOTE):
        m = pat.search(body)
        if m:
            body = body[:m.start()]
    body = re.sub(r"\n{3,}", "\n\n", body)
    return re.sub(r"[ \t]+\n", "\n", body).strip()


def iso_date(s):
    """LinkedIn is inconsistent: messages are ISO, invitations are '9/2/26, 8:14 AM'."""
    s = (s or "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})", s)
    if m:
        mo, d, y = (int(x) for x in m.groups())
        return f"{y + 2000 if y < 100 else y:04d}-{mo:02d}-{d:02d}"
    return "unknown"


def write(rec):
    rec["date"] = iso_date(rec.get("date"))
    key = (rec.get("id") or "") + rec["body"][:80]
    name = f"{rec['channel']}-{rec['date']}-{hashlib.md5(key.encode()).hexdigest()[:8]}.json"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    json.dump(rec, open(os.path.join(CORPUS, name), "w"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- Gmail ----
def gmail_messages(obj):
    """Both search_threads and get_thread payloads, one shape."""
    if isinstance(obj, dict):
        if "threads" in obj:
            for t in obj["threads"]:
                yield from t.get("messages", [])
        elif "messages" in obj:
            yield from obj["messages"]


def ingest_gmail():
    kept = nobody = 0
    for path in sorted(glob.glob(os.path.join(RAW, "*"))):
        if not path.endswith((".txt", ".json")):
            continue
        if os.path.basename(path) in ("thread-ids.json", "snippets.json"):
            continue
        try:
            obj = json.load(open(path))
        except Exception:
            continue
        for m in gmail_messages(obj):
            if ME_EMAIL not in (m.get("sender") or ""):
                continue
            body = clean(m.get("plaintextBody") or "")
            if len(body) < 40:
                nobody += 1
                continue
            to = m.get("toRecipients") or []
            write({
                "channel": "email", "id": m.get("id"), "date": (m.get("date") or "")[:10],
                "subject": m.get("subject"), "to": to,
                "internal": all("cre8orglobal.com" in a for a in (to or ["x"])),
                "opener": not (m.get("subject") or "").lower().startswith("re:"),
                "body": body,
            })
            kept += 1
    return kept, nobody


# ------------------------------------------------------------- LinkedIn ----
def ingest_linkedin_messages():
    path = os.path.join(RAW, "messages.csv")
    if not os.path.exists(path):
        return 0
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8-sig"))
            if r.get("FROM", "").strip() == ME_NAME and r.get("CONTENT", "").strip()]
    rows.sort(key=lambda r: r.get("DATE", ""))
    first_in_thread, kept = set(), 0
    for r in rows:
        cid = r.get("CONVERSATION ID")
        is_opener = cid not in first_in_thread
        first_in_thread.add(cid)
        body = clean(r["CONTENT"])
        if not body:
            continue
        write({
            "channel": "linkedin", "id": cid, "date": (r.get("DATE") or "")[:10],
            "subject": r.get("CONVERSATION TITLE") or "", "to": [r.get("TO", "")],
            "internal": False, "opener": is_opener, "body": body,
        })
        kept += 1
    return kept


def ingest_linkedin_invites():
    path = os.path.join(RAW, "Invitations.csv")
    if not os.path.exists(path):
        return 0
    kept = 0
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        if r.get("Direction", "").strip() != "OUTGOING":
            continue
        note = (r.get("Message") or "").strip()
        if not note:
            continue
        write({
            "channel": "linkedin-invite", "id": r.get("inviteeProfileUrl"),
            "date": (r.get("Sent At") or "")[:10], "subject": "", "to": [r.get("To", "")],
            "internal": False, "opener": True, "body": note,
        })
        kept += 1
    return kept


def ingest_connections():
    """Connections.csv is not voice — it is Scout's first-degree graph.

    LinkedIn prefixes the file with a Notes: preamble, so find the real header.
    Written to agents/state/ rather than the corpus, and gitignored with it.
    """
    path = os.path.join(RAW, "Connections.csv")
    if not os.path.exists(path):
        return 0
    text = open(path, encoding="utf-8-sig").read().split("\n")
    try:
        start = next(i for i, l in enumerate(text) if l.startswith("First Name"))
    except StopIteration:
        return 0
    rows = list(csv.DictReader(io.StringIO("\n".join(text[start:]))))
    out = os.path.join(REPO, "agents", "state", "connections.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "company", "position", "linkedin_url", "email", "connected_on"])
        for r in rows:
            w.writerow([
                f"{r.get('First Name','')} {r.get('Last Name','')}".strip(),
                r.get("Company", ""), r.get("Position", ""), r.get("URL", ""),
                r.get("Email Address", ""), r.get("Connected On", ""),
            ])
    return len(rows)


# ------------------------------------------------------------------ main ----
def main():
    os.makedirs(CORPUS, exist_ok=True)
    em, nobody = ingest_gmail()
    li = ingest_linkedin_messages()
    inv = ingest_linkedin_invites()
    conn = ingest_connections()

    print(f"email      {em:>5} messages with bodies "
          f"({nobody} search rows had none — snippets only)")
    print(f"linkedin   {li:>5} messages")
    print(f"invites    {inv:>5} connection notes")
    if conn:
        print(f"connections{conn:>5} written to agents/state/connections.csv "
              f"(Scout's first-degree graph)")
    print(f"corpus now holds {len(glob.glob(os.path.join(CORPUS,'*.json')))} messages")
    if "--stats" in sys.argv:
        stats()


def _pct(n, d):
    return f"{100*n//d:>3}%" if d else "  —"


def stats():
    docs = [json.load(open(f)) for f in glob.glob(os.path.join(CORPUS, "*.json"))]
    for ch in ("email", "linkedin", "linkedin-invite"):
        rs = [d for d in docs if d["channel"] == ch and not d["internal"]]
        if not rs:
            continue
        print(f"\n=== {ch}  ({len(rs)} messages) ===")
        for label, sub in (("openers", [r for r in rs if r["opener"]]),
                           ("replies", [r for r in rs if not r["opener"]])):
            if not sub:
                continue
            L = sorted(len(r["body"].split()) for r in sub)
            C = sorted(len(r["body"]) for r in sub)
            print(f"  {label:<8} n={len(L):<5} words: median {L[len(L)//2]}, "
                  f"p90 {L[int(len(L)*.9)]}, max {L[-1]}   chars: median {C[len(C)//2]}")
        for p in ["Let's Cre8", "calendly", "would love", "great to meet", "...",
                  "hello", "Best,", "bump", "follow up", "Shalom"]:
            n = sum(1 for r in rs if p.lower() in r["body"].lower())
            print(f"    {_pct(n,len(rs))}  {n:>4}/{len(rs)}  {p!r}")


if __name__ == "__main__":
    main()
