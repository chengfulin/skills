# SDD 交接輸入：{title} v{N}

> 交接包由 make-mockup-harness 步驟 7 產出。本目錄複製進開發 repo 並入版控後唯讀，新版另開目錄。
> 交接日期：{date}　　交接人：{填 SA 姓名}　　PM 補答：{填 PM 姓名／日期}
>
> `{…}` 為待填欄位，交接前全部填完或刪除；`<!-- -->` 為填寫指引，填完刪除。

## 交接前提核對

| 條件 | 結果 |
|---|---|
| 最新一致性檢核無未裁決「待決定」 | 是（`pack-sdd-handoff.sh` 已檢查，見 `reference/v{N}-consistency.md`） |
| storyboard 待決定表全數定案 | 是（`pack-sdd-handoff.sh` 已檢查） |
| 版本一致 | storyboard 變更紀錄最後一列 v{N} = 目錄 v{N} = mockups/v{N} |
| Prototype sha256 = export.json | 是：{sha_prototype} |
| StoryBoard 自身一致性（狀態轉換 vs 全域規則） | {已檢查，無矛盾 ｜ 發現：…，已於 v{N} 修正 ｜ 發現：…，列為已知缺口} |
| Prototype 有實作、StoryBoard 未寫的業務規則 | {無 ｜ 有：…，處置：補進 storyboard／列為已知缺口} |

## 檔案清單

| 檔案 | 說明 | 權威 |
|---|---|---|
| `storyboard.md` | StoryBoard v{N} 原檔（sha256 {sha_storyboard}） | 業務規則 |
| `prototype/index.html` | Prototype v{N} 單檔 HTML（約 {proto_size}，**不得整份 Read**；以截圖、限量 grep 或本機開啟操作取證） | 呈現 |
| `prototype/export.json` | Claude Design 匯出紀錄（含 sha256） | — |
| `prototype/screens/*.png` | 1440×900、Chrome、full-page 截圖（衍生產物） | 無獨立權威 |
| `reference/v{N}-design-brief.md` | Design Brief v{N}：畫面 ID、假資料表、展示腳本 | 參考 |
| `reference/v{N}-consistency.md` | v{N} 一致性檢核報告（含操作驗證） | 參考 |

### 截圖索引

<!-- 畫面 ID 沿用 Design Brief 的 S<n>。每個畫面至少一張預設狀態，加上每個互動後狀態
     （點卡片、套用篩選、空狀態、各類明細展開、錯誤或提示）。檔名 S<n>-<兩位序號>-<狀態>.png。 -->

| 檔名 | 畫面 | 狀態 | 對應 US |
|---|---|---|---|
| S1-01-{狀態}.png | S1 {畫面名} | {預設：…} | US-01 |

## US 對照

<!-- Priority 由 PM 指定（P1 為 MVP 必要）。spec 的 User Story 會依此編號與排序。 -->

| StoryBoard | spec | Priority | 畫面 | 理由 |
|---|---|---|---|---|
| US-01 {名稱} | US1 | {P1} | S1 | {一句話} |

## 驗收條件原文

<!-- 逐條從 storyboard 各 US 的「驗收條件」原文搬移，不改寫。ID 為 AC-nn，spec 必須原文保留。 -->

| ID | US | Given / When / Then |
|---|---|---|
| AC-01 | US-01 | Given … / When … / Then … |

### Prototype 操作驗證轉來的互動驗收

<!-- 取自 reference/v{N}-consistency.md「操作驗證」表，改寫成 Given／When／Then；以 v{N} 假資料為準。 -->

| ID | US | Given / When / Then |
|---|---|---|
| AC-P1 | US-01 | Given v{N} 假資料 / When … / Then … |

## FR 候選

<!-- 每條標來源：US-nn 的規則／狀態／邊界、全域規則、或 brief 本版異動。spec 階段據此展開並編號。 -->

| 候選 | 內容 | 來源 |
|---|---|---|
| FR-a | … | 全域規則 |

## 已定案決策

<!-- storyboard 待決定表已定案項、各版一致性檢核的裁決。spec 階段預填進 Clarifications。 -->

| # | 決策 | 出處 |
|---|---|---|
| 1 | … | storyboard 待決定 #1 |

## 範圍外

<!-- 各 US 的「不涵蓋」與 Prototype 中不屬本 feature 的畫面或區塊。spec 階段寫入 Assumptions。 -->

- US-01：…
- Prototype：{登入頁、側欄其他選單等僅外框展示的部分}

## 補問清單

<!-- StoryBoard 沒有、SDD 一定會問的事。答案欄由 PM 填；沒有答案的題目，開發者在 clarify 階段只能寫 [NEEDS CLARIFICATION] 等人。 -->

| # | 主題 | 問題 | PM 答案 |
|---|---|---|---|
| Q1 | Success Criteria | 可量測的成功指標是什麼？ | {…} |
| Q2 | 資料來源 | 資料由 API、DB 或假資料提供？格式與時程？ | {…} |
| Q3 | 權限與登入 | 誰能使用？需要登入與角色控制嗎？ | {…} |
| Q4 | 「今日」基準 | 日期相關判定以什麼為今日？展示與測試固定哪一天？ | {…} |
| Q5 | 非功能需求 | 資料量級、瀏覽器、響應式、效能基準？ | {…} |
