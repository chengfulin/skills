# Mockup build：輸入與產出紀錄

步驟 3 的每一次產出都是一個 **build**：orchestrator 寫輸入（`request.md`），`mockup-builder` 依輸入產出
HTML 快照與產出紀錄（`index.html`、`build.md`），orchestrator 審過後採用、發布並在索引回填版本 id。
符合「inline 條件」的微修由 orchestrator 自己產出（`inline` 模式），紀錄格式相同。
任何修改（含改字、調間距）都開新 build，不直接改工作檔——迭代與回退都靠 build id 索引。

```
mockup-src/
├── index.html              # 發布用工作檔 = 目前採用的 build 快照（orchestrator 複製過來）
├── builds.md               # 索引（orchestrator 維護）
└── builds/
    └── v<N>-b<kk>/
        ├── request.md      # 輸入（orchestrator 寫，派遣後不改）
        ├── index.html      # 產出快照（builder 寫；inline 由 orchestrator 寫）
        └── build.md        # 產出紀錄（同上）
```

## 識別碼

- **build id**：`v<N>-b<kk>`，`kk` 為該版內兩位數流水號，從 `01` 起；跨版不續號（v2 從 `v2-b01` 起）。
- **變更項**：request 內以 `C<nn>` 編號，引用時寫 `v<N>-b<kk>#C<nn>`（例：`v1-b03#C02`）。
  SA 說「b05 的 C01 做錯了」，下一個 request 的來源欄就寫 `v1-b05#C01`。
- **base**：本次以哪個 build 的快照為底稿。`new` 無 base；回退時 base 指向較舊的 build，不必是最新那個。

## 模式

| 模式 | 用途 | base | 變更項來源 |
|------|------|------|-----------|
| `new` | v1 初版，依 brief 全新製作 | 無 | 整份 brief（變更項只列一條 `C01 依 brief 全部畫面`） |
| `revise` | v≥2 第一個 build，依 brief「本版異動」增量修改 | 前一版凍結時採用的 build | brief「本版異動」逐條轉成 C 項 |
| `patch` | 迭代中的修改（不符 inline 條件者） | 通常是目前採用的 build | SA 對話、artifact 留言、回退要求 |
| `inline` | 微修，orchestrator 直接改、不派 builder | 目前採用的 build | SA 對話中的改字、調樣式數值 |

## inline 條件與程序

派 builder 有固定開銷（載入格式文件、定位 base 程式碼），一次只改幾個字時開銷是改動本身的十倍以上。
**全部符合**才走 `inline`，任一不符就用 `patch`：

- 所有變更項都是「呈現」類（不含規則、回退）。
- 只改既有文案，或在既有 CSS 規則內改值、加宣告（顏色、字級、字重、間距、圓角、寬高、陰影）；不新增 CSS 規則、不新增或刪除元素、
  不改 class／id／`data-page`、不動 `<script>` 內的邏輯（JS 字串常數中的純文案可以改）。
- 整個 request 改動處合計 ≤ 3 處（同一條 CSS 規則內改多個屬性算 1 處）。
- base 是目前採用的 build。

程序（主對話執行，仍遵守通用規則 3，不整份 Read 快照）：

1. request.md 照常寫（模式 `inline`），`builds.md` 加一列。
2. `mkdir` build 目錄 → `cp` base 快照進去。
3. 每個變更項以 `grep -n -m 3` 定位；同一字串出現多處、或需要看上下文才能判斷時，Read 該行前後各 10 行。
   定位結果不唯一或發現要動的不只是值 → 停下，把該 build 改成 `patch` 派 builder（同一 build id、request 模式改寫）。
4. 對**本 build 目錄的快照**做 Edit；`shasum -a 256`、`wc -c` 取 base 與產出的雜湊與大小。
5. 寫 build.md：標頭與「變更項處理」照格式填（位置寫行號與 selector），其餘段落寫「—（inline 不變動結構）」。
   artifact-design 欄寫「沿用 base」。

## 接續同一個 builder

同一 session 內，下一個 `patch` 的 base 正是某個 builder 剛產出的 build 時，以 SendMessage 接續它，
訊息只寫新 build id（request 已寫好）。它已讀過格式文件與 base 內容，省去重讀；
跨 session、base 是其他 build、或該 builder 已接續 3 次時改派新的（context 累積過長）。

## `request.md`（orchestrator 寫）

