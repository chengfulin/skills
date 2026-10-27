# 教訓紀錄

本 repo 的 skill 在回歸測試與可行性驗證中踩到的問題。只記通則，不記實驗對象的
專案名、feature 編號、程式碼或業務內容——實驗素材只留在 session 暫存目錄。

本檔分兩節：**現行**（未升格，仍需靠人記住）與**歸檔**（已升格進 skill 規則檔，
內容保留作為脈絡與證據）。新條目 append 到「現行」節尾端；升格後整段搬到歸檔節
尾端，狀態改 `已升格 → <檔案>#<小節>`。

條目格式：

```markdown
## L<流水號>：<一句話標題>（<YYYY-MM-DD>）
- 情境：做什麼任務、什麼條件下踩的
- 錯誤行為：實際發生什麼
- 正確行為：應該怎麼做
- 證據：能重現判斷的最小資訊（數字、指令、輸出），不含實驗對象資訊
- 狀態：`未升格`｜`已升格 → <檔案>#<小節>`｜`已過時（<原因>）`
```

**升格判準**：同類問題第 2 次出現，或單次就造成功能落差，就提案寫進對應 skill。

## 同類索引

| 主題 | 條目 | 一句話 |
|------|------|--------|
| sdd-harness 的 context 用量 | L2、L3、L4、L5 | plan／tasks 不留主對話；大 story 分批；新任務派新 agent；上游資料靠索引與錨點定範圍 |
| 規格與上游資料的一致性 | L1、L5 | 設計稿每個範例都要比對；版型看截圖不抽文字；範圍超標是上游問題，反饋不砍 |
| 驗證實驗的方法 | L6 | 知道答案的 orchestrator 不能替被測流程出題 |

---

## 現行（未升格）

## L6：知道原版答案的 orchestrator 在派遣 prompt 裡洩漏提示（2026-10-20）
- 情境：以 sdd-harness 重做一個已上線的 feature，比較流程能否獨立得到原版的
  決策。orchestrator 事先讀過原版規格，撰寫類步驟改派不知情的 subagent 執行。
- 錯誤行為：派 clarify 第二段時，orchestrator 在 prompt 舉了兩個「可能的後續
  議題」當例子，而這兩個正是原版後來的裁決點。被測流程因此「找到」了它們，
  結果無法當作流程能力的證據。
- 正確行為：派遣 prompt 只給流程輸入（檔案路徑、使用者已給的答案），不舉例、
  不暗示方向。發現洩漏就還原產物、改派全新 agent 重跑。乾淨重跑後，流程仍自行
  提出相同議題，另多找到一處原版漏改的文案。
- 證據：同一階段兩次執行，第一次 prompt 含例子，第二次不含；第二次的 6 個
  判斷點涵蓋原版所有後續裁決。
- 狀態：未升格（屬實驗方法，不屬任何 skill 的規則）

---

## 歸檔（已升格）

## L1：clarifier 沒有逐例比對設計稿，漏掉「規格要求與範例不一致」（2026-10-20）
- 情境：以 sdd-harness 重做一個報告輸出類 feature。spec 規定某欄位每格的末行
  必有一段說明；上游設計稿給了多個範例。
- 錯誤行為：clarifier 只對照憲章與 spec 內部一致性，沒有看設計稿。設計稿裡只有
  一個範例有那段說明，這個矛盾正是原版 PM 裁決「移除該段」的起點；漏掉它之後，
  重做的結果符合需求文字，但與原版有 6 項功能落差（輸出行數、送進模型的素材、
  內建提示、設定頁文案、設計稿同步等）。
- 正確行為：clarifier 要掃 `.specify/context/` 的上游資料，對每一個範例都檢查
  結構與必填元素；來源彼此不一致列 HIGH 並請使用者裁決；spec 的「明確不含」不能
  當成略過衝突的理由。改版後重跑，clarifier 提出了這個矛盾，後續連帶議題也由
  流程自行找出。
- 證據：改版前後各跑一次 clarify；改版後的審查多用約 27k token（55k → 82k）。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-spec-clarifier.md`#審查程序 5

## L2：plan 等撰寫類步驟留在主對話，主對話會在流程中段被壓縮（2026-10-20）
- 情境：同一實驗，大型既有專案。即使 specify～tasks 都改派 subagent 執行，
  主對話到流程結束仍累積約 310k token，主要來自約 60 份 subagent 回報。
