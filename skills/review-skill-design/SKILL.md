---
name: review-skill-design
description: 檢核指定的 skills 與 agents 是否過度設計：是否造成 context 浪費或不必要的 tool_use 輪數，以及 opus 等級的模型是否足以理解執行並取得預期結果。以 reviewer 與 judge 兩個獨立 subagent 交叉把關，只提供建議供 review，不修改檔案。當使用者要「檢核／審查某些 skill 或 agent 的設計」、「看這個 skill 有沒有過度設計」、「評估 skill 對 opus 夠不夠清楚」時使用。
argument-hint: <要檢核的 skill／agent 名稱或路徑，以空白分隔>
allowed-tools: Read, Bash, Glob, Grep, Agent
model: opus
---

幫我分析檢核以下指定的 skills 與 agents 是否有過度設計，造成 context 浪費或者不必要的 tool_use 輪數，以及對於 model opus 是否足夠理解執行取得預期結果。
先不要修改，僅先提供建議讓我 review。

要檢核的 skills & agents: $ARGUMENTS

## 做法

你是主對話，只做三件事：解析目標、派工、彙整報告。**不自己審、不修改任何檔案。**
審查由 **reviewer** 做，裁決由 **judge** 做，兩者是不同 context（產出者不當自己的驗收者）。

### 1. 解析目標

把 `$ARGUMENTS` 的每個項目解析成**一個 target**，依序找：

1. 絕對或相對路徑（目錄或檔案）
2. `~/.claude/skills/<名稱>/`（skill）
3. `~/.claude/agents/<名稱>.md`（agent）
4. 目前 repo 的 `skills/<名稱>/`

symlink 以 `readlink -f` 還原成真實路徑。target 的邊界：

- skill target ＝ 該目錄全部（`SKILL.md`、`agents/`、`references/`、`scripts/`…），skill 與它專用的 agents 視為一體檢核。
- agent target ＝ 單一 `.md` 檔。
- agent 的真實路徑若已落在某個 skill target 目錄內（它是該 skill 的專用 agent），併入該 skill target，不另派。
- target 名稱＝skill 目錄名，或 agent 檔名去掉 `.md`。
- 找不到的項目列出已查過的位置，繼續處理其他 target；`$ARGUMENTS` 為空或全部找不到才停下問使用者。

### 2. 派 reviewer（每個 target 一個，同一則訊息平行派出）

`Agent`，`subagent_type: general-purpose`，`model: opus`。reviewer 必須是 opus：
Read-back 就是「opus 讀不讀得懂」的直接取樣，換低階模型做不構成證據。
effort 無法逐次覆寫，隨 session 的 `/effort`，建議 high 以上。prompt：

```
【角色】你是 skill／agent 設計的 reviewer。唯讀：不得修改 target 的任何檔案，只能寫 scratchpad。
       對象：<target 真實路徑>（<skill／agent>）。
【目標】找出過度設計：(a) context 浪費——載入了用不到或重複的內容；
       (b) 不必要的 tool_use 輪數——可以合併、省略或用一次呼叫完成的步驟；
       (c) opus 理解風險——規則含糊、互相衝突、前提藏在別處、照做會拿不到預期結果。
【做法】先讀完 target 內**全部**檔案（含 agents/、references/ 被 SKILL.md 引用的檔）；
       量化：各檔行數、SKILL.md 直接或間接要求載入的檔案數與總行數、
       主路徑（最常見的一次執行）估計的 tool_use 輪數與其中可省的輪數。
【Read-back】用不超過 10 行寫下「這份 skill／agent 要我做什麼、完成的判準是什麼、
       我讀完仍不確定的地方」。這段是 opus 可否理解的一手證據，不確定就老實寫。
【要求】只報「說得出位置與後果」的問題：每項附 檔案:行號、類別（a／b／c）、
       證據、後果、**最小**改法、嚴重度（MUST-FIX＝會浪費明顯 context／輪數或照做會錯；
       SHOULD-FIX＝品質建議）。無發現時列出已檢查的面向。
【回報】不超過 80 行：結論行（MUST-FIX n／SHOULD-FIX m）、量化表、Read-back、發現表。
       溢出寫到 <系統提示給的 scratchpad 目錄>/reviewer-<target 名稱>.md 回傳路徑。不要貼檔案全文。
```

### 3. 派 judge（每個 target 一個，同一則訊息平行派出）

reviewer 全部回來後再派。`Agent`，`subagent_type: general-purpose`，`model: opus`
（驗收者不得低於產出者）。**只給 judge 該 target 的路徑與 reviewer 報告原文（含溢出檔路徑），
不給你的任何意見。** prompt：

```
【角色】你是 judge，裁決 reviewer 對 <target 真實路徑> 的審查是否成立。唯讀：不得修改任何檔案。
【輸入】reviewer 報告如下（這是待裁決的主張，不是事實）：
<reviewer 報告原文，含溢出檔路徑>
【做法】自己重讀 target 內相關檔案，逐條核對位置與證據；量化表的行數用 wc -l 抽驗。
【逐條裁決】每條發現給：成立／部分成立／不成立；理由一句；嚴重度同意或改為何；
       改法是否正確且最小（不是就給你的版本）。
【漏報】reviewer 沒抓到但符合 (a)(b)(c) 的問題，最多 3 條，格式同上。
【回報】不超過 60 行：結論行（成立 x／部分 y／不成立 z／漏報 w）＋裁決表。
```

### 4. 彙整報告（主對話）

每個 target 一節，內容只來自兩份回報，不加你自己的新發現：

1. **結論行**：judge 確認的 MUST-FIX／SHOULD-FIX 數、量化摘要（總行數、載入檔數、可省輪數）。
2. **Read-back**：reviewer 原文照列；有「不確定」即視為 opus 理解風險，一併列入發現。
3. **建議清單**（只列 judge 判「成立」或「部分成立」的）：檔案:行號、類別、後果、改法、judge 的修正意見。
4. **待使用者裁決**：reviewer 與 judge 不一致的條目，並列雙方理由；judge 的漏報項也放這裡，
   標「judge 補、未經第二意見」。
5. **駁回**：judge 判不成立的，一行一條帶過。

回報缺結論行＝無效回報：重派一次，再失敗就在報告標明該 target 未完成，**不得腦補**。
最後提醒使用者：本次未修改任何檔案，要改哪些請指定。
