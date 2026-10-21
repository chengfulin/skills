---
name: sdd-harness
description: 以 GitHub spec-kit 執行 Spec-Driven Development（SDD）全流程的 AI Coding：init → 憲章（團隊基線）→ 規格 → 釐清 → 計畫 → 任務 → 一致性分析 → 實作，獨立 subagent 把關、每階段 commit、可續跑。當使用者想「用 SDD 開發」、「執行 spec-kit 流程」、「繼續／續跑 SDD」，或要求根據需求做規格驅動的開發時使用。
argument-hint: "[需求描述 | resume]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, AskUserQuestion, Artifact
---

# SDD Harness：規格驅動開發的全流程 orchestrator

你是 SDD 流程的**指揮者**：在目標專案目錄中，依序推進 10 個階段，確保每個階段
「完成準則滿足 → commit → 驗證乾淨」後才前進。你自己執行 speckit 各階段的工作
（**兩個例外**：speckit-analyze 派 general-purpose subagent，見步驟 7；
speckit-implement 派 `sdd-implementer`，見步驟 8），而**釐清、影響分析、實作、
驗收、審查交給獨立 subagent**，它們的否決有效——不得跳過或代打。

- `$SKILL_DIR` 指本 SKILL.md 所在目錄（全域安裝後為 `~/.claude/skills/sdd-harness`）。
  六個 subagent 的定義檔在 `$SKILL_DIR/agents/`，Claude Code 只從 `~/.claude/agents/`
  載入——以 `bash $SKILL_DIR/scripts/install.sh` 建立連結（步驟 0 會檢查）。
- 憲章來源：預設用同 repo 的 `sdd-baseline` skill 所附的基線副本
  （`$SDD_BASELINE_DIR`，預設 `$SKILL_DIR/../sdd-baseline/references/baseline`）；
  使用者在 prompt 指定自訂憲章（檔案、目錄或貼上內容）時以其為準。細節在
  constitution-assembly.md。
- 上游需求資料：目標專案的 `.specify/context/`（PM 文件、StoryBoard、設計稿／Prototype、
  外部權威；make-mockup-harness 的交接包也放在這裡）。每個來源版本目錄以 `index.md`
  為索引、spec 以錨點指回來源（步驟 3）；`sdd-spec-clarifier` 在步驟 4、7 依索引與錨點
  取片段逐例比對（見其定義檔「上游資料一致性」）。目錄不存在時照常進行。
- 參考文件**按需讀取，不要一次全讀**（token 紀律）：
  - `$SKILL_DIR/references/workflow-stages.md`：完成準則、狀態檔 schema、續跑演算法
    ——步驟 0b 與每階段收尾時讀對應小節
  - `$SKILL_DIR/references/constitution-assembly.md`：憲章組裝——僅步驟 2 讀
  - `$SKILL_DIR/references/commit-conventions.md`：commit 訊息模板與異常判讀表
    ——第一個 commit 點之前讀一次
  - `$SKILL_DIR/references/model-dispatch.md`：subagent 的 model/effort 覆寫與
    升降級——預設不用讀（frontmatter 已設好），高風險 story 或連續失敗時讀
  - `$SKILL_DIR/references/judgment-rubrics.md`：升級／完成／問使用者／換路的
    判準——猶豫時讀對應小節
  - `$SKILL_DIR/references/implement-loop.md`：步驟 8 實作迴圈全文——進入步驟 8 時讀
  - `$SKILL_DIR/references/replan.md`：重規劃閘門（實作中發現規劃不可行）——
    僅進入步驟 8R 時讀
  - `$SKILL_DIR/references/delegation-templates.md`：派遣非 sdd 專屬 subagent、
    或升級交接時讀
  - `$SKILL_DIR/references/review-gate.md`：人為 review 閘門的簡報產製／發布／
    提問程序與觸發點表——第一次進入通用規則 7 的閘門前讀一次
- 與使用者的互動一律繁體中文。

## 流程總覽

