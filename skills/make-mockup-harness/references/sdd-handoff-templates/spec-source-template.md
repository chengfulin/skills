# spec.md「規格來源」範本段落（v4）

> 用途：feature 以 StoryBoard 與 Prototype 為依據時，放在 spec.md 開頭（`**Input**` 之後、`## Clarifications` 之前），為必填段落。
> 來源：歸納多個以 StoryBoard 與設計稿為依據的 feature 實務：來源表與 StoryBoard 優先、第三方權威與部署後目視重做、版面依設計稿與偏離分類。
> `<!-- -->` 為填寫指引，產出 spec 時刪除；`<!-- spec-source:begin -->`／`end` 錨點保留，供機械檢查定位。
> 本檔由 make-mockup-harness 步驟 7 的 `pack-sdd-handoff.sh` 複製到開發 repo 的 `.specify/context/_shared/`。
> 範例中的 sha256 僅為示意，實際交接時須以複製到 `.specify/context/` 的檔案重新計算。

---

<!-- spec-source:begin -->
## 規格來源 *(mandatory when StoryBoard／Prototype exists)*

<!--
本段由 orchestrator 在 specify 階段建立。clarify／analyze 只能引用、不得改寫；
需要變更時（例如來源升版）由 orchestrator 依「來源升版」規則處理。
-->

### 來源

<!--
1. 來源檔放在 `.specify/context/<slug>/v<N>/`，入版控後不得修改；新版另開目錄。多個 feature 可引用同一版本。
2. 版本 = 目錄名 v<N> = StoryBoard 變更紀錄最後一列的版本，三者必須一致。
3. sha256 填完整 64 碼：`shasum -a 256 <檔>`；Prototype 的值須與 mockup 匯出時的 `export.json` 相同。
4. 沒有 StoryBoard、只有自由格式需求文件時，第一列改為「需求文件」，權威範圍不變。
-->

| 來源 | 版本 | 路徑 | sha256 | 權威範圍 |
| :---- | :---- | :---- | :---- | :---- |
| StoryBoard | v{N} | `.specify/context/{slug}/v{N}/storyboard.md` | {64 碼} | 業務規則（定義見下） |
| Prototype | v{N} | `.specify/context/{slug}/v{N}/prototype/index.html` | {64 碼} | 呈現：版面、區塊順序、互動流程、UI 文案、目標視覺樣式 |
| 外部權威 | {版本} | {路徑} | {64 碼或 —} | {例：法規條文、既有報告輸出；無則刪除本列} |

- **設計系統模式**：{A 沿用專案現行 | B 自 Prototype 導入}
- **版面比對基準**：viewport 1440×900（團隊預設），瀏覽器 Chrome；其他基準須登記為權威劃分例外

**衍生產物**（由上列來源產生，不具獨立權威，與來源不一致時以來源為準）：

| 產物 | 產生自 | 路徑 |
| :---- | :---- | :---- |
| 畫面截圖 | Prototype v{N} | `.specify/context/{slug}/v{N}/prototype/screens/`（尚未產出寫 N/A） |
| design token 清單 | Prototype v{N} | `research.md`「設計 token」節（plan 階段產出） |

**參考資料**（不具權威）：

| 文件 | 用途 | 與 spec 衝突時 |
| :---- | :---- | :---- |
| {路徑或連結} | {例：系統流程 drawio，初步規劃} | {讓位：以實作分析為準} |

### 權威劃分

以下五條為基準，不改寫條文；唯一的設定項是上方「設計系統模式」。
個別 feature 需要不同做法時，提出例外並登記於「權威劃分例外」，未登記的一律依五條處理。

1. **判別式**：會改變資料、狀態、權限、計算結果或驗收結果的，是**業務規則**，以 StoryBoard 為準；
   只改變呈現方式的，是**呈現**，以 Prototype 為準。
2. **互動行為**：StoryBoard 有明文的（例如卡片聯動、排序規則）以 StoryBoard 為準；
   其餘互動（展開收合、捲動、焦點移動）以 Prototype 為準。
3. **用詞**：領域術語（狀態名、欄位名、業務名詞）以 StoryBoard 為準；其餘 UI 文案（按鈕、提示、說明）
   以 Prototype 逐字採用。有外部權威列時，外部權威的用詞優先於兩者。
