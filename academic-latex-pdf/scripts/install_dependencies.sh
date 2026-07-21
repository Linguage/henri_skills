#!/bin/sh
set -eu

usage() {
  echo "usage: install_dependencies.sh [--check|--dry-run]" >&2
}

MODE=install
if [ "$#" -gt 1 ]; then
  usage
  exit 2
fi
if [ "$#" -eq 1 ]; then
  case "$1" in
    --check) MODE=check ;;
    --dry-run) MODE=dry-run ;;
    *) usage; exit 2 ;;
  esac
fi

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installer currently supports macOS with Homebrew." >&2
  exit 1
fi

font_present() {
  family=$1
  command -v fc-list >/dev/null 2>&1 && fc-list : family 2>/dev/null | grep -Fq "$family"
}

check_environment() {
  missing=0
  for command_name in python3 pandoc xelatex latexmk pdfinfo pdffonts pdftoppm; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "MISSING command: $command_name"
      missing=1
    fi
  done
  for family in "Noto Serif CJK SC" "Noto Sans CJK SC" "LXGW WenKai"; do
    if ! font_present "$family"; then
      echo "MISSING font: $family"
      missing=1
    fi
  done
  if [ "$missing" -ne 0 ]; then
    return 1
  fi
  echo "Environment is ready."
}

if [ "$MODE" = check ]; then
  check_environment
  exit $?
fi

if [ "$MODE" = dry-run ]; then
  cat <<'EOF'
brew install python pandoc poppler
brew install --cask basictex
sudo /Library/TeX/texbin/tlmgr update --self
sudo /Library/TeX/texbin/tlmgr install latexmk collection-xetex collection-langchinese collection-latexrecommended collection-mathscience enumitem
brew install --cask font-noto-serif-cjk-sc font-noto-sans-cjk-sc font-lxgw-wenkai
fc-cache -f
EOF
  exit 0
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install it from https://brew.sh/ and rerun this script." >&2
  exit 1
fi

brew install python pandoc poppler

if ! command -v xelatex >/dev/null 2>&1; then
  brew install --cask basictex
fi
export PATH="/Library/TeX/texbin:$PATH"

TLMGR=$(command -v tlmgr || true)
if [ -z "$TLMGR" ] && [ -x /Library/TeX/texbin/tlmgr ]; then
  TLMGR=/Library/TeX/texbin/tlmgr
fi
if [ -z "$TLMGR" ]; then
  echo "tlmgr was not found after installing BasicTeX. Start a new shell and rerun." >&2
  exit 1
fi

sudo "$TLMGR" update --self
sudo "$TLMGR" install \
  latexmk \
  collection-xetex \
  collection-langchinese \
  collection-latexrecommended \
  collection-mathscience \
  enumitem

for cask in font-noto-serif-cjk-sc font-noto-sans-cjk-sc font-lxgw-wenkai; do
  if ! brew list --cask "$cask" >/dev/null 2>&1; then
    brew install --cask "$cask"
  fi
done

if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f
fi

check_environment
