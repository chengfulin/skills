# SDD 流程狀態機：各階段完成準則與續跑偵測

本文件定義 sdd-harness 的 10 步狀態機。每個階段都有**進入條件**、**完成準則**與
**commit 點**；orchestrator 必須在完成準則全數滿足後才進入下一階段。

## 階段總表

流程總覽表以 **SKILL.md「流程總覽」為唯一版本**，此處不重複（重複表是改一漏一
的來源）。本文件只負責：各階段完成準則、狀態檔 schema、續跑演算法。
補充事實：階段 1 恰一個 commit 點（收尾 chore commit；0.12.14 起 `specify init`
不再自動 git init／不再自帶 init commit，改由步驟 1 顯式 `git init`，見該步驟）；
階段 7 的 `after_analyze` 恆有 commit（至少狀態檔更新）；階段 8 為並行規劃
commit + 逐 phase／story（依序模式）或逐波次（並行模式）多 commit + 最後
`after_implement`。

## 各階段完成準則

### 0 前置檢查（每次啟動都重跑）

指令區塊以 SKILL.md 步驟 0 為準；以下判讀規則以**本節為唯一版本**
（SKILL.md 只留要點指引）。逐行看 `check_*` 輸出：

- `check_specify`：須成功。版本高於本 skill 的最後驗證版（README.md「相依工具
  版本」）→ 警告「harness 行為結論尚未於此版驗證（skill 安裝形式、git-config.yml
  解析、init 是否 git init 皆可能改變）」，AskUserQuestion 由使用者決定是否繼續。
- `check_git`：須成功。
- `check_baseline`（`$SDD_BASELINE_DIR`，預設 sdd-baseline skill 的
  `references/baseline/`，須含 `constitution.md` 與 `manifest.json`）`absent`
  **不立即中止**：先跑步驟 0b。偵測結果為 init／constitution，或使用者要開新
  feature（需比對基線更新）→ 依「錯誤處理細則」的憲章來源決策樹處置；其他階段
  → 警告「本次無法檢查基線漂移」後繼續（這些階段用的是已入版控的本地副本）。
- `check_agents`：agent 檔皆須 `[ -f ]` 通過（會跟隨 symlink）；缺檔或 symlink
  失效 → 執行 `bash $SKILL_DIR/scripts/install.sh`（定義檔在 `$SKILL_DIR/agents/`，
  腳本把它們逐檔連到 `~/.claude/agents/`）。
- `check_codegraph=absent` **不算失敗**（選配）：記下「codegraph 不可用」，
  實作階段影響分析走 grep 降級（references/implement-loop.md）。可用時，版本 ≠ 最後驗證版
  → 提醒使用者「init 的 gitignore 行為與查詢子指令需重驗」（同上，§5）。
- `check_specify_latest`／`check_codegraph_latest`（上游最新 stable 檢查，兩者
  皆唯讀指令）：
  - `UPDATE` → 上游有新版。AskUserQuestion 三選一：「我自行升級後重跑步驟 0」
    （回覆升級指令 `specify self upgrade`／`codegraph upgrade`，由使用者執行）／
    「不升級，本次以現版繼續」／「中止」。harness **絕不代執行升級**（含
    `uv tool install --force`），這是本 skill 的硬約束（README.md）。使用者升級後重跑步驟 0，
    新版 ≠ 最後驗證版會觸發上面的重驗警告，不重複問升級。
  - `current` → 無動作。`unknown`（離線、GitHub API 失敗、舊版無此子指令）→
    警告「本次無法檢查上游新版」後繼續，不算失敗。`absent` 同 `check_codegraph`。
- 其餘任何 `check_*=FAIL`：**中止**並輸出修復指引（specify：`uv tool install
  specify-cli --from git+https://github.com/github/spec-kit.git`），不要帶病前進。

