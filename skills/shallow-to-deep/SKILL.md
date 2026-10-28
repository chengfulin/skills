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
- 每章一個 `<article class="chapter" id="<唯一 id>">`，章名用 `<h2>`。目錄由 shell 依 `h2` 自動產生。
- 片段內所有 `id`（章節、SVG 的 `marker`／`symbol`／`gradient`／`clipPath` 等）一律加前綴：第一部 `e-`、第二部 `m-`（例：`e-flow`、`m-arr`）。兩部並行撰寫，不加前綴容易撞名。
- 每張 SVG 自帶它用到的 `<defs>`；`href="#…"`／`url(#…)` 只引用同一張 SVG 內的 id，不跨 SVG 共用。章節被收合或抽掉時，其他圖才不會斷。id 仍須全頁唯一，所以 defs 的 id 帶上章節名（例：`e-flow-arr`、`m-story-arr`）。
- 配色只用 shell 的 CSS 變數（`--bg` `--surface` `--fg` `--muted` `--line` `--accent` `--accent-2` `--warn`），SVG 的 `fill`／`stroke` 也一樣，深淺色主題才會一致。可用的值只有 `var(--…)`、`none`、`currentColor`；不寫 hex、`rgb()`／`hsl()`、具名顏色（`white`、`black`、`gray`…）。需要額外樣式時，放在片段內的 `<style>`，選擇器一律以 `#part-eli5` 或 `#part-mentor` 開頭。
- 對比度在深淺色兩個主題都要達標：一般文字 ≥ 4.5、大字（≥ 18.66px 粗體或 ≥ 24px）≥ 3、理解圖意必需的形狀與線條 ≥ 3。依目前 shell 色值，照下列用法就會達標：
  - `--fg` `--muted` `--accent` `--accent-2` `--warn` 對 `--surface`／`--bg` 兩個主題都 ≥ 4.7，可用於文字與必要的形狀、線條。
  - `--line` 只有約 1.4，只能用在裝飾線、分隔線與次要框線；表達圖意的線（牆、時間軸、流程箭頭）改用 `--muted` 或彩色 token。
  - 色塊上的文字用 `--bg` 或 `--surface`（疊在 `--accent`／`--accent-2`／`--warn`／`--fg` 色塊上都 ≥ 4.7）。
  - 兩個彩色 token 直接疊放（如 `--accent-2` 疊在 `--accent` 上）不保證對比；有意義的相鄰色塊用 `--surface` 描邊或留白隔開。
  - 文字與必要圖形不加 `opacity`／`fill-opacity`，透明度會拉低對比。
- SVG 一律用 `viewBox`，不在屬性寫死像素寬度。內容圖加 `width="100%"` 隨欄寬縮放；固定尺寸的小圖示（如角色卡圖示）改由片段 `<style>` 的 CSS 控制大小，不必加 `width="100%"`。不載入外部資源。

## 兩部的寫作要求

兩部的寫作要求內嵌於此，不呼叫外部 skill：上游改版（例如改產 PDF／Word、要求呼叫其他工具）不會影響本流程的產出與檢核。交付方式一律依上方片段契約，不產出、不發布 artifact。

- **第一部（ELI5）**，改寫自 `eli5` plugin 1.0.0：
  > 對一個完全不懂這個主題的人講解，用大圖、極少的字。
- **第二部（Mentor）**，改寫自本 repo 的 `tech-mentor`：
  > 以一位資深工程師帶 junior 工程師／intern 的角度講解這個主題，先建立觀念與架構全貌，再逐步深入實作細節。章節由淺入深引導讀者理解（概念 → 架構 → 流程 → 實作細節／常見陷阱）；每一章開頭先 2–3 句概要＋一張 inline SVG 圖（架構圖／流程圖／時序圖擇適合者），細節放在 `<details>` 可展開區塊。

工作目錄：scratchpad 下的 `shallow-to-deep/<主題-slug>/`（下稱 `<dir>`，一律用絕對路徑交給 subagent）。

## 實看環境

步驟 4、5 要在瀏覽器實看頁面時，一律用 headless Chrome 搭配自己起的本機伺服器，不用 Claude in Chrome（它打不開 `file://`）。

1. **驗證目錄**：建 `<dir>-verify/`（下稱 `<vdir>`），把 `<dir>/index.html` 複製進去。shell 只靠 `<html data-theme>` 切換主題，在**副本**的 `</body>` 前（沒有就附在檔尾）注入一段 script，讀網址參數 `?theme=light|dark` 設定 `data-theme`；需要取計算後樣式時，同一段 script 把結果寫進 DOM 供 `--dump-dom` 讀出。不修改 `<dir>/index.html`。
2. **本機伺服器**：shell 沒有 `meta charset`（發布時由 Artifact 補上），伺服器必須回 `charset=utf-8`，否則中文亂碼。在背景啟動並記下 PID：
   ```bash
   python3 -c 'import functools,http.server as h,sys;h.SimpleHTTPRequestHandler.extensions_map[".html"]="text/html; charset=utf-8";h.test(HandlerClass=functools.partial(h.SimpleHTTPRequestHandler,directory=sys.argv[1]),port=int(sys.argv[2]),bind="127.0.0.1")' "<vdir>" 8765 &
   ```
   用 `curl -sI http://127.0.0.1:8765/index.html` 確認 `Content-type: text/html; charset=utf-8`。埠被占用就換一個。
