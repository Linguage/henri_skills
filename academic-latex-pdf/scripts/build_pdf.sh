#!/bin/sh
set -eu

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: build_pdf.sh ANNOTATED.md OUTPUT_DIR [TITLE]" >&2
  exit 2
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SOURCE=$1
OUTPUT_DIR=$2
TITLE=${3:-}

for command_name in python3 pandoc xelatex latexmk; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "missing required command: $command_name" >&2
    exit 1
  }
done

if [ -z "$TITLE" ]; then
  TITLE=$(awk 'BEGIN { found=0 } !found && /^# / { sub(/^# /, ""); print; found=1; exit }' "$SOURCE")
fi
if [ -z "$TITLE" ]; then
  TITLE=$(basename "$SOURCE")
  TITLE=${TITLE%.*}
fi

BASE=$(basename "$SOURCE")
BASE=${BASE%.*}
BUILD_DIR=$(mktemp -d /tmp/academic-latex-pdf.XXXXXX)
trap 'rm -rf "$BUILD_DIR"' EXIT INT TERM
mkdir -p "$OUTPUT_DIR"

# Pandoc uses metadata for the title, so remove only the first level-one heading
# from the disposable build copy to avoid displaying it twice.
awk 'BEGIN { removed=0 } !removed && /^# / { removed=1; next } { print }' "$SOURCE" > "$BUILD_DIR/prepared.md"

pandoc "$BUILD_DIR/prepared.md" \
  --from=markdown+raw_tex \
  --to=latex \
  --standalone \
  --toc \
  --toc-depth=2 \
  --shift-heading-level-by=-1 \
  --lua-filter="$SKILL_DIR/assets/semantic-style.lua" \
  --include-in-header="$SKILL_DIR/assets/header.tex" \
  --pdf-engine=xelatex \
  --variable=documentclass:ctexart \
  --variable=classoption:fontset=none \
  --variable=fontsize:12pt \
  --variable=papersize:a4 \
  --variable=geometry:margin=2.6cm \
  --variable=indent:true \
  --metadata=title:"$TITLE" \
  --metadata=date:'' \
  --output="$BUILD_DIR/$BASE.tex"

cd "$BUILD_DIR"
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error "$BASE.tex"
cp "$BUILD_DIR/$BASE.tex" "$OUTPUT_DIR/$BASE.tex"
cp "$BUILD_DIR/$BASE.pdf" "$OUTPUT_DIR/$BASE.pdf"

printf 'Generated:\n  %s\n  %s\n' "$OUTPUT_DIR/$BASE.tex" "$OUTPUT_DIR/$BASE.pdf"
