# make-mockup-harness

## 目的

讓 Agent 擔任 orchestrator，帶 SA 從客戶／PM 的需求走到**可迭代的互動 Mockup**：
Story Board → Design Brief → 依 brief 製作互動 HTML 並發布成 artifact → 凍結版本 →
storyboard 與 mockup 一致性檢核 → 回饋回寫升版。每個版本的需求變更與畫面異動都有紀錄可追。

```
需求 ──► 1 Story Board ──► 2 Design Brief ──► 3 製作 mockup（artifact）──► 4 凍結
             ▲                                                              │
             └──────── 6 回饋回寫、升版 ◄──── 5 一致性檢核 ◄────────────────┘
                              ▲                      │
                 handback-to-sa.md（開發回寫）        └──► 7 交接 SDD（選配）──► sdd-harness 開發 repo
```

---

## 檔案結構

| 檔案 | 說明 |
|------|------|
| `SKILL.md` | orchestrator 主規則：6 階段＋選配的交接 SDD、通用規則（含派工與模型對照表）、每步驟指示 |
| `agents/mockup-brief-writer.md` | 步驟 2 的 subagent：讀 storyboard 推導畫面、狀態、假資料寫成 brief（sonnet + high；v1 覆寫 opus） |
| `agents/mockup-builder.md` | 步驟 3 的 subagent：依 build request 產出 mockup HTML 快照與產出紀錄，不發布、不問使用者（sonnet + high）；微修由主對話以 inline build 直接改 |
| `agents/mockup-consistency-checker.md` | 步驟 5 的 subagent：獨立 context 檢核凍結 mockup 與 storyboard 的一致性，含 Chrome 操作驗證（sonnet + high；交接版覆寫 opus） |
| `references/workflow-stages.md` | 各階段完成準則、狀態檔 schema、續跑規則 |
| `references/design-brief.template.md` | mockup 製作指示（brief）模板 |
| `references/mockup-build.md` | build 的輸入（request.md）、產出紀錄（build.md）、索引（builds.md）格式與 build id 規則 |
| `references/artifact-mockup.md` | 製作、發布、迭代、凍結、取留言、操作驗證程序與實測踩過的坑 |
| `references/legacy-claude-design-handoff.md` | （舊）Claude Design 網站的 Chrome 交接程序，只供 2026-12-14 前舊專案收尾 |
| `references/consistency-check.md` | 一致性檢核程序、操作驗證、五類報告格式 |
| `references/revisions.template.md` | 版本 ↔ 回饋 ↔ User Story ↔ 畫面 對照表 |
| `references/sdd-handoff.md` | 步驟 7 交接 SDD：前提、截圖、sdd-input、PM 補答、開發回寫 |
| `references/sdd-handoff-templates/` | 交接包範本：`spec-source-template.md`（spec 規格來源段）、`sdd-source-instructions.template.md`（sdd-harness 各階段補充指示）、`sdd-input.template.md`、`sdd-start.template.md`（開發者啟動說明） |
| `scripts/install.sh` | 冪等安裝：symlink skill、agents 到 `~/.claude/`，順帶連上同 repo 的 `make-storyboard` |
| `scripts/mockup-root.sh` | 解析產物根目錄（讀 `.make-mockup.json`，預設 `make-mockups/`） |
| `scripts/detect-stage.sh` | 續跑偵測：讀狀態檔印出階段與下一步 |
| `scripts/ingest-export.sh` | 把凍結的 mockup 歸檔到 `mockups/v<N>/` 並寫 export.json（來源網址、版本 id、build id、sha256），拒絕覆蓋凍結版 |
| `scripts/extract-screens.sh` | 從單檔 HTML 以關鍵字取證，避免整份讀入 context |
| `scripts/check-js.sh` | 以 `node --check` 檢查 mockup 內 inline script 的語法，錯誤行號對應 HTML 行號；builder 自查與 inline 微修用 |
| `scripts/serve-mockup.sh` | 以本機 http server 開啟凍結的 mockup，供操作驗證 |
| `scripts/pack-sdd-handoff.sh` | 步驟 7：前提機械檢查，把 v<N> 打包成開發 repo 的 `.specify/context/` 結構、代入範本、產生規格來源索引 `index.md` |

依賴同目錄的 `make-storyboard` skill（步驟 1 與 6 以 Read 方式 inline 執行）。

---

## 範例

