---
name: shallow-to-deep
description: 由淺入深的圖解指引：同一主題先產出白話大圖版（ELI5），再產出工程師分層教學版（tech mentor），合併成一份 HTML artifact。當使用者要「由淺入深」了解一個 repo、一項新技術、一段完整流程或架構時使用。
argument-hint: <主題，或 repo／目錄路徑＋想了解的面向>
---

# 由淺入深圖解指引

同一主題講兩遍：**第一部**建立直覺（大圖、極少字、生活比喻），**第二部**把直覺接回真實名詞與細節（概念 → 架構 → 流程 → 實作細節／常見陷阱）。兩部合併成**一份** HTML artifact，讀者從頭讀到尾就是一條由淺入深的路。

主題：$ARGUMENTS

## 交付規則

兩部各自交付**片段檔**，最後只發布一份合併後的 artifact。片段契約：

- 第一部寫成 `<section class="part" id="part-eli5">…</section>`，第二部寫成 `<section class="part" id="part-mentor">…</section>`；不含 `<html>`、`<head>`、`<body>`（shell 本身也不含，發布時由 Artifact 包上）。
- 每章一個 `<article class="chapter" id="<唯一 id>">`，章名用 `<h2>`。目錄由 shell 依 `h2` 自動產生成 `<ol>`，章名**不自帶編號**（「1. 」「一、」之類），否則目錄會編兩次。
- 片段內所有 `id`（章節、SVG 的 `marker`／`symbol`／`gradient`／`clipPath` 等）一律加前綴：第一部 `e-`、第二部 `m-`（例：`e-flow`、`m-arr`）。兩部並行撰寫，不加前綴容易撞名。
- 每張 SVG 自帶它用到的 `<defs>`；`href="#…"`／`url(#…)` 只引用同一張 SVG 內的 id，不跨 SVG 共用。id 仍須全頁唯一，所以 defs 的 id 帶上章節名（例：`e-flow-arr`、`m-story-arr`）。
- 配色只用 shell 的 CSS 變數（`--bg` `--surface` `--fg` `--muted` `--line` `--accent` `--accent-2` `--warn`，以及色塊專用的 `--accent-fill` `--accent-2-fill` `--warn-fill`），SVG 的 `fill`／`stroke` 也一樣，深淺色主題才會一致。可用的值只有 `var(--…)`、`none`、`currentColor`；不寫 hex、`rgb()`／`hsl()`、具名顏色（`white`、`black`、`gray`…）。需要額外樣式時，放在片段內的 `<style>`，選擇器一律以 `#part-eli5` 或 `#part-mentor` 開頭。
- shell 的色值已調到深淺色主題都符合對比度門檻，照下列用法就不會出問題：
  - 文字與表達圖意的形狀、線條用 `--fg` `--muted` `--accent` `--accent-2` `--warn`。圖內文字以 `--fg` 為主，深淺色主題都是同一個 token。
  - `--line` 只用在裝飾線、分隔線與次要框線；表達圖意的線（牆、時間軸、流程箭頭）改用 `--muted` 或彩色 token。
  - 放文字的色塊用 `--accent-fill`／`--accent-2-fill`／`--warn-fill`（淺色主題是淡色底、深色主題是深色底，shell 已調到與 `--fg` 的對比達 4.5:1），上面的字一律 `--fg`，不用 `--muted` 或彩色 token。`--accent`／`--accent-2`／`--warn` 留給線條、描邊、圖示、彩色文字與不放文字的小色塊；放了文字就要改用對應的 `*-fill`。反白色塊（`--fg`／`--muted` 當底）上的字才用 `--bg`／`--surface`。兩個彩色 token 不直接疊放，有意義的相鄰色塊用 `--surface` 描邊或留白隔開。
  - 文字與必要圖形不加 `opacity`／`fill-opacity`。
  - 片段 `<style>` 不得以元素選擇器對 SVG 元素設 `fill`／`stroke`（例：`#part-mentor svg text { fill: var(--fg) }`）：CSS 規則優先於元素上的 `fill="…"` 屬性，會把色塊上的字一併蓋成前景色。要給預設字色只能寫 `svg text:not([fill])`。每個 `<text>` 都要有有效的 fill（屬性、class 或上述預設），否則瀏覽器預設黑色，深色主題看不見。
