# Agents.md

This is the personal AI agent skills repository (`henri_skills`). Each subdirectory contains a skill with a `SKILL.md` file. The repo is the single source of truth for Claude Code, OpenCode, `.agents`, and Codex user skills.

## Conventions

- Each skill lives in its own directory: `<skill-name>/SKILL.md`
- SKILL.md must have frontmatter with `name` and `description` fields
- Skills may include `agents/`, `references/`, `templates/`, `prompts/`, or other supporting directories
- Skill names use kebab-case
- Write skills in English; user-facing descriptions can be bilingual
- Each SKILL.md 在 frontmatter 后、正文前包含「单一来源」声明

## Skills project management (this repo)

- **Single source of truth**: edit skills only in this repository, never in symlinked directories (`~/.claude/skills/`, `~/.config/opencode/skills/`, `~/.agents/skills/`, `~/.codex/skills/<skill>/`).
- **Frontmatter — originals**: set `author: Henri`, plus `created` (first commit date for that `SKILL.md`) and `last_updated` when applicable (see README for the `2026-04-12` exclusion rule).
- **Frontmatter — third-party**: keep `source`, `author` (upstream maintainer), and `modifications` (note that the skill may have been changed from upstream); same `created` / `last_updated` rules as above.
- **Description**: keep under 12 words when practical. State WHAT the skill does, not capabilities or supported formats. Longer trigger text is acceptable only when matching quality requires it.
- **Externalize bulk content**: templates, prompts, and reference data go in subdirectories (`templates/`, `prompts/`, `references/`); SKILL.md only contains workflow and rules.
- **README**: when adding or reclassifying a skill, update `README.md` — list originals vs third-party in the two tables and keep them accurate.
- **Codex linking**: after adding a skill that Codex must load, create `~/.codex/skills/<skill-name> → this repo/<skill-name>/` and note it in README if the linked set changes.
- **Attribution**: do not duplicate long attribution in skill bodies; upstream and modification intent live in frontmatter (and README tables for discovery).

Recommended「单一来源」wording:

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/`、`~/.codex/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

## Symlink Chain

This repo is the source of truth. It is consumed via directory-level symlinks:

```
~/.claude/skills/          → this repo          # 全局
~/.config/opencode/skills/ → this repo          # 全局
~/.agents/skills/          → this repo          # 全局
```

Codex keeps `~/.codex/skills/.system` for platform skills, so user skills are linked per skill:

```
~/.codex/skills/<skill-name> → this repo/<skill-name>/   # Codex
```

Project-level symlinks are also supported (e.g., for workspace-specific skills):

```
<project>/.claude/skills/<skill-name> → this repo/<skill-name>/   # 项目级
~/Downloads/.claude/skills/organize-downloads → this repo/organize-downloads/
```

Do NOT edit skills in any symlinked directory — always edit here.

## 配置方式

在一台新设备上使用这些 skills，需要创建符号链接让各工具链能发现它们。以下是配置步骤：

### 1. 检测已有目录

```bash
# 全局目录级消费路径
ls -la ~/.claude/skills 2>/dev/null
ls -la ~/.agents/skills 2>/dev/null
ls -la ~/.config/opencode/skills 2>/dev/null

# Codex（保留真实目录 + .system；用户 skill 为子项软链接）
ls -la ~/.codex/skills 2>/dev/null
```

### 2. 创建全局符号链接

对本仓库已存在的消费端目录，直接创建指向本仓库的符号链接：

```bash
REPO="$HOME/settings/henri_skills"

# Claude Code
mkdir -p ~/.claude
ln -s "$REPO" ~/.claude/skills

# OpenCode
mkdir -p ~/.config/opencode
ln -s "$REPO" ~/.config/opencode/skills

# .agents
mkdir -p ~/.agents
ln -s "$REPO" ~/.agents/skills
```

如果某个目录已经存在（非符号链接），则只创建 `skills` 子链接，不破坏已有内容。

### 3. 项目级符号链接（按需）

对于需要在特定项目中使用的 skill，创建项目级链接：

```bash
# 示例：在某个项目中启用 health skill
mkdir -p <project>/.claude/skills
ln -s "$REPO/health" <project>/.claude/skills/health
```

### 4. Codex 按 skill 软链接

Codex 的 `~/.codex/skills/` 不能整目录替换（需保留 `.system`）。对需要在 Codex 中使用、且已纳入本仓库的 skill，按名称创建软链接：

```bash
mkdir -p ~/.codex/skills

# 当前已纳入并建议链接的示例
ln -s "$REPO/henri-writing-style" ~/.codex/skills/henri-writing-style

# 其他 skill 按同样模式追加，例如：
# ln -s "$REPO/academic-latex-pdf" ~/.codex/skills/academic-latex-pdf
```

不要把 Codex 专属的 `.system` 技能迁入本仓库。用户自建 skill 若仍只存在于 `~/.codex/skills/`，应迁入本仓库后再改软链接。

### 5. organize-downloads 的特殊配置

`organize-downloads` skill 需要在 `~/Downloads` 目录下工作。为了让 agent 在 Downloads 目录中自动发现该 skill，在 Downloads 下创建 `.claude/skills/` 并链接：

```bash
mkdir -p ~/Downloads/.claude/skills
ln -s "$REPO/organize-downloads" ~/Downloads/.claude/skills/organize-downloads
```

这样当 agent 以 `~/Downloads` 为工作目录时，就能自动加载 `organize-downloads` skill。

### 验证

配置完成后，验证符号链接是否正确：

```bash
# 应指向同一仓库
readlink ~/.claude/skills
readlink ~/.agents/skills
readlink ~/.config/opencode/skills

# Codex 按 skill 链接
readlink ~/.codex/skills/henri-writing-style

# Downloads 项目级链接
readlink ~/Downloads/.claude/skills/organize-downloads
```

所有链接应指向 `henri_skills` 仓库的对应路径。
