# sdd-harness 規格來源模式：各階段補充指示

> 用途：由 make-mockup-harness 步驟 7 的 `pack-sdd-handoff.sh` 代入 slug 與版本後，隨交接包複製到開發 repo 的
> `.specify/context/_shared/sdd-source-instructions.md`，
> 每次啟動或續跑 sdd-harness 的 prompt 都要求先讀本檔。這樣指示才能跟著 repo 走，
> 不會因為 session 中斷、換人、換機器而消失。
> 本檔是流程指示，不是規格來源；規格來源只有 `.specify/context/<slug>/v<N>/` 內的檔案。
> `{slug}`、`{N}` 由腳本代入，其餘內容不要改寫；需要例外時登記在 spec 的「權威劃分例外」。

## 0. 全程規則

1. 規格來源目錄 `.specify/context/{slug}/v{N}/` 唯讀。要改的是 spec.md，不是來源檔。
2. `prototype/index.html` 是 Claude Design 匯出的單檔（內嵌圖片與字型，通常數 MB），**不得整份 Read**。取證據的方式只有三種：
   看 `prototype/screens/` 截圖（索引在 `sdd-input.md`）、限量 grep
   （`grep -o -m 5 -E '<詞A>|<詞B>' …`）、或以本機 http server 開啟後用 Playwright／Chrome 實際操作。
3. 權威劃分五條以 `.specify/context/_shared/spec-source-template.md` 的原文為準，
   不在任何階段改寫。業務規則看 StoryBoard，呈現看 Prototype，兩者沒定義的依專案慣例補齊並登記「來源缺口」。
4. 偏離只登記在 spec.md「偏離登記」表（D-ID）；與 StoryBoard 明文不同的處置必須同時登記例外（X-ID）。
   Clarifications 與 `contracts/ui-contracts.md` 只引用 D-ID，不另寫一份。
5. 派遣任何 subagent 時，附件欄一律加上：`sdd-input.md` 路徑、本 story 相關的截圖檔名、
   `spec.md` 規格來源段的位置。不要把 `prototype/index.html` 當附件。

## 1. 步驟 3 specify

- 不要重新摘要需求。spec.md 的內容依 `storyboard.md` 與 `sdd-input.md` 整理：
  - `**Input**` 一行寫「規格來源：StoryBoard v{N} ＋ Prototype v{N}（見下方規格來源段）」。
  - 緊接著插入 `spec-source-template.md` 的「規格來源」段，填齊來源表（路徑、完整 64 碼 sha256）、
    設計系統模式、範圍對照、來源缺口；偏離登記先寫「無」。
  - User Story 依 `sdd-input.md` 的 US 對照表編號與優先序，每個 story 標「來源：US-nn」與「畫面：S<n>」。
  - 驗收條件（AC-01…）**原文搬移**，不改寫；Prototype 操作驗證轉來的條目（AC-P1…）也納入。
  - FR 依 `sdd-input.md` 的 FR 候選展開並編號，每條保留來源標註。
  - `sdd-input.md`「已定案決策」預填進 Clarifications；「範圍外」寫進 Assumptions。
  - `sdd-input.md`「補問清單」已有 PM 答案的直接採用並記入 Clarifications；沒有答案的寫
    `[NEEDS CLARIFICATION: …]`，留給步驟 4。
- 產 spec 後自行跑一次規格來源段的機械檢查 1～7，不過就先修。
- 人為 review 閘門：簡報附 `prototype/screens/` 截圖，讓 reviewer 對照。

## 2. 步驟 4 clarify

- 派 `sdd-spec-clarifier` 時，附件加一條檢查要求：spec 是否涵蓋 StoryBoard 每條規則與驗收條件、
  每個 User Story 是否標出畫面；遺漏列 HIGH。
