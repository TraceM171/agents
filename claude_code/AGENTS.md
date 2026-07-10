# Project AGENTS.md

Agent entry point for this project. Defines the mandatory reads and the consultation contract for the knowledge tree.

## Mandatory reads

These files must be read in full, every session, before doing anything else:

- `knowledge/_basic.md` — project index (subdirectory map, key decisions, philosophy)
- `knowledge/.local/_basic.md` — owner-specific context (VPS, domain, repo, backup, collab rules)
- `knowledge/status.md` — current deployment/project state

**How this reaches you depends on setup — verify, don't assume either way.** Plugin installs (Option A): the `SessionStart` hook explicitly tells you to read these files rather than pre-loading their content — stuffing a large file (especially `status.md`, which only grows) directly into hook context silently truncates past a certain size with no error, so the hook asks for an explicit read instead of gambling on size. Manual installs (Option B, this file symlinked to `CLAUDE.md`): Claude Code's `@` notation (`@knowledge/_basic.md`, `@knowledge/.local/_basic.md`) pre-loads those two directly, but `status.md` is not on that list — read it yourself the same way. **Either way:** if you don't actually see a mandatory file's content already in this conversation at the start of a session, don't take "it was probably preloaded" on faith — read it yourself before doing anything else.

**Transitive rule:** if any mandatory file above, or any file subsequently opened, explicitly marks another file as "always read" or "mandatory", treat that file as mandatory too and read it before acting. The mandatory set is a closure — follow it at runtime, do not wait to be told. (Example: `knowledge/.local/_basic.md` says "Always read `collab.md`" — so `collab.md` is mandatory by transitivity and must be read on the first turn.)

## Proactive consultation (read as needed)

Beyond the mandatory set, consult the rest of the knowledge tree **before acting, not after**. When a task touches a domain:

1. `status.md` is already mandatory reading (above) — but if the task touches the running system and it's been a while since you last looked at it this session (long conversation, resumed session, anything that could have pushed it out of view), re-open it. It is the snapshot of what is deployed, in flight, and recently changed. Stale assumptions about the system are the most common mistake.
2. Open the domain's `_basic.md` next (e.g. `knowledge/services/_basic.md`, `knowledge/security/_basic.md`, `knowledge/operations/_basic.md`) — it tells you what the domain contains and the recommended read order inside it.
3. Read the specific model / pattern / audit files in that domain that the task touches.
4. Cross-reference anything linked from the mandatory reads and from any `_basic.md` you open — links are routing hints, not optional.
5. Use `KNOWLEDGE_ORG.md` only when adding, moving, or restructuring knowledge files — not on every interaction.

Do not wait to be asked. If a relevant file exists, open it. The cost of a quick read is lower than the cost of acting on a stale assumption.

## Capture as you go

Update the knowledge tree inline, while working — the moment a fact is confirmed, a decision is made, or a stale value is caught, write it into the right file immediately (per `KNOWLEDGE_ORG.md`). Do not batch learnings up for a later `reflect` pass by default. `reflect` exists as an end-of-session catch-all for whatever slipped through, not as the primary capture mechanism — a `reflect` run that finds little or nothing to add because everything was already written down live is the expected outcome, not a sign it was skipped.

## Memory discipline — knowledge system only

**Never use external memory functions to remember things.** This includes the Claude Code memory tool, auto-managed `MEMORY.md` sidecars, or any other tool-level persistence layer. They fragment context, drift from the source of truth, and bypass the org rules.

The knowledge tree (`knowledge/**`, governed by `KNOWLEDGE_ORG.md`) is the single source of truth. Anything worth remembering across sessions — facts, decisions, preferences, conventions, environment quirks, deployment state — goes into the appropriate knowledge file using the five kinds, the per-X convention, and the domain structure. Do not write a sidecar memory file, do not call a memory tool, do not duplicate facts into a tool-managed store. If a memory function offers to record something, write it into the knowledge tree instead and ignore the offer.

## Editing knowledge — `KNOWLEDGE_ORG.md` is mandatory reading first

**Read `KNOWLEDGE_ORG.md` in full before any edit to the knowledge tree.** Invoke the `knowledge-org` skill if available, otherwise read the file directly. This is mandatory, not optional. Triggers (any of these means you must read it first):

- Adding a new file
- Moving, renaming, or deleting a file
- Restructuring a domain (split, merge, promote top-level → domain, etc.)
- Changing the kind of a file (e.g. promoting status content into a model)

Why hard: the rules (five kinds, per-X convention, no top-level cruft, no duplication, models contain no state / no history / no recipes) are what keep the tree navigable as it grows. Guessing the rules produces drift, and drift eventually forces a full rewrite. A 5-minute read of `KNOWLEDGE_ORG.md` prevents that.

Quick reminder (still read the full file before editing):

- Files are one of five kinds: **index** / **status** / **model** / **audit** / **pattern**.
- New files go into a domain subdirectory. Do not add top-level files.
- The per-X convention: one file per running service, integration, environment, etc.
- `.local/` is owner-specific. Test: *would a different owner of the same project need this?* If yes, it is not local.
- Model files contain no dates, no state, no history, no recipes — link instead.
- Status lives only in `status.md`. Audits are dated and append-only. Patterns are recipes, not design.
- Link, do not restate. If a fact appears in two files, one of them is wrong.