- SVG 一律用 `viewBox`，不在屬性寫死像素寬度。內容圖加 `width="100%"` 隨欄寬縮放；固定尺寸的小圖示（如角色卡圖示）改由片段 `<style>` 的 CSS 控制大小，不必加 `width="100%"`。不載入外部資源。
- SVG 文字要放得進它所在的色塊：粗估寬度＝中日韓字每字 1em、英數每字 0.55em（em 取該文字的 font-size），不得超出包住它的 `<rect>` 或 viewBox。長標籤改短、拆兩行，或把色塊加寬。

## 兩部的寫作要求

兩部的寫作要求內嵌於此，不呼叫外部 skill：上游改版（例如改產 PDF／Word、要求呼叫其他工具）不會影響本流程的產出與檢核。交付方式一律依上方片段契約，不產出、不發布 artifact。

- **第一部（ELI5）**，改寫自 `eli5` plugin 1.0.0：
  > 對一個完全不懂這個主題的人講解，用大圖、極少的字。
- **第二部（Mentor）**，改寫自本 repo 的 `tech-mentor`：
  > 以一位資深工程師帶 junior 工程師／intern 的角度講解這個主題，先建立觀念與架構全貌，再逐步深入實作細節。章節由淺入深引導讀者理解（概念 → 架構 → 流程 → 實作細節／常見陷阱）；每一章開頭先 2–3 句概要＋一張 inline SVG 圖（架構圖／流程圖／時序圖擇適合者），細節放在 `<details>` 可展開區塊。

工作目錄：scratchpad 下的 `shallow-to-deep/<主題-slug>/`（下稱 `<dir>`，一律用絕對路徑交給 subagent）。

## 分工

主對話蒐集事實、派工、合併、靜態檢核、實看、發布。撰寫與驗證交給獨立 subagent（`general-purpose`）：

| 角色 | 做什麼 | 產出 |
| --- | --- | --- |
| 主對話 | 蒐集事實、定比喻、派工、合併、靜態檢核、實看、修正、發布、回報 | `notes.md`、`index.html`、artifact 連結 |
| ELI5 subagent | 依第一部寫作要求寫第一部 | `part-eli5.html` |
| Mentor subagent | 依第二部寫作要求寫第二部 | `part-mentor.html` |
| 內容驗證 subagent | 唯讀，對照原始來源驗證合併後兩部的敘述是否正確、是否互相一致 | 內容發現表 |

這樣分的理由：兩部的寫作要求各自完整進入一個乾淨的 context，不會互相稀釋；兩部共用 `notes.md` 的比喻與對照表，可以並行；片段全文不經過主對話。指引文件的價值在於內容正確，所以內容由沒參與撰寫的 subagent 回到原始來源驗證，才不會替自己背書；一個人同時讀兩部，也才看得出第一部的比喻說法與第二部的真實說法有沒有矛盾。

subagent 只看得到 brief，因此每份 brief 都要寫明 `<dir>` 的絕對路徑，以及該步驟列出的內容。撰寫兩部的 brief 另要寫明：要讀的 `notes.md`、**該部的寫作要求原文**（「兩部的寫作要求」中對應的那一條）、**本頁「交付規則」整段原文**、產出檔路徑、「不要發布 artifact，只寫片段檔」、完成標準，以及回報格式（檔案路徑、章節清單、沒涵蓋到的項目）。

環境沒有 Agent 工具時，主對話依序自己做步驟 2 與 4 的內容，規則不變。

## 步驟

1. **蒐集事實並定比喻，寫 `<dir>/notes.md`。** 兩部共用同一份事實與比喻，避免各說各話，也讓兩個 subagent 能並行。
   - 主題是 repo 或程式碼：有 `.codegraph/` 先用 codegraph，否則讀 README、進入點、目錄結構與主流程的程式碼。每條事實附出處（`path:line`）。
   - 主題是技術或流程：依知識整理；涉及版本、近期變動的部分先查證，並記下來源網址。
   - `notes.md` 內容：一句話定義、它解決的問題、核心元件（3–7 個）、主流程步驟、關鍵術語、常見陷阱。
   - 選**一個**貫穿全篇的生活比喻，寫成「比喻對照表」：比喻角色 → 真實名詞，每個核心元件一列。
   - 完成標準：第二部要用到的每個元件與流程步驟都在 notes 裡，每條都有出處（`path:line` 或來源網址）；每個核心元件都在對照表上。