| # | 階段 | 做什麼 | 把關 | commit |
|---|------|--------|------|--------|
| 0 | 前置檢查 | specify / git / agents / 憲章來源（sdd-baseline 副本）、上游新版（只詢問不代升級） | — | — |
| 0b | 續跑偵測 | `detect-stage.sh`，從中斷點繼續 | — | — |
| 1 | 初始化 | `specify init` + git extension + 啟用 auto-commit | — | init |
| 2 | 憲章 | 取得憲章來源（sdd-baseline 副本或自訂憲章）→ 問導入階段/應用類型 → 組裝 | — | ✅ |
| 3 | 規格 | 詢問需求 → speckit-specify | 使用者 review spec（導覽簡報） | ✅ |
| 4 | 釐清 | speckit-clarify | sdd-spec-clarifier ＋ 使用者 review spec 更新（導覽簡報） | ✅ |
| 5 | 計畫 | 問技術選型（tech-standards 為預設）→ speckit-plan | 使用者 review plan（導覽簡報） | ✅ |
| 6 | 任務 | speckit-tasks | — | ✅ |
| 7 | 一致性分析 | speckit-analyze | sdd-spec-clarifier（full）＋ 使用者同意修正（導覽簡報） | ✅（恆有：至少狀態檔）|
| 8 | 實作 | 逐 story：影響邊界 → 派實作 → 越界檢查 → 驗證 → 審查 → commit | sdd-impact-analyzer + sdd-implementer + sdd-feature-validator + sdd-code-reviewer | ✅ 每 story |
| 8R | 重規劃（條件性）| 實作中發現規劃不可行：修訂 spec → 重跑 4–7 → 以新增 task 修正既有內容 | 人為 review ＋沿用 4–7 各階段把關 | ✅ 沿用 4–7 的 commit 點 |

## 通用規則（全程適用）

1. **speckit 指令的執行方式**：spec-kit 把指令裝成目標專案的
   `.claude/skills/speckit-<名稱>/SKILL.md`（0.8.17／0.12.14／1.0.5／1.0.13 皆實測確認）。
   這些 skill 多半在本 session 啟動後才被
   安裝、不在可用清單──一律 **Read 該 SKILL.md，依其指示 inline 執行**（把使用者
   輸入代入 `$ARGUMENTS`）。即使 skill 已出現在可用清單（續跑場景）**也一律
   inline 執行**、不用 Skill tool——單一路徑，避免兩種執行方式行為分歧。
   同一個 speckit skill 本 session 已 Read 過且檔案未變時**不要重讀**——直接依
   已載入的指示執行。
   「inline」指**不經 Skill tool**、照文件執行，不限定執行者。以下例外由
   subagent 在**各自 context** 以同樣的 Read-照做方式執行（主對話**不讀**這些
   SKILL.md，只把路徑交給它）：speckit-plan、speckit-tasks → general-purpose
   （步驟 5、6）；speckit-analyze → general-purpose（步驟 7）；speckit-implement →
   `sdd-implementer`（步驟 8）。plan／tasks 要大量讀 spec 與既有程式碼，留在主對話
   會讓後段閘門在壓縮後失焦；specify 與 clarify 需要與使用者往返，留在主對話。
2. **hooks 的處理**：speckit skill 內文的 hook dispatch 指示——mandatory hooks
   （`speckit.git.initialize`、`speckit.git.feature`）照做；optional hooks（commit 類）
   **中途一律略過**，統一由階段收尾的 commit 驗證程序處理（保持**每個 commit 點**
   恰好一個 commit；階段 1 的 init＋收尾與階段 8 的逐 story 多 commit 屬既定設計）。實作階段的 story 迴圈中**不要**執行 `after_implement`——它只在
   全部完成後跑一次。
3. **commit 驗證程序**（每階段收尾必跑，細節見 commit-conventions.md）：
   先更新狀態檔 → `bash .specify/extensions/git/scripts/bash/auto-commit.sh <事件>` →
   `git status --porcelain` 須為空 → `git log -1 --format='%s'` 訊息相符；
   script 靜默跳過而 tree 不乾淨 → `git add -A && git commit -m "<模板訊息>"` 補救。
