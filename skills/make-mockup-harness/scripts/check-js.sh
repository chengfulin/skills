#!/usr/bin/env bash
# 用法：check-js.sh <mockup.html>
# 以 node --check 檢查單檔 mockup 內每段 inline <script> 的語法，不執行、不開瀏覽器。
# 每段前補空行，錯誤訊息的行號即 HTML 檔的行號。只抓語法錯，執行期錯誤仍要靠步驟 5 操作驗證。
# 結果最後一行固定為「JS 語法：通過|失敗|未檢查 …」；失敗時 exit 1，沒有 node 時 exit 0 並標未檢查。
set -euo pipefail
f="${1:?mockup html}"
command -v node >/dev/null || { echo "JS 語法：未檢查（找不到 node）"; exit 0; }
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
python3 - "$f" "$tmp" <<'PY'
import re, sys
html, out = open(sys.argv[1], encoding="utf-8").read(), sys.argv[2]
n = 0
for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, re.S | re.I):
    attrs, body = m.group(1), m.group(2)
    if re.search(r"\bsrc\s*=", attrs, re.I):
        continue
    t = re.search(r"\btype\s*=\s*[\"']?([^\"'\s>]+)", attrs, re.I)
    t = t.group(1).lower() if t else ""
    if t and t not in ("module", "text/javascript", "application/javascript"):
        continue  # JSON、template 等非 JS 內容
    n += 1
    pad = "\n" * (html.count("\n", 0, m.start(2)))
    ext = "mjs" if t == "module" else "js"
    open(f"{out}/s{n:02d}.{ext}", "w", encoding="utf-8").write(pad + body)
print(n, file=open(f"{out}/count", "w"))
PY
count="$(cat "$tmp/count")"
[[ "$count" -gt 0 ]] || { echo "JS 語法：通過（無 inline script）"; exit 0; }
fail=0
for s in "$tmp"/s*.*; do
  if ! err="$(node --check "$s" 2>&1)"; then
    fail=$((fail+1))
    echo "$err" | sed -n '1,4p' | sed -E "s#[^ ]*/s[0-9]+\.m?js#$(basename "$f")#"
  fi
done
if [[ "$fail" -gt 0 ]]; then echo "JS 語法：失敗（$count 段中 $fail 段有錯）"; exit 1; fi
echo "JS 語法：通過（$count 段）"
