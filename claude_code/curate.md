---
name: curate
description: Perform a thorough, whole-tree audit and cleanup of the knowledge base, restructuring it if needed to conform to KNOWLEDGE_ORG.md. Use when the user says "curate" or asks for a deep knowledge cleanup/audit — typically after many reflect runs have left the knowledge tree degraded. Run much less often than reflect; expect it to take longer since it is a thorough pass over the entire tree, not an incremental update.
---

# Curate Skill

Use this skill when the user says "curate" or asks for a deep cleanup, audit, or restructure of the knowledge base. Curate is reflect's big brother: reflect appends one session's learnings incrementally; curate re-examines everything already in the tree and brings it back into line with `KNOWLEDGE_ORG.md`, restructuring where needed.

## When Invoked

The user wants a thorough top-to-bottom review of the entire knowledge tree, not just recent changes. This is typically requested after many `reflect` runs have accumulated drift: duplicated facts, misplaced files, stale status masquerading as model content, mega-files, missing `_basic.md`s, broken kind boundaries, and similar rot. Curate has authority to fully restructure the tree when the current shape no longer fits, per the "Restructuring" section of `KNOWLEDGE_ORG.md`.

This is a heavier operation than reflect: expect to read every file in the tree, not skim it. If the harness allows selecting a stronger or higher-effort model for this task, prefer it — the audit's value comes from careful judgment on ambiguous classification calls, not speed.

### Curate needs fresh eyes

**Curate is a review, and a review of your own work is the weakest kind.** If this session wrote knowledge — did the work, ran `reflect`, captured the facts — then you are the author, and you will pass your own writing. You already decided that 10-line status entry was justified when you wrote it; you will decide it again now, for the same reasons, and the pass finds nothing.

This is not hypothetical: it is the observed failure mode. A curate run at the end of a long working session reliably approves that session's own output and reports the tree clean.

So, in order of preference:

1. **Best — run curate in a fresh session.** No memory of writing any of it. If the user invokes curate at the end of a heavy session, say so and offer to defer it: *"I wrote most of today's knowledge — a curate in a fresh session will catch things I'll rationalize. Want me to run it now anyway, or next session?"* Ask; don't refuse.
2. **Next best — delegate the audit to a subagent.** If the harness has one, spawn a general-purpose agent with instructions to read `KNOWLEDGE_ORG.md` and the whole tree and report findings, and give it *no* narrative about the session. It reads what is actually on disk, not what you meant to write. Then act on its findings yourself.
3. **If auditing your own session's writes anyway** — audit them **first and hardest**. For each one ask: *"if I found this file in a tree I had never seen, would I accept it?"* Not "did I have a good reason?" — you did, and it doesn't matter. The reader will not have your reason.

Never skip curate because it might be self-review. A compromised pass beats no pass. Just name the limitation in the step 8 report.

## Workflow

### 1. Read the rules in full

**Invoke the `knowledge-org` skill.** That is how you read the rules — it is the same content, delivered by the harness, and it works regardless of how this plugin was installed. Every judgment made later in this workflow is a rule from `KNOWLEDGE_ORG.md` applied to a specific file — do not rely on memory of the rules.

Do **not** go looking for a `KNOWLEDGE_ORG.md` file on disk. On a plugin install there is no such file in the project — it lives inside the plugin's own versioned cache directory, and guessing at that path wastes tool calls on files that do not exist and risks reading a stale version. Only if the skill is genuinely unavailable (a manual install, where the repo has its own copy at a path the project's `AGENTS.md`/`CLAUDE.md` points to) do you read the file directly.

`AGENTS.md`'s rules are already in context (injected at session start when running via the plugin).

### 2. Inventory the entire tree

- `ls -R ./knowledge/` (and `./knowledge/.local/`) to get a complete file list. Do not sample — every file gets read.
- For each file, note: path, apparent kind (index / status / model / audit / pattern), size, last-modified.
- Flag anything that doesn't fit the six kinds, or that lives outside the expected `knowledge/<domain>/` shape, for step 3.

### 3. Audit each file against KNOWLEDGE_ORG.md

Read every file and check it against each rule, not just the ones that seem obviously violated:

