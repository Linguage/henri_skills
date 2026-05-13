---
title: Skills 仓库健康检查与精简重构
date: "2026-05-13"
created: "2026-05-13T15:17:00"
category: worknotes
tags:
  - skills
  - health-check
  - 精简
  - 软链接
  - 仓库管理
---

# Skills 仓库健康检查与精简重构

**日期**：2026-05-13

本轮工作对 `henri_skills` 仓库执行了一次全面的健康检查，发现了三重复制、skill 膨胀、description 过长等问题，随后完成了目录统一、内容精简、skill 合并与降级等修复。

## 1. 背景与动机

用户提出 skills 配置可能过于臃肿，要求使用 health skill 进行诊断。当时 8 个 skill 被完整复制到 3 个目录（`~/.claude/skills/`、`~/.config/opencode/skills/`、`~/.agents/skills/`），共 20 个 SKILL.md 文件，总计约 8,922 词。没有任何符号链接，所有副本独立存在，编辑一处后其余两处静默漂移。

## 2. 健康检查发现

按 health skill 的四层诊断流程启动了 4 个并行 subagent，发现：

- **🔴 三重复制无 symlink**：每次编辑需同步 2-3 个位置，已有漂移案例（find-skills 和 health 在 `~/.agents/skills/` 中缺少 frontmatter 字段）
- **🔴 总 context 开销偏高**：约 12,000 tokens（占 200K 窗口的 6%），7/8 的 description 超过 12 词
- **🟡 膨胀 skill**：doc-system-scaffold（411 行，大量内联模板）、health（387 行，4 个完整 agent prompt 内联）、ai-tools-management（514 行，冗余安全规则和工作流段）
- **🟡 可合并**：session-summary-writer 和 rewriting-worknotes-to-articles 同属 work-notes 管线
- **🟡 可降级**：find-skills 的核心内容只有 3 行 CLI 命令，不适合占用一个 skill 位

## 3. 修复措施

### 3.1 目录统一

选定 `~/Documents/ZCode/projects/henri_skills/`（已有的 Git 仓库）为唯一实体目录。将 `~/.claude/skills/`、`~/.config/opencode/skills/`、`~/.agents/skills/` 三个目录备份后替换为指向 `henri_skills` 的符号链接。旧目录备份为 `*.bak.20260513`。

确认 canonical 版本（4 月 12 日）比 `~/.agents/skills/` 中的副本（3 月 13 日）更新，无需反向同步。

### 3.2 Skill 精简

| Skill | 修复前 | 修复后 | 操作 |
|-------|--------|--------|------|
| doc-system-scaffold | 411 行 | 98 行 | 11 个文档模板提取到 `templates/` 目录，SKILL.md 改为引用表格 |
| health | 387 行 | 224 行 | 4 个 subagent prompt 提取到 `prompts/` 目录，Step 3 改为按需读取 |
| ai-tools-management | 514 行 | 469 行 | 安全规则从 9 条精简为 3 条，删除 Interaction Workflow、Adding New Tools、Dry-run 模板段 |

### 3.3 Skill 合并

将 `session-summary-writer`（85 行）和 `rewriting-worknotes-to-articles`（89 行）合并为 `work-notes-pipeline`（116 行），通过 mode 参数区分 summary 和 article 两种工作模式。去重了共享的目录解析逻辑和 frontmatter 约定。合并后删除两个原始 skill 目录。

### 3.4 Skill 降级

删除 `find-skills` skill（138 行），其核心内容（3 行 CLI 命令）写入 `~/.claude/CLAUDE.md` 的 Skills CLI 小节。

### 3.5 Description 优化

所有保留 skill 的 description 缩减至 ≤14 词：

| Skill | 修复前 | 修复后 |
|-------|--------|--------|
| ai-tools-management | 36 词 | 11 词 |
| baoyu-youtube-transcript | 60 词 | 12 词 |
| health | 20 词 | 14 词 |
| testing-sdk-models | 31 词 | 10 词 |

### 3.6 单一来源声明

在每个 skill 的 frontmatter 之后、正文之前，添加 blockquote 声明该 skill 的唯一实体在 `henri_skills` 仓库中，提醒编辑时直接修改仓库文件。

本设备的实际路径（`~/Documents/ZCode/projects/henri_skills/`）及软链接关系记录在 `~/.claude/CLAUDE.md` 中，不在 skill 内硬编码。

### 3.7 创建全局 CLAUDE.md

新建 `~/.claude/CLAUDE.md`，包含全局偏好、Skills 管理约定（路径与软链接关系）和 Skills CLI 命令。

## 4. 成果对比

| 指标 | 修复前 | 修复后 | 变化 |
|------|--------|--------|------|
| Skill 数量 | 8 | 6 | -25% |
| 总词数 | 8,922 | 6,256 | -30% |
| SKILL.md 文件数 | 20（三重复制） | 6（单源 + symlink） | -70% |
| 估算 tokens | ~12,000 | ~8,100 | -33% |

## 5. 当前状态与未决事项

- 所有修复已写入 `henri_skills` 仓库，通过 symlink 对所有工具链（opencode、claude code、agents）即时生效
- 旧目录备份仍在磁盘上（`~/.claude/skills.bak.20260513` 等），确认无问题后可手动删除
- `henri_skills` 仓库的变更尚未 git commit
- `doc-system-scaffold` 的 `templates/` 目录和 `health` 的 `prompts/` 目录需要验证在实际触发时能被正确读取
- `work-notes-pipeline` 的 `references/` 目录已从原始 skill 迁移，`agents/` 目录已更新
- README.md 尚未更新（需反映 skill 列表从 8 个变为 6 个）
