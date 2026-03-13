---
name: ai-tools-management
description: Scan, back up, clean, and uninstall AI development tools on macOS. Use when the user asks about AI tool disk usage, wants to clean caches, back up chat histories, or completely remove an AI coding assistant.
---

# AI Development Tools Management (macOS)

Scan, back up, clean, and uninstall AI development tools on macOS.

## When to Trigger

- User asks to check disk usage of AI/dev tools
- User wants to back up chat histories from AI coding assistants
- User wants to clean caches, duplicate extensions, or unused data
- User wants to uninstall an AI tool completely
- User asks "what AI tools do I have installed" or similar

## Critical Safety Rules

**Non-negotiable. Violating any rule risks permanent data loss.**

1. **Never delete without scanning first.** Always run a full scan before proposing cleanup.
2. **Never delete chat data without backup.** Chat histories contain irreplaceable context.
3. **Verify backups before deleting sources.** Check file count, test decompression, run `sqlite3 ... "PRAGMA integrity_check"` on databases.
4. **Check process state before cleaning.** Use `pgrep -f <process>` — warn the user to close running tools first.
5. **Never use `rm -rf` on dynamically constructed paths without validation.** Verify path is not empty, not a system directory, and falls under a known tool data directory.
6. **Always use dry-run first.** Show what would be deleted and space freed. Ask for explicit confirmation.
7. **Warn about sensitive data in backups.** Chat histories and configs may contain API tokens, internal URLs, code snippets.
8. **Scope sudo narrowly.** Only for `/Applications/*.app` bundles. Never `sudo rm -rf` with variable paths.
9. **Prefer Trash over rm.** Move files to macOS Trash instead of permanent deletion. Allows recovery if user changes mind.

---

## Helper Function

```bash
trash() {
  for path in "$@"; do
    if [ -e "$path" ]; then
      osascript -e "tell application \"Finder\" to delete POSIX file \"$path\"" 2>/dev/null || \
        mv "$path" ~/.Trash/ 2>/dev/null || \
        rm -rf "$path"
    fi
  done
}
```

---

## Tool Registry

### Detection Table

| Tool | ID | Detect App | Detect Data | Process Name |
|------|----|-----------|-------------|--------------|
| VS Code | `vscode` | `/Applications/Visual Studio Code.app` | `~/Library/Application Support/Code/` | `Electron` (Code) |
| Cursor | `cursor` | `/Applications/Cursor.app` | `~/.cursor/` | `Cursor` |
| Windsurf | `windsurf` | `/Applications/Windsurf.app` | `~/.windsurf/`, `~/.codeium/` | `Windsurf` |
| Claude Code | `claude-code` | — (CLI) | `~/.claude/` | `claude` |
| OpenCode | `opencode` | — (CLI) | `~/.local/share/opencode/` | `opencode` |

### Detection Script

```bash
echo "=== AI Tool Detection ==="
for p in \
  "/Applications/Visual Studio Code.app" \
  "/Applications/Cursor.app" \
  "/Applications/Windsurf.app" \
  "$HOME/.windsurf" \
  "$HOME/.codeium" \
  "$HOME/.claude" \
  "$HOME/.local/share/opencode" \
  "$HOME/.opencode"; do
  if [ -e "$p" ]; then
    size=$(du -sh "$p" 2>/dev/null | cut -f1)
    echo "  ✅ Found: $p ($size)"
  fi
done
```

---

## Tool Data Maps

### VS Code + Copilot

```
/Applications/Visual Studio Code.app              # App bundle (~715M)
~/.vscode/extensions/                              # Installed extensions (~2G+)
~/Library/Application Support/Code/
  ├── User/settings.json                           # ⛔ CONFIG
  ├── User/keybindings.json                        # ⛔ CONFIG
  ├── User/workspaceStorage/<hash>/
  │   ├── state.vscdb                              # SQLite: workspace state
  │   └── chatSessions/                            # ⚠️ CHAT: Copilot chat logs (JSON)
  ├── User/globalStorage/state.vscdb               # Global state DB
  ├── CachedExtensionVSIXs/                        # ✅ CACHE
  ├── CachedData/                                  # ✅ CACHE
  ├── Cache/                                       # ✅ CACHE
  ├── WebStorage/                                  # 🟡 MODERATE
  ├── logs/                                        # ✅ CACHE
  └── History/                                     # 🟡 MODERATE
~/Library/Caches/com.microsoft.VSCode/             # ✅ CACHE
~/Library/Saved Application State/com.microsoft.*  # ✅ CACHE
```

