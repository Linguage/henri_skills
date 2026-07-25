---
title: Skills 路径迁移与软链接收敛
date: "2026-05-15"
created: "2026-05-15T17:47:34+0800"
category: worknotes
tags:
  - skills
  - symlink
  - settings
  - Codex
  - Claude
---

# Skills 路径迁移与软链接收敛

**日期**：2026-05-15

本轮工作把个人 skills 仓库从 `Documents` 下迁移到 `~/settings/henri_skills`，并取消 `cc-switch` 作为中间层。调整的直接背景是：在 Codex 中读取 `Documents/ZCode/projects/henri_skills` 下的 skill 文件时，macOS 隐私权限层多次返回 `Operation not permitted`，导致 `work-notes-pipeline` 虽然在会话可用列表中出现，但正文无法被读取，进而引发了错误的 work note 写法。

## 1. 问题来源

此前 skills 的真实仓库位于：

`~/Documents/ZCode/projects/henri_skills`

并通过一层 `cc-switch` 链路暴露给不同工具。实际结构曾经是：

`~/.cc-switch/skills -> ~/Documents/ZCode/projects/henri_skills`

Codex、Claude、agents 等工具再从各自目录链接到这一层。

这个结构有两个问题。第一，`Documents` 属于 macOS TCC 隐私保护路径，即使 Unix 权限显示可读，应用进程仍可能读文件失败。第二，`cc-switch` 作为中间层增加了认知成本，后续迁移时容易出现旧路径、断链和备份目录残留。

## 2. 恢复云端版本

迁移过程中先把 `henri_skills` 现有仓库移动到：

`~/settings/henri_skills`

随后对该仓库执行云端恢复：

- `git fetch origin`
- `git reset --hard origin/main`
- `git clean -fd`

这样恢复了云端版本中存在但本地一度缺失的 skill，包括：

- `work-notes-pipeline`
- `organize-downloads`

恢复后确认 `work-notes-pipeline/SKILL.md` 可以从新路径直接读取。

## 3. 取消 cc-switch 中间层

本次明确不再使用 `cc-switch` 管理 skills。已移除：

`~/.cc-switch/skills`

新的全局软链接结构为：

```text
~/.claude/skills          -> ~/settings/henri_skills
~/.agents/skills          -> ~/settings/henri_skills
~/.config/opencode/skills -> ~/settings/henri_skills
```

Codex 由于 `~/.codex/skills` 目录中还包含 `.system` skills，因此保留目录本身，只把用户 skill 逐项直连到新仓库：

```text
~/.codex/skills/<skill-name> -> ~/settings/henri_skills/<skill-name>
```

同时保留项目级链接：

```text
~/Downloads/.claude/skills/organize-downloads
-> ~/settings/henri_skills/organize-downloads
```

## 4. 清理旧路径与断链

本轮还处理了历史残留链接：

- `~/.agents/skills` 与 `~/.claude/skills` 从旧 `Documents` 路径改为新路径。
- `~/.config/opencode/skills` 从旧路径改为新路径。
- `~/.codex/skills/*` 不再经过 `~/.cc-switch/skills`。
- `~/.claude/skills.bak.20260513`、`~/.agents/skills.bak.20260513`、`~/.config/opencode/skills.bak.20260513` 中能对应到现有 skill 的链接改到新路径。
- 云端仓库已经不存在的旧 skill 链接被删除。

同时更新了活跃配置中的旧路径引用：

- `~/.codex/config.toml`
- `~/.claude/CLAUDE.md`
- `~/.claude/projects/-Users-henripogatrain-Documents-ZCode/memory/feedback_skills_management.md`
- `~/settings/henri_skills/Agents.md`

## 5. 相关 settings 迁移

同一轮配置治理中，也把 Vim 与 Emacs 配置迁移到 `~/settings` 下，避免继续散落在 home 根目录：

```text
~/settings/vim_settings
~/settings/henri.emacs.d
```

当前入口为：

```text
~/.vim          -> ~/settings/vim_settings
~/.vimrc        -> ~/settings/vim_settings/vimrc
~/.gvimrc       -> ~/settings/vim_settings/vimrc
~/.config/emacs -> ~/settings/henri.emacs.d
```

并同步修正了 Journal 中指向 Emacs LaTeX 字体目录的旧链接。

## 6. 验证结果

已确认：

- `~/.cc-switch/skills` 已不存在。
- `~/.claude/skills`、`~/.agents/skills`、`~/.config/opencode/skills` 均直接指向 `~/settings/henri_skills`。
- `~/.codex/skills` 下的用户 skill 均直接指向 `~/settings/henri_skills/<skill-name>`。
- `work-notes-pipeline/SKILL.md` 可以通过 Codex 链路读取。
- 定向检查未发现已知 skills 目录中仍有指向 `.cc-switch/skills` 或旧 `Documents/.../henri_skills` 的软链接。
- Vim 与 Emacs 的实际入口均解析到 `~/settings` 下的新位置。

## 7. 当前状态与未决事项

`henri_skills` 当前仍有本地修改，主要是 `Agents.md` 路径更新以及本工作记录。该变更尚未提交。

需要注意的是，历史日志文件中仍可能出现旧路径，这是历史记录，不应批量改写。后续如果继续新增 skill，应直接在：

`~/settings/henri_skills/<skill-name>/SKILL.md`

中编辑，并让各工具通过软链接读取同一个实体。