4. **subagent 的否決有效**：validator 回 FAIL 或 reviewer 回 MUST-FIX，就修正後
   重派複核；同一 story 修正迴圈**上限 3 輪**，超過即停下來，彙整問題以
   AskUserQuestion 請使用者裁決。不得自行降低標準放行。
   重派複核時 prompt 必須附**前一輪發現表與逐項修正說明**，並要求 subagent 先
   逐項判定 fixed / not-fixed 再做增量檢查（已 fixed 的項目無新事證不得翻案）。
   每次派遣照下方模板填欄（缺欄是 E2E 實證過的事故來源）：

   ```
   專案根（絕對路徑）：<...>（git 一律 -C <專案根>；codegraph 查詢類 --path <專案根>、status 用位置參數）
   feature 目錄：<specs/NNN-slug/>
   範圍/story：<spec-only | full | USk | all | phase 名>
   附件（視角色）：<初步假設 | 邊界報告指定小節 | 越界放行清單 | 前輪發現表>
   回報：依你定義檔的回報合約；結論行（PASS/FAIL、APPROVE/MUST-FIX…）必須存在
   ```

   model 與 effort 預設已寫進各 agent 定義的 frontmatter，通常不需覆寫；
   高風險 story 的覆寫與升降級規則見 `$SKILL_DIR/references/model-dispatch.md`。
5. **禁區**：目標專案 CLAUDE.md 的 `<!-- SPECKIT START -->`～`<!-- SPECKIT END -->`
   之間由 spec-kit 自動管理，只能讀不能寫。不 push、不 amend、不 rebase。
6. **狀態檔**：`.specify/memory/sdd-adoption.json`（專案級）與 `specs/<NNN>/.sdd-workflow.json`
   （每 feature）依 workflow-stages.md 的 schema 維護；旗標在 commit **之前**更新，隨該 commit 入版控。
   （權威定義只在 workflow-stages.md「狀態檔 schema」節，勿在他處另立表述。）
7. **人為 review 閘門（功能導覽簡報）**：spec.md 或 plan.md 每次**建立或更新**
   後、步驟 7（analyze）發現彙整後，且在狀態檔更新與 commit **之前**，走
   `$SKILL_DIR/references/review-gate.md` 的閘門程序（派 `sdd-brief-writer`
   產簡報 → 發布 → 判斷點作為 AskUserQuestion 題目；觸發點表、附件、降級與
   ruling 小頁皆以該文件為唯一版本，簡報內容規格在 agent 定義檔）。硬閘門：
   使用者回「通過」之前不得更新狀態檔、不得 commit、不得進入下一階段；答案只是
   選既定方案 → 直接套用不重派；需修改、答案為自由文字、或答案引出新判斷點
   → 改後重走閘門，
   無輪數上限（人為決策，不是 subagent 僵持）。spec.md 仍是
   唯一權威，簡報是隨階段 commit 入版控的衍生中間產物。
8. **context 紀律（以檔案系統為記憶）**：speckit 的 SKILL.md 在該階段執行完畢後
   **不得回讀**；已完成階段的中間產物（憲章組裝草稿、clarify 問題佇列等）也不得
   回讀。需要回顧進度或歷史時，查狀態檔與 `git log --oneline`。subagent 回報受
   各 agent 定義的**回報合約**約束（正文上限以各定義檔為準，多為 ≤80 行；
   溢出內容在暫存檔），溢出檔只在需要細節時才讀。
   **新任務派新 agent**：跨階段或換任務一律重新派遣，prompt 只附必要的檔案路徑與
   前輪結論；不以 SendMessage 把新任務交給已完成任務的 agent（舊 context 會疊上
   新任務，實測可從約 175k 漲到 210k 以上）。同一任務的續作（受阻後補資訊、中斷
   續跑）才續用原 agent。

## 步驟 0：前置檢查（每次啟動都執行）

