#!/usr/bin/env bash
# 並行模式的 worktree 管理（implement-loop.md「並行模式」使用）。
#
#   wave-worktree.sh add    <專案根> <NNN> <k> <unit...>   每個 unit 從 HEAD 建一個 worktree
#   wave-worktree.sh merge  <專案根> <NNN> <k> <feature 目錄> <unit...>
#                                                        依序把各 unit 的變更套回專案根（不 commit）
#   wave-worktree.sh status <專案根> <NNN>                列出殘留的 unit 分支與其變更檔（續跑用）
#   wave-worktree.sh clean  <專案根> <NNN>                移除本 feature 全部 worktree 與 unit 分支
#
# worktree 放在專案根之外：${TMPDIR:-/tmp}/sdd-wt-<NNN>/w<k>-<unit>，分支 sdd-wave/<NNN>-w<k>-<unit>。
# 被 gitignore 的單檔（.env、.specify/feature.json 等，<1MB）複製進 worktree；
# 依賴目錄（node_modules、.venv、venv）以 symlink 共用，合併時排除。依賴只裝在專案根：
# add 前專案根缺依賴目錄就中止（退出碼 4）；merge 後若出現缺依賴的 manifest 印 deps=missing。
#
# 波次（wave）是本 skill 自訂的執行單位（非慣用語，詳見 README「名詞：批次與波次」）：
# 由 task-plan.py next 排出，每個 phase 一條 lane（＝這裡的 unit），各 unit 在自己的
# worktree 同時實作、合併後一起過閘門、一個波次一個 commit。0P 規劃裡的「批次」只是
# 衝突分層的統計，不對應任何 worktree。
set -euo pipefail

BASE="${TMPDIR:-/tmp}"; BASE="${BASE%/}"
cmd="${1:-}"; root="${2:-}"; nnn="${3:-}"
[ -n "$cmd" ] && [ -n "$root" ] && [ -n "$nnn" ] || { sed -n '2,14p' "$0"; exit 2; }
WT_DIR="$BASE/sdd-wt-$nnn"
G() { git -c core.quotepath=off -C "$@"; }

# 版控中有 manifest、專案根卻沒有對應依賴目錄的位置（每行一個缺的目錄）。
# worktree 只 symlink 專案根已存在的依賴目錄；缺的話 lane 會在 worktree 自己安裝，
# 合併時帶不回專案根，整合測試就跑不起來。
missing_deps() {
    G "$1" ls-files -- 'package.json' '*/package.json' 'uv.lock' '*/uv.lock' 'poetry.lock' '*/poetry.lock' \
    | while IFS= read -r m; do
        d=$(dirname "$m"); [ "$d" = . ] && d="" || d="$d/"
        case "$m" in
            *package.json) grep -qE '"(dev)?[dD]ependencies"' "$1/$m" 2>/dev/null \
                               && [ ! -d "$1/${d}node_modules" ] && echo "${d}node_modules" ;;
            *) [ -d "$1/${d}.venv" ] || [ -d "$1/${d}venv" ] || echo "${d}.venv" ;;
        esac
        :  # 迴圈狀態恆為 0，避免 pipefail 讓呼叫端的 $(…) 在 set -e 下中止
    done
}

case "$cmd" in
add)
    k="$4"; shift 4
    miss=$(missing_deps "$root" | paste -sd, -)
    if [ -n "$miss" ]; then
        echo "error=deps_missing ${miss}（先在專案根安裝依賴再建 worktree）"; exit 4
    fi
    mkdir -p "$WT_DIR"
    for u in "$@"; do
        wt="$WT_DIR/w$k-$u"; br="sdd-wave/$nnn-w$k-$u"
        if [ -d "$wt" ]; then echo "unit=$u path=$wt status=exists"; continue; fi
        G "$root" worktree add -q -b "$br" "$wt" HEAD
        G "$root" rev-parse HEAD > "$wt.base"
        : > "$wt.links"
        while IFS= read -r p; do
            case "$p" in
                .codegraph/*|*/.codegraph/*) ;;
                */) d="${p%/}"; case "$(basename "$d")" in
                        node_modules|.venv|venv)
                            mkdir -p "$wt/$(dirname "$d")"; ln -s "$root/$d" "$wt/$d"; echo "$d" >> "$wt.links" ;;
                    esac ;;
                *) if [ -f "$root/$p" ] && [ "$(wc -c < "$root/$p")" -lt 1048576 ]; then
                       mkdir -p "$wt/$(dirname "$p")"; cp -p "$root/$p" "$wt/$p"
                   fi ;;
            esac
        done < <(G "$root" ls-files --others --ignored --exclude-standard --directory)
        echo "unit=$u path=$wt branch=$br links=$(wc -l < "$wt.links" | tr -d ' ')"
    done
    ;;
