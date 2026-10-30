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
| sdd-harness 並行模式（波次） | L7–L14 | 整合測試要認得預期紅燈；依賴、port、共用 CSS／DOM 約定都是 lane 間共用資源；空 diff 的收尾 task 不該獨占一波；verify 要讀狀態檔的 mode |
| skill 文件與範本的一致性 | L15、L16、L17 | 命名判準只留一處、不寫進受保護的原文；寫大檔的 agent 要有 Edit；交接包涵蓋欄要涵蓋所有錨點類別 |
| 執行環境 | L18 | sandbox 偶發擋瀏覽器啟動，重跑可過 |
| sdd-harness 並行模式（修正後重跑） | L19–L26 | 預期紅燈以對應實作是否完成判斷並交給 implementer；呼叫端不在同批時契約變更須相容；首波先建工具鏈；DOM 約定只由產生方登記；lane 用 lane-fix+；W6 全量排除預期紅燈 |

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

## L18：sandbox 偶發擋 subagent 啟動瀏覽器（2026-10-29）
- 情境：同一實驗，validator 在 subagent 內跑多瀏覽器 E2E 抽驗。
- 錯誤行為：其中一個瀏覽器啟動時報 `kill EPERM` 失敗；嘗試以關閉 sandbox 重跑被
  權限分類器拒絕。
- 正確行為：不繞過 sandbox；先單獨重跑該瀏覽器，仍失敗再回報使用者。這次重跑即
  通過。
- 證據：同一指令第一次 EPERM，稍後重跑通過。
- 狀態：未升格（屬環境問題，暫不寫進 skill）

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

## L7：並行波次的整合測試把「預期紅燈」當失敗（2026-10-29）
- 情境：首次以 sdd-harness 並行模式端到端跑完一個前端 feature（強制並行，19 個
  波次）。同一波次裡有測試先行（TDD red）的 task，對應實作排在後面的波次。
- 錯誤行為：W6 整合測試沒有「預期紅燈」的概念，這種波次必定判紅。靜態型別語言
  的紅燈測試還會讓型別檢查失敗，連帶 build 失敗，E2E 測試的 webServer 起不來，
  整套 E2E 回歸都跑不了；只能繞道（跳過型別檢查直接打包、手動起 preview server）。
- 正確行為：tasks.md 標了測試先行的 task，W6 要先列出本波次預期為紅的測試檔，
  判定時只把「非預期」的失敗算紅；E2E 的 build 指令要能排除尚未有實作的測試檔
  （或拆出不跑型別檢查的 build），不讓預期紅燈擋住其他回歸。
- 證據：19 個波次中多次遇到；每次都要人工判定哪些紅燈屬預期，並以替代指令跑 E2E。
- 狀態：已升格 → `skills/sdd-harness/references/implement-loop.md`#W1、W6、W7；`skills/sdd-harness/scripts/task-plan.py`（next 的 expected_red）；`skills/sdd-harness/agents/sdd-impact-analyzer.md`#Kind；`skills/sdd-harness/agents/sdd-feature-validator.md`#輸入

## L8：worktree 裡安裝的依賴不會合併回專案根（2026-10-29）
- 情境：同一實驗，首波 lane 在自己的 worktree 執行套件安裝（被 gitignore 的依賴
  目錄）。
- 錯誤行為：合併只帶回版控內的檔案，專案根沒有依賴目錄；W6 在專案根跑整合測試
  直接失敗，要先手動安裝依賴。
- 正確行為：合併後若 lockfile 有變更（或專案根缺依賴目錄），W6 前先在專案根執行
  依賴安裝；`wave-worktree.sh add` 已會把專案根的依賴目錄 symlink 進 worktree，
  所以應讓安裝發生在專案根，worktree 只引用。
- 證據：首波合併後第一次 W6 失敗，安裝依賴後重跑通過。
- 狀態：已升格 → `skills/sdd-harness/scripts/wave-worktree.sh`（missing_deps：add 中止、merge 警告）；`skills/sdd-harness/references/implement-loop.md`#W2、W3

## L9：「修到全綠」型 task 單獨占一個波次，diff 為空卻要跑完整閘門（2026-10-29）
- 情境：同一實驗，tasks.md 每個 story 尾端有「執行全部測試並修到通過」這類收尾
  task。
- 錯誤行為：plan 模式的 analyzer 處理不一，有的標低信心、有的記成共用資源、有的
  列出全部檔案。結果它與其他 task 全部衝突，單獨排成一個波次；實際 diff 為空，
  仍要跑一輪審查、驗收與 commit。
