---
name: session-summary-writer
description: Write staged work-summary documents for a series of coding or restructuring sessions. Use when the user wants a phase summary, session recap, work note, or milestone document saved into the current repository's work-notes area. Default to numbered summary notes; only switch to an articles subdirectory when the user explicitly wants a reflective essay-style article.
---

# Session Summary Writer

Write a durable work note that explains what a series of sessions accomplished, why the work was done, and what remains open. Default to the current repository's established work-notes style, not a chat transcript.

## Workflow

1. Gather the real scope of work from the current session series:
   - changed files
   - created or moved directories
   - tests or validation that were run
   - docs that were added or updated
   - unresolved items that were explicitly left for later
2. Resolve the repository-local output root:
   - if the repository already has a work-notes convention, follow it
   - otherwise default to `<repo>/docs/work-notes/`
   - treat `<repo>/docs/work-notes/articles/` as the reflective-article subdirectory when that mode is requested
3. Decide the output type:
   - default: numbered summary note in the resolved work-notes directory
   - only if explicitly requested: reflective article in the `articles/` subdirectory under that root
4. Inspect existing work-note files to match the current naming and structure.
5. Write a summary that explains:
   - background and motivation
   - main goals of this phase
   - concrete structural or code changes
   - validation performed
   - documentation updates
   - current state and remaining open items
6. Separate confirmed outcomes from unverified assumptions.
7. Save the note in the appropriate location with a consistent filename.

## Summary Note Rules

- Prefer a numbered filename such as `NN_TOPIC_SUMMARY_YYYY-MM-DD.md`.
- Infer the next numeric prefix from existing summary files when creating a new note.
- Write the document in Chinese by default, including the title, section headings, and body prose, unless the user explicitly requests another language.
- Write for future humans, not for the current chat. The document should still make sense weeks later without conversation context.
- Summarize decisions and their rationale, not just a changelog of edited files.
- Record unfinished work explicitly instead of implying completion.
- Mention validation honestly:
  - what was run
  - what passed
  - what could not be verified

## Reflective Article Rules

- Use the repository-local `articles/` subdirectory under the work-notes root only when the user explicitly wants a broader retrospective or essay.
- Prefer thematic sections and a stronger narrative voice.
- Focus on lessons and patterns, not a file-by-file record.

## Writing Constraints

- Do not invent tests, commands, or completed work.
- Do not copy terminal output verbatim unless a short excerpt is essential.
- Do not turn the document into a raw transcript of the session.
- Keep the structure readable with clear numbered sections and short explanatory paragraphs.

## Reference

- Read `references/work-notes-style.md` before drafting to match naming, section flow, and tone.
