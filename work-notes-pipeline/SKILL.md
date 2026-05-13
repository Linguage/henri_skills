---
name: work-notes-pipeline
version: "2.0.0"
description: "Write session summaries and rewrite work-notes into articles."
author: Henri
created: "2026-03-10"
last_updated: "2026-05-13"
---

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

# Work Notes Pipeline

Two modes: **summary** (numbered session summaries) and **article** (reflective narrative articles from work-notes).

## Directory Resolution

- Follow the repository's existing work-notes convention if one exists.
- Otherwise default to `<repo>/docs/work-notes/` for summaries.
- Reflective articles go in `<repo>/docs/work-notes/articles/`.

## Mode: Summary

### Workflow

1. Gather scope: changed files, directories created/moved, tests run, docs updated, unresolved items.
2. Inspect existing work-note files to match naming and structure.
3. Infer the next numeric prefix from existing summary files.
4. Write a numbered summary explaining: background, goals, concrete changes, validation, documentation updates, current state, and remaining open items.
5. Separate confirmed outcomes from unverified assumptions.
6. Save as `NN_TOPIC_SUMMARY_YYYY-MM-DD.md`.

### Summary Rules

- Write in Chinese by default (title, headings, body) unless the user requests another language.
- Write for future humans, not the current chat.
- Summarize decisions and rationale, not just a file changelog.
- Record unfinished work explicitly.
- Report validation honestly: what was run, what passed, what could not be verified.

## Mode: Article

### Workflow

1. Identify the source work-note to rewrite.
2. Read 1–2 existing articles from the local articles directory to calibrate tone.
3. Draft a reflective article (see article writing rules below).
4. Save locally with a descriptive kebab-case filename (no numeric prefix, no date suffix).
5. Optionally publish to a blog directory with Hugo frontmatter (see below).

### Article Writing Rules

- Use natural paragraphs; avoid bullet lists as primary structure.
- Write in Chinese by default. First-person is fine but keep focus on work and lessons.
- **Technical blog tone — not marketing, not drama:**
  - No exaggerated exclamations or clickbait titles.
  - No filler phrases: "回头看", "挺有意思的是", "更让人头疼的是", "说白了".
  - No management jargon ("收口", "单点故障", "静默失效") or bureaucratic tone ("综上所述").
  - State facts, reasons, actions, results. Let content carry value.
- **Prefer everyday language over jargon.** If a concept can be said plainly, don't use the term. Code identifiers (e.g. `data-iv-*`) are fine to keep. Generic technical terms (skill, commit, diff) are fine.
- **Hide project-specific details.** Don't name the project, modules, or internal paths. Describe generically.
- Reorganize by insight, not chronological order.
- Merge related bullets into flowing paragraphs.
- Drop file inventories and checklists — keep only what supports the narrative.
- Preserve honest acknowledgment of unfinished work.
- Do not invent outcomes.

### Article Structure

- Title: direct and descriptive. No clickbait.
- 4–8 thematic sections with short headings.
- Opening: 2–3 paragraphs setting context.
- Closing: reflect on what changed, end with a forward-looking observation.

### Blog Frontmatter

When publishing externally, prepend Hugo-compatible YAML:

```yaml
---
title: "文章标题"
subtitle: "一句话副标题"
date: "YYYY-MM-DDTHH:MM:SS"
description: "2-3 句 SEO 友好的描述"
tags: ["标签1", "标签2"]
section: build
author: amp-smart
---
```

- `section`: `build` for engineering/tooling articles.
- `author`: `amp-smart` unless user specifies otherwise.
- `date`: date the source work-note was written.
- `tags`: 3–6 relevant Chinese tags.
- Ask for the blog directory unless the repo contains an obvious content path.

## Shared Frontmatter

Both modes add YAML frontmatter:

- `title`: from content or filename
- `date`: current date (YYYY-MM-DD)
- `created`: creation timestamp
- `category`: "worknotes" (summary) or "articles" (article)
- `tags`: inferred from content
- `updated`: only for modified documents

## Writing Constraints

- Do not invent tests, commands, or completed work.
- Do not copy terminal output verbatim unless a short excerpt is essential.
- Keep structure readable with clear sections and short paragraphs.

## Reference

- Read `references/work-notes-style.md` before drafting to match naming, section flow, and tone.
- Read existing local articles before drafting article mode to match tone and structure.
- Read the source work-note thoroughly — do not summarize from memory.