```markdown
# Build request v<N>-b<kk>

- 模式：new | revise | patch | inline
- base：v<N>-b<kk> | 無
- brief：briefs/v<N>-design-brief.md
- storyboard：變更紀錄最新列 v<N>（<日期>）
- 設計系統：<檔案路徑與名稱> | 不套設計系統

## 變更項

| C | 類型 | 來源 | 要求 | 影響畫面 |
|---|------|------|------|---------|
| C01 | 呈現 | SA 對話 2026-10-21 | 列表卡片間距加大，標題改粗體 | S2 |
| C02 | 規則 | storyboard US-03 規則 4（v1 更正，2026-10-21） | 「已逾期」優先於「進行中」顯示：<規則原文> | S2, S4 |
| C03 | 回退 | v1-b05#C01 | 還原 S3 篩選列為 v1-b04 的樣式 | S3 |
```

- **類型**：`呈現`（版面、配色、文案措辭、元件樣式）、`規則`（行為、狀態、範圍）、`回退`（還原某 build 的某部分）。
- **規則類必須引用已寫回的 storyboard 位置並抄錄規則原文**（通用規則 1）；
  沒有引用的規則類變更項，builder 一律不做，回報退回。
- 一個 request 可以合併多條回饋；SA 一次說了好幾件事就寫成多個 C 項，不要拆成多個 build。

## `build.md`（builder 寫）

```markdown
# Build v<N>-b<kk>

- 模式：patch | inline｜base：v<N>-b<kk>（sha256 <前 8 碼>）
- 產出：builds/v<N>-b<kk>/index.html（<bytes> bytes，sha256 <前 8 碼>）
- artifact-design：已載入 | 未載入（依 mockup-build.md「頁面契約」製作）| 沿用 base

## 變更項處理

| C | 結果 | 位置 | 說明 |
|---|------|------|------|
| C01 | 完成 | S2 `#task-list .card` | |
| C02 | 完成 | S2、S4 `statusLabel()` | |
| C03 | 退回 | — | 規則類未引用 storyboard |

## data-page 對照
- brief 畫面清單 vs 產出：一致 | 缺 S<n>…／多 S<n>…

## 自行決定的呈現選擇
- <brief 沒指定、由 builder 決定的版面／元件／文案，一條一句；revise／patch 只列本次新增的>

## 偏離 brief
- <無 | 哪一條、為什麼>

## 待確認
- <brief／request 未定義或矛盾、需要業務決定的事；做法是留佔位不選邊>
```

- **結果**：`完成`、`部分`、`未做`（有理由）、`退回`（request 不合規）。
- **位置**：`data-page` 的畫面編號加上 CSS selector 或函式名，下一個 build 與一致性檢核都靠它定位。
- 「待確認」與「自行決定的呈現選擇」是一致性檢核反向盤點的輸入（`consistency-check.md` 程序 3）。

## `builds.md`（orchestrator 維護）

```markdown
# Mockup builds

| build | 模式 | base | 摘要 | 結果 | sha256 | artifact 版本 | 狀態 |
|-------|------|------|------|------|--------|---------------|------|
| v1-b01 | new | — | 依 brief v1 全部畫面 | 完成 | 3fa1c2d0 | 1792403746-95f1 | 已發布 |
| v1-b02 | patch | v1-b01 | C01 卡片間距；C02 逾期優先 | 完成 1／退回 1 | 9b07e611 | — | 未採用 |
```

- **狀態**：`已派遣` → `已產出` → `已發布`（採用並發布）｜`未採用`（審後不發布）｜`已凍結`（步驟 4 凍結的那個）。
- 每版凍結的 build 恰有一個；`export.json` 的 `build` 欄記同一個 id。

## 頁面契約（`artifact-design` 無法載入時的最低要求）

- 不寫 `<!doctype>`、`<html>`、`<head>`、`<body>`（發布時自動包外殼）；開頭放 `<title>`（2 到 4 字的名稱）。
- 色彩定義成 `:root` token，並在 `@media (prefers-color-scheme: dark)` 內以 `:root:not([data-theme="light"])`、
  另以 `:root[data-theme="dark"]` 重新定義；`body` 要有明確背景色。
- 外部 script 只用 cdnjs.cloudflare.com、cdn.jsdelivr.net/npm/、unpkg.com，且指定確切版本；樣式表只用 Google Fonts。
- 手機寬度可用：左右 16px 邊距，不產生水平捲動。
