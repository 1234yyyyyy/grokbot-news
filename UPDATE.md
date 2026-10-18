# Grok Bot 情報站：每日更新步驟

資料來源是 `/workspace/grokbot-intel/index.csv`，欄位為 date, platform, category, title, link, summary。網站目錄 `/workspace/grokbot-intel/site` 本身就是 git repo（1234yyyyyy/grokbot-news，main 分支，GitHub Pages 從根目錄發布）。

1. **追加新資料列**到 `../index.csv`（不要改舊的列）。日期一律用台北時間 `YYYY-MM-DD`，查不到就寫 `未知`。category 只能是 官方更新／新聞／使用分享／應用案例／教學／問題回報。只收實際找到的真實連結。
2. **去重**（也要排除 `../dropped.csv` 裡已有的連結）：依 link 去重，有重複會列出並保留第一筆：
   ```bash
   cd /workspace/grokbot-intel && python3 -c "
   import csv;R=list(csv.DictReader(open('index.csv',encoding='utf-8')));s=set();o=[]
   for r in R:
       if r['link'] in s: print('dup',r['link']); continue
       s.add(r['link']);o.append(r)
   w=csv.DictWriter(open('index.csv','w',newline='',encoding='utf-8'),fieldnames=R[0].keys());w.writeheader();w.writerows(o);print(len(o))"
   ```
3. **可參考標記**（選用）：把新的「可參考」項目連結逐行加到 `site/ref_links.txt`。

## 互動門檻（每次更新都要套用，2026-10-18 起）

新資料列加進 index.csv 之後、重建之前，要做下面兩件事：
- **抓互動數**
  - X 貼文：用 `x` 的 get_posts_by_ids（`post.fields=public_metrics`），把結果合併進 `../x_metrics.json`（格式：id → public_metrics）。
  - Reddit：抓「網址＋.json」的 score 和 num_comments。這台機器 curl 會被 403 擋、WebFetch 常逾時，抓不到時可用 WebSearch 結果摘要裡的「N points · M comments」，並註明 `src`。
  - YouTube：用 curl 抓頁面，找 `"viewCount"`。
  - Threads：讀得到才記 likes／replies。
  - Reddit、YouTube、Threads 的數據都寫進 `../other_metrics.json`（格式：link → 數值；可加 `date` 校正日期）。
- **套用門檻**：執行 `python3 engage.py`。它會加上 engagement 和 score 欄，把不合格的列連同原因移到 `../dropped.csv`。門檻如下：
  - X：♥≥50 或 👁≥5,000
  - Reddit：▲≥20 或 💬≥10
  - YouTube：👁≥1,000
  - Threads：♥≥20
  - 豁免：X 趨勢摘要、官方帳號（@grok、@bot 等）、平台標為「網站」的官方文件、新聞或部落格
  - 不在豁免名單、又抓不到數據的一律剔除。
- 被剔除的連結要從 `ref_links.txt` 刪掉；`../cases/` 裡有引用到的，加一行註記。
- 網頁排序：先依分類，分類內依 score（互動數）由高到低，再依日期由新到舊。豁免項目的 score 固定為 1000。

4. **縮圖＋重建**：
   ```bash
   cd /workspace/grokbot-intel/site && python3 fetch_img.py && python3 build.py
   ```
   `fetch_img.py` 只處理新連結；抓不到 og:image 會自動產生佔位圖，X 連結一律用佔位圖。`build.py` 會自動帶入筆數和今天日期（台北時間）。
5. **驗證**：`python3 verify.py`。必須印出 `OK`，代表筆數正確、各分類／平台篩選與搜尋都正常、沒有 JS 錯誤，並會更新 `preview.png`。失敗就不要 push。
6. **push 一次**：
   ```bash
   git add -A && git commit -m "update $(TZ=Asia/Taipei date +%F)" && git push origin main
   ```
7. **確認線上已更新**（Pages 通常 1–3 分鐘內生效）。這個指令會等到線上筆數跟本機一樣：
   ```bash
   N=$(grep -o '<h1>[^<]*' index.html); for i in $(seq 40); do curl -s "https://1234yyyyyy.github.io/grokbot-news/?t=$(date +%s)" | grep -q "$N" && { echo live; break; }; sleep 15; done
   ```
