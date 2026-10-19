#!/usr/bin/env bash
# 用法：serve-mockup.sh <slug> <N> [port]
# 以本機 http server 提供凍結的 mockup（mockups/v<N>/index.html），供 Chrome 以最上層文件開啟做操作驗證。
# 請用 Bash 的 run_in_background 執行；結束時 kill 該 PID 或 lsof -ti:<port> | xargs kill。
set -euo pipefail
slug="${1:?slug}"; n="${2:?version}"; port="${3:-8765}"
base="$(bash "$(dirname "$0")/mockup-root.sh")"
dir="$base/$slug/mockups/v$n"
[[ -f "$dir/index.html" ]] || { echo "找不到 $dir/index.html" >&2; exit 2; }
if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "port $port 已被占用；若是上次殘留：lsof -ti:$port | xargs kill" >&2; exit 3
fi
echo "serving $dir at http://127.0.0.1:$port/index.html"
cd "$dir" && exec python3 -m http.server "$port" --bind 127.0.0.1
