#!/usr/bin/env python3
"""Apply reviewed semantic quotation annotations to Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from index_markdown import document_index, normalize, split_blocks


def escape_span_text(text: str) -> str:
    return text.replace("[", r"\[").replace("]", r"\]")


def validate_annotation(entry: object, kind: str) -> dict[str, str]:
    if not isinstance(entry, dict):
        raise SystemExit(f"{kind} entry must be an object")
    paragraph_id = entry.get("paragraph_id")
    reason = entry.get("reason")
    if not isinstance(paragraph_id, str) or not paragraph_id:
        raise SystemExit(f"{kind} entry is missing paragraph_id")
    if not isinstance(reason, str) or not reason.strip():
        raise SystemExit(f"{kind} entry {paragraph_id} is missing a review reason")
    return entry  # type: ignore[return-value]


def apply(source: str, annotations: dict[str, object]) -> str:
    index = document_index(source)
    if annotations.get("version") != 1:
        raise SystemExit("annotations version must be 1")
    if annotations.get("source_sha256") != index["source_sha256"]:
        raise SystemExit("source hash differs from annotations; regenerate and review the index")

    indexed_blocks = index["blocks"]
    assert isinstance(indexed_blocks, list)
    known_ids = {item["paragraph_id"] for item in indexed_blocks}

    block_ids: set[str] = set()
    for raw in annotations.get("block_quotes", []):
        entry = validate_annotation(raw, "block quote")
        block_ids.add(entry["paragraph_id"])

    inline_by_id: dict[str, list[str]] = {}
    for raw in annotations.get("inline_quotes", []):
        entry = validate_annotation(raw, "inline quote")
        text = entry.get("text")
        if not isinstance(text, str) or not text:
            raise SystemExit(f"inline quote {entry['paragraph_id']} is missing exact text")
        inline_by_id.setdefault(entry["paragraph_id"], []).append(text)

    unknown = (block_ids | set(inline_by_id)) - known_ids
    if unknown:
        raise SystemExit("unknown paragraph IDs: " + ", ".join(sorted(unknown)))
    overlap = block_ids & set(inline_by_id)
    if overlap:
        raise SystemExit("paragraphs cannot have both block and inline annotations: " + ", ".join(sorted(overlap)))

    source_blocks = split_blocks(normalize(source))
    output: list[str] = []
    open_block_quote = False

    for block, item in zip(source_blocks, indexed_blocks, strict=True):
        paragraph_id = item["paragraph_id"]
        is_block_quote = paragraph_id in block_ids
        if is_block_quote and not open_block_quote:
            output.append("::: {.semantic-quote}")
            open_block_quote = True
        elif not is_block_quote and open_block_quote:
            output.append(":::")
            open_block_quote = False

        if paragraph_id in inline_by_id:
            for exact_text in inline_by_id[paragraph_id]:
                if block.count(exact_text) != 1:
                    raise SystemExit(
                        f"inline text in {paragraph_id} must occur exactly once; found {block.count(exact_text)}"
                    )
                marked = f"[{escape_span_text(exact_text)}]{{.semantic-inline-quote}}"
                block = block.replace(exact_text, marked, 1)
        output.append(block)

    if open_block_quote:
        output.append(":::")
    return "\n\n".join(output).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("annotations", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.input.read_text(encoding="utf-8")
    annotations = json.loads(args.annotations.read_text(encoding="utf-8"))
    if not isinstance(annotations, dict):
        raise SystemExit("annotations root must be an object")
    result = apply(source, annotations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Applied semantic annotations -> {args.output}")


if __name__ == "__main__":
    main()
