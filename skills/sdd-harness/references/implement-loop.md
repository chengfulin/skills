# 步驟 8 實作迴圈（/speckit.implement，依序模式逐 phase／並行模式逐波次）

僅由 SKILL.md 步驟 8 進入時讀取，**全程照本文件執行**；本文件是步驟 8 執行細節
（索引準備、測試工具前置、tasks.md 勾選、並行規劃與模式判定、依序模式的逐 phase
迴圈、並行模式的波次迴圈、越界放行、收尾 checklist）的唯一版本。完成準則與不變量在 workflow-stages.md「8 實作」節；入口訊號與 8R 重規劃在
SKILL.md 步驟 8R 與 replan.md；「通用規則 N」「模板」指 SKILL.md 的通用規則。

**進入本階段先做索引準備**（codegraph 可用時；不可用則整段跳過，影響分析走降級）：
`.codegraph/` 不存在 → `codegraph init .`；已存在 → `codegraph sync`。
init **不會**自動 gitignore（1.2.0／1.6.0／1.6.1 實測）——確認目標專案 `.gitignore` 含
`.codegraph/`，沒有就補上（隨下一個 commit 入版控，否則會破壞 working tree
乾淨檢查）。

**測試工具前置**：依 plan.md 的技術選型確認測試執行工具可用（如
`bats --version`、`pytest --version`，以 plan.md 實際選定者為準）；缺工具 →
停下回報並給安裝指引（例：`brew install bats-core`），不得帶病進入 story
迴圈——validator 無法執行測試＝驗收閘門必卡。撰寫 bats 測試時
`@test` 名稱一律用 ASCII，情境說明放註解（非 ASCII 名稱會使整檔 parse 失敗，
bats 1.13 實測）。

**tasks.md 勾選（主對話單一寫入）**：implementer 不碰 tasks.md，只回報完成的任務
ID；每次 implementer 回報（含分批、修正迴圈、失敗續作）後，**進下一個閘門之前**
由你勾選：

1. 核對回報的每個 ID 都屬於本次派遣範圍（該 phase，分批時為該批）；範圍外的 ID
   不勾，視同越界候選，依步驟 2c 的判準處理。
2. 以一行指令勾選（不 Read 整份 tasks.md），再以 grep 計數確認勾到的數目等於 ID 數：
   ```bash
   perl -pi -e 's/^([-*] )\[ \]( (?:T031|T032)\b)/$1\[X\]$2/' <FEATURE_DIR>/tasks.md
   grep -cE '^[-*] \[[Xx]\] (T031|T032)\b' <FEATURE_DIR>/tasks.md
   ```
3. 回報為「部分完成」或「受阻」時只勾已列出的 ID；未列出的任務維持 `[ ]`。

勾選在閘門前就寫入，讓中斷後續跑看得到進度；story 是否完成仍以狀態檔旗標為準。