4. **視覺樣式**：Prototype 是目標外觀，實作一律透過 design token 與共用元件，不照搬行內樣式或色碼。
   - 模式 A（沿用專案現行）：Prototype 的樣式對應到現有 token；對應不到或數值不同處登記偏離。
   - 模式 B（自 Prototype 導入）：從 Prototype 萃取 token，命名沿用 Prototype，清單見 research.md。
   - 狀態標籤：「顯示哪個狀態」屬業務規則；「顏色與形狀」屬視覺樣式。
5. **來源都沒定義的部分**（空狀態、錯誤、載入中、窄螢幕等）：依專案既有慣例補齊，登記在「來源缺口」。

### 權威劃分例外

<!-- 例外由任何人提出，經使用者（PM／SA）裁決後才登記；clarify／analyze 不得自行新增。
     例外只覆蓋指名的條次與範圍，其餘仍依五條。無例外寫「無」。 -->

| ID | 條次 | 範圍 | 例外內容 | 理由 | 提出者 | 裁決日期 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| X-1 | {第 n 條} | {US-nn／S<n>／全 feature} | {改為…} | {…} | {姓名} | {YYYY-MM-DD} |

### 範圍對照

<!-- 畫面 ID 沿用 Design Brief 的 S<n>；Prototype 含其他 feature 的畫面時只列本 feature 的。 -->

| spec User Story | StoryBoard | Prototype 畫面 |
| :---- | :---- | :---- |
| US1 {名稱} | US-01 | S1 {畫面名} |
| US2 {名稱} | US-02 | S1、S2 |

- **StoryBoard 中不在本 feature 的 User Story**：{US-nn：理由；無則寫「無」}
- **Prototype 中不在本 feature 的畫面或區塊**：{S<n> 或區塊名：理由；無則寫「無」}

### 錨點慣例

見 `.specify/context/_shared/spec-source-template.md`「錨點慣例（原文）」；本 spec 的錨點依該表，由機械檢查 8、9 守。

### 來源缺口
| :---- | :---- | :---- |
| `[SB US-nn]`、`[SB US-nn 規則 k]`、`[SB US-nn 狀態]`、`[SB US-nn 邊界 k]`、`[SB 全域規則 k]`、`[SB 資料關聯 k]` | StoryBoard 的 User Story／該 US「規則」清單第 k 條／其「狀態」項／「邊界情況」第 k 條／「全域規則」第 k 條／「資料關聯性」第 k 列 | `[SB US-02 規則 3]` |
| `[P S<n>]`、`[P S<n>-<序號>]` | Prototype 畫面（範圍對照的 S<n>）／`screens/` 中檔名 `S<n>-<序號>-*.png` 的那張截圖 | `[P S1-03]` |
| `[EXT <簡稱> §<節>｜p.<頁>]` | 來源表「外部權威」列的文件，只到節或頁 | `[EXT 法規 §12]` |
| `[IN Q<n>]`、`[IN AC-<id>]` | 同目錄 `sdd-input.md` 的補問清單答案／驗收條件原文（含 `AC-P` 系列） | `[IN AC-P1]` |

<!-- 來源未定義、由 spec 補上的項目。每條必須是已決處置並指向 FR；
     尚未決定的寫 [NEEDS CLARIFICATION: …]，clarify 後不得殘留。無則寫「無」。 -->

| # | 缺口 | 處置 | 對應 |
| :---- | :---- | :---- | :---- |
| G-1 | {例：Prototype 無載入失敗狀態} | {依站內既有錯誤元件} | FR-0xx |

### 偏離登記

<!-- 本表是偏離的唯一登記處。Clarifications 與 contracts/ui-contracts.md 只引用 D-ID，不另寫一份。
     plan 階段在 ui-contracts 發現的偏離，也回填到本表。 -->

| ID | 類別 | 來源原文 | 本 spec 處置 | 驗收影響 | 回寫來源 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| D-1 | {元件限制／來源缺漏／來源矛盾／業務決策} | {StoryBoard US-nn 或 Prototype S<n> 的原文} | {改為…，理由} | {無／修改 FR-0xx、SC-0xx} | {是／否} |

