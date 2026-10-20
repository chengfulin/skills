#!/usr/bin/env bash
# 把憲章來源複製到目標專案的基線目錄（預設 .specify/memory/baseline），並確保有 manifest.json。
#
# 來源優先序：第 1 參數 > $SDD_BASELINE_DIR > 同 repo 的 sdd-baseline skill 副本
#            ($SKILL_DIR/../sdd-baseline/references/baseline) > ~/.claude/skills/sdd-baseline/references/baseline
# 來源形式：
#   目錄 → 複製頂層全部 *.md（排除 CLAUDE.md）；有 manifest.json 就原樣帶走，沒有就產生
#          repo=custom 的 manifest（files 為各檔的 git blob sha）。
#   單一 .md 檔 → 寫成 constitution.md（自訂憲章），產生 repo=custom 的 manifest。
# 先寫入暫存目錄、全部成功才替換目標目錄——不留半套快照；替換採挪開-放上-刪除三步，
# 硬中斷殘留由下次執行開頭還原或清理。
#
# 用法: copy-baseline.sh [來源目錄或 .md 檔] [輸出目錄]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${1:-}"
OUT_DIR="${2:-.specify/memory/baseline}"
EXCLUDE="CLAUDE.md"

command -v python3 >/dev/null 2>&1 || { echo "錯誤：找不到 python3。" >&2; exit 1; }

if [ -z "$SRC" ] && [ -n "${SDD_BASELINE_DIR:-}" ]; then
    # 明確覆寫就只用它：設錯時直接報錯，不靜默退回其他來源
    SRC="$SDD_BASELINE_DIR"
    [ -f "$SRC/constitution.md" ] || { echo "錯誤：SDD_BASELINE_DIR=$SRC 沒有 constitution.md。" >&2; exit 1; }
fi
if [ -z "$SRC" ]; then
    for cand in "$SKILL_DIR/../sdd-baseline/references/baseline" \
                "$HOME/.claude/skills/sdd-baseline/references/baseline"; do
        [ -f "$cand/constitution.md" ] && { SRC="$cand"; break; }
    done
    [ -n "$SRC" ] || { echo "錯誤：找不到憲章來源。請安裝 sdd-baseline skill、設定 SDD_BASELINE_DIR，或以參數指定自訂憲章（目錄或 .md 檔）。" >&2; exit 1; }
fi
[ -e "$SRC" ] || { echo "錯誤：來源不存在：$SRC" >&2; exit 1; }

PARENT=$(dirname "$OUT_DIR")
mkdir -p "$PARENT"
# 先處理先前硬中斷的殘留：正式目錄已不在時先還原挪開的舊快照，其餘殘留一律清掉，
# 避免之後階段收尾的 git add -A 把半套快照掃進 commit。
if [ ! -e "$OUT_DIR" ]; then
    for d in "$PARENT"/.baseline-old.*; do
        if [ -d "$d" ]; then mv "$d" "$OUT_DIR"; break; fi
    done
fi
rm -rf "$PARENT"/.baseline-copy.* "$PARENT"/.baseline-old.* 2>/dev/null || true

STAGE=$(mktemp -d "$PARENT/.baseline-copy.XXXXXX")
OLD_DIR=""
trap 'rm -rf "$STAGE"; if [ -n "$OLD_DIR" ] && [ ! -e "$OUT_DIR" ] && [ -e "$OLD_DIR" ]; then mv "$OLD_DIR" "$OUT_DIR"; fi' EXIT

HAS_MANIFEST=no
if [ -d "$SRC" ]; then
    SRC=$(cd "$SRC" && pwd)
    found=0
    for f in "$SRC"/*.md; do
        [ -f "$f" ] || continue
        name=$(basename "$f")
        [ "$name" = "$EXCLUDE" ] && continue
        cp "$f" "$STAGE/$name"; found=$((found + 1))
        echo "已複製 ${name}" >&2
    done
    [ "$found" -gt 0 ] || { echo "錯誤：$SRC 頂層沒有 .md 檔。" >&2; exit 1; }
    [ -f "$STAGE/constitution.md" ] || { echo "錯誤：來源沒有 constitution.md（自訂憲章請以單一 .md 檔指定，或目錄內須有 constitution.md）。" >&2; exit 1; }
    if [ -f "$SRC/manifest.json" ]; then cp "$SRC/manifest.json" "$STAGE/manifest.json"; HAS_MANIFEST=yes; fi
else
    case "$SRC" in *.md) ;; *) echo "錯誤：單檔來源須為 .md：$SRC" >&2; exit 1 ;; esac
    cp "$SRC" "$STAGE/constitution.md"
    echo "已複製 $(basename "$SRC") → constitution.md（自訂憲章）" >&2
fi

if [ "$HAS_MANIFEST" = no ]; then
    # 產生 custom manifest：repo=custom、head_commit=null；files 為 git blob sha（不依賴 git）
    python3 - "$STAGE" "$SRC" <<'PY'
import sys, os, json, re, hashlib, datetime
stage, src = sys.argv[1], sys.argv[2]
def blob_sha(p):
    data = open(p, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
def ver_of(p):
    try:
        m = re.search(r"版本[：: ]*v?(\d+\.\d+\.\d+)", open(p, encoding="utf-8").read())
        return m.group(1) if m else None
    except OSError:
        return None
files = {n: blob_sha(os.path.join(stage, n)) for n in sorted(os.listdir(stage)) if n.endswith(".md")}
manifest = {
    "repo": "custom",
    "source": src,
    "head_commit": None,
    "constitution_version": ver_of(os.path.join(stage, "constitution.md")),
    "tech_standards_version": ver_of(os.path.join(stage, "tech-standards.md")),
    "fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "files": files,
}
with open(os.path.join(stage, "manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=2); fh.write("\n")
PY
fi

# 全部成功才替換目標目錄：挪開舊快照 → 放上新快照 → 刪舊快照
if [ -e "$OUT_DIR" ]; then
    OLD_DIR="$PARENT/.baseline-old.$$"
    mv "$OUT_DIR" "$OLD_DIR"
fi
mv "$STAGE" "$OUT_DIR"
trap - EXIT
[ -z "$OLD_DIR" ] || rm -rf "$OLD_DIR"

python3 - "$OUT_DIR/manifest.json" <<'PY' >&2
import sys, json
d = json.load(open(sys.argv[1], encoding="utf-8"))
sha = d.get("head_commit") or "custom"
print("完成：%s@%s（constitution v%s）→ %s/ ；files=%d" % (
    d.get("repo"), sha[:7], d.get("constitution_version") or "?", sys.argv[1].rsplit("/", 1)[0], len(d.get("files", {}))))
PY
python3 -c 'import sys,json; print(json.load(open(sys.argv[1])).get("head_commit") or "custom")' "$OUT_DIR/manifest.json"