**0P. 並行規劃與模式判定（task 粒度、全域）**：
索引準備與測試工具前置之後、Setup 開工之前執行。單位是 **task**，範圍是 tasks.md
**全部未勾選的 task**（Setup／Foundational／各 story／Polish 一起排），只算 task
之間的相依——phase 級的整體宣告（「Foundational 阻擋所有 story」「US2 相依 US1」）
不構成衝突，analyzer 逐 task 找出真正需要的前置。未勾選 task 少於 2 個 → 跳過，
走依序模式；`python3 $SKILL_DIR/scripts/task-plan.py check --tasks <FEATURE_DIR>/tasks.md --plan
<FEATURE_DIR>/parallel-plan.json` 印出 `plan=ok` → 跳過，沿用狀態檔
`parallel_plan.mode`。
   a. **切範圍**：每個 phase 一個 analyzer；未勾選 task 超過 20 個的 phase，依
      `###` 小節或任務 ID 切成每段 ≤15 個（同一檔案的連號任務放同一段）。
   b. 建空目錄 `${TMPDIR:-/tmp}/sdd-plan-<NNN>/`（已存在先清空），在**同一則訊息**
      並行派 `sdd-impact-analyzer`，每段一個（依模板：專案根絕對路徑 + 範圍（phase
      名或 `Txxx–Tyyy`）+ feature 目錄 + 模式 `plan` + 輸出檔
      `${TMPDIR:-/tmp}/sdd-plan-<NNN>/<範圍>.txt`；不附初步假設）。超過 10 段時
      分兩輪派，前一輪全部回報後再派下一輪（subagent 同時執行數有上限）。
   c. 全部回報後跑：
      ```bash
      python3 $SKILL_DIR/scripts/task-plan.py build --tasks <FEATURE_DIR>/tasks.md \
        --sets ${TMPDIR:-/tmp}/sdd-plan-<NNN> --out <FEATURE_DIR>/parallel-plan.json \
        --state <FEATURE_DIR>/.sdd-workflow.json --root <專案根> --basis <codegraph|grep|greenfield>
      ```
      `--basis` 取各 analyzer 回報中最弱者。退出碼 3（`error=missing_sets`）→
      對缺行 task 所屬的範圍重派一次；仍缺 → 視同閘門 FAIL，回報使用者。
      腳本的判定規則（主對話不手算，也不改判）：任一成立即**衝突**——
      - `寫入`：兩者寫入集合有同一檔案（檔名未定的 `目錄/*` 與同目錄任何路徑視為同檔）；
      - `相依`：一方寫入的檔案出現在另一方讀取集合；
      - `資源`：共用資源識別相同（migration 一律視為相同）；
      - `契約`：一方契約變更所在檔出現在另一方的寫入或讀取集合；
      - `宣告`：一方 Dep 列了另一方的 task ID，或列了另一方所屬的 phase 標籤；
      - `未定`：任一方信心「低」（實際落點要等其他 task 實作後才能判定）——
        與其他所有 task 都記為衝突，寧可錯殺。
      分批：先依明文 Dep 做拓撲排序（同層依 tasks.md 順序；成環的 task 比照信心
      低，與其他所有 task 衝突），衝突再依此順序定方向；
      task 的批次＝1＋（衝突的前序 task 的最大批次）。同批＝判定可同時開工。
      **模式判定**（腳本輸出 `mode=`）：以每個 phase 一條 lane 模擬波次（見下方
      「並行模式」），估計加速＝task 數 ÷ 各波次最長 lane 的 task 數總和；分析基礎
      為 `codegraph` 且估計加速 ≥1.5× → `parallel`，否則 `sequential`（原因寫在
      `mode_reason`）。greenfield／降級 grep 的集合不夠可靠，不能當並行實作的邊界。
   d. 腳本已把摘要寫入狀態檔 `steps.implement.parallel_plan`（schema 見
      workflow-stages.md），完整規劃在 `parallel-plan.json`。立即
      `git add -A && git commit -m "chore(sdd): 完成並行規劃（NNN）"`——避免規劃
      檔混進 Setup 的越界檢查。
   e. 向使用者回報（≤15 行，取自腳本輸出）：**採用的模式與原因**、波次數對照
      phase 數與估計加速、衝突比例與類型分布、關鍵路徑與前 3 個熱點檔、低信心
      task；另列 **tasks.md 品質訊號**
      ——`order_conflicts`（task 依賴排在後面的 task）、`cyclic`（明文相依成環，
      已比照低信心處理）、`P_marked_conflicts`（標
      `[P]` 卻被判衝突的 pair 數）與 analyzer 指出的「沒有 task 負責的必要改動」，
      建議使用者是否回 tasks.md 修正（不設閘門，修正走 8R 或下次 feature 改善）。
      使用者要求改用另一個模式 → 改寫 `parallel_plan.mode` 並把 `mode_reason` 記為
      「使用者指定：<原因>」，隨下一個 commit 入版控；在 `basis` 不是 codegraph 時
      指定並行，先提醒越界與撞檔會變多。

