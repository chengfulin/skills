#!/usr/bin/env bash
# 偵測目標專案目前的 SDD 流程階段（供續跑使用）。
# 在目標專案根目錄執行；輸出 key=value 證據行，最後一行為 detected_stage=<階段>。
#
# 階段順序: init → constitution → specify → clarify → plan → tasks → analyze
#           → implement → done
# 偵測以「檔案系統 + git」為準，.sdd-workflow.json 狀態檔為輔；clarify / analyze /
# implement 收尾這類無（或不可靠）檔案產物的階段以狀態檔為權威。
# 例外：狀態檔 replan.active=true（重規劃迴圈進行中）時輸出 detected_stage=replan，
# 以 replan.resume_at 為權威——優先於 clarify 之後的所有階段檢查。
#
# 用法: detect-stage.sh [專案根目錄]    # 預設為目前目錄
set -uo pipefail

cd "${1:-.}" || { echo "error=bad_project_dir" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "error=python3_missing" >&2; exit 2; }

json_get() {  # json_get <file> <dotted.path> → 值或空字串
    [ -f "$1" ] || { echo ""; return; }
    python3 -c '
import sys, json
try:
    with open(sys.argv[1]) as fh:
        node = json.load(fh)
    for key in sys.argv[2].split("."):
        node = node[key]
    print(node if not isinstance(node, bool) else str(node).lower())
except Exception:
    print("")' "$1" "$2" 2>/dev/null
}

# placeholder 掃描：剔除 HTML 註解（Sync Impact Report 有 [TEMPLATE] 之類的歷史
# 紀錄）；字元類含數字（範本 token 如 [PRINCIPLE_2_NAME]）；用 grep -c 讀完整個
# 輸入避免 pipefail 下 -q 提前退出造成 sed SIGPIPE 反轉結果。
# 先就地消同行註解再刪跨行範圍——sed 的 /a/,/b/ 範圍起訖落在同一行時不會關閉，
# 單行註解會吞掉其後直到下一個 --> 或檔尾的全部內容，使檢查失效
has_placeholders() {
    sed -e 's/<!--.*-->//g' -e '/<!--/,/-->/d' "$1" 2>/dev/null \
      | grep -cE '\[[A-Z][A-Z0-9_ ]{2,}\]' >/dev/null
}

# --- git 與 working tree ---
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    GIT=ok
    DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo 0)
else
    GIT=none; DIRTY=0; COMMITS=0
fi
echo "git=$GIT dirty_files=$DIRTY commits=$COMMITS"

# --- 初始化 ---
if [ ! -d .specify ]; then
    echo "specify_init=missing"
    echo "detected_stage=init"
    exit 0
fi
echo "specify_init=ok"

if grep -q '"git"' .specify/extensions/.registry 2>/dev/null; then
    echo "git_extension=ok"
else
    echo "git_extension=missing"
fi

GC=".specify/extensions/git/git-config.yml"
ENABLED=0
for e in after_constitution after_specify after_clarify after_plan after_tasks after_analyze after_implement; do
    if [ -f "$GC" ] && awk -v ev="$e" '
        $0 ~ "^  " ev ":" { found = 1; next }
        found && /^    enabled: true/ { ok = 1; exit }
        found && /^  [a-z_]/ { exit }
        END { exit ok ? 0 : 1 }' "$GC"; then
        ENABLED=$((ENABLED + 1))
    fi
done
echo "autocommit_enabled=$ENABLED/7"

# init 半途（extension 未裝或 auto-commit 未全啟用）→ 回 init 重走：
# 步驟 1 冪等（有 .specify 不會重跑 init；extension add 與 enable-autocommit 可重複執行）
if ! grep -q '"git"' .specify/extensions/.registry 2>/dev/null || [ "$ENABLED" -ne 7 ]; then
    echo "detected_stage=init"
    exit 0
fi

# --- 憲章 ---
CONST=".specify/memory/constitution.md"
ADOPT=".specify/memory/sdd-adoption.json"
if [ ! -f "$CONST" ] || has_placeholders "$CONST" || [ ! -f "$ADOPT" ] \
   || ! grep -q '^## SDD 導入宣告' README.md 2>/dev/null; then
    [ -f "$CONST" ] || echo "constitution=missing"
    [ -f "$CONST" ] && has_placeholders "$CONST" && echo "constitution=has_placeholders"
    [ -f "$ADOPT" ] || echo "adoption_declaration=missing"
    grep -q '^## SDD 導入宣告' README.md 2>/dev/null || echo "readme_declaration=missing"
    echo "detected_stage=constitution"
    exit 0
fi
echo "constitution=ok adoption_phase=$(json_get "$ADOPT" adoption_phase) app_type=$(json_get "$ADOPT" app_type)"