以「水滸傳人物時間軸」為題實際跑完的產物（v1 → v2 升版的 Design Brief、回饋紀錄、凍結的 mockup，以及步驟 7 的 SDD 交接包）：
[chengfulin/demo_skill_make-mockup-harness](https://github.com/chengfulin/demo_skill_make-mockup-harness/tree/main)

---

## 前置需求

- 目標 repo 需為 git repo（產物逐階段 commit）。
- Claude Code 可使用 Artifacts（Pro／Max／Team／Enterprise、以 claude.ai 帳號登入、Anthropic API；
  不支援 Bedrock／Vertex／Foundry、ZDR 組織與 `-p` 模式）。步驟 3、4 用它發布 mockup 與收留言。
- Claude in Chrome 擴充功能（步驟 5、7 用來在本機實際操作凍結的 mockup 與截圖）。
- 設計系統為選配：repo 內的 tokens／theme 檔，或已遷移到 Claude 的設計系統 artifact。

## 安裝

```bash
bash skills/make-mockup-harness/scripts/install.sh
```

冪等安裝：把 `skills/make-mockup-harness` symlink 到 `~/.claude/skills/`、`agents/*.md` 逐檔 symlink 到
`~/.claude/agents/`（Claude Code 只從該處載入 subagent）；同 repo 的 `make-storyboard` 尚未安裝時一併連上。
重複執行安全；repo 移動位置後重跑即可修復連結。執行中的 session 要到下一輪對話才會載入新裝的 agent
（2026-10-21 實測：同一輪派遣回 not found，下一輪即可用）；步驟 0 的 `check_agents` 只檢查檔案存在。

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
├── briefs/v<N>-research.md    # 假資料涉及真實事實時的查證結果與來源（沒有就不產）
├── mockup-src/index.html      # 發布用工作檔＝目前採用的 build 快照（發布到同一 artifact，隨凍結 commit 入版）
├── mockup-src/builds.md       # build 索引：模式、base、摘要、sha256、artifact 版本 id、狀態
├── mockup-src/builds/v<N>-b<kk>/  # 每次產出一組：request.md（輸入）、index.html（快照）、build.md（產出紀錄）
├── mockups/v<N>/index.html    # 凍結版 + export.json（來源網址、版本 id、build id、sha256）
├── reviews/v<N>-consistency.md
├── feedback/                  # artifact 留言、客戶回饋
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
    └── <slug>/v<N>/{index.md, storyboard.md, sdd-input.md, prototype/, reference/}
```

開發者把 `.specify/context/` 複製進開發 repo、commit，依 `SDD-START.md` 啟動 sdd-harness 即可，不需要本 skill。
開發完成後交回 `handback-to-sa.md`，SA 以步驟 6 升版。做 mockup 與做開發可以是不同人。

## 設計決策

- storyboard 是唯一真相；mockup 每版對應 storyboard 變更紀錄一列，commit 後凍結。
- mockup 由 Claude Code 依 brief 直接寫成互動 HTML，發布成私人 artifact 給 SA／客戶檢視與留言；
  凍結時從 artifact 取回已發布的檔案。全程用正式工具（Artifact、ArtifactComments），不靠操作網頁或未公開的 API。
- 原本透過 Chrome 操作 claude.ai/design，因該網站於 2026-12-14 關閉而改版（2026-10-19 以同一份 brief 驗證兩條路徑結果一致）。
- `/design` 是 slash command，只能由使用者輸入，產出是 artboard 畫布、只能匯出 PNG／PDF，
  接不上凍結與操作驗證，只當選配的視覺參考。
- 每個畫面標 `data-page`，檢核與截圖都靠它定位；操作驗證在本機開啟凍結檔做，驗的是 repo 裡的版本。
- brief 推導與一致性檢核交給獨立 subagent，mockup 由主對話製作：產出者與驗收者不同 context，
  主對話做了 mockup 就不能自己檢核。模型預設 sonnet + high，只在 v1 brief（畫面拆解屬架構判斷）與
  交接版檢核（交接後鎖定、誤判代價最高）逐次升 opus；effort 無法逐次覆寫，所以需要自訂 agent 定義檔。
  subagent 不問使用者、不派 subagent，問題整理成選項交回 orchestrator 轉問。
  改版時以既有專案回歸驗證：製作者自檢的報告全數通過，獨立 checker 以較少的操作數抓到自檢漏掉的
  反向案例（已成立狀態下再操作一次），因此 checker 定義檔要求互動規則測正反兩面。
