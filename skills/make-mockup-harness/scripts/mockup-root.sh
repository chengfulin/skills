#!/usr/bin/env bash
# 印出 mockup 根目錄的絕對路徑。
# 讀 repo 根的 .make-mockup.json（{"root":"<相對路徑>"}），沒有就用預設 make-mockups。
set -euo pipefail
top="$(git rev-parse --show-toplevel)"
cfg="$top/.make-mockup.json"
root="make-mockups"
if [[ -f "$cfg" ]]; then
  root="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("root","make-mockups"))' "$cfg")"
fi
echo "$top/$root"
