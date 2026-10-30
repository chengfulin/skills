# {title} v{N}：需求交接包

本目錄是「{title}」v{N} 的需求交接包（{date} 交付）：`storyboard.md` 定業務規則，`prototype/` 是可操作的畫面，
`handoff-notes.md` 是 SA 與 PM 的交接說明。拆規格、估工或直接實作都以它為依據；本包不指定開發流程與工具。

## 讀取順序

1. `index.md`：文件索引。每個檔的用途、權威、取證方式與涵蓋範圍；開任何來源檔之前先查它，依「取證方式」開檔，只讀「涵蓋」指到的段落。
2. `handoff-notes.md`：全文讀。US 對照與優先序、驗收條件原文、功能需求候選、已定案決策、範圍外、補問清單（PM 已答）、截圖索引。
3. 做某個 User Story 時：`storyboard.md` 只讀該 `### US-nn`、「全域規則」與「資料關聯性」，畫面看截圖索引列出的 `prototype/screens/` 檔。

## 全程規則

1. 本目錄唯讀。理解或處置與來源不同時，寫進你自己的開發文件並登記回寫（見「回寫給 SA」），來源檔維持原樣。
2. `prototype/index.html` 是單檔 mockup（約 {proto_size}），取證只用三種方式：
   - 看 `prototype/screens/` 截圖；
   - 限量 grep：`grep -o -m 5 -E '<詞A>|<詞B>' prototype/index.html`；
   - 本機開啟後操作：`python3 -m http.server 8765 --bind 127.0.0.1 -d prototype`，開 http://127.0.0.1:8765/index.html。
     每個畫面有 `data-page="S<n>"`，畫面 ID 與 `handoff-notes.md`、截圖檔名一致。
3. 業務類問題（「權威劃分」第 1 條）由 SA／PM 裁決：整理成題目、選項、建議交回，答案回來前標為待釐清，不代答。
   互動與呈現類問題先操作 Prototype，依第 2 條直接裁決。
4. 版本以 sha256 鎖定。複製進開發 repo 後重算，須與下表相同：

   | 檔案 | sha256 |
   |---|---|
   | `storyboard.md` | {sha_storyboard} |
   | `prototype/index.html` | {sha_prototype}（= `prototype/export.json`） |

## 權威劃分

1. **判別式**：會改變資料、狀態、權限、計算結果或驗收結果的，是**業務規則**，以 StoryBoard 為準；
   只改變呈現方式的，是**呈現**，以 Prototype 為準。
2. **互動行為**：StoryBoard 有明文的（例如卡片聯動、排序規則）以 StoryBoard 為準；
   其餘互動（展開收合、捲動、焦點移動）以 Prototype 為準。
3. **用詞**：領域術語（狀態名、欄位名、業務名詞）以 StoryBoard 為準；其餘 UI 文案（按鈕、提示、說明）
   以 Prototype 逐字採用。
4. **視覺樣式**：Prototype 是目標外觀，實作透過 design token 與共用元件，不照搬行內樣式或色碼。
   狀態標籤「顯示哪個狀態」屬業務規則，「顏色與形狀」屬視覺樣式。
5. **來源都沒定義的部分**（空狀態、錯誤、載入中、窄螢幕等）：依開發專案既有慣例補齊，登記為缺口。

## 錨點

在規格、任務、測試或 commit 引用來源時，句尾標錨點，寫到能定位片段的粒度；每個錨點都能在 `index.md`「涵蓋」欄找到。

| 錨點 | 指向 | 例 |
|---|---|---|
| `[SB US-nn]`、`[SB US-nn 規則 k]`、`[SB US-nn 狀態]`、`[SB US-nn 邊界 k]`、`[SB 全域規則 k]`、`[SB 資料關聯 k]` | `storyboard.md` 的 User Story／其「規則」第 k 條／「狀態」項／「邊界情況」第 k 條／「全域規則」第 k 條／「資料關聯性」第 k 列 | `[SB US-02 規則 3]` |
| `[P S<n>]`、`[P S<n>-<序號>]` | Prototype 畫面／`prototype/screens/` 中 `S<n>-<序號>-*.png` 那張截圖 | `[P S1-03]` |
| `[HO Q<n>]`、`[HO AC-<id>]` | `handoff-notes.md` 的補問清單答案／驗收條件原文（含 `AC-P` 系列） | `[HO AC-P1]` |

## 回寫給 SA

開發期出現以下三類就登記，完成時（或需要 SA 先裁決時）彙整成 `handback-to-sa.md` 交回 SA。
SA 據此升版 StoryBoard 與 Prototype，新版另開目錄交付；開發中的版本預設不換。

| 類型 | 登記時機 | SA 的處置 |
|---|---|---|
| 偏離 | 實作與來源明文不同（元件做不到、來源自身矛盾、來源漏畫的取捨） | 依處置改寫條文 |
| 決策 | 開發期經 SA／PM 裁決、新定或改變的業務規則 | 寫進對應 US 的規則 |
| 缺口 | 來源沒定義、開發依慣例補上的行為 | 逐條決定是否補進 StoryBoard |

```markdown
# 開發回寫：{title} v{N}

- 鎖定來源：v{N}；storyboard.md {sha_storyboard}；prototype/index.html {sha_prototype}
- 開發位置：<repo>／<路徑、分支或規格目錄>

| ID | 類型 | 來源錨點 | 來源原文 | 開發處置 | 理由 |
|---|---|---|---|---|---|
| <開發端自己的編號> | 偏離／決策／缺口 | [SB US-02 規則 3] | … | … | … |
```
