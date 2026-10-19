# 階段完成準則、狀態檔 schema 與續跑

## 狀態檔 schema：`make-mockups/<slug>/.mockup-workflow.json`

```json
{
  "feature": "<slug>",
  "title": "<功能中文名>",
  "currentVersion": 1,
  "stage": "init | storyboard | brief | handoff | export | review | iterate | handed-off",
  "claudeDesign": {
    "projectId": null,
    "projectUrl": null,
    "pageFile": null
  },
  "designSystem": { "projectId": null, "name": null },
  "versions": [
    {
      "v": 1,
      "storyboardDate": "2026-10-01",
      "brief": "briefs/v1-design-brief.md",
      "briefSentAt": null,
      "mockup": "mockups/v1/index.html",
      "sourceFile": "治理工作台 Mockup（單檔版）.html",
      "sourceVersion": "1790239744982072",
      "sha256": null,
      "review": "reviews/v1-consistency.md",
      "feedback": "feedback/v1-comments.md",
      "commit": null,
      "handoff": null
    }
  ]
}
```

`stage` 代表**已完成**的最後一個階段；續跑從下一階段開始。
`versions[]` 每版一筆，欄位缺值為 `null`，不要省略鍵。
`handoff` 在步驟 7 交接後填 `{"date": "YYYY-MM-DD", "sha256": "<prototype sha256>", "targetRepo": null, "specDir": null}`，
後兩欄由開發者告知後補；舊狀態檔沒有這個鍵時視為 `null`。

## 完成準則

### §1 Story Board
- `storyboard.md` 存在，Introduction、變更紀錄（至少 v1 一列）、使用者角色、User Story、
  展示情境章節非空。
- 每個 User Story 有 `US-nn` 編號、As a / I want / so that 表格、需求來源、定位、角色與入口、規則、狀態、範圍（含不涵蓋）、
  驗收條件。
- 內文沒有殘留 `[待釐清]`；未決項目在「待決定」表格。
- 使用者已回「通過」。
- 狀態檔 `stage: storyboard`，`versions[0].storyboardDate` 填入。

### §2 Design Brief
- `briefs/v<N>-design-brief.md` 存在，畫面清單每項都標了對應 `US-nn`。
- 每個 storyboard User Story 至少對應一個畫面，否則 brief 要寫明為何不需畫面。
- N ≥ 2 時有「本版異動」段落。
- 使用者已確認。狀態檔 `stage: brief`，`versions[N-1].brief` 填入。

### §3 交接
- 狀態檔 `claudeDesign.projectId`、`projectUrl` 非空，`versions[N-1].briefSentAt` 填入。
- 狀態檔 `stage: handoff`。本階段不 commit（SA 在外部工具迭代中）。

### §4 匯出凍結
- `mockups/v<N>/index.html` 與 `export.json` 存在，`export.json` 的 sha256 與檔案相符。
- 狀態檔 `versions[N-1]` 的 `sourceFile`、`sourceVersion`、`sha256`、`mockup` 填入。
- 有留言則 `feedback/v<N>-comments.md` 存在。
- 狀態檔 `stage: export`。

### §5 一致性檢核
- `reviews/v<N>-consistency.md` 存在，四個分類段落皆在（可為「無」）。
- 「待決定」每題都有「裁決」欄，值為使用者答案或「延後」。
- 狀態檔 `stage: review`。

### §6 回饋回寫
- storyboard 變更紀錄新增 v<N+1> 一列，「觸發來源」已填；`revisions.md` 新增一列。
- 被取代的規則以刪除線保留在對應 User Story 末尾。
- 狀態檔 `currentVersion = N+1`，`versions[]` 新增一筆空殼，`stage: iterate`。

### §7 交接 SDD
- `handoff/v<N>/SDD-START.md` 與 `handoff/v<N>/.specify/context/` 存在，`pack-sdd-handoff.sh` 的 `check_*` 全數 ok。
- `prototype/screens/` 至少每個畫面一張，`sdd-input.md` 截圖索引與檔案一一對應。
- `sdd-input.md` 無殘留 `{…}` 待填欄位與 `<!-- -->` 指引；US 對照 Priority 與補問清單答案已由 PM 填齊。
- 狀態檔 `stage: handed-off`，`versions[N-1].handoff.date`、`sha256` 填入；`revisions.md` v<N> 列註記已交付。

## 續跑演算法

1. 讀狀態檔，取 `stage` 與 `currentVersion`。
2. 依下表決定起點：

| stage | 從哪一步繼續 |
|---|---|
| init | 步驟 1 |
| storyboard | 步驟 2 |
| brief | 步驟 3 |
| handoff | 步驟 4（先問使用者是否已在 Claude Design 迭代完成） |
| export | 步驟 5 |
| review | 步驟 6；使用者選擇交接 SDD 時步驟 7（見 SKILL.md 步驟 5 收尾分流） |
| iterate | 步驟 2（產 v<currentVersion> brief） |
| handed-off | 步驟 6（有開發回寫或新回饋時升版；否則告知本版已交付，流程可停） |

3. 起點階段的產物若已部分存在（例如 brief 草稿），先讓使用者決定沿用或重做。
4. 狀態檔與 `git log --oneline -- make-mockups/<slug>` 不一致時，以檔案系統實際存在的產物為準，
   修正狀態檔後再繼續。
