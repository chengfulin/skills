# 步驟 8 實作迴圈（/speckit.implement，逐 story 閘門）

僅由 SKILL.md 步驟 8 進入時讀取，**全程照本文件執行**；本文件是步驟 8 執行細節
（索引準備、測試工具前置、tasks.md 勾選、逐 phase 迴圈、並行規劃、越界放行、
story 收尾 checklist）的唯一版本。完成準則與不變量在 workflow-stages.md「8 實作」節；入口訊號與 8R 重規劃在
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

對 tasks.md 的每個 phase 依序（細節見 workflow-stages.md 的階段 8）：

1. **Setup / Foundational**：派 `sdd-implementer`（依模板：專案根絕對路徑 +
   phase 名稱 + feature 目錄 + speckit-implement SKILL.md 路徑；邊界＝該 phase
   任務描述涉及的檔案）→ 依回報勾選 tasks.md → 核對該 phase 全 `[X]` 且變更檔案
   未超出任務範圍 →
   派 `sdd-code-reviewer`（依模板；diff 範圍：上一個 commit 之後全部變更含
   untracked；註明 phase 名稱、無 story ID）→ 需 APPROVE（MUST-FIX 走通用規則 4
   修正迴圈）→ `git add -A && git commit -m "chore(sdd): 完成 <phase>（NNN）"` →
   `codegraph sync`（codegraph 可用時，下同）。基礎設施是全 feature 的地基，
   不設審查等於零把關入版控。
1P. **並行規劃（觀察期：只產出分組建議，執行仍逐 story 依序）**：
   Foundational（tasks.md 沒有此 phase 則 Setup）commit 並 `codegraph sync` 之後、
   第一個 story 開工之前執行；未完成的 story 少於 2 個、或狀態檔已有
   `steps.implement.parallel_plan` 且其 `stories` 涵蓋全部未完成 story → 跳過。
   a. 在**同一則訊息**並行派 `sdd-impact-analyzer`，每個未完成 story 一個（依模板：
      專案根絕對路徑 + story ID + feature 目錄 + 模式 `plan`；不附初步假設）。
   b. 依各 story 的集合兩兩判定（路徑字串比對，不重新掃描）。任一成立即為**衝突**，
      記下類型與證據（一行）：
      - `寫入`：兩者寫入集合有同一檔案；
      - `相依`：一方寫入集合的檔案／symbol 出現在另一方讀取集合；
      - `資源`：共用資源有同一項（同類別且資源識別相同，migration 一律視為相同）；
      - `契約`：一方的契約變更 symbol 出現在另一方的寫入或讀取集合，或另一方
        新增了該契約的實作類別——文字上不衝突、合併後才編譯失敗的那一類；
      - `宣告`：任一方宣告相依另一方。
      優先順序：spec 的 P1（MVP）story 自成最前面的群組，其餘 story 的優先順序
      只決定執行與合併順序，不構成衝突。任一方信心「低」→ 該 pair 一律記為
      衝突（類型 `未定`），寧可錯殺。
   c. 分組：依 tasks.md 的 story 順序逐一放入，story s 的群組編號＝1＋（與 s
      衝突的前面 story 的最大群組編號；無則為 0）。P1 story 先在彼此之間依此規則
      分組；其餘 story 的群組編號下限＝P1 的最大群組編號＋1。宣告相依指向後面的
      story（順序矛盾）→ 不分組，回報使用者這是 tasks.md 的排序問題。
   d. 寫入狀態檔 `steps.implement.parallel_plan`（schema 見 workflow-stages.md），
      `git add -A && git commit -m "chore(sdd): 完成並行規劃（NNN）"`——立即
      commit，避免狀態檔變更混進下一個 story 的越界檢查。
   e. 向使用者回報（≤15 行）：分組、衝突清單（類型＋一行證據），並註明「目前
      仍依 tasks.md 順序逐 story 執行，本結果供評估並行實作用」。不設閘門。
   之後照步驟 2 逐 story 執行；1P 的集合**不取代**步驟 2a 的邊界報告（前面 story
   commit 後程式碼已變，邊界報告必須重做）。
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
