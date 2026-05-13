---
name: ai-tools-management
description: "Scan, clean, back up, and uninstall AI dev tools on macOS."
author: Henri
created: "2026-03-12"
last_updated: "2026-05-13"
---

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

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

- **Never delete without scanning + backing up first.** Always run a full scan before proposing cleanup. Always back up chat data (irreplaceable) and verify backups (file count, integrity check) before deleting sources.
- **Always dry-run before executing; ask for explicit confirmation.** Show what would be deleted and space freed. Check process state with `pgrep -f <process>` — warn user to close running tools first. Warn about sensitive data (API tokens, internal URLs) in backups.
- **Prefer Trash over rm; scope sudo narrowly.** Use the `trash` helper below. Only use `sudo rm -rf` for `/Applications/*.app` bundles, never with variable paths. Validate dynamically constructed paths are non-empty and under known tool directories.

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

### IDE Tools

| Tool | ID | Detect App | Detect Data | Process Name |
|------|----|-----------|-------------|--------------|
| VS Code | `vscode` | `/Applications/Visual Studio Code.app` | `~/Library/Application Support/Code/` | `Electron` (Code) |
| Cursor | `cursor` | `/Applications/Cursor.app` | `~/.cursor/` | `Cursor` |
| Windsurf | `windsurf` | `/Applications/Windsurf.app` | `~/.windsurf/`, `~/.codeium/` | `Windsurf` |

### CLI Tools

| Tool | ID | Install Method | Detect Data | Process Name |
|------|----|---------------|-------------|--------------|
| Claude Code | `claude-code` | 独立二进制 `~/.local/bin/claude` | `~/.claude/` | `claude` |
| OpenCode | `opencode` | brew: `anomalyco/tap/opencode` | `~/.local/share/opencode/` | `opencode` |
| GitHub Copilot CLI | `copilot` | npm: `@github/copilot` | `~/.copilot/` | `copilot` |
| OpenAI Codex | `codex` | npm: `@openai/codex` | `~/.codex/` | `codex` |
| Cline | `cline` | npm: `cline` | `~/.cline/` | `cline` |
| Gemini CLI | `gemini` | brew: `gemini-cli` | `~/.gemini/` | `gemini` |
| Amp | `amp` | 独立二进制 `~/.local/bin/amp` | `~/.amp/`, `~/.local/share/amp/`, `~/.config/amp/` | `amp` |
| Droid | `droid` | npm: `@factory/cli` 或独立二进制 | `~/.factory/` | `droid` |

### Detection Script

```bash
echo "=== AI Tool Detection ==="

echo "--- IDE Tools ---"
for p in \
  "/Applications/Visual Studio Code.app" \
  "/Applications/Cursor.app" \
  "/Applications/Windsurf.app"; do
  if [ -e "$p" ]; then
    size=$(du -sh "$p" 2>/dev/null | cut -f1)
    echo "  ✅ Found: $p ($size)"
  fi
done

echo "--- CLI Tools ---"
for p in \
  "$HOME/.claude" \
  "$HOME/.local/share/opencode" \
  "$HOME/.opencode" \
  "$HOME/.copilot" \
  "$HOME/.codex" \
  "$HOME/.cline" \
  "$HOME/.gemini" \
  "$HOME/.amp" \
  "$HOME/.factory"; do
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

### GitHub Copilot CLI

```
~/.copilot/
  ├── config.json                                   # ⛔ CONFIG
  ├── permissions-config.json                       # ⛔ CONFIG
  ├── settings.json                                 # ⛔ CONFIG
  ├── command-history-state.json                    # 🟡 MODERATE
  ├── session-state/                                # ⚠️ CHAT — session data (~4M)
  ├── logs/                                         # ✅ CACHE (~136K)
  ├── pkg/                                          # ✅ CACHE — bundled packages (~352M)
  ├── installed-plugins/                            # 🟡 MODERATE
  ├── ide/                                          # 🟡 MODERATE — IDE integration
  ├── oaicopilot/                                   # 🟡 MODERATE
  └── plugin-data/                                  # 🟡 MODERATE