**Chat extraction:**
```bash
find ~/Library/Application\ Support/Code/User/workspaceStorage \
  -name "*.json" -path "*/chatSessions/*" 2>/dev/null
```

**Duplicate extension detection:**
```bash
ls ~/.vscode/extensions/ 2>/dev/null | \
  sed 's/-[0-9]*\.[0-9]*\.[0-9]*$//' | sort | uniq -d | while read ext; do
    echo "Duplicate: $ext"
    ls -d ~/.vscode/extensions/${ext}-* 2>/dev/null | while read dir; do
      echo "  $dir ($(du -sh "$dir" | cut -f1))"
    done
  done
```

### Cursor

```
/Applications/Cursor.app                           # App bundle
~/.cursor/
  ├── extensions/                                  # ✅ CACHE — reinstallable (~627M)
  ├── projects/                                    # ⛔ CONFIG
  ├── ai-tracking/ai-code-tracking.db              # ⚠️ CHAT — SQLite (may be empty)
  └── *.json                                       # ⛔ CONFIG
```

### Windsurf (Codeium)

```
/Applications/Windsurf.app                         # App bundle
~/.windsurf/
  ├── extensions/                                  # ✅ CACHE — installed extensions (~1G+)
  ├── plans/                                       # 🟡 MODERATE
  └── worktrees/                                   # 🟡 MODERATE
~/.codeium/windsurf/
  ├── cascade/*.pb                                 # ⚠️ CHAT — Protobuf binary (~80M)
  ├── database/                                    # 🟡 MODERATE — embedding DB (~62M)
  ├── memories/                                    # ⛔ CONFIG — global rules
  ├── codemaps/                                    # 🟡 MODERATE
  └── implicit/                                    # 🟡 MODERATE
```

**Notes:** 
- Cascade `.pb` files cannot be converted to text without the `.proto` schema. Always preserve originals.
- Extensions in `~/.windsurf/extensions/` can be reinstalled from Marketplace.
- Duplicate extension detection:
```bash
ls ~/.windsurf/extensions/ 2>/dev/null | \
  sed 's/-[0-9].*$//' | sort | uniq -d | while read ext; do
    echo "Duplicate: $ext"
    ls -d ~/.windsurf/extensions/${ext}-* 2>/dev/null | while read dir; do
      echo "  $(du -sh "$dir" | cut -f1) - $(basename "$dir")"
    done
  done
```

### Claude Code

```
~/.claude/
  ├── history.jsonl                                # ⚠️ CHAT — command history
  ├── settings.json                                # ⛔ CONFIG + 🔴 SENSITIVE (may contain API tokens)
  ├── projects/                                    # ⛔ CONFIG — per-project data and CLAUDE.md
  ├── shell-snapshots/                             # ✅ CACHE
  ├── todos/                                       # 🟡 MODERATE
  ├── skills/                                      # ⛔ CONFIG — skill definitions
  └── plugins/                                     # ⛔ CONFIG
```

**Sensitive data check:**
```bash
grep -E "(TOKEN|KEY|SECRET|PASSWORD)" ~/.claude/settings.json 2>/dev/null
```

### OpenCode

```
~/.local/share/opencode/
  ├── opencode.db                                  # ⚠️ CHAT — SQLite (~14M)
  ├── opencode.db-shm                              # temp
  └── opencode.db-wal                              # temp
~/.opencode/                                       # ⛔ CONFIG (if exists)
```

**Chat extraction:**
```bash
db="$HOME/.local/share/opencode/opencode.db"
if [ -f "$db" ]; then
  echo "Sessions: $(sqlite3 "$db" 'SELECT COUNT(*) FROM session;')"
  echo "Messages: $(sqlite3 "$db" 'SELECT COUNT(*) FROM message;')"
fi
```

---

## Operations

### 1. Scan

**Goal:** Discover installed AI tools and report space usage.

1. Run detection script
2. For each tool, calculate sizes: `du -sh <path> 2>/dev/null`
3. Identify duplicate extensions (VS Code / Cursor)
4. Present summary table: tool, total size, cache (cleanable), chat data, extensions

### 2. Backup

**Goal:** Export chat histories and critical configs before destructive operations.

1. Create timestamped backup: `~/Downloads/ai-tools-backup-$(date +%Y%m%d-%H%M%S)/`
2. Copy chat data per tool (see data maps for paths and formats)
3. Generate `manifest.json` with tool details, file counts, checksums
4. Verify backup: check SQLite integrity, compare file counts with source
5. Compress: `tar czf`
6. **Warn** user about API tokens and sensitive paths in backup

