---
name: academic-latex-pdf
description: Convert scholarly Chinese, English, or bilingual Markdown into polished LaTeX and PDF with semantic quotation styling, configured Chinese fonts, mathematical typesetting, table of contents, A4 academic layout, XeLaTeX compilation, and rendered-page verification. Use for academic articles, OCR-cleaned book chapters, lecture notes, mathematical manuscripts, or other reading-oriented documents when Codex must produce or revise a reproducible .tex/.pdf package; also use when quotations must be distinguished semantically from titles, terms, and emphasis. Do not use this skill as the OCR stage for raw scanned PDFs.
author: Henri
created: "2026-07-21"
last_updated: "2026-07-21"
---

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/`、`~/.codex/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

# Academic LaTeX PDF

Produce a reproducible LaTeX project and visually verified PDF. Keep semantic judgment separate from deterministic conversion.

## Workflow

1. Preserve the source. Work in a new output or temporary directory; never overwrite the input Markdown.
2. Check the environment before processing:

   ```sh
   sh scripts/install_dependencies.sh --check
   ```

   If dependencies are missing, obtain approval and run `sh scripts/install_dependencies.sh`. Use `--dry-run` to preview changes. The installer targets macOS with Homebrew.
3. Normalize non-Markdown inputs first. For DOCX, HTML, or text-based PDF, convert to Markdown and inspect it. For a scanned PDF, complete OCR before using this skill.
4. Generate a paragraph index:

   ```sh
   python3 scripts/index_markdown.py INPUT.md blocks.json
   ```

5. Read the complete article and classify citations by meaning. Read [references/semantic-annotation.md](references/semantic-annotation.md), then create `annotations.json`. Do not infer quotations merely from quotation marks, length, or verbs such as “写道”.
6. Apply the reviewed annotations:

   ```sh
   python3 scripts/apply_annotations.py INPUT.md annotations.json annotated.md
   ```

7. Build with the configured system fonts and template:

   ```sh
   sh scripts/build_pdf.sh annotated.md OUTPUT_DIR
   ```

   Pass an optional third argument to override the title. The default title is the first level-one Markdown heading.
8. Verify the resulting PDF and render representative pages:

   ```sh
   python3 scripts/verify_pdf.py OUTPUT.pdf --render-dir rendered
   ```

9. Inspect the first, middle, last, quotation-dense, formula-dense, and section-transition pages. Rebuild after any meaningful correction. Do not deliver until there are no clipped lines, overlaps, missing glyphs, black boxes, broken lists, or incorrect quotation boundaries.
10. Deliver the source path, `annotations.json`, annotated Markdown, `.tex`, `.pdf`, and the exact rebuild command.

## Semantic requirements

- Apply Kai to a complete paragraph or multi-paragraph passage only when the passage reproduces another speaker or source.
- Apply Kai only inside the quotation span when cited words are embedded in the authors' prose.
- Keep book titles, article titles, named concepts, scare quotes, questions, and ordinary emphasis in the body font unless context establishes an actual citation.
- Keep translator notes, editor notes, and OCR warnings outside a surrounding source quotation unless they are themselves quoted material.
- Record every judgment in the document-specific annotation file. Never hard-code one article's paragraph IDs into this skill.
- If a boundary is genuinely ambiguous, preserve the main font and report the ambiguity rather than silently extending Kai across authorial prose.

## Typesetting defaults

Use the A4, 小四, two-character indent profile unless the user specifies otherwise. Read [references/typography.md](references/typography.md) before changing paper size, fonts, margins, hierarchy, or quote treatment.

Do not store or copy font binaries in this skill. Install the required font families through `scripts/install_dependencies.sh`; the generated PDF must still embed every font it uses.

## Failure handling

- Stop on unknown annotation IDs, source-hash drift, non-unique inline quote text, compilation failure, missing fonts, or a non-A4 result when A4 is requested.
- Treat `overfull` boxes as layout defects requiring inspection. Treat small `underfull` warnings as review items, not automatic failures.
- Never declare success from the compiler exit code alone; render and inspect the PDF.
