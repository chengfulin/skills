# Commit 慣例（sdd-harness 各階段）

格式：Angular 慣例 `type(scope): 主旨`；主旨繁體中文、祈使語氣、不加句號。
scope 固定 `sdd`；story commit 在主旨尾附 `（NNN, USk）` 供追溯（§CP-1）。

## 階段 commit（auto-commit 事件 → 訊息）

由 `enable-autocommit.sh` 寫入 `git-config.yml`，`auto-commit.sh <event>` 觸發。
**本表是 `enable-autocommit.sh` 之 `message_for()` 的鏡像**：改訊息必須兩處同步
（先改腳本、再改本表），否則補救 commit 與 `git log -1` 驗證會比對失敗：

| 事件 | 訊息 |
|------|------|
| after_constitution | `docs(sdd): 制定專案憲章（constitution）` |
| after_specify | `docs(sdd): 建立功能規格（specify）` |
| after_clarify | `docs(sdd): 釐清規格（clarify）` |
| after_plan | `docs(sdd): 建立實作計畫（plan）` |
| after_tasks | `docs(sdd): 產生任務清單（tasks）` |
| after_analyze | `docs(sdd): 一致性分析修正（analyze）` |
| after_implement | `feat(sdd): 完成功能實作（implement）` |

## 手動 commit（無 hook 的 commit 點）

| 時機 | 模板 | 範例 |
|------|------|------|
| Setup / Foundational phase 完成 | `chore(sdd): 完成 <phase>（NNN）` | `chore(sdd): 完成 Setup（001）` |
| 並行規劃寫入狀態檔（implement-loop.md 步驟 1P）| `chore(sdd): 完成並行規劃（NNN）` | `chore(sdd): 完成並行規劃（001）` |
| User story 通過驗證與審查 | `feat(sdd): 實作 <story 標題>（NNN, USk）` | `feat(sdd): 實作檔案大小排序（001, US1）` |
| 驗證/審查後的修正（若單獨 commit）| `fix(sdd): 修正 <問題摘要>（NNN, USk）` | — |
| auto-commit 靜默跳過時的補救 | 沿用該事件在上表的訊息 | — |

## Commit 驗證程序（每階段收尾必跑）

```bash
bash .specify/extensions/git/scripts/bash/auto-commit.sh <事件名>   # 階段 commit
git status --porcelain        # 必須為空
git log -1 --format='%s'      # 訊息必須符合上表
```

**commit 之前**先確認該階段核心產物已寫入實際內容（spec.md / plan.md / tasks.md
非範本殘留）——auto-commit 只看「有無變更」，範本骨架也算變更，順序錯了會把
半成品 commit 進去（屆時需 `git reset --soft HEAD~1` 重做，能免則免）。

`auto-commit.sh` 在「事件未啟用」或「無變更」時會**靜默跳過（exit 0）**
（0.8.17 實測）——驗證不能只看退出碼。跑完上面三行後，照下表對號入座：

| 觀察到 | 判定 | 處置 |
|--------|------|------|
| porcelain **不為空** | script 跳過了，但有東西該 commit | `git add -A && git commit -m "<上表對應訊息>"`，重新驗證 |
| porcelain 為空，但 log -1 訊息**不是**本階段模板 | 本階段沒有任何變更被 commit——幾乎都是狀態檔漏更新（每階段收尾前必先更新狀態檔，所以恆有東西可 commit）| 先補狀態檔，重跑 auto-commit 與驗證 |
| porcelain 為空且 log -1 訊息相符 | 正常 | 進入下一階段 |

狀態檔更新時機的權威定義在 workflow-stages.md「狀態檔 schema」節。
specify 之後 spec.md 沒出現屬**流程錯誤**（回步驟 3 重跑），不是 commit 問題。

## 邊界

- 不使用 `--amend`、不 rebase、不 push（推送由使用者決定）。
- 不在 commit 訊息使用 emoji。
- **一個 commit 點恰好一個 commit**（階段 1 恰一個收尾 commit、階段 8 的
  逐 phase／story 多 commit 是既定設計，不算違反）；發現前一個 commit 點漏了，
  先補上再開始新階段（不要把不同 commit 點混進同一個 commit）。
