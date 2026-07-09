# Agents Knowledge Template

Structured knowledge for agent-assisted development. Agents read this to understand your project, preferences, and conventions.

Per-tool integrations live in their own top-level folder (`claude_code/` today; more may be added later). Each folder holds real, tool-specific copies of the conventions — not shared across tools — so each integration can be adapted to what that tool actually supports.

## Setup — Claude Code

### Option A: Plugin (recommended)

```bash
claude
/plugin marketplace add ~/agents-template
/plugin install agents-knowledge@agents-marketplace
```

Installs the `reflect`, `curate`, `handoff`, and `knowledge-org` skills, plus a `SessionStart` hook. The install prompt asks for a scope — pick **project** (writes to that repo's `.claude/settings.json`, committed, shared with collaborators) if you only want this active in specific repos; **user** installs it globally across every project you open.

Either way, the hook only acts in projects that already have a `knowledge/` directory — it's a complete no-op everywhere else, so a global install won't inject anything or create files in unrelated repos. To adopt the template in a project:

```bash
mkdir knowledge
```

Next session, the hook bootstraps `knowledge/.local/_basic.md` etc. automatically and injects `AGENTS.md`'s rules into context. The status line still needs manual setup below — plugins can't configure `statusLine`.

### Option B: Manual

```bash
# 1. Clone this template
git clone <repo-url> ~/agents-template

# 2. In each project, create links and directories
cd your-project
ln ~/agents-template/claude_code/AGENTS.md .
ln ~/agents-template/claude_code/KNOWLEDGE_ORG.md .
mkdir -p knowledge/.local
touch knowledge/_basic.md knowledge/.local/_basic.md

# 3. Point Claude Code at AGENTS.md
ln -s AGENTS.md CLAUDE.md
```

That's it. The agent will read the knowledge files on first start and follow the organization rules.

## Knowledge Structure

```
knowledge/           # Shared project knowledge (git-tracked)
  _basic.md          # Always read at start
  .local/             # Personal preferences (typically gitignored)
    _basic.md        # Always read at start
  auth/              # Authentication
  infra/             # Infrastructure
  ...
```

## Key Files

| File | Purpose |
|------|---------|
| `claude_code/AGENTS.md` | Tells the agent where to find knowledge and rules |
| `claude_code/KNOWLEDGE_ORG.md` | How to organize new knowledge |

## Rules

1. Never edit `AGENTS.md` directly
2. Read `KNOWLEDGE_ORG.md` before adding knowledge
3. Don't use agent memories — use these folders
4. Keep knowledge current — remove obsolete info

## Reflect Skill

Capture session learnings into the knowledge base. Included in the Claude Code plugin (Option A above).

**Manual setup:**
```bash
# Claude Code
mkdir -p .claude/skills/reflect
ln ~/agents-template/claude_code/reflect.md .claude/skills/reflect/SKILL.md

# OpenCode
mkdir -p .opencode/skills/reflect
ln ~/agents-template/claude_code/reflect.md .opencode/skills/reflect/SKILL.md
```

**Use:** Say "reflect" or use the skill tool to invoke it.

## Curate Skill

Reflect's big brother. Thorough, whole-tree audit and cleanup of the knowledge base — run it much less often than reflect, once knowledge has degraded across many reflect runs (duplication, mega-files, misplaced content). Has authority to fully restructure the tree to conform to `KNOWLEDGE_ORG.md`. Included in the Claude Code plugin (Option A above).

**Manual setup:**
```bash
# Claude Code
mkdir -p .claude/skills/curate
ln ~/agents-template/claude_code/curate.md .claude/skills/curate/SKILL.md

# OpenCode
mkdir -p .opencode/skills/curate
ln ~/agents-template/claude_code/curate.md .opencode/skills/curate/SKILL.md
```

**Use:** Say "curate" or use the skill tool to invoke it. Prefer your strongest available model — this is a careful, thorough pass, not a fast one.

## Knowledge-Org Skill

`KNOWLEDGE_ORG.md` packaged as an on-demand skill, so it can be pulled into context whenever the agent is creating, moving, or restructuring knowledge files — not just during reflect/curate. Included in the Claude Code plugin (Option A above).

**Manual setup:**
```bash
# Claude Code
mkdir -p .claude/skills/knowledge-org
ln ~/agents-template/claude_code/KNOWLEDGE_ORG.md .claude/skills/knowledge-org/SKILL.md

# OpenCode
mkdir -p .opencode/skills/knowledge-org
ln ~/agents-template/claude_code/KNOWLEDGE_ORG.md .opencode/skills/knowledge-org/SKILL.md
```

## Status Line

`claude_code/statusline.py` — Claude Code status line script (knowledge-tree activity with reflect/curate nudges, git branch/session diffs, context %, model, rate-limit countdowns). Not installable via the plugin — `statusLine` is a user-level setting only.

**Setup:**
```bash
ln -s ~/agents-template/claude_code/statusline.py ~/.claude/statusline.py
```

Then in `~/.claude/settings.json`:
```json
"statusLine": {
  "type": "command",
  "command": "python3 /home/trace/.claude/statusline.py",
  "refreshInterval": 10
}
```

## Handoff Skill

Generate a copy-pasteable handoff prompt summarizing the current session for the next one. Included in the Claude Code plugin (Option A above).

**Manual setup:**
```bash
# Claude Code
mkdir -p .claude/skills/handoff
ln ~/agents-template/claude_code/handoff.md .claude/skills/handoff/SKILL.md

# OpenCode
mkdir -p .opencode/skills/handoff
ln ~/agents-template/claude_code/handoff.md .opencode/skills/handoff/SKILL.md
```

**Use:** Say "handoff" or "wrap up" or use the skill tool to invoke it.