**依 `steps.implement.parallel_plan.mode` 進入對應模式**：`parallel` → 下方「並行
模式」；`sequential` 或沒有 `parallel_plan` → 下方「依序模式」。

## 依序模式（逐 phase）

0P 的集合**不取代**步驟 2a 的邊界報告（前面 phase commit 後程式碼已變，邊界報告
必須重做）。對 tasks.md 的每個 phase 依序（細節見 workflow-stages.md 的階段 8；
從並行模式降級而來時，已全數勾選的 phase 跳過，部分勾選的 phase 只派未勾選的
task）：

1. **Setup / Foundational**：派 `sdd-implementer`（依模板：專案根絕對路徑 +
   phase 名稱 + feature 目錄 + speckit-implement SKILL.md 路徑；邊界＝該 phase
   任務描述涉及的檔案）→ 依回報勾選 tasks.md → 核對該 phase 全 `[X]` 且變更檔案
   未超出任務範圍 →
   派 `sdd-code-reviewer`（依模板；diff 範圍：上一個 commit 之後全部變更含
   untracked；註明 phase 名稱、無 story ID）→ 需 APPROVE（MUST-FIX 走通用規則 4
   修正迴圈）→ `git add -A && git commit -m "chore(sdd): 完成 <phase>（NNN）"` →
   `codegraph sync`（codegraph 可用時，下同）。基礎設施是全 feature 的地基，
   不設審查等於零把關入版控。
2. **每個 User Story phase**：
   a. **影響邊界**：從 tasks.md 該 phase 的任務描述與 plan.md 的檔案規劃**列出**
      預期新增／修改的檔案與 symbol 清單作為初步假設（tasks.md 只取該 phase 段落，
      不整份 Read；**不執行 codegraph／grep
      掃描**——索引查證是 analyzer 的工作，主對話不下場、掃描原文不進主 context）；
      Agent tool 派 `sdd-impact-analyzer`（依模板：專案根絕對路徑 + story ID +
      feature 目錄 + 初步假設）取得**影響邊界報告**。greenfield 索引近空時報告
      很短，屬正常，不要因此跳過派遣。
   b. 派 `sdd-implementer`（依模板：專案根絕對路徑 + story ID + feature 目錄 +
      speckit-implement SKILL.md 路徑），限定「只做 Phase N（USk）的任務」，
      **並附上邊界報告的約束摘要**（預期新增/修改檔案、邊界外禁區）。
      它回報「受阻」或「越界候選」→ 先解決（裁決越界、修 spec 缺陷、問使用者）
      再重派續作，不要帶著未決事項前進。
      **分批派遣**：邊界報告的預期新增／修改檔案超過 12 個，或含超過約 3,000 行的
      檔案時，依任務 ID 把該 phase 切成數批（同一檔案的任務放同一批、測試與其對應
      實作放同一批），每批派一個新的 implementer，prompt 寫明「只做 Txxx–Tyyy」；
      前一批回報完成後才派下一批。步驟 c～g 仍以整個 story 為單位做一次。單一
      implementer 一次吃下整個大 story，實測會用到約 210k context。
   b2. 依 implementer 回報勾選 tasks.md（見上方「tasks.md 勾選」）。
   c. 越界檢查（雙重）：tasks.md 的 diff 只有你依回報勾的該 phase `[X]`
      （出現其他改動＝implementer 碰了 tasks.md，屬越界，先還原再追問）；且
      `git diff HEAD --name-only` 加 untracked 的檔案集合對照邊界報告。
      超出邊界的檔案**逐一處理**：能指出該 phase 對應的具體任務 ID（Txxx）→
      放行並記入「越界放行清單」（檔案 + 任務 ID；隨步驟 e 交 reviewer 覆核，
      commit 訊息 body 附一行）；指不出任務 ID → 停止實作，向使用者回報檔案
      清單與 diff 摘要。「合理產物」的唯一判準＝對得到任務 ID，不接受其他理由。
   d. Agent tool 派 `sdd-feature-validator`（依模板：專案根絕對路徑 + story ID +
      feature 目錄）→ 需 PASS。
   e. Agent tool 派 `sdd-code-reviewer`（依模板：專案根絕對路徑 + story ID +
      feature 目錄；diff 範圍：上一個 commit 之後的全部變更，即 `git diff HEAD`
      加 untracked；附件＝邊界報告的「預期修改的既有 symbol」表與「邊界外」
      清單＋越界放行清單——漣漪檢查用不到其他小節，**不要整份轉貼**）→ 需 APPROVE。
   f. FAIL / MUST-FIX → 修正（發現表已給 檔案:行號 與具體修法的小修正，你直接
      套用；需要重寫或成批變更 → 派 `sdd-implementer` 附前輪發現表）→
      **重跑步驟 c 的越界檢查**（修正本身也可能越界）→
      重派該 subagent 複核（附前輪發現表，見通用規則 4；上限 3 輪）。
      reviewer 階段的修正若動到產品程式碼，複核 APPROVE 後**必須再派 validator
      對該 story 回歸一次**——修正可能弄壞已 PASS 的驗收（回歸計入同一 3 輪上限）。
   g. 通過 → 依下方「story 收尾 checklist」逐項核對後 commit。

   **story 收尾 checklist**（每個 story 收尾前回到本節重讀，逐項打勾）：
   - [ ] tasks.md：該 phase 任務全數 `[X]`（由你依回報勾選），且**只有**該 phase 新增 `[X]`
   - [ ] 最後一輪 validator 結論 PASS、reviewer 結論 APPROVE
   - [ ] 有修正過 → 越界檢查已在最後一輪修正後重跑
   - [ ] 狀態檔 story 旗標已更新（validated/reviewed/committed）——必須在 commit 之前
   - [ ] `git add -A && git commit -m "feat(sdd): 實作 <story 標題>（NNN, USk）"`
   - [ ] `git status --porcelain` 為空
   - [ ] `codegraph sync`（codegraph 可用時；讓下一個 story 的邊界分析基於最新索引）