### 1 初始化
完成準則（全部滿足）：
- `.specify/` 與 `.claude/skills/speckit-constitution/SKILL.md` 存在。
- `.specify/extensions/.registry` 含 `"git"`。
- `git-config.yml` 的 7 個 `after_*` 事件 `enabled: true`（跑 `enable-autocommit.sh` 後驗證）。
- `git rev-parse --is-inside-work-tree` 成功且至少一個 commit（0.12.14 實測：
  `specify init` 本身**不會**自動 git init——步驟 1 顯式執行 `git init`
  建 repo，該 repo 尚無 commit，commit 由本節下一條的收尾動作產生；步驟 2
  的 `speckit.git.initialize` mandatory hook 屆時偵測到 repo 已存在會自動
  跳過，不會補一個額外的 "Initial commit from Specify template"）。
- **working tree 乾淨**：init 與 extension 設定的殘留變更已以
  `chore(sdd): 初始化 spec-kit 專案` commit（不得讓 init 產物混入憲章 commit）。

### 2 憲章
完成準則：
- `.specify/memory/constitution.md` 無殘留 placeholder：剔除 HTML 註解後無
  `\[[A-Z][A-Z0-9_ ]{2,}\]` 樣式 token——**含數字型**如 `[PRINCIPLE_2_NAME]`、
  `[SECTION_3_CONTENT]`（0.8.17 範本實測：20 個 token 中 14 個含數字；1.0.5／1.0.13 範本經 resolve-template.sh 解析後仍為同 20 個）。
- `.specify/memory/baseline/` 含基線原始副本 + `manifest.json`。
- `.specify/memory/sdd-adoption.json` 存在（schema 見下）。
- 專案 README.md 含「SDD 導入宣告」章節。
- 上述變更已 commit（working tree 乾淨）。

### 3 規格
- `.specify/feature.json` 的 `feature_directory` 指向的目錄含 `spec.md`
  （該檔自 spec-kit 1.0.5 起被 `.specify/.gitignore` 忽略，屬 per-checkout
  狀態、不入版控；缺席時的回退與重建見「續跑演算法」規則 2）。
- feature branch 已建立（`git branch --show-current` 為 `NNN-slug` 格式；由
  before_specify 的 `speckit.git.feature`（mandatory hook）建立）。
- spec.md 經使用者 review 確認（SKILL.md 通用規則 7；閘門在 commit 之前，
  commit 即為已 review 的證據，不另設狀態旗標）。
- `.specify/context/` 存在時：spec 引用的每個來源版本目錄含 `index.md`；spec 的
  User Story／FR／驗收情境帶來源錨點（SKILL.md 步驟 3 第 2 點）。
- `<feature 目錄>/brief/feature-brief.html` 與 `brief/README.md` 已建立
  （review-gate.md 觸發點 `spec`）並隨本階段 commit；簡報產製失敗而改用文字
  摘要完成閘門時例外，須已向使用者告知。
- `.sdd-workflow.json` 已建立且 `steps.specify.done=true`；已 commit。

### 4 釐清
- sdd-spec-clarifier 已執行且其 CRITICAL 發現全數處理（修正或使用者明確接受）。
- spec.md 含 `## Clarifications` 章節（即使無問題也要求 speckit-clarify 記錄
  「本輪無需釐清」，讓檔案系統留下痕跡）。
- 依答案更新後的 spec 經使用者 review 確認（SKILL.md 通用規則 7）；
  `brief/feature-brief.html` 已依本輪更新（觸發點 `clarify`）並隨本階段 commit
  （失敗例外同階段 3）。
- `steps.clarify.done=true`；已 commit。
- **續跑偵測以狀態旗標為權威**：釐清可能中斷在「章節已寫入但 CRITICAL 未處理」，
  `## Clarifications` 標記只作證據行，不作完成依據。

### 5 計畫
- `FEATURE_DIR/plan.md` 存在；技術選型經使用者確認（tech-standards.md 為預設建議）。
- plan.md 內容經使用者 review 確認（SKILL.md 通用規則 7）；
  `brief/feature-brief.html` 已依本輪更新並含架構圖（觸發點 `plan`）並隨本階段
  commit（失敗例外同階段 3）。
