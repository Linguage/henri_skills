---
name: ai-tools-management
description: "Exports directly readable AI chat archives and manages macOS tool cleanup. Use for session backup, disk audits, cleanup, or uninstallation."
created: "2026-03-12"
last_updated: "2026-10-12"
---

> **Single source of truth:** Edit this skill in its source repository, not in a tool's symlinked skill directory.

# AI Development Tools Management (macOS)

Scan, back up, clean, and uninstall AI development tools on macOS.

For recalling previous work, turn stored chat records into ordinary, directly readable files; verify the archive before authorized cleanup of the source sessions. Restoring the original tool state is a separate backup goal.

Data maps and example sizes are illustrative; inspect current files and formats before acting.

Keep this public skill generic: never add real chat excerpts, personal names, account identifiers, machine-specific paths, private project names, or cleanup reports. Store task-specific inventories and audit records privately, outside the skill repository.

## When to Trigger

- User asks to check disk usage of AI/dev tools
- User wants to back up chat histories from AI coding assistants
- User wants to clean caches, duplicate extensions, or unused data
- User wants to uninstall an AI tool completely
- User asks "what AI tools do I have installed" or similar

## Critical Safety Rules

**Non-negotiable. Violating any rule risks permanent data loss.**

- **Scan before removal; back up affected irreplaceable data first.** Verify content, not just counts. Session cleanup must cover active and archived records, or explicitly report exclusions. Removing isolated obsolete binaries does not require copying unrelated chats.
- **Dry-run before executing; obtain scoped confirmation.** List exact paths, expected effects, and estimated space. Reuse existing approval for that batch. Check actual process references and resolved launchers; exclude the inspecting shell from process matches.
- **Prefer Trash; never silently fall back to permanent deletion.** Validate absolute paths against authorized roots. Emptying Trash or permanently deleting user data requires explicit authorization for that batch, not permission to inspect it.
- **Separate completion states.** A verified archive, a verified copy at the user-selected destination, remote synchronization when applicable, removal from the source directory, and actual disk-space release are different facts.

---

## Helper Function

```bash
trash() {
  if [ ! -x /usr/bin/trash ]; then
    printf '%s\n' 'Native trash command unavailable; use Finder after confirmation.' >&2
    return 1
  fi
  for path in "$@"; do
    case "$path" in /*) ;; *) printf '%s\n' 'Absolute paths required.' >&2; return 1 ;; esac
    [ "$path" != / ] || return 1
  done
  /usr/bin/trash -s "$@"
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

**Duplicate extension candidates:** Group directories by `publisher` and `name` from each `package.json`; record `version` and platform. Filename suffix stripping misses architecture suffixes and UUID-named remnants. Before removal, check `.obsolete`, `extensions.json`, profiles and running processes as described in [the cleanup reference](references/backup-and-cleanup.md#conservative-tool-cleanup).

### Cursor

```
/Applications/Cursor.app                           # App bundle
~/.cursor/
  ├── extensions/                                  # 🟡 installed extensions; retain active versions
  ├── projects/                                    # ⛔ CONFIG
  ├── ai-tracking/ai-code-tracking.db              # ⚠️ CHAT — SQLite (may be empty)
  └── *.json                                       # ⛔ CONFIG
```

Standalone Cursor Agent versions may also live in `~/.local/share/cursor-agent/versions/`; resolve `~/.local/bin/agent` and `cursor-agent` and check process references before cleaning old versions.

### Windsurf (Codeium)

```
/Applications/Windsurf.app                         # App bundle
~/.windsurf/
  ├── extensions/                                  # 🟡 installed extensions; retain active versions
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
- Identify duplicate candidates from package metadata as for VS Code; do not remove merely by filename/version.

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

Standalone binaries may live in `~/.local/share/claude/versions/`; resolve `~/.local/bin/claude` and check running versions before removing any binary.

**Sensitive data check:**
```bash
grep -IlE "(TOKEN|KEY|SECRET|PASSWORD)" ~/.claude/settings.json 2>/dev/null
```

### OpenCode

