# shallow-to-deep

同一主題講兩遍、合併成**一份** HTML artifact 的由淺入深圖解指引：先用白話大圖建立直覺，再以資深工程師帶 junior 的方式接回真實名詞與實作細節。

## 適用情境

- 接手或研究一個陌生的 repo，想先知道它在做什麼、再看怎麼做
- 學一項新技術，想先有畫面再進細節
- 想釐清一段完整的流程或系統架構

## 使用方式

```
/shallow-to-deep <主題，或 repo／目錄路徑＋想了解的面向>
```

範例：

```
/shallow-to-deep DNS 查詢的完整流程
/shallow-to-deep ./ 這個 repo 的請求處理流程
/shallow-to-deep Kafka 的 consumer group 與 rebalance
```

## 產出內容

| 段落 | 寫作要求改寫自 | 內容 |
| --- | --- | --- |
| 第一部 · 先有畫面 | `eli5` | 大圖、極少字，用一個貫穿全篇的生活比喻；最後一章是「比喻對照表」（比喻角色 → 真實名詞） |
| 第二部 · 再看細節 | `tech-mentor` | 概念 → 架構 → 流程 → 實作細節／常見陷阱；每章概要先回扣第一部的比喻，細節收在可展開區塊 |

兩部由兩個 subagent 依內嵌於 SKILL.md 的寫作要求並行產出片段；主對話套頁面骨架合併並以 `assets/check.py` 做靜態檢核（結構、章名、id 前綴、配色 token、style 覆寫 fill、色塊文字對比、SVG 引用、SVG 文字寬度粗估）、以 grep 確認對照表涵蓋；合併後由一個內容驗證 subagent 回到原始來源核對兩部的敘述是否正確、是否互相一致，主對話修正一輪；再以 `assets/snapshot.py` 用 headless Chrome 截圖實看一次版面（深淺色、最小寬度 720px 溢出），修完發布。兩部共用同一份事實筆記與比喻對照表（repo 主題附 `path:line` 出處），頁首有自動目錄與「淺 → 深」指示，支援深淺色主題與手機寬度。

## 相依

無。兩部的寫作要求改寫自 [`eli5`](https://github.com/anthropics/claude-plugins-community/tree/main/eli5)（Claude Community plugin 1.0.0）與本 repo 的 [`tech-mentor`](../tech-mentor/)，直接內嵌在 SKILL.md，不需安裝或呼叫這兩個 skill；它們改版也不會影響本 skill 的產出與檢核。

## 檔案

| 檔案 | 說明 |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill 定義：片段契約、兩部的寫作要求、subagent 分工與七個步驟 |
| [assets/shell.html](assets/shell.html) | 合併用的頁面骨架（色彩 token、深淺色、目錄、兩部橫幅） |
| [assets/check.py](assets/check.py) | 片段檔靜態檢核（標準函式庫，不開瀏覽器）：片段契約各項、色塊文字對比與 SVG 文字寬度粗估 |
| [assets/snapshot.py](assets/snapshot.py) | 實看截圖：建驗證副本、量最小寬度 720px 溢出與各部高度、以 headless Chrome 分頁截圖（不起伺服器） |
