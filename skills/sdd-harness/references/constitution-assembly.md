# 憲章組裝規則（/speckit.constitution 階段）

目標：以**憲章來源**為基本憲章，依專案的**導入階段**與**應用類型**組裝出自足的
`.specify/memory/constitution.md`。憲章來源二選一：

| 來源 | 何時用 | 內容 |
|------|--------|------|
| **團隊基線（預設）** | 使用者未指定憲章 | 同 repo 的 `sdd-baseline` skill 所附副本 `references/baseline/`（README、constitution、延伸檔、tech-standards、`manifest.json`）；位置以 `$SDD_BASELINE_DIR` 覆寫，預設 `$SKILL_DIR/../sdd-baseline/references/baseline` |
| **自訂憲章** | 使用者在 prompt 指定（檔案路徑、目錄路徑，或直接貼上內容） | 使用者給的 `*.md`；貼上的內容先寫到系統暫存檔再當單檔來源 |

「自足」是硬需求：下游（speckit-plan / speckit-analyze 與各審查 subagent）以
constitution.md 為**主要基準**，輔以 `.specify/memory/baseline/` 的本地副本
（tech-standards.md、manifest.json——這也是副本必須隨憲章 commit 入版控的原因）；
**不可用連結或「見 sdd-baseline」代替內容**。

## 1. 取得憲章來源

```bash
bash "$SKILL_DIR/scripts/copy-baseline.sh" [來源目錄或檔案] .specify/memory/baseline
```

- 不帶來源 → 依序找 `$SDD_BASELINE_DIR`、`$SKILL_DIR/../sdd-baseline/references/baseline`、
  `~/.claude/skills/sdd-baseline/references/baseline`；都沒有就非零退出
  （步驟 0 的 `check_baseline=absent` 已預告此情形，依 workflow-stages.md
  「錯誤處理細則」的憲章來源決策樹處置）。
- 來源是目錄 → 複製頂層全部 `*.md`（排除 `CLAUDE.md`）；有 `manifest.json` 就原樣
  帶走（`repo`／`head_commit`／版本供追溯與漂移比對），沒有就產生一份
  （`repo` 為 `custom`、`head_commit` 為 null）。
- 來源是單一 `.md` → 寫成 `constitution.md` 並產生 `custom` manifest。
- 腳本先寫暫存目錄、全部成功才整目錄替換；清單與數量以 `manifest.json` 的
  `files` 為準——**不要寫死檔案數**。之後所有組裝**只用這份本地副本**。

## 2. 解析基線 README（不要寫死規則）

團隊基線含 `README.md` 時，從 `.specify/memory/baseline/README.md` **即時解析**兩張表：
1. **三階段導入總覽**：各階段的「必要（MUST 採用）」與「參考」範圍。
2. **載入文件表**（在 constitution.md 的「文件結構與載入指引」）：應用類型 → 須載入的延伸檔。

基線持續演進，表格內容以副本的版本為準；解析結果要在向使用者提問時呈現，
讓使用者看到「這個選擇會載入哪些文件」。

**自訂憲章沒有這兩張表**時：不做階段裁剪，整份視為 MUST 納入；第 3 節仍問
導入階段與應用類型（寫進宣告與 `sdd-adoption.json`，供下游審查者判讀強度），
`loaded_docs` 列實際複製的檔案。

## 3. 向使用者確認（AskUserQuestion）

使用者已附 `/sdd-baseline decide` 產出的「SDD 導入決策摘要」時，直接採用其
導入階段／應用類型／風險分級／載入文件，只覆述一次請使用者確認，不重問。
否則：

| 問題 | 選項 | 預設 |
|------|------|------|
| 導入階段 | 1 對齊基礎 / 2 分級與應用紀律 / 3 治理與部署 | **1**（基線的預設起點）|
| 開發應用類型 | API 服務 / 微服務 / 工具服務（worker、批次、CLI）/ Shell Script / 前端網頁應用 | 依需求描述推斷後仍須確認 |
| 服務風險分級（僅階段 ≥ 2）| Critical / Standard / Internal / Experimental | 依基線「團隊專案類型 × 風險分級對照」建議 |

確認後把「導入階段 × 載入文件」的解析結果覆述給使用者（例：「階段 1 + Shell Script
→ 憲章主檔（CP/GV 為必要）+ §SH 延伸（參考）」），取得同意再組裝。

## 4. 組裝規則（策展式合併，非全文照抄）

