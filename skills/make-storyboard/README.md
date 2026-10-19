# make-storyboard

面向互動 Mockup 的 Story Board skill，是 `make-mockup-harness` 步驟 1 與 6 的子程序，也可單獨使用。

## 設計重點

- 下游是 Design Brief 與互動 Mockup，每條內容都要能對應畫面、狀態、角色。
- 兩種模式：初版 `new`、依回饋升版 `revise`。
- User Story 穩定編號 `US-nn`，brief 與檢核報告以編號引用。
- 欄位含角色與入口、狀態（含顯示優先序）、驗收條件（Given/When/Then）、展示情境。
- 變更紀錄含「版本」與「觸發來源」，版本號與 mockup 目錄 `mockups/v<N>` 對齊。
- 「待決定」為獨立的表，交接 SDD 前須全數定案。
- `references/question-framework.md` 固定提問順序；升版時被取代的規則以刪除線保留，供 mockup 對照。

## 檔案

| 檔案 | 說明 |
|---|---|
| `SKILL.md` | 角色設定、初版／升版流程、品質門檻 |
| `references/storyboard.template.md` | Story Board 模板 |
| `references/question-framework.md` | 初版模式的固定提問順序與每題的「為什麼問」 |
| `references/example-user-story.md` | 三個形態各異的 User Story 範例（few-shot），用來對齊粒度 |

## 單獨使用

```
/make-storyboard new 智能客服的對話紀錄查詢功能
/make-storyboard revise chat-log-query make-mockups/chat-log-query/feedback/v1-comments.md
```
