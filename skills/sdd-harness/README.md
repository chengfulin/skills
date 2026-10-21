# sdd-harness

以 [GitHub spec-kit](https://github.com/github/spec-kit) 執行 **Spec-Driven Development（SDD）**
全流程的 orchestrator skill：根據需求進行 AI Coding，全程遵循專案憲章（預設由同 repo 的
`sdd-baseline` skill 提供團隊基線，也可用使用者自訂的憲章），並以六個獨立 subagent 進行
規格釐清、功能導覽簡報、影響範圍分析、程式實作、功能驗證與 code review，每個階段完成即 commit。

## 架構

```
使用者需求
   │
   ▼
sdd-harness（orchestrator skill）
   │  0  前置檢查（specify / git / agents / 憲章來源 / 上游新版只詢問）
   │  0b 續跑偵測（可從任一中斷點繼續）
   │  1  specify init + git extension + 啟用 auto-commit
   │  2  /speckit.constitution ─ 以憲章來源組裝專案憲章 ─────── commit
   │  3  /speckit.specify ─ 詢問需求、建立規格
   │        → [sdd-brief-writer] 導覽簡報 → 使用者 review ──── commit
   │  4  /speckit.clarify ─ [sdd-spec-clarifier] 憲章衝突檢核
   │        → spec 更新 → 簡報更新 → 使用者 review ─────────── commit
   │  5  /speckit.plan ─ 詢問技術選型（參考 tech-standards）
   │        → plan → 簡報加架構圖 → 使用者 review ──────────── commit
   │  6  /speckit.tasks ──────────────────────────────────── commit
   │  7  /speckit.analyze ─ [sdd-spec-clarifier] 一致性檢核
   │        → 簡報列發現表 → 使用者同意修正 ───────────────── commit（恆有：至少狀態檔）
   │  8  /speckit.implement ─ codegraph 建索引；Foundational 後並行派
   │        [sdd-impact-analyzer]（plan 模式）產出 story 並行分組建議 ── commit
   │        之後逐 user story：
   │        [sdd-impact-analyzer] 影響邊界 → [sdd-implementer] 實作（限定邊界）→
   │        [sdd-feature-validator] 驗收 → [sdd-code-reviewer] 審查（含漣漪檢查）
   │        → 通過才 commit → codegraph sync
   │  8R 重規劃（條件性）：實作中發現規劃不可行 → 修訂 spec → 重跑 4–7（roll forward）
   ▼
符合憲章、可追溯、已驗證的程式碼
```

## 前置需求

| 工具 | 說明 |
|------|------|
| [specify CLI](https://github.com/github/spec-kit)（spec-kit）| `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`（裝最新 stable）|
| git | 版本控制 |
| Claude Code | 執行本 skill；人為 review 閘門用 Artifact 工具發布導覽簡報（不可用時退回檔案路徑）|
| `sdd-baseline` skill（同 repo）| **預設憲章來源**：其 `references/baseline/` 副本會被複製到目標專案。改用自訂憲章時不需要 |
| [codegraph](https://github.com/colbymchenry/codegraph)（**選配**）| 實作階段的影響範圍分析與漣漪檢查；未安裝時自動降級為 grep 分析 |

### 相依工具版本

安裝目標一律**最新 stable**，不釘版本。本 skill 對 spec-kit 與 codegraph 的行為結論
全是實測結果，**最後驗證版本**：spec-kit **1.0.13**、codegraph **1.6.1**。
步驟 0 偵測到安裝版高於最後驗證版時只警告、由使用者決定是否繼續；各處「X.Y.Z 實測」
註記是證據時間戳，不是安裝限制。重新驗證通過後才更新此處數字。

## 安裝

```bash
bash skills/sdd-harness/scripts/install.sh
```

冪等安裝：把 `skills/sdd-harness` symlink 到 `~/.claude/skills/`、`agents/*.md` 逐檔 symlink 到
`~/.claude/agents/`（Claude Code 只從該處載入 subagent）；同 repo 的 `sdd-baseline` 尚未安裝時
一併連上。重複執行安全；repo 移動位置後重跑即可修復連結。

## 使用方式

1. 在**目標專案目錄**（新建空目錄或既有專案）開啟 Claude Code。
2. 輸入 `/sdd-harness <需求描述>`，或直接說「用 SDD 開發 ○○○」。
   - 要用自訂憲章：在同一句 prompt 給檔案／目錄路徑或貼上內容，例如
     `/sdd-harness 用 ./docs/constitution.md 作為憲章，開發 ○○○`。
   - 已先用 `/sdd-baseline decide` 定案的話，把決策摘要一起貼上，步驟 2 直接採用。
3. 依提示回答：導入階段、應用類型、（階段二起）風險分級、實作需求、技術選型。
4. 流程中斷後，在同一目錄輸入 `/sdd-harness resume` 即可從偵測到的階段續跑。

環境變數：`SDD_BASELINE_DIR` 覆寫憲章來源目錄（預設 `sdd-baseline` skill 的 `references/baseline/`）。

## 組成

```
sdd-harness/
├── SKILL.md                       # orchestrator：10 步 SDD 狀態機
├── agents/                        # 六個 subagent（以 scripts/install.sh 連到 ~/.claude/agents/）
│   ├── sdd-spec-clarifier.md      # 規格/計畫 對憲章的對抗式審查（唯讀）
│   ├── sdd-brief-writer.md        # 人為 review 閘門的功能導覽簡報（HTML；只寫 feature 的 brief/）
│   ├── sdd-impact-analyzer.md     # story 開工前的影響邊界分析＋並行規劃集合（唯讀，codegraph）
│   ├── sdd-implementer.md         # implement 階段的獨立 context 實作（寫碼與測試，不 commit）
│   ├── sdd-feature-validator.md   # user story 驗收條件驗證（可執行測試與操作，不改原始碼）
│   └── sdd-code-reviewer.md       # 憲章合規 + 品質 + 漣漪效應 code review（唯讀）
├── references/
│   ├── workflow-stages.md         # 各階段完成準則、狀態檔 schema、續跑演算法、錯誤處理細則
│   ├── constitution-assembly.md   # 憲章組裝規則（憲章來源、導入階段裁剪、載入文件表）
│   ├── commit-conventions.md      # 各階段 commit 訊息模板
│   ├── model-dispatch.md          # 模型調度守則（model/effort、升降級、回報合約）
│   ├── judgment-rubrics.md        # 判斷準則（升級/完成/問人/換路，附正反例）
│   ├── delegation-templates.md    # 派工 prompt 模板（搜尋/實作/重構/研究/審查/升級交接）
│   ├── implement-loop.md          # 步驟 8 實作迴圈全文（索引準備、逐 phase 閘門、越界放行、story 收尾 checklist）
│   ├── replan.md                  # 重規劃閘門（實作中發現規劃不可行時的 roll-forward 程序）
│   ├── review-gate.md             # 人為 review 閘門：導覽簡報的產製／發布／提問程序與觸發點表
│   └── brief-storyboard-kit.html  # 導覽簡報的故事板套件（色票、symbol 圖庫、概念圖／流程圖格子骨架）
└── scripts/
    ├── install.sh                 # 冪等安裝（symlink skill、agents、sdd-baseline 到 ~/.claude/）
    ├── copy-baseline.sh           # 把憲章來源（sdd-baseline 副本或自訂憲章）複製到目標專案並確保 manifest
    ├── detect-stage.sh            # 續跑階段偵測（state file + 檔案系統啟發法）
    └── enable-autocommit.sh       # 啟用 spec-kit git extension 的階段 auto-commit
```

## 設計要點

- **憲章來源可替換**：預設複製 `sdd-baseline` skill 的基線副本到目標專案
  `.specify/memory/baseline/`（含 `manifest.json` 供追溯與漂移比對），依導入階段與應用類型
  策展式組裝成自足的 constitution.md；使用者在 prompt 指定自訂憲章時改用其內容
  （manifest 的 `repo` 記為 `custom`）。既有專案只唯讀比對漂移，經使用者同意才重抓。
- **每階段一個 commit**：spec-kit git extension 的 auto-commit 出廠全部停用，且 optional hooks
  不會自動執行；本 skill 以 `enable-autocommit.sh` 逐項啟用 `after_*` 事件，
  orchestrator 在每階段收尾主動執行並驗證，缺漏時手動補 commit。
- **實作階段逐 story 把關**：每個 user story 開工前由 `sdd-impact-analyzer` 產出影響邊界報告；
  實作由 `sdd-implementer` 在獨立 context 執行，只回報完成的任務 ID，tasks.md 勾選由主對話
  單一寫入；完成後先由
  `sdd-feature-validator` 逐條驗收、再由 `sdd-code-reviewer` 審查憲章合規與漣漪效應，
  全數通過才 commit 繼續。
- **並行規劃（觀察期）**：Foundational 完成後一次並行分析所有未完成 story 的寫入／讀取集合、
  共用資源與契約變更，判定 story 間衝突並產出分組建議寫入狀態檔；執行仍逐 story 依序，
  完成報告附「規劃誤判」統計，作為日後是否導入 worktree 並行實作的依據。
- **人為 review 閘門用導覽簡報，不用長文**：spec／clarify／plan／analyze 四個閘門由
  `sdd-brief-writer` 產製 `specs/<NNN>/brief/feature-brief.html`，orchestrator 以 Artifact 發布並把
  判斷點直接作為 AskUserQuestion 的題目。簡報是入版控的中間產物，spec.md 仍是唯一權威。
- **重規劃閘門（roll forward）**：實作中發現規劃不可行時不回滾已完成的 story——修訂 spec 後
  重跑釐清→計畫→任務→分析，以**新增** task 修正既有內容，git 歷史保持 append-only。
- **codegraph 影響分析（選配）**：進入實作階段時建立/同步索引（並確保 `.codegraph/` 被
  gitignore），每個 story commit 後 `codegraph sync`；未安裝時整條路徑降級為 grep。
- **可續跑**：狀態記錄於 `.specify/memory/sdd-adoption.json` 與 `specs/<NNN>/.sdd-workflow.json`，
  搭配檔案系統啟發法交叉驗證。

## 硬約束（維護本 skill 時逐條核對）

- `enable-autocommit.sh` 改寫的 `git-config.yml` 會被 spec-kit 的 `auto-commit.sh`
  **逐行 shell 解析**：事件鍵 2 空格縮排、`enabled:`/`message:` 4 空格縮排，格式不可破壞。
- `commit-conventions.md` 的事件訊息表與 `enable-autocommit.sh` 的 `message_for()` 是**鏡像**：
  改其一必同步另一。
- 目標專案 CLAUDE.md 的 `<!-- SPECKIT START/END -->` 標記區**只能讀不能寫**。
- `agents/*.md` 的 `name` 與檔名必須一致（orchestrator 以此名派遣）；審查者
  （clarifier／reviewer）與 brief-writer 固定 `model: sonnet` + `effort: high`，執行者
  （validator／impact-analyzer／implementer）`model: inherit`（理由見 model-dispatch.md §3）。
- `codegraph init` **不會**自動 gitignore：階段 8 須自行確保 `.gitignore` 含 `.codegraph/`。
- 步驟 0 的上游版本檢查**只詢問、不代升級**：不得執行 `specify self upgrade`／
  `codegraph upgrade`／`uv tool install --force`。
- 憲章內容不寫死在本 skill 內：一律在執行時從憲章來源複製；規則一條只寫一處，其餘引用。
- 腳本：bash、`set -euo pipefail`（detect-stage 除外，刻意 `-uo`）、macOS bash 3.2 相容
  （無關聯陣列、無 mapfile）；設定用環境變數覆寫，不硬編碼。

## 驗證程序

1. **腳本單測**：`detect-stage.sh` 對合成情境（空目錄→init、`.specify` 存在但 extension 未裝→init、
   單行 HTML 註解＋placeholder→constitution、README 宣告缺→constitution、完整→specify）輸出正確階段；
   `enable-autocommit.sh` 對 git-config.yml 副本驗證逐項 enabled、縮排不變、冪等；
   `copy-baseline.sh` 對目錄來源（含／不含 manifest）與單檔來源各跑一次，檢查 manifest 與原子替換。
   用 bash 執行，勿用 zsh。
2. **E2E**（動到 SKILL.md 流程主幹或 scripts 行為時必跑）：拋棄式目錄以極小需求走完 10 步，
   檢核每個 commit 點恰好一個 commit 且 working tree 乾淨、constitution.md 無殘留 placeholder、
   README 有「SDD 導入宣告」、每個 story commit 前有 impact→validator→reviewer 紀錄。
3. **續跑**：中斷後 `resume` 正確偵測階段且不重做已完成階段；implement 中斷的 dirty tree
   （產品程式碼）不得被補 commit，須回 story 閘門。
