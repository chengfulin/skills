# sdd-baseline

團隊 SDD 憲章基線（[chengfulin/sdd-baseline](https://github.com/chengfulin/sdd-baseline)，private）的參考型 skill。
在 SDD 流程（`sdd-harness`）開始前，帶使用者決定「這個專案要套多重的規範」；也能查條款、同步基線副本。

## 設計重點

- 三個維度分開決定，對應憲章的設計：**專案類型**描述成熟度、**服務風險分級**描述出錯的後果、**導入階段**是團隊層級的紀律成熟度。
- 提問選項與判定規則都從 `references/baseline/` 的表格即時讀出，不在 skill 內寫死；基線升版只要重跑同步腳本。
- 產出「SDD 導入決策摘要」：欄位對應 `sdd-harness` 的 `sdd-adoption.json`，並附可直接貼進專案 README 的「SDD 導入宣告」區塊。
- `references/baseline/` 就是 `sdd-harness` 步驟 2 預設複製到目標專案 `.specify/memory/baseline/` 的來源（含 `manifest.json`）。

## 檔案

| 檔案 | 說明 |
|---|---|
| `SKILL.md` | 三種模式：決策（decide）、查條款（lookup）、同步（sync） |
| `references/question-framework.md` | 決策模式的五組提問、每題該查哪張表、判定規則 |
| `references/decision.template.md` | 導入決策摘要的輸出格式 |
| `references/baseline/` | 憲章基線副本（README、constitution、API／FE／SH／SVC／DEP 延伸、tech-standards）＋ `manifest.json` |
| `scripts/sync-baseline.sh` | 從本地 checkout 或 `gh api` 更新基線副本並重寫 manifest |

## 使用

```
/sdd-baseline decide 內部用的報表查詢 API，讀正式 DB 但只讀不寫
/sdd-baseline lookup §API-4
/sdd-baseline lookup 審計日誌
/sdd-baseline sync ~/Documents/Personal/sdd-baseline
```

## 與 sdd-harness 搭配

`sdd-harness` 步驟 2 預設直接複製本 skill 的 `references/baseline/`，不需額外設定
（要改用其他位置的副本時設 `SDD_BASELINE_DIR=<目錄>`）。
建議先跑 `/sdd-baseline decide` 定案，再把摘要貼進 `/sdd-harness` 的啟動 prompt，步驟 2 會直接採用。
