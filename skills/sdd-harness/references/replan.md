# 重規劃閘門（re-plan）：實作中發現規劃不可行時的處置程序

僅由 SKILL.md 步驟 8R 進入時讀取。入口訊號與 roll-forward 原則寫在 SKILL.md
步驟 8R；狀態檔 `replan` schema 與完成準則寫在 workflow-stages.md「8R 重規劃」
節與「狀態檔 schema」節；中斷後的續跑優先權規則寫在同檔「續跑（resume）演算法」
規則 3——本文件只負責進入程序與迴圈執行細節，上述內容不在此重複。

## 進入程序

1. **與使用者確認**（AskUserQuestion）：先依 review-gate.md 產「選項與影響」
   裁決小頁（觸發點 `ruling`，不入版控；由 3 輪僵持裁決直接進入時已在該次
   裁決併問，不再另產），附發現的問題、受影響的 story／驗收條件清單、修訂
   方向建議。修訂若觸及**超過半數**既有 user story 的驗收條件
   → 同題附「改開新 feature（目前 feature 出具部分完成的完成報告，回步驟 3）」
   選項並建議之——同 feature 疊加方向性大改會讓 tasks.md 失去可讀性。
   使用者不同意進入 → 回原閘門依其裁決處理（放行／放棄 story 等）。
2. **清場**：進行中 story 的半成品（未 commit 的產品碼／測試碼）不得補 commit。
   AskUserQuestion 問使用者，預設建議**丟棄**（`git checkout -- <檔>` ＋刪除
   untracked 檔——重規劃後依新 task 重做，成本低於帶著過時半成品）；使用者要
   保留 → `git stash push -u -m "replan#<i> 半成品"`，重規劃完成後於吸收它的
   story 開工時 `git stash pop`（衝突由該 story 的實作處理）。清場後
   `git status --porcelain` 只剩狀態檔（與可能的 `.gitignore`）變更。
3. **狀態檔寫入**：`replan.active=true`、`iteration` 加 1（首次為 1）、
   `resume_at="spec"`、`reason`（一句話：實作中發現什麼）。不單獨 commit——
   隨本輪 `after_clarify` commit 入版控。

## 重規劃迴圈（依 `resume_at` 依序推進）

每站完成即把 `resume_at` 推進到下一站，時機與旗標同慣例：在該站 commit
**之前**更新。各站沿用原步驟（SKILL.md 步驟 4–7）的把關與 commit 驗證程序，
以下只寫與原步驟的**差異**。

### `spec`：修訂規格（本站不 commit）

- **直接編修 spec.md，絕不重跑 speckit-specify**——其 mandatory hook
  `speckit.git.feature` 會另開 feature branch 與目錄。
- 在 spec 的 Clarifications 章節新增「重規劃紀錄（第 <i> 輪）」小節：實作中
  發現什麼、決定改什麼、影響哪些既有 story——spec 要記錄的是**變更的決策**，
  不只是最終狀態。
- 人為 review 閘門（SKILL.md 通用規則 7，觸發點 `clarify`，「本輪變更」＝
  重規劃紀錄）→ 通過後 `resume_at="clarify"`。spec 修訂與簡報更新隨 clarify
  站的 commit 入版控。

### `clarify`：重跑釐清

- 依 SKILL.md 步驟 4 執行（sdd-spec-clarifier `spec-only` ＋ speckit-clarify
  inline）；派遣 prompt 附件註明「本輪聚焦重規劃修訂的章節與其漣漪」。
- 人為 review 閘門（通用規則 7，觸發點 `clarify`，「本輪變更」＝本站新增的
  Clarifications）→ `resume_at="plan"` → `after_clarify` commit 驗證。

### `plan`：重跑計畫

- 依 SKILL.md 步驟 5 執行。技術選型未變 → 不重問使用者（閘門附件改附
  plan.md 既有的選型與偏離紀錄）；修訂涉及選型 → 重新確認並記錄偏離理由。
