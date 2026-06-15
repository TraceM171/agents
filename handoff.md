---
name: handoff
description: Generate a copy-pasteable handoff prompt summarizing the current session for the next one. Use when the user says "handoff", "wrap up", or asks for a summary to paste into a new session.
---

# Handoff Skill

Use this skill when the user says "handoff", "wrap up", or asks for a session summary to carry into a new session.

## When Invoked

The user wants a self-contained prompt they can paste into a fresh session so the next agent can pick up where this one left off.

## Workflow

### 1. Identify Session State

Review the conversation history and pull out:
- Concrete things done (past tense, with file paths or commit refs where relevant)
- Concrete next steps (imperative, ordered)
- Open questions, blockers, or assumptions worth flagging
- Non-obvious state the next session needs (branch, env, partial edits, in-progress work)

### 2. Pull Pointers From Knowledge

Open the knowledge tree to ground the handoff — do not restate what is already in the tree:
- `@knowledge/_basic.md` and `@knowledge/.local/_basic.md` — project layout and owner context
- `@knowledge/status.md` — what is deployed, in flight, recently changed
- Domain `_basic.md` files for any area the session touched
- `@AGENTS.md` and `@KNOWLEDGE_ORG.md` — rules the next session must follow

Quote paths as `@`-prefixed pointers so the next agent can load them on demand. Do not paste large excerpts.

### 3. Draft the Handoff

Write a tight, copy-pasteable prompt. Target medium-small — long enough to be unambiguous, short enough to skim. Use this shape:

```
# Handoff — <one-line session topic>

## Goal
<one or two sentences: what this session was trying to accomplish>

## Done
- <concrete change, with file path or commit if relevant>

## Next
1. <imperative step, ordered>

## Context
- @knowledge/path/to/relevant.md — <one line: why it matters>
- <non-obvious state: branch, env var, partial work, assumption>
- <open question or blocker>

## Start
Read AGENTS.md and the @-pointers above, then resume at "Next".
```

Prefer this shape, but adjust section names to fit the work. Keep it pointer-heavy: inline detail only when there is no knowledge file to point at.

### 4. Output Rule

**Output only the handoff. No text before it, no text after it, no "Here is your handoff:" framing.** The user is going to copy the result directly into a new session, so anything outside the handoff becomes noise in the next session's context.

## Important Notes

- The handoff is read-only — do not edit the knowledge tree, commit, or change project state
- Pointers beat prose: if a fact already lives in a knowledge file, link to it rather than restate
- If a step depends on something the next session cannot discover (e.g. an unmerged branch, a local-only env var), call it out explicitly in "Context"
- When in doubt, shorten — a tight handoff is more useful than a complete one
