---
name: reflect
description: Collect everything learned during the current session and update knowledge accordingly. Use when the user says "reflect" or asks to "capture what we've learned".
---

# Reflect Skill

Use this skill when the user says "reflect" or asks to "capture what we've learned" or similar requests to summarize and persist session knowledge.

## When Invoked

The user wants the agent to collect everything learned during the current session and update the knowledge base accordingly.

## Workflow

### 1. Identify Learned Information

Review the conversation history and identify:
- New facts about the project
- Decisions made and their rationale
- Architecture choices, patterns, or conventions discovered
- User preferences revealed during the session
- Any other information worth persisting

### 2. Update Knowledge Files

For each piece of learned information:

1. Read the relevant knowledge directory structure with `ls ./knowledge/` or `ls ./knowledge/.local/`
2. Create files or subdirectories as needed (refer to `KNOWLEDGE_ORG.md` for structure rules)
3. Append new information to the appropriate file
4. If information is time-sensitive or experimental, mark it clearly

### 3. Commit and Push (if applicable)

If the knowledge directory is a separate repo (not in the project repo), ask the user whether they want to commit and push the changes before finishing.

### 4. Report Summary

After updating knowledge, provide a brief summary:
- What new information was captured
- Where it was stored
- Any gaps or uncertainties noted

## Important Notes

- Only capture information the user explicitly shared or that was discovered through work
- Do not fabricate or assume information — ask the user if unsure
- Preserve existing knowledge structure — do not restructure unless necessary