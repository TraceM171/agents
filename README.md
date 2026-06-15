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