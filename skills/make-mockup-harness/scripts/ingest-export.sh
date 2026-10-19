#!/usr/bin/env bash
# 用法：ingest-export.sh <slug> <N> [來源檔路徑]
# 把 Claude Design 匯出的單檔版 HTML 歸檔到 make-mockups/<slug>/mockups/v<N>/index.html，
# 並寫 export.json。目標已存在即拒絕（凍結規則）。
# 來源檔未指定時，取 ~/Downloads 內檔名含 "<slug>-v<N>"（其後非數字）的最新 .html。
set -euo pipefail
slug="${1:?slug}"; n="${2:?version}"; src="${3:-}"
base="$(bash "$(dirname "$0")/mockup-root.sh")"
dst_dir="$base/$slug/mockups/v$n"
if [[ -z "$src" ]]; then
  # v1 不可誤配 v10／v11：版本號後須接非數字字元
  src="$(ls -t "$HOME/Downloads"/*"$slug-v$n".html "$HOME/Downloads"/*"$slug-v$n"[!0-9]*.html 2>/dev/null | head -n1 || true)"
fi
[[ -n "$src" && -f "$src" ]] || { echo "找不到來源檔（可用第三個參數指定）" >&2; exit 2; }
[[ -e "$dst_dir/index.html" ]] && { echo "$dst_dir/index.html 已存在，版本已凍結，請升版" >&2; exit 3; }
mkdir -p "$dst_dir"
cp "$src" "$dst_dir/index.html"
sha="$(shasum -a 256 "$dst_dir/index.html" | cut -d' ' -f1)"
size="$(wc -c < "$dst_dir/index.html" | tr -d ' ')"
if [[ -n "${SOURCE_VERSION:-}" ]]; then sv="\"$SOURCE_VERSION\""; else sv=null; fi
cat > "$dst_dir/export.json" <<JSON
{
  "sourceFile": "$(basename "$src")",
  "sourceVersion": $sv,
  "importedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "bytes": $size,
  "sha256": "$sha"
}
JSON
echo "archived -> $dst_dir/index.html ($size bytes, sha256 ${sha:0:8})"
