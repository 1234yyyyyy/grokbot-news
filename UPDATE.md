# Grok Bot 情報站：每日更新步驟

資料來源是 `/workspace/grokbot-intel/index.csv`，欄位為 date, platform, category, title, link, summary。網站目錄 `/workspace/grokbot-intel/site` 本身就是 git repo（1234yyyyyy/grokbot-news，main 分支，GitHub Pages 從根目錄發布）。

1. **追加新資料列**到 `../index.csv`（不要改舊的列）。日期一律用台北時間 `YYYY-MM-DD`，查不到就寫 `未知`。category 只能是 官方更新／新聞／使用分享／應用案例／教學／問題回報。只收實際找到的真實連結。
2. **去重**：依 link 去重，有重複會列出並保留第一筆：
   ```bash
   cd /workspace/grokbot-intel && python3 -c "
   import csv;R=list(csv.DictReader(open('index.csv',encoding='utf-8')));s=set();o=[]
   for r in R:
       if r['link'] in s: print('dup',r['link']); continue
       s.add(r['link']);o.append(r)
   w=csv.DictWriter(open('index.csv','w',newline='',encoding='utf-8'),fieldnames=R[0].keys());w.writeheader();w.writerows(o);print(len(o))"
   ```
3. **可參考標記**（選用）：把新的「可參考」項目連結逐行加到 `site/ref_links.txt`。
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
