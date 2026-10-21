# {title} v{N}：用 sdd-harness 開發的啟動說明

> 給開發者。這個目錄是 make-mockup-harness 產出的 SDD 交接包，`.specify/context/` 下的結構
> 可以原樣複製進開發 repo。你不需要安裝 make-mockup-harness，也不需要進 mockup 工作區。

## 內容

```
.specify/context/
├── _shared/
│   ├── spec-source-template.md        # spec.md「規格來源」段範本（機械檢查 7 的比對原文）
│   └── sdd-source-instructions.md     # sdd-harness 各階段補充指示；每個 prompt 都要先讀它
└── {slug}/v{N}/                       # 規格來源，唯讀
    ├── index.md                       # 規格來源索引：每檔的媒材、取證方式、涵蓋的 US／畫面——找來源從這裡開始
    ├── storyboard.md                  # 業務規則的權威
    ├── sdd-input.md                   # US 對照、驗收條件原文、FR 候選、已定案決策、補問清單（PM 已答）
    ├── prototype/index.html           # 呈現的權威；約 {proto_size}，不要整份 Read
    ├── prototype/export.json          # sha256
    ├── prototype/screens/             # 截圖，索引在 sdd-input.md
    └── reference/                     # brief、一致性檢核（參考，不具權威）
```

| 來源 | sha256 |
|---|---|
| storyboard.md | {sha_storyboard} |
| prototype/index.html | {sha_prototype} |

## 開始之前確認

- [ ] `sdd-input.md` 的「US 對照」Priority 欄與「補問清單」PM 答案欄都已填。沒填就退回 SA，不要自己猜。
- [ ] 開發 repo 已決定：新 repo、既有 SDD repo，或尚未導入 SDD 的既有 repo（見下）。

## 步驟 1：放進開發 repo 並 commit

**新 repo 或尚未導入 SDD 的 repo**：先讓 sdd-harness 完成 init 與憲章，再放交接包。

```text
/sdd-harness 新專案 {專案名稱}，應用類型 frontend-web。請先完成步驟 1 init 與步驟 2 憲章，
步驟 2 commit 完成後停下來等我放入規格來源，不要進入步驟 3。
```

**既有 SDD repo**：直接放交接包，sdd-harness 會從步驟 3 開新 feature。

```bash
cd {開發 repo}
HANDOFF={本目錄絕對路徑}

# _shared/ 若 repo 已有（前一個 feature 放的），先 diff；不同時以 repo 現有為準，差異回報 SA
mkdir -p .specify/context
cp -Rn "$HANDOFF/.specify/context/." .specify/context/

# 重算 sha256，必須與上表及 export.json 相同
shasum -a 256 .specify/context/{slug}/v{N}/storyboard.md .specify/context/{slug}/v{N}/prototype/index.html

git add .specify/context
git commit -m "docs(context): 新增 {slug} v{N} 規格來源（StoryBoard＋Prototype）"
```

先 commit 的原因：sdd-harness 啟動時會把未 commit 的檔案分類，`.specify/context/` 不在它的分類表內，會被歸為「不明」而中斷。

## 步驟 2：啟動 sdd-harness

```text
/sdd-harness 開新 feature「{title}」。
先讀 .specify/context/_shared/sdd-source-instructions.md，全程照它執行。
規格來源：StoryBoard v{N} 與 Prototype v{N}，位於 .specify/context/{slug}/v{N}/，
交接說明在同目錄 sdd-input.md。spec.md 依來源整理，不要重新摘要需求；
開頭插入 .specify/context/_shared/spec-source-template.md 的「規格來源」段並填齊。
設計系統模式：{A 沿用專案現行 ｜ B 自 Prototype 導入}。
```

之後 sdd-harness 會依序走 clarify → plan → tasks → analyze → implement。各階段的補充規則都在
`sdd-source-instructions.md`，只需在對應階段開始前提醒一句：

| 階段 | 提醒 |
|---|---|
| clarify | 「clarify 的問題依 sdd-source-instructions.md 第 2 節分類：互動類先操作 Prototype 裁決；業務類寫到 `specs/{NNN}/clarify-questions-for-sa.md` 等我轉給 SA／PM；G7 類以 sdd-input.md 補問清單為準。」 |
| plan | 「plan 依第 3 節產前端設計：token 用 Playwright computed style 萃取，ui-contracts 文案用 innerText 從 Prototype DOM 抽取，並規劃 Prototype 並列比對 E2E。」 |
| implement | 「implement 依第 5 節：implementer 附 ui-contracts 章節與截圖；validator 必做與 `prototype/screens/` 的並列結構比對；reviewer 加查 token 與共用元件。」 |

開 Prototype 來操作或對照：

```bash
python3 -m http.server 8765 --bind 127.0.0.1 -d .specify/context/{slug}/v{N}/prototype
# http://127.0.0.1:8765/index.html
```

## 中斷後續跑

```text
/sdd-harness resume
先讀 .specify/context/_shared/sdd-source-instructions.md，再依狀態檔續跑。
```

SA／PM 回答了 `clarify-questions-for-sa.md` 之後：

```text
/sdd-harness resume
先讀 .specify/context/_shared/sdd-source-instructions.md。
SA／PM 已回覆 specs/{NNN}/clarify-questions-for-sa.md（答案在「答覆」欄），請據此更新 spec 並續跑。
```

## 完成後交回 SA

```text
請依 sdd-source-instructions.md 第 6 節產出 specs/{NNN}/handback-to-sa.md：
列出偏離登記中回寫來源＝是的 D-ID 與 X-ID（原文、處置、理由）、來源缺口 G-ID、鎖定的來源版本與 sha256。
```

把 `handback-to-sa.md` 交給 SA，由 SA 以 make-mockup-harness 升版 StoryBoard 與 Prototype。
開發期間 SA 若升版了 mockup，預設**不套用**；要套用時依 spec「來源升版」規則處理。

## 注意

- 找來源先讀 `index.md`，再依 spec 的錨點取片段；`prototype/index.html` 不整份 Read——看截圖、限量 grep、或開本機 server 操作。
- 業務類問題不自己代答；權威劃分第 1 條：會改變資料、狀態、計算結果的是業務規則，裁決權在 SA／PM。
- 與 StoryBoard 明文不同的處置，除 D-ID 外要同時登記 X-ID，否則機械檢查 7 不過。
- 版面比對以結構為準，像素差不判 FAIL。
