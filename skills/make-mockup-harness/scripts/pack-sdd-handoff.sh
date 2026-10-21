#!/usr/bin/env bash
# 用法：pack-sdd-handoff.sh <slug> <N>
# 把 make-mockups/<slug>/ 的 v<N> 產出打包成 sdd-harness 開發 repo 可直接複製的 `.specify/context/` 結構，
# 放在 make-mockups/<slug>/handoff/v<N>/，並附開發者用的 SDD-START.md。
# 只做機械性工作：前提檢查、複製、sha256、代入範本、產生規格來源索引 index.md。截圖、index.md 的
# 待填欄與 sdd-input.md 的內容由 orchestrator 依 references/sdd-handoff.md 步驟 7 補齊。目標目錄已存在即拒絕（凍結規則）。
set -euo pipefail
slug="${1:?slug}"; n="${2:?version}"
here="$(cd "$(dirname "$0")" && pwd)"
skill_dir="$(cd "$here/.." && pwd)"
tpl="$skill_dir/references/sdd-handoff-templates"
base="$(bash "$here/mockup-root.sh")"
src="$base/$slug"
state="$src/.mockup-workflow.json"
out="$src/handoff/v$n"
ctx="$out/.specify/context"
fail=0

ok()   { echo "check_$1=ok"; }
bad()  { printf "check_%s=FAIL  %b\n" "$1" "$2" >&2; fail=1; }
warn() { echo "check_$1=WARN  $2" >&2; }

# ---- 前提檢查 --------------------------------------------------------------
[[ -f "$src/storyboard.md" ]] && ok storyboard || bad storyboard "找不到 $src/storyboard.md"
[[ -f "$src/mockups/v$n/index.html" && -f "$src/mockups/v$n/export.json" ]] \
  && ok mockup || bad mockup "找不到 $src/mockups/v$n/index.html 或 export.json"
[[ -f "$src/reviews/v$n-consistency.md" ]] && ok review || bad review "找不到 $src/reviews/v$n-consistency.md"
[[ -f "$src/briefs/v$n-design-brief.md" ]] && ok brief || warn brief "找不到 $src/briefs/v$n-design-brief.md（reference/ 會缺 brief）"
[[ -f "$state" ]] && ok state || bad state "找不到狀態檔 $state"
[[ -e "$out" ]] && bad frozen "$out 已存在；交接包一旦產出即凍結，要重做請先刪除該目錄，或升版後再交接" || ok target
[[ -f "$tpl/spec-source-template.md" && -f "$tpl/sdd-source-instructions.template.md" \
   && -f "$tpl/sdd-input.template.md" && -f "$tpl/sdd-start.template.md" ]] \
  && ok templates || bad templates "references/sdd-handoff-templates/ 缺檔"
[[ $fail -eq 0 ]] || { echo "前提檢查未通過，停止。" >&2; exit 2; }

# 版本一致：狀態檔 currentVersion、storyboard 變更紀錄最後一列
cur="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("currentVersion"))' "$state")"
title="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("title") or sys.argv[2])' "$state" "$slug")"
sb_ver="$(grep -E '^\| *v[0-9]+ *\|' "$src/storyboard.md" | tail -n1 | sed -E 's/^\| *(v[0-9]+).*/\1/')"
[[ "$cur" == "$n" ]] && ok state_version || bad state_version "狀態檔 currentVersion=$cur ≠ v$n；只能交接已完成步驟 5 的當前版本，升版後請先走完 v$cur 的步驟 2–5"
[[ "$sb_ver" == "v$n" ]] && ok storyboard_version || bad storyboard_version "storyboard 變更紀錄最後一列為 $sb_ver，不是 v$n"

# sha256 與 export.json 一致
sha_proto="$(shasum -a 256 "$src/mockups/v$n/index.html" | cut -d' ' -f1)"
sha_export="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("sha256") or "")' "$src/mockups/v$n/export.json")"
[[ "$sha_proto" == "$sha_export" ]] && ok sha256 || bad sha256 "index.html 的 sha256 與 export.json 不符"

