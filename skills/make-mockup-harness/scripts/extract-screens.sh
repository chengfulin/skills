#!/usr/bin/env bash
# 用法：KEYWORDS='詞1|詞2|…' extract-screens.sh <mockup.html>
# 以啟發式規則從單檔 mockup 抽出畫面線索，避免整份讀入 context。
# 實測：Claude Design 單檔版把畫面打包成 JS 字串，data-page / href=# 等 DOM 線索多半抓不到，
# 真正有用的是關鍵字計數——請用 KEYWORDS 帶入該 feature storyboard 的狀態詞、標籤文字、提示文案。
set -euo pipefail
f="${1:?mockup html}"
echo "== file =="; ls -l "$f" | awk '{print $5" bytes"}'; shasum -a 256 "$f" | cut -c1-8
echo "== <title> =="; grep -o -m1 '<title>[^<]*' "$f" | sed 's/<title>//' || true
show() { local label="$1" re="$2" n="${3:-30}"
  echo "== $label =="
  grep -o -E "$re" "$f" | sed 's/^[[:space:]]*//' | sort | uniq -c | sort -rn | head -n "$n" || true; }
show "data-page / data-screen / data-route" 'data-(page|screen|route|view)="[^"]+"'
show "id=page-* / screen-* / view-*" 'id="(page|screen|view|route)[^"]*"'
show "href=#..." 'href="#[^"]{1,40}"'
show "h1 / h2 文字" '<h[12][^>]*>[^<]{1,40}'
show "nav / sidebar / menu 內文字" '<(a|button|li)[^>]*(nav|menu|sidebar|tab)[^>]*>[^<]{1,30}'
show "props 線索" '(defaultRole|skipLogin|data-prop[a-z-]*)' 10
if [[ -n "${KEYWORDS:-}" ]]; then
  echo "== 關鍵字計數（KEYWORDS）=="
  IFS='|' read -ra kws <<< "$KEYWORDS"
  for k in "${kws[@]}"; do printf '%6s  %s\n' "$(grep -o -F -- "$k" "$f" | wc -l | tr -d ' ')" "$k"; done
else
  echo "== 關鍵字計數：未設定 KEYWORDS，略過（建議帶入 storyboard 的狀態詞與標籤文字）=="
fi