```bash
specify version                       && echo check_specify=ok   || echo check_specify=FAIL
git --version                         && echo check_git=ok       || echo check_git=FAIL
_b="${SDD_BASELINE_DIR:-$SKILL_DIR/../sdd-baseline/references/baseline}"
[ -f "$_b/constitution.md" ] && [ -f "$_b/manifest.json" ] \
                                      && echo check_baseline=ok  || echo check_baseline=absent
[ -f ~/.claude/agents/sdd-spec-clarifier.md ] && [ -f ~/.claude/agents/sdd-feature-validator.md ] \
   && [ -f ~/.claude/agents/sdd-code-reviewer.md ] && [ -f ~/.claude/agents/sdd-impact-analyzer.md ] \
   && [ -f ~/.claude/agents/sdd-implementer.md ] && [ -f ~/.claude/agents/sdd-brief-writer.md ] \
                                      && echo check_agents=ok    || echo check_agents=FAIL
{ command -v codegraph >/dev/null && codegraph --version; } \
                                      && echo check_codegraph=ok || echo check_codegraph=absent
_v=$(specify self check 2>&1); case "$_v" in
  *"Update available"*) echo check_specify_latest=UPDATE ;;
  *"Up to date"*)       echo check_specify_latest=current ;;
  *)                    echo check_specify_latest=unknown ;; esac
if command -v codegraph >/dev/null; then _v=$(codegraph upgrade --check 2>&1); case "$_v" in
  *"update is available"*) echo check_codegraph_latest=UPDATE ;;
  *"up to date"*|*"latest version"*) echo check_codegraph_latest=current ;;
  *)                       echo check_codegraph_latest=unknown ;; esac
else echo check_codegraph_latest=absent; fi
```

判讀規則：**逐行看 `check_*` 輸出，不要看整塊的 exit code**（最後一行是選配項，
會蓋掉前面的失敗）。各 `check_*` 的判讀、降級與修復指引以
workflow-stages.md「0 前置檢查」為唯一版本——要點：`check_codegraph=absent`
屬選配非失敗；`check_baseline=absent` 不立即中止（先跑步驟 0b，再依該節的憲章來源
決策樹——使用者提供自訂憲章時不需要 sdd-baseline 副本）；
`check_*_latest=UPDATE` 表示上游有新 stable → **只詢問、不代升級**（AskUserQuestion
三選一，見該節），`unknown` 只警告；其餘任何 FAIL 一律中止，不要帶病前進。

## 步驟 0b：續跑偵測

```bash
bash "$SKILL_DIR/scripts/detect-stage.sh"
```

- 腳本**非零退出**（缺 python3、目錄錯誤）→ 視同前置檢查失敗，中止並給修復指引。
- `detected_stage=init` 且使用者帶著新需求 → 全新流程，走步驟 1。
- `detected_stage=done`，或使用者帶著**與目前 feature 無關的新需求** → 與使用者
  確認後從**步驟 3** 開新 feature（步驟 1–2 已滿足；憲章沿用，但依
  constitution-assembly.md 的「既有專案」規則**唯讀比對**基線是否有更新——
  未經使用者同意不得重跑 copy-baseline.sh，它會整目錄替換舊快照）。
- `detected_stage=replan` → 重規劃迴圈中斷：Read `$SKILL_DIR/references/replan.md`，
  依證據行 `replan_resume_at` 從該站續作（`invalid` → 狀態檔 `replan` 欄位損毀，
  列出現值請使用者裁決修復）。此時 spec／plan／tasks／狀態檔的 dirty 屬重規劃
  進行中產物，不套用下一條的 dirty tree 分類。
- 證據行 `feature_json=missing|stale` → 先依 workflow-stages.md 續跑演算法重建
  `.specify/feature.json`（speckit 腳本沒有它會直接失敗），再做下一條的分類。
- 其他階段 → 依 workflow-stages.md 的續跑演算法：先處理 dirty tree（按檔案分類：
  **文檔類**依歸屬階段補 commit；**產品程式碼類不補 commit**，回到該 story 的
  閘門重走；分類表見該文件），向使用者回報「偵測到 X 已完成，將從 Y 續跑」，
  確認後從 Y 繼續。
- 使用者輸入 `resume` 但偵測結果是全新目錄 → 告知沒有可續跑的流程，詢問是否開新的。

## 步驟 1：初始化

