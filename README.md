# Henri Skills

个人 AI agent skills 合集，通过目录级符号链接供 Claude Code、opencode 等工具使用。

## 架构

```
henri_skills/                              ← 源仓库（本仓库）
  ↑
~/.claude/skills/          → henri_skills/ ← 全局符号链接
~/.config/opencode/skills/ → henri_skills/
~/.agents/skills/          → henri_skills/

<project>/.claude/skills/<skill>/ → henri_skills/<skill>/  ← 项目级符号链接
```

- **henri_skills** 是所有 skills 的唯一源仓库，所有修改都在此进行
- 三个消费端目录均为指向本仓库的符号链接，不要在链接路径下直接编辑

## Skills 列表

### 原创

| Skill | 作者 | 说明 |
|-------|------|------|
| [ai-tools-management](ai-tools-management/) | henri | 扫描、清理、备份和卸载 macOS 上的 AI 开发工具 |
| [doc-system-scaffold](doc-system-scaffold/) | henri | 一键搭建项目文档系统骨架 |
| [organize-downloads](organize-downloads/) | henri | 整理 Downloads 目录：文件分类、书籍归档、图片来源识别、PDF 重命名 |
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
4. 通过符号链接自动对所有工具链生效（配置方式详见 [Agents.md](Agents.md#配置方式)）
