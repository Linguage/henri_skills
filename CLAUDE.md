# CLAUDE.md

This is a Claude Code skills repository. Each subdirectory contains a skill with a `SKILL.md` file.

## Conventions

- Each skill lives in its own directory: `<skill-name>/SKILL.md`
- SKILL.md must have frontmatter with `name` and `description` fields
- Skills may include `agents/`, `references/`, or other supporting directories
- Skill names use kebab-case
- Write skills in English; user-facing descriptions can be bilingual

## Symlink Chain

This repo is the source of truth. It is consumed via:

```
~/.cc-switch/skills → this repo
~/.claude/skills/<name> → ~/.cc-switch/skills/<name>
```

Do NOT edit skills in `~/.cc-switch/` or `~/.claude/` directly — always edit here.
