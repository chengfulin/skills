# 模型調度守則

給主對話（orchestrator／維護 session）的派工規則：誰下場、派給哪個模型、
用什麼 effort、失敗怎麼升降級、回報怎麼收。判斷類準則（何時升級、何時算完成）
在 `judgment-rubrics.md`；派工 prompt 模板在 `delegation-templates.md`——
本文不重複那些內容。

## 0. 環境事實基準（2026-07-29 查證自 code.claude.com/docs；2026-10-01 複查 model 解析順序與巢狀深度）

| 事實 | 值 |
|------|-----|
| 模型別名 | `haiku`／`sonnet`／`opus`／`fable`，浮動指向該系列官方推薦版本、隨升級更新；規則與 frontmatter 一律用別名，不釘完整 ID |
| subagent frontmatter | 支援 `model:`（別名／完整 ID／`inherit`，預設 inherit）與 `effort:`（low／medium／high／xhigh／max） |
| 逐次覆寫 | 派遣時可逐次覆寫 **model**（只有 Agent 工具的 model 參數；解析順序＝model 參數 → frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → 主對話模型，六個 sdd agent 皆有 `model` 欄，該環境變數對它們無效）；**effort 無法逐次覆寫**，只能在 agent 定義檔設 |
| /effort | 內建指令，session 層級；值 low／medium／high／xhigh／max |
| subagent 巢狀 | 允許（tools 需列 Agent；預設最多主對話以下 3 層，`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 可調）——本 harness 不使用，保持單層好追蹤 |

**Claude Code 升級後**，上表任何一格存疑就重查官方文件；查證結果更新本表。不要憑記憶沿用。

## 1. 指揮官不下場

主對話的 context 是整條流程的工作記憶，被大量原文灌爆＝後段必然失焦。
**主對話只做：決策、彙整結論、套用修正、commit、與使用者互動。**
出現下列任一情況，一律派 subagent、只取回結論：

| 觸發條件 | 派給 |
|---------|------|
| 需通讀 3 個以上檔案或任何單檔 >400 行才能回答 | 搜尋／研究型 subagent（回結論與 檔案:行號） |
| grep／codegraph 掃描（結果數未知） | 搜尋型 subagent 或 sdd-impact-analyzer |
| 查網頁／查官方文件 | 研究型 subagent（附來源 URL） |
| 對 3 個以上檔案做同模式修改 | 實作型 subagent（給明確 pattern 與檔案清單） |
| 唯讀分析、產報告（如 speckit-analyze） | general-purpose subagent |

例外（主對話可以自己做）：讀單一小檔確認一個事實、跑一條指令看結果、
套用 subagent 已指出 檔案:行號 的修正，以及 **speckit 步驟 2–6 的 inline 執行**
——spec-kit 0.8.17 的刻意取捨（speckit skill 必須照文件逐字執行，見
SKILL.md 通用規則 1）。步驟 7（analyze）與步驟 8（implement）已分別派 general-purpose
與 sdd-implementer，不在此例外內。

## 2. 模型 × effort 對照表

**預設 sonnet、不另指定**：派 subagent 時 model 一律用別名（§0，不釘版本），
沒有下表理由就是 `sonnet`（或 agent 定義檔的預設）。只在有明確理由時才指定
家族，四族只選其一：`haiku`（省成本）、`sonnet`（預設）、`opus`（高價值判斷）、
`fable`（**只作主對話模型**，由使用者選擇；不派給任何 subagent）。

| 任務型態 | model | effort | 備註 |
|---------|-------|--------|------|
| 標準實作、寫測試、一般研究、搜尋／盤點、語意搜尋 | sonnet（預設） | medium–high | 大多數工作，不需理由 |
| 審查、對抗式驗證、影響分析 | sonnet | high | sdd 審查者已寫死在 frontmatter，見 §3 |
| 明確低價值、可機械驗證的大批次（套已知 pattern、格式檢查、重新命名），且接受錯 1 次即整批重做 | haiku | low–medium | 指定的理由只有省成本；錯 1 次直接升 sonnet（見 §4） |
| 架構取捨、難 bug、多方案評審的裁判、規格仲裁 | opus | high–xhigh | 一次性、高價值的判斷；subagent 的上限 |
| 主對話（orchestrator） | 使用者所選（含 fable） | 使用者所選 | 不下場（§1）；fable 只在此 |

effort 無法逐次覆寫（§0）：需要不同 effort 的常態任務，在 agent 定義檔裡設好；
臨時需求就接受該 agent 的預設。

## 3. sdd-harness 六個 subagent 的預設與覆寫

| agent | frontmatter | 理由 |
|-------|------------|------|
| sdd-spec-clarifier | `model: sonnet` + `effort: high` | 憲章衝突推理吃判斷力。**固定下限**：主模型是 haiku 時審查者不跟著降級，避免同級互相背書 |
| sdd-code-reviewer | `model: sonnet` + `effort: high` | 同上（合規＋漣漪判斷） |
| sdd-feature-validator | `model: inherit` | 執行型（跑測試、逐條核對），主模型等級即可 |
| sdd-impact-analyzer | `model: inherit` | 執行型（索引查詢、清單比對） |
| sdd-implementer | `model: inherit` | 撰寫型（實作與主模型同級；品質由 validator／reviewer 閘門把關） |
| sdd-brief-writer | `model: sonnet` + `effort: high` | 撰寫型但**不下場實作**：把 spec／plan 轉成圖像簡報與判斷點，吃的是判斷力不是產能；固定 sonnet 讓簡報成本可預期、且不隨主模型升降（使用者決策，2026-09-29） |

覆寫規則（逐次，用 Agent 工具的 model 參數）：
- story 涉及**安全、金流、資料刪改、對外 API 破壞性變更** → 該 story 的 reviewer
  覆寫為 `opus`。
- 主對話模型是 **haiku** → validator 與 implementer 覆寫為 `sonnet`
  （驗收判定與程式撰寫的品質下限）。
- 主對話模型比 sonnet 強、且該 story 無上述風險 → 不覆寫，用預設即可。

## 4. 升降級路徑

1. **haiku 錯 1 次** → 不重試，直接升 sonnet **重做整批**（含 haiku 已做的部分
   ——它的「已完成」不可信），並把錯誤模式寫進新 prompt。
2. **sonnet 同一子任務連錯 2 次且原因不同** → 帶完整失敗軌跡升 opus，
   用 `delegation-templates.md` T6 模板交接（原任務照抄、兩輪失敗原文、已排除、
   目前假設）。
3. **opus 仍解不了** → 停下問使用者：附失敗軌跡與你的建議選項。不存在第四次嘗試，
   subagent 也不升 fable（§2：fable 只作主對話模型）；使用者可選擇改由主對話親自處理。
4. **降級**：opus／sonnet 解出可複製的模式後，把模式寫成明確步驟（含判斷分支），
   降回 haiku 批次套用（這是 §2 指定 haiku 的正當理由）；套用結果抽查 2 件
   （fresh context），全對才繼續。
5. **重試上限**：同一方法最多 2 輪。第 2 輪仍失敗＝方法錯了，走升級或換路
   （訊號判準見 judgment-rubrics.md R1／R4），不是第 3 輪。
   計數單位注意：SDD story 的「修正迴圈上限 3 輪」計的是**閘門輪數**
   （修正→複核的次數），本條的 2 輪計的是**同一方法**的嘗試次數——兩者銜接：
   story 修正走到第 3 輪時，**必須**換方法或升級模型，同一方法不做第三次。

## 5. 回報合約（收 subagent 報告的標準）

- 只收**結論與位置**（檔案:行號），不收過程敘事；長產物（完整清單、log、diff
  佐證）落檔到系統暫存目錄、回傳路徑。
- sdd 各 agent 的上限已寫進各定義檔（正文 ≤80 行；brief-writer ≤25 行）；臨時派遣的 subagent 在
  prompt 裡明訂上限（搜尋 ≤20 行、實作／研究 ≤30 行，見 delegation-templates.md）。
- 回報缺結論行（PASS/FAIL、APPROVE/MUST-FIX、找到/沒找到）→ 視為無效回報：
  重派一次，再失敗視同該閘門 FAIL（SKILL.md 錯誤處理），**不得腦補結論**。
- 回報**超長**（超過該 agent 合約上限）但內容有效 → 要求它依合約重整一次
  （結論不變、溢出落檔回傳路徑），**不要照單全收**灌進主對話。

## 6. 驗證不自驗（調度面的落實）

產出者與驗收者必須是**不同 context**（判準與正反例見 judgment-rubrics.md R5）：

- 檔案／規則 → 派 fresh-context agent read-back（不給撰寫脈絡）。
- 程式碼 → validator 執行測試與實際操作（sdd 流程已內建）。
- 高風險判斷 → 第二意見（不給第一個結論）或多答案評審；兩者矛盾 → 升級或問使用者。
- 驗收 agent 的 model 不得低於產出 agent（haiku 驗 sonnet 的產出＝沒驗）。
  例外：§3 把 sdd 審查者固定為 sonnet + high 是**判斷力下限、不是上限**——
  主對話（產出者）模型高於 sonnet 時，是否升級審查者依 §3 的覆寫規則
  （風險 story 才升 opus），不因本條自動升級。
