---
name: doc-system-scaffold
description: "搭建项目管理文档，并为 DeepSeek Harness 项目工作台生成管理目录索引和 Agent 进度事件。适用于初始化文档系统、登记多仓库工作台或接续已有工作台任务。"
metadata:
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

## DSH 项目工作台接入

用户要创建可由 DSH「项目工作台」打开的管理目录时，先复用或补齐上面的 Markdown 结构，再从实际子项目清单生成索引。目标是管理目录本身，通常是项目下的 `docs/`。

```sh
python3 <skill目录>/scripts/workbench.py init <管理目录> --title '项目名称' \
  --project application '应用' apps/application
```

每个子项目可用一项 `--project 标识 显示名 相对项目根目录` 登记。标识用于关联进度，重定位目录时继续使用原标识。已存在的索引会保留，内容有差异时先核对现有登记。把最终管理目录、记录命令和本项目的交付证据要求写入项目协作约定，供后续 Agent 自动使用。

### 工作中自动更新

Agent 接手任务时沿用在制任务的标识。在开始、重要进展、阻塞、待审查、验证或完成时主动发布对应记录。能观察到中断时登记中断及接续点。共同任务由负责汇总的 Agent 发布，多 Agent 子任务各用独立标识。用户可在插件追溯记录和文档。

```sh
python3 <skill目录>/scripts/workbench.py record <管理目录> \
  --task validate-import --title '验证资料导入' --agent '验证 Agent' \
  --project application --status verified --summary '隔离环境导入通过' \
  --evidence '导入命令退出码 0' --document jobs/validate-import.md
```

状态值为 `running`、`blocked`、`review`、`verified`、`completed`、`interrupted`。可以补充 `--next`、重复提供 `--evidence`，或用 `--event-id` 让可重试的同一事件重复提交时保持幂等。验证和完成记录附上实际证据。进度保存在管理目录下的 `.workbench/events/`，正文继续维护在所属 Markdown 文档。
