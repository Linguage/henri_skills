# Typography profile

## Default reading profile

- Paper: A4 portrait
- Body: 小四 via `\zihao{-4}`
- Margins: 2.6 cm
- Main Chinese font: Noto Serif CJK SC
- Sans Chinese font: Noto Sans CJK SC
- Quotation font: LXGW WenKai
- Paragraph indent: 2 em
- Paragraph spacing: 0.35 em with slight stretch and shrink
- Contents depth: sections and subsections
- Engine: XeLaTeX through latexmk

The body size is imposed at document start because Pandoc's `12pt` class option alone is not the Chinese 小四 specification.

## Adaptation rules

- Prefer changing template parameters over editing generated TeX repeatedly.
- Keep formulas in the math font; switching CJK families around a quotation must not alter math typesetting.
- Preserve list numbering, headings, block quotes, references, and code blocks when adding semantic Divs.
- For denser output, reduce paragraph spacing before reducing body size.
- For two-sided book layouts, change geometry and headers explicitly; do not reuse the single-sided article profile without review.
- When using different fonts, install them as environment dependencies, update `header.tex`, rebuild, and confirm embedding with `pdffonts`. Do not add font binaries to the skill.

## Visual acceptance

Reject pages with clipped text, glyph substitution boxes, inconsistent quotation fonts, isolated headings at page bottoms, severe rivers of whitespace, broken mathematics, or list-number resets caused by annotation wrappers.