# --- feature 與各階段產物 ---
# feature.json 是 per-checkout 狀態：spec-kit 1.0.5 起被 .specify/.gitignore 忽略，
# fresh clone／另一台機器續跑時不存在。缺席或指向無 spec.md 的目錄時回退：
# 先以目前分支名 NNN-slug 對應 specs/NNN-slug/spec.md，再掃 specs/ 取編號最大者。
# 回退時輸出 feature_json=missing|stale，orchestrator 須先重建該檔再續跑——
# speckit 各腳本（check-prerequisites 等）沒有 feature.json 會直接失敗（1.0.5 實測）。
FEATURE_DIR=$(json_get .specify/feature.json feature_directory)
FEATURE_SOURCE=feature.json
if [ -z "$FEATURE_DIR" ] || [ ! -f "$FEATURE_DIR/spec.md" ]; then
    FEATURE_SOURCE=none
    BR=$(git branch --show-current 2>/dev/null || true)
    case "$BR" in
        [0-9][0-9][0-9]-*)
            [ -f "specs/$BR/spec.md" ] && { FEATURE_DIR="specs/$BR"; FEATURE_SOURCE=branch; } ;;
    esac
    if [ "$FEATURE_SOURCE" = none ]; then
        for d in $(ls -d specs/[0-9][0-9][0-9]-*/ 2>/dev/null | sed 's:/$::' | sort -r); do
            [ -f "$d/spec.md" ] && { FEATURE_DIR="$d"; FEATURE_SOURCE=specs-scan; break; }
        done
    fi
fi
if [ "$FEATURE_SOURCE" = none ]; then
    echo "feature=none"
    echo "detected_stage=specify"
    exit 0
fi
FJ=ok
if [ "$FEATURE_SOURCE" != feature.json ]; then
    [ -f .specify/feature.json ] && FJ=stale || FJ=missing
fi
echo "feature_dir=$FEATURE_DIR feature_source=$FEATURE_SOURCE feature_json=$FJ"
STATE="$FEATURE_DIR/.sdd-workflow.json"

committed() { git ls-files --error-unmatch "$1" >/dev/null 2>&1 && echo yes || echo no; }

echo "spec=ok committed=$(committed "$FEATURE_DIR/spec.md")"

# --- 重規劃（replan）：active 時 resume_at 為權威，優先於後續各階段檢查 ---
# resume_at 非法值不中止（狀態檔可能損毀）：標記 invalid 交 orchestrator 問使用者
if [ "$(json_get "$STATE" replan.active)" = "true" ]; then
    REPLAN_AT=$(json_get "$STATE" replan.resume_at)
    case "$REPLAN_AT" in
        spec|clarify|plan|tasks|analyze) ;;
        *) REPLAN_AT=invalid ;;
    esac
    echo "replan_active=true replan_iteration=$(json_get "$STATE" replan.iteration) replan_resume_at=$REPLAN_AT"
    echo "detected_stage=replan"
    exit 0
fi

# clarify 以狀態檔為權威：釐清可能中斷在「章節已寫入但 CRITICAL 未處理」，
# 光看 '## Clarifications' 標記會誤判完成
CLARIFY_MARK=no
grep -q '^## Clarifications' "$FEATURE_DIR/spec.md" 2>/dev/null && CLARIFY_MARK=yes
CLARIFY_STATE=$(json_get "$STATE" steps.clarify.done)
echo "clarify_marker=$CLARIFY_MARK clarify_state=${CLARIFY_STATE:-unset}"
if [ "$CLARIFY_STATE" != "true" ]; then
    echo "detected_stage=clarify"
    exit 0
fi

if [ ! -f "$FEATURE_DIR/plan.md" ]; then
    echo "plan=missing"
    echo "detected_stage=plan"
    exit 0
fi
echo "plan=ok committed=$(committed "$FEATURE_DIR/plan.md")"

if [ ! -f "$FEATURE_DIR/tasks.md" ]; then
    echo "tasks=missing"
    echo "detected_stage=tasks"
    exit 0
fi
echo "tasks=ok committed=$(committed "$FEATURE_DIR/tasks.md")"

ANALYZE_STATE=$(json_get "$STATE" steps.analyze.done)
echo "analyze_state=${ANALYZE_STATE:-unset}"
if [ "$ANALYZE_STATE" != "true" ]; then
    echo "detected_stage=analyze"
    exit 0
fi

# --- 實作進度：tasks.md 勾選 + 收尾狀態（最後回歸驗證與 after_implement）---
DONE_TASKS=$(grep -cE '^[-*] \[[Xx]\]' "$FEATURE_DIR/tasks.md" 2>/dev/null || true)
OPEN_TASKS=$(grep -cE '^[-*] \[ \]' "$FEATURE_DIR/tasks.md" 2>/dev/null || true)
IMPL_STATE=$(json_get "$STATE" steps.implement.done)
echo "tasks_done=${DONE_TASKS:-0} tasks_open=${OPEN_TASKS:-0} implement_state=${IMPL_STATE:-unset}"
if [ "${OPEN_TASKS:-0}" -gt 0 ] || [ "$IMPL_STATE" != "true" ]; then
    echo "detected_stage=implement"
    exit 0
fi

echo "detected_stage=done"