- 類別：**元件限制**（共用元件做不到）、**來源缺漏**（來源未畫出該狀態）、**來源矛盾**（來源自身或彼此衝突）、
  **業務決策**（clarify 改變了 StoryBoard 規則）。
- 「回寫來源」為「是」者，由 sdd-harness 完成報告彙整，交 make-mockup-harness 升版 StoryBoard 與 Prototype。

### 來源升版

- 開發中的 feature **預設鎖定**在上表版本，來源升版不自動套用。
- 要套用新版時：在 Clarifications 記一筆 session，更新上表版本與 sha256，重做範圍對照，
  新版差異逐條判定為「納入」或「偏離」；已 commit 的 story 依 roll forward 原則以新增 task 修正。

### 機械檢查（clarifier／analyze／validator 使用）

1. 上表每個路徑存在，`shasum -a 256` 的完整 64 碼相符；Prototype 另與 `export.json` 相符。
2. 版本 = 目錄名 = StoryBoard 變更紀錄最後一列。
3. StoryBoard 每個 US-nn 不是出現在範圍對照，就是出現在「不在本 feature」清單。
4. spec 每個 User Story 都出現在範圍對照。
5. 來源缺口與偏離登記不含 `[NEEDS CLARIFICATION`（clarify 之後）。
6. Clarifications 與 ui-contracts 引用的 D-ID 都存在於偏離登記。
7. 權威劃分五條原文未被改動；與五條不同的做法都有對應的 X-ID，且每列的提出者與裁決日期非空。
8. spec 每條 User Story、FR、AC／SC 至少一個錨點，且每個錨點只用 spec 與 `index.md` 就能解析：`SB`／`P`／`EXT`／`SRC`
   指到的 US-nn、S<n>、§節、p.頁出現在來源目錄 `index.md` 的「涵蓋」欄（`EXT`／`SRC` 的簡稱在來源表）；`IN` 指同目錄
   `sdd-input.md` 的 Q<n>／AC-<id>；`[G-n]`／`[D-n]` 存在於本 spec 的對應表。
9. 範圍對照的每個 US-nn 與 S<n> 至少被一條 User Story 或 FR 的錨點引用。
<!-- spec-source:end -->

---

## 錨點慣例（原文）

spec 內只留指標，本節是唯一版本。spec 每條 User Story、FR、驗收情境（AC／SC）句尾至少一個錨點，可多個；
沒有上游依據的標 `[G-n]` 或 `[D-n]`。錨點是 clarifier 的讀取範圍：比對某 story 時只開其錨點指到的片段，
所以要寫到能定位片段的粒度（US、規則、畫面、頁、節），不引整份檔案；錨點必須能在來源目錄 `index.md` 的「涵蓋」欄找到。

| 錨點 | 指向 | 例 |
| :---- | :---- | :---- |
| `[SB US-nn]`、`[SB US-nn 規則 k]`、`[SB US-nn 狀態]`、`[SB US-nn 邊界 k]`、`[SB 全域規則 k]`、`[SB 資料關聯 k]` | StoryBoard 的 User Story／該 US「規則」清單第 k 條／其「狀態」項／「邊界情況」第 k 條／「全域規則」第 k 條／「資料關聯性」第 k 列 | `[SB US-02 規則 3]` |
| `[P S<n>]`、`[P S<n>-<序號>]` | Prototype 畫面（範圍對照的 S<n>）／`screens/` 中檔名 `S<n>-<序號>-*.png` 的那張截圖 | `[P S1-03]` |
| `[EXT <簡稱> §<節>｜p.<頁>]` | 來源表「外部權威」列的文件，只到節或頁；簡稱登記在來源表「來源」欄 | `[EXT 法規 §12]` |
| `[IN Q<n>]`、`[IN AC-<id>]` | 同目錄 `sdd-input.md` 的補問清單答案／驗收條件原文（含 `AC-P` 系列） | `[IN AC-P1]` |
| `[G-n]`、`[D-n]` | 本 spec 的來源缺口／偏離登記第 n 筆（spec 自身，不是上游；clarify 改變規則的也是 D-ID） | `[G-1]` |
| `[SRC <簡稱> §<節>｜p.<頁>]` | 沒有 StoryBoard、只有自由格式需求文件時用 | `[SRC PRD §3.2]` |