3. **Polish**：派 `sdd-implementer`（依模板，限定 Polish；邊界＝該 phase 任務
   描述涉及的檔案）→ 依回報勾選 tasks.md → 全部任務 `[X]` → 派 `sdd-code-reviewer`
   （依模板；diff 範圍：Polish 的全部變更）→ 需 APPROVE → 派 `sdd-feature-validator`
   （依模板，story ID＝`all`：全 feature 回歸，逐 story 分節判定）→ 需 PASS
   （FAIL → 通用規則 4 修正迴圈，上限 3 輪，超過即問使用者；修正若動到產品
   程式碼，validator 複核 PASS 後**必須再派 reviewer 覆審該批修正**——鏡像
   8.2f 的回歸規則，未經覆審的修正不得進 after_implement commit；reviewer
   覆審若再引出產品程式碼修正，APPROVE 後須再派 validator（`all`）回歸——
   雙向閉合，兩個方向的複核均計入同一 3 輪上限）→
   `steps.implement.done=true` → `auto-commit.sh after_implement` → commit 驗證 →
   最終 `codegraph sync`。

## 並行模式（波次）

單位是**波次**：每個 phase 一條 lane，一條 lane 交給一個 implementer，依序做一串
task（lane 內的 task 可以彼此相依）；不同 lane 的 task 由 `task-plan.py` 保證兩兩
不衝突，各在自己的 git worktree 同時實作，再合併回專案根一起過閘門、一個波次一個
commit。同時最多 3 條 lane；一條 lane 累計寫入超過 12 個檔就收口，剩下的留到下一個
波次。**0P 的集合就是實作邊界**——不另派 boundary 模式的 analyzer；集合漏判由合併
撞檔、越界檢查與整合測試三道關卡抓。

