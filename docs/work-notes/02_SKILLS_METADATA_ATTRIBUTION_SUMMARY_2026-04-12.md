---
title: Skills 元数据、署名与 README 分层整理
date: "2026-04-12"
created: "2026-04-12T20:30:00"
category: worknotes
tags:
  - skills
  - frontmatter
  - attribution
  - README
  - 文档规范
---

# Skills 元数据、署名与 README 分层整理

**日期**：2026-04-12

本轮工作把「谁写的、是否改自上游、何时入库与更新」收敛成可维护的约定，避免在正文里堆长段致谢，同时让 README 一眼区分原创与第三方。

## 1. 背景与目标

需要标明部分 Skill 来自第三方上游，并说明本仓库副本可能相对上游有改动；此前若在正文或 README 里写得太细，容易与「只改 frontmatter」的期望冲突。目标是：**署名与修改说明主要在 YAML frontmatter**，README 只做索引级区分；日期字段尽量与 **Git 历史**一致，避免手写占位日误导。

## 2. 第三方 Skill 的 frontmatter 约定

对 `find-skills`、`health`、`baoyu-youtube-transcript` 统一保留：

- `source`：上游仓库链接  
- `author`：上游维护者（Tw93 / JimLiu）  
- `modifications`：一句说明——本 Skill 可能是在原作者 Skill 的基础上进行了修改  

不在各 Skill 正文里重复长表格或长段来源说明（与后续「仅 frontmatter」要求一致）。

## 3. 日期字段：`created` 与 `last_updated`

- **`created`**：该 `SKILL.md` **首次进入本仓库**的提交日（`git log --reverse --format=%cs -- <path> | head -1`），保留真实首次提交日（含批量导入日）。  
- **`last_updated`**：在该文件历史上取**最近一次非 `2026-04-12`** 的提交日；该日曾用于批量元数据提交，按约定不计入「最近内容更新」。若除去该日后无记录则**省略**该字段。  

据此为各 Skill 填过一轮；个别文件的 `created` 若与用户本地后续提交不一致，应以当前仓库 `git log` 为准再对齐。

## 4. README：原创与第三方分表

`README.md` 中 Skills 列表拆为两张表：

- **原创**：作者列统一为 **henri**（与 frontmatter 中 `author: Henri` 对应，README 表格为小写 henri）。  
- **第三方**：原作者 + 上游仓库链接，便于与 frontmatter 对照。  

文末保留对 `created` / `last_updated` 规则及 `source` / `author` / `modifications` 的简短说明。

## 5. 原创 Skill 的 `author: Henri`

在以下原创 Skill 的 frontmatter 中增加 **`author: Henri`**（与第三方共用字段名，语义为本仓库原创作者）：

- `ai-tools-management`  
- `doc-system-scaffold`  
- `rewriting-worknotes-to-articles`  
- `session-summary-writer`  
- `testing-sdk-models`  

第三方 Skill 仍使用上游 `author`，未改。

## 6. CLAUDE.md：项目管理基本要求

在 `CLAUDE.md` 增加 **Skills project management (this repo)** 小节，提炼为可执行约定，包括：仅在本仓库编辑、原创与第三方的 frontmatter 分工、`created` / `last_updated` 与 README 双表同步、署名不重复堆在正文等。

## 7. 验证与文档

- 未运行自动化测试；变更为 Markdown 与 frontmatter，以人工核对与 `git log` 为准。  
- 本笔记遵循 `session-summary-writer/references/work-notes-style.md` 的编号摘要风格。

## 8. 当前状态与未决事项

- 工作区仍存在**未提交修改**（`CLAUDE.md`、`README.md` 及多个 `SKILL.md`），需要用户自行 `git add` / `commit`。  
- 第三方 Skill 与上游的同步策略仍以各 Skill 正文或上游仓库说明为准；`health` 内已有面向 `claude-health` 的更新检查提示，未在本轮改动。  
- 若今后放弃「排除 `2026-04-12`」这条特殊规则，应同步改 `README.md` 与 `CLAUDE.md`，并批量重算 `last_updated`。