- **Kind purity — between files** — does the file mix kinds (state in a model, a recipe in a model, rationale in a model)? Split what's mixed.
- **Kind purity — *within* a dated file.** Read each dated audit's sections and classify each one *separately*. Audits are where mixed kinds hide, because "it's the record of that work" feels like it licenses including everything about that work. It does not. Look specifically for:
  - **Live status inside an append-only file** — "as of this writing", "built, not yet deployed", "blocked on X", "remaining steps". This is the worst case: the file can never be corrected (append-only), so the claim rots permanently *and* duplicates `status.md`. Move it to `status.md`/`plan.md`, leave the audit describing only what was true on its date.
  - **Design/config description** — how the thing is built belongs in the per-X or model file. The audit records the decision and the evidence, not the resulting spec.
  - **A conclusion with no living home** — see the decision check below.
- **Decisions with no living home.** For each dated audit, ask: *does this file contain a conclusion someone would later ask "is this still true?" about?* If yes, there must be a `decision-<topic>.md` stating it currently. Two smells that mean this is broken:
  - **Correction chains** — file B exists mainly to correct a fact in file A (a price, a limit, a name), and file C reaffirms it. Collapse: the live value goes in the decision file (edited in place); A/B/C stay as dated deliberation and get linked from it. A value that is *only* readable inside a correction file is stated nowhere current.
  - **A decision reachable only by reading N dated files in order.** That is the failure the Decision kind exists to end. Create the decision file, state the current answer + current reasoning + rejected alternatives, link the audits.
- **Duplication** — does a fact appear in more than one file? Identify the canonical home (`status.md` for state, `decision-<topic>.md` for a choice in force, a dated audit for history, one model file for reference) and convert the others to links.
- **Placement** — is the file in the right domain? Is anything sitting at top level that should be inside a domain?
- **Naming** — `kebab-case.md`; dated files are `<prefix>-YYYY-MM[-DD][-descriptor].md` with the prefix from the closed list (`audit-`/`incident-`/`deploy-`/`upgrade-`) and the **prefix before the date**; decisions are `decision-<topic>.md` with no date; no `-v2` / `-final` / `-new` suffixes. Descriptor-first names (`domain-cutover-2026-06.md`) are violations — `git mv` them.
- **`_basic.md` coverage** — does every directory (top level, every domain, `.local/`) have one, and does it accurately list what's in the directory and the recommended read order?
- **Mega-files** — any file that can't be summarized in one sentence, or that clearly bundles unrelated topics, is a split candidate. **Do not let a file's title do the summarizing** — "AFFiNE setup" reads like one topic while the file holds a deploy recipe, an admin pattern, and a root-cause analysis. Test against the *index's own description* of the file: if the `_basic.md` entry needs "X + Y + Z" or a comma-separated list of five things to describe it, that is the split list, already written for you. Length is a hint, not the test: past ~300 lines, look harder; past ~500, assume it splits until proven otherwise.
- **Per-X convention** — collections of similar instances (services, integrations, environments) each get their own file; flag any that got merged into one. Also flag the **inverse**: two files covering the *same* instance split by kind (`services/x.md` + `operations/x-setup.md`). Per `KNOWLEDGE_ORG.md`'s "Per-X files link to recipes", the steps belong with the generic recipe they extend and the facts belong in the per-X file — a per-service shadow file is not a valid home for either.
- **`.local/` scoping** — for **every** file in `.local/`, apply the test: would a different owner of this project need it? If yes, it's misplaced and belongs in the shared tree. Apply this to files that have been there a long time, not just recent additions — a `.local/` file that started genuinely owner-specific accretes portable content section by section (a security protocol, a safety rule, a project standard), and nobody re-runs the test on a file that "was already there". Check **section by section**, not file by file: the fix is usually to move three sections out, not the whole file.
- **Dated files** — confirm closed audits/incidents haven't been edited in place; corrections to *what happened* should be new dated files. (Corrections to a *still-true fact* are different — those belong in the decision/model file, edited in place. See the decision check above.)
- **Stale content** — status claims that no longer match reality, dead links, references to removed files or domains.
- **Resolved open questions.** A model or decision file that poses a choice ("host agent vs container — decide at build time", "TBD", "to be confirmed") when another file already records the answer. Grep the tree for `TBD`, `to be decided`, `at build time`, `vs\.`, `TODO` and check each against the per-X files and `status.md`. This is a knowledge-to-knowledge contradiction — resolvable from existing knowledge, so **fix it**, don't just flag it. It is the most common form of quiet rot: the question was answered and nobody went back.
- **`status.md` hygiene** — every "recent changes" entry is ≤2 lines and ends with a link (`KNOWLEDGE_ORG.md`'s hard budget); entries are strictly newest-first; the Open section holds only atomic one-line pointers. Over-long entries: move the narrative to its real home and cut the entry to a line + link.
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