2. **並行派 ELI5 與 Mentor 兩個 subagent**（同一則訊息送出兩個 Agent 呼叫；兩者都需要 Write）。
   - **ELI5 subagent**：主題帶入，照第一部寫作要求寫內容，依片段契約寫到 `<dir>/part-eli5.html`。
     - 全篇只用 notes 定好的比喻，不另起比喻。
     - 最後一章是「比喻對照表」，照 notes 的表畫出來。這張表就是通往第二部的橋。
     - 完成標準：notes 裡每個核心元件都出現在對照表上。
   - **Mentor subagent**：主題帶入，照第二部寫作要求寫內容（每章 2–3 句概要＋一張 inline SVG，細節放 `<details>`），依片段契約寫到 `<dir>/part-mentor.html`。
     - 每章概要第一句**回扣 notes 對照表裡的比喻**（例：「第一部的郵差，在這裡就是 resolver」），讓讀者把直覺接上正式名詞。
     - 在 `<details>` 裡附出處（repo 主題用 `path:line`，技術主題用來源網址）。
     - 完成標準：對照表上每個真實名詞都在第二部某一章被講到。
   - 回報有未涵蓋項目時，以 SendMessage 請該 subagent 補齊，補齊後才進步驟 3。
3. **合併並做靜態檢核（主對話自己做）。** 複製 [assets/shell.html](assets/shell.html) 到 `<dir>/index.html`，替換佔位符：
   - `{{TITLE}}`：2–4 個字的頁名（例：「DNS 由淺入深」）。
   - `{{SUBTITLE}}`：一句話說明這份指引帶讀者從哪裡走到哪裡。
   - `{{PART_ELI5}}`、`{{PART_MENTOR}}`：兩個片段檔的完整內容。

   接著對兩個片段檔跑靜態檢核，不必開瀏覽器：

   ```bash
   python3 <本 skill 目錄>/assets/check.py <dir>/part-eli5.html <dir>/part-mentor.html
   ```

   它逐項檢查（最後一行 `靜態檢核：PASS`，否則列出問題）：
   - 外層 `section` 與 id、每章 `article`＋`h2`，章名不自帶編號；沒有 `html`／`head`／`body`、`script`、外部資源。
   - 所有 `id="…"` 都帶 `e-`／`m-` 前綴，且全頁唯一。
   - 沒有寫死的顏色（hex、`rgb(`、`hsl(`、具名顏色）；沒有 `opacity`。
   - 每個 `<svg>` 有 `viewBox`，屬性沒有像素寬度。
   - 每個 `href="#…"`／`url(#…)` 指到的 id 存在於同一個 `<svg>` 內。
   - 片段 `<style>` 的選擇器都以 `#part-eli5` 或 `#part-mentor` 開頭；沒有以元素選擇器覆寫 SVG 的 `fill`／`stroke`（只允許 `:not([fill])`／`:not([stroke])` 當預設值）。
   - 每個 SVG `<text>` 都有有效 fill，且與包住它的 `<rect>` 配對：`*-fill` 色塊上的字只能是 `--fg`；`--accent`／`--accent-2`／`--warn` 色塊裡不得有文字（要改用 `*-fill`）；`--fg`／`--muted` 反白色塊上的字只能是 `--bg`／`--surface`；`--bg`／`--surface`／`--line`／`none` 底上的字不能是 `--bg`／`--surface`。
   - 每個 SVG `<text>` 的粗估寬度（中日韓字 1em、英數 0.55em）不超出包住它的 `<rect>` 或 viewBox（容忍 4px；旋轉、多行與 transform 群組外的對照不估）。

   另用 grep 確認：對照表的每一列在第二部都找得到對應章節。

   格式類問題（寫死顏色、id 重複或缺前綴、選擇器前綴、style 覆寫 fill、色塊文字對比、跨 SVG 引用、章名編號、文字溢出）主對話直接修片段後重新合併，直到 PASS；內容缺漏（對照表某列在第二部沒有對應）以 SendMessage 請 Mentor subagent 補寫，再重新合併。