- 正確行為：寫入集合無法預知的收尾 task 不參與衝突判定，併入同 phase lane 的最後
  一步，或由波次收尾（W6 整合測試）吸收；analyzer 定義檔對這類 task 要有單一處理
  規則。
- 證據：至少 2 個波次只含這類 task，合併時 diff 為空。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-impact-analyzer.md`#Kind（gate）；`skills/sdd-harness/scripts/task-plan.py`（conflict、build）；`skills/sdd-harness/references/implement-loop.md`#0P c

## L10：熱點檔把多個 story 串成鏈，波次數多於 phase 數（2026-10-29）
- 情境：同一實驗，多數 story 都要修改同一個狀態管理檔（reducer）。
- 錯誤行為：這個檔案讓幾乎所有 story 兩兩衝突，排程只能一條接一條；波次數 19 比
  依序模式的 phase 數 10 還多。每個波次都要跑一輪閘門，總成本反而高於依序模式。
- 正確行為：模式判定除了估計加速，也要比較波次數與 phase 數，波次數較多時傾向
  依序模式；plan 階段若發現單一檔案被大多數 story 寫入，建議拆檔（每個 story 一個
  slice），或把該檔的改動集中到 Foundational。
- 證據：腳本預估加速 1.3×（低於 1.5× 門檻，判定依序），使用者為驗證流程強制並行；
  實際 19 個波次中只有 7 個有兩條 lane 同時跑。
- 狀態：已升格 → `skills/sdd-harness/scripts/task-plan.py`（模式判定加「波次數不多於 phase 數」、hot_files）；`skills/sdd-harness/references/implement-loop.md`#0P c、0P e

## L11：寫入集合不重疊，lane 之間仍有語意衝突（2026-10-29）
- 情境：同一實驗，兩條 lane 同時實作不同畫面，各自依設計稿（Prototype）實作樣式。
- 錯誤行為：兩條 lane 的寫入檔案不重疊，但各自實作了設計稿的同一個 CSS class：
  一個在組合後重複套用（兩層內距、兩層捲動容器），另一個全域版面 class 兩邊都
  以為對方會做，結果沒人負責。另有 E2E 斷言依賴另一條 lane 尚未寫出的 DOM 結構。
  審查與驗收各抓到一次，都在波次內修正。
- 正確行為：plan 模式除了檔案，也要把共用的 CSS class、全域樣式與 E2E 依賴的 DOM
  約定列為共用資源，指定唯一負責的 task；lane 之間的 DOM 約定寫進 contracts，讓
  reviewer 依約定核對。
- 證據：一次審查 MUST-FIX（重複的樣式容器）、一次驗收 FAIL（缺全域版面 class），
  修正後重跑皆通過。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-impact-analyzer.md`#Res（樣式、DOM 約定）；`skills/sdd-harness/references/implement-loop.md`#W7；`skills/sdd-harness/agents/sdd-code-reviewer.md`#輸入

## L12：E2E port 是並行時的共用資源（2026-10-29）
- 情境：同一實驗，兩條 lane 的 implementer 同時跑 E2E；波次收尾時 validator 與
  reviewer 也同時起 dev server。
- 錯誤行為：都用預設 port，互相撞到，出現無關實作的失敗或測到另一條 lane 的
  server。
- 正確行為：替每條 lane 與每個 validator／reviewer 分配不同的 port（例如由
  `wave-worktree.sh add` 寫入 worktree 的環境變數，或在派遣 prompt 指定），E2E
  設定讀環境變數決定 port 與 base URL。
- 證據：手動指定不同 port 後撞 port 的失敗消失。
- 狀態：已升格 → `skills/sdd-harness/references/implement-loop.md`#並行模式「E2E port」、W1、W2、W7；`skills/sdd-harness/scripts/task-plan.py`（next 的 ports）；sdd-implementer／sdd-feature-validator／sdd-code-reviewer 的輸入

## L13：修正迴圈的越界檢查只認本 unit 的 task，太嚴（2026-10-29）
- 情境：同一實驗，波次修正迴圈要修審查或驗收的發現。
- 錯誤行為：修正常需改同一 story 早先 task 建立的檔案，這些檔案不在本 unit 的
  寫入集合 W 裡；W5 越界檢查只對本 unit 的 task ID，每次都判越界，要逐一手動放行。
