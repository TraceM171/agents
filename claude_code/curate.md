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
- **Open/backlog scope** — does `status.md` (or a domain's own backlog) hold an entry that has an internal order/dependency, spans more than one domain, or has grown past ~5–7 items? Per `KNOWLEDGE_ORG.md`'s "Open entries are pointers, not plans", that belongs in `phases.md`/`<domain>/plan.md`, not inline.
- **Inconsistencies and contradictions** — facts that conflict across files (two files claiming different values/states for the same thing, rationale that contradicts a decision recorded elsewhere). If the existing knowledge resolves it, fix the stale side. A factcheck against the actual code/config/resource is capped at a couple of quick, targeted reads (a file or two, a command or two) per finding — not a live-system audit: no SSH sessions, no querying running services, no sweeping multiple compose files or scripts to build a picture. If confirming a suspected mismatch would take more than that, skip the check and go straight to marking it for review instead — knowledge review is the main focus, not a codebase investigation. Curate never edits code or anything outside the knowledge tree, and never silently rewrites knowledge to match what it finds in code — any mismatch a factcheck turns up between knowledge and the code gets marked in the findings list for review in step 8, never resolved in place. If a knowledge-to-knowledge contradiction can't be resolved from existing knowledge, that's a business-level fact question — add it to the findings list as a question for the user in step 8.

Keep a running list of findings: file, rule violated, proposed fix. This list is the basis for step 4.

### 4. Decide: patch vs. restructure

Per `KNOWLEDGE_ORG.md`'s "Restructuring" section — if the findings are a handful of local fixes (rename a file, split one mega-file, delete a duplicate), just do them. If the findings show the domain taxonomy itself no longer fits (multiple junk-drawer domains, systemic misplacement, kinds mixed everywhere), plan a restructuring.

Deciding *what* to restructure — which files move, merge, split, or get deleted — is an organization-of-knowledge call, and that decision is curate's to make on its own judgment; don't ask the user how to organize it.

**Before executing** a restructuring that moves, merges, or deletes more than a few files, summarize the plan and pause for the user's go-ahead. This isn't an organizational question (curate already decided the plan) — it's a safety checkpoint on a hard-to-reverse batch action across potentially many files: cheap to preview, expensive to redo. Small, obviously-correct fixes (fixing one filename, adding a missing `_basic.md`) don't need this pause.

### 5. Execute

- Use `git mv` for renames/moves so history is preserved, per `KNOWLEDGE_ORG.md`.
- Split mega-files along the seams identified in step 3; update the domain's `_basic.md` to list the new files.
- Merge/deduplicate: keep the fact in its canonical file, replace the others with a link.
- Create any missing `_basic.md` files.
- Do not fabricate content to fill gaps. Classification is an organization-of-knowledge call — decide it directly from `KNOWLEDGE_ORG.md` and best judgment rather than asking the user; note genuinely borderline calls in the final report (step 8) instead of stopping to ask.
- Leave closed dated audits untouched; if one contains a fact that needs correcting, open a new dated file per the append-only rule instead of editing the original.

### 6. Commit and Push the Audit (if applicable)

Same as reflect: if the knowledge directory is a separate repo, ask the user whether to commit and push the changes before finishing. If it's part of the project repo, follow the project's normal commit conventions and only commit if asked. Do **not** include `_curated.md` in this commit — the marker isn't stamped yet (step 7).

### 7. Stamp the Curate Marker

Run `date -u +%Y-%m-%dT%H:%M:%SZ` and write its output, and nothing else, to `knowledge/_curated.md` (create it if missing). Use the actual command output, not a remembered or guessed timestamp. This is a reserved marker file per `KNOWLEDGE_ORG.md` — tooling (e.g. the status line) reads it to gauge drift since the last curate pass. Do this even on a run that found nothing to fix; a clean audit still resets the drift clock.

Stamp and commit this **after** step 6's commit lands, as its own small trailing commit (same repo/push decision as step 6) — never bundled with the audit commit. The marker's timestamp has to sit strictly after everything this pass touched; if it shared a commit with the audit, or landed before it, the next drift check would immediately recount this session's own work as post-curate drift (`git log --since=<marker>` includes anything at or after that instant). A bare date had this same problem at whole-day granularity — see `status.md`; this ordering closes the narrower same-commit version of it.

### 8. Report Summary

Report:
- What was audited (file/directory count)
- What changed structurally (splits, merges, moves, renames, deletions) — a compact list, not a diff dump
- What was left as-is and why, for anything that looked borderline
- Any open questions that need the user's call

## Important Notes

- Curate operates on the whole tree; reflect operates on the current session. Don't use curate to do reflect's job (appending new session learnings) — run reflect first if there's fresh material, then curate to clean up.
- Curate can restructure fully, but "restructure, do not patch" is not a license to reorganize a domain that's already clean — see `KNOWLEDGE_ORG.md`'s "wrong time to restructure" list.
- Curate only ever edits files under `knowledge/` (including `.local/`). It never edits code, config, or any file outside the knowledge tree — a knowledge/code mismatch gets flagged for review, not fixed on either side.
- Curate asks the user only about business-level fact questions (e.g. which of two conflicting facts is true). Organization, classification, and restructuring calls are curate's own to make from `KNOWLEDGE_ORG.md` — never ask the user how to organize. The one exception: pause for a go-ahead before executing a large-blast-radius restructuring (many files moved/merged/deleted) — that's a safety checkpoint on the action, not a question about organization.
