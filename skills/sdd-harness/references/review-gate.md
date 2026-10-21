# 人為 review 閘門：功能導覽簡報的產製、發布與提問程序

SKILL.md 通用規則 7 引用本文件；**閘門執行程序以本文件為唯一版本**，
簡報的內容規格與頁面契約在 `agents/sdd-brief-writer.md`（agent 定義檔），
狀態檔欄位與完成準則在 workflow-stages.md——三處不互相重複。

設計意圖：閘門上的人要決定「通過／需修改」，但 spec／plan 原文太長；純文字
摘要又讓沒接手過此功能的人拼不出全貌。簡報用圖像說明「要做什麼」，下半部把
本輪真正要人決定的事列成最多 3 個判斷點，AskUserQuestion 的題目直接對應這些
判斷點。spec.md 仍是唯一權威，簡報是入版控的中間產物（`<feature 目錄>/brief/`）。

## 觸發點表（只在下表列出的時機產製，其他時機不做）

| 觸發點 | 時機 | 簡報形式 | 派遣附件 | 判斷點聚焦 | 末題固定問法 |
|--------|------|----------|----------|------------|--------------|
| `spec` | 步驟 3 spec.md 建立後 | 首建 `brief/feature-brief.html`（概念圖＋流程圖；無「本輪變更」） | 無 | 驗收條件可否驗證、spec 未定義之處 | 通過 review／需修改 |
| `clarify` | 步驟 4 spec 依答案更新後；8R 的 `spec` 站（spec 修訂）與 `clarify` 站 | 同頁更新，「本輪變更」＝本輪 Clarifications 新增內容與被改動小節（8R 的 spec 站＝重規劃紀錄小節） | 新增的 Clarifications 條目、被改動的小節名 | 釐清答案是否讓驗收可寫、漣漪到哪些 story | 通過 review／需修改 |
| `plan` | 步驟 5 plan.md 建立後；8R 的 `plan` 站 | 同頁更新，新增架構圖；「本輪變更」＝技術選型與偏離 tech-standards | 使用者確認的選型、偏離項與理由 | 架構決策、規範缺漏或偏離 | 通過 review／需修改 |
| `analyze` | 步驟 7 兩份發現彙整後；8R 的 `analyze` 站 | 同頁更新，「本輪變更」＝發現表 | speckit-analyze 與 clarifier（full）的發現表 | CRITICAL／HIGH 的處置方案 | 修正方案：同意套用／調整 |
| `ruling` | 3 輪僵持裁決（錯誤處理「subagent 僵持」）、8R 入口確認（replan.md 進入程序 1） | 獨立小頁，寫系統暫存目錄，**不入版控** | 問題、各方立場、可選方案與你的建議 | 各方案的影響與風險 | 裁決選項（放行／調整規格／放棄 story／進入重規劃…） |

僵持裁決中使用者選「調整規格」而直接進入 8R 時，8R 入口確認**併入該次裁決**
（同一小頁、同一次 AskUserQuestion 附「改開新 feature」選項），不再另產一頁。
判斷點數量以 agent 定義檔為準（最多 3 個，加末題恰為 AskUserQuestion 單次上限
4 題；超出者寫者列為「次要疑點」，不入題）。

**不觸發**：步驟 6（tasks 無人為閘門）、步驟 8 逐 story 的 validator／reviewer
閘門（讀者要的是 PASS/FAIL 證據，不是概念圖）、步驟 4 釐清問答本身
（speckit-clarify 的前 5 題照原程序問，簡報在 spec 更新後才產）。

## 閘門程序（每個觸發點都走一遍）

1. **派 `sdd-brief-writer`**（Agent tool；依 SKILL.md 通用規則 4 模板填欄，
   對本 agent 的欄位值：範圍＝觸發點（`spec`／`clarify`／`plan`／`analyze`／
   `ruling`）、附件＝上表「派遣附件」，並**另加一欄「輸出檔絕對路徑」**——
   `spec`～`analyze` 為 `<專案根>/<feature 目錄>/brief/feature-brief.html`，
   `ruling` 為 `${TMPDIR:-/tmp}/sdd-brief-ruling-<feature>-<slug>.html`；
   模板沒有這欄，漏填寫者會拒收）。複核輪次另附前輪判斷點與使用者答案。