3. **headless Chrome**：macOS 為 `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`，其他平台找 `google-chrome`／`chromium`。每次執行都加 `--headless=new --hide-scrollbars --user-data-dir=<vdir>/profile`：
   - 截圖：`--window-size=1280,<高度> --screenshot=<vdir>/<名稱>.png "http://127.0.0.1:8765/index.html?theme=dark"`；手機寬度用 `--window-size=390,<高度>`。
   - 取 DOM：`--dump-dom "<網址>"`，讀注入 script 寫入的結果。
4. **收尾（必做）**：`kill <PID>`，以 `lsof -i :<埠>` 確認埠已釋放，再 `rm -rf <vdir>`（含 profile 與截圖）。需要留存的證據先複製到 scratchpad 的其他目錄，並在回報寫出路徑。
5. 找不到 Chrome 或伺服器起不來時，回報寫「未實看」與原因，不得當作通過。

## 分工

主對話只做三件事：蒐集事實、派工、發布。其餘工作各交給一個獨立 subagent（`general-purpose`）：

| 角色 | 做什麼 | 產出 |
| --- | --- | --- |
| 主對話 | 蒐集事實、定比喻、派工、轉交發現、發布、回報 | `notes.md`、artifact 連結 |
| ELI5 subagent | 依第一部寫作要求寫第一部 | `part-eli5.html` |
| Mentor subagent | 依第二部寫作要求寫第二部 | `part-mentor.html` |
| 內容驗證 subagent（每部一個） | 唯讀，對照原始來源驗證該部的敘述是否正確 | 內容發現表 |
| 整合 subagent | 套 shell 合併、靜態檢核、實看深淺色與手機寬度、修格式問題 | `index.html`＋檢核結果 |
| 對比度 review subagent | 唯讀，計算每張圖在深淺色主題下的顏色對比度 | 對比度發現表 |

這樣分的理由：兩部的寫作要求各自完整進入一個乾淨的 context，不會互相稀釋；兩部共用 `notes.md` 的比喻與對照表，可以並行；片段全文不經過主對話。指引文件的價值在於內容正確，所以內容由沒參與撰寫的 subagent 回到原始來源驗證，對比度也由沒參與撰寫與合併的 subagent 審查，才不會替自己背書。

subagent 只看得到 brief，因此每份 brief 都要寫明 `<dir>` 的絕對路徑，以及該步驟列出的內容。撰寫兩部的 brief 另要寫明：要讀的 `notes.md`、**該部的寫作要求原文**（「兩部的寫作要求」中對應的那一條）、**本頁「交付規則」整段原文**、產出檔路徑、「不要發布 artifact，只寫片段檔」、完成標準，以及回報格式（檔案路徑、章節清單、沒涵蓋到的項目）。需要實看的 brief（步驟 4、5）附上**本頁「實看環境」整段原文**。

環境沒有 Agent 工具時，主對話依序自己做步驟 2–5 的內容，規則不變。

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
3. **內容驗證（每部一個 subagent，該部完成就派，兩部的驗證並行進行）。** 唯讀，不修改任何檔案。brief 附上該部片段檔、`notes.md` 的絕對路徑、原始來源位置（repo 路徑，或技術主題的權威來源），並寫明該部的定位（第一部允許簡化，但不得說錯；第二部要精確）。工作：
   - 逐條驗證片段裡的事實敘述：流程順序、角色職責與權限、數字與上限、觸發條件、因果關係。圖裡的文字、標籤、箭頭方向與先後順序也算敘述。
   - 回到**原始來源**核對，不只比對 `notes.md`（notes 本身也可能有誤）。repo 主題讀出處檔案本身；技術主題查官方文件或權威來源，涉及版本的敘述要確認版本。
   - 第二部的 `path:line` 出處要指到真正支持該敘述的內容。
   - 比喻不得誤導：比喻角色的行為要和真實元件一致（例：比喻說「驗收員順手修好」，實際元件卻是唯讀，就是錯）。
   - 分級：**錯誤**（與來源矛盾，或會讓讀者誤解）必修；**不精確**（簡化過頭但不誤導）建議修；**無法查證**（找不到來源支持）列出。
   - 回報（≤40 行）：結論行 `內容驗證：PASS` 或 `N 項發現（錯誤 x、不精確 y、無法查證 z）`；發現逐列寫出章節 id、原文摘句、問題、證據（`path:line` 或網址）、建議改寫。
   - 處理：主對話把發現表轉給該部的撰寫 subagent（SendMessage，屬同一任務的續作）修正，再請驗證 subagent 只複核這幾項。錯誤源自 `notes.md` 時，主對話先修 notes，並通知兩部的撰寫 subagent，另一部有同樣敘述也要一起修。最多 2 輪；仍有錯誤時，以 AskUserQuestion 請使用者決定保留、刪除或改寫，其餘列入步驟 7 的回報。
   - 兩部都通過驗證（或剩餘發現已由使用者決定）後，才進步驟 4。
