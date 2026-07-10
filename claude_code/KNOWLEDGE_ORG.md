---
name: knowledge-org
description: Organization rules for the knowledge/ tree — the five kinds of knowledge, directory structure, naming, and when to restructure. Use before creating, moving, or restructuring any file under knowledge/.
---

# Knowledge Organization Rules

This document defines how to organize knowledge directories so they stay navigable, current, and free of duplication over the life of a project. The rules target the failure modes that appear in long-lived, single-developer projects: mega-files, status rot, misplaced content, and duplicated facts.

The rules are **project-agnostic**. They apply to any project — web, mobile, data, research, design — and to any stack.

## Directory structure

Both the shared knowledge tree and the owner-specific tree follow the same rules. The owner-specific tree (commonly `.local/` or `knowledge.local/`) holds knowledge that applies to a single human or environment; everything else is project-shared.

### Required file in every knowledge directory

- **`_basic.md`** must exist in the root of every knowledge directory — top level and every subdirectory. It is read first and acts as a routing index. The body should list the files in that directory and the recommended read order.

### One level of subdirectories max

Subdirectories hold related files on a single topic. Do not nest deeper than one level. If you need a sub-subdirectory, the taxonomy is wrong — promote it to a peer of its parent.

### File naming

- `kebab-case.md` (e.g. `auth-pattern.md`, not `Auth_Pattern.md`).
- Dated files use the format `YYYY-MM[-descriptor].md` (e.g. `audit-2026-06.md`, `incident-2025-11-payment-outage.md`).
- Reserved names: `_basic.md` (index), `status.md` (current state), `_curated.md` (top level only — single-line date marker written by the curate skill, read by tooling; not one of the five kinds, exempt from kind-purity checks). Do not use these for other purposes.
- No version suffixes (`-v2`, `-final`, `-new`). If a file replaces another, delete the old one and let git history show the change.

## The five kinds of knowledge

Every file in the knowledge tree should be one of five kinds. The kind determines its update cadence, its primary reader, and where it lives.

| Kind | Definition | Update cadence | Primary reader | Example |
|------|------------|----------------|----------------|---------|
| **Index** | Pointer to other files; "what lives where" and "read in this order" | When structure changes | First read of a session | `knowledge/_basic.md`, `services/_basic.md` |
| **Status** | Current state of the system: what is deployed, what is in flight, what changed recently | Updated on every change | Every read | `knowledge/status.md` |
| **Model** | Ongoing reference: how the system is built, the design as it stands today | When the design changes | When working on the topic | `security/model.md`, `architecture/decisions.md` |
| **Audit** | Dated historical record of a specific investigation, decision, or incident | Append-only after closure | When the date is referenced | `security/audit-2026-06.md`, `operations/incident-2025-11-04.md` |
| **Pattern** | Reusable recipe: how to do X with the system, the steps a future task should follow | When a better way is found | When applying the pattern | `security/patterns.md`, `operations/runbooks.md` |

A file that does not fit one of these is either misplaced or the taxonomy is missing a kind. **Do not create a sixth kind to dodge the rule** — refine the taxonomy instead.

### Why the kinds matter

Each kind has a different update cadence. Mixing kinds in one file means every reader needs every update:

- A *model* changes when the design changes (rarely).
- A *status* changes when the system changes (often).
- An *audit* changes when the dated event is reopened (almost never).
- A *pattern* changes when a better way is found (occasionally).

A file that mixes a model and a status forces a reader to verify, on every read, which parts are still true. A file that mixes a model and a pattern forces the reader to skip the recipes when they only want the design.

## Directory taxonomy

A subdirectory is a *domain* — a group of files about a single kind of thing. The default shape:

```
knowledge/
├── _basic.md              # index
├── status.md              # current state
├── <top-level files>      # cross-cutting only (see below)
│
├── <domain-1>/            # one per domain
│   ├── _basic.md          # domain index
│   └── *.md               # model / audit / pattern files
│
├── <domain-2>/
│   └── ...
│
└── .local/                # owner-specific (see "The .local/ directory")
    ├── _basic.md
    └── ...
```

