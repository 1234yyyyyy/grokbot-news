# Build index.html from ../index.csv + img/*.jpg (run fetch_img.py first) + ref_links.txt (「可參考」 links)
import base64, csv, html, os, hashlib, datetime, re
D = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(D, "..", "index.csv"), encoding="utf-8")))
seen = set(); items = []
for r in rows:
    if r["link"] in seen: continue
    seen.add(r["link"]); items.append(r)
REF = {l.strip() for l in open(f"{D}/ref_links.txt", encoding="utf-8") if l.strip()}
def sk(r):  # real dates first (newest), then approximate/unknown
    m = re.match(r"\d{4}-\d{2}-\d{2}", r["date"]); return m.group(0) if m else "0000"
items.sort(key=sk, reverse=True)  # date desc as tiebreaker
CATS = ["官方更新", "新聞", "使用分享", "應用案例", "教學", "問題回報"]
items.sort(key=lambda r: (CATS.index(r["category"]) if r["category"] in CATS else 99, -float(r.get("score") or 0)))  # stable: category, engagement desc, then date desc
N = len(items); TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d")
PLATS = sorted({r["platform"] for r in items}, key=lambda p: ["X","Reddit","Threads","YouTube","網站"].index(p) if p in ["X","Reddit","Threads","YouTube","網站"] else 99)
e = html.escape
def img(link):
    f = f"{D}/img/{hashlib.md5(link.encode()).hexdigest()[:12]}.jpg"
    return "data:image/jpeg;base64," + base64.b64encode(open(f, "rb").read()).decode()
cards = []
for i, r in enumerate(items, 1):
    ref = r["link"] in REF
    meta = f'{r["platform"]}・{r["category"]}・{r["date"]}'
    tags = f'#ca-{r["category"]} #pl-{r["platform"]} ' + ("#可參考 " if ref else "")
    badge = '<span class="b">可參考</span>' if ref else ""
    cards.append(f'<a class="c" data-cat="{e(r["category"])}" href="{e(r["link"])}" target="_blank" rel="noopener"><img src="{img(r["link"])}" alt="{e(r["title"])}" loading="lazy"><div class="t"><label class="ni"><input type="checkbox" class="nic">不重要</label><div class="n">{i}. {e(r["title"])}{badge}</div><div class="m">{e(meta)}</div><div class="eg">{e(r.get("engagement",""))}</div><p>{e(r["summary"])}</p><span class="k">{e(tags)} {e(r["link"])}</span></div></a>')
cb = '<button data-k="" class=on>全部</button>' + "".join(f'<button data-k="#ca-{c}">{c}</button>' for c in CATS) + '<button data-k="#可參考">★ 可參考</button>'
pb = '<button data-p="" class=on>所有平台</button>' + "".join(f'<button data-p="#pl-{e(p)}">{e(p)}</button>' for p in PLATS)
CSS = open(f"{D}/style.css", encoding="utf-8").read()
JS = open(f"{D}/app.js", encoding="utf-8").read()
H = f'''<!DOCTYPE html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Grok Bot 情報站</title><style>
{CSS}</style></head>
<body><h1>Grok Bot 情報站・{N} 則</h1><div class="s">{TODAY} 更新（台北時間）・Grok Bot 桌面助理 App 的官方更新、新聞與使用者分享・依分類排列，分類內依互動數再依日期・只收達互動門檻或官方／新聞來源・點卡片看原始來源</div><div class="f" id="f"><div class="sb"><input id="q" type="search" placeholder="搜尋關鍵字（例：額度、家庭、routine、信箱）" autocomplete="off"><button id="qc" type="button">清除</button></div>{cb}<div class="pr">{pb}<span class="cnt" id="cnt">{N} 則</span></div></div><div id="em">找不到符合的項目，換個關鍵字試試</div><div class="g">{"".join(cards)}</div><button id="nib" type="button" style="display:none">送出不重要清單（0）</button><script>
{JS}
</script></body></html>'''
open(f"{D}/index.html", "w", encoding="utf-8").write(H)
print(N, len(H))
