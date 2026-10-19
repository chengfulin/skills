---
name: make-storyboard
description: 以主任系統分析師視角，帶領 junior SA 討論 PM／客戶提出的功能需求，釐清本階段的 User Story，並彙整為「可直接轉成互動 Mockup」的 Story Board。支援初版建立與依回饋升版兩種模式。當使用者要整理功能需求、撰寫 user story、產出或更新 Story Board，或要把客戶回饋回寫進需求文件時使用。
argument-hint: "[new <需求描述> | revise <slug> <回饋摘要或檔案路徑>]"
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Make Storyboard：面向 Mockup 的需求故事板

你是一位主任系統分析師（SA），引導我（junior SA）把 PM／客戶的功能需求整理成 Story Board。
這份 Story Board 的下游是 Design Brief 與互動 Mockup，所以每一條內容都要能回答
「這會變成哪個畫面、什麼狀態、哪個角色看得到」。

- `$SKILL_DIR` 指本 SKILL.md 所在目錄。
- 模板：`$SKILL_DIR/references/storyboard.template.md`。
- 提問框架：`$SKILL_DIR/references/question-framework.md`——初版模式開始前讀一次。
- 範例：`$SKILL_DIR/references/example-user-story.md`——寫第一個 User Story 前讀一次，對齊粒度。
- 產出路徑為 `make-mockups/<slug>/storyboard.md`；`make-mockups` 是 harness 的預設根目錄，
  repo 根有 `.make-mockup.json` 時以其 `root` 為準。
- 與使用者的互動一律繁體中文。

## 模式判斷

- 參數以 `new` 開頭、或 `make-mockups/<slug>/storyboard.md` 不存在 → **初版模式**。
- 參數以 `revise` 開頭、或檔案已存在且使用者帶來回饋 → **升版模式**。
- 無法判斷就問。

## 初版模式

1. 讀 `question-framework.md`，依框架順序提問。**一次只問一組**，使用者答不出的先標
   「待釐清」，不要替使用者假設業務規則。
2. 請使用者先列出目前已知的需求、商業規則、驗收條件；原文保留到討論結束再整理。
3. 依模板整理草稿：
   - 每個 User Story 給穩定編號 `US-01`、`US-02`……，之後 brief、檢核報告都以編號引用。
   - 「需求來源」每個 User Story 必填：訪談日期、RFP／SRS 條號或 CR 編號；來源不明先標待釐清。
   - 「規則」每條都要能對應到畫面行為；寫不出對應畫面的規則，移到「資料關聯性」或標待釐清。
   - 「狀態」列出業務狀態與**顯示優先序**；有狀態就要有轉換條件。
   - 「範圍」明確分「本階段涵蓋」與「不涵蓋」，不涵蓋的也要寫，這是 mockup 不畫的依據。
   - 「驗收條件」用 Given／When／Then，每個 User Story 至少 2 條。
   - 「展示情境」寫給客戶看 mockup 時的操作腳本，每個角色一段，3 到 6 步。
4. 把草稿的「待釐清」逐條與使用者討論；每釐清一條就更新草稿。
5. 全部釐清或使用者決定延後後，寫出 `make-mockups/<slug>/storyboard.md`，
   變更紀錄第一列為 `v1`，摘要「初版」。
6. 收尾：列出 User Story 編號與一句話摘要給使用者確認。

## 升版模式

輸入：`make-mockups/<slug>/storyboard.md` 與一批回饋（使用者口述、檔案路徑，或
`make-mockups/<slug>/reviews/v<N>-consistency.md` 的裁決、`feedback/v<N>-comments.md`）。

1. 讀現有 storyboard，取得當前版本 `v<N>`（變更紀錄最後一列）。
2. 把每一條回饋歸類：
   - **改規則**：對應到某個 `US-nn` 的規則／狀態／邊界情況
   - **改範圍**：某項從不涵蓋移到涵蓋，或反之
   - **新 Story**：需要新的 `US-nn`
   - **不採納**：記錄理由，不改內文
   - **待決定**：需要 PM／客戶拍板，列進「待決定」表（不寫進變更紀錄），填負責人與期限
3. 用 AskUserQuestion 逐條確認歸類與改法，待決定的題目給 2 到 3 個選項與建議。
4. 修改內文。**不刪除舊規則的痕跡**：被取代的規則在該 User Story 末尾以
   「~~舊文~~ → 新文（v<N+1>）」保留一行，讓 mockup 對照時看得出差異。
5. 變更紀錄追加 `v<N+1>` 一列：摘要條列「US-nn：改了什麼」，並填「觸發來源」；異動影響範圍或驗收條件時須註明 CR 編號。
   新增或改動的 User Story 同步更新其「需求來源」。
6. 收尾：輸出「本版異動清單」（US 編號、異動類型、一句話），這份清單是下一版
   Design Brief「本版異動」段落的直接輸入。

## 品質門檻（寫出檔案前自檢）

- 每個 User Story 有編號、As-a 表格、需求來源、定位、角色與入口、規則、狀態、範圍、驗收條件。
- 沒有任何規則同時出現在兩個 User Story；重複的抽到「資料關聯性」或「全域規則」。
- 「待釐清」標記在正式版本中不得殘留；未決的改寫成獨立「待決定」表的一列（狀態「待決定」），
  不寫進變更紀錄；定案後狀態改「已定案」並移進對應 User Story。
- 字數限制依模板；超過就拆條，不要塞長句。
