# git-commit

## 目的

讓 Agent 將目前 repo 下產生的變更，進行整理，並依照統一的規則建立 commit message。規則演化自 Angular 的 [Commit Message Guideline](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md)。

## 檔案結構

| 檔案 | 說明 |
|---|---|
| `SKILL.md` | Skill 主規則：執行流程、安全規則、語言規範與範例 |
| `commit-message-structure.md` | Commit message 的 header / body / footer 格式 |
| `commit-types.md` | 可用的 commit type 清單與說明 |

## 語言規則

- `<type>`：使用英文（`feat`、`fix`、`docs` 等），來源為 `commit-types.md`
- `<short summary>`、body、footer 說明：使用繁體中文；開發相關英文技術詞彙（如 query、hotfix、test case）允許夾用
- footer 關鍵字（`BREAKING CHANGE:`、`DEPRECATED:`、`Fixes #`、`Closes #`）與 `Co-Authored-By:` 等 trailer 維持英文，供 changelog 工具與 GitHub 解析

## 安全規則

- 只允許 `git status`／`diff`／`log`／`add`／`commit` 指令
- 指名檔案 stage，不使用 `git add -A`／`git add .`；不 commit 機密檔
- 不 `--amend`、不 `--no-verify`、不 push（除非使用者明確要求）
- 使用者已 stage 的內容視為刻意選擇，只 commit 該部分

## 優化方向

此 skill 規則單純，日後依各專案需求調整語言設定或新增 type 即可。