- `steps.plan.done=true`；已 commit。

### 6 任務
- `FEATURE_DIR/tasks.md` 存在，且任務依 user story 分 phase（Setup → Foundational →
  US1..USn → Polish），每個 story phase 有 Checkpoint。
- `steps.tasks.done=true`；已 commit。

### 7 一致性分析
- speckit-analyze 報告已輸出；sdd-spec-clarifier（full 範圍）已執行。
- CRITICAL 發現全數處理；修正經使用者同意後套用（同意透過通用規則 7 閘門，
  觸發點 `analyze`；`brief/feature-brief.html` 的「本輪變更」＝發現表，隨本階段
  commit，失敗例外同階段 3）。
- `steps.analyze.done=true`（**必須寫入**——續跑只認得狀態檔；簡報更新不作
  完成依據）。
- 有修改→commit；無修改→只 commit 狀態檔更新（狀態檔本身就是修改）。

### 8 實作（依序模式逐 story／並行模式逐波次）
執行細節（索引準備、模式判定、逐 phase 迴圈、波次迴圈、閘門順序、越界放行、收尾
checklist）**只寫在 references/implement-loop.md**（SKILL.md 步驟 8 只留摘要），此處不重複。此處只記完成準則與不變量：

- 影響邊界報告不寫檔、不入狀態檔——中斷後續跑時**重做**（唯讀、冪等）。
- tasks.md 的 `[X]` 只由主對話依 implementer 回報勾選（單一寫入者）；
  implementer 改動 tasks.md 即越界。
- 未勾選 task ≥2 時，Setup 開工前須有並行規劃 commit、`<FEATURE_DIR>/parallel-plan.json`
  與 `steps.implement.parallel_plan`（task 粒度、全域）；其 `mode` 決定執行方式：
  `parallel`＝依波次執行，`sequential`（或沒有規劃）＝依 tasks.md 逐 phase。
- 並行模式：同一時間至多一個進行中的波次（`current_wave`）；波次內各 unit 只在
  自己的 worktree 寫入，合併回專案根後才勾選、過閘門；一個波次恰一個 commit，
  commit 前 `current_wave` 已移除、worktree 與 `sdd-wave/<NNN>-*` 分支在 commit 後
  清除。story 旗標在完成該 story 的波次 commit **之前**更新。
- 狀態檔 story 旗標：`steps.implement.stories.USk = {validated, reviewed, committed}`，
  在該 story 的 commit **之前**更新。
- 修正迴圈上限 3 輪（含 reviewer 修正後的 validator 回歸，與 Polish 階段
  validator FAIL 修正後的 reviewer 覆審），超過即停，問使用者。

完成準則：tasks.md 無 `[ ]`、每個 story 在狀態檔有 validated+reviewed+committed、
Setup／Foundational／Polish 的 commit（並行模式：每個波次 commit）均經
sdd-code-reviewer APPROVE、
Polish 收尾經 validator 全 feature 回歸（story＝`all`）PASS、
`steps.implement.done=true`、working tree 乾淨、（啟用 codegraph 時）
`.codegraph/` 已被 gitignore 且未入版控、（並行模式）沒有殘留的 worktree 與
`sdd-wave/<NNN>-*` 分支。

### 8R 重規劃（replan，條件性——實作中發現規劃不可行時）

入口訊號寫在 SKILL.md 步驟 8R、執行程序寫在 references/replan.md，此處只記
完成準則與不變量：

- **roll forward**（原則的唯一版本在 SKILL.md 步驟 8R）：狀態面不變量＝
  已完成 story 的 `stories.USk` 旗標不回退。
- 重規劃期間 `steps.clarify.done`／`steps.analyze.done` 維持 true——「重跑中」
  由 `replan.resume_at` 表達（schema 見下），**不視為狀態不一致**（本文件
  續跑演算法規則 5 的 (a)(b) 不適用於此情形）。
- **加法不變量**：tasks.md 重生後，已完成的 `[X]` 零消失、既有 story ID
  未重編號。
