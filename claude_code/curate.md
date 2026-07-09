---
name: curate
description: Perform a thorough, whole-tree audit and cleanup of the knowledge base, restructuring it if needed to conform to KNOWLEDGE_ORG.md. Use when the user says "curate" or asks for a deep knowledge cleanup/audit — typically after many reflect runs have left the knowledge tree degraded. Run much less often than reflect; expect it to take longer since it is a thorough pass over the entire tree, not an incremental update.
---

# Curate Skill

Use this skill when the user says "curate" or asks for a deep cleanup, audit, or restructure of the knowledge base. Curate is reflect's big brother: reflect appends one session's learnings incrementally; curate re-examines everything already in the tree and brings it back into line with `KNOWLEDGE_ORG.md`, restructuring where needed.

## When Invoked

The user wants a thorough top-to-bottom review of the entire knowledge tree, not just recent changes. This is typically requested after many `reflect` runs have accumulated drift: duplicated facts, misplaced files, stale status masquerading as model content, mega-files, missing `_basic.md`s, broken kind boundaries, and similar rot. Curate has authority to fully restructure the tree when the current shape no longer fits, per the "Restructuring" section of `KNOWLEDGE_ORG.md`.

This is a heavier operation than reflect: expect to read every file in the tree, not skim it. If the harness allows selecting a stronger or higher-effort model for this task, prefer it — the audit's value comes from careful judgment on ambiguous classification calls, not speed.

## Workflow

### 1. Read the rules in full

Read `KNOWLEDGE_ORG.md` in full before touching anything — invoke the `knowledge-org` skill if available, otherwise read the file directly. `AGENTS.md`'s rules are already in context (injected at session start when running via the Claude Code plugin; read the file directly otherwise). Every judgment made later in this workflow is a rule from `KNOWLEDGE_ORG.md` applied to a specific file — do not rely on memory of the rules.

### 2. Inventory the entire tree

- `ls -R ./knowledge/` (and `./knowledge/.local/`) to get a complete file list. Do not sample — every file gets read.
- For each file, note: path, apparent kind (index / status / model / audit / pattern), size, last-modified.
- Flag anything that doesn't fit the five kinds, or that lives outside the expected `knowledge/<domain>/` shape, for step 3.

### 3. Audit each file against KNOWLEDGE_ORG.md

Read every file and check it against each rule, not just the ones that seem obviously violated:

- **Kind purity** — does the file mix kinds (state in a model, a recipe in a model, rationale in a model)? Split what's mixed.
- **Duplication** — does a fact appear in more than one file? Identify the canonical home (`status.md` for state, a dated audit for history, one model file for reference) and convert the others to links.
- **Placement** — is the file in the right domain? Is anything sitting at top level that should be inside a domain?
- **Naming** — `kebab-case.md`, `YYYY-MM[-descriptor].md` for dated files, no `-v2` / `-final` / `-new` suffixes.
- **`_basic.md` coverage** — does every directory (top level, every domain, `.local/`) have one, and does it accurately list what's in the directory and the recommended read order?
- **Mega-files** — any file that can't be summarized in one sentence, or that clearly bundles unrelated topics, is a split candidate.
- **Per-X convention** — collections of similar instances (services, integrations, environments) each get their own file; flag any that got merged into one.
- **`.local/` scoping** — for each file in `.local/`, apply the test: would a different owner of this project need it? If yes, it's misplaced and belongs in the shared tree.
- **Dated files** — confirm closed audits/incidents haven't been edited in place; corrections should be new dated files, not rewrites of the original.
- **Stale content** — status claims that no longer match reality, dead links, references to removed files or domains.
- **Inconsistencies and contradictions** — facts that conflict across files (two files claiming different values/states for the same thing, rationale that contradicts a decision recorded elsewhere). If the existing knowledge resolves it, fix the stale side. A quick, targeted factcheck against the actual code/config/resource is also fair game when it's fast and clean (e.g. checking one file, running one command) — never go down a rabbit hole in the codebase over this; knowledge review is still the main focus. If it can't be resolved quickly, do not guess — add it to the findings list as a question for the user in step 7. Resolving from evidence is preferred; asking the user is preferred over inventing or assuming.

Keep a running list of findings: file, rule violated, proposed fix. This list is the basis for step 4.

### 4. Decide: patch vs. restructure

Per `KNOWLEDGE_ORG.md`'s "Restructuring" section — if the findings are a handful of local fixes (rename a file, split one mega-file, delete a duplicate), just do them. If the findings show the domain taxonomy itself no longer fits (multiple junk-drawer domains, systemic misplacement, kinds mixed everywhere), propose a restructuring.

**Before executing a restructuring that moves, merges, or deletes more than a few files, summarize the plan and confirm with the user.** This is a hard-to-reverse action across potentially many files — cheap to preview, expensive to redo. Small, obviously-correct fixes (fixing one filename, adding a missing `_basic.md`) don't need this pause.

### 5. Execute

- Use `git mv` for renames/moves so history is preserved, per `KNOWLEDGE_ORG.md`.
- Split mega-files along the seams identified in step 3; update the domain's `_basic.md` to list the new files.
- Merge/deduplicate: keep the fact in its canonical file, replace the others with a link.
- Create any missing `_basic.md` files.
- Do not fabricate content to fill gaps — if a file's classification is genuinely unclear, ask the user rather than guessing.
- Leave closed dated audits untouched; if one contains a fact that needs correcting, open a new dated file per the append-only rule instead of editing the original.

### 6. Stamp the Curate Marker

Write today's date (`YYYY-MM-DD`), and nothing else, to `knowledge/_curated.md` (create it if missing). This is a reserved marker file per `KNOWLEDGE_ORG.md` — tooling (e.g. the status line) reads it to gauge drift since the last curate pass. Do this even on a run that found nothing to fix; a clean audit still resets the drift clock.

### 7. Commit and Push (if applicable)

Same as reflect: if the knowledge directory is a separate repo, ask the user whether to commit and push the changes before finishing. If it's part of the project repo, follow the project's normal commit conventions and only commit if asked. Include the `_curated.md` marker update in this commit.

### 8. Report Summary

Report:
- What was audited (file/directory count)
- What changed structurally (splits, merges, moves, renames, deletions) — a compact list, not a diff dump
- What was left as-is and why, for anything that looked borderline
- Any open questions that need the user's call

## Important Notes

- Curate operates on the whole tree; reflect operates on the current session. Don't use curate to do reflect's job (appending new session learnings) — run reflect first if there's fresh material, then curate to clean up.
- Curate can restructure fully, but "restructure, do not patch" is not a license to reorganize a domain that's already clean — see `KNOWLEDGE_ORG.md`'s "wrong time to restructure" list.
- Never invent facts to resolve an ambiguity; ask the user.
- Confirm before large-blast-radius moves/deletes; small, obviously-correct fixes don't need a pause.
