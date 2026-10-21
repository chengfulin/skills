#!/usr/bin/env bash
# 冪等安裝：把本 skill 目錄 symlink 到 ~/.claude/skills/make-mockup-harness，
# 並把 agents/*.md 逐檔 symlink 到 ~/.claude/agents/（Claude Code 只從該處載入 subagent）。
# 同 repo 的 make-storyboard skill（步驟 1、6 依賴）尚未安裝時一併連上。
# 重複執行安全；repo 移動位置後重跑即可修復連結。
set -euo pipefail

# 解析 symlink（經 symlink 執行時 BASH_SOURCE 指向連結本身，需還原真實位置）
SRC="${BASH_SOURCE[0]}"
while [ -L "$SRC" ]; do
    DIR="$(cd "$(dirname "$SRC")" && pwd)"
    SRC="$(readlink "$SRC")"
    case "$SRC" in /*) ;; *) SRC="$DIR/$SRC" ;; esac
done
SKILL_DIR="$(cd "$(dirname "$SRC")/.." && pwd)"
SKILLS_DST="$HOME/.claude/skills"
AGENTS_DST="$HOME/.claude/agents"

mkdir -p "$SKILLS_DST" "$AGENTS_DST"

# skill：整個目錄一個 symlink（-n 避免跟隨既有連結建到目錄內層）
ln -sfn "$SKILL_DIR" "$SKILLS_DST/make-mockup-harness"

# agents：逐檔 symlink
for f in "$SKILL_DIR"/agents/*.md; do
    ln -sf "$f" "$AGENTS_DST/$(basename "$f")"
done

# make-storyboard（步驟 1、6 以 Read 方式 inline 執行）：同 repo 有、目的地尚無時才連
STORYBOARD_SRC="$(cd "$SKILL_DIR/.." && pwd)/make-storyboard"
if [ -f "$STORYBOARD_SRC/SKILL.md" ] && [ ! -e "$SKILLS_DST/make-storyboard" ]; then
    ln -sfn "$STORYBOARD_SRC" "$SKILLS_DST/make-storyboard"
fi

echo "安裝結果："
printf '  %-50s -> %s\n' "$SKILLS_DST/make-mockup-harness" "$(readlink "$SKILLS_DST/make-mockup-harness")"
for f in "$SKILL_DIR"/agents/*.md; do
    name=$(basename "$f")
    printf '  %-50s -> %s\n' "$AGENTS_DST/$name" "$(readlink "$AGENTS_DST/$name")"
done
if [ -L "$SKILLS_DST/make-storyboard" ]; then
    printf '  %-50s -> %s\n' "$SKILLS_DST/make-storyboard" "$(readlink "$SKILLS_DST/make-storyboard")"
fi

FAIL=0
[ -f "$SKILLS_DST/make-mockup-harness/SKILL.md" ] || { echo "錯誤：skill 連結無效" >&2; FAIL=1; }
for f in "$SKILL_DIR"/agents/*.md; do
    [ -f "$AGENTS_DST/$(basename "$f")" ] || { echo "錯誤：agent 連結無效：$(basename "$f")" >&2; FAIL=1; }
done
[ -f "$SKILLS_DST/make-storyboard/SKILL.md" ] \
    || echo "提醒：~/.claude/skills/make-storyboard 不存在；步驟 1、6 會改由 $SKILL_DIR/../make-storyboard 讀取。" >&2
[ "$FAIL" -eq 0 ] && echo "驗證通過（skill 1 個、agents $(ls "$SKILL_DIR"/agents/*.md | wc -l | tr -d ' ') 個）"
echo "提醒：執行中的 Claude Code session 要到下一輪對話才會載入新裝的 agent；若 Agent 工具回 not found，再試一次即可。"
exit "$FAIL"
