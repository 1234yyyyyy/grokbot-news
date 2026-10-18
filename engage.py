# Apply engagement thresholds to ../index.csv. Inputs: ../x_metrics.json (id -> public_metrics from x get_posts_by_ids),
# ../other_metrics.json (link -> {"score":..,"comments":..} for Reddit, {"views":..} for YouTube, {"likes":..} for Threads).
# Adds columns engagement, score; moves failing rows to ../dropped.csv (with reason). Idempotent.
import csv, json, os, re
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D, "..")
X = json.load(open(f"{P}/x_metrics.json")); O = json.load(open(f"{P}/other_metrics.json"))
OFFICIAL_X = {"grok", "bot", "xai", "spacexai", "cursor_ai"}
def k(n): return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)
def judge(r):
    l, pl = r["link"], r["platform"]
    if "/i/trending/" in l: return True, "X 趨勢摘要（豁免）", 1000, ""
    m = re.match(r"https://x\.com/([^/]+)/status/(\d+)", l)
    if m:
        if m.group(1).lower() in OFFICIAL_X: return True, "官方帳號（豁免）", 1000, ""
        pm = X.get(m.group(2))
        if not pm: return False, "", 0, "X 數據抓不到"
        lk, im = pm["like_count"], pm.get("impression_count", 0)
        e = f'♥{k(lk)} · 🔁{k(pm["repost_count"])} · 💬{k(pm["reply_count"])} · 👁 {k(im)}'
        return (lk >= 50 or im >= 5000), e, lk + im / 100, f"X 未達門檻（♥{lk}、👁{im}；需 ♥≥50 或 👁≥5000）"
    if pl == "網站": return True, "官方文件／部落格（豁免）", 1000, ""
    if "threads.com/@grok/" in l: return True, "官方帳號（豁免）", 1000, ""
    o = O.get(l)
    if pl == "Reddit":
        if not o: return False, "", 0, "Reddit 數據抓不到"
        return (o["score"] >= 20 or o["comments"] >= 10), f'▲{o["score"]} · 💬{o["comments"]}', o["score"] * 5 + o["comments"] * 5, f'Reddit 未達門檻（▲{o["score"]}、💬{o["comments"]}；需 ▲≥20 或 💬≥10）'
    if pl == "YouTube":
        if not o: return False, "", 0, "YouTube 觀看數抓不到"
        return o["views"] >= 1000, f'👁 {k(o["views"])}', o["views"] / 100, f'YouTube 未達門檻（👁{o["views"]}）'
    if pl == "Threads":
        if not o: return False, "", 0, "Threads 讚數無法讀取（未登入）"
        return o["likes"] >= 20, f'♥{o["likes"]}' + (f' · 💬{o["replies"]}' if "replies" in o else ""), o["likes"], f'Threads 未達門檻（♥{o["likes"]}）'
    return False, "", 0, "無法判定平台"
rows = list(csv.DictReader(open(f"{P}/index.csv", encoding="utf-8")))
dropped = list(csv.DictReader(open(f"{P}/dropped.csv", encoding="utf-8"))) if os.path.exists(f"{P}/dropped.csv") else []
dl = {r["link"] for r in dropped}; keep = []
for r in rows:
    if r["link"] in O and "date" in O[r["link"]]: r["date"] = O[r["link"]]["date"]
    ok, e, s, why = judge(r); r["engagement"], r["score"] = e, f"{s:.0f}"
    if ok: keep.append(r)
    elif r["link"] not in dl: r["reason"] = why; dropped.append(r); dl.add(r["link"])
F = ["date", "platform", "category", "title", "link", "summary", "engagement", "score"]
w = csv.DictWriter(open(f"{P}/index.csv", "w", newline="", encoding="utf-8"), fieldnames=F, extrasaction="ignore"); w.writeheader(); w.writerows(keep)
w = csv.DictWriter(open(f"{P}/dropped.csv", "w", newline="", encoding="utf-8"), fieldnames=F + ["reason"], extrasaction="ignore"); w.writeheader(); w.writerows(dropped)
print("kept", len(keep), "dropped", len(dropped))