4. **派整合 subagent。** brief 附上 shell 的絕對路徑（本 skill 目錄下的 [assets/shell.html](assets/shell.html)）、`<dir>`、`notes.md`、交付規則與實看環境原文，以及下列工作：
   - 複製 shell 到 `<dir>/index.html`，替換佔位符：
     - `{{TITLE}}`：2–4 個字的頁名（例：「DNS 由淺入深」）。
     - `{{SUBTITLE}}`：一句話說明這份指引帶讀者從哪裡走到哪裡。
     - `{{PART_ELI5}}`、`{{PART_MENTOR}}`：兩個片段檔的完整內容。
   - 靜態檢核（逐項）：
     - 兩個片段都符合片段契約（外層 `section` 與 id、每章 `article`＋`h2`、所有 id 帶 `e-`／`m-` 前綴且全頁唯一、額外樣式的選擇器前綴）。
     - 每張 SVG 的配色只用契約允許的值，沒有寫死的顏色。
     - 每張 SVG 有 `viewBox`，屬性沒有寫死像素寬度。
     - 每個 `href="#…"`／`url(#…)` 都指到同一張 SVG 內存在的 id。
     - 對照表的每一列在第二部都找得到對應章節。
   - 實看檢核（依「實看環境」）：淺色、深色各截一次全頁圖，再以 390px 寬截一次，並以注入 script 比對 `scrollWidth` 與 `clientWidth`。確認每張圖都看得見、文字沒有超出框、沒有破版或水平捲動、目錄列出兩部所有章節。
   - 格式類問題（寫死顏色、id 重複或缺前綴、選擇器前綴、跨 SVG 引用、破版、文字溢框）直接修片段後重新合併；內容缺漏（對照表某列在第二部沒有對應）不自行補寫，回報給主對話。
   - 回報：`index.html` 路徑、每項檢核結果（實看附看到什麼）、修了什麼、還缺什麼、實看環境已收尾。
   - 回報有內容缺漏時，請對應的部分 subagent 補齊，補寫部分照步驟 3 再驗證一次，再請整合 subagent 重新合併檢核。
5. **派對比度 review subagent。** 整合回報通過後派遣，唯讀，不修改任何受審檔案。brief 附上 `<dir>/index.html` 與 shell 的絕對路徑、實看環境原文，以及下列工作：
   - 從 shell 讀出淺色與深色兩組 token 的實際色值（`:root` 與深色區塊）。
   - 依「實看環境」載入頁面，以注入 script 對每張 SVG 的元素取 `getComputedStyle` 的 `fill`／`stroke`／`opacity`（祖先的 opacity 要相乘），淺色、深色各算一次。
   - 逐張 SVG 列出每組「前景 → 背景」配對：圖上的文字對它所在的形狀或頁面底色、形狀與線條對它所在的底色。有透明度時先依透明度與底色混色再計算。
   - 依 WCAG 對比度公式計算比值，門檻同交付規則。純裝飾、不影響理解的元素不計，回報要說明排除了哪類元素。
   - 另截淺色、深色全頁圖實看，補抓計算看不出的問題（文字疊在線上、標籤被色塊蓋住）。
   - 回報（≤40 行）：結論行 `PASS` 或 `N 項不足`；不足項逐列寫出章節 id、元素（文字內容或形狀描述）、前景／背景 token、淺色比值、深色比值、建議改用的 token；另寫實看環境已收尾。
   - 回報有不足項時，問題出在 shell 色值（同一 token 在全頁大量不足）就由主對話提出修改 shell 的方案，請使用者決定；出在片段用法就把發現表轉給整合 subagent（SendMessage，屬同一任務的續作），由它改片段的 token 並重新合併。之後請對比度 review subagent 只複核這幾項。最多 2 輪，仍不足的列入步驟 7 的回報。
6. **發布。** 主對話依 Artifact 工具規範發布 `<dir>/index.html`（shell 已符合頁面契約：title、色彩 token、深淺色、手機寬度），`icon` 用 `book`，`description` 一句話寫主題。之後的修正都以同一路徑重發。
7. **回報。** 回報 artifact 連結、第一部用的比喻、內容驗證結果（兩部各自修了幾項、剩下什麼）、整合檢核結果（含是否實看），以及對比度審查結果（全數通過，或還有哪些未解決）。
