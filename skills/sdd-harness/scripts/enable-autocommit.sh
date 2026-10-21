#!/usr/bin/env bash
# 啟用 spec-kit git extension 的階段 auto-commit。
#
# spec-kit 0.8.17 出廠的 git-config.yml 把每個事件都設為 enabled: false，
# 且 auto-commit.sh 的 default fallback 只在事件段落「不存在」時生效，
# 所以必須逐項把 after_* 改為 enabled: true，並順帶換成慣例式 commit 訊息。
#
# git-config.yml 會被 spec-kit 的 auto-commit.sh 逐行 shell 解析：
# 事件鍵固定 2 空格縮排、enabled:/message: 固定 4 空格縮排——本腳本只替換
# 目標行內容，不動任何縮排與結構。重複執行安全（冪等）。
# 相容 macOS 內建 bash 3.2 與 BWK awk（不用 declare -A / gawk 擴充）。
#
# 用法: enable-autocommit.sh [git-config.yml 路徑]
#       預設 .specify/extensions/git/git-config.yml
set -euo pipefail

CONFIG="${1:-.specify/extensions/git/git-config.yml}"
[ -f "$CONFIG" ] || { echo "錯誤：找不到 $CONFIG（git extension 尚未安裝？先跑 specify extension add git）。" >&2; exit 1; }

# 需求對應的 commit 點：constitution/specify/clarify/plan/tasks/analyze/implement 各階段完成後
EVENTS="after_constitution after_specify after_clarify after_plan after_tasks after_analyze after_implement"

message_for() {
    case "$1" in
        after_constitution) echo "docs(sdd): 制定專案憲章（constitution）" ;;
        after_specify)      echo "docs(sdd): 建立功能規格（specify）" ;;
        after_clarify)      echo "docs(sdd): 釐清規格（clarify）" ;;
        after_plan)         echo "docs(sdd): 建立實作計畫（plan）" ;;
        after_tasks)        echo "docs(sdd): 產生任務清單（tasks）" ;;
        after_analyze)      echo "docs(sdd): 一致性分析修正（analyze）" ;;
        after_implement)    echo "feat(sdd): 完成功能實作（implement）" ;;
        *) echo "" ;;
    esac
}

MAPFILE=$(mktemp)
for e in $EVENTS; do printf '%s\t%s\n' "$e" "$(message_for "$e")"; done > "$MAPFILE"

TMP=$(mktemp)
awk -v mapfile="$MAPFILE" '
BEGIN {
    while ((getline line < mapfile) > 0) {
        tab = index(line, "\t")
        if (tab > 0) msgs[substr(line, 1, tab - 1)] = substr(line, tab + 1)
    }
    close(mapfile)
    in_auto = 0; cur = ""
}
/^auto_commit:/            { in_auto = 1; cur = ""; print; next }
in_auto && /^[a-zA-Z#]/    { in_auto = 0; cur = "" }   # 離開 auto_commit 區段
{
    if (in_auto && $0 ~ /^  [a-z_]+:[ \t]*$/) {        # 事件段落起點（鍵後無值）
        cur = $0; sub(/^  /, "", cur); sub(/:[ \t]*$/, "", cur)
    }
    if (in_auto && cur != "" && (cur in msgs)) {
        if ($0 ~ /^    enabled:/) { print "    enabled: true"; next }
        if ($0 ~ /^    message:/) { print "    message: \"" msgs[cur] "\""; next }
    }
    print
}' "$CONFIG" > "$TMP"

mv "$TMP" "$CONFIG"
rm -f "$MAPFILE"

# 驗證：每個目標事件都必須是 enabled: true，否則以非零退出
FAIL=0
for e in $EVENTS; do
    if ! awk -v ev="$e" '
        $0 ~ "^  " ev ":" { found = 1; next }
        found && /^    enabled: true/ { ok = 1; exit }
        found && /^  [a-z_]/ { exit }
        END { exit ok ? 0 : 1 }' "$CONFIG"; then
        echo "驗證失敗：$e 未啟用" >&2
        FAIL=1
    fi
done
[ "$FAIL" -eq 0 ] || exit 1

echo "已啟用階段 auto-commit：$EVENTS" >&2
