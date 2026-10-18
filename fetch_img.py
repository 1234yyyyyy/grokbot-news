# Download og:image for each row in ../index.csv -> img/<md5(link)[:12]>.jpg (480px). Placeholder if none. Skips existing.
import csv, re, html, hashlib, os, subprocess, io, sys
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); CSV = os.path.join(D, "..", "index.csv")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
os.makedirs(f"{D}/img", exist_ok=True); os.makedirs(f"{D}/raw", exist_ok=True)
COLORS = {"X":"#222222","Reddit":"#ff4500","YouTube":"#cc0000","Threads":"#555555","網站":"#2c6fbb"}
FONT = [f for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc","/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"] if os.path.exists(f)][0]
def key(link): return hashlib.md5(link.encode()).hexdigest()[:12]
def og(url):
    fn = f"{D}/raw/{key(url)}.html"
    if not os.path.exists(fn): subprocess.run(["curl","-sL","-m","25","-A",UA,"-o",fn,url])
    s = open(fn, errors="ignore").read() if os.path.exists(fn) else ""
    m = re.search(r'<meta[^>]+(?:property|name)="og:image"[^>]+content="([^"]+)"', s) or re.search(r'<meta[^>]+content="([^"]+)"[^>]+(?:property|name)="og:image"', s)
    if not m: return None
    u = html.unescape(m.group(1))
    if u.startswith("//"): u = "https:" + u
    if u.startswith("/"): u = re.match(r"https?://[^/]+", url).group(0) + u
    return u
def placeholder(r, out):
    im = Image.new("RGB", (480, 270), COLORS.get(r["platform"], "#444")); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT, 46); f2 = ImageFont.truetype(FONT, 22)
    for t, f, y in [(r["platform"], f1, 90), ("Grok Bot・" + r["category"], f2, 165)]:
        d.text(((480 - d.textlength(t, font=f)) / 2, y), t, font=f, fill="white")
    im.save(out, "JPEG", quality=82)
force = "--force" in sys.argv
for r in csv.DictReader(open(CSV, encoding="utf-8")):
    out = f"{D}/img/{key(r['link'])}.jpg"
    if os.path.exists(out) and not force: continue
    u = None if "x.com/" in r["link"] else og(r["link"]); ok = False
    if u:
        p = subprocess.run(["curl","-sL","-m","25","-A",UA,u], capture_output=True)
        try:
            im = Image.open(io.BytesIO(p.stdout)); im.load()
            if im.mode in ("RGBA","LA","P"):
                im = im.convert("RGBA"); bg = Image.new("RGB", im.size, (0,0,0)); bg.paste(im, mask=im.split()[-1]); im = bg
            im = im.convert("RGB")
            if im.width > 480: im = im.resize((480, round(im.height*480/im.width)), Image.LANCZOS)
            if im.width >= 200: im.save(out, "JPEG", quality=80, optimize=True); ok = True
        except Exception as e: print("  img fail", r["link"], e)
    if not ok: placeholder(r, out)
    print(("OG " if ok else "PH ") + r["link"])
