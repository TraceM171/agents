# Agents Knowledge Template

Structured knowledge for agent-assisted development. Agents read this to understand your project, preferences, and conventions.

## Setup (2 minutes)

```bash
# 1. Clone this template
git clone <repo-url> ~/agents-template

# 2. In each project, create links and directories
cd your-project
ln ~/agents-template/AGENTS.md .
ln ~/agents-template/KNOWLEDGE_ORG.md .
mkdir -p knowledge/.local

# 3. Create required files
touch knowledge/_basic.md
touch knowledge/.local/_basic.md

# 4. Point your agent to AGENTS.md

# For Claude Code: create CLAUDE.md link to AGENTS.md
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
| `AGENTS.md` | Tells the agent where to find knowledge and rules |
| `KNOWLEDGE_ORG.md` | How to organize new knowledge |

## Rules

1. Never edit `AGENTS.md` directly
2. Read `KNOWLEDGE_ORG.md` before adding knowledge
3. Don't use agent memories — use these folders
4. Keep knowledge current — remove obsolete info

## Reflect Skill

Capture session learnings into the knowledge base.

**Setup:**
```bash
# Claude Code
mkdir -p .claude/skills/reflect
ln ~/agents-template/reflect.md .claude/skills/reflect/SKILL.md

# OpenCode
mkdir -p .opencode/skills/reflect
ln ~/agents-template/reflect.md .opencode/skills/reflect/SKILL.md
```

**Use:** Say "reflect" or use the skill tool to invoke it.

## Curate Skill

Reflect's big brother. Thorough, whole-tree audit and cleanup of the knowledge base — run it much less often than reflect, once knowledge has degraded across many reflect runs (duplication, mega-files, misplaced content). Has authority to fully restructure the tree to conform to `KNOWLEDGE_ORG.md`.

**Setup:**
```bash
# Claude Code
mkdir -p .claude/skills/curate
ln ~/agents-template/curate.md .claude/skills/curate/SKILL.md

# OpenCode
mkdir -p .opencode/skills/curate
ln ~/agents-template/curate.md .opencode/skills/curate/SKILL.md
```

**Use:** Say "curate" or use the skill tool to invoke it. Prefer your strongest available model — this is a careful, thorough pass, not a fast one.

## Status Line

`statusline.py` — Claude Code status line script (context %, model, rate-limit countdowns).

**Setup:**
```bash
ln -s ~/agents-template/statusline.py ~/.claude/statusline.py
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

Generate a copy-pasteable handoff prompt summarizing the current session for the next one.

**Setup:**
```bash
# Claude Code
mkdir -p .claude/skills/handoff
ln ~/agents-template/handoff.md .claude/skills/handoff/SKILL.md

# OpenCode
mkdir -p .opencode/skills/handoff
ln ~/agents-template/handoff.md .opencode/skills/handoff/SKILL.md
```

**Use:** Say "handoff" or "wrap up" or use the skill tool to invoke it.