merge)
    k="$4"; fdir="${5%/}"; shift 5
    for u in "$@"; do
        wt="$WT_DIR/w$k-$u"; br="sdd-wave/$nnn-w$k-$u"
        [ -d "$wt" ] || { echo "unit=$u status=missing"; continue; }
        base=$(cat "$wt.base")
        G "$wt" add -A
        if [ -s "$wt.links" ]; then
            while IFS= read -r l; do G "$wt" rm -q --cached --ignore-unmatch "$l"; done < "$wt.links"
        fi
        G "$wt" diff-index --quiet --cached HEAD \
            || G "$wt" -c user.name=sdd-harness -c user.email=sdd-harness@localhost commit -q -m "wave $u"
        # 歸屬檔案從建立時的基準算；套用只取上次合併之後的增量（同一 worktree 續作後
        # 重跑 merge 不會重複套用）。feature 目錄（tasks.md、狀態檔、設計文件）不套用，列為越界
        files=$(G "$wt" diff --name-only "$base" HEAD)
        forbidden=$(printf '%s\n' "$files" | grep -E "^$fdir/" || true)
        from=$(cat "$wt.merged" 2>/dev/null || echo "$base")
        patch="$wt.patch"
        G "$wt" diff --binary "$from" HEAD -- . ":(exclude)$fdir" > "$patch"
        ok=$(printf '%s\n' "$files" | grep -vE "^$fdir/" | paste -sd, - || true)
        if [ ! -s "$patch" ]; then
            echo "unit=$u status=$([ -f "$wt.merged" ] && echo merged || echo empty) files=$ok forbidden=${forbidden//$'\n'/,}"
        elif G "$root" apply --index --check "$patch" 2>"$wt.err"; then
            G "$root" apply --index "$patch"
            G "$wt" rev-parse HEAD > "$wt.merged"
            echo "unit=$u status=merged files=$ok forbidden=${forbidden//$'\n'/,}"
        else
            echo "unit=$u status=conflict files=$ok reason=$(head -1 "$wt.err")"
        fi
    done
    # 合併帶進新的 manifest（如首波由 lane 建立專案骨架）時，依賴只裝在了 worktree
    miss=$(missing_deps "$root" | paste -sd, -)
    [ -z "$miss" ] || echo "deps=missing ${miss}（整合測試前在專案根安裝依賴）"
    ;;
status)
    for wt in "$WT_DIR"/w*; do
        [ -d "$wt" ] || continue
        files=$( { G "$wt" diff --name-only "$(cat "$wt.base")"; G "$wt" ls-files --others --exclude-standard; } \
                 | sort -u | grep -vxFf "$wt.links" | paste -sd, - || true)
        [ -f "$wt.merged" ] && files="${files}（已合併至 $(cut -c1-7 "$wt.merged")）"
        echo "worktree=$(basename "$wt") path=$wt files=${files:-（無變更）}"
    done
    ;;
clean)
    if [ -d "$WT_DIR" ]; then
        for wt in "$WT_DIR"/w*; do
            [ -d "$wt" ] && G "$root" worktree remove --force "$wt"
        done
        rm -rf "$WT_DIR"
    fi
    G "$root" worktree prune
    G "$root" for-each-ref --format='%(refname:short)' "refs/heads/sdd-wave/$nnn-*" \
        | while IFS= read -r br; do G "$root" branch -q -D "$br"; done
    echo "clean=ok"
    ;;
*) sed -n '2,14p' "$0"; exit 2 ;;
esac