# 一致性檢核「待決定」須無未裁決項
pending="$(awk '/^## 待決定/{f=1;next} /^## /{f=0} f && /^\|/' "$src/reviews/v$n-consistency.md" \
  | grep -v -E '^\| *# *\||^\| *:?-+' | grep -v -E '^\| *— *\| *無' || true)"
if [[ -z "$pending" ]]; then ok review_pending
else
  unresolved="$(echo "$pending" | awk -F'|' '{gsub(/^ +| +$/,"",$(NF-1)); if ($(NF-1)=="" || $(NF-1)=="延後") print}')"
  [[ -z "$unresolved" ]] && ok review_pending || bad review_pending "一致性檢核仍有未裁決的待決定：\n$unresolved"
fi

# storyboard「待決定」須全數定案
sb_pending="$(awk '/^## 待決定/{f=1;next} /^## /{f=0} f && /^\|/' "$src/storyboard.md" \
  | grep -v -E '^\| *# *\||^\| *:?-+' | grep -v -E '^\| *— *\| *無' | grep -v '已定案' || true)"
[[ -z "$sb_pending" ]] && ok storyboard_pending || bad storyboard_pending "storyboard 待決定表仍有未定案項：\n$sb_pending"

[[ $fail -eq 0 ]] || { echo "前提檢查未通過，停止。請先回步驟 5／6 處理。" >&2; exit 2; }

# ---- 打包 ------------------------------------------------------------------
feat="$ctx/$slug/v$n"
mkdir -p "$feat/prototype/screens" "$feat/reference" "$ctx/_shared"
cp "$src/storyboard.md"               "$feat/storyboard.md"
cp "$src/mockups/v$n/index.html"      "$feat/prototype/index.html"
cp "$src/mockups/v$n/export.json"     "$feat/prototype/export.json"
cp "$src/reviews/v$n-consistency.md"  "$feat/reference/v$n-consistency.md"
[[ -f "$src/briefs/v$n-design-brief.md" ]] && cp "$src/briefs/v$n-design-brief.md" "$feat/reference/v$n-design-brief.md"
for f in "$src"/feedback/v$n-*.md; do [[ -f "$f" ]] && cp "$f" "$feat/reference/"; done
cp "$tpl/spec-source-template.md" "$ctx/_shared/spec-source-template.md"

sha_sb="$(shasum -a 256 "$feat/storyboard.md" | cut -d' ' -f1)"
today="$(date +%Y-%m-%d)"
proto_size="$(wc -c < "$feat/prototype/index.html" | awk '{printf "%.1f MB", $1/1048576}')"
fill() {  # fill <template> <output>
  sed -e "s|{slug}|$slug|g" -e "s|{N}|$n|g" -e "s|{title}|$title|g" -e "s|{date}|$today|g" \
      -e "s|{sha_storyboard}|$sha_sb|g" -e "s|{sha_prototype}|$sha_proto|g" -e "s|{proto_size}|$proto_size|g" "$1" > "$2"
}
fill "$tpl/sdd-source-instructions.template.md" "$ctx/_shared/sdd-source-instructions.md"
fill "$tpl/sdd-input.template.md"               "$feat/sdd-input.md"
fill "$tpl/sdd-start.template.md"               "$out/SDD-START.md"

# ---- index.md：規格來源索引 ----------------------------------------------------
# clarifier／analyze 找來源的入口：每檔一列寫媒材、大小、權威、取證方式、涵蓋範圍。
# 涵蓋欄能從來源機械抓到的就抓（storyboard 的 US-nn 標題、mockup 的 data-page），抓不到留 {填：…}。
size_of() { wc -c < "$1" | awk '{b=$1; if (b<1024) printf "%d B", b; else if (b<1048576) printf "%.0f KB", b/1024; else printf "%.1f MB", b/1048576}'; }
# grep 沒命中回 1，在 pipefail 下會讓整個賦值失敗、script 中止，所以各加 || true 讓 fallback 生效。
sb_us="$( { grep -E '^#+ *US-[0-9]+' "$feat/storyboard.md" || true; } | grep -v '已移除' | grep -o -E 'US-[0-9]+' | sort -u | paste -sd '、' - || true)"
proto_pages="$( { grep -o -E 'data-page="S[0-9]+[^"]*"' "$feat/prototype/index.html" || true; } | sed -E 's/^data-page="([^"]*)"$/\1/' \
  | sort -u | sort -t S -k2,2n | paste -sd '、' - || true)"
