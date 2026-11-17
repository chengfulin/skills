---
name: tech-mentor
description: 以資深工程師帶 junior 工程師／intern 的視角，將技術主題整理成由概念到細節的分層 HTML 教學頁（每章：概要＋SVG 圖解，細節可展開）。當使用者想學習、理解某項技術、架構設計、流程，或想搞懂某段程式時使用。
argument-hint: <要學的技術主題>
---

# Tech Mentor

請以一位資深工程師帶 junior 工程師 / intern 的角度講解以下主題，先建立觀念與架構全貌，再逐步深入實作細節。只產出單一 HTML artifact，章節由淺入深引導他們理解（概念 → 架構 → 流程 → 實作細節／常見陷阱）；每一章節開頭先 2–3 句概要 + 一張 inline SVG 圖（架構圖／流程圖／時序圖擇適合者），細節放在 `<details>` 可展開區塊。主題是 repo 或某段程式時，先讀實際程式碼，圖與細節使用其中真實的檔名與 symbol。有 artifact 發布工具時發布成 Claude artifact 並回報連結；沒有時寫成單一 `.html` 檔並回報絕對路徑，不要把 HTML 貼進對話。

主題：$ARGUMENTS
