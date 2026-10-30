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
| skill 文件與範本的一致性 | L15、L16、L17 | 來源包命名規則與規格範本矛盾；brief-writer 工具與職責不符；交接包 index.md 涵蓋欄不全 |
| 執行環境 | L18 | sandbox 偶發擋瀏覽器啟動，重跑可過 |

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

## L15：來源包的 token 命名規則與規格範本互相矛盾（2026-10-29）
- 情境：同一實驗，上游是含 Prototype 的來源包，plan 要從 Prototype 導入設計 token。
- 錯誤行為：`source-package.md` 寫「模式 B：由 plan 依用途命名」，
  `spec-source-template.md` 寫「模式 B：命名沿用 Prototype」。plan 階段兩邊各有
  依據，只能交給使用者裁決，最後採混合命名。
- 正確行為：兩份文件只留一個規則（或明定混合命名的判準），另一份引用它。
- 證據：plan review 閘門多出一個本不該需要的判斷點。
- 狀態：未升格

## L16：brief-writer 沒有 Edit，修改大檔只能用 Bash 拼接（2026-10-29）
- 情境：同一實驗，review 閘門要求修改已產出的導覽簡報；簡報是內嵌截圖的大型
  HTML。
- 錯誤行為：`sdd-brief-writer` 的工具只有 Read／Write／Grep／Glob／Bash，Write 要
  重寫整個大檔，agent 改用 Bash 拼接檔案，違反其定義檔「Bash 僅用於唯讀操作」。
- 正確行為：給 brief-writer 加 Edit，或讓截圖改成外部檔案引用、HTML 本體保持小，
  使 Write 重寫可行。
- 證據：修改簡報的派遣中出現 Bash 寫檔。
- 狀態：未升格

## L17：交接包 index.md 涵蓋欄缺少「全域規則」「資料關聯性」（2026-10-29）
- 情境：同一實驗，spec 以 `[SB 全域規則 k]`、`[SB 資料關聯 k]` 錨點引用
  StoryBoard 的全域段落。
- 錯誤行為：make-mockup-harness 產出的 `index.md` 涵蓋欄只列 US-nn，機械檢查 8
  （錨點能在涵蓋欄找到）對這兩類錨點必定失敗，開發端只能改以 AGENTS.md 的錨點表
  解析，並回寫給 SA。
- 正確行為：`pack-handoff.sh` 產 `index.md` 時，也把 StoryBoard 的全域規則與資料
  關聯性等非 US 章節抓進涵蓋欄。
- 證據：回寫清單中有一筆專為此開的來源缺口。
- 狀態：未升格

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