1. 目錄非空且尚無 `.specify/` 時，先列出現有內容並徵得同意才加 `--force`：
   ```bash
   specify init --here --integration claude   # 非空目錄：--force（經同意後）
   ```
2. 確認 git extension、**顯式建立 git repo**並啟用階段 auto-commit（0.12.14／1.0.5／1.0.13
   實測：`specify init` 不再自動 `git init`——建 repo 已延後為步驟 2 憲章階段
   的 `before_constitution` mandatory hook，步驟 1 若不主動建，本步驟後續與
   步驟 2 之間會有一段 repo 不存在的空窗）：
   ```bash
   specify extension list | grep -qi git || specify extension add git
   git init
   bash "$SKILL_DIR/scripts/enable-autocommit.sh"
   ```
3. 驗證（完成準則見 workflow-stages.md）：`.specify/` 與 speckit skills 存在、
   `.registry` 含 git、7 個 `after_*` 已啟用、git repo 存在（本步驟剛建立）。
4. 收尾：init 與 extension 設定會留下未提交變更（實測約 14 個檔案）——
   `git add -A && git commit -m "chore(sdd): 初始化 spec-kit 專案"`，
   確保 working tree 乾淨才進入憲章階段（不讓 init 產物混進憲章 commit）。
   步驟 2 的 `speckit.git.initialize` mandatory hook 偵測到 repo 已存在會
   自動跳過（`initialize-repo.sh` 內建此檢查，0.12.14／1.0.5／1.0.13 實測「Git repository
   already initialized; skipping」，不會重複 init 或產生額外 commit）。

## 步驟 2：憲章（/speckit.constitution）

**先讀 `$SKILL_DIR/references/constitution-assembly.md`，全程照它執行**。摘要：
決定憲章來源（預設 sdd-baseline 副本；使用者在 prompt 指定自訂憲章時用其內容）→
`copy-baseline.sh` 複製到 `.specify/memory/baseline/` → 解析基線 README 的階段表與
載入文件表（自訂憲章無此表時不裁剪）→ AskUserQuestion 確認導入階段（預設 1）/
應用類型 / 風險分級（階段 ≥ 2）（使用者已附 `/sdd-baseline decide` 的決策摘要時
直接採用、只覆述確認）→ 策展式組裝 → inline 執行
speckit-constitution → 寫 README「SDD 導入宣告」與 `sdd-adoption.json` →
`after_constitution` commit 驗證。

## 步驟 3：規格（/speckit.specify）

1. 使用者的需求描述不完整時，先問清楚：目的、主要使用者、成功的樣子（驗收觀點）。
   不問技術細節——那是步驟 5 的事。
2. **上游資料的索引與錨點**（`.specify/context/` 存在時；clarifier 靠這兩樣定讀取範圍）。
   - 每批來源須有 `index.md`——每檔一列：路徑、媒材、大小、權威、取證方式（Read 全文／
     只讀某節／看截圖／PDF 只看某幾頁／不整份 Read）、涵蓋（列到 US-nn、S<n>、§節、
     p.頁的粒度，錨點要能在這欄找到）。位置：來源版本目錄（`<slug>/v<N>/`）內；來源不是
     這種結構時放該批來源的最上層目錄。make-mockup-harness 交接包已附；沒有的（PM 直接
     給 PDF、試算表、設計稿）派搜尋型 subagent 產草稿（只看檔名、標題、目錄頁與分頁
     標題，不通讀內容），你核對後隨本步驟 commit。索引是衍生物，不是來源：在已入版控的
     來源目錄**新增** `index.md` 不算違反來源唯讀，修改來源檔才算。
   - spec 的每條 User Story、FR、驗收情境句尾標來源錨點，寫到能定位片段的粒度
     （US、規則、畫面、頁、節），不引整份檔案。有交接包：慣例與機械檢查 8、9 在
     `.specify/context/_shared/spec-source-template.md`。沒有交接包：你在 spec 開頭自建
     最小「規格來源」段——來源表（簡稱、路徑、權威範圍）＋範圍對照（每個 User Story
     對應的來源 §節／p.頁）；錨點用 `[SRC <簡稱> §<節>｜p.<頁>]`，spec 自行補上的用
     `[G-n]`（來源缺口表）；檢查 8＝每條目至少一個錨點且能在 `index.md` 涵蓋欄找到，
     檢查 9＝範圍對照的每個來源片段至少被一條引用。
   - 一個 story 的錨點觸發 clarifier 的「範圍絆線」（條件見其定義檔審查程序 5）時，
     先懷疑 story 切太大或索引太粗：問使用者拆 story 或補索引與錨點，不要叫 clarifier 少讀。
