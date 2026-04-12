# CLAUDE.md

This is a Claude Code skills repository. Each subdirectory contains a skill with a `SKILL.md` file.

## Conventions

- Each skill lives in its own directory: `<skill-name>/SKILL.md`
- SKILL.md must have frontmatter with `name` and `description` fields
- Skills may include `agents/`, `references/`, or other supporting directories
- Skill names use kebab-case
- Write skills in English; user-facing descriptions can be bilingual

## Skills project management (this repo)

- **Single source of truth**: edit skills only in this repository, never in `~/.cc-switch/skills` or `~/.claude/skills` (those are symlinks).
- **Frontmatter — originals**: set `author: Henri`, plus `created` (first commit date for that `SKILL.md`) and `last_updated` when applicable (see README for the `2026-04-12` exclusion rule).
- **Frontmatter — third-party**: keep `source`, `author` (upstream maintainer), and `modifications` (note that the skill may have been changed from upstream); same `created` / `last_updated` rules as above.
- **README**: when adding or reclassifying a skill, update `README.md` — list originals vs third-party in the two tables and keep them accurate.
- **Attribution**: do not duplicate long attribution in skill bodies; upstream and modification intent live in frontmatter (and README tables for discovery).

## Symlink Chain

This repo is the source of truth. It is consumed via:

```
~/.cc-switch/skills → this repo
~/.claude/skills/<name> → ~/.cc-switch/skills/<name>
```

Do NOT edit skills in `~/.cc-switch/` or `~/.claude/` directly — always edit here.