```
~/.local/share/opencode/
  ├── opencode.db                                  # ⚠️ CHAT — SQLite (~14M)
  ├── opencode.db-shm                              # ⚠️ live SQLite state; not an independent cleanup target
  ├── opencode.db-wal                              # ⚠️ may hold committed data not yet checkpointed
  └── snapshot/                                    # ⚠️ recovery data; inspect before removal
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
  ├── *.sqlite, *.sqlite-wal, *.sqlite-shm            # ⚠️ persistent state; never delete WAL independently
  ├── worktrees/                                    # ⚠️ project copies; check uncommitted/unpushed work
  ├── generated_images/, attachments/               # ⚠️ generated/user assets, not disposable caches
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
  ├── .tmp/                                         # 🟡 inspect plugin backups and in-progress installs
  └── tmp/                                          # ✅ CACHE
```

Also inspect `~/.cache/codex-runtimes/` separately; its primary runtime is not a disposable download cache.

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
4. Present summary table: tool, allocated space, logical bytes, rebuildable candidates, persistent data, extensions. Keep active and archived sessions separate; group by recorded project paths without equating similarly named directories.

### 2. Backup

**Goal:** Make complete chat history directly readable for recalling previous work, or preserve resumable originals when the user requests restoration.

Follow [Session backup, readable archiving, and cleanup](references/backup-and-cleanup.md) before exporting or removing sessions. It defines scope, readable archive layout, media deduplication, time-range naming, content verification, destination transfer, and post-cleanup reconciliation.

Ask the user to specify an absolute backup path if none has been provided. Do not assume a folder or storage provider. Export full messages, tool activity and linked attachments as ordinary files in one archive that needs no restoration script to read after extraction. Verify content and the destination copy before authorized source cleanup. Warn that conversations, outputs, and screenshots can contain secrets; do not print credential values or publish archives.

### 3. Clean

**Always scan first. Always dry-run before executing.**

Follow the conservative-cleanup checks in [the reference](references/backup-and-cleanup.md#conservative-tool-cleanup). A directory's size is not its reclaimable size; rebuilding may require network access. Preserve anything whose usage or recovery status is uncertain.

#### Rebuildable candidates (verify usage; not zero risk)

| Target | Tool | Command |
|--------|------|---------|
| Extension VSIX cache | VS Code | `trash ~/Library/Application\ Support/Code/CachedExtensionVSIXs` |
| App cache | VS Code | `trash ~/Library/Application\ Support/Code/CachedData` |
| Browser cache | VS Code | `trash ~/Library/Application\ Support/Code/Cache` |
| State DB backup | VS Code | `trash .../User/globalStorage/state.vscdb.backup` |
| Old logs (>7d) | VS Code | `find .../Code/logs -mtime +7 -exec trash {} +` |
| Duplicate extensions (old versions) | VS Code/Cursor/Windsurf | check `.obsolete`, registrations/profiles and process references before removing |
| Shell snapshots | Claude Code | `trash ~/.claude/shell-snapshots` |
| System cache | VS Code | `trash ~/Library/Caches/com.microsoft.VSCode` |
| Logs | Droid | `trash ~/.factory/logs` — 可释放 ~186M |
| Logs | OpenAI Codex | `trash ~/.codex/log` — ~8.4M |
| Logs | GitHub Copilot CLI | `trash ~/.copilot/logs` |
| Cache / temp | OpenAI Codex | inspect `cache`, `tmp`, and `.tmp` independently; skip active installs |
| Temp / telemetry | Droid | `trash ~/.factory/temp ~/.factory/telemetry` |
| Temp | Gemini CLI | `trash ~/.gemini/tmp` |
| Bundled packages | GitHub Copilot CLI | `trash ~/.copilot/pkg` — ~352M, re-downloaded on next run |

#### Moderate (low risk, recoverable)

| Target | Tool | Notes |
|--------|------|-------|
| Bundled Chromium | Windsurf | `ws-browser/` ~465M, re-downloaded on launch |
| WebStorage | VS Code | ~1.4G browser storage |
| All extensions | Cursor/Windsurf | reinstallable from Marketplace |
| Shell snapshots | OpenAI Codex | `~/.codex/shell_snapshots/` |
| Code server data | Droid | `~/.factory/code-server-data/` ~1.9M |
| File changes | Amp | `~/.amp/file-changes/` ~58M, 重建代价高 |

Archived sessions, project worktrees, generated assets, and SQLite stores are persistent data, not caches. Back up and verify the affected data before authorized removal.

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