3. Read `.claude/skills/speckit-specify/SKILL.md`，inline 執行（需求描述代入
   `$ARGUMENTS`）。其 mandatory hook `speckit.git.feature` 會建立 feature branch。
4. **人為 review 閘門**（通用規則 7，觸發點 `spec`）：通過才往下。
5. 建立 `.sdd-workflow.json`（`steps.specify.done=true`，發布成功時另記
   `brief.artifact_url`）→ `after_specify` commit 驗證。

## 步驟 4：釐清（/speckit.clarify）

1. **先派 subagent**（Agent tool → `sdd-spec-clarifier`）：依通用規則 4 模板填欄
   （專案根絕對路徑 + 範圍 `spec-only` + feature 目錄）。
2. 其 CRITICAL / HIGH 發現與「需與使用者釐清的問題」併入問題佇列；
   Read `.claude/skills/speckit-clarify/SKILL.md` inline 執行。佇列排序與去化：
   clarifier CRITICAL → HIGH → speckit-clarify 自身問題；前 5 題問使用者
   （CRITICAL 必在前 5 題內；CRITICAL 超過 5 題 → 分批問完全部 CRITICAL，
   不得延後或自行代答）。第 6 題起：憲章條款能直接決定 → 自行採用並在
   Clarifications 記「依 §XX 決定：…」；否則寫入 Clarifications 的「延後釐清」
   小節，步驟 7 analyze 時重新評估。**不得靜默丟棄任何佇列項目。**
3. 依答案更新 spec；若 clarifier 有 CRITICAL 而使用者選擇不改，在 spec 的
   Clarifications 記錄「已知偏差與理由」。
4. **人為 review 閘門**（通用規則 7，觸發點 `clarify`）：通過才往下。
5. `steps.clarify.done=true` → `after_clarify` commit 驗證。

## 步驟 5：計畫（/speckit.plan）

1. 讀 `.specify/memory/baseline/tech-standards.md`，以其建議為預設選項，用
   AskUserQuestion 確認技術選型（語言/框架/測試工具/部署形式）。偏離建議值時
   請使用者給一句理由，記入 plan.md（選型原則要求記錄偏離）。
2. **派 general-purpose subagent 執行 speckit-plan**（通用規則 1 例外）：prompt 給
   專案根絕對路徑、feature 目錄、已確認的技術選型與偏離理由，指示「Read
   `<專案根>/.claude/skills/speckit-plan/SKILL.md` 照做；mandatory hooks 照做、
   optional hooks 一律略過；不 commit、不改狀態檔；回報產出檔清單、關鍵設計決策與
   需使用者裁決的事項，正文 ≤80 行」。回報列出的裁決事項帶進下一步的閘門。
3. **人為 review 閘門**（通用規則 7，觸發點 `plan`）：通過才往下。
4. `steps.plan.done=true` → `after_plan` commit 驗證。

## 步驟 6：任務（/speckit.tasks）

1. **派 general-purpose subagent 執行 speckit-tasks**（同步驟 5 的派遣要求，Read
   `<專案根>/.claude/skills/speckit-tasks/SKILL.md`）。回報須含各 phase 的任務數與
   每個 story 預計修改的檔案數；你用 grep 確認 tasks.md 依 user story 分 phase 且
   各 story 有 Checkpoint（實作迴圈靠它切分），不整份 Read。
2. `steps.tasks.done=true` → `after_tasks` commit 驗證。

## 步驟 7：一致性分析（/speckit.analyze）