W1. **排波次**：
    ```bash
    python3 $SKILL_DIR/scripts/task-plan.py next --tasks <FEATURE_DIR>/tasks.md \
      --plan <FEATURE_DIR>/parallel-plan.json --state <FEATURE_DIR>/.sdd-workflow.json
    ```
    輸出 `wave=<k>`、`completes=`（本波次做完就全數完成的 phase），以及每個 unit
    一行 `u<j> | <phase> | <task ID，依執行順序> | W=<寫入集合>`；腳本同時把波次寫入
    狀態檔 `current_wave`（續跑時原樣印出、標 `resume=yes`，不重排）。
    `wave=none` → 跳到「並行模式收尾」；`error=stale_plan` → 回 0P 只規劃剩下的 task。
W2. **派遣**：
    - **只有 1 個 unit** → 不建 worktree，在專案根派 `sdd-implementer`（依模板：
      專案根絕對路徑 + phase + 任務 ID 清單 + feature 目錄 + speckit-implement
      SKILL.md 路徑；邊界＝該 unit 的 W），直接進 W4。
    - **多個 unit** → `bash $SKILL_DIR/scripts/wave-worktree.sh add <專案根> <NNN> <k> u1 u2 …`
      （每個 unit 從 HEAD 建一個 worktree，被 gitignore 的單檔如 `.env`、
      `.specify/feature.json` 會複製進去，`node_modules`／`.venv` 以 symlink 共用）；
      在**同一則訊息**並行派 `sdd-implementer`，每個 unit 一個（依模板：專案根
      絕對路徑 + **工作目錄＝該 unit 的 worktree 路徑** + phase + 任務 ID 清單（照
      W1 的順序）+ feature 目錄 + 專案根下的 speckit-implement SKILL.md 路徑；邊界＝
      該 unit 的 W）。
    - 任一 unit 回報「受阻」或「越界候選」→ 先解決（同依序模式 2b），再對**同一個
      worktree** 重派續作。全部 unit 有結論後才合併；決定放棄的任務不勾，下一個
      波次會重新排到。
W3. **合併**（多 unit 波次）：
    `bash $SKILL_DIR/scripts/wave-worktree.sh merge <專案根> <NNN> <k> <FEATURE_DIR> u1 u2 …`
    依序把各 unit 的變更套回專案根（不 commit），逐 unit 判讀：
    - `status=merged`：`files=` 是該 unit 的實際變更檔，W5 越界檢查用；`forbidden=`
      非空＝implementer 改了 feature 目錄（已排除、不套用），記為越界並追問。
    - `status=conflict`：與先合併的 unit 撞檔＝規劃漏判。該 unit **不套用、不勾選**，
      下一個波次會在新基礎上重做；記入波次 commit body 的「合併衝突退回」。
    - `status=empty`：沒有變更。回報卻說有完成任務 → 視同回報無法判讀
      （workflow-stages.md「錯誤處理細則」）。
W4. **勾選**：依各 unit 回報勾選（規則同上方「tasks.md 勾選」，核對範圍＝該 unit
    的任務清單；`conflict` 的 unit 不勾）。
W5. **越界檢查（逐 unit）**：tasks.md 的 diff 只有本波次的勾選；該 unit 的 `files=`
    （單 unit 波次＝`git diff HEAD --name-only` 加 untracked）對照該 unit 的 W（`目錄/*`
    涵蓋同目錄任何檔）。W 之外的檔案逐一處理：
    - 也在本波次**其他 unit** 的 `files=`、W 或 R 裡 → **撞到別條 lane**，不放行：
      停下回報使用者，建議還原該檔、把相關 task 的勾選撤回留到下一個波次重做。
    - 否則同依序模式 2c：對得到該 unit 的任務 ID → 放行並記入越界放行清單；對不到
      → 停止實作，回報使用者。
