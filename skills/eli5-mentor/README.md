# eli5-mentor

同一主題講兩遍、合併成**一份** HTML artifact 的由淺入深圖解指引：先用 `eli5` 建立直覺，再用 `tech-mentor` 接回真實名詞與實作細節。

## 適用情境

- 接手或研究一個陌生的 repo，想先知道它在做什麼、再看怎麼做
- 學一項新技術，想先有畫面再進細節
- 想釐清一段完整的流程或系統架構

## 使用方式

```
/eli5-mentor <主題，或 repo／目錄路徑＋想了解的面向>
```

範例：

```
/eli5-mentor DNS 查詢的完整流程
/eli5-mentor ./ 這個 repo 的請求處理流程
/eli5-mentor Kafka 的 consumer group 與 rebalance
```

## 產出內容

| 段落 | 來源 skill | 內容 |
| --- | --- | --- |
| 第一部 · 先有畫面 | `eli5` | 大圖、極少字，用一個貫穿全篇的生活比喻；最後一章是「比喻對照表」（比喻角色 → 真實名詞） |
| 第二部 · 再看細節 | `tech-mentor` | 概念 → 架構 → 流程 → 實作細節／常見陷阱；每章概要先回扣第一部的比喻，細節收在可展開區塊 |

兩部由兩個 subagent 分別呼叫 `eli5`、`tech-mentor` 並行產出片段，每部完成後各由一個內容驗證 subagent 回到原始來源核對敘述是否正確；接著由整合 subagent 套頁面骨架合併、靜態檢核，並以 headless Chrome 搭配本機伺服器實看深淺色與手機寬度；最後由對比度 review subagent 計算每張圖在深淺色主題下的顏色對比度。主對話只負責蒐集事實、派工與發布。兩部共用同一份事實筆記與比喻對照表（repo 主題附 `path:line` 出處），頁首有自動目錄與「淺 → 深」指示，支援深淺色主題與手機寬度。

## 相依

- [`eli5`](https://github.com/anthropics/claude-plugins-community/tree/main/eli5)：Claude Community plugin。未安裝時，skill 會照它的原始要求自行產出第一部。
- [`tech-mentor`](../tech-mentor/)：本 repo 的 skill。

## 檔案

| 檔案 | 說明 |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill 定義：片段契約（含對比度）、實看環境、subagent 分工與七個步驟 |
| [assets/shell.html](assets/shell.html) | 合併用的頁面骨架（色彩 token、深淺色、目錄、兩部橫幅） |
