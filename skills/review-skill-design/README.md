# review-skill-design

檢核指定的 skills 與 agents 是否過度設計：會不會浪費 context、產生不必要的 tool_use 輪數，以及 opus 等級的模型是否足以理解執行並取得預期結果。只提供建議供 review，不修改任何檔案。

## 使用方式

```
/review-skill-design <要檢核的 skill／agent 名稱或路徑，以空白分隔>
```

範例：

```
/review-skill-design sdd-harness sdd-implementer sdd-code-reviewer
/review-skill-design skills/make-mockup-harness
```

名稱依序在指定路徑、`~/.claude/skills/<名稱>/`、`~/.claude/agents/<名稱>.md`、目前 repo 的 `skills/<名稱>/` 尋找。skill 目錄連同它的 `agents/`、`references/` 視為一個檢核對象。

## 流程與角色

| 角色 | 誰 | 做什麼 |
| --- | --- | --- |
| 主對話 | 使用者所選模型（frontmatter 預設 opus） | 解析目標、派工、彙整報告；不自己審、不改檔 |
| reviewer | `general-purpose` subagent，`opus`，每個對象一個，平行 | 讀完對象全部檔案，量化行數／載入檔數／tool_use 輪數，寫 read-back（opus 能否理解的一手證據），列出附 檔案:行號 的發現與最小改法 |
| judge | `general-purpose` subagent，`opus`，每個對象一個，平行 | 只拿 reviewer 報告與對象路徑，自己重讀檔案逐條裁決成立與否、改法是否最小，補最多 3 條漏報 |

最終報告只列 judge 確認的建議；reviewer 與 judge 不一致的條目另列給使用者裁決。

## 模型

frontmatter 指定 `model: opus`；若執行環境有 fable，也建議改用 fable 當主對話執行。subagent 固定 opus。

## 產出

一份建議清單，不會動到被檢核的 skill／agent 檔案；修改與否由使用者 review 後決定。
