#!/usr/bin/env bash
# 同步團隊 SDD 憲章基線到本 skill 的 references/baseline/，並寫入 manifest.json
# （schema 與 sdd-harness fetch-baseline.sh 相同：repo / head_commit / constitution_version /
#   fetched_at / files，另加 tech_standards_version）。
#
# 用法: sync-baseline.sh [<本地 sdd-baseline checkout 路徑>]
#   不帶參數：以 gh api 抓 ${SDD_BASELINE_REPO:-chengfulin/sdd-baseline} 的 HEAD（private，需 gh auth login）
#   帶路徑  ：從本地 git checkout 複製，head_commit 取該 checkout 的 HEAD
# 同步頂層 *.md，排除 CLAUDE.md（它是基線 repo 自身的維護指引，不是憲章內容）。
# 先寫入暫存目錄、全部成功才替換目標目錄。
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$SKILL_DIR/references/baseline"
REPO="${SDD_BASELINE_REPO:-chengfulin/sdd-baseline}"
EXCLUDE="CLAUDE.md"
SRC="${1:-}"

command -v python3 >/dev/null 2>&1 || { echo "錯誤：找不到 python3。" >&2; exit 1; }

old_ver=""; old_sha=""
if [ -f "$OUT_DIR/manifest.json" ]; then
  old_ver=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("constitution_version") or "?")' "$OUT_DIR/manifest.json")
  old_sha=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("head_commit") or "")' "$OUT_DIR/manifest.json")
fi

STAGE=$(mktemp -d "${TMPDIR:-/tmp}/sdd-baseline.XXXXXX")
trap 'rm -rf "$STAGE"' EXIT
ENTRIES=""

if [ -n "$SRC" ]; then
  git -C "$SRC" rev-parse --git-dir >/dev/null 2>&1 || { echo "錯誤：$SRC 不是 git checkout。" >&2; exit 1; }
  SRC=$(cd "$SRC" && pwd)
  HEAD_SHA=$(git -C "$SRC" rev-parse HEAD)
  if [ -n "$(git -C "$SRC" status --porcelain)" ]; then
    echo "警告：$SRC 工作樹有未提交變更，manifest 的 head_commit 不一定對應複製的內容。" >&2
  fi
  remote=$(git -C "$SRC" remote get-url origin 2>/dev/null || true)
  if [ -n "$remote" ]; then
    REPO=$(printf '%s' "$remote" | sed -E 's#.*github\.com[:/]##; s#\.git$##')
  fi
  for f in "$SRC"/*.md; do
    name=$(basename "$f")
    if [ "$name" = "$EXCLUDE" ]; then continue; fi
    cp "$f" "$STAGE/$name"
    ENTRIES+="$name $(git hash-object "$f")"$'\n'
    echo "已複製 ${name}" >&2
  done
else
  command -v gh >/dev/null 2>&1 || { echo "錯誤：找不到 gh（GitHub CLI）。請先安裝並 gh auth login。" >&2; exit 1; }
  gh auth status >/dev/null 2>&1 || { echo "錯誤：gh 未登入。請執行 gh auth login。" >&2; exit 1; }
  HEAD_SHA=$(gh api "repos/$REPO/commits/HEAD" --jq '.sha' 2>/dev/null) \
    || { echo "錯誤：無法存取 ${REPO}（private repo 需帳號權限）。" >&2; exit 1; }
  FILES=$(gh api "repos/$REPO/git/trees/$HEAD_SHA" --jq '.tree[] | select(.type=="blob") | .path' \
    | grep -E '^[^/]+\.md$' || true)
  [ -n "$FILES" ] || { echo "錯誤：${REPO}@${HEAD_SHA:0:7} 頂層沒有 .md 檔。" >&2; exit 1; }
  while IFS= read -r f; do
    if [ -z "$f" ] || [ "$f" = "$EXCLUDE" ]; then continue; fi
    json=$(gh api "repos/$REPO/contents/$f?ref=$HEAD_SHA" 2>/dev/null) \
      || { echo "錯誤：抓取 ${f} 失敗（ref=${HEAD_SHA}）。" >&2; exit 1; }
    blob_sha=$(printf '%s' "$json" | python3 -c '
import sys, json, base64
d = json.load(sys.stdin)
open(sys.argv[1], "wb").write(base64.b64decode(d["content"]))
print(d["sha"])' "$STAGE/$f")
    ENTRIES+="$f $blob_sha"$'\n'
    echo "已抓取 ${f}（blob ${blob_sha:0:7}）" >&2
  done <<FILES_EOF
$FILES
FILES_EOF
fi

[ -f "$STAGE/constitution.md" ] || { echo "錯誤：來源沒有 constitution.md。" >&2; exit 1; }
ver_of() { grep -m1 -oE '版本[：: ]*v?[0-9]+\.[0-9]+\.[0-9]+' "$1" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || true; }
CONST_VERSION=$(ver_of "$STAGE/constitution.md")
TS_VERSION=$(ver_of "$STAGE/tech-standards.md")

printf '%s' "$ENTRIES" | python3 -c '
import sys, json, datetime
entries = {}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    name, sha = line.rsplit(" ", 1)
    entries[name] = sha
manifest = {
    "repo": sys.argv[1],
    "head_commit": sys.argv[2],
    "constitution_version": sys.argv[3] or None,
    "tech_standards_version": sys.argv[4] or None,
    "fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "files": dict(sorted(entries.items())),
}
with open(sys.argv[5], "w") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
' "$REPO" "$HEAD_SHA" "$CONST_VERSION" "$TS_VERSION" "$STAGE/manifest.json"

rm -rf "$OUT_DIR"
mkdir -p "$(dirname "$OUT_DIR")"
mv "$STAGE" "$OUT_DIR"
trap - EXIT

echo "完成：$REPO@${HEAD_SHA:0:7}（constitution v${CONST_VERSION:-?}，tech-standards v${TS_VERSION:-?}）→ $OUT_DIR/" >&2
if [ -n "$old_sha" ]; then
  if [ "$old_sha" = "$HEAD_SHA" ]; then echo "與前一版相同（v${old_ver}@${old_sha:0:7}）。" >&2
  else echo "前一版：v${old_ver}@${old_sha:0:7}" >&2; fi
fi
echo "$HEAD_SHA"