W6. **整合測試**：以 plan.md 選定的測試指令在專案根跑全量測試，輸出寫入
    `${TMPDIR:-/tmp}/sdd-wave-<NNN>-<k>.log`，只讀摘要（`tail -30`）。各 worktree
    單獨綠燈不代表合起來沒壞（例如一條 lane 改了建構子簽名、另一條 lane 的新測試用
    舊簽名），這一步抓合併後才出現的語意衝突。失敗 → 派 `sdd-implementer`（專案根、
    不建 worktree；附失敗摘要與 log 路徑；邊界＝本波次全部 unit 的 W）修正，計入
    W8 的 3 輪上限。
W7. **閘門**（在**同一則訊息**並行派）：
    - `sdd-code-reviewer`，每個 unit 一個（依模板；diff 範圍＝`git diff HEAD --
      <該 unit 的 files>` 加其中的 untracked；註明 phase 與任務 ID；附件＝該 unit 各
      task 在 parallel-plan.json 的 W 與 C（契約變更）、越界放行清單）→ 需 APPROVE。
    - `sdd-feature-validator`，`completes=` 中每個 user story 一個（story ID）→ 需
      PASS。Setup／Foundational／Polish 不派（由 W6 與收尾的 `all` 回歸涵蓋）。
W8. **修正迴圈**：同依序模式 2f（上限 3 輪），差別：修正一律在專案根進行；修正後重跑
    W5 越界檢查與 W6 整合測試；動到產品程式碼 → 對修正涉及的 unit 重派 reviewer
    覆審，並對 `completes=` 的 story 重派 validator 回歸。
W9. **收尾**：依下方「波次收尾 checklist」逐項核對後 commit，回到 W1。

**波次收尾 checklist**（每個波次收尾前回到本節重讀，逐項打勾）：
- [ ] tasks.md：新增的 `[X]` 恰為本波次各 unit 回報完成的任務
- [ ] 最後一輪整合測試全綠；reviewer 全數 APPROVE；`completes=` 的 story validator 全數 PASS
- [ ] 有修正過 → 越界檢查與整合測試已在最後一輪修正後重跑
- [ ] `completes=` 中的 story 已更新 `stories.USk` 旗標（validated/reviewed/committed）
- [ ] `python3 $SKILL_DIR/scripts/task-plan.py close --state <FEATURE_DIR>/.sdd-workflow.json`
      （waves_done 加 1、移除 current_wave）——必須在 commit 之前
- [ ] `git add -A && git commit`，訊息 `feat(sdd): 實作波次 <k>（NNN）`，body 逐行：
      `tasks: <本波次勾選的 ID，逗號分隔>`（完成報告靠它核對涵蓋率）、每個完成的
      story 一行 `完成 USk：<story 標題>`、有的話加 `越界放行：<檔案> → <任務 ID>`、
      `合併衝突退回：<任務 ID>` 與 `撞到別條 lane：<檔案>`（完成報告據此統計漏判）
- [ ] `git status --porcelain` 為空
- [ ] `bash $SKILL_DIR/scripts/wave-worktree.sh clean <專案根> <NNN>`（單 unit 波次也跑，無害）
- [ ] `codegraph sync`（codegraph 可用時）

**降級回依序模式**：同一 feature 累計 2 個波次出現 W3 `conflict` 或 W5「撞到別條
lane」→ 集合對這個專案不夠可靠。AskUserQuestion 建議改回依序模式；同意 → 先讓
當下的波次照常收尾，再把 `parallel_plan.mode` 改為 `sequential`、`mode_reason` 記
原因，隨下一個 commit 入版控，剩下的 task 照「依序模式」執行。

**並行模式收尾**（W1 印出 `wave=none`）：派 `sdd-feature-validator`（依模板，story
ID＝`all`：全 feature 回歸）→ 需 PASS（FAIL → 通用規則 4 修正迴圈，上限 3 輪；
修正動到產品程式碼，PASS 後須再派 reviewer 覆審該批修正，雙向閉合同依序模式的
Polish）→ `steps.implement.done=true` → `auto-commit.sh after_implement` →
commit 驗證 → 最終 `codegraph sync`。