```

### OpenAI Codex

```
~/.codex/
  ├── config.toml                                   # ⛔ CONFIG
  ├── auth.json                                     # ⛔ CONFIG + 🔴 SENSITIVE
  ├── history.jsonl                                 # ⚠️ CHAT — command history
  ├── AGENTS.md                                     # ⛔ CONFIG
  ├── sessions/                                     # ⚠️ CHAT — session data (~443M)
  ├── archived_sessions/                            # ⚠️ CHAT — archived sessions (~49M)
  ├── cache/                                        # ✅ CACHE (~644K)
  ├── log/                                          # ✅ CACHE (~8.4M)
  ├── shell_snapshots/                              # ✅ CACHE
  ├── memories/                                     # 🟡 MODERATE
  ├── plugins/                                      # 🟡 MODERATE (~37M)
  ├── skills/                                       # 🟡 MODERATE
  ├── rules/                                        # 🟡 MODERATE
  ├── sqlite/                                       # 🟡 MODERATE
  ├── ambient-suggestions/                          # 🟡 MODERATE
  ├── computer-use/                                 # 🟡 MODERATE (~28M)
  ├── vendor_imports/                               # 🟡 MODERATE
  ├── node_repl/                                    # 🟡 MODERATE
  └── tmp/                                          # ✅ CACHE
```

### Cline

```
~/.cline/
  └── data/
      ├── globalState.json                          # ⛔ CONFIG — settings, provider prefs
      ├── secrets.json                              # 🔴 SENSITIVE — API keys (minimaxApiKey, zaiApiKey, etc.)
      └── workspaces/                               # 🟡 MODERATE — per-workspace state
```

**Notes:** Cline 是 VS Code 扩展的 CLI 版本。数据量通常较小（~140K）。

### Gemini CLI

```
~/.gemini/
  ├── settings.json                                 # ⛔ CONFIG
  ├── GEMINI.md                                     # ⛔ CONFIG — global rules
  ├── google_accounts.json                          # 🔴 SENSITIVE — Google OAuth
  ├── oauth_creds.json                              # 🔴 SENSITIVE — OAuth credentials
  ├── projects.json                                 # ⛔ CONFIG
  ├── state.json                                    # 🟡 MODERATE
  ├── trustedFolders.json                           # 🟡 MODERATE
  ├── installation_id                               # 🟡 MODERATE
  ├── history/                                      # ⚠️ CHAT — per-session history files (~20M)
  ├── antigravity/                                  # 🟡 MODERATE
  ├── skills/                                       # 🟡 MODERATE
  └── tmp/                                          # ✅ CACHE
```

**Chat extraction:**
```bash
ls ~/.gemini/history/ 2>/dev/null | wc -l
du -sh ~/.gemini/history/ 2>/dev/null
```

### Amp

```
~/.amp/                                             # 主目录 (~125M)
  ├── bin/amp                                       # ⛔ CONFIG — binary (symlinked from ~/.local/bin/amp)
  └── file-changes/                                 # 🟡 MODERATE — tracked file changes (~58M)
~/.local/share/amp/                                 # 数据目录 (~44M)
  ├── threads/                                      # ⚠️ CHAT — per-thread JSON (~44M)
  ├── history.jsonl                                 # ⚠️ CHAT — command history
  ├── session.json                                  # 🟡 MODERATE
  ├── device-id.json                                # 🟡 MODERATE
  ├── secrets.json                                  # 🔴 SENSITIVE — API key
  └── ide/                                          # 🟡 MODERATE — IDE integration
~/.config/amp/
  └── settings.json                                 # ⛔ CONFIG
```

**Notes:** Amp 通过独立安装脚本安装，二进制存储在 `~/.amp/bin/` 并 symlink 到 `~/.local/bin/amp`。自更新命令: `amp update`。

### Droid (Factory)

```
~/.factory/                                         # 主目录 (~217M)
  ├── settings.json                                 # ⛔ CONFIG
  ├── auth.v2.file                                  # 🔴 SENSITIVE — auth token
  ├── auth.v2.key                                   # 🔴 SENSITIVE — auth key
  ├── history.json                                  # ⚠️ CHAT — command history (~36K)
  ├── sessions/                                     # ⚠️ CHAT — per-session data (~18M, 22 sessions)
  ├── sessions-index.json                           # 🟡 MODERATE
  ├── droids/                                       # ⛔ CONFIG — custom droid definitions
  ├── plugins/                                      # 🟡 MODERATE (~3.4M)
  ├── logs/                                         # ✅ CACHE (~186M ⚠️ large)
  ├── cache/                                        # ✅ CACHE
  ├── bin/                                          # ⛔ CONFIG — binary
  ├── code-server-data/                             # 🟡 MODERATE — embedded code server
  ├── code-server.sock                              # temp
  ├── artifacts/                                    # 🟡 MODERATE
  ├── snapshots/                                    # 🟡 MODERATE
  ├── sounds/                                       # 🟡 MODERATE
  ├── telemetry/                                    # ✅ CACHE
  ├── temp/                                         # ✅ CACHE
  ├── ide/                                          # 🟡 MODERATE
  ├── certs/                                        # 🟡 MODERATE
  ├── computer.json                                 # 🟡 MODERATE
  ├── background-processes.json                     # 🟡 MODERATE
  └── background-tasks.json                         # 🟡 MODERATE
