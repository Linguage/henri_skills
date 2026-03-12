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
- **cc-switch** 通过目录符号链接引用本仓库
- **.claude/skills** 逐个链接到 cc-switch 中的 skill

## Skills 列表

| Skill | 说明 |
|-------|------|
| [ai-tools-management](ai-tools-management/) | 扫描、备份、清理和卸载 macOS 上的 AI 开发工具 |
| [session-summary-writer](session-summary-writer/) | 为编码会话编写工作总结文档 |
| [rewriting-worknotes-to-articles](rewriting-worknotes-to-articles/) | 将工作笔记改写为叙述性反思文章 |

## 新增 Skill

1. 在本仓库下创建目录：`<skill-name>/SKILL.md`
2. 通过 `cc-switch → henri_skills` 的符号链接自动生效
3. 在 `~/.claude/skills/` 中添加对应的符号链接：
   ```bash
   ln -s ~/.cc-switch/skills/<skill-name> ~/.claude/skills/<skill-name>
   ```
