# SDD 導入決策摘要（輸出模板）

產出時整段輸出給使用者；`<>` 內換成實際值，「依據」欄寫一句話並指向基線的表或條款。
一個 repo 有多個可部署單元時，第一張表每個單元各一列組。

## SDD 導入決策摘要

> 基線：`<repo>` v<constitution 版本>@<sha 前 7 碼>（tech-standards v<版本>）

| 項目 | 值 | 依據 |
|------|-----|------|
| 專案類型 | <正式專案／POC／內部探索型實驗／Spike・Tweak> | 使用者選擇 |
| 服務風險分級 | <Critical／Standard／Internal／Experimental> | 對照表預設 <X>；調整條件：<勾選的風險因子，或「無」> |
| 應用類型 | <表的第一欄名稱>（`<app_type>`） | 載入文件表 |
| 導入階段 | 第 <N> 階段（<階段名>） | 進入第 <N+1> 階段的條件：<尚未成立的條目，或「全部成立」> |
| 載入文件 | <constitution.md ＋ 延伸檔清單> | 載入文件表「<該列名稱>」 |
| 本階段 MUST | <抄自 README 對應階段「必要（MUST 採用）」> | README 第 <N> 階段 |
| 參考（暫不強制） | <抄自 README 對應階段「參考」> | README 第 <N> 階段 |
| 待確認 | <未能回答的項目，或「無」> | — |

### 本階段 PR 檢查清單

<逐條抄自 README「第 <N> 階段 PR 檢查清單」；階段 ≥ 2 連同前面階段的清單一起列>

### 專案 README「SDD 導入宣告」區塊（可直接貼上）

```markdown
## SDD 導入宣告

| 項目 | 值 |
|------|-----|
| 目前導入階段 | 第 <N> 階段（<階段名>） |
| 服務風險分級 | <分級>（階段一暫不分級時寫「未分級（階段一）」） |
| 應用類型 | <類型> |
| 憲章基線 | <repo> v<版本>@<sha 前 7 碼> |
```

### sdd-harness `sdd-adoption.json` 對應值

```json
{
  "baseline_repo": "<repo>",
  "baseline_version": "<constitution 版本>",
  "baseline_commit": "<40 字元 sha>",
  "adoption_phase": <N>,
  "app_type": "<api-service|microservice|tool-service|shell-script|frontend-web>",
  "risk_tier": "<critical|standard|internal|experimental>",
  "loaded_docs": ["constitution.md", "<延伸檔>"]
}
```

### 下一步

<AskUserQuestion 的結果：寫入 README／交給 sdd-harness（把本摘要貼進啟動 prompt）／只要摘要>
