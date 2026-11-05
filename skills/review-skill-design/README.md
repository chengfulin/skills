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

## 模型

frontmatter 指定 `model: opus`；若執行環境有 fable，也建議改用 fable 執行，檢核品質更好。

## 產出

一份建議清單，不會動到被檢核的 skill／agent 檔案；修改與否由使用者 review 後決定。