- 問題佇列先分類：
  - **互動類**（StoryBoard 沒寫、Prototype 有做的行為）：先開啟 Prototype 實際操作，依權威劃分第 2 條
    以 Prototype 為準直接裁決，寫入 Clarifications 並註明「依 Prototype 操作結果」。不問使用者。
  - **業務類**（會改變資料、狀態、計算結果）：若執行者不是 SA／PM，不得代答。整理成一份問題清單
    （題目、選項、建議）交給 SA／PM，答案回來前依 sdd-harness 的「延後釐清」規則處理。
  - **G7 類**（Success Criteria、資料來源、權限、非功能）：以 `sdd-input.md` 補問清單的答案為準。
- StoryBoard 自身矛盾或 Prototype 有做而 StoryBoard 沒寫的業務規則，裁決後登記 D-ID，
  「回寫來源」填「是」。

## 3. 步驟 5 plan

- 技術選型除語言、框架、測試工具外，必須同時確認**前端框架與元件庫**，並決定設計系統模式
  （A 沿用專案現行／B 自 Prototype 導入），寫回 spec 規格來源段。
- plan.md 新增「前端設計（依 Prototype v{N}）」節，內容落在 spec-kit 既有產物，不另立新檔：
  - `research.md`「設計 token」節：以 Playwright 讀 Prototype 的 computed style 萃取色彩、字級、間距、圓角
    （Claude Design 匯出檔沒有 CSS 變數，限量 grep 只抓得到 hex，抓不到套用關係）。
    模式 A：對應到專案現有 token，對不到的登記偏離。模式 B：由 plan 依用途命名，不要假設 Prototype 有 token 名。
  - `contracts/ui-contracts.md`：逐畫面列「區塊順序、元件對照、逐字文案與狀態、畫面對照（S<n> → 路由 → US<k> → 截圖）、偏離」。
    **文案從 Prototype DOM 抽取**（Playwright `innerText`），不要人工轉寫；偏離回填 spec 的 D-ID。
  - Prototype 假資料轉成前端 fixture／mock 資料層，頁面只能經資料存取層取用。
  - 規劃一支「Prototype 並列比對」E2E：依 `sdd-input.md` 截圖索引重現每個狀態，輸出同名截圖到 `test-results/compare/`，並以 DOM 斷言檢查區塊順序與逐字文案。
- 人為 review 閘門：簡報並列 Prototype 截圖與 ui-contracts 的版面，偏離逐條確認。

## 4. 步驟 6 tasks、步驟 7 analyze

- 前端任務以畫面為單位，每個任務標 `S<n>`、`US<k>`，並引用 `ui-contracts.md` 對應章節。
- analyze 時派 `sdd-spec-clarifier`（full）加做規格來源段機械檢查 1～7；第 7 條比對
  `.specify/context/_shared/spec-source-template.md` 原文。

## 5. 步驟 8 implement

- `sdd-implementer`：附件加該 story 相關的 `ui-contracts.md` 章節與截圖檔名。
- `sdd-feature-validator`（frontend-web）：PASS 必須同時滿足
  1. spec 驗收條件以 Playwright 或 Chrome 實際操作通過；
  2. 版面比對：實作版截圖與 `prototype/screens/` 同名檔並列，區塊結構、元件位置、文案、狀態標籤不符即 FAIL；
     像素級差異與偏離登記已核准的項目不判 FAIL。
- `sdd-code-reviewer`：附帶檢查是否使用 design token 與共用元件，有無寫死色碼與樣式。
- 展示情境轉成 E2E 測試。

## 6. 完成報告

除 sdd-harness 既有內容外，必須列出：

1. 偏離登記中「回寫來源＝是」的 D-ID 與 X-ID 清單（原文、處置、理由），交給 SA 以 make-mockup-harness 升版 StoryBoard 與 Prototype。
2. 來源缺口清單（G-ID），供 SA 判斷是否補進 StoryBoard。
3. 鎖定的來源版本與 sha256，供 SA 在 mockup 工作區登記「已交付開發」。