```

**Notes:** Droid 由 Factory AI 开发。日志目录可能非常大（~186M），是清理重点目标。npm 包名为 `@factory/cli`。

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
| Logs | Droid | `trash ~/.factory/logs` — 可释放 ~186M |
| Logs | OpenAI Codex | `trash ~/.codex/log` — ~8.4M |
| Logs | GitHub Copilot CLI | `trash ~/.copilot/logs` |
| Cache | OpenAI Codex | `trash ~/.codex/cache ~/.codex/tmp` |
| Temp / telemetry | Droid | `trash ~/.factory/temp ~/.factory/telemetry` |
| Temp | Gemini CLI | `trash ~/.gemini/tmp` |
| Bundled packages | GitHub Copilot CLI | `trash ~/.copilot/pkg` — ~352M, re-downloaded on next run |

#### Moderate (low risk, recoverable)

| Target | Tool | Notes |
|--------|------|-------|
| Bundled Chromium | Windsurf | `ws-browser/` ~465M, re-downloaded on launch |
| WebStorage | VS Code | ~1.4G browser storage |
| All extensions | Cursor/Windsurf | reinstallable from Marketplace |
| Archived sessions | OpenAI Codex | `~/.codex/archived_sessions/` ~49M |
| Shell snapshots | OpenAI Codex | `~/.codex/shell_snapshots/` |
| Code server data | Droid | `~/.factory/code-server-data/` ~1.9M |
| File changes | Amp | `~/.amp/file-changes/` ~58M, 重建代价高 |

#### Aggressive (medium risk)

| Target | Tool | Notes |
|--------|------|-------|
| All extensions | VS Code | ~2.2G, private extensions may be lost |
| Embedding database | Windsurf | rebuilt on next indexing |
| Extension data (globalStorage) | VS Code | may contain extension state |

### 4. Uninstall

**Goal:** Completely remove an AI tool.

1. Check if tool is running → ask user to quit
2. Check for chat data → force backup if not already backed up
3. List everything to delete with sizes
4. Execute removal (see per-tool commands below)
5. Verify no remnants

**Per-tool uninstall commands:**

**IDE Tools:**

- **VS Code:** `trash ~/.vscode ~/Library/Application\ Support/Code ~/Library/Caches/com.microsoft.VSCode` + `sudo rm -rf "/Applications/Visual Studio Code.app"`
- **Cursor:** `trash ~/.cursor` + `sudo rm -rf "/Applications/Cursor.app"`
- **Windsurf:** `trash ~/.windsurf ~/.codeium` + `sudo rm -rf "/Applications/Windsurf.app"`

**CLI Tools:**

- **Claude Code:** `trash ~/.claude` + 删除 `~/.local/share/claude/` 和 `~/.local/bin/claude` 符号链接
- **OpenCode:** `trash ~/.local/share/opencode ~/.opencode` + `brew uninstall opencode`
- **GitHub Copilot CLI:** `trash ~/.copilot` + `npm uninstall -g @github/copilot`
- **OpenAI Codex:** `trash ~/.codex` + `npm uninstall -g @openai/codex`
- **Cline:** `trash ~/.cline` + `npm uninstall -g cline`
- **Gemini CLI:** `trash ~/.gemini` + `brew uninstall gemini-cli`
- **Amp:** `trash ~/.amp ~/.local/share/amp ~/.config/amp` + 删除 `~/.local/bin/amp` 符号链接
- **Droid:** `trash ~/.factory` + `npm uninstall -g @factory/cli` 或删除 `~/.local/bin/droid` 二进制

---

## Sensitive Data Patterns

When scanning or backing up, check and warn:

| Pattern | Type |
|---------|------|
| `*TOKEN*`, `*_KEY`, `*SECRET*` | API credentials |
| `ANTHROPIC_*`, `OPENAI_*`, `GOOGLE_*` | AI service tokens |
| `mongodb://`, `postgres://` | Connection strings |
| `apiKey@*`, `sgamp_user_*` | Amp API keys (`~/.local/share/amp/secrets.json`) |
| `minimaxApiKey`, `zaiApiKey` | Cline API keys (`~/.cline/data/secrets.json`) |
| `auth.v2.file`, `auth.v2.key` | Droid auth tokens (`~/.factory/`) |
| `oauth_creds.json`, `google_accounts.json` | Gemini OAuth (`~/.gemini/`) |
| `auth.json` | Codex auth (`~/.codex/`) |

```bash
grep -rIl -E "(TOKEN|API_KEY|SECRET|PASSWORD|apiKey|mongodb://|postgres://)" <directory> 2>/dev/null
```
