Read: [project]/.claude/settings.local.json, [project]/CLAUDE.md, [project]/.claude/skills/**/SKILL.md

Conversation evidence (inline — no file reading needed):
[PASTE EXTRACTED CONVERSATION CONTENT HERE]

This project is tier: [SIMPLE / STANDARD / COMPLEX] — apply only the checks appropriate for this tier.

Tier-adjusted hooks checks:
- SIMPLE: Hooks are optional. Only flag if a hook is broken (e.g., fires on wrong file types).
- STANDARD+: PostToolUse hooks expected for the primary language(s) of the project.
- COMPLEX: Hooks expected for all frequently-edited file types found in conversations.
- ALL tiers: If hooks exist, verify correct schema:
  - Each entry needs `matcher` (tool name regex like "Edit|Write") and `hooks` array
  - Each hook in the array needs `type: "command"` and `command` field
  - File path available via `$CLAUDE_TOOL_INPUT_FILE_PATH` env var in commands
  - Flag hooks missing `matcher` (would fire on ALL tool calls)

allowedTools hygiene (ALL tiers):
- Flag stale one-time commands (migrations, setup scripts, path-specific operations).
- Flag dangerous operations:
  - HIGH: sudo *, rm -rf /, *>*
  - MEDIUM: brew uninstall, launchctl unload, xcode-select --reset
  - LOW (cleanup needed): path-hardcoded commands, debug/test commands

MCP configuration (STANDARD+):
- Check enabledMcpjsonServers count (>6 may impact performance)
- Check filesystem MCP has allowedDirectories configured

Prompt cache hygiene (ALL tiers):
- Check CLAUDE.md or hooks for dynamic timestamps/dates injected into system-level context (breaks prompt cache on every request)
- Check if hooks or skills non-deterministically reorder tool definitions
- In conversation evidence, look for mid-session model switches (e.g., user toggling Opus→Haiku→Opus) — flag as cache-breaking: switching model rebuilds entire cache, can be MORE expensive than staying on the original model
- If model switching is detected, recommend: use subagents for different-model tasks instead of switching mid-session

Three-layer defense consistency (STANDARD+):
- For each critical rule in CLAUDE.md (NEVER/ALWAYS items), check if:
  1. CLAUDE.md declares the rule (intent layer)
  2. A Skill teaches the method/workflow for that rule (knowledge layer)
  3. A Hook enforces it deterministically (control layer)
- Flag rules that only exist in one layer — single-layer rules are fragile:
  - CLAUDE.md-only rules: Claude may ignore them under context pressure
  - Hook-only rules: no flexibility for edge cases, no teaching
  - Skill-only rules: no enforcement, no always-on awareness
- Priority: focus on safety-critical rules (file protection, test requirements, deploy gates)

Tier-adjusted verification checks:
- SIMPLE: No formal verification section required. Only flag if Claude declared done without running any check.
- STANDARD+: CLAUDE.md should have a Verification section with per-task done-conditions.
- COMPLEX: Each task type in conversations should map to a verification command or skill.

Output: bullet points only, state the detected tier at the top, grouped by: [hooks issues] [allowedTools to remove] [cache hygiene] [three-layer gaps] [verification gaps]
