# Work Notes Style Guide

Use this guide when writing staged summary documents in the current repository's work-notes directory.

## Default Output Type

Prefer a numbered summary note:

- Preferred path when no project-specific convention exists: `<repo>/docs/work-notes/`
- Filename pattern: `NN_TOPIC_SUMMARY_YYYY-MM-DD.md`

Generic examples:

- `01_INFRA_SETUP_SUMMARY_2026-03-08.md`
- `02_PIPELINE_REORG_SUMMARY_2026-03-09.md`
- `05_VALIDATION_REFINEMENT_SUMMARY_2026-03-09.md`

Use the `articles/` subdirectory under the resolved work-notes root only when the user explicitly asks for a reflective or essay-style writeup.

## Typical Summary Structure

Most summary notes in this repository follow this pattern:

1. Title
2. Date line
3. Opening paragraph stating what this round of work covered
4. `## 1. ...` background, problem statement, or goals
5. `## 2. ...` onward for the main work areas
6. A late section for validation, documentation updates, or environment setup when relevant
7. A closing section summarizing current state and remaining unfinished items

Not every note needs the exact same headings, but the structure should feel like a staged engineering summary rather than a casual diary entry.

## Tone

- Write the title, section headings, and body in Chinese by default.
- Keep the title concise and descriptive.
- Explain why the work mattered, not only what changed.
- Prefer calm, explicit wording over hype or vague praise.
- Treat unresolved items as normal engineering state, not as failure.

## Content Priorities

- State the actual motivation for the work.
- Group related changes by engineering theme, not by edit order.
- Explain how the structure, workflow, or project semantics became clearer.
- Mention tests, smoke runs, or validation truthfully.
- Call out what is still open when the work intentionally stopped short of a larger refactor.

## Avoid

- Avoid chatty first-person transcript style.
- Avoid pretending that every session reached a final architecture.
- Avoid raw file inventories unless they support a larger point.
- Avoid mixing reflective article voice into a numbered engineering summary unless the user asked for it.