- 正確行為：修正迴圈的越界檢查改以「同一 story／phase 已完成 task 的寫入集合」
  為邊界；只有超出這個範圍的檔案才需放行，並記入越界放行清單。
- 證據：多次修正迴圈都需手動放行同 story 的地基檔案。
- 狀態：已升格 → `skills/sdd-harness/references/implement-loop.md`#W8；`skills/sdd-harness/scripts/task-plan.py`（next 的 fix+）

## L14：使用者指定模式只改狀態檔，`task-plan.py verify` 讀規劃檔而走錯分支（2026-10-29）
- 情境：同一實驗，腳本判定依序模式，使用者選擇強制並行；orchestrator 把狀態檔的
  mode 改為 parallel，parallel-plan.json 仍是 sequential。
- 錯誤行為：收尾的 `verify` 讀 parallel-plan.json 的 mode，用依序模式的規則核對
  並行模式的 commit，結果錯誤；只能手動以波次規則重算。涵蓋率統計也把 specs/ 下的
  設計文件算進「未涵蓋」。
- 正確行為：mode 只有一個權威來源——`verify` 以狀態檔的 mode 為準（或使用者指定
  時同步寫回規劃檔，並記 mode_reason）；涵蓋率統計排除 feature 的 specs/ 目錄。
- 證據：手動重算後實際變更 190 檔、未涵蓋 7（3.7%），依序模式過去實驗為 25–29%；
  7 檔中 2 檔是 specs/ 文件。
- 狀態：已升格 → `skills/sdd-harness/scripts/task-plan.py`（mode 子命令、verify --state、排除 feature 目錄）；`skills/sdd-harness/references/implement-loop.md`#0P e、降級回依序模式；`skills/sdd-harness/references/workflow-stages.md`#完成報告

## L19：預期紅燈以 phase 為粒度，已轉綠的測試也被豁免（2026-10-30）
- 情境：L7–L14 修正後重跑同一個前端 feature 的並行模式（強制並行，跑完 8 個波次）。
  `task-plan.py next` 依「測試先行 task 已完成且所屬 phase 仍有未完成 task」算 `expected_red`。
- 錯誤行為：測試對應的實作早已完成、測試已轉綠，只因同 phase 還有別的 task 沒做，仍留在
  清單裡；一個測試檔先由前一 phase 寫入、後一 phase 再追加新案例時，整檔被豁免，檔內原本
  通過的舊案例若回歸也會被放行。另外 W 中的測試輔助檔（非測試檔）也被列入。
- 正確行為：以「該測試 task 的讀取集合 R 中，仍有未完成 task 寫入的檔」判斷預期紅燈；只列
  測試檔；W6 判定時，清單內的檔若是本波次之前就已通過，失敗仍算紅。
- 證據：多個波次的清單含 3–4 個早已通過的測試檔；一次清單 7 檔中只有 2 檔真的在紅。全程
  靠主對話逐一手動核對失敗項，才沒漏掉回歸。
- 採用改法（獨立 judge 複核後）：next 改以「同 phase、寫入集合與該測試 R 相交的實作 task 仍未完成」判定，找不到對應實作才退回 phase 粒度；只列測試檔。不採「本波次前已通過者失敗算紅」——精準規則後只剩同 lane 內的窗口。以 8 個波次重算，清單與實際失敗一致（例：13 檔→3 檔）。
- 狀態：已升格 → `skills/sdd-harness/scripts/task-plan.py`（next_wave 的 still_red、TEST_FILE）；`skills/sdd-harness/references/implement-loop.md`#W1；`skills/sdd-harness/agents/sdd-impact-analyzer.md`#Kind

## L20：預期紅燈清單與替代 build 只交給閘門，implementer 不知道（2026-10-30）
- 情境：同上。W6 與 validator 會拿到 `expected_red`，以及「build 含型別檢查時改用不檢查的
  build 起 E2E」的作法；W2 派 implementer 時兩者都不附。
- 錯誤行為：implementer 每次都把別條 lane 的預期紅燈當異常回報，有的還說明「不是我造成
  的」；要跑 E2E 的 implementer 自行摸索出替代 build。收尾 task（修到全綠）若不知道哪些
  失敗屬他人，可能去改範圍外的測試。
- 正確行為：W2 派遣模板附 `expected_red` 與替代 build 指令，並寫明「這些檔的失敗不是本
  unit 的問題，不要修改」。