- 每輪重規劃恰有 4 個 commit 點：`after_clarify`（含 spec 修訂與 replan 欄位
  首寫）→ `after_plan` → `after_tasks` → `after_analyze`（收尾，`active` 轉
  false 隨此 commit）。

完成準則：`replan.active=false`（`iteration`／`reason` 保留）、上述 4 個
commit 存在且 working tree 乾淨、tasks.md 滿足加法不變量、已回到步驟 8
story 迴圈。

## 狀態檔 schema

### `.specify/memory/sdd-adoption.json`（專案級，憲章階段建立）
```json
{
  "baseline_repo": "chengfulin/sdd-baseline",
  "baseline_version": "5.3.0",
  "baseline_commit": "<40 字元 sha>",
  "adoption_phase": 1,
  "app_type": "shell-script",
  "risk_tier": null,
  "loaded_docs": ["constitution.md", "constitution-shell.md"],
  "adopted_at": "2026-07-05T00:00:00Z"
}
```
- `baseline_repo`／`baseline_version`／`baseline_commit` 抄自 `.specify/memory/baseline/manifest.json`
  的 `repo`／`constitution_version`／`head_commit`（自訂憲章：`repo` 為 `custom`、
  `head_commit` 為 null、版本可為 null）。
- `app_type` 取值：`api-service` / `microservice` / `tool-service` / `shell-script` / `frontend-web`。
- `risk_tier`：`critical` / `standard` / `internal` / `experimental`；導入階段 1 可為 null。

### `specs/<NNN>-<slug>/.sdd-workflow.json`（每 feature，規格階段建立）
```json
{
  "feature": "001-example",
  "steps": {
    "specify":  {"done": true},
    "clarify":  {"done": true, "clarifier_findings": 2},
    "plan":     {"done": true},
    "tasks":    {"done": true},
    "analyze":  {"done": false, "findings": null, "remediated": null},
    "implement": {
      "done": false,
      "stories": {
        "US1": {"validated": true, "reviewed": true, "committed": true},
        "US2": {"validated": false, "reviewed": false, "committed": false}
      },
      "parallel_plan": {
        "mode": "parallel",
        "mode_reason": "波次估計加速 2.4x，分析基礎 codegraph",
        "granularity": "task",
        "basis": "codegraph",
        "tasks": 48,
        "conflict_pairs": 211,
        "pairs": 1128,
        "by_type": {"寫入": 40, "相依": 120, "資源": 6, "宣告": 15, "未定": 30},
        "batches": 17,
        "max_width": 9,
        "phases": 7,
        "waves": 6,
        "est_speedup": 2.4,
        "low_conf": ["T031"],
        "plan_file": "specs/001-xxx/parallel-plan.json"
      },
      "waves_done": 2,
      "current_wave": {
        "k": 3,
        "units": {
          "u1": {"phase": "US1", "tasks": ["T014", "T015"], "W": ["src/a.ts", "test/a.spec.ts"]},
          "u2": {"phase": "US2", "tasks": ["T021"], "W": ["src/b.ts"]}
        },
        "completes": ["US2"]
      }
    }
  },
  "replan": {
    "active": false,
    "iteration": 1,
    "resume_at": null,
    "reason": "US2 依賴的外部 API 不支援批次查詢"
  },
  "brief": {
    "artifact_url": "https://claude.ai/artifact/<id>"
  }
}
```
**更新時機**：在執行該階段/story 的 commit **之前**更新旗標，讓狀態檔隨同一個
commit 入版控（收尾必須 working tree 乾淨，不允許 commit 後再補寫狀態檔）。
不記 commit sha——需要時以 `git log --grep '（NNN, USk）'` 或階段訊息回溯。

