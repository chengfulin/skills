# 步驟 7：交接開發

目的：把凍結的 v<N> storyboard 與 mockup 打包成**與開發流程無關**的需求交接包：一份文件索引、
一份給 AI agent 的 `AGENTS.md`（`CLAUDE.md` 匯入同一份），開發端用任何流程或工具都能直接採用，
做 mockup 的人與做開發的人可以是不同人、不同 repo。開發流程怎麼接（例如 sdd-harness 的來源包模式）由該流程自己定義，
本包不寫。交接後本版鎖定；開發期的偏離由開發端以 `handback-to-sa.md` 交回，走步驟 6 升版。

## 前提

全部成立才交接。`pack-handoff.sh` 會機械檢查前四項，第五項由 orchestrator 自行做：

1. `reviews/v<N>-consistency.md` 的「待決定」無未裁決項（裁決欄非空且不是「延後」）。
2. `storyboard.md`「待決定」表全數「已定案」。
3. 版本一致：storyboard 變更紀錄最後一列 = `mockups/v<N>` = 目錄 v<N>。
4. `mockups/v<N>/index.html` 的 sha256 與 `export.json` 相同。
5. **StoryBoard 自身一致性與 Prototype 反查**（POC 發現 clarify 問題多來自這裡）：
   - 各 US「狀態」的轉換描述與「全域規則」是否矛盾（例：轉換寫「到期日轉已到期」，規則寫「7 天內含當日」）。
   - Prototype 有實作、StoryBoard 沒寫的**業務規則**（會改變資料、狀態、計算結果的，不是呈現）。
     用 `extract-screens.sh` 與限量 grep 比對 storyboard 規則關鍵字，或開 `serve-mockup.sh` 操作。
   - 發現項目用 AskUserQuestion 請使用者決定：回步驟 6 修 storyboard 再交接，或列為已知缺口寫進 handoff-notes.md。

## 程序

1. 打包：

   ```bash
   bash $SKILL_DIR/scripts/pack-handoff.sh <slug> <N>
   ```

   產出 `make-mockups/<slug>/handoff/v<N>/`：

   ```
   handoff/v<N>/
   ├── index.md            # 文件索引：用途、權威、取證方式、涵蓋範圍；script 產生，涵蓋欄本步驟核對
   ├── AGENTS.md           # 給 AI agent：讀取順序、全程規則、權威劃分、錨點、回寫格式（已代入版本與 sha256）
   ├── CLAUDE.md           # 只有 `@AGENTS.md`，Claude Code 匯入同一份
   ├── handoff-notes.md    # 交接說明骨架，本步驟填
   ├── storyboard.md
   ├── prototype/{index.html, export.json, screens/}
   └── reference/{v<N>-design-brief.md, v<N>-consistency.md, feedback}
   ```

   任一 `check_*=FAIL` 就停下來回報，依訊息回步驟 5 或 6；目標目錄已存在表示本版已交接過，要重做需使用者同意後刪除。

2. 截圖到 `prototype/screens/`，並填 `handoff-notes.md`「截圖索引」：
   - 規格：1440×900、Chrome、full-page，檔名 `S<n>-<兩位序號>-<狀態>.png`，畫面 ID 沿用 brief。
   - 覆蓋範圍：每個畫面的預設狀態，加上**每個互動後狀態**（點卡片、套用篩選、空狀態、各類明細展開）。
     以 brief 的展示腳本與一致性檢核的「操作驗證」表為清單。
   - 做法：`serve-mockup.sh <slug> <N>`（run_in_background）後，優先用 Playwright：
     `npx -y playwright screenshot --browser chromium --viewport-size=1440,900 --full-page <url> <out.png>`
     只能拍預設狀態；互動後狀態寫一支短 Playwright script（click 後 `page.screenshot({fullPage:true})`）放 scratchpad 執行。
     沒有 node 環境時用 Chrome 工具 `resize_window` 1440×900 後操作並截圖，再由使用者存檔；
     `resize_window` 在 macOS 分割／全螢幕下會回報成功但不生效（見 artifact-mockup.md §4），
     截圖前以 `javascript_tool` 讀 `innerWidth` 確認。
   - 拍完 kill 伺服器、關分頁。

3. 核對 `index.md` 並填 `handoff-notes.md` 其餘章節（模板已含填寫指引）。
   `index.md` 是開發端找來源的入口，錨點都要能在它的「涵蓋」欄找到：script 自動抓的「涵蓋」欄（storyboard 的 US-nn、
   mockup 的 `data-page` 畫面）要與 storyboard、brief 畫面清單一致，`{填：…}` 補齊；
   不要刪列，也不要改取證方式欄。`AGENTS.md` 由範本產生，不改。`handoff-notes.md` 原則：
   - 驗收條件**原文搬移**，不改寫；每條標 US。
   - 一致性檢核「操作驗證」表改寫成 Given／When／Then，作為互動驗收（AC-P 系列）。
   - 功能需求候選每條標來源（US-nn 的規則／狀態／邊界、全域規則、brief 本版異動）。
   - 已定案決策：storyboard 待決定表與各版檢核裁決。
   - 範圍外：各 US 的「不涵蓋」與 Prototype 中不屬本 feature 的部分（登入頁、側欄其他項目）。
   - 前提第 5 項的發現寫進「交接前提核對」對應列。
   - US 對照的 Priority 與補問清單的答案**留空**，不要代填。

4. PM 補答：用 AskUserQuestion 確認 PM 是否在場。在場就逐題問完填入；不在場就停在這裡，
   告知使用者把 `handoff-notes.md` 交 PM 填 Priority 與補問清單後說「繼續交接」。
   **答案未填齊不得進入第 5 步**，否則開發端會卡在待釐清或自行假設。

5. 收尾：
   - 狀態檔 `stage: handed-off`；`versions[N-1].handoff` 填
     `{"date": "YYYY-MM-DD", "sha256": "<prototype sha256>", "targetRepo": null, "targetPath": null}`
     （後兩欄開發者告知後再補）。
   - `revisions.md` 的 v<N> 列「變更摘要」末尾加「；已交付開發（YYYY-MM-DD）」。
   - commit：`handoff(<slug>): v<N> 交付開發`。
   - 告知使用者：把 `handoff/v<N>/` 整個目錄（或其 git 路徑）交給開發者，從 `index.md` 開始；
     開發者讓 agent 開工時，在 prompt 指定交接包路徑並以其 `AGENTS.md` 為起點（範例在 `index.md` 開頭）；
     用 sdd-harness 開發時，放進開發 repo 的方式見該 skill 的 `references/source-package.md`。

## 開發回寫

開發者交回 `handback-to-sa.md`（格式見 `AGENTS.md`「回寫給 SA」，每列類型為偏離／決策／缺口）。使用者貼上後走步驟 6：
偏離依處置改寫對應條文並留刪除線；決策寫進對應 US 規則；缺口逐條由使用者決定是否補進 storyboard。
舊格式（D-ID／X-ID／G-ID）依序對應偏離／決策／缺口。
觸發來源寫「開發回寫（<開發 repo>/<feature>）」。升版後若開發尚未結束，由開發端決定是否套用。

## 完成準則

見 workflow-stages.md §7。
