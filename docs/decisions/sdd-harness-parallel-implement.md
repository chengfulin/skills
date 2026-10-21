# 決策紀錄：sdd-harness 實作階段的 story 並行化

- 日期：2026-10-21
- 狀態：第一、二階段已採行；第三階段暫緩，待觀察資料決定
- 影響範圍：`skills/sdd-harness/`（步驟 8 實作迴圈）

## 背景

sdd-harness 步驟 8 逐 user story 執行：影響邊界 → implementer → 越界檢查 →
validator → reviewer → commit。希望評估能否讓多個 story 並行實作以縮短時間。
討論的三個問題：

1. 並行前應先分析 story 間的實作範圍重疊、程式流程相依與功能優先順序；互相
   影響或依賴的 story 不可並行。
2. tasks.md 的勾選由各 implementer 自行更新，但記錄在同一份檔案——應改由主對話
   （orchestrator）更新，implementer 只負責實作與回報。
3. 抽象層的改動（adapter 新增 method、service 新增 DI 參數）是否會造成衝突。

## 分析

### 現行流程預設「同一時間只有一個 story 在動」

| 機制 | 並行時的問題 |
|------|--------------|
| 越界檢查以 `git diff HEAD` 加 untracked 判定 | 分不出哪個檔案屬於哪個 story |
| reviewer 的 diff 範圍＝上一個 commit 之後全部變更 | 兩個 story 的變更混在一起審 |
| validator 在工作目錄跑測試 | 另一個 story 改到一半，測試結果不可信 |
| 收尾 `git add -A && git commit` | 會把另一個 story 的半成品一起 commit |
| 續跑找「第一個未完成的 story」 | 無法表達多個進行中的 story |

結論：真正的並行必須每個 story 一個 git worktree，再依序合併回 feature branch；
只並行 implementer、其餘留在同一工作目錄，上表每一項都要另外處理，成本更高。

### 問題 1：衝突判定要寫成可檢查的規則

每個 story 取得以下集合，兩兩比對，任一成立即不可並行：

- 寫入集合（新增／修改的檔案與 symbol）有交集 → `寫入`
- 一方的寫入出現在另一方的讀取集合（會呼叫、繼承、注入的既有 symbol）→ `相依`
- 共用的非程式資源相同（migration、套件清單與 lockfile、設定檔、登錄點、
  i18n、測試 fixture、測試執行期的 port／DB）→ `資源`
- 抽象層契約變更波及另一方（見問題 3）→ `契約`
- tasks.md／spec 宣告相依 → `宣告`

功能優先順序的處理：spec-kit 常讓每個 story 有不同優先級，若「優先級不同」就算
衝突，等於全部依序執行。因此只把 **P1（MVP）** 視為硬性前置——P1 story 自成最前面
的群組；其餘優先級只決定執行與合併順序，不構成衝突。

分析基礎薄弱時（greenfield 索引近空、降級 grep），任一方信心為低即一律記為衝突，
寧可錯殺。

### 問題 2：tasks.md 單一寫入者

同意。`.sdd-workflow.json` 原本就只由主對話寫；實際會被多方寫入的是 tasks.md 的
`[X]`。改為 implementer 回報完成的任務 ID、主對話勾選。主對話本身依序執行，
寫入自然有先後，不會互相覆蓋。代價是主對話須信任回報，但後面仍有 validator 與
reviewer 兩道閘門把關，可以接受。

### 問題 3：抽象層改動的衝突

兩類：

- **文字衝突**：兩個 story 都改同一個 interface 或 DI 註冊檔——寫入集合規則擋得下，
  但這類熱點檔案會讓多數 story 被判定依序執行。
- **語意衝突（文字不衝突、合併後才壞）**：例如 US2 在 interface 加 `refund()`，
  US3 同時新增該 interface 的實作類別；或 US2 在 service 建構子加 DI 參數，US3 的
  新測試用舊簽名建構。git merge 不報錯，合併後編譯或測試失敗。影響分析只看得到
  分析當下已存在的實作與呼叫端，看不到另一個 story 將新增的類別。

因應：契約變更列為獨立衝突類型，比對時同時看「另一方的讀寫集合」與「plan.md
規劃另一方會新增的實作類別」。真正並行時（第三階段）另需：先把共用的契約改動
做成一個依序完成的「契約小批」，以及每次合併後一律全量 build 與測試。

## 決策

分三階段導入，**本次只做第一、二階段**。

### 第一階段（已採行）：單一寫入與讀取集合

- `sdd-implementer` 不再勾選 tasks.md，回報逐一列出完成的任務 ID；改動 tasks.md
  視為越界。覆蓋 speckit-implement「完成即標 `[X]`」的指示。
- 主對話在每次 implementer 回報後、進下一個閘門前，核對 ID 屬於派遣範圍並以一行
  `perl` 指令勾選、`grep` 計數確認。
- `sdd-impact-analyzer` 的邊界報告新增「依賴的既有 symbol（讀取集合）」一節。

### 第二階段（已採行）：並行規劃，觀察期只出建議

- Foundational（無則 Setup）commit 之後、第一個 story 之前，新增步驟 1P：在同一
  則訊息並行派每個未完成 story 一個 `sdd-impact-analyzer`（`plan` 模式，輸出寫入／
  讀取集合、共用資源、契約變更、宣告相依、信心，上限 40 行）。
- 主對話依上述規則兩兩判定、貪婪分組，結果寫入
  `steps.implement.parallel_plan` 並立即 commit（`chore(sdd): 完成並行規劃（NNN）`），
  避免狀態檔混入下一個 story 的越界檢查。
- **執行順序不變**，仍依 tasks.md 逐 story；1P 的集合不取代每個 story 開工前的
  邊界報告（前面 story commit 後程式碼已變）。
- 完成報告附「並行規劃觀察」：群組數、可並行 pair 數、衝突類型分布，以及
  **規劃誤判**——被判可並行的 pair 實際 commit 的檔案有交集者。
- 重規劃（8R）回到步驟 8 前刪除 `parallel_plan`，由 1P 依新任務重做；續跑時缺少
  規劃則先補做。

### 第三階段（暫緩）：worktree 並行實作

待第二階段累積資料後再決定。啟動前須解決：

- 每個 story 一個 worktree；被 gitignore 的 `.codegraph/`、`.env` 等不會出現在
  worktree，測試可能因缺 `.env` 失敗。
- 合併順序依優先級；每次合併後全量 build 與測試（等同 validator `all`），失敗的
  story 改在主線依序重做，不在合併時臨時修。
- tasks.md 勾選在合併回主線時才寫入，story 自己的 commit 不碰 tasks.md。
- 狀態檔與續跑演算法需能表達多個進行中的 story 與其 worktree 路徑。
- 同時並行上限 2 個 story。
- 待決：「契約小批」前移會改變 tasks.md 結構，歸 8R 重規劃處理，或定義為不新增
  任務、只調整順序的輕量重排。

**啟動門檻（建議）**：在數個 feature 上，被判可並行的 pair 占比有實際價值，且
規劃誤判為零或僅限可補規則的類別（例如補一種共用資源）。若多數 feature 幾乎
全部依序，第三階段不值得做。

## 不採行的方案

- **同一工作目錄只並行 implementer、其餘依序**：越界檢查、reviewer diff、validator
  測試、commit 都要改成依路徑歸屬，複雜度高於 worktree，且仍有測試互相干擾。
- **把優先級不同一律視為衝突**：會讓幾乎所有 story 依序，規劃失去意義。
- **允許登錄點「只追加一行」的例外並行**：正是語意衝突的典型來源，觀察期不開放。