`parallel_plan` 欄位（implement-loop.md 步驟 0P 由 `scripts/task-plan.py build`
寫入，主對話只在使用者指定或降級時改 `mode`／`mode_reason`；未勾選 task 少於 2 個
時不建立）：`mode` 取 `parallel`／`sequential`，`mode_reason` 一句話原因；
`granularity` 恆為 `task`；`basis` 取 `codegraph`／`grep`／`greenfield`（各
analyzer 中最弱者）；`tasks`／`pairs`／`conflict_pairs` 為規劃涵蓋的 task 數、
pair 數與衝突 pair 數；`by_type` 的鍵取 `寫入`／`相依`／`資源`／`契約`／`宣告`／
`未定`；`batches`＝批次數（同批＝判定可同時開工）、`max_width`＝最寬批次的 task
數；`phases`＝phase 數（依序模式的輪數）、`waves`＝波次模擬的波次數、
`est_speedup`＝估計加速（task 數 ÷ 各波次最長 lane 的 task 數總和）；`low_conf`＝
信心低、與其他所有 task 記為衝突的 task；`plan_file` 指向完整規劃（執行順序、
逐 task 集合、衝突清單、批次表、關鍵路徑、熱點檔），隨規劃 commit 入版控。
重規劃回到步驟 8 前刪除此欄位與 `plan_file`（任務已變，規劃失效）。

`waves_done`／`current_wave`（僅並行模式）：`task-plan.py next` 排出波次時寫入
`current_wave`（`k` 波次序號、`units` 各 unit 的 phase／任務／寫入集合、`completes`
本波次完成的 phase），`task-plan.py close` 在波次 commit 前移除它並把 `waves_done`
加 1——所以**已 commit 的狀態檔不會有 `current_wave`**，出現在 dirty 狀態檔裡＝
該波次進行中。

`brief` 欄位（選填）：導覽簡報首次以 Artifact 工具發布成功時寫入 `artifact_url`，
供跨 session 續跑時更新同一頁（程序見 references/review-gate.md）；Artifact
工具不可用或發布失敗時不建立此欄位，簡報只以檔案形式存在。detect-stage.sh
不讀此欄位。

`replan` 欄位（見「8R 重規劃」節與 references/replan.md）僅在**首次進入**
重規劃閘門時建立，多數 feature 沒有它：`resume_at` 取值 `spec`／`clarify`／
`plan`／`tasks`／`analyze`（`active=false` 時為 null）；`iteration` 逐輪累計
不歸零；`reason` 記最近一輪的一句話緣由。

## 續跑（resume）演算法

1. 跑 `detect-stage.sh`（腳本位於本 skill 目錄 `scripts/`），讀取全部證據行。
2. **feature.json 重建**：證據行 `feature_json=missing`（fresh clone／另一台
   機器續跑，1.0.5 起該檔被 gitignore）或 `stale`（存在但指向無 spec.md 的
   目錄）→ 依 `feature_dir=` 寫回 `.specify/feature.json`
   （`{"feature_directory":"<feature_dir>"}`），再向使用者回報
   `feature_source=`（`branch`＝分支名對應、`specs-scan`＝取 specs/ 編號最大者）
   請其確認是同一個 feature。該檔被 ignore 時不會出現在 dirty tree；未被 ignore
   的舊版專案若重寫後產生 diff，隨下一個階段 commit 入版控。speckit 各腳本
   沒有這個檔會直接失敗，所以必須在任何 speckit 步驟之前重建。
3. **replan 最優先**：證據行 `replan_active=true`（此時 `detected_stage=replan`）
   → `replan_resume_at` 為權威——dirty 的 spec.md／plan.md／tasks.md／
   `.sdd-workflow.json` 屬重規劃進行中產物，**跳過下一條的分類表**，依
   references/replan.md 從該站續作；dirty 產品碼（進入重規劃時理應已清場）→
   不補 commit，列清單問使用者；`replan_resume_at=invalid` → 狀態檔損毀，
   列出現值請使用者裁決修復。
