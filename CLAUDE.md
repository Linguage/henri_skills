# CLAUDE.md

This is a Claude Code skills repository. Each subdirectory contains a skill with a `SKILL.md` file.

## Conventions

- Each skill lives in its own directory: `<skill-name>/SKILL.md`
- SKILL.md must have frontmatter with `name` and `description` fields
- Skills may include `agents/`, `references/`, `templates/`, `prompts/`, or other supporting directories
- Skill names use kebab-case
- Write skills in English; user-facing descriptions can be bilingual
- Each SKILL.md 在 frontmatter 后、正文前包含「单一来源」声明

## Skills project management (this repo)

- **Single source of truth**: edit skills only in this repository, never in symlinked directories (`~/.claude/skills/`, `~/.config/opencode/skills/`, `~/.agents/skills/`).
- **Frontmatter — originals**: set `author: Henri`, plus `created` (first commit date for that `SKILL.md`) and `last_updated` when applicable (see README for the `2026-04-12` exclusion rule).
- **Frontmatter — third-party**: keep `source`, `author` (upstream maintainer), and `modifications` (note that the skill may have been changed from upstream); same `created` / `last_updated` rules as above.
- **Description**: keep under 12 words. State WHAT the skill does, not capabilities or supported formats.
- **Externalize bulk content**: templates, prompts, and reference data go in subdirectories (`templates/`, `prompts/`, `references/`); SKILL.md only contains workflow and rules.
- **README**: when adding or reclassifying a skill, update `README.md` — list originals vs third-party in the two tables and keep them accurate.
- **Attribution**: do not duplicate long attribution in skill bodies; upstream and modification intent live in frontmatter (and README tables for discovery).

## Symlink Chain

This repo is the source of truth. It is consumed via directory-level symlinks:

```
~/.claude/skills/          → this repo
~/.config/opencode/skills/ → this repo
~/.agents/skills/          → this repo
```

Do NOT edit skills in any symlinked directory — always edit here.