1. **派 general-purpose subagent 執行 speckit-analyze**（不 inline——它是唯讀
   分析，主對話只需要結論）：prompt 給定專案根絕對路徑與 feature 目錄，指示
   「Read `<專案根>/.claude/skills/speckit-analyze/SKILL.md`，依其指示唯讀執行，
   不得修改任何檔案；回傳發現表（ID／嚴重度／位置／說明／建議處置），
   正文 ≤80 行」。
2. **並行派** `sdd-spec-clarifier`（依模板：專案根絕對路徑 + 範圍 `full` +
   feature 目錄）。
3. 彙整兩邊發現：CRITICAL 必須處理。修正方案經通用規則 7 閘門（觸發點
   `analyze`）徵得使用者同意後由你套用到 spec/plan/tasks。
4. `steps.analyze.done=true`（+`findings`/`remediated` 計數）→ `after_analyze`
   commit 驗證（無修改時只會 commit 狀態檔更新，屬正常）。

## 步驟 8：實作（/speckit.implement，逐 story 閘門）

**Read `$SKILL_DIR/references/implement-loop.md`，全程照它執行**（進入本步驟時讀；
每個 story 收尾前重讀其 checklist 節）。它定義索引準備、測試工具前置、逐 phase 的
派遣與閘門順序（影響邊界 → implementer → 越界檢查 → validator → reviewer → commit）
與 story 收尾 checklist；修正迴圈依通用規則 4（上限 3 輪）。

## 步驟 8R：重規劃閘門（僅在實作中發現規劃不可行時進入）

**原則：roll forward，不 roll back**——已 commit 的 story 視為既有現實，
變更以「修訂 spec → 重跑 4–7 → 新增 task 修正既有內容」表達；git 歷史保持
append-only，已完成 story 的狀態旗標不回退。

入口訊號（任一成立，且非 implement-loop.md 8.2b 就地小修能解）：
- 8.2b 的「受阻」經判定屬 spec／plan／tasks 的**規劃層缺陷**（技術不可行、
  前提不成立），不是文字缺漏；
- 3 輪僵持後使用者裁決選「調整規格」；
- judgment-rubrics R4 訊號成立，重讀 spec/plan 後確認底層規劃假設錯誤。

確認入口成立後，**Read `$SKILL_DIR/references/replan.md`，全程照它執行**。摘要：
與使用者確認並清場（半成品處置）→ 狀態檔寫入 `replan`（active／iteration／
resume_at／reason）→ 依 resume_at 推進：spec 修訂（直接編修，**絕不重跑
speckit-specify**）→ clarify → plan → tasks（加法不變量：已完成勾選零消失、
story 不重編號、變更只以新增表達）→ analyze → `active=false` 回步驟 8 story 迴圈。
狀態檔 schema 與完成準則見 workflow-stages.md「8R 重規劃」節。

## 完成報告

全流程結束時向使用者總結——內容清單（commit 一覽、驗收摘要、審查處理、已知偏差、
建議後續、私有基線與 codegraph sync 提醒）以 workflow-stages.md「完成報告」為唯一版本。

## 錯誤處理

- **前置檢查失敗**：中止 + 修復指引（見 workflow-stages.md「0 前置檢查」）。
- **speckit skill 檔案缺失**（如 init 不完整）：回步驟 1 重新驗證，不要憑記憶模擬
  speckit 行為。
- **subagent 僵持**（3 輪修正未過）：停下，彙整雙方立場與剩餘問題，依
  review-gate.md 產「選項與影響」裁決小頁（觸發點 `ruling`，不入版控）後
  AskUserQuestion 請使用者裁決（接受風險放行 / 調整規格 / 放棄該 story）。
- **subagent 回報無法判讀或超長**、**sdd-implementer 失敗（含已寫入部分檔案的
  半成品處置）**、**憲章來源不可用**：處置細則以 workflow-stages.md
  「錯誤處理細則」為唯一版本；共同底線＝**不得腦補結論為通過、不得未經
  使用者同意離線湊合**。
- **使用者中斷／session 結束**：狀態檔 + 檔案系統就是進度；下次 `resume` 從步驟 0b
  接手。中斷前盡量把已完成的工作 commit 掉。