4. **dirty tree 優先處理**（`dirty_files > 0` 時，按變更檔案路徑分類）：

   | 變更檔案 | 歸屬 | 處置 |
   |----------|------|------|
   | constitution.md／baseline/／sdd-adoption.json／README 的「SDD 導入宣告」章節 | constitution | 提示使用者後補該階段 commit |
   | README 的其他章節 | 視內容 | 對得到當前 feature tasks.md 的任務 ID → 併入「產品程式碼」列處理（回 story 閘門）；對不到 → 併入「不明」列問使用者 |
   | spec.md（新增）、`.specify/context/<slug>/v<N>/index.md`（新增） | specify | 同上 |
   | spec.md（修改，含 Clarifications） | clarify | 同上 |
   | plan.md 與 research／data-model 等設計檔 | plan | 同上 |
   | tasks.md | tasks | 同上 |
   | `specs/<NNN>/brief/`（feature-brief.html／README.md） | 隨同批 dirty 的 spec／plan／tasks 歸屬 | 與同批檔案一起處置；**單獨** dirty（簡報已產、階段 commit 未做）→ 不單獨補 commit，回該階段的通用規則 7 閘門重走（簡報可重生；「該階段」＝`detected_stage`，因狀態旗標在閘門通過前不會寫入） |
   | `specs/<NNN>/parallel-plan.json`（可能連同 `.sdd-workflow.json`） | implement 0P 中斷於 commit 前 | 規劃可重生：刪除該檔、還原狀態檔的 `parallel_plan`，回 implement-loop.md 步驟 0P 重做 |
   | `.sdd-workflow.json` 含 `current_wave`（可能連同產品程式碼、tasks.md 勾選） | implement 並行模式波次中斷 | **不補 commit**。`wave-worktree.sh status <專案根> <NNN>` 看各 unit 的 worktree 與變更檔：專案根沒有產品程式碼變更 → 從 implement-loop.md W2 續作（已有變更的 worktree 重派續作，沒有 worktree 的 unit 重新 add）；專案根已有合併後的變更 → 從 W4 起重走（各 unit 的 `files=` 取自 status）。worktree 已不存在而專案根有變更 → 無法逐 unit 歸屬，列檔案清單問使用者（丟棄重做該波次，或整批視為單一 unit 過閘門） |
   | 產品程式碼／測試碼 | implement 中斷 | **不補 commit**——半成品未過閘門。找出所屬 story，回到 story 閘門重走（影響邊界 → 續作 → 越界檢查 → validator → reviewer），全數通過才依正常程序 commit |
   | `.gitignore` 的 `.codegraph/` 行／`.codegraph/` 目錄 | implement 前置 | 依 implement-loop.md 索引準備規則：`.gitignore` 變更不單獨補 commit、隨下一個 commit 入版控；`.codegraph/` 目錄確認已被 ignore（未 ignore 就補行），不得入版控 |
   | 橫跨多階段或對不進表 | 不明 | 不自行 commit；列出檔案清單，AskUserQuestion 請使用者指定歸屬（可分多次 commit） |

   處理完成後重新偵測。
5. 狀態檔與檔案系統不一致時，依**方向**裁決（兩條規則不可互換）：
   - (a) 狀態檔宣稱 done 但對應產物**缺失**（如 `steps.plan.done=true` 而 plan.md
     不存在）→ 以檔案系統為準：回到該階段，旗標改回 false。
   - (b) 產物或標記**存在**但旗標非 true（如 spec.md 已有 `## Clarifications` 但
     `steps.clarify.done ≠ true`——釐清可能中斷在 CRITICAL 未處理）→ 以狀態檔
     為準：視為未完成，從該階段續跑。**禁止**憑檔案標記把旗標改成 true。
6. 向使用者回報偵測結果（「偵測到：<階段> 已完成，將從 <下一階段> 續跑」），
   確認後繼續；不重做已完成階段。
