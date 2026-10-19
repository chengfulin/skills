# skills

個人維護的 [Claude Code](https://claude.com/claude-code) Skills 與 Agents 集合。

## 目錄結構

```
.
├── skills/          # Skill 定義，每個 skill 一個資料夾，內含 SKILL.md
│   └── tech-mentor/
├── agents/          # Subagent 定義（預留）
└── LICENSE
```

## Skills 一覽

| Skill | 說明 |
| --- | --- |
| [tech-mentor](skills/tech-mentor/) | 以資深工程師帶 junior 的視角，將技術主題整理成由概念到細節的分層 HTML 教學頁 |

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

## 新增 Skill

1. 在 `skills/` 下建立以 skill 名稱命名的資料夾
2. 撰寫 `SKILL.md`，frontmatter 至少包含 `name` 與 `description`
3. 為該 skill 補上 `README.md`，並更新本文件的「Skills 一覽」

## License

[MIT](LICENSE)
