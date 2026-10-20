#!/usr/bin/env bash
# 冪等安裝：把本 skill 目錄 symlink 到 ~/.claude/skills/sdd-harness，
# 並把 agents/*.md 逐檔 symlink 到 ~/.claude/agents/（Claude Code 只從該處載入 subagent）。
# 同 repo 的 sdd-baseline skill（預設憲章來源）尚未安裝時一併連上。
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
ln -sfn "$SKILL_DIR" "$SKILLS_DST/sdd-harness"

# agents：逐檔 symlink
for f in "$SKILL_DIR"/agents/*.md; do
    ln -sf "$f" "$AGENTS_DST/$(basename "$f")"
done

# sdd-baseline（預設憲章來源）：同 repo 有、目的地尚無時才連，不覆蓋使用者既有設定
BASELINE_SRC="$(cd "$SKILL_DIR/.." && pwd)/sdd-baseline"
if [ -f "$BASELINE_SRC/SKILL.md" ] && [ ! -e "$SKILLS_DST/sdd-baseline" ]; then
    ln -sfn "$BASELINE_SRC" "$SKILLS_DST/sdd-baseline"
fi

echo "安裝結果："
printf '  %-45s -> %s\n' "$SKILLS_DST/sdd-harness" "$(readlink "$SKILLS_DST/sdd-harness")"
for f in "$SKILL_DIR"/agents/*.md; do
    name=$(basename "$f")
    printf '  %-45s -> %s\n' "$AGENTS_DST/$name" "$(readlink "$AGENTS_DST/$name")"
done
if [ -L "$SKILLS_DST/sdd-baseline" ]; then
    printf '  %-45s -> %s\n' "$SKILLS_DST/sdd-baseline" "$(readlink "$SKILLS_DST/sdd-baseline")"
fi

FAIL=0
[ -f "$SKILLS_DST/sdd-harness/SKILL.md" ] || { echo "錯誤：skill 連結無效" >&2; FAIL=1; }
for f in "$SKILL_DIR"/agents/*.md; do
    [ -f "$AGENTS_DST/$(basename "$f")" ] || { echo "錯誤：agent 連結無效：$(basename "$f")" >&2; FAIL=1; }
done
if [ ! -f "$SKILLS_DST/sdd-baseline/references/baseline/constitution.md" ]; then
    echo "提醒：~/.claude/skills/sdd-baseline 未提供基線副本；步驟 2 需設定 SDD_BASELINE_DIR 或提供自訂憲章。" >&2
fi
[ "$FAIL" -eq 0 ] && echo "驗證通過（skill 1 個、agents $(ls "$SKILL_DIR"/agents/*.md | wc -l | tr -d ' ') 個）"
exit "$FAIL"
