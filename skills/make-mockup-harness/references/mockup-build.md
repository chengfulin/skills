# Mockup build：輸入與產出紀錄

步驟 3 的每一次產出都是一個 **build**：orchestrator 寫輸入（`request.md`），`mockup-builder` 依輸入產出
HTML 快照與產出紀錄（`index.html`、`build.md`），orchestrator 審過後採用、發布並在索引回填版本 id。
任何修改（含改字、調間距）都開新 build，不直接改工作檔——迭代與回退都靠 build id 索引。

```
mockup-src/
├── index.html              # 發布用工作檔 = 目前採用的 build 快照（orchestrator 複製過來）
├── builds.md               # 索引（orchestrator 維護）
└── builds/
    └── v<N>-b<kk>/
        ├── request.md      # 輸入（orchestrator 寫，派遣後不改）
        ├── index.html      # 產出快照（builder 寫）
        └── build.md        # 產出紀錄（builder 寫）
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
| `patch` | 迭代中的任何修改 | 通常是目前採用的 build | SA 對話、artifact 留言、回退要求 |

## `request.md`（orchestrator 寫）

```markdown
# Build request v<N>-b<kk>

- 模式：new | revise | patch
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

- 模式：patch｜base：v<N>-b<kk>（sha256 <前 8 碼>）
- 產出：builds/v<N>-b<kk>/index.html（<bytes> bytes，sha256 <前 8 碼>）
- artifact-design：已載入 | 未載入（依 mockup-build.md「頁面契約」製作）

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