- 證據：每個波次的 implementer 回報都有一段在解釋他人的紅燈；收尾 task 的派遣由主對話臨時
  補上清單後才正常。
- 採用改法（獨立 judge 複核後）：照原提案；只附已 commit 的部分（`expected_red_base`，其他 lane 本波次才寫的檔在 worktree 裡看不到）。
- 狀態：已升格 → `skills/sdd-harness/references/implement-loop.md`#W2 派遣附件；`skills/sdd-harness/agents/sdd-implementer.md`#輸入；`skills/sdd-harness/scripts/task-plan.py`（expected_red_base）

## L21：契約變更沒有記錄既有呼叫端，合併後打壞已完成的 story（2026-10-30）
- 情境：同上。一個後段 story 的 task 把共用元件的 props 改成必填；元件唯一的既有呼叫端由前
  一個已完成的 story 建立，負責更新呼叫端的 task 排在更後面的波次。
- 錯誤行為：各 lane 單獨綠燈；合併後型別檢查在呼叫端失敗，已完成 story 的整合測試與一條
  E2E 也失敗。analyzer 的 C 欄只有 `symbol@路徑`，沒有呼叫端，腳本無從把呼叫端的修改排進
  同一波次，「改了契約、呼叫端尚未更新」的中間狀態必然壞掉。
- 正確行為：analyzer 對 C 一併列出既有呼叫端檔案（可放進該 task 的 R 或另一欄），腳本把
  「改契約的 task」與「寫呼叫端的 task」視為相依；做不到同波次時，要求契約變更保持向後相容
  （新參數選用），並在呼叫端 task 的驗收寫明「接線後收回相容寫法」。
- 證據：W6 抓到，以把新 props 改為選用的修正迴圈解決；reviewer 確認 C 漏列唯一呼叫端。
- 採用改法（獨立 judge 複核後）：原提案「視為相依」無效——兩個 task 本來就有 Dep，是波次在中間切開；greenfield 時呼叫端在規劃當下也還不存在。改以流程規則為主：呼叫端更新不在本次任務清單時，契約變更必須向後相容；W2 把 C 附給 implementer；reviewer 對不相容的變更判 MUST-FIX；analyzer 把既有呼叫端放進 R 作輔助。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-implementer.md`#輸入；`skills/sdd-harness/agents/sdd-code-reviewer.md`#輸入；`skills/sdd-harness/agents/sdd-impact-analyzer.md`#C；`skills/sdd-harness/references/implement-loop.md`#W2、W6

## L22：greenfield 首波與 Setup 同波次的 lane 沒有工具鏈可跑測試（2026-10-30）
- 情境：同上，專案從零開始，Setup phase 負責建立套件清單與安裝依賴。
- 錯誤行為：首波同時排了 Setup 與其他 phase 的 task；其他 lane 的 worktree 沒有套件清單、
  沒有依賴，寫好的測試無法執行，只能在專案外臨時搭環境驗證，或乾脆不驗。
- 正確行為：專案根沒有可用的測試工具鏈時，Setup（或至少建立工具鏈的 task）單獨成第一個
  波次；或排程時讓其他 task 相依於建立工具鏈的 task。
- 證據：首波 3 條 lane 中 2 條回報「無法執行測試」。
- 採用改法（獨立 judge 複核後）：不走 analyzer Dep（宣告衝突會爆量）。改為 `next --setup-first`：Setup 有未完成 task 時只排 Setup 一條 lane；同時修正「測試工具前置缺工具即停」與 Setup 建工具鏈的矛盾。
- 狀態：已升格 → `skills/sdd-harness/scripts/task-plan.py`（--setup-first）；`skills/sdd-harness/references/implement-loop.md`#測試工具前置、W1

## L23：「DOM 約定」資源在兩種情況下判定不當（2026-10-30）
- 情境：同上，plan 模式依 L11 新增的 `DOM 約定` 資源類別登記。
- 錯誤行為：(1) 只定義定位器、不斷言 DOM 的 E2E fixture，照字面要把所有產生該 DOM 的後段
  task 寫進 Dep，相依方向反了，analyzer 只能自行違反規則。(2) 測試先行的測試 task 與其實作
  task 登記同一個 DOM 約定，被判為資源衝突；同 phase 同 lane 時無害，跨 phase 則會多一條
  不必要的序列化。
- 正確行為：規則改成「斷言 DOM 的一方把產生方寫進 Dep；只定義定位器的 fixture 不必」；
  DOM 約定只由產生方登記為資源，使用方以 Dep 表達。
- 證據：analyzer 回報中有兩段在說明這兩種情況並請主對話裁決。
- 採用改法（獨立 judge 複核後）：照原提案；reviewer 改依 R／Dep 所指產生方的檔案核對使用方的選擇器。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-impact-analyzer.md`#Res；`skills/sdd-harness/agents/sdd-code-reviewer.md`#輸入；`skills/sdd-harness/references/implement-loop.md`#W7

