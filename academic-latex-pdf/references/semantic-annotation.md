# Semantic annotation

## Purpose

Separate model judgment from deterministic formatting. Generate an index, read the whole document, and store document-specific decisions in JSON.

## Annotation schema

Copy `source_sha256` from the index file without modification.

```json
{
  "version": 1,
  "source_sha256": "SHA256_FROM_BLOCKS_JSON",
  "block_quotes": [
    {
      "paragraph_id": "p-0012-a1b2c3d4e5",
      "reason": "Direct quotation from the cited preface"
    }
  ],
  "inline_quotes": [
    {
      "paragraph_id": "p-0047-f6e7d8c9b0",
      "text": "“Exact quoted words, including visible quotation marks”",
      "reason": "Words attributed directly to the named speaker"
    }
  ]
}
```

`reason` is required for reviewability but does not affect rendering.

## Decision procedure

For every candidate, identify the current narrator and ask whether the wording belongs to that narrator or to a cited source.

Mark as a block quotation when:

- an attribution introduces one or more paragraphs reproduced from a source;
- a letter, interview answer, inscription, report, or extended extract is reproduced;
- the source voice continues across paragraph breaks until authorial narration clearly resumes.

Mark as an inline quotation when:

- exact words from another speaker occur inside an authorial paragraph;
- the quoted text is attributed explicitly or unmistakably by context.

Do not mark merely because text is enclosed by quotation marks. Common exclusions include:

- book and article titles;
- mathematical terms or labels;
- hypothetical questions;
- scare quotes and ironic emphasis;
- the authors' own restatement;
- quoted material already inside a block quotation, because the whole block already uses Kai.

## Boundary checks

- Read at least the introducing paragraph, the candidate passage, and the following paragraph.
- Use changes in pronouns, tense, source attribution, and argumentative role to locate the end.
- Exclude intervening editor or OCR notes from the quoted font unless the source includes them.
- For malformed OCR quotation marks, select the exact surviving text. Correct a visibly damaged closing mark only in the annotated derivative, never silently in the source.
- Do not choose a substring that appears more than once in the same paragraph. Expand it until it is unique.

## Source drift

Paragraph IDs combine ordinal position and a content hash. If applying annotations reports source drift, regenerate the index and review the affected decisions. Do not bypass the hash check for a materially edited document.