### 3. Clean

**Always scan first. Always dry-run before executing.**

#### Safe (zero risk)

| Target | Tool | Command |
|--------|------|---------|
| Extension VSIX cache | VS Code | `trash ~/Library/Application\ Support/Code/CachedExtensionVSIXs` |
| App cache | VS Code | `trash ~/Library/Application\ Support/Code/CachedData` |
| Browser cache | VS Code | `trash ~/Library/Application\ Support/Code/Cache` |
| State DB backup | VS Code | `trash .../User/globalStorage/state.vscdb.backup` |
| Old logs (>7d) | VS Code | `find .../Code/logs -mtime +7 -exec trash {} +` |
| Duplicate extensions (old versions) | VS Code/Cursor/Windsurf | detect then `trash` older dirs |
| Shell snapshots | Claude Code | `trash ~/.claude/shell-snapshots` |
| System cache | VS Code | `trash ~/Library/Caches/com.microsoft.VSCode` |

#### Moderate (low risk, recoverable)

| Target | Tool | Notes |
|--------|------|-------|
| Bundled Chromium | Windsurf | `ws-browser/` ~465M, re-downloaded on launch |
| WebStorage | VS Code | ~1.4G browser storage |
| All extensions | Cursor/Windsurf | reinstallable from Marketplace |

#### Aggressive (medium risk)

| Target | Tool | Notes |
|--------|------|-------|
| All extensions | VS Code | ~2.2G, private extensions may be lost |
| Embedding database | Windsurf | rebuilt on next indexing |
| Extension data (globalStorage) | VS Code | may contain extension state |

**Dry-run template:**
```bash
echo "=== DRY RUN ==="
total=0
for target in \
  "$HOME/Library/Application Support/Code/CachedExtensionVSIXs" \
  "$HOME/Library/Application Support/Code/CachedData" \
  "$HOME/Library/Application Support/Code/Cache"; do
  if [ -d "$target" ]; then
    size=$(du -sk "$target" 2>/dev/null | cut -f1)
    total=$((total + size))
    echo "  Would delete: $target (${size}K)"
  fi
done
echo "Total to free: $((total / 1024))M"
```

### 4. Uninstall

**Goal:** Completely remove an AI tool.

1. Check if tool is running → ask user to quit
2. Check for chat data → force backup if not already backed up
3. List everything to delete with sizes
4. Execute removal (see per-tool commands below)
5. Verify no remnants

**Per-tool uninstall commands:**

- **VS Code:** `trash ~/.vscode ~/Library/Application\ Support/Code ~/Library/Caches/com.microsoft.VSCode` + `sudo rm -rf "/Applications/Visual Studio Code.app"`
- **Cursor:** `trash ~/.cursor` + `sudo rm -rf "/Applications/Cursor.app"`
- **Windsurf:** `trash ~/.windsurf ~/.codeium` + `sudo rm -rf "/Applications/Windsurf.app"`
- **Claude Code:** `trash ~/.claude` + `npm uninstall -g @anthropic-ai/claude-code`
- **OpenCode:** `trash ~/.local/share/opencode ~/.opencode` + `trash "$(which opencode)"`

---

## Sensitive Data Patterns

When scanning or backing up, check and warn:

| Pattern | Type |
|---------|------|
| `*TOKEN*`, `*_KEY`, `*SECRET*` | API credentials |
| `ANTHROPIC_*`, `OPENAI_*`, `GOOGLE_*` | AI service tokens |
| `mongodb://`, `postgres://` | Connection strings |

```bash
grep -rIl -E "(TOKEN|API_KEY|SECRET|PASSWORD|mongodb://|postgres://)" <directory> 2>/dev/null
```

---

## Interaction Workflow

1. **Start with scan** — never assume what's installed
2. **Present findings** — summary table with tool, size, cleanable space, chat data
3. **Propose plan** — state risk level and expected savings
4. **Execute incrementally** — safe first, then moderate if needed
5. **Confirm destructive actions** — explicit confirmation for non-cache deletions
6. **Report results** — before/after comparison

---

## Adding New Tools

When encountering an unlisted AI tool:

1. Check common macOS paths: `~/.<tool>`, `~/.local/share/<tool>`, `~/Library/Application Support/<Tool>`
2. Classify each path: CACHE / CHAT / CONFIG / SENSITIVE / MODERATE
3. Identify chat storage format (SQLite / JSON / JSONL / Protobuf)
4. Report findings to user and suggest updating this skill
