#!/usr/bin/env python3
"""Turn raw Gmail tool-result JSON into a clean corpus of David's own prose.

Reads every *.txt / *.json in voice/raw/ (whatever the Gmail MCP tool saved
there), keeps only messages David actually sent, strips the signature block
and any quoted reply, and writes one text file per message to voice/corpus/.

The corpus is gitignored. Only the derived STYLE.md is committed — the raw
mail never leaves this machine.

  python3 voice/ingest.py            # ingest, report
  python3 voice/ingest.py --stats    # ingest, then print style statistics
"""
import json, glob, os, re, sys, html, hashlib

ME = "david@cre8orglobal.com"
ROOT = os.path.dirname(os.path.abspath(__file__))
RAW, CORPUS = os.path.join(ROOT, "raw"), os.path.join(ROOT, "corpus")

# Everything from here down is signature, not voice.
SIG = re.compile(
    r"(Let'?s Cre8!|\[image: David\]|David Feuerstein\s*\n\s*Founder|"
    r"Meeting Button|\+972-54-440-9813|\[image: __tpx__\])", re.I)
QUOTE = re.compile(
    r"(^On .{0,120}wrote:$|^-{2,}\s*Forwarded message|^From: .+@|"
    r"^_{5,}$|^\s*>{1,}\s)", re.M)

def clean(body: str) -> str:
    body = html.unescape(body or "")
    for pat in (SIG, QUOTE):
        m = pat.search(body)
        if m:
            body = body[:m.start()]
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = re.sub(r"[ \t]+\n", "\n", body)
    return body.strip()

def messages(obj):
    """Both search_threads and get_thread payloads, one shape."""
    if isinstance(obj, dict):
        if "threads" in obj:
            for t in obj["threads"]:
                yield from t.get("messages", [])
        elif "messages" in obj:
            yield from obj["messages"]

def main():
    os.makedirs(CORPUS, exist_ok=True)
    kept = skipped = 0
    for path in sorted(glob.glob(os.path.join(RAW, "*"))):
        if os.path.basename(path) in ("thread-ids.json", "snippets.json"):
            continue
        try:
            obj = json.load(open(path))
        except Exception:
            continue
        for m in messages(obj):
            if ME not in (m.get("sender") or ""):
                continue
            body = clean(m.get("plaintextBody") or "")
            if len(body) < 40:          # snippet-only rows carry no body
                skipped += 1
                continue
            rec = {
                "id": m.get("id"),
                "date": (m.get("date") or "")[:10],
                "subject": m.get("subject"),
                "to": m.get("toRecipients") or [],
                "cc": m.get("ccRecipients") or [],
                "internal": all("cre8orglobal.com" in a
                                for a in (m.get("toRecipients") or ["x"])),
                "body": body,
            }
            name = f"{rec['date']}-{hashlib.md5((rec['id'] or body).encode()).hexdigest()[:8]}.json"
            json.dump(rec, open(os.path.join(CORPUS, name), "w"),
                      ensure_ascii=False, indent=1)
            kept += 1
    total = len(glob.glob(os.path.join(CORPUS, "*.json")))
    print(f"ingested {kept} messages with bodies "
          f"({skipped} rows had no body — snippet-only search results)")
    print(f"corpus now holds {total} messages at {CORPUS}")
    if "--stats" in sys.argv:
        stats()

def stats():
    docs = [json.load(open(f)) for f in glob.glob(os.path.join(CORPUS, "*.json"))]
    ext = [d for d in docs if not d["internal"]]
    if not ext:
        print("\nno external messages in corpus yet"); return
    words = [len(d["body"].split()) for d in ext]
    words.sort()
    print(f"\n{len(ext)} external messages")
    print(f"length: median {words[len(words)//2]} words, "
          f"p90 {words[int(len(words)*0.9)]}, max {words[-1]}")
    opens = {}
    for d in ext:
        first = d["body"].split("\n")[0].strip()
        opens[first[:40]] = opens.get(first[:40], 0) + 1
    print("\nmost repeated openers:")
    for k, v in sorted(opens.items(), key=lambda x: -x[1])[:12]:
        print(f"  {v:>3}  {k}")
    for phrase in ["Let's Cre8", "link in my signature", "calendly", "follow up",
                   "bump", "Hope you", "great to", "...", "Best,", ":)", "revert"]:
        n = sum(1 for d in ext if phrase.lower() in d["body"].lower())
        print(f"  {n:>3}/{len(ext)}  contains {phrase!r}")

if __name__ == "__main__":
    main()