7. 特例：`detected_stage=implement` 時，從狀態檔找出第一個未完成的 story，
   並向使用者列出已完成/待做的 story 清單。未勾選 task ≥2 而 `task-plan.py check`
   未印出 `plan=ok`（規劃檔缺失、未涵蓋全部未勾選 task，或是導入並行實作前的舊版
   規劃檔）→ 先補做 implement-loop.md 步驟 0P（只規劃剩下的 task）再續跑。
   `implement_mode=parallel` → 從 W1 續跑（`task-plan.py next` 會原樣印出進行中的波次）；
   working tree 乾淨卻有殘留 worktree 或 `sdd-wave/<NNN>-*` 分支（波次已 commit、
   清理前中斷）→ 先 `wave-worktree.sh clean`。

## 錯誤處理細則（SKILL.md「錯誤處理」引用，本節為唯一版本）

- **subagent 回報無法判讀**（Agent 呼叫失敗，或回報缺「審查結論／驗證結論／影響
  邊界報告／並行規劃集合」標頭，或 plan 模式的輸出檔缺行）→ 以原 prompt 重派一次；仍失敗 → 一律**視同該閘門 FAIL**
  （不得腦補為通過），計入 3 輪上限並依 SKILL.md 通用規則 4 處理。
  回報**超長但有效** → 依 model-dispatch.md §5 要求重整一次，不照單全收。
- **憲章來源不可用**（`check_baseline=absent` 且使用者未在 prompt 提供自訂憲章）
  ——決策樹（步驟 0 判讀規則引用這裡）：無 `.specify/memory/baseline/` 舊副本 →
  AskUserQuestion 三選一：「安裝 sdd-baseline skill（連到 `~/.claude/skills/`
  或設 `SDD_BASELINE_DIR`）後重跑步驟 0」／「改提供自訂憲章（檔案、目錄或貼上
  內容）」／「中止」，不可未經使用者同意憑記憶湊一份憲章；有舊副本 →
  AskUserQuestion 明確告知「可用舊快照（版本 X）繼續，但可能落後」，由使用者
  決定續用或中止。
- **sdd-implementer 失敗或回報無法判讀**：它可能已寫入部分檔案——先查
  `git status` 現況，再以原 prompt **重派續作**（prompt 註明「前次中斷，
  現有 diff 為現況；tasks.md 只勾了已確認完成的任務，未勾任務請比對 diff 判斷
  進度後續作，回報本次確認完成的全部任務 ID」）；仍失敗 → 半成品依上方
  dirty tree 分類表處理（產品程式碼不補 commit），並問使用者。並行模式的 unit
  同理，但查的是該 unit 的 worktree（`git -C <worktree> status`），重派時工作目錄
  不變；其他 unit 不受影響，照常等它們回報。

## 完成報告（SKILL.md 引用，本節為唯一版本）

全流程結束時向使用者總結：feature 名稱與分支、各階段 commit 一覽
（`git log --oneline`）、驗收結果摘要（幾條 PASS）、審查發現與處理、
已知偏差（若有）、建議後續（push / PR / 下一個 feature）。

有 `parallel_plan` 時另附**並行規劃觀察**（供校準規劃與模式門檻），內容取自
`python3 $SKILL_DIR/scripts/task-plan.py verify --plan <FEATURE_DIR>/parallel-plan.json
--root <專案根> --feature NNN`：採用的模式與原因、task 數／批次數／理論加速、
衝突比例與類型分布，以及**集合涵蓋率**——依序模式以各 phase 的 commit、並行模式
以各波次 commit（body 的 `tasks:` 行）核對：實際變更檔中沒被對應 task 寫入集合
涵蓋的檔案，其中也被其他 phase／波次碰到的列為「可能漏判」（並行時最可能撞檔
之處），逐項註明屬隱含測試修改、實作時拆出的新檔或共用資源。並行模式另附實際
波次數對照預估、合併衝突退回與「撞到別條 lane」的次數（取自波次 commit body）。建議後續固定附兩條
提醒：

1. `.specify/memory/baseline/` 含憲章基線副本（來源記於其 `manifest.json`），
   目標專案公開發布或開源前需先評估此目錄的處置。
2. 日後在本 harness 之外 merge / rebase 後，記得跑 `codegraph sync` 再開下一個
   feature（codegraph 啟用時）。
