#!/usr/bin/env python3
"""Index blank-line-delimited Markdown blocks for semantic review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text.strip() + "\n"


def split_blocks(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def block_kind(block: str) -> str:
    first = block.splitlines()[0].lstrip()
    if first.startswith("#"):
        return "heading"
    if first.startswith("$$") or first.startswith("\\["):
        return "display-math"
    if first.startswith(">"):
        return "markdown-blockquote"
    if re.match(r"(?:[-+*]|\d+[.)])\s+", first):
        return "list"
    if first.startswith("```") or first.startswith("~~~"):
        return "code"
    return "paragraph"


def make_id(ordinal: int, block: str) -> str:
    digest = hashlib.sha256(block.encode("utf-8")).hexdigest()[:10]
    return f"p-{ordinal:04d}-{digest}"


def document_index(text: str) -> dict[str, object]:
    normalized = normalize(text)
    blocks = split_blocks(normalized)
    return {
        "version": 1,
        "source_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "normalization": "LF; strip HTML comments; trim outer whitespace",
        "blocks": [
            {
                "paragraph_id": make_id(index, block),
                "ordinal": index,
                "kind": block_kind(block),
                "markdown": block,
            }
            for index, block in enumerate(blocks)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = document_index(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {len(data['blocks'])} blocks -> {args.output}")


if __name__ == "__main__":
    main()
