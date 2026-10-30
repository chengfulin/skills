# 來源包模式：以需求交接包為規格來源

**來源包**是需求端交付的一個版本目錄，根有 `index.md`（文件索引）與 `AGENTS.md`（讀取規則、權威劃分、錨點、
回寫格式），另含 `handoff-notes.md`、`storyboard.md`、`prototype/`、`reference/`；make-mockup-harness 步驟 7 產出的
交接包就是這種結構。來源包本身不認識 sdd-harness，本檔定義 sdd-harness 怎麼接它。下文 `<來源目錄>` 指
`.specify/context/<slug>/v<N>/`。

舊格式交接包（開發 repo 有 `.specify/context/_shared/sdd-source-instructions.md`）照該檔執行，本檔不適用。

## 放進開發 repo

1. 新 repo 或尚未導入 SDD 的 repo：先走完步驟 1 init 與步驟 2 憲章，再放來源包。
2. 整個目錄複製到 `<來源目錄>`，以 `AGENTS.md` 的 sha256 表重算核對 `storyboard.md` 與 `prototype/index.html`，再 commit：
   `docs(context): 新增 <slug> v<N> 規格來源（StoryBoard＋Prototype）`。
   先 commit 的原因：步驟 0 的 dirty tree 分類表沒有 `.specify/context/` 的來源檔，未 commit 會歸為「不明」而中斷。
3. 使用者在啟動的 prompt 指定來源包位置與起點即可，例如「開新 feature『<title>』，規格來源 `.specify/context/<slug>/v<N>/`，
   先讀其 `AGENTS.md`；設計系統模式 A／B」；設計系統模式沒給就在步驟 5 問。來源包只屬於這個 feature，
   不寫進 repo 根的 AGENTS.md／CLAUDE.md。

## 0. 全程規則

1. `<來源目錄>` 唯讀，`AGENTS.md`「全程規則」照原文適用；權威劃分以 spec 規格來源段的五條為準（與 `AGENTS.md` 同義，另含設計系統模式與外部權威）。要改的是 spec.md，不是來源檔。
2. 偏離只登記在 spec.md「偏離登記」表（D-ID）；與 StoryBoard 明文不同的處置必須同時登記例外（X-ID）。
   Clarifications 與 `contracts/ui-contracts.md` 只引用 D-ID，不另寫一份。
3. 派遣任何 subagent 時，附件欄一律加上：`<來源目錄>/index.md`、`AGENTS.md`、`handoff-notes.md` 路徑、本 story 相關的截圖檔名、
   `spec.md` 規格來源段的位置。`prototype/index.html` 不當附件。
4. 找來源的順序固定：先讀 `<來源目錄>/index.md`，再依 spec 的錨點只取指到的片段。

## 1. 步驟 3 specify

- spec.md 依 `storyboard.md` 與 `handoff-notes.md` 整理，不重新摘要需求：
  - `**Input**` 一行寫「規格來源：StoryBoard v<N> ＋ Prototype v<N>（見下方規格來源段）」。
  - 緊接著插入 `$SKILL_DIR/references/spec-source-template.md` 的「規格來源」段，填齊來源表（路徑、完整 64 碼 sha256）、
    設計系統模式、範圍對照、來源缺口；偏離登記先寫「無」。
  - User Story 依 `handoff-notes.md` 的 US 對照表排序（Priority），編號 US1、US2…，每個 story 句尾標錨點 `[SB US-nn]` `[P S<n>]`。
  - 驗收條件（AC-01…）**原文搬移**，不改寫，句尾標 `[HO AC-01]`；Prototype 操作驗證轉來的條目（AC-P1…）也納入，標 `[HO AC-P1]` 與對應截圖 `[P S<n>-<序號>]`。
  - FR 依 `handoff-notes.md` 的功能需求候選展開並編號，每條句尾把來源寫成錨點
    （`[SB US-nn 規則 k]`、`[SB 全域規則 k]`、`[P S<n>]`、`[HO Q<n>]`；慣例見 `AGENTS.md`「錨點」）。
  - 「已定案決策」預填進 Clarifications；「範圍外」寫進 Assumptions。
  - 「補問清單」已有 PM 答案的直接採用並記入 Clarifications；沒有答案的寫 `[NEEDS CLARIFICATION: …]`，留給步驟 4。
- 產 spec 後自行跑一次規格來源段的機械檢查 1～9，不過就先修。
- 人為 review 閘門：簡報附 `prototype/screens/` 截圖（複製到 `brief/screens/` 引用、一張一列直排，見 `sdd-brief-writer`），讓 reviewer 對照。

## 2. 步驟 4 clarify

