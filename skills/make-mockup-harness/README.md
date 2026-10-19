# make-mockup-harness

## 目的

讓 Agent 擔任 orchestrator，帶 SA 從客戶／PM 的需求走到**可迭代的互動 Mockup**：
Story Board → Design Brief → 透過 Chrome 交接 Claude Design → 匯出單檔 HTML 凍結版本 →
storyboard 與 mockup 一致性檢核 → 回饋回寫升版。每個版本的需求變更與畫面異動都有紀錄可追。

```
需求 ──► 1 Story Board ──► 2 Design Brief ──► 3 Claude Design 迭代 ──► 4 匯出單檔 HTML
             ▲                                                              │
             └──────── 6 回饋回寫、升版 ◄──── 5 一致性檢核 ◄────────────────┘
                              ▲                      │
                 handback-to-sa.md（開發回寫）        └──► 7 交接 SDD（選配）──► sdd-harness 開發 repo
```

---

## 檔案結構

| 檔案 | 說明 |
|------|------|
| `SKILL.md` | orchestrator 主規則：6 階段＋選配的交接 SDD、通用規則、每步驟指示 |
| `references/workflow-stages.md` | 各階段完成準則、狀態檔 schema、續跑規則 |
| `references/design-brief.template.md` | 貼進 Claude Design 的 brief 模板 |
| `references/claude-design-handoff.md` | Chrome 操作程序、Claude Design 專案 API、實測踩過的坑、手動後備 |
| `references/consistency-check.md` | 一致性檢核程序、操作驗證、五類報告格式 |
| `references/revisions.template.md` | 版本 ↔ 回饋 ↔ User Story ↔ 畫面 對照表 |
| `references/sdd-handoff.md` | 步驟 7 交接 SDD：前提、截圖、sdd-input、PM 補答、開發回寫 |
| `references/sdd-handoff-templates/` | 交接包範本：`spec-source-template.md`（spec 規格來源段）、`sdd-source-instructions.template.md`（sdd-harness 各階段補充指示）、`sdd-input.template.md`、`sdd-start.template.md`（開發者啟動說明） |
| `scripts/mockup-root.sh` | 解析產物根目錄（讀 `.make-mockup.json`，預設 `make-mockups/`） |
| `scripts/detect-stage.sh` | 續跑偵測：讀狀態檔印出階段與下一步 |
| `scripts/ingest-export.sh` | 把匯出的單檔版歸檔到 `mockups/v<N>/` 並寫 sha256，拒絕覆蓋凍結版 |
| `scripts/extract-screens.sh` | 從單檔 HTML 以關鍵字取證，避免整份讀入 context |
| `scripts/serve-mockup.sh` | 以本機 http server 開啟凍結單檔版，供操作驗證 |
| `scripts/pack-sdd-handoff.sh` | 步驟 7：前提機械檢查，把 v<N> 打包成開發 repo 的 `.specify/context/` 結構並代入範本 |

依賴同目錄的 `make-storyboard` skill（步驟 1 與 6 以 Read 方式 inline 執行）。

---

## 前置需求

- 目標 repo 需為 git repo（產物逐階段 commit）。
- Claude in Chrome 擴充功能（步驟 3、4 用來操作 claude.ai/design）。
- 設計系統為選配；要讀 Claude Design 的設計系統專案時先執行 `/design-login`。

## 安裝

```bash
ln -s "$(pwd)/skills/make-mockup-harness" ~/.claude/skills/make-mockup-harness
ln -s "$(pwd)/skills/make-storyboard"     ~/.claude/skills/make-storyboard
```

## 使用方式

在目標 repo 內：

```
/make-mockup-harness 智能客服的對話紀錄查詢功能
/make-mockup-harness resume
```

產物放在目標 repo 的 `make-mockups/<slug>/`（可用 `.make-mockup.json` 改根目錄）：

```
make-mockups/<slug>/
├── storyboard.md              # 唯一權威，含版本化變更紀錄
├── briefs/v<N>-design-brief.md
├── mockups/v<N>/index.html    # 凍結的單檔版 + export.json（sha256）
├── reviews/v<N>-consistency.md
├── feedback/                  # 留言、Claude Design 待確認清單、客戶回饋
├── revisions.md               # 版本對照表
├── handoff/v<N>/              # 步驟 7 產出：SDD-START.md ＋ .specify/context/（整包交給開發者）
└── .mockup-workflow.json      # 狀態檔，供續跑
```

## 交接 SDD（步驟 7，選配）

步驟 5 一致性檢核完成、沒有待改項時選「交接 SDD」，harness 會把 v<N> 打包成 sdd-harness 開發 repo 可直接複製的結構：

```
handoff/v<N>/
├── SDD-START.md                           # 開發者照貼的啟動 prompt 與步驟
└── .specify/context/
    ├── _shared/{spec-source-template.md, sdd-source-instructions.md}
    └── <slug>/v<N>/{storyboard.md, sdd-input.md, prototype/, reference/}
```

開發者把 `.specify/context/` 複製進開發 repo、commit，依 `SDD-START.md` 啟動 sdd-harness 即可，不需要本 skill。
開發完成後交回 `handback-to-sa.md`，SA 以步驟 6 升版。做 mockup 與做開發可以是不同人。

## 設計決策

- storyboard 是唯一真相；mockup 每版對應 storyboard 變更紀錄一列，commit 後凍結。
- Claude Design 是製作工具，Claude Code 與它只有兩條交接：brief 貼進去、單檔 HTML 取回來。
  Claude Code 的 `/design-sync` 只看得到設計系統專案、`/design` 產的是 artboard canvas，都不適合此流程。
- 操作驗證在本機開啟凍結的單檔版做，不在 Claude Design 的 iframe 裡做。
