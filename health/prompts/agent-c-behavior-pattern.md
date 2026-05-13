Read: ~/.claude/CLAUDE.md, [project]/CLAUDE.md

Conversation evidence (inline — no file reading needed):
[PASTE EXTRACTED CONVERSATION CONTENT HERE]

Analyze actual behavior against stated rules:

1. Rules violated: Find cases where CLAUDE.md says NEVER/ALWAYS but Claude did the opposite. Quote both the rule and the violation.
2. Repeated corrections: Find cases where the user corrected Claude's behavior more than once on the same issue. These are candidates for stronger rules.
3. Missing local patterns: Find project-specific behaviors the user reinforced in conversation but that aren't in local CLAUDE.md.
4. Missing global patterns: Find behaviors that would apply to any project (not just this one) that aren't in ~/.claude/CLAUDE.md.
5. Anti-patterns and context hygiene: Check for:
   - CLAUDE.md used as wiki/documentation instead of executable rules
   - Skills covering too many unrelated tasks
   - Claude declaring done without running verification
   - Subagents used without tool/permission constraints
   - User re-explaining same context across sessions (missing HANDOFF.md or memory)
   - Long sessions (>20 turns) without /compact or /clear
   - Task switches within session without /clear (context pollution)
   - Same architectural decisions re-discussed (should be in CLAUDE.md or memory)

Output: bullet points only, grouped by: [rules violated] [repeated corrections] [add to local CLAUDE.md] [add to global CLAUDE.md] [anti-patterns]
