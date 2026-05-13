Read: ~/.claude/CLAUDE.md, [project]/CLAUDE.md, [project]/.claude/rules/**, [project]/.claude/skills/**/SKILL.md (exclude health/ skill -- it is the auditor itself)

This project is tier: [SIMPLE / STANDARD / COMPLEX] — apply only the checks appropriate for this tier.

Tier-adjusted CLAUDE.md checks:
- ALL tiers: Is CLAUDE.md short and executable? No prose, no background, no soft guidance.
- ALL tiers: Does it have build/test commands?
- STANDARD+: Is there a "Verification" section with per-task done-conditions?
- STANDARD+: Is there a "Compact Instructions" section?
- COMPLEX only: Is content that belongs in rules/ or skills already split out?

Tier-adjusted rules/ checks:
- SIMPLE: rules/ is NOT required — do not flag its absence.
- STANDARD+: Language-specific rules (e.g., Rust, Lua) should be in rules/ not CLAUDE.md.
- COMPLEX: Path-specific rules should be isolated; no rules in root CLAUDE.md.

Tier-adjusted skill checks:
- SIMPLE: 0–1 skills is fine. Do not flag absence of skills.
- ALL tiers: If skills exist, descriptions should be <12 words (space-separated) and say WHEN to use. (Skip detailed skill content/security analysis -- Agent D handles this.)
- STANDARD+: Low-frequency skills should have disable-model-invocation: true.

Tier-adjusted MEMORY.md checks (STANDARD+):
- Check if project has `.claude/projects/.../memory/MEMORY.md`
- Verify CLAUDE.md references MEMORY.md for architecture decisions
- Ensure scrollbar, rendering, or other key design decisions are documented there

Tier-adjusted AGENTS.md checks (COMPLEX with multiple modules):
- Verify CLAUDE.md includes "AGENTS.md 使用指南" section
- Check that it explains WHEN to consult each AGENTS.md (not just list links)

MCP token cost check (ALL tiers):
- Count MCP servers and estimate token overhead (~200 tokens/tool, ~25 tools/server)
- If estimated MCP tokens > 10% of 200K context (~20,000 tokens), flag as context pressure
- If >6 servers, flag as HIGH: likely exceeding 12.5% context overhead
- Check if any idle/rarely-used servers could be disconnected to reclaim context

Tier-adjusted HANDOFF.md check (STANDARD+):
- STANDARD+: Check if HANDOFF.md exists or if CLAUDE.md mentions handoff practice
- COMPLEX: Recommend HANDOFF.md pattern for cross-session continuity if not present

Skill frequency strategy check (STANDARD+):
- If conversation evidence is available, check actual skill invocation frequency
- High frequency (>1x/session): should keep auto-invoke, optimize description
- Low frequency (<1x/session): should set disable-model-invocation: true
- Very low frequency (<1x/month): consider removing skill, move to AGENTS.md docs

Output: bullet points only, state the detected tier at the top, grouped by: [CLAUDE.md issues] [rules/ issues] [skills description issues] [MCP cost issues] [skill frequency issues]
