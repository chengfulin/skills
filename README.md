# skills

個人維護的 [Claude Code](https://claude.com/claude-code) Skills 與 Agents 集合。

## 目錄結構

```
.
├── skills/          # Skill 定義，每個 skill 一個資料夾，內含 SKILL.md
│   ├── git-commit/
│   ├── make-mockup-harness/ # 內含 agents/：該 skill 專用的兩個 subagent（以 scripts/install.sh 安裝）
│   ├── make-storyboard/
│   ├── sdd-baseline/
│   ├── sdd-harness/         # 內含 agents/：該 skill 專用的六個 subagent（以 scripts/install.sh 安裝）
│   ├── shallow-to-deep/
│   └── tech-mentor/
└── LICENSE
```

## Skills 一覽

| Skill | 說明 |
| --- | --- |
| [git-commit](skills/git-commit/) | 依 Angular 格式與繁體中文規範整理變更並建立 git commit |
| [make-mockup-harness](skills/make-mockup-harness/) | 以 orchestrator 帶 SA 從需求走到可互動 Mockup：Story Board → Design Brief → 互動 mockup（artifact）→ 凍結版本 → 一致性檢核 → 升版，可選打包中性的開發交接包 |
| [make-storyboard](skills/make-storyboard/) | 以主任 SA 視角帶 junior SA 釐清需求，產出可直接轉成互動 Mockup 的 Story Board，支援依回饋升版 |
| [sdd-baseline](skills/sdd-baseline/) | 團隊 SDD 憲章基線的參考型 skill：SDD 開始前依專案類型、風險因子、應用類型與團隊成熟度決定風險分級、導入階段與載入文件，也可查條款、同步基線副本 |
| [sdd-harness](skills/sdd-harness/) | 以 GitHub spec-kit 執行 SDD 全流程的 orchestrator：init → 憲章 → 規格 → 釐清 → 計畫 → 任務 → 一致性分析 → 實作，六個獨立 subagent 把關、每階段 commit、可續跑 |
| [shallow-to-deep](skills/shallow-to-deep/) | 由淺入深的圖解指引：同主題先產白話大圖版、再產工程師分層版，合併成一份 HTML artifact |
| [tech-mentor](skills/tech-mentor/) | 以資深工程師帶 junior 的視角，將技術主題整理成由概念到細節的分層 HTML 教學頁 |

## 使用範例

| Skill | 範例 repo |
| --- | --- |
| [make-mockup-harness](skills/make-mockup-harness/) | [demo_skill_make-mockup-harness](https://github.com/chengfulin/demo_skill_make-mockup-harness/tree/main) |

## 安裝

將需要的 skill 資料夾複製（或 symlink）到 Claude Code 的 skills 目錄：

```bash
git clone https://github.com/chengfulin/skills.git
cd skills

# 個人層級（所有專案可用）
ln -s "$(pwd)/skills/tech-mentor" ~/.claude/skills/tech-mentor

# 或專案層級（僅該專案可用）
mkdir -p /path/to/project/.claude/skills
cp -r skills/tech-mentor /path/to/project/.claude/skills/
```

安裝後在 Claude Code 中輸入 `/<skill-name>` 即可呼叫，或由 Claude 依描述自動判斷使用時機。

帶有 subagent 的 skill（`sdd-harness`、`make-mockup-harness`）另需把 `agents/*.md` 連到 `~/.claude/agents/`，
Claude Code 才找得到它們；用該 skill 的安裝腳本一次處理 skill、agents 與它預設依賴的同 repo skill
（`sdd-baseline`、`make-storyboard`）：

```bash
bash skills/sdd-harness/scripts/install.sh
bash skills/make-mockup-harness/scripts/install.sh
```

## 新增 Skill

1. 在 `skills/` 下建立以 skill 名稱命名的資料夾
2. 撰寫 `SKILL.md`，frontmatter 至少包含 `name` 與 `description`
3. 為該 skill 補上 `README.md`，並更新本文件的「Skills 一覽」

## 授權與使用說明

本 repo 是個人實驗 skill 的整理與紀錄，以 [MIT](LICENSE) 授權分享：歡迎自由取用、修改、整合進自己的專案，只需保留版權聲明。

- **實驗性質**：內容會隨實驗持續調整，尚未定版，也不保證向後相容；建議複製一份到自己的環境再依需求修改。
- **第三方來源**：改寫自他人作品的 skill，會在該 skill 的 README 註明出處與原授權，取用時請一併遵守原授權。