fill_us='{填：US-nn 清單}'; fill_pages='{填：S<n> 畫面清單（舊 Claude Design 單檔無 data-page，依 brief 畫面清單填）}'
fill_ref='{填：涵蓋的章節或 US}'
{
  echo "# 規格來源索引：$title v$n"
  echo
  echo "> 由 \`pack-sdd-handoff.sh\` 產生，入版控後與來源檔一起唯讀；新版另開目錄。"
  echo "> 用途：clarifier／analyze **找來源的入口**——先依本表決定開哪個檔、怎麼取證、看哪一段，再依 spec 的錨點取片段，不掃目錄。"
  echo "> 「涵蓋」欄列到錨點的粒度（US-nn、S<n>、§節、p.頁），spec 錨點要能在這欄找到。自動抓到的要與 storyboard、brief 核對；標「填」的欄由 SA 在交接步驟 3 補齊。"
  echo
  echo "| 路徑 | 媒材 | 大小 | 權威 | 取證方式 | 涵蓋（US／畫面／章節） |"
  echo "|---|---|---|---|---|---|"
  echo "| \`storyboard.md\` | markdown | $(size_of "$feat/storyboard.md") | 業務規則 | Read；US 以 \`### US-nn\` 標題定位，只讀錨點指到的 US 與全域規則 | ${sb_us:-$fill_us} |"
  echo "| \`prototype/index.html\` | html（單檔 mockup） | $proto_size | 呈現 | **不整份 Read**：看 \`prototype/screens/\`、限量 grep（\`grep -o -m 5\`）、或本機 http server 開啟操作 | ${proto_pages:-$fill_pages} |"
  echo "| \`prototype/export.json\` | json | $(size_of "$feat/prototype/export.json") | — | Read（sha256、來源 artifact） | — |"
  echo "| \`prototype/screens/*.png\` | 截圖（1440×900 full-page） | — | 衍生產物，無獨立權威 | Read 看圖；逐張對應畫面、狀態、US 見 \`sdd-input.md\`「截圖索引」 | 依截圖索引 |"
  echo "| \`sdd-input.md\` | markdown | — | 交接說明 | Read 全文 | US 對照、AC 原文、FR 候選、已定案決策、PM 答案 |"
  for f in "$feat"/reference/*; do
    [[ -f "$f" ]] || continue
    rel="reference/$(basename "$f")"
    case "$(basename "$f")" in
      *design-brief*) cov="畫面 ID 與畫面清單、假資料表、展示腳本" ;;
      *consistency*)  cov="操作驗證表、裁決" ;;
      *)              cov="$fill_ref" ;;
    esac
    echo "| \`$rel\` | markdown | $(size_of "$f") | 參考，不具權威 | Read；只讀錨點或 FR 關鍵詞指到的節 | $cov |"
  done
  echo
  echo "sha256：\`storyboard.md\` ${sha_sb}；\`prototype/index.html\` ${sha_proto}（= export.json）。"
} > "$feat/index.md"

# ---- 報告 ------------------------------------------------------------------
echo
echo "packed -> $out"
( cd "$out" && find . -type f -o -type d -empty | sort | sed 's|^\./|  |' )
echo
echo "sha256:"
echo "  storyboard.md        $sha_sb"
echo "  prototype/index.html $sha_proto  (= export.json)"
echo
echo "index.md 涵蓋欄："
echo "  storyboard US：${sb_us:-（未抓到，待填）}"
echo "  prototype 畫面：${proto_pages:-（未抓到 data-page，待填）}"
echo
echo "尚待 orchestrator 完成（見 references/sdd-handoff.md 步驟 7）："
echo "  1. prototype/screens/ 截圖（1440×900、full-page、含互動後狀態）並填 sdd-input.md 截圖索引"
echo "  2. 核對 index.md 自動抓到的涵蓋欄、補 {填：…}；sdd-input.md 其餘章節：US 對照、驗收條件原文、FR 候選、已定案決策、範圍外、補問清單"
echo "  3. PM 填 Priority 與補問清單答案"
echo "  4. 狀態檔 stage: handed-off、versions[].handoff，commit"