## L24：worktree 的依賴目錄 symlink 在 git 顯示為 untracked，且寫入會穿透到專案根（2026-10-30）
- 情境：同上，`wave-worktree.sh add` 把專案根的 `node_modules` 以 symlink 帶進 worktree。
- 錯誤行為：`.gitignore` 的 `node_modules/`（結尾斜線只匹配目錄）不匹配 symlink，worktree
  的 `git status` 每次都出現 `?? .../node_modules`，implementer 與 reviewer 每次都要解釋；
  有 implementer 在其中暫放腳本，實際寫進了專案根的依賴目錄。
- 正確行為：add 時把 symlink 路徑寫進 worktree 的 `.git/info/exclude`；implementer 定義檔
  註明依賴目錄是共用的、不得寫入。
- 證據：幾乎每份 implementer 回報都有一句說明 untracked 的 node_modules。
- 採用改法（獨立 judge 複核後）：`info/exclude` 是全 worktree 共用的（沒有單一 worktree 專屬的 exclude）：add 在其中以獨立標記行加規則（ignore 規則不支援行尾註解），clean 連同下一行刪除；implementer 定義檔註明依賴目錄不得寫入。
- 狀態：已升格 → `skills/sdd-harness/scripts/wave-worktree.sh`（add、clean）；`skills/sdd-harness/agents/sdd-implementer.md`#環境注意

## L25：修正邊界 fix+ 的適用範圍沒寫清楚（2026-10-30）
- 情境：同上。`fix+` 是 L13 為 W8 修正迴圈加的邊界延伸。
- 錯誤行為：orchestrator 派收尾 task（同樣是「修到全綠」）時，把 `fix+` 也給了 lane 的
  implementer；其中一個檔正好在同波次另一條 lane 的 W 內，若被修改就會撞檔（這次 implementer
  沒動它，未實際發生）。
- 正確行為：寫明 `fix+` 只用於專案根的 W6／W8 修正；若要擴給 lane，腳本須先扣掉同波次其他
  lane 的 W 與 R。
- 證據：該波次的派遣 prompt 與另一 lane 的 W 有 2 檔重疊。
- 採用改法（獨立 judge 複核後）：文件其實已寫 fix+ 給 W8 用；真缺口是含收尾 task 的 lane 沒有可用邊界。next 另算 `lane-fix+`（fix+ 扣掉同波次其他 lane 的 W 與 R），W2 給含收尾 task 的 unit 用；fix+ 明定只用於專案根的 W6／W8。
- 狀態：已升格 → `skills/sdd-harness/scripts/task-plan.py`（lane_fix）；`skills/sdd-harness/references/implement-loop.md`#W1、W2

## L26：W6「全量測試」與實務不一致，E2E 實際留給 validator（2026-10-30）
- 情境：同上，plan.md 的測試含單元測試與 E2E。
- 錯誤行為：W6 規則寫「以 plan.md 選定的測試指令在專案根跑全量測試」；實際每個波次只跑
  單元測試、型別檢查與 lint，E2E 只在 story 完成的波次由主對話補跑或交給 validator。早期
  波次 E2E 全是預期紅燈，每波都跑成本高、訊號少。
- 正確行為：W6 明定分層——每波跑單元測試、型別檢查、lint；`completes=` 含 story 的波次，
  另跑已完成 story 的 E2E（回歸），預期紅燈的 E2E 不跑。
- 證據：8 個波次中 E2E 只在 2 個完成 story 的波次跑過；唯一一次合併後語意衝突，正是靠該
  波次補跑的已完成 story E2E 抓到（見 L21）。
- 採用改法（獨立 judge 複核後）：不採「只在完成 story 的波次跑 E2E」（會延後已完成 story 的回歸，而 L21 正是靠回歸 E2E 抓到）。改為每波跑全量但排除 expected_red：早期 E2E 自然不跑、後期每波跑已完成 story 的回歸；刪除「expected_red 通過也要記下」。
- 狀態：已升格 → `skills/sdd-harness/references/implement-loop.md`#W6

