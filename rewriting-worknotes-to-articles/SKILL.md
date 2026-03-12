---
name: rewriting-worknotes-to-articles
description: "Rewrite numbered work-notes from the current repository's work-notes area into reflective, narrative-style articles for its local articles subdirectory and optionally for external blog publication. Use when the user wants to turn a summary note into a shareable essay, or asks to generate an article from a work note."
---

# Rewriting Work Notes to Articles

Transform an internal numbered work-note into a reflective, readable article suitable for sharing. The source is a structured engineering summary; the output is a narrative essay with natural paragraphs.

## Workflow

1. **Identify the source note.** The user will specify (or you should confirm) which file in the repository's work-notes directory to rewrite. Prefer the existing project convention; if no convention exists, default to `<repo>/docs/work-notes/`.
2. **Read reference articles.** Before drafting, read 1–2 existing articles from the local articles directory under the same work-notes root, usually `<repo>/docs/work-notes/articles/`, to calibrate tone, paragraph rhythm, and section style. These articles use:
   - A conversational but thoughtful first-person voice
   - Thematic sections with short descriptive headings
   - Natural paragraphs instead of bullet-heavy structure
   - Concrete details grounded in real experience
3. **Draft the article** following the writing rules below.
4. **Save locally** to the repository-local articles directory under the work-notes root, usually `<repo>/docs/work-notes/articles/`, with a descriptive kebab-case filename (no numeric prefix, no date suffix).
5. **Optionally publish to blog.** If the user requests, also save a copy to the blog articles directory with Hugo-compatible YAML frontmatter (see Blog Frontmatter below).

## Writing Rules

### Voice and style
- Use natural paragraphs. Avoid bullet lists as the primary structure.
- Write in Chinese by default. Use first-person where it feels natural, but keep the focus on the work and the lessons, not on "I".
- Allow generic technical terms freely: `AGENTS.md`, skill, code review, `.skills/`, baseline, fixture, prompt, diff, commit, etc.
- **Hide project-specific details.** Do not name the project, specific modules, specific skill names, proprietary model class names, or internal directory paths that would identify the project. Describe them generically instead (e.g., "核心装配模块" instead of the actual module name).
- Use a few key domain terms where they genuinely help the reader understand the point, but don't pile on jargon. The goal is that a developer working on any project could read the article and find it useful.

### Structure
- Title: a single sentence that captures the theme, not a summary label.
- Sections: 4–8 thematic sections with short headings. Each section should read as a self-contained thought.
- Opening: set context in 2–3 paragraphs — what was the situation before this round of work.
- Closing: reflect on what changed and what remains. End with a forward-looking observation, not a grand conclusion.

### Content transformation
- Reorganize by insight, not by chronological order of edits.
- Merge related bullet points from the source into flowing paragraphs.
- Drop internal file inventories and detailed checklists — keep only what supports a narrative point.
- Preserve honest acknowledgment of unfinished work and limitations.
- Do not invent outcomes or embellish what was actually done.

## Blog Frontmatter

When publishing to the blog directory, prepend Hugo-compatible YAML frontmatter:

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

- `section` should be `build` for engineering/tooling articles.
- `author` should be `amp-smart` unless the user specifies otherwise.
- `date` should be the date the source work-note was written.
- `tags` should be 3–6 relevant Chinese tags.

## Blog Output Path

There is no fixed global blog output path for this skill.

- If the user requests external publication, ask for the target blog articles directory unless the current repository already contains an obvious blog content path.
- Common patterns include `content/articles/`, `contents/articles/`, or another project-specific publishing directory.
- Use a descriptive kebab-case English filename for the blog copy.

## Reference

- Read existing local articles under the repository's work-notes root before drafting to match tone and structure.
- Read the source work-note thoroughly — do not summarize from memory or partial reading.