FR 寫法示例：「FR-003 列表依到期日升冪，同日依帳號名稱 `[SB US-02 規則 2]` `[P S1-02]`」；「FR-007 載入失敗顯示站內錯誤元件 `[G-2]`」。

---

## 填寫範例（claude-subscription-inventory）

<!-- spec-source:begin -->
## 規格來源

### 來源

| 來源 | 版本 | 路徑 | sha256 | 權威範圍 |
| :---- | :---- | :---- | :---- | :---- |
| StoryBoard | v2 | `.specify/context/claude-subscription-inventory/v2/storyboard.md` | 526a03be8f41cf7f0fba42358f077939ddefc7adc34796220849f0c8568602bf | 業務規則（定義見下） |
| Prototype | v2 | `.specify/context/claude-subscription-inventory/v2/prototype/index.html` | 9a83dd863aaaa29e00228f144ba6abf20d2bcd989785dccd944b814a980623ed | 呈現：版面、區塊順序、互動流程、UI 文案、目標視覺樣式 |

- **設計系統模式**：B 自 Prototype 導入（新專案，尚無設計系統）
- **版面比對基準**：viewport 1440×900（團隊預設），瀏覽器 Chrome

**衍生產物**：

| 產物 | 產生自 | 路徑 |
| :---- | :---- | :---- |
| 畫面截圖 | Prototype v2 | N/A（make-mockup-harness 交接步驟尚未產出） |
| design token 清單 | Prototype v2 | `research.md`「設計 token」節（plan 階段產出） |

**參考資料**：無。

### 權威劃分

1. **判別式**：會改變資料、狀態、權限、計算結果或驗收結果的，是業務規則，以 StoryBoard 為準；只改變呈現方式的，是呈現，以 Prototype 為準。
2. **互動行為**：StoryBoard 有明文的以 StoryBoard 為準（本例：卡片聯動取代既有篩選、排序規則）；其餘互動以 Prototype 為準。
3. **用詞**：領域術語以 StoryBoard 為準（本例：「已取消續訂」「即將到期」「低使用率」）；其餘 UI 文案以 Prototype 逐字採用。
4. **視覺樣式**：Prototype 是目標外觀，透過 design token 與共用元件實作。模式 B：token 自 Prototype 萃取，清單見 research.md。狀態標籤顯示哪個狀態依全域規則的優先序；顏色依 token。
5. **來源都沒定義的部分**：依專案既有慣例補齊，登記在「來源缺口」。

### 權威劃分例外

無。

### 範圍對照

| spec User Story | StoryBoard | Prototype 畫面 |
| :---- | :---- | :---- |
| US1 檢視盤點總覽 | US-01 | S1 訂閱盤點（頂部彙總卡） |
| US2 檢視帳號清單 | US-02 | S1 訂閱盤點（列表） |
| US3 展開帳號明細 | US-03 | S1 訂閱盤點（展開明細） |

- **StoryBoard 中不在本 feature 的 User Story**：無。
- **Prototype 中不在本 feature 的畫面或區塊**：側欄「訂閱盤點」以外的選單項目（僅外框展示）。

### 錨點慣例

見 `.specify/context/_shared/spec-source-template.md`「錨點慣例（原文）」；本 spec 的錨點依該表，由機械檢查 8、9 守。

### 來源缺口

| # | 缺口 | 處置 | 對應 |
| :---- | :---- | :---- | :---- |
| G-1 | 資料來源：StoryBoard 註明「未來由 API 提供，本階段以假資料展示」 | 本階段以前端 mock 資料層提供，假資料取自 Prototype；頁面只經資料存取層取用 | FR-010 |
| G-2 | 載入中與載入失敗狀態：Prototype 未畫出 | 依專案既有元件補齊 | FR-007 |

### 偏離登記

| ID | 類別 | 來源原文 | 本 spec 處置 | 驗收影響 | 回寫來源 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| — | — | 無 | — | — | — |

### 來源升版

（同範本）

### 機械檢查

（同範本）
<!-- spec-source:end -->