4. **派內容驗證 subagent。** 唯讀，不修改任何檔案。brief 附上 `<dir>/index.html`、`notes.md` 的絕對路徑、原始來源位置（repo 路徑，或技術主題的權威來源），並寫明兩部的定位（第一部允許簡化，但不得說錯；第二部要精確）。工作：
   - 逐條驗證兩部的事實敘述：流程順序、角色職責與權限、數字與上限、觸發條件、因果關係。圖裡的文字、標籤、箭頭方向與先後順序也算敘述。
   - 回到**原始來源**核對，不只比對 `notes.md`（notes 本身也可能有誤）。repo 主題讀出處檔案本身；技術主題查官方文件或權威來源，涉及版本的敘述要確認版本。
   - 第二部的 `path:line` 出處要指到真正支持該敘述的內容。
   - 比喻不得誤導：比喻角色的行為要和真實元件一致（例：比喻說「驗收員順手修好」，實際元件卻是唯讀，就是錯）。第一部的比喻說法與第二部對同一元件的說法要一致。
   - 分級：**錯誤**（與來源矛盾，或會讓讀者誤解）必修；**不精確**（簡化過頭但不誤導）建議修；**無法查證**（找不到來源支持）列出。
   - 回報（≤40 行）：結論行 `內容驗證：PASS` 或 `N 項發現（錯誤 x、不精確 y、無法查證 z）`；發現逐列寫出章節 id、原文摘句、問題、證據（`path:line` 或網址）、建議改寫。
   - 處理：主對話依發現表直接修片段（錯誤源自 `notes.md` 時一併修 notes，另一部有同樣敘述也要一起修），重新合併、重跑 check.py，只做一輪，不再派驗證。無法查證與未修的項目列入步驟 7 的回報。
5. **實看（一次，主對話自己做）。** 內容修完、check.py 通過後，用 headless Chrome 看一遍版面；check.py 估的是寬度，抓不到字型實際較寬、標籤互相重疊、色塊互相蓋住這類問題。不起伺服器、不用 Claude in Chrome（它開不了 `file://`）：

   ```bash
   python3 <本 skill 目錄>/assets/snapshot.py <dir>/index.html <dir>-verify
   ```

   腳本在 `<dir>-verify/` 建驗證副本（補 doctype 與 charset，注入切主題／分部／分頁的 script，不動 `index.html`），印出：
   - 最小寬度 720px（直式手機 9:16 的下限）的 `.wrap` 有無水平溢出（scrollWidth 等於 clientWidth 才算 OK）。不另做更窄的檢查。
   - 各部高度，與截圖清單：頁首（目錄）淺色一張；每部深色依 3000px 分頁、淺色第一頁。

   以 Read 工具逐張看圖，確認：目錄列出兩部所有章節且不重複編號；每張圖都看得見；文字沒有被色塊邊緣裁掉或跑到框外；同一列標籤沒有互相重疊；箭頭、框線沒有壓到文字；深淺色都看得清楚。有問題就修片段、重跑 check.py、重新合併，只重拍受影響的那幾頁（`snapshot.py` 整個重跑也可以）。看完 `rm -rf <dir>-verify`。腳本找不到 Chrome（退出碼 2）時，回報寫「未實看」與原因，不得當作通過。
6. **發布。** 主對話依 Artifact 工具規範發布 `<dir>/index.html`（shell 已符合頁面契約：doctype、title、色彩 token、深淺色、最小寬度），`icon` 用 `book`，`description` 一句話寫主題。之後的修正都以同一路徑重發。
7. **回報。** 回報 artifact 連結、第一部用的比喻、靜態檢核修了什麼、實看修了什麼（或未實看與原因），以及內容驗證結果（修了幾項、剩下什麼）。