- 派遣 speckit-plan 的 subagent 時**明確要求 plan 記錄「已建成現況」**：US1..k 已
  commit 的檔案、行為與可沿用部分——plan 與現實脫節＝重規劃白做。
- 人為 review 閘門（通用規則 7，觸發點 `plan`）→ `resume_at="tasks"` →
  `after_plan` commit 驗證。

### `tasks`：重跑任務（加法不變量）

- 重生前先留副本：`cp <FEATURE_DIR>/tasks.md <系統暫存目錄>/tasks.pre-replan.md`。
- 依 SKILL.md 步驟 6 派 subagent 執行 speckit-tasks，prompt **外加四條指示**：
  1. 已完成 phase 與其 `[X]` 勾選**原樣保留**；
  2. 既有 story ID **不得重編號**（狀態檔 `stories` 鍵與續跑演算法依賴它）；
  3. 變更一律以**新增**表達：新 task 掛既有未完成 phase，或新 story phase
     （US<n+1> 起）；修正已完成內容的 rework task 也是新 task，且每個新 task
     必須對得到修訂後 spec 的驗收條件（validator 閘門靠它驗收）。
  4. 舊任務因本輪修訂不再需要執行（如已被新方案取代）→ 加刪除線並註記
     `SUPERSEDED（replan#<i>）`，checkbox 改標 **`[X]`**（語意＝不再阻塞流程
     推進，非等同「依原計畫執行完成」，靠刪除線＋SUPERSEDED 文字與真正完成
     的 `[X]` 區分）。**不得**留 `[ ]`——`detect-stage.sh` 的完成判定只看
     checkbox 計數，未打勾的殘留任務會讓已全數完工的 feature 被誤判為
     `detected_stage=implement`（E2E 實測重現）。
- **勾選 diff 檢查**（對照重生前副本）：已完成的 `[X]` 零消失、既有 story
  phase 的標題與順序未變。違反 → 你直接手修 tasks.md 恢復不變量（保留合規的
  新增部分），**不重跑** speckit-tasks——重跑只會再抹一次。
- `resume_at="analyze"` → `after_tasks` commit 驗證。

### `analyze`：重跑一致性分析（收尾）

- 依 SKILL.md 步驟 7 執行（general-purpose 跑 speckit-analyze ＋
  sdd-spec-clarifier `full` 並行）——full 範圍會交叉檢查新 task、修訂後 spec
  與既有實作的一致性。
- CRITICAL 處理與修正同意走通用規則 7 閘門（觸發點 `analyze`）；處理完 →
  `replan.active=false`（`iteration`／`reason` 保留作歷史證據）→ 更新
  `steps.analyze` 計數 → `after_analyze` commit 驗證。
- 處理完、commit 之前一併刪除 `steps.implement.parallel_plan`（任務已變，
  規劃失效；回步驟 8 時由 implement-loop.md 步驟 1P 依新任務重做）。
- 回 SKILL.md 步驟 8 story 迴圈：從第一個未完成 story（含本輪新增）繼續。
  已完成 story 的旗標不回退；rework 內容由新 story／新 task 的正常閘門
  （影響邊界 → 實作 → 越界檢查 → validator → reviewer → commit）把關。

## 迴圈中的注意事項

- 重規劃期間 `steps.clarify.done`／`steps.analyze.done` 維持 true（**不回退**）
  ——「重跑中」由 `replan.resume_at` 表達，兩套機制不混用。
- 迴圈中斷後續跑：detect-stage.sh 輸出 `detected_stage=replan` 與
  `replan_resume_at=<站>`，從該站續作；dirty 的 spec／plan／tasks／狀態檔屬
  進行中產物，不套用一般 dirty tree 分類表（SKILL.md 步驟 0b 已有此分支）。
- 同一 feature 重規劃到**第 3 輪**仍未回到實作 → 停下問使用者是否改開新
  feature——反覆重規劃是需求不穩定的訊號（judgment-rubrics R6 模糊題），
  不是執行問題。
