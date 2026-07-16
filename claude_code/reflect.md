---
name: reflect
description: Collect everything learned during the current session and update knowledge accordingly. Use when the user says "reflect" or asks to "capture what we've learned".
---

# Reflect Skill

Use this skill when the user says "reflect" or asks to "capture what we've learned" or similar requests to summarize and persist session knowledge.

## When Invoked

The user wants the agent to collect everything learned during the current session and update the knowledge base accordingly.

Knowledge should already be captured inline as work happens, per AGENTS.md's "Capture as you go" — reflect is the end-of-session safety net for whatever didn't get written down live, not the primary capture mechanism. It's typically run once, near the end of a session, not after every few edits. A pass that finds little or nothing *new* to add is the expected steady state — but that's a separate question from whether what was already written live is duplicated or misfiled. Check both; don't let "everything was already captured" skip the audit in step 1 below.

## Workflow

### 1. Audit this session's own live writes

Before hunting for gaps, check what already got written live this session for the mistakes `reflect` exists to catch in aggregate — but scoped cheaply to just this session's diff:

1. `git diff` / `git status` restricted to `knowledge/**`, limited to files this session actually touched.
2. For each changed file, ask:
   - **Duplication** — does this same fact also appear somewhere else now?
   - **Status budget** — did a `status.md` "recent changes" entry grow past **2 lines**, or fail to end with a link? That is the most-violated rule in the whole system and it is violated *from inside this session*, by you, for reasons that felt good at the time. Count the lines; don't eyeball it. Root cause, evidence, next steps, and security narrative all have homes that are not `status.md` (see `KNOWLEDGE_ORG.md`'s "Recent-changes entries are pointers, not records"). Also check ordering: newest first, strictly.
   - **Decision without a home** — did this session settle a choice (a tool, a provider, a design tradeoff, "X not Y because Z")? It needs a `decision-<topic>.md` in the governing domain, stating the current answer, the current why, and the rejected alternatives — not just a mention in `status.md` and a paragraph inside a dated audit. If you wrote a dated file whose job is to correct a fact in an earlier dated file, that fact belongs in a decision/model file, edited in place.
   - **Status inside an append-only file** — did a dated audit you wrote this session pick up "as of this writing" / "built, not yet deployed" / "blocked on X" / "remaining steps"? Move it to `status.md`; audits record only what was true on their date, and can never be corrected later.
   - **Open entries** — did an Open/backlog entry turn into an ordered or cross-domain plan sitting inline instead of being extracted to `phases.md`/`<domain>/plan.md` (see "Open entries are pointers, not plans")?
3. Fix what's found now — trim the status.md entry to a line + link, move the narrative to its canonical home, extract a plan that outgrew the Open section — rather than leaving it for the next `curate`.
4. This is a small, session-scoped check. It does not replace `curate`, which still audits the whole tree for drift accumulated across sessions.

### 2. Identify Learned Information

Review the conversation history and identify:
- New facts about the project
- Decisions made and their rationale
- Architecture choices, patterns, or conventions discovered
- User preferences revealed during the session
- Any other information worth persisting

### 3. Update Knowledge Files

For each piece of learned information:

1. Read the relevant knowledge directory structure with `ls ./knowledge/` or `ls ./knowledge/.local/`, including the domain's `_basic.md`.
2. **Find the canonical home before writing.** Quick grep the tree (or at least the relevant domain) for the fact — if it already lives in `status.md` or a dated audit, update or link there instead of restating it in a new place. `KNOWLEDGE_ORG.md`'s no-duplication rule applies at write time, not just at curate time.
3. **If the fact supersedes an existing one** (a value changed — MFA type, a group membership, a port, a variable name — not a brand-new addition), grep for the old value/term across the tree and fix or link *every* file that states it, not just the one this session naturally touches. This is the main way knowledge goes stale between curate passes; don't leave it for curate to find later.

   **Never touch `knowledge/_curated.md` while doing this.** It is a tooling marker, not knowledge — a timestamp written *only* by the `curate` skill to record when the last whole-tree audit ran. It will look like a stale date to a sweep like this one. It is not. Writing it from `reflect` falsely resets the drift clock and tells the status line the tree was audited when it wasn't. Leave it exactly as found; it is exempt from every staleness and kind-purity check.
4. Create files as needed (invoke the `knowledge-org` skill for the structure rules). Before naming a new file, decide its kind:
   - a reusable recipe is a **pattern**;
   - a completed one-time action (a deploy, a cutover, an incident, an investigation) is a dated **audit** — `<prefix>-YYYY-MM[-DD][-descriptor].md`, prefix first, from the closed list (`audit-`/`incident-`/`deploy-`/`upgrade-`) — from the start, not a generic runbook name that outlives its relevance;
   - a choice that is still in force is a **decision** — `decision-<topic>.md`, no date, living. Ask: *would a reader later ask "is this still true?"* If yes, it is not an audit.
   
   An investigation that reached a conclusion produces **both**: the audit (deliberation, frozen) and the decision (verdict, living).
5. **Update the domain's `_basic.md` in the same pass** whenever a file is created or renamed — an index that lags its directory is exactly the drift curate exists to clean up; don't manufacture more of it.
6. If a file is moved, renamed, or deleted this session, grep the tree for references to its old path and fix them now, not later.
7. Append new information to the appropriate file.
8. If information is time-sensitive or experimental, mark it clearly.

### 4. Commit and Push (if applicable)

If the knowledge directory is a separate repo (not in the project repo), ask the user whether they want to commit and push the changes before finishing.

### 5. Report Summary

After updating knowledge, provide a brief summary:
- Any duplication/misfiling found and fixed in step 1's session-scoped audit
- What new information was captured
- Where it was stored
- Any gaps or uncertainties noted
- If while reading/writing you noticed substantial rule deviations beyond this session's own edits — duplication, mega-files, misplaced content, missing `_basic.md`s, mixed kinds, decisions reachable only through a chain of dated audits — flag it and suggest the user run `curate` for a full audit/cleanup. A file or two slightly off doesn't warrant this; a pattern across the tree does. Note that a `curate` run in *this* session would be reviewing work you just wrote — mention that it lands better in a fresh session (see `curate`'s "Curate needs fresh eyes").

## Important Notes

- Only capture information the user explicitly shared or that was discovered through work
- Do not fabricate or assume information — ask the user if unsure
- Preserve existing knowledge structure — do not restructure unless necessary