---
name: health
description: "Audit agent config health across all layers. Run periodically or when collaboration feels off."
version: "1.3.0"
created: "2026-03-13"
source: https://github.com/tw93/claude-health
author: Tw93
modifications: 本 Skill 可能是在原作者 Skill 的基础上进行了修改。
last_updated: "2026-03-13"
---

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

# Claude Code Configuration Health Audit

Systematically audit the current project's Claude Code setup using the six-layer framework:
`CLAUDE.md → rules → skills → hooks → subagents → verifiers`

The goal is not just to find rule violations, but to diagnose which layer is misaligned and why — **calibrated to the project's actual complexity**.

## Step 0: Assess project tier

```bash
P=$(pwd)
echo "source_files: $(find "$P" -type f \( -name "*.rs" -o -name "*.ts" -o -name "*.py" -o -name "*.go" -o -name "*.lua" -o -name "*.swift" \) -not -path "*/.git/*" -not -path "*/node_modules/*" | wc -l)"
echo "contributors: $(git -C "$P" log --format='%ae' 2>/dev/null | sort -u | wc -l)"
echo "ci_workflows:  $(ls "$P/.github/workflows/"*.yml 2>/dev/null | wc -l)"
echo "skills:        $(ls "$P/.claude/skills/" 2>/dev/null | wc -l)"
echo "claude_md_lines: $(wc -l < "$P/CLAUDE.md" 2>/dev/null)"
```

Use this rubric to pick the audit tier before proceeding:

| Tier | Signal | What's expected |
|------|--------|-----------------|
| **Simple** | <500 source files, 1 contributor, no CI | CLAUDE.md only; 0–1 skills; no rules/; hooks optional |
| **Standard** | 500–5K files, small team or CI present | CLAUDE.md + 1–2 rules files; 2–4 skills; basic hooks |
| **Complex** | >5K files, multi-contributor, multi-language, active CI | Full six-layer setup required |

**Apply the tier's standard throughout the audit. Do not flag missing layers that aren't required for the detected tier.**

## Step 0.5: Check for skill updates (weekly)

```bash
CACHE="$HOME/.cache/claude-health-last-check"
VER="1.3.0"
NOW=$(date +%s)
LAST=$(cat "$CACHE" 2>/dev/null | tr -d '[:space:]')
LAST=${LAST:-0}
if (( NOW - LAST > 604800 )); then
    SHA=$(curl -sf "https://api.github.com/repos/tw93/claude-health/commits/main" | grep -o '"sha": "[^"]*"' | head -1 | cut -d'"' -f4 | cut -c1-7)
    PREV=$(cat "$CACHE.v" 2>/dev/null | tr -d '[:space:]')
    [[ -n "$SHA" && -n "$PREV" && "$SHA" != "$PREV" ]] && echo "[UPDATE] claude-health 有更新: npx skills add tw93/claude-health@latest"
    echo "$NOW" > "$CACHE"; [[ -n "$SHA" ]] && echo "$SHA" > "$CACHE.v"
fi
```

## Step 1: Collect configuration snapshot

```bash
P=$(pwd)
SETTINGS="$P/.claude/settings.local.json"

echo "=== CLAUDE.md (global) ===" ; cat ~/.claude/CLAUDE.md
echo "=== CLAUDE.md (local) ===" ; cat "$P/CLAUDE.md" 2>/dev/null || echo "(none)"
echo "=== rules/ ===" ; find "$P/.claude/rules" -name "*.md" 2>/dev/null | while IFS= read -r f; do echo "--- $f ---"; cat "$f"; done
echo "=== skill descriptions ===" ; grep -r "^description:" "$P/.claude/skills" ~/.claude/skills 2>/dev/null
echo "=== hooks ===" ; python3 -c "import json,sys; d=json.load(open('$SETTINGS')); print(json.dumps(d.get('hooks',{}), indent=2))" 2>/dev/null
echo "=== MCP ===" ; python3 -c "
import json
try:
    d=json.load(open('$SETTINGS'))
    s = d.get('mcpServers', d.get('enabledMcpjsonServers', {}))
    names = list(s.keys()) if isinstance(s, dict) else list(s)
    n = len(names)
    print(f'servers({n}):', ', '.join(names))
    est = n * 25 * 200  # ~200 tokens/tool, ~25 tools/server
    print(f'est_tokens: ~{est} ({round(est/2000)}% of 200K)')
except: print('(no MCP)')
" 2>/dev/null
echo "=== allowedTools count ===" ; python3 -c "import json; d=json.load(open('$SETTINGS')); print(len(d.get('permissions',{}).get('allow',[])))" 2>/dev/null
echo "=== HANDOFF.md ===" ; cat "$P/HANDOFF.md" 2>/dev/null || echo "(none)"
```

Collect skill security and quality data for Agent D:

```bash
P=$(pwd)
# Exclude self from audit -- a diagnostic tool should not evaluate itself (see issue #2)
SELF_SKILL="health/SKILL.md"

echo "=== SKILL INVENTORY ==="
for DIR in "$P/.claude/skills" "$HOME/.claude/skills"; do
  [ -d "$DIR" ] || continue
  find -L "$DIR" -name "SKILL.md" 2>/dev/null | grep -v "$SELF_SKILL" | while IFS= read -r f; do
    WORDS=$(wc -w < "$f" | tr -d ' ')
    IS_LINK="no"; LINK_TARGET=""
    SKILL_DIR=$(dirname "$f")
    if [ -L "$SKILL_DIR" ]; then
      IS_LINK="yes"; LINK_TARGET=$(readlink -f "$SKILL_DIR")
    fi
    echo "path=$f words=$WORDS symlink=$IS_LINK target=$LINK_TARGET"
  done
done

echo "=== SKILL SECURITY SCAN ==="
for DIR in "$P/.claude/skills" "$HOME/.claude/skills"; do
  [ -d "$DIR" ] || continue
  find -L "$DIR" -name "SKILL.md" 2>/dev/null | grep -v "$SELF_SKILL" | while IFS= read -r f; do
    echo "--- SCANNING: $f ---"
    # Prompt injection
    grep -inE 'ignore (previous|above|all) (instructions|prompts|rules)' "$f" && echo "[!] PROMPT_INJECTION: $f"
    grep -inE '(you are now|pretend you are|act as if|new persona)' "$f" && echo "[!] ROLE_HIJACK: $f"
    # Data exfiltration
    grep -inE '(curl|wget).*(-X *POST|--data).*\$' "$f" && echo "[!] DATA_EXFIL: $f"
    grep -inE 'base64.*encode.*secret|base64.*encode.*key|base64.*encode.*token' "$f" && echo "[!] DATA_EXFIL_B64: $f"
    # Destructive commands
    grep -nE 'rm\s+-rf\s+[/~]' "$f" && echo "[!] DESTRUCTIVE: $f"
    grep -nE 'git push --force\s+origin\s+main' "$f" && echo "[!] DESTRUCTIVE_GIT: $f"
    grep -nE 'chmod\s+777' "$f" && echo "[!] DESTRUCTIVE_PERM: $f"
    # Hardcoded credentials
    grep -nE '(api_key|secret_key|api_secret|access_token)\s*[:=]\s*["'"'"'][A-Za-z0-9+/]{16,}' "$f" && echo "[!] HARDCODED_CRED: $f"
    # Obfuscation
    grep -nE 'eval\s*\$\(' "$f" && echo "[!] OBFUSCATION_EVAL: $f"
    grep -nE 'base64\s+-d' "$f" && echo "[!] OBFUSCATION_B64: $f"
    grep -nE '\\x[0-9a-fA-F]{2}' "$f" && echo "[!] OBFUSCATION_HEX: $f"
    # Safety override
    grep -inE '(override|bypass|disable)\s*(the\s+)?(safety|rules?|hooks?|guard|verification)' "$f" && echo "[!] SAFETY_OVERRIDE: $f"
  done
done

echo "=== SKILL FRONTMATTER ==="
for DIR in "$P/.claude/skills" "$HOME/.claude/skills"; do
  [ -d "$DIR" ] || continue
  find -L "$DIR" -name "SKILL.md" 2>/dev/null | grep -v "$SELF_SKILL" | while IFS= read -r f; do
    if head -1 "$f" | grep -q '^---'; then
      echo "frontmatter=yes path=$f"
      sed -n '2,/^---$/p' "$f" | head -10
    else
      echo "frontmatter=MISSING path=$f"
    fi
  done
done

echo "=== SKILL SYMLINK PROVENANCE ==="
for DIR in "$P/.claude/skills" "$HOME/.claude/skills"; do
  [ -d "$DIR" ] || continue
  find "$DIR" -maxdepth 1 -type l 2>/dev/null | while IFS= read -r link; do
    TARGET=$(readlink -f "$link")
    echo "link=$(basename "$link") target=$TARGET"
    if [ -d "$TARGET/.git" ]; then
      REMOTE=$(git -C "$TARGET" remote get-url origin 2>/dev/null || echo "unknown")
      COMMIT=$(git -C "$TARGET" rev-parse --short HEAD 2>/dev/null || echo "unknown")
      echo "  git_remote=$REMOTE commit=$COMMIT"
    fi
  done
done
```

## Step 2: Collect conversation evidence

Read conversation files directly — do NOT write to disk and pass paths to subagents (subagents cannot read `~/.claude/` paths). Instead, read content here and inline it into agent prompts in Step 3.

```bash
PROJECT_PATH=$(pwd | sed 's|/|-|g' | sed 's|^-||')
CONVO_DIR=~/.claude/projects/-${PROJECT_PATH}

# List the 15 most recent conversations with sizes
ls -lhS "$CONVO_DIR"/*.jsonl 2>/dev/null | head -15
```

For each conversation file you want to include, use the Read tool (or jq via Bash) to extract its text content directly into a variable in your context. Assign files to agents B and C based on size:
- Large (>50KB): 1–2 per agent
- Medium (10–50KB): 3–5 per agent
- Small (<10KB): up to 10 per agent

Extract each file's content with:
```bash
cat <file>.jsonl | jq -r '
  if .type == "user" then "USER: " + ((.message.content // "") | if type == "array" then map(select(.type == "text") | .text) | join(" ") else . end)
  elif .type == "assistant" then
    "ASSISTANT: " + ((.message.content // []) | map(select(.type == "text") | .text) | join("\n"))
  else empty
  end
' 2>/dev/null | grep -v "^ASSISTANT: $" | head -300
```

Store the output in your context. You will paste it inline into the agent B and C prompts below.

## Step 3: Launch parallel diagnostic agents

Spin up **four focused subagents** in parallel, each examining one diagnostic dimension:

### Agent A — Context Layer Audit
Read the prompt from `prompts/agent-a-context-audit.md` and launch a subagent with it. Fill in [project path] and [conversation content] placeholders.

### Agent B — Control + Verification Layer Audit
Read the prompt from `prompts/agent-b-control-verification.md` and launch a subagent with it. Fill in [project path] and [conversation content] placeholders.

### Agent C — Behavior Pattern Audit
Read the prompt from `prompts/agent-c-behavior-pattern.md` and launch a subagent with it. Fill in [project path] and [conversation content] placeholders.

### Agent D — Skill Security & Quality Audit
Read the prompt from `prompts/agent-d-skill-security.md` and launch a subagent with it. Fill in [project path] and [conversation content] placeholders.

Paste the extracted conversation content inline into agent B and C prompts. Do not pass file paths.

## Step 4: Synthesize and present

Aggregate all agent outputs into a single report with these sections:

### 🔴 Critical (fix now)
Rules that were violated, missing verification definitions, dangerous allowedTools entries, MCP token overhead >12.5%, cache-breaking patterns in active use. **Agent D security findings**: prompt injection, data exfiltration, destructive commands, hardcoded credentials, obfuscation, safety overrides detected in skills.

### 🟡 Structural (fix soon)
CLAUDE.md content that belongs elsewhere, missing hooks for frequently-edited file types, skill descriptions that are too long, single-layer critical rules missing enforcement, mid-session model switching. **Agent D quality findings**: missing frontmatter, overly broad descriptions, content bloat (>5000 words), broken file references in skills.

### 🟢 Incremental (nice to have)
New patterns to add, outdated items to remove, global vs local placement improvements, context hygiene habits, HANDOFF.md adoption, skill frequency optimization. **Agent D provenance findings**: symlink source identification, missing version numbers, unknown-origin skills.

---

**Stop condition:** After presenting the report, ask:
> "Should I draft the changes? I can handle each layer separately: global CLAUDE.md / local CLAUDE.md / hooks / skills."

Do not make any edits without explicit confirmation.
