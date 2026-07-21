#!/usr/bin/env python3
"""Verify PDF size/font embedding and render representative pages."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess


def run(command: list[str]) -> str:
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout


def require(command: str) -> None:
    if shutil.which(command) is None:
        raise SystemExit(f"missing required command: {command}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--require-quote-font", action="store_true")
    args = parser.parse_args()

    for command in ("pdfinfo", "pdffonts"):
        require(command)
    info = run(["pdfinfo", str(args.pdf)])
    pages_match = re.search(r"^Pages:\s+(\d+)", info, flags=re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", info, flags=re.MULTILINE)
    if not pages_match or not size_match:
        raise SystemExit("could not read page count or page size")
    pages = int(pages_match.group(1))
    page_size = size_match.group(1)
    if "A4" not in page_size:
        raise SystemExit(f"expected A4, got: {page_size}")

    fonts = run(["pdffonts", str(args.pdf)])
    if "NotoSerifCJKsc-Regular" not in fonts:
        raise SystemExit("bundled Noto Serif CJK SC was not embedded")
    if args.require_quote_font and "LXGWWenKai-Regular" not in fonts:
        raise SystemExit("quotation font was requested but not embedded")
    font_lines = [line for line in fonts.splitlines()[2:] if line.strip()]
    for line in font_lines:
        columns = line.split()
        if len(columns) >= 6 and columns[5].lower() != "yes":
            raise SystemExit(f"font is not embedded: {line}")

    print(f"OK: {pages} pages; {page_size}")
    print("OK: bundled body font embedded; all reported fonts embedded")

    if args.render_dir:
        require("pdftoppm")
        args.render_dir.mkdir(parents=True, exist_ok=True)
        selected = sorted({1, max(1, (pages + 1) // 2), pages})
        for page in selected:
            prefix = args.render_dir / f"page-{page}"
            subprocess.run(
                ["pdftoppm", "-f", str(page), "-singlefile", "-png", "-r", "144", str(args.pdf), str(prefix)],
                check=True,
            )
        print("Rendered representative pages: " + ", ".join(str(page) for page in selected))


if __name__ == "__main__":
    main()
