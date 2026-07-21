---
title: Skills 管理文档同步与 henri-writing-style 入库
date: "2026-07-21"
created: "2026-07-21T10:45:00+0800"
category: worknotes
tags:
  - skills
  - symlink
  - Codex
  - README
  - Agents.md
---

# Skills 管理文档同步与 henri-writing-style 入库

**日期**：2026-07-21

本轮把仍只存在于 Codex 本地的 `henri-writing-style` 迁入 `henri_skills`，并按现行消费链路改成软链接；同时更新仓库管理文档，使 README / Agents.md 与实际目录、链接方式一致。

## 1. 背景

盘点 `~/.codex/skills` 后确认：

- `.system/` 下的平台技能（imagegen、openai-docs、plugin-creator、review-agent、skill-creator、skill-installer）属于 Codex 专属，不应迁入本仓库。
- 用户自建的 `henri-writing-style` 此前只在 `~/.codex/skills/` 有实体副本，未进入 `henri_skills`，与「单一来源」约定不一致。
- Claude / OpenCode / `.agents` 已是整目录软链接；Codex 因保留 `.system`，只能按 skill 链接。管理文档此前对 Codex 侧写得不够完整，且 README 技能表落后于仓库现状。

## 2. 已完成变更

### 2.1 `henri-writing-style` 入库

- 实体迁入 `henri_skills/henri-writing-style/`（`SKILL.md`、`agents/`、`references/`）。
- 补全 `author` / `created` / `last_updated` 与「单一来源」声明。
- `~/.codex/skills/henri-writing-style` 改为指向仓库的软链接。
- 迁入前原目录备份为 `~/.codex/archived-skills/henri-writing-style-pre-symlink-2026-07-21`。

### 2.2 管理文档

- **README.md**：补全架构图（含 Codex、Downloads 项目级链接）；原创表增加 `academic-latex-pdf`、`henri-writing-style`；更新 `organize-downloads` 说明；写明 Codex 需手动补链；记录当前已链接项。
- **Agents.md**：开篇改为多消费端仓库说明；约定中补充 Codex 链接职责与推荐「单一来源」措辞；配置步骤增加 Codex 检测与按 skill 链接；`REPO` 路径统一为 `$HOME/settings/henri_skills`。

### 2.3 登记一致性

- 为仓库内已有、但此前未入表的 `academic-latex-pdf` 补 frontmatter（`author` / `created` / `last_updated`）与「单一来源」声明，并写入 README 原创表。

## 3. 当前消费链路（本机）

| 消费端 | 方式 | 状态 |
|--------|------|------|
| `~/.claude/skills` | 目录级 → `henri_skills` | 已生效 |
| `~/.agents/skills` | 目录级 → `henri_skills` | 已生效 |
| `~/.config/opencode/skills` | 目录级 → `henri_skills` | 已生效 |
| `~/.codex/skills/henri-writing-style` | 按 skill → 仓库同名目录 | 已生效 |
| `~/Downloads/.claude/skills/organize-downloads` | 项目级 | 已生效 |

## 4. 未收口事项

- `organize-downloads` 自 2026-07-19/20 起有大量未提交改动（新 phase 文档、`apply_move_plan.py` 等）；管理文档已按能力更新简述，但技能本体尚未 commit。
- `academic-latex-pdf`、`henri-writing-style` 目前为工作区新增/迁入内容，尚未 commit。
- 若 Codex 还需要 `academic-latex-pdf` 等其它仓库技能，需按 Agents.md 追加软链接（文档中已留示例，本机尚未全部链接）。
- 各 skill 正文里旧的「单一来源」短句（只提 `~/.claude/skills/`）尚未批量改成含 Codex 的推荐措辞；新迁入/新登记的已用新措辞。

## 5. 验证

- `readlink ~/.codex/skills/henri-writing-style` 指向 `~/settings/henri_skills/henri-writing-style`。
- 经该链接可读取 `SKILL.md`；经 `~/.claude/skills/henri-writing-style` 同样可见（目录级链接连带生效）。
