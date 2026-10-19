# tech-mentor

以資深工程師帶 junior 工程師／intern 的視角，將任一技術主題整理成**由概念到細節**的分層 HTML 教學頁。

## 適用情境

- 想學習或理解某項技術、架構設計、流程
- 想搞懂某段程式碼的運作方式
- 要準備給新人看的技術導讀

## 使用方式

```
/tech-mentor <要學的技術主題>
```

範例：

```
/tech-mentor Kafka 的 consumer group 與 rebalance
/tech-mentor OAuth 2.0 Authorization Code Flow with PKCE
/tech-mentor React Server Components
```

## 產出內容

產出**單一 HTML artifact**，章節由淺入深：

1. **概念** — 這是什麼、解決什麼問題
2. **架構** — 組成元件與彼此關係
3. **流程** — 資料／請求如何流動
4. **實作細節／常見陷阱** — 落地時要注意的事

每一章節的版面：

- 開頭 2–3 句概要
- 一張 inline SVG 圖（架構圖／流程圖／時序圖，擇適合者）
- 細節收在 `<details>` 可展開區塊，先看全貌、需要時再深入

## 檔案

| 檔案 | 說明 |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill 定義與 prompt |
