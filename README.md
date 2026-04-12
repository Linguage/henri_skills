# Henri Skills

个人 Claude Code Skills 合集。

## 架构

```
henri_skills/                          ← 源仓库（本仓库）
  ↑
~/.cc-switch/skills → henri_skills/    ← 目录级符号链接
  ↑
~/.claude/skills/<name> → ~/.cc-switch/skills/<name>
```

- **henri_skills** 是所有 skills 的唯一源仓库
- **cc-switch** ([farion1231/cc-switch](https://github.com/farion1231/cc-switch)) 通过目录符号链接引用本仓库
- **.claude/skills** 逐个链接到 cc-switch 中的 skill

## Skills 列表

### 原创

| Skill | 作者 | 说明 |
|-------|------|------|
| [ai-tools-management](ai-tools-management/) | henri | 扫描、备份、清理和卸载 macOS 上的 AI 开发工具 |
| [doc-system-scaffold](doc-system-scaffold/) | henri | 一键搭建项目文档系统骨架 |
| [rewriting-worknotes-to-articles](rewriting-worknotes-to-articles/) | henri | 将工作笔记改写为叙述性反思文章 |
| [session-summary-writer](session-summary-writer/) | henri | 为编码会话编写工作总结文档 |
| [testing-sdk-models](testing-sdk-models/) | henri | 测试 Claude Agent SDK 对各模型 provider 的连通性 |

### 第三方

| Skill | 原作者 | 说明 |
|-------|--------|------|
| [find-skills](find-skills/) | [Tw93](https://github.com/tw93)（[claude-health](https://github.com/tw93/claude-health)） | 发现并安装 agent skills |
| [health](health/) | [Tw93](https://github.com/tw93)（[claude-health](https://github.com/tw93/claude-health)） | 审计 Claude Code 各层配置健康状态 |
| [baoyu-youtube-transcript](baoyu-youtube-transcript/) | [JimLiu](https://github.com/JimLiu)（[baoyu-skills](https://github.com/JimLiu/baoyu-skills)） | 下载 YouTube 字幕/封面等 |

`created` 为该 `SKILL.md` **首次进入本仓库**的 Git 提交日（`git log --reverse --format=%cs -- <path> | head -1`）。`last_updated` 取**最近一次非 `2026-04-12`** 的提交；若除去该日后无记录则省略。有上游的另含 `source` / `author` / `modifications`。目录引用见 [farion1231/cc-switch](https://github.com/farion1231/cc-switch)。

## 新增 Skill

1. 在本仓库下创建目录：`<skill-name>/SKILL.md`
2. 通过 `cc-switch → henri_skills` 的符号链接自动生效
3. 在 `~/.claude/skills/` 中添加对应的符号链接：
   ```bash
   ln -s ~/.cc-switch/skills/<skill-name> ~/.claude/skills/<skill-name>
   ```