- 派 `sdd-spec-clarifier` 時，附件加一條檢查要求：spec 是否涵蓋 StoryBoard 每條規則與驗收條件、
  每個 User Story 是否標出畫面；遺漏列 HIGH。它會依 `index.md` 與錨點定範圍；
  若回報「來源範圍超出絆線」，依其原因處理（補錨點／拆 story），不要叫它少讀。
- 問題佇列先分類：
  - **互動類**（StoryBoard 沒寫、Prototype 有做的行為）：開啟 Prototype 實際操作，依權威劃分第 2 條
    以 Prototype 為準直接裁決，寫入 Clarifications 並註明「依 Prototype 操作結果」。不問使用者。
  - **業務類**（會改變資料、狀態、計算結果）：使用者不是 SA／PM 時，整理成 `specs/<NNN>/clarify-questions-for-sa.md`
    （題目、選項、建議、空白「答覆」欄）交 SA／PM，答案回來前依「延後釐清」規則處理。
  - **補問類**（成功指標、資料來源、權限、非功能）：以 `handoff-notes.md` 補問清單的答案為準。
- StoryBoard 自身矛盾或 Prototype 有做而 StoryBoard 沒寫的業務規則，裁決後登記 D-ID，「回寫來源」填「是」。

## 3. 步驟 5 plan

- 技術選型除語言、框架、測試工具外，必須同時確認**前端框架與元件庫**，並決定設計系統模式
  （A 沿用專案現行／B 自 Prototype 導入），寫回 spec 規格來源段。
- plan.md 新增「前端設計（依 Prototype v<N>）」節，內容落在 spec-kit 既有產物，不另立新檔：
  - `research.md`「設計 token」節：以 Playwright 讀 Prototype 的 computed style 萃取色彩、字級、間距、圓角
    （artifact 製作的 mockup 在 `:root` 有色彩與字型變數，可作命名參考；舊 Claude Design 匯出檔只有 hex；都以 computed style 為準）。
    模式 A：對應到專案現有 token，對不到的登記偏離。模式 B：Prototype `:root` 有變數名的 token 沿用其名；只有色碼等無名值的，由 plan 依用途命名，兩套命名各自成組、不交錯；對應表寫入 research.md。
  - `contracts/ui-contracts.md`：逐畫面列「區塊順序、元件對照、逐字文案與狀態、畫面對照（S<n> → 路由 → US<k> → 截圖）、偏離」。
    **文案從 Prototype DOM 抽取**（Playwright `innerText`）；偏離回填 spec 的 D-ID。
  - Prototype 假資料轉成前端 fixture／mock 資料層，頁面只能經資料存取層取用。
  - 規劃一支「Prototype 並列比對」E2E：依 `handoff-notes.md` 截圖索引重現每個狀態，輸出同名截圖到 `test-results/compare/`，並以 DOM 斷言檢查區塊順序與逐字文案。
- 人為 review 閘門：簡報把 Prototype 截圖與 ui-contracts 的版面上下相鄰對照（不左右並列），偏離逐條確認。

## 4. 步驟 6 tasks、步驟 7 analyze

- 前端任務以畫面為單位，每個任務標 `S<n>`、`US<k>`，並引用 `ui-contracts.md` 對應章節。
- analyze 時派 `sdd-spec-clarifier`（full）加做規格來源段機械檢查 1～9；第 7 條比對 `$SKILL_DIR/references/spec-source-template.md` 原文。

## 5. 步驟 8 implement

- `sdd-implementer`：附件加該 story 相關的 `ui-contracts.md` 章節與截圖檔名。
- `sdd-feature-validator`（frontend-web）：PASS 必須同時滿足
  1. spec 驗收條件以 Playwright 或 Chrome 實際操作通過；
  2. 版面比對：實作版截圖與 `prototype/screens/` 同名檔並列，區塊結構、元件位置、文案、狀態標籤不符即 FAIL；
     像素級差異與偏離登記已核准的項目不判 FAIL。
- `sdd-code-reviewer`：附帶檢查是否使用 design token 與共用元件，有無寫死色碼與樣式。
- 展示情境轉成 E2E 測試。

## 6. 完成報告與回寫

除既有內容外，依 `<來源目錄>/AGENTS.md`「回寫給 SA」的格式產出 `specs/<NNN>/handback-to-sa.md`，ID 沿用 spec 的編號：

| spec 登記 | 回寫類型 |
|---|---|
| D-ID（回寫來源＝是），類別「業務決策」或有對應 X-ID | 決策 |
| 其他 D-ID（回寫來源＝是） | 偏離 |
| G-ID | 缺口 |

鎖定的來源版本與 sha256 照填。開發期間需求端升版了來源包，預設**不套用**；要套用時依 spec「來源升版」規則處理。
