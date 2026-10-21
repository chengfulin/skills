# 一致性檢核：storyboard 對照 mockup

目的：把「規格 vs mockup」的核對變成可重複的程序，產出五類報告，並把「待決定」送回
storyboard。報告路徑：`make-mockups/<slug>/reviews/v<N>-consistency.md`。

執行者：程序 1 到 5 由 `mockup-consistency-checker` subagent 在獨立 context 執行（它不是 mockup 的製作者）；
程序 6 的使用者裁決由 orchestrator（SKILL.md 步驟 5）完成。

## 輸入
- `storyboard.md`（當前版本）
- `briefs/v<N>-design-brief.md`
- `mockups/v<N>/index.html`——**不整份 Read**，只用下列方式取證據
- `feedback/v<N>-comments.md`（若有）
- `mockups/v<N>/export.json` 的 `build` 欄所指 build 及其之前的 `mockup-src/builds/v<N>-b*/build.md`
  （只看「自行決定：呈現」「自行決定：互動行為」「偏離 brief」「待確認」四段；舊專案沒有 build 紀錄時改看 `feedback/v<N>-build-notes.md`）

## 程序

1. **畫面盤點**
   `KEYWORDS='<狀態詞>|<按鈕文字>|<提示文案>' bash $SKILL_DIR/scripts/extract-screens.sh <mockup 根>/<slug>/mockups/v<N>/index.html`
   「data-page」段即畫面清單（artifact 製作的 mockup 每個畫面都有 `data-page="S<n> 名稱"`）。
   關鍵字用完整詞，「S1」這類短字串會在 JS 裡大量誤中。
   舊專案的 Claude Design 單檔版把畫面打包成 JS 字串、沒有 `data-page`，改在步驟 4 開啟的本機頁面
   以 `find`／`read_page` 列出實際可切換的頁面。
   對照 brief 的畫面清單：brief 有、mockup 無 → 缺漏；mockup 有、brief 無 → 多出。
2. **規則逐條核對**
   對 storyboard 每個 `US-nn` 的每條「規則」與「驗收條件」的 Then，挑 1 到 3 個關鍵字
   （狀態名稱、按鈕文字、欄位名、提示文字），以限量 grep 取證：
   `grep -o -m 5 -E '<關鍵字A>|<關鍵字B>' mockups/v<N>/index.html | sort | uniq -c`
   有證據 → 一致；無證據 → 規格有、mockup 無；證據顯示行為與規則不同 → 衝突。
3. **反向盤點**
   從步驟 1 的多出項與各 build.md 的「自行決定：互動行為」（`B` 項，逐條列入）、「自行決定：呈現」（`P` 項，只列碰到規則的）、
   「偏離 brief」「待確認」，列出 mockup 已有但 storyboard 沒寫的規則；出處寫 `v<N>-b<kk>#B<nn>` 等完整引用。
   引用時標 build id 與 C 編號（例：`v1-b03#C02`），方便回寫時定位。
   帶 `data-demo` 的展示鷹架（角色切換列）不算多出項。
4. **操作驗證（互動行為）**
   篩選、聯動、展開、切換這類行為在字面上取證不到，改在**凍結的檔案**上實測（細節與實測坑見 `artifact-mockup.md` §4）：
   `bash $SKILL_DIR/scripts/serve-mockup.sh <slug> <N>`（run_in_background）→
   Chrome `navigate` 到 `http://127.0.0.1:8765/index.html`。頁面是最上層文件，
   `find` 找得到元素，`javascript_tool` 可直接 `.click()` 並讀回文字，不受視窗寬度限制；
   截圖只用來佐證外觀。每個行為記「操作 → 預期 → 實際」三欄。驗證完 kill 伺服器、關分頁。
   這一步驗的是 repo 裡凍結的檔案，而不是 artifact 的最新版本；凍結後 artifact 若又重新發布，以凍結檔為準。
5. **待決定**
   凡是需要業務決策才能定案的（例如狀態優先序、刪除後資料處置、權限邊界），
   列成問題，每題給 2 到 3 個選項與建議。
6. **裁決（orchestrator）**：checker 寫報告時「裁決」欄填 `待裁決`，並把每題以
   「問題｜選項（標建議）｜影響」回報；orchestrator 用 AskUserQuestion 逐題請使用者裁決，把答案填進「裁決」欄。
   「規格需修正」與「mockup 已有但規格未寫」的項目由 checker 在原表寫建議處置，不再抄進「待決定」表；
   「待決定」只放需要業務決策、原表放不下的問題。

## 報告格式

```markdown
# {feature} v{N} 一致性檢核

檢核日期：YYYY-MM-DD　　storyboard：v{N}　　mockup：mockups/v{N}/index.html（sha256 前 8 碼）

## 一致
| US | 規則／驗收條件 | 證據（關鍵字／畫面） |
|---|---|---|

## 操作驗證（本機開啟凍結檔實測）
| 操作 | 預期 | 實際 |
|---|---|---|

## 規格需修正
> storyboard 寫法有誤或不精確，mockup 的做法才對；要改 storyboard。
| US | 原文 | 建議改為 | 理由 |
|---|---|---|---|

## mockup 已有但規格未寫
> 建議補進 storyboard，或確認是否採用。
| 畫面 | 行為 | 建議處置（採用／移除／待決定） |
|---|---|---|

## 規格有但 mockup 缺漏
| US | 規則／畫面 | 下一版 brief 要補的指示 |
|---|---|---|

## 待決定
| # | 問題 | 選項 | 建議 | 裁決 |
|---|---|---|---|---|
```

## 寫回規則
- 「規格需修正」與「待決定」的裁決 → 步驟 6 交給 `make-storyboard` 升版模式寫進對應 `US-nn`。
- 「mockup 已有但規格未寫」裁決為採用 → 補進 storyboard 規則；裁決為移除 → 寫進下一版 brief 的「本版異動」。
- 「規格有但 mockup 缺漏」→ 直接進下一版 brief 的「本版異動」。
