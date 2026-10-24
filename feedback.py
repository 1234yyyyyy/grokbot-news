#!/usr/bin/env python3
"""讀 GitHub not-important issues -> /workspace/grokbot-intel/not_important.csv（冪等，以 link 去重）"""
import csv, json, re, subprocess, os
OUT = "/workspace/grokbot-intel/not_important.csv"
LIB = "/workspace/grokbot-intel/index.csv"
lib = {r["link"]: r for r in csv.DictReader(open(LIB, encoding="utf-8"))} if os.path.exists(LIB) else {}
js = json.loads(subprocess.check_output(["gh","issue","list","-R","1234yyyyyy/grokbot-news","--label","not-important","--state","all","--limit","500","--json","number,title,body,createdAt,state"]))
STOP = set("the a an of to and in on for with is are by from at grok bot app 的 了 和 與 在 是".split())
def kw(t):
    ws = re.findall(r"[A-Za-z][A-Za-z0-9.+-]{2,}|[\u4e00-\u9fff]{2,}", t)
    return " ".join(dict.fromkeys(w.lower() for w in ws if w.lower() not in STOP))[:200]
rows = {}
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT, encoding="utf-8")): rows[r["link"]] = r
for iss in js:
    d = iss["createdAt"][:10]
    for line in (iss.get("body") or "").splitlines():
        m = re.search(r"https?://\S+", line)
        if not m: continue
        link = m.group(0).rstrip(").,")
        mm = re.match(r"\s*-\s*\[([^\]]*)\]\s*(.*?)\s*\|\s*https?://", line)
        cat, title = (mm.group(1), mm.group(2)) if mm else ("", "")
        L = lib.get(link, {})
        title = title or L.get("title", ""); cat = cat or L.get("category", "")
        rows.setdefault(link, {"date": d, "title": title, "link": link, "category": cat,
            "keywords": kw(title + " " + L.get("summary", "")), "platform": L.get("platform", ""), "issue": iss["number"]})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date","title","link","category","keywords","platform","issue"]); w.writeheader()
    for r in sorted(rows.values(), key=lambda r: r["date"]): w.writerow({k: r.get(k, "") for k in w.fieldnames})
print(f"{len(rows)} not-important items; open issues: {[i['number'] for i in js if i['state']=='OPEN']}")
