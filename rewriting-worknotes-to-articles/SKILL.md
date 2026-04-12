---
name: rewriting-worknotes-to-articles
description: "Rewrite numbered work-notes from the current repository's work-notes area into reflective, narrative-style articles for its local articles subdirectory and optionally for external blog publication. Use when the user wants to turn a summary note into a shareable essay, or asks to generate an article from a work note."
author: Henri
created: "2026-03-12"
last_updated: "2026-03-12"
---

# Rewriting Work Notes to Articles

Transform an internal numbered work-note into a reflective, readable article suitable for sharing. The source is a structured engineering summary; the output is a narrative essay with natural paragraphs.

## Workflow

1. **Identify the source note.** The user will specify (or you should confirm) which file in the repository's work-notes directory to rewrite. Prefer the existing project convention; if no convention exists, default to `<repo>/docs/work-notes/`.
2. **Read reference articles.** Before drafting, read 1–2 existing articles from the local articles directory under the same work-notes root, usually `<repo>/docs/work-notes/articles/`, to calibrate tone, paragraph rhythm, and section style. These articles use:
   - A calm, factual tone — technical blog style, not conversational or dramatic
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
- **写技术科普文，不是营销号也不是灌水文。** 语气平实、就事论事，像写给同行看的技术博客。具体来说：
  - 不要用夸张的感叹句或悬念式标题（如"比想象中难多了！"、"真正复杂的部分才刚开始"）。标题直述主题即可。
  - 不要用"说白了"、"回头看"、"挺有意思的是"、"更让人头疼的是"这类口语化填充和情绪渲染。
  - 不要用"收口"、"单点故障"、"静默失效"、"归一化"、"收敛"、"反直觉"这类项目管理术语，也不要用"综上所述"、"值得注意的是"这类公文腔。
  - 每段就事论事，陈述事实、原因、做法、结果。让内容本身传递价值，不靠语气制造戏剧感。
- **优先使用日常语言，而不是堆砌专业术语。** 这是偏科普的技术文章，读者不一定是该领域的专家。具体来说：
  - 如果一个概念可以用日常语言说清楚，就不要用术语。例如："页面声明的标准地址"比"canonical URL"对大部分读者更友好；"先后匹配的方式"比"双路匹配策略"更容易理解。
  - 项目代码中的标记名（如 `data-iv-*`、`.nojekyll`）可以保留，因为它们是具体操作的一部分，读者需要知道确切写法。
  - 但描述机制和原理时，避免不加解释地使用 XPath、DOM 结构、语义契约、静默失效、耦合、选择器 等术语。如果必须提及，用一句日常语言先说明白意思，再附上术语作为补充。
  - 判断标准：如果把这段话念给一个不做前端的程序员听，他能不能不查资料就听懂？如果不能，就需要换个说法。
- Allow generic technical terms freely: `AGENTS.md`, skill, code review, `.skills/`, baseline, fixture, prompt, diff, commit, etc.
- **Hide project-specific details.** Do not name the project, specific modules, specific skill names, proprietary model class names, or internal directory paths that would identify the project. Describe them generically instead (e.g., "核心装配模块" instead of the actual module name).
- Use a few key domain terms where they genuinely help the reader understand the point, but don't pile on jargon. The goal is that a developer working on any project could read the article and find it useful.

### Structure
- Title: direct and descriptive, stating the topic plainly. Avoid clickbait, rhetorical questions, or emotional hooks.
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
