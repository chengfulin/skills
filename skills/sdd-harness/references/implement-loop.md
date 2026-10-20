# 步驟 8 實作迴圈（/speckit.implement，逐 story 閘門）

僅由 SKILL.md 步驟 8 進入時讀取，**全程照本文件執行**；本文件是步驟 8 執行細節
（索引準備、測試工具前置、逐 phase 迴圈、越界放行、story 收尾 checklist）的唯一
版本。完成準則與不變量在 workflow-stages.md「8 實作」節；入口訊號與 8R 重規劃在
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

對 tasks.md 的每個 phase 依序（細節見 workflow-stages.md 的階段 8）：

1. **Setup / Foundational**：派 `sdd-implementer`（依模板：專案根絕對路徑 +
   phase 名稱 + feature 目錄 + speckit-implement SKILL.md 路徑；邊界＝該 phase
   任務描述涉及的檔案）→ 核對該 phase 全 `[X]` 且變更檔案未超出任務範圍 →
   派 `sdd-code-reviewer`（依模板；diff 範圍：上一個 commit 之後全部變更含
   untracked；註明 phase 名稱、無 story ID）→ 需 APPROVE（MUST-FIX 走通用規則 4
   修正迴圈）→ `git add -A && git commit -m "chore(sdd): 完成 <phase>（NNN）"` →
   `codegraph sync`（codegraph 可用時，下同）。基礎設施是全 feature 的地基，
   不設審查等於零把關入版控。
2. **每個 User Story phase**：
   a. **影響邊界**：從 tasks.md 該 phase 的任務描述與 plan.md 的檔案規劃**列出**
      預期新增／修改的檔案與 symbol 清單作為初步假設（**不執行 codegraph／grep
      掃描**——索引查證是 analyzer 的工作，主對話不下場、掃描原文不進主 context）；
      Agent tool 派 `sdd-impact-analyzer`（依模板：專案根絕對路徑 + story ID +
      feature 目錄 + 初步假設）取得**影響邊界報告**。greenfield 索引近空時報告
      很短，屬正常，不要因此跳過派遣。
   b. 派 `sdd-implementer`（依模板：專案根絕對路徑 + story ID + feature 目錄 +
      speckit-implement SKILL.md 路徑），限定「只做 Phase N（USk）的任務」，
      **並附上邊界報告的約束摘要**（預期新增/修改檔案、邊界外禁區）。
      它回報「受阻」或「越界候選」→ 先解決（裁決越界、修 spec 缺陷、問使用者）
      再重派續作，不要帶著未決事項前進。
   c. 越界檢查（雙重）：diff tasks.md，只有該 phase 的任務新增 `[X]`；且
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
   - [ ] tasks.md：該 phase 任務全數 `[X]`，且**只有**該 phase 新增 `[X]`
   - [ ] 最後一輪 validator 結論 PASS、reviewer 結論 APPROVE
   - [ ] 有修正過 → 越界檢查已在最後一輪修正後重跑
   - [ ] 狀態檔 story 旗標已更新（validated/reviewed/committed）——必須在 commit 之前
   - [ ] `git add -A && git commit -m "feat(sdd): 實作 <story 標題>（NNN, USk）"`
   - [ ] `git status --porcelain` 為空
   - [ ] `codegraph sync`（codegraph 可用時；讓下一個 story 的邊界分析基於最新索引）
3. **Polish**：派 `sdd-implementer`（依模板，限定 Polish；邊界＝該 phase 任務
   描述涉及的檔案）→ 全部任務 `[X]` → 派 `sdd-code-reviewer`
   （依模板；diff 範圍：Polish 的全部變更）→ 需 APPROVE → 派 `sdd-feature-validator`
   （依模板，story ID＝`all`：全 feature 回歸，逐 story 分節判定）→ 需 PASS
   （FAIL → 通用規則 4 修正迴圈，上限 3 輪，超過即問使用者；修正若動到產品
   程式碼，validator 複核 PASS 後**必須再派 reviewer 覆審該批修正**——鏡像
   8.2f 的回歸規則，未經覆審的修正不得進 after_implement commit；reviewer
   覆審若再引出產品程式碼修正，APPROVE 後須再派 validator（`all`）回歸——
   雙向閉合，兩個方向的複核均計入同一 3 輪上限）→
   `steps.implement.done=true` → `auto-commit.sh after_implement` → commit 驗證 →
   最終 `codegraph sync`。
