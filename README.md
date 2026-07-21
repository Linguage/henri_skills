# Henri Skills

个人 AI agent skills 合集。本仓库是唯一源；Claude Code、OpenCode、`.agents`、Codex 等通过符号链接消费。

## 架构

```
henri_skills/                              ← 源仓库（本仓库）
  ↑
~/.claude/skills/          → henri_skills/ ← 全局目录级符号链接
~/.config/opencode/skills/ → henri_skills/
~/.agents/skills/          → henri_skills/

~/.codex/skills/<skill>/ → henri_skills/<skill>/  ← Codex 按 skill 软链接
                                                       （保留 .system 系统技能）

~/Downloads/.claude/skills/organize-downloads → …/organize-downloads/
<project>/.claude/skills/<skill>/ → henri_skills/<skill>/  ← 项目级（按需）
```

- **henri_skills** 是所有 skills 的唯一源仓库，所有修改都在此进行
- Claude / OpenCode / `.agents`：整目录指向本仓库
- Codex：因需保留 `~/.codex/skills/.system`，只能按 skill 软链接；新增或迁入仓库后需手动补链
- 不要在任何链接路径下直接编辑

当前机器上 Codex 已链接：`henri-writing-style`。

## Skills 列表

### 原创

| Skill | 作者 | 说明 |
|-------|------|------|
| [academic-latex-pdf](academic-latex-pdf/) | henri | 将学术 Markdown 排版为可复现的 LaTeX / PDF |
| [ai-tools-management](ai-tools-management/) | henri | 扫描、清理、备份和卸载 macOS 上的 AI 开发工具 |
| [doc-system-scaffold](doc-system-scaffold/) | henri | 一键搭建项目文档系统骨架 |
| [henri-writing-style](henri-writing-style/) | henri | 按条款整理口述、审查中文，保留作者原表述 |
| [organize-downloads](organize-downloads/) | henri | 整理下载目录：分类、书库对账、OCR、清单与迁移 |
| [testing-sdk-models](testing-sdk-models/) | henri | 测试 Claude Agent SDK 对各模型 provider 的连通性 |
| [work-notes-pipeline](work-notes-pipeline/) | henri | 编写会话总结，或将工作笔记改写为叙述性文章 |

### 第三方

| Skill | 原作者 | 说明 |
|-------|--------|------|
| [health](health/) | [Tw93](https://github.com/tw93)（[claude-health](https://github.com/tw93/claude-health)） | 审计 agent 配置各层健康状态 |
| [baoyu-youtube-transcript](baoyu-youtube-transcript/) | [JimLiu](https://github.com/JimLiu)（[baoyu-skills](https://github.com/JimLiu/baoyu-skills)） | 下载 YouTube 字幕/封面等 |

`created` 为该 `SKILL.md` **首次进入本仓库**的 Git 提交日（`git log --reverse --format=%cs -- <path> | head -1`）。`last_updated` 取**最近一次非 `2026-04-12`** 的提交；若除去该日后无记录则省略。有上游的另含 `source` / `author` / `modifications`。

## 新增 Skill

1. 在本仓库下创建目录：`<skill-name>/SKILL.md`
2. 含 YAML frontmatter（`name`、`description`、`author`、`created`）
3. 在 frontmatter 后添加「单一来源」声明
4. 更新本 README 的原创 / 第三方表
5. Claude / OpenCode / `.agents` 经目录级链接自动可见；若需在 Codex 使用，再执行：

   ```bash
   ln -s "$HOME/settings/henri_skills/<skill-name>" ~/.codex/skills/<skill-name>
   ```

配置细节见 [Agents.md](Agents.md#配置方式)。
