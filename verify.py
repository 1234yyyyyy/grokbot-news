# Headless check of index.html: counts, filters, search, clear, JS errors; writes preview.png
import os, csv
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
rows = {r["link"]: r for r in csv.DictReader(open(os.path.join(D, "..", "index.csv"), encoding="utf-8"))}
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome"); pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("pageerror", lambda x: errs.append(str(x))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.goto("file://" + D + "/index.html")
    vis = lambda: pg.locator(".c:not(.h)").count()
    assert vis() == len(rows), (vis(), len(rows))
    for c in ["官方更新","新聞","使用分享","應用案例","教學","問題回報"]:
        pg.click(f'#f button[data-k="#ca-{c}"]'); exp = sum(r["category"] == c for r in rows.values()); assert vis() == exp, (c, vis(), exp); print(c, exp)
    pg.click('#f button[data-k="#可參考"]'); print("可參考", vis()); assert vis() == pg.locator(".c .b").count()
    pg.click('#f button[data-k=""]')
    for pl in sorted({r["platform"] for r in rows.values()}):
        pg.click(f'#f button[data-p="#pl-{pl}"]'); exp = sum(r["platform"] == pl for r in rows.values()); assert vis() == exp, (pl, vis(), exp); print(pl, exp)
    pg.click('#f button[data-k="#ca-問題回報"]'); pg.click('#f button[data-p="#pl-Reddit"]')
    exp = sum(r["platform"] == "Reddit" and r["category"] == "問題回報" for r in rows.values()); assert vis() == exp; print("問題回報+Reddit", exp)
    pg.click('#f button[data-k=""]'); pg.click('#f button[data-p=""]')
    pg.fill("#q", "額度"); print("search 額度", vis()); assert 0 < vis() < len(rows)
    pg.fill("#q", "zzzqqq"); assert vis() == 0 and pg.is_visible("#em")
    pg.click("#qc"); assert vis() == len(rows)
    assert pg.locator(".c .eg").count()==len(rows) and all(t.strip() for t in pg.locator(".c .eg").all_inner_texts()), "engagement missing"
    pg.screenshot(path=f"{D}/preview.png", full_page=True)
    b.close()
print("JS errors:", errs); assert not errs; print("OK")