**讀取範圍（token 紀律）**：只 Read 三類檔案——`baseline/README.md`（解析兩張表）、
`baseline/constitution.md`、載入文件表對本專案應用類型指定的延伸檔（導入階段 ≥ 2
另加 `tech-standards.md`）。其餘延伸檔**不要讀入**——它們只存於磁碟，
供日後階段升級與 subagent 取用。

依導入階段裁剪**規範強度**，內容取自本地副本：

| 導入階段 | MUST（全文納入，具約束力）| 參考（納入但明確標示「參考、暫不強制」）|
|---------|---------------------------|------------------------------------------|
| 1 | §CP-1~6 + 最小審查（§GV 之 PR 審查部分）| §TR、風險分級、應用類型延伸檔 |
| 2 | 階段 1 + 風險分級宣告 + §TR + 應用類型對應延伸檔（依載入文件表）| §SVC、§DEP（若載入表要求才升為 MUST）|
| 3 | 階段 2 + §SVC + §DEP + 完整 §GV | —（全部納入）|

組裝後的 constitution.md 結構：

```markdown
<!--
Sync Impact Report
Version change: [none] → 1.0.0 (initial ratification)
Source baseline: <manifest.repo>@<head_commit 前 7 碼，custom 時寫 custom> (v<版本或 n/a>, 導入階段 <N>)
Loaded docs: constitution.md + <延伸檔清單>
-->
# <專案名> 憲章

> 上游基線：<團隊 SDD 憲章 v<版本>｜自訂憲章>（導入階段 <N>：<階段名>）
> 應用類型：<類型>；服務風險分級：<分級或「階段一暫不分級」>

## 規範用語
（沿用基線 RFC 2119 段落；自訂憲章沒有時補一段標準 RFC 2119 說明）

## 核心原則（MUST）
（§CP-1~6 全文，依基線）

## 治理
（依階段裁剪的 §GV）

## <依階段納入的其他章節>
（§TR / 延伸檔內容；階段未及者標示【參考】並整節註明「本階段暫不作為合併條件」）
```

裁剪判斷不確定時：**寧可整節納入並標【參考】，不可默默省略**——省略會讓後續
analyze 無從比對。

## 5. 執行 speckit-constitution

讀 `.claude/skills/speckit-constitution/SKILL.md` 並依其指示執行，把組裝好的內容
作為輸入（該 skill 負責填 template、寫 Sync Impact Report、對 templates 做一致性
傳播檢查）。產出後檢查：剔除 HTML 註解後無殘留 placeholder——樣式
`\[[A-Z][A-Z0-9_ ]{2,}\]`，**含數字型** token 如 `[PRINCIPLE_2_NAME]`（與
detect-stage.sh 的檢查一致）。

## 6. 導入宣告（基線 §GV 的硬要求）

1. **專案 README.md** 新增（或更新）章節：

```markdown
## SDD 導入宣告

| 項目 | 值 |
|------|-----|
| 目前導入階段 | 第 <N> 階段（<階段名>）|
| 服務風險分級 | <分級>（階段一暫不分級時寫「未分級（階段一）」）|
| 應用類型 | <類型> |
| 憲章基線 | <manifest.repo> v<版本>@<sha 前 7 碼>（自訂憲章寫「自訂憲章（<來源檔名>）」）|
```

專案沒有 README.md 就建立一個最小版（專案名 + 一句描述 + 本章節）。

2. **寫 `.specify/memory/sdd-adoption.json`**（schema 見 workflow-stages.md；
   `baseline_*` 三欄抄自 `manifest.json`）。

## 7. Commit

`bash .specify/extensions/git/scripts/bash/auto-commit.sh after_constitution`
→ 依「commit 驗證規則」（見 SKILL.md）確認 working tree 乾淨。
本階段所有產物（constitution.md、baseline/、adoption.json、README）會被一併帶入
這個 commit。

## 既有專案（非首次導入）的注意事項

- constitution.md 已存在且無 placeholder：詢問使用者要「沿用」還是「以最新基線重新
  組裝」；重新組裝時 Sync Impact Report 的 Version change 依 §GV-1 SemVer 升版。
- **唯讀比對，不重抓**：專案副本 `.specify/memory/baseline/manifest.json` 的
  `head_commit` 與憲章來源的 manifest（`$SDD_BASELINE_DIR/manifest.json`）比對。
  相同 → 沿用。不同 → 告知使用者兩個 sha 與版本差異，**經使用者同意才**重跑
  copy-baseline.sh（它會整目錄替換舊快照），重抓後的變更以獨立 commit 收尾。
  專案副本為 `custom`、或來源副本不存在 → 略過比對，告知「本次無法檢查基線漂移」。