- 錯誤行為：原規則要求 specify、clarify、plan、tasks 在主對話 inline 執行。
  照做的話，plan（subagent 實測 175k）與 specify（約 110k）會讓主對話超過
  600k，後段閘門判斷要在壓縮後的 context 上進行。
- 正確行為：plan、tasks 改派 general-purpose subagent，主對話只拿回產出清單與
  待裁決事項；specify、clarify 要與使用者往返，留在主對話。
- 證據：各階段 subagent 結束時的 token 數（plan 175k、specify 101k～117k、
  tasks／analyze 約 90k～105k）。
- 狀態：已升格 → `skills/sdd-harness/SKILL.md`#通用規則 1、步驟 5、步驟 6

## L3：一個 story 要改的檔案太多時，implementer 會撐滿 context（2026-10-20）
- 情境：同一實驗的第一個 user story 改了 20 個檔，其中產生器約 4,500 行、
  對應測試檔超過 5,000 行。
- 錯誤行為：單一 implementer 做完整個 story，用了約 208k token、80 次工具呼叫，
  是全流程最接近上限的 agent。
- 正確行為：邊界報告的預期檔案超過 12 個，或含超過約 3,000 行的檔案時，依任務
  ID 分批，每批派新的 implementer；越界檢查、驗收與審查仍以整個 story 做一次。
- 證據：同一流程其他 story 的 implementer 多在 100k 以下。
- 狀態：已升格 → `skills/sdd-harness/references/implement-loop.md`#步驟 2b

## L4：把新任務交給已完成任務的 agent，context 只增不減（2026-10-20）
- 情境：同一實驗，plan 的 subagent 完成後，orchestrator 用 SendMessage 讓它接手
  analyze 發現的修正；決策模擬 agent 也跨多個閘門重複使用。
- 錯誤行為：plan agent 從 175k 漲到 211k；決策模擬 agent 每過一個閘門多一截
  （50k → 81k）。
- 正確行為：跨階段或換任務一律派新 agent，只附必要的檔案路徑與前輪結論；同一
  任務的續作才續用原 agent。
- 證據：同上各 agent 的 token 數。
- 狀態：已升格 → `skills/sdd-harness/SKILL.md`#通用規則 8

## L5：上游資料目錄很大，clarifier 沒有可計算的讀取範圍，只能靠猜或靠砍（2026-10-20；2026-10-21 修訂）
- 情境：同一實驗的 `.specify/context/` 約 9MB，含 PDF、試算表與單檔大型 HTML
  設計稿。
- 錯誤行為：clarifier 定義檔沒規定怎麼找來源，也沒規定各媒材怎麼取證。這次 agent
  自行略過 PDF，但沒在回報中說明略過了什麼。報告版型與前端畫面若只靠抽出的
  文字比對，看不到哪些元素實際顯示。
- 初版對策（已撤回）：「深入比對最多 8 個來源檔，依相關度挑選」。問題：上限只是
  減少掃描，沒有讓範圍變正確；掃到爆的真正訊號是上游沒索引、或單一 story 範圍
  太大，該反饋上游整理，不該往下砍。
- 正確行為：讓讀取範圍可計算——來源版本目錄有 `index.md`（每檔的媒材、取證方式、
  涵蓋的 US／畫面／章節），spec 每條 FR／AC 帶來源錨點，clarifier 依索引與錨點取
  片段、不掃目錄；錨點缺失或範圍對照的畫面沒被引用都列 HIGH。8 改為絆線（每 story
  計、單位是 index.md 索引列）：錨點太粗或超過 8 列，該 story 本輪不比對、列 HIGH 問
  使用者（補索引與錨點、或拆 story），不挑一部分比對。8 沿用舊上限無依據，回報附每
  story 的錨點目標數與索引列數，累積後再修。媒材取證規則
  （截圖首選、HTML 不整份 Read、PDF 只看相關頁影像）保留——那是證據品質，不是範圍。
- 證據：clarifier 改版前後的 token 數與回報內容；類比 codegraph——程式碼有
  symbol→edge 的索引才有有界查詢，規格要有 FR→錨點的邊才有有界比對。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-spec-clarifier.md`#審查程序 5、
  `skills/sdd-harness/SKILL.md`#步驟 3、
  `skills/sdd-harness/references/spec-source-template.md`#錨點慣例、
  `skills/make-mockup-harness/scripts/pack-handoff.sh`（產 `index.md`）