### Choosing domains

A valid domain answers three questions:

1. **What kinds of knowledge live here that do not live elsewhere?**
2. **Who reads these files?**
3. **What is the update cadence?**

If the answer to (1) is "everything else that doesn't fit", the domain is a junk drawer — split it. If the answer to (2) is "everyone, sometimes", the domain is too generic. If the answer to (3) is "whenever", the domain mixes cadences and should be split.

### Top-level is reserved for cross-cutting knowledge

The files at the top of the knowledge tree are the only ones read by every session. Top-level is reserved for knowledge that is truly cross-cutting — read by everyone regardless of what they are working on. Typical top-level files:

- `_basic.md` — the project index
- `status.md` — current state of the system
- `requirements.md` — what the project is for and what it is not (optional)
- `phases.md` — the deployment or delivery roadmap (optional)
- `stack.md` — the chosen tools and why (optional)

If you find yourself adding a new top-level file, ask: **which domain does it belong to?** If the answer is "none, it's its own thing", the project probably needs a new domain, not a new top-level file.

### Cross-cutting knowledge that has no domain

Some knowledge is genuinely cross-domain — it touches every domain. Two examples:

- A **roadmap** of the project (phases, milestones, status of each).
- A **glossary** of domain terms.

These belong at the top level as their own files. They are not part of any single domain because every domain is involved.

## The per-X convention

When a project has many instances of a thing — services, components, integrations, environments, vendors — give each its own file under a per-X domain. One file per instance, always.

Examples of the per-X convention:

- `services/<name>.md` — one file per running service
- `integrations/<name>.md` — one file per third-party integration
- `infrastructure/<env>.md` — one file per environment
- `components/<name>.md` — one file per internal component

### Why per-X matters

A per-X domain **structurally prevents** the "one mega-file that grows by appending" failure mode. The temptation to "just add a section to the existing file" disappears when the convention is "create a new file in the per-X domain". The act of writing forces you to commit to a topic.

### Per-X file checklist

A per-X file has a documented structure so the reader knows where to look. Every per-X file should cover:

1. **Identity** — name, version, location, owner
2. **Purpose** — one paragraph: what this thing does and why it exists
3. **Configuration** — how it is set up (auth, network, data, environment, dependencies)
4. **Operations** — useful commands, runbooks, monitoring, alerts
5. **History** — pointers to dated records (audits, decisions, incidents) that affect it

A per-X file does not duplicate its domain's model — it references the model and adds the per-X details.

## Content rules

### No duplication

If the same fact appears in two files, one of them is wrong. The fix is one of:

- The fact is *current state* → it lives in `status.md`. Other files reference it; they do not restate it.
- The fact is *historical* → it lives in a dated audit file. The model references the audit.
- The fact is *reference* → it lives in exactly one model file. Other files link to it; they do not restate it.

### Model files contain no dynamic state

A model file describes the system *as designed*. Current state — "is X deployed? does Y pass the check?" — belongs in `status.md`. A model file that says "X is deployed on 2026-06-08" will be wrong within weeks. State goes in `status.md`; the model references the design.

### Model files contain no historical record

A model file is the current understanding. "We decided X because of Y" belongs in a dated audit file. The model may *reference* the audit but does not restate the rationale inline.

### Model files contain no recipes

"How to do X" is a pattern, not a model. Patterns live in `patterns.md` or `runbooks.md` files in the relevant domain. The model describes the design; the pattern applies it.

### One file, one topic

If a file cannot be summarized in one sentence, it is doing too much. Split it. A 500-line file titled "infrastructure" probably contains facts about the host, the network, the storage, *and* per-instance operations — those are different domains and different files.

### Link, do not restate

When a fact in one file is relevant to another, link to the canonical source. Do not copy the text across files. Restated text drifts; links do not.

### Recent-changes entries are pointers, not records