2. **收回報**：須有 `## 簡報結論` 結論行與「本輪判斷點」清單；回報無效或
   Agent 呼叫失敗 → 以原 prompt 重派一次；仍失敗 → **簡報不阻塞流程**：改以純文字
   重點條列（user story 與驗收要點／架構決策與偏離／發現表）完成本閘門，
   並明確告知使用者「本輪簡報產製失敗，改用文字摘要」。
3. **發布**：Read 該 HTML（Artifact 工具規定發布前必須通讀自己沒寫的檔案；
   agent 契約限 ≤400 行）→ Artifact 工具 `publish`，`file_path`＝該檔絕對路徑，
   `description` 一句話（feature 名＋本輪觸發點），首次另給 `icon`（如 `map`）。
   - 同一 session 內以**同一檔案路徑**再發布＝更新同一 URL（`clarify`／`plan`／
     `analyze` 皆如此）。
   - 跨 session（`resume` 後）：讀狀態檔 `brief.artifact_url`，先 Artifact `read`
     該 URL，再 `publish` 時帶 `url` 更新原頁；沒有該欄位或 read 失敗 → 發布為
     新 artifact，並更新狀態檔。
   - URL 首次取得或變更時寫入 `.sdd-workflow.json` 的 `brief.artifact_url`
     （schema 見 workflow-stages.md），隨本階段 commit 入版控。
   - **Artifact 工具不可用**（不在允許工具清單、或呼叫失敗）→ 不重試：把 HTML
     檔絕對路徑給使用者，請其以瀏覽器開啟，其餘程序不變。
   - `ruling` 小頁：檔案在暫存目錄、路徑不同＝獨立 artifact，不寫狀態檔。
4. **提問**：一次 AskUserQuestion 問完（judgment-rubrics R3 的格式；單次上限
   4 題）：前面各題＝回報的判斷點（選項照寫者給的方案，寫者的建議標
   「(Recommended)」並排第一），末題＝上表「末題固定問法」，其說明文字須寫明
   「判斷點答案將直接套用到文件，不再重發簡報」。給使用者 artifact 連結（或檔案路徑）
   與 spec／plan 檔案路徑；**不整份轉貼** spec／plan。
5. **依答案處置**（兩條路，依答案型態分流）：
   - **答案只是選既定方案**（A／B／C 其一，含 Recommended）且末題「通過」→
     由你直接套用到 spec／plan（照各步驟原本的修改方式）、同步簡報對應列
     （判斷點改記為已決事項）、以同一路徑重新發布，**不重派寫者、不重問**；
     接著依該步驟原程序更新狀態檔 → commit。E2E 實證：重派只會多一輪、
     回報「無新判斷點」。
   - **末題「需修改」、答案為自由文字、或套用答案時引出新的判斷點** → 修改
     後回到第 1 步重派（附前輪判斷點與答案）、重新發布與提問；無輪數上限
     （這是人為決策，不是 subagent 僵持）。
   - commit 時 `brief/` 隨階段 commit 入版控（spec-kit 的 auto-commit.sh 以
     `git add .` 暫存，1.0.5／1.0.13 實測；補救路徑用 `git add -A`，兩者都會納入）。
   - 回報的「與 spec 不一致」：屬簡報畫錯 → 重派修正後才發布；屬 spec 缺漏 →
     併入本輪判斷點問使用者。

## 產物歸屬與不變量

- `<feature 目錄>/brief/` 是 feature 的中間產物：`feature-brief.html` 每輪更新、
  與同輪的 spec／plan／狀態檔**同一個 commit** 入版控（不單獨 commit）；
  `README.md` 首輪建立後不再變動。歷史版本靠 git，不另存多份。
- 內容最終須與 spec.md 一致；接手者發現不一致時以 spec 為準並要求重生。
- 頁面依 Artifact 契約不含 `<!DOCTYPE>` 與文件骨架（發布時由平台包上）；直接
  用瀏覽器開啟入版控的檔案時可讀，但版面以 Artifact 發布版為準（brief/README.md
  已註明）。
- 續跑時 `brief/` dirty 的歸屬見 workflow-stages.md「續跑演算法」分類表。
- 簡報不取代任何 subagent 閘門：clarifier／validator／reviewer 的否決效力
  不因簡報存在而改變（SKILL.md 通用規則 4）。
