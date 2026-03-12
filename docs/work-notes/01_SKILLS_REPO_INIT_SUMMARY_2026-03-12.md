# Skills 仓库初始化与管理架构建立

**日期**：2026-03-12

本次会话完成了个人 Claude Code skills 的统一管理架构搭建，将分散在不同位置的 skills 集中到一个 Git 仓库中，并通过符号链接链路实现注册。

## 1. 背景与动机

此前 skills 文件分散在 `~/.cc-switch/skills/` 和 `~/.claude/skills/` 中，缺乏版本管理和统一入口。需要一个集中的仓库来管理自己创建的 skills，同时保持与 cc-switch 配置管理工具的兼容。

## 2. 确立的管理架构

最终确定的三层符号链接架构：

```
henri_skills/                          ← 源仓库（Git 管理）
  ↑
~/.cc-switch/skills → henri_skills/    ← 目录级符号链接
  ↑
~/.claude/skills/<name> → ~/.cc-switch/skills/<name>
```

设计原则：
- **henri_skills** 是所有 skills 的唯一源仓库，所有修改都在此进行
- **cc-switch** 通过目录级符号链接整体引用 henri_skills，负责配置管理
- **.claude/skills** 按 skill 逐个链接到 cc-switch，是 Claude Code 的注册入口

## 3. 新增的 ai-tools-management Skill

基于已有的设计文档（`ai-cleaner-design.md`）和 skill 草稿（`SKILL-ai-tools-management.md`），微调并注册了 `ai-tools-management` skill。主要调整：

- 添加了符合 skill 格式的 frontmatter（name + description）
- 精简内容，去掉 GUI 设计和开发路线图等与 skill 无关的部分
- 修正了 Claude Code 的实际数据路径（补充 `projects/`、`skills/` 等目录）
- 移除了信息不充分的 AMP/Gemini 条目

## 4. 仓库结构

```
henri_skills/
├── CLAUDE.md
├── README.md
├── .gitignore
├── ai-tools-management/SKILL.md
├── session-summary-writer/SKILL.md + agents/ + references/
├── rewriting-worknotes-to-articles/SKILL.md + agents/ + references/
└── docs/work-notes/
```

## 5. 已完成的操作

- 初始化 Git 仓库并推送到 GitHub（Linguage/henri_skills，公开仓库）
- 创建 `ai-tools-management` skill 并注册
- 建立完整的三层符号链接架构
- 迁移已有的 `session-summary-writer` 和 `rewriting-worknotes-to-articles` 到统一链路
- 创建 README.md（中文）和 CLAUDE.md

## 6. 当前状态与待办

- 三个 skills 已全部通过符号链接链路正常注册
- GitHub 仓库已创建但 README.md、CLAUDE.md 和本工作总结尚未推送
- `ai-tools-management` skill 尚未在实际场景中测试验证