A `status.md` "recent changes" entry is one line: what changed, and a link to where the full record lives. It is not the record itself. If a change needs more than a line to explain — root cause, evidence, verification steps — that detail belongs in the per-X file's current-state content (if it's a design/config fact) or a dated audit (if it's a historical incident), never written out inline in `status.md`. A status entry that has grown into a paragraph is a sign the fact was captured in the wrong place, not that status.md needed a bigger entry.

This matters most for facts captured live, mid-task, rather than during a dedicated `reflect`/`curate` pass — see `AGENTS.md`'s "Capture as you go" for the live-capture discipline this enables.

### Dated files are append-only

A dated audit or incident file, once closed, is not edited. New findings open a new dated file that references the old one. Corrections to the original go in a new dated file with "Correction:" in the title, not by editing the closed record.

## The .local/ directory

`.local/` (or equivalent) holds knowledge that is:

- **Owner-specific** — about a single human, account, or environment, not the project
- **Not portable** — would not apply if the project moved to a different owner
- **Not security-sensitive model content** — patterns and the model belong in the project-shared tree

Examples that belong in `.local/`:

- Owner account identifiers, contact info, time zone
- SSH key fingerprints, hardware token serial numbers
- Personal collaboration preferences with the assistant

Examples that do **not** belong in `.local/`:

- Auth patterns, integration patterns, account conventions — these are system design and should be shared
- Tool configuration recipes and provider creation snippets — these are reusable
- Decision rationale — this is project history

If unsure, ask: **would a different owner of the same project need this?** If yes, it is not local.

## When something does not fit

If a piece of knowledge cannot be classified into the five kinds, or if no domain is the right home:

1. **Do not create a "misc" / "general" / "other" directory.** That is a sign the taxonomy needs a new kind or domain, not a catch-all.
2. **Do not add it to the top level** unless it is read by every session. Top-level is reserved.
3. **Do not bury it in an unrelated domain** — that is how the mess starts.
4. **Refine the taxonomy.** The right answer is to recognize the missing kind or domain and add it explicitly, not to violate the rules.

## Restructuring

When the existing structure no longer fits the project, restructure — do not patch. The cost of a one-time restructuring is much lower than the cost of permanent confusion caused by drift.

A restructuring is the right time to:

- Split a mega-file (e.g. one >500-line file mixing unrelated topics) into per-X files or new domains
- Extract dynamic state from an index file into `status.md`
- Promote a misplaced file to its proper domain
- Detect renames in git so history is preserved (`git mv` before commit)

A restructuring is the wrong time to:

- Rename files for cosmetic reasons
- Reorganize within a domain that is already clean
- Move files just to move them

## Summary

| Rule | What it prevents |
|------|------------------|
| `_basic.md` in every knowledge directory | Hidden files, undiscoverable content |
| One level of subdirectories max | Accidental deep nesting, lost files |
| `kebab-case.md`; dated `YYYY-MM-*.md`; no version suffixes | Inconsistency, ambiguity, false lineages |
| Five kinds: index / status / model / audit / pattern | Mixed cadences, mixed audiences |
| One file, one topic | Mega-files that grow by appending |
| Model files contain no dates, no state, no history, no recipes | Models that go stale, drift, or balloon |
| Status lives only in `status.md` | State scattered across files, or worse, in the index |
| Audits are dated and append-only | History silently rewritten |
| Patterns are recipes, not design | Models that conflate "what" with "how" |
| No duplication; link, do not restate | Two files claiming to be the truth |
| Recent-changes entries are pointers, not records | `status.md` bloating into a de facto changelog/audit |
| Top-level is cross-cutting only | Top-level becomes a junk drawer |
| Per-X convention for collections of instances | The mega-file-that-grows failure mode |
| Per-X files have a documented structure | Inconsistent per-instance docs |
| `.local/` is owner-specific only | Portable knowledge trapped in private dir |
| Restructure, do not patch | Permanent debt from accumulated drift |
| Refine the taxonomy when something does not fit | The "misc" / "general" escape hatch |
