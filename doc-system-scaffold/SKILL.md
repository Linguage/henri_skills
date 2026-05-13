---
name: doc-system-scaffold
description: "一键搭建项目文档系统骨架（核心三文档 + c.md + jobs/legacy 流转 + Agents.md 约定）。当用户要求初始化文档系统、搭建文档结构、或为新项目创建文档骨架时使用。"
author: Henri
created: "2026-04-12"
---

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

# Doc System Scaffold

为项目一键生成「人 + AI 协同」文档系统骨架。该系统源自 VeTBIP 项目的实践沉淀，适用于任何中长期技术项目。

## 体系概览

```
<project>/
├── Agents.md                  ← 人机协同约定（工具链、目录规范、AI 行为边界）
├── README.md                  ← 项目能力与导航（轻量，不放长指令）
├── c.md                       ← 操作清单 cheatsheet（命令、路径、索引）
└── docs/
    ├── specs/                  ← 核心治理三件（BLUEPRINT / ARCHITECTURE / ROADMAP）
    │   ├── BLUEPRINT.md         ← 战略层：宏观规划与理念
    │   ├── ARCHITECTURE.md      ← 架构层：实现框架与技术细节
    │   └── ROADMAP.md           ← 执行层：阶段路线与 todo-list
    ├── jobs/                   ← 在制任务文档（doing → done 后移入 legacy）
    │   └── README.md
    ├── legacy/                 ← 已完成任务归档
    │   └── README.md
    ├── reports/                ← 经验沉淀：复盘、原则、可复用结论与决策证据
    │   └── INDEX.md
    ├── work-notes/             ← 经历记录：按时间推进的研发工作记录与 session 索引
    │   └── INDEX.md
    └── theory/                 ← 理论推导与参考资料（可选）
```

> 核心三件统一收敛在 `docs/specs/` 下，与 `docs/jobs/`、`docs/legacy/`、`docs/reports/`、`docs/work-notes/` 同层并列；`docs/` 根目录不再直接放置散落文档。

## 触发条件

满足以下任一条件时使用本 skill：

1. 用户要求「初始化文档系统」「搭建文档结构」「创建项目文档骨架」。
2. 用户在一个新项目中要求「按 VeTBIP 风格建文档」。
3. 用户要求「一键部署文档系统」。

## 执行步骤

### Step 1: 收集项目信息

向用户确认以下信息（使用 AskUser 工具）：

1. **项目名称**：用于文档标题和 Agents.md。
2. **项目简述**：一句话描述项目目标。
3. **主要工具链**：项目使用的语言、构建工具、运行环境。
4. **是否需要 theory/ 目录**：偏研究/数值的项目通常需要。
5. **是否有子项目**：如有，每个子项目也会生成自己的 `c.md`。
6. **协作文件名检查**：项目协作约定文件统一使用 `Agents.md`。执行前检查是否已存在 `Agents.md`、`AGENTS.md`、`agents.md` 等大小写变体；若存在非标准变体，不再创建新的协作文件，并在汇报中提示用户用 `git mv` 或等价方式统一到 `Agents.md`。

### Step 2: 生成文件

在项目根目录下依次创建以下文件。如果文件已存在，**跳过并提示用户**，不覆盖。协作约定文件统一命名为 `Agents.md`；若检测到 `AGENTS.md`、`agents.md` 等大小写变体，视为已存在并提示规范化，不并行创建第二份。

| # | 目标文件 | 说明 | 模板 |
|---|---------|------|------|
| 2.1 | `docs/specs/BLUEPRINT.md` | 战略层：宏观规划、理念、技术路线与验收标准 | 读 `templates/BLUEPRINT.md.md`，填充占位符 |
| 2.2 | `docs/specs/ARCHITECTURE.md` | 架构层：功能实现框架与关键技术细节 | 读 `templates/ARCHITECTURE.md.md`，填充占位符 |
| 2.3 | `docs/specs/ROADMAP.md` | 执行层：阶段路线与 todo-list | 读 `templates/ROADMAP.md.md`，填充占位符 |
| 2.4 | `docs/jobs/README.md` | 在制任务文档区使用规则与进度模板 | 读 `templates/jobs-README.md.md`，直接写入 |
| 2.5 | `docs/legacy/README.md` | 已完成任务归档说明 | 读 `templates/legacy-README.md.md`，直接写入 |
| 2.6 | `docs/reports/INDEX.md` | 经验沉淀索引（与 work-notes 边界说明） | 读 `templates/reports-INDEX.md.md`，填充占位符 |
| 2.7 | `docs/work-notes/INDEX.md` | 经历记录索引 | 读 `templates/work-notes-INDEX.md.md`，直接写入 |
| 2.8 | `docs/theory/README.md` | 理论推导与参考资料（可选，用户确认时才创建） | 读 `templates/theory-README.md.md`，直接写入 |
| 2.9 | `c.md` | 操作清单：常用命令、结果路径、常看目录 | 读 `templates/c.md.md`，填充占位符 |
| 2.10 | `Agents.md` | 人机协同约定（工具链、文档分工、AI 约束） | 读 `templates/Agents.md.md`，填充占位符 |
| 2.11 | `README.md` | 项目能力与导航（仅当不存在时创建） | 读 `templates/README.md.md`，填充占位符 |

### Step 3: 汇报结果

创建完成后，向用户汇报：

1. 列出所有已创建的文件。
2. 列出因已存在而跳过的文件。
3. 如检测到 `AGENTS.md`、`agents.md` 等协作文件名变体，提示用户统一为 `Agents.md`。
4. 提示下一步：建议用户先填写 BLUEPRINT.md 的项目定位和技术路线部分。

## 设计原则

1. **不覆盖**：已存在的文件永远不覆盖，只跳过并提示。
2. **最小骨架**：生成的是可填充的模板，不是空目录。每个文件有足够的结构引导用户填写。
3. **渐进完善**：`{待补充}` 占位符明确标记了需要用户后续填写的部分。
4. **尊重现有结构**：如果项目已有部分文档，只补缺不重建。
5. **协作文件统一命名**：项目协作约定文件统一使用 `Agents.md`；检测到大小写变体时只提示规范化，不并行创建。

## 子项目支持

如果用户声明有子项目（如 `frontend/`、`backend/`），为每个子项目额外生成：

- `{子项目}/c.md` — 该子项目的操作清单
- `{子项目}/README.md` — 该子项目的说明文档（仅在用户明确需要、或该子项目需要独立 onboarding 时创建）
