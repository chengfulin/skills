---
name: git-commit
description: 依團隊規範（Angular 格式、繁體中文）整理目前 repo 的變更並建立 git commit：檢查變更、必要時拆成多個 commit、撰寫 commit message。當使用者要求「commit」、「幫我提交」、「寫 commit message」或整理變更成 commit 時使用。
allowed-tools:
  - Read
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git add:*)
  - Bash(git commit:*)
model: sonnet
---

# Angular Commit Message Guidelines

These guidelines are based on the Angular commit message convention, which is widely used in open source projects. They help create a consistent, meaningful, and easy-to-read commit history that can also be analyzed for changelog generation.

## Workflow

1. Run `git status` and `git diff` / `git diff --staged` to inspect the changes, and `git log -n 10 --oneline` to see the existing message style.
2. If there are no changes, do not create a commit. Tell the user there is nothing to commit.
3. Decide what to commit:
   - If the staging area already has changes, the user staged them on purpose: commit only the staged changes and leave unstaged changes untouched.
   - If nothing is staged, group the changes yourself. If there are multiple unrelated changes, split them into separate commits with one message each. If multiple changes are related and form a single unit of work, keep them in one commit.
4. Stage each group by naming files explicitly (`git add <file>...`). Interactive staging (`git add -p`) is not available: if a single file contains unrelated changes, keep that file in one commit and mention it in the body, or ask the user how to split it.
5. Write the message following the rules below, and commit with a HEREDOC so multi-line messages are preserved:

   ```bash
   git commit -F - <<'EOF'
   feat: 新增匯出報表功能

   使用者需要離線檢視報表，新增 CSV 匯出按鈕。
   EOF
   ```

6. Run `git status` after committing to confirm the result, then report the created commit(s) to the user.

## Safety Rules

- Never use `git add -A` or `git add .`; always name the files.
- Never commit files that likely contain secrets (`.env`, credentials, private keys, tokens). Warn the user if such files are among the changes.
- Never use `--amend`, `--no-verify`, or `git push` unless the user explicitly asks.
- If a pre-commit hook fails, fix the reported problem, re-stage, and create a new commit (do not amend).

## Message Rules

1. Each message MUST follow the structure from [commit-message-structure.md](commit-message-structure.md) and use the commit types from [commit-types.md](commit-types.md).
2. Each message MUST be written in Traditional Chinese, with the following exceptions:
   - `<type>` MUST remain in English as defined in [commit-types.md](commit-types.md).
   - Footer keywords parsed by tools MUST remain in English: `BREAKING CHANGE:`, `DEPRECATED:`, `Fixes #`, `Closes #`, and trailers such as `Co-Authored-By:`. Only the description text after them is written in Traditional Chinese.
   - English technical terms (e.g. query, hotfix, test case) may be used where appropriate.
3. The message should describe only the changes included in that commit.

## Examples

Simple feature:

```
feat: 新增 tech-mentor skill
```

Bug fix with body explaining the motivation:

```
fix: 修正分頁查詢最後一頁重複顯示資料

原本 offset 以 (page) * size 計算，導致頁碼從 1 開始時跳過第一頁、
最後一頁重複。改為 (page - 1) * size，並補上邊界 test case。

Fixes #42
```

Breaking change:

```
refactor: 調整設定檔載入方式為環境變數

BREAKING CHANGE: 移除 config.json 讀取

設定改由環境變數提供，升級時請將 config.json 內容
轉為對應的環境變數（參考 .env.example）。
```

Revert:

```
revert: 還原 feat: 新增匯出報表功能

還原 commit 1a2b3c4，因匯出功能在大量資料時造成逾時，待改善後重新提交。
```
