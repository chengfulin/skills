---
name: eli5-mentor
description: 由淺入深的圖解指引：同一主題先用 eli5 產出白話大圖版，再用 tech-mentor 產出工程師分層教學版，合併成一份 HTML artifact。當使用者要「由淺入深」了解一個 repo、一項新技術、一段完整流程或架構時使用。
argument-hint: <主題，或 repo／目錄路徑＋想了解的面向>
---

# ELI5 → Mentor 圖解指引

同一主題講兩遍：**第一部**用 `eli5` 建立直覺（大圖、極少字、生活比喻），**第二部**用 `tech-mentor` 把直覺接回真實名詞與細節（概念 → 架構 → 流程 → 實作細節／常見陷阱）。兩部合併成**一份** HTML artifact，讀者從頭讀到尾就是一條由淺入深的路。

主題：$ARGUMENTS

## 交付規則

`eli5` 與 `tech-mentor` 各自要求「產出一份 HTML artifact」。在本流程中，兩者改交付**片段檔**，最後只發布一份合併後的 artifact。片段契約：

- 第一部寫成 `<section class="part" id="part-eli5">…</section>`，第二部寫成 `<section class="part" id="part-mentor">…</section>`；不含 `<html>`、`<head>`、`<body>`（shell 本身也不含，發布時由 Artifact 包上）。
- 每章一個 `<article class="chapter" id="<唯一 id>">`，章名用 `<h2>`。目錄由 shell 依 `h2` 自動產生。
- 配色只用 shell 的 CSS 變數（`--bg` `--surface` `--fg` `--muted` `--line` `--accent` `--accent-2` `--warn`），SVG 的 `fill`／`stroke` 也一樣，深淺色主題才會一致。需要額外樣式時，放在片段內的 `<style>`，選擇器一律以 `#part-eli5` 或 `#part-mentor` 開頭。
- SVG 用 `viewBox` 加 `width="100%"`，不寫死寬度；不載入外部資源。

工作目錄：scratchpad 下的 `eli5-mentor/<主題-slug>/`。

## 步驟

1. **蒐集事實，寫 `notes.md`。** 兩部共用同一份事實，避免各說各話。
   - 主題是 repo 或程式碼：有 `.codegraph/` 先用 codegraph，否則讀 README、進入點、目錄結構與主流程的程式碼。每條事實附出處（`path:line`）。
   - 主題是技術或流程：依知識整理；涉及版本、近期變動的部分先查證。
   - `notes.md` 內容：一句話定義、它解決的問題、核心元件（3–7 個）、主流程步驟、關鍵術語、常見陷阱。
   - 完成標準：第二部要用到的每個元件與流程步驟都在 notes 裡，repo 主題的每條都有出處。
2. **第一部：ELI5。** 以 Skill 工具呼叫 `eli5`（plugin 名稱可能是 `eli5:eli5`），主題帶入，照它的要求寫內容，依片段契約寫到 `part-eli5.html`。若環境沒有 `eli5`，照它的原始要求寫：*Explain like I'm someone who knows nothing about this topic, with big pictures and few words.*
   - 選**一個**貫穿全篇的生活比喻，每個核心元件都對到比喻裡的一個角色或物件。
   - 最後一章是「比喻對照表」：比喻角色 → 真實名詞，一列一個核心元件。這張表就是通往第二部的橋。
   - 完成標準：notes 裡每個核心元件都出現在對照表上。
3. **第二部：Tech Mentor。** 以 Skill 工具呼叫 `tech-mentor`，主題帶入，照它的要求寫內容（每章 2–3 句概要＋一張 inline SVG，細節放 `<details>`），依片段契約寫到 `part-mentor.html`。
   - 每章概要第一句**回扣第一部的比喻**（例：「第一部的郵差，在這裡就是 resolver」），讓讀者把直覺接上正式名詞。
   - repo 主題在 `<details>` 裡附出處（`path:line`）。
   - 完成標準：對照表上每個真實名詞都在第二部某一章被講到。
4. **合併。** 複製 [assets/shell.html](assets/shell.html) 到工作目錄為 `index.html`，替換佔位符：
   - `{{TITLE}}`：2–4 個字的頁名（例：「DNS 由淺入深」）。
   - `{{SUBTITLE}}`：一句話說明這份指引帶讀者從哪裡走到哪裡。
   - `{{PART_ELI5}}`、`{{PART_MENTOR}}`：兩個片段檔的完整內容。
5. **發布。** 依 Artifact 工具規範發布 `index.html`（shell 已符合頁面契約：title、色彩 token、深淺色、手機寬度），`icon` 用 `book`，`description` 一句話寫主題。
6. **檢核後回報。** 逐項確認，有不符就修片段、重新合併、以同一路徑重發：
   - 頁面上只有一份 artifact，目錄列出兩部所有章節。
   - 每張 SVG 在深色主題下看得見（沒有寫死的黑／白色）。
   - 對照表的每一列在第二部都找得到對應章節。
   - 回報 artifact 連結，以及第一部用的比喻是什麼。