## L15：來源包的 token 命名規則與規格範本互相矛盾（2026-10-29）
- 情境：同一實驗，上游是含 Prototype 的來源包，plan 要從 Prototype 導入設計 token。
- 錯誤行為：`source-package.md` 寫「模式 B：由 plan 依用途命名」，
  `spec-source-template.md` 寫「模式 B：命名沿用 Prototype」。plan 階段兩邊各有
  依據，只能交給使用者裁決，最後採混合命名。
- 正確行為：兩份文件只留一個規則（或明定混合命名的判準），另一份引用它。
- 證據：plan review 閘門多出一個本不該需要的判斷點。
- 採用改法（獨立 judge 複核後）：命名屬 plan 層細節，不放在會抄進 spec、受機械檢查 7
  保護的五條原文；第 4 條模式 B 只寫「清單與命名見 research.md」，命名判準只留在
  來源包手冊：`:root` 有變數名的沿用，只有色碼等無名值的由 plan 依用途命名，兩套各自
  成組。範本升 v5，v4 舊文在檢查 7 也視為原文，避免進行中的 feature 誤判。
- 狀態：已升格 → `skills/sdd-harness/references/source-package.md`#3. 步驟 5 plan、
  `skills/sdd-harness/references/spec-source-template.md`#權威劃分 4（v5）

## L16：brief-writer 沒有 Edit，修改大檔只能用 Bash 拼接（2026-10-29）
- 情境：同一實驗，review 閘門要求修改已產出的導覽簡報；簡報是內嵌截圖的大型
  HTML。
- 錯誤行為：`sdd-brief-writer` 的工具只有 Read／Write／Grep／Glob／Bash，Write 要
  重寫整個大檔，agent 改用 Bash 拼接檔案，違反其定義檔「Bash 僅用於唯讀操作」。
- 正確行為：給 brief-writer 加 Edit，或讓截圖改成外部檔案引用、HTML 本體保持小，
  使 Write 重寫可行。
- 證據：修改簡報的派遣中出現 Bash 寫檔。
- 採用改法（獨立 judge 複核後，截圖部分經使用者裁決）：tools 加 Edit；「非首輪整檔重寫、
  不拼接片段」改為局部修改用 Edit、大幅改版才整檔 Write，不以 Bash 寫檔。根因是截圖以
  base64 內嵌：模型讀 base64 看不到圖、只花大量 token，Read 也會截斷長行。改為把用到的
  截圖 `cp` 到 `brief/screens/` 以相對路徑引用，發布時用多檔發布一併上傳；截圖一張一列
  直排（原本「並列」對照讓截圖小到看不清）。
- 狀態：已升格 → `skills/sdd-harness/agents/sdd-brief-writer.md`#輸入（非首輪）、#風格與技術契約、#硬約束、
  `skills/sdd-harness/references/review-gate.md`#閘門程序 3、`skills/sdd-harness/references/source-package.md`

## L17：交接包 index.md 涵蓋欄缺少「全域規則」「資料關聯性」（2026-10-29）
- 情境：同一實驗，spec 以 `[SB 全域規則 k]`、`[SB 資料關聯 k]` 錨點引用
  StoryBoard 的全域段落。
- 錯誤行為：make-mockup-harness 產出的 `index.md` 涵蓋欄只列 US-nn，機械檢查 8
  （錨點能在涵蓋欄找到）對這兩類錨點必定失敗，開發端只能改以 AGENTS.md 的錨點表
  解析，並回寫給 SA。
- 正確行為：`pack-handoff.sh` 產 `index.md` 時，也把 StoryBoard 的全域規則與資料
  關聯性等非 US 章節抓進涵蓋欄。
- 證據：回寫清單中有一筆專為此開的來源缺口。
- 採用改法（獨立 judge 複核後）：`pack-handoff.sh` 計算 StoryBoard「全域規則」「資料關聯性」
  兩節的頂層條列數，涵蓋欄加「全域規則 1–N、資料關聯 1–M」（用錨點字面，0 條不列）；
  取證方式欄、交接包 AGENTS.md 讀取順序、handoff.md 與 workflow-stages.md 的完成條件同步。
  sdd-harness 的機械檢查 8 不動。
- 狀態：已升格 → `skills/make-mockup-harness/scripts/pack-handoff.sh`（產 `index.md`）、
  `skills/make-mockup-harness/references/handoff-templates/AGENTS.template.md`#讀取順序
