---
name: knowledge-org
description: Organization rules for the knowledge/ tree — the six kinds of knowledge, directory structure, naming, and when to restructure. Use before creating, moving, or restructuring any file under knowledge/.
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
- **Dated files: `<prefix>-YYYY-MM[-DD][-descriptor].md`.** The prefix comes first, then the date, then an optional descriptor. The day is included only when more than one record of that prefix can land in the same month, or when the exact day is itself the identifier (an incident).
  - **The prefix is a closed list:** `audit-` (an investigation or review), `incident-` (something broke), `deploy-` (a one-pass rollout or migration that cannot be re-run), `upgrade-` (a version migration).
  - Correct: `audit-2026-06.md`, `incident-2026-07-08-dns-cascade.md`, `deploy-2026-06-domain-cutover.md`, `upgrade-2026-05-authentik.md`.
  - Wrong: `domain-cutover-2026-06.md` (descriptor before the date), `upgrade-authentik-2026-05.md` (same), `storage-notes-2026-07.md` (prefix not on the list).
  - Sorting is the point: prefix-then-date makes `ls` group by record type and order by time within it. A descriptor-first name sorts next to unrelated files and hides the record type. If none of the four prefixes fit, you are probably not writing a dated record — check whether it is a **decision** (living, `decision-<topic>.md`, no date) or a model.
- **Decision files: `decision-<topic>.md`** — no date. Decisions are living; a date in the name implies frozen. The date belongs in the file's `Status:` line, where it can be updated.
- Reserved names: `_basic.md` (index), `status.md` (current state), `_curated.md` (top level only — single-line UTC timestamp marker, `YYYY-MM-DDTHH:MM:SSZ`, written by the curate skill, read by tooling; not one of the six kinds, exempt from kind-purity checks), `phases.md` (top level only — cross-domain ordered plan) and `plan.md` (domain-scoped ordered plan) — see "Open entries are pointers, not plans" below. Do not use these for other purposes.
- No version suffixes (`-v2`, `-final`, `-new`). If a file replaces another, delete the old one and let git history show the change.

## The six kinds of knowledge

Every file in the knowledge tree should be one of six kinds. The kind determines its update cadence, its primary reader, and where it lives.

| Kind | Definition | Update cadence | Primary reader | Example |
|------|------------|----------------|----------------|---------|
| **Index** | Pointer to other files; "what lives where" and "read in this order" | When structure changes | First read of a session | `knowledge/_basic.md`, `services/_basic.md` |
| **Status** | Current state of the system: what is deployed/published, what is in flight, what changed recently | Updated on every change | Every read | `knowledge/status.md` |
| **Model** | Ongoing reference: how the system is built, the design as it stands today | When the design changes | When working on the topic | `security/model.md`, `services/traefik.md` |
| **Decision** | A choice that is still in force, and the reasoning that keeps it in force | When the choice is revisited | When the choice is questioned or built on | `infrastructure/decision-storage-tier.md` |
| **Audit** | Dated historical record of a specific investigation or incident — what was found/done on that date | Append-only after closure | When the date is referenced | `security/audit-2026-06.md`, `operations/incident-2025-11-04.md` |
| **Pattern** | Reusable recipe: how to do X with the system, the steps a future task should follow | When a better way is found | When applying the pattern | `security/patterns.md`, `operations/runbooks.md` |

A file that does not fit one of these is either misplaced or the taxonomy is missing a kind. **Do not create a seventh kind to dodge the rule** — refine the taxonomy instead.

### Why the kinds matter

Each kind has a different update cadence. Mixing kinds in one file means every reader needs every update:

- A *model* changes when the design changes (rarely).
- A *status* changes when the system changes (often).
- A *decision* changes when the choice is revisited (rarely — but it must be *possible*, in place).
- An *audit* changes when the dated event is reopened (almost never).
- A *pattern* changes when a better way is found (occasionally).

A file that mixes a model and a status forces a reader to verify, on every read, which parts are still true. A file that mixes a model and a pattern forces the reader to skip the recipes when they only want the design.

### Decision vs. Audit — the distinction that matters most

These two are the easiest to confuse and the most damaging to confuse, because they have **opposite** update rules: a decision is edited in place forever; an audit is never edited again.

- **Decision** answers *"what did we choose, and is it still true?"* It is **living**. When the choice is revisited — reaffirmed, adjusted, or overturned — you **edit the decision file in place**.
- **Audit** answers *"what happened on that date?"* It is **frozen**. The investigation, the evidence gathered, the options priced that day, the incident timeline.

An investigation that *reaches* a conclusion produces **both**: a dated audit holding the deliberation, and a decision file holding the conclusion. The audit is the transcript; the decision is the verdict. The verdict is what future readers need, and it must be updatable without opening a new file.

**The failure this prevents:** if the conclusion only lives in an append-only audit, then re-examining it can't update anything — it can only spawn *another* dated file. Do that three times and "what did we decide?" costs four file reads and a mental patch-merge, with nothing marking which answer is live. A pricing figure corrected in a follow-up audit is stated *nowhere current*. If you are about to write a dated file whose purpose is to correct a fact in an earlier dated file, stop: that fact belongs in a decision or model file that you edit directly.

Rule of thumb: **if a reader would ask "is this still true?", it is not an audit.**

### Decision files

Decisions live **in the domain they govern**, as `decision-<topic>.md` — one file per decision (`infrastructure/decision-storage-tier.md`, `security/decision-mfa-policy.md`). Not a `decisions/` subdirectory: that would be a second level of nesting, which the structure rules forbid. Not a single shared `decisions.md` either — that is the mega-file-that-grows-by-appending failure mode, and the per-X convention exists precisely to prevent it.

A decision that genuinely governs the whole project rather than one domain (e.g. "we self-host everything") is cross-cutting and lives at the top level as `decision-<topic>.md`, alongside `stack.md`. These are rare — most decisions belong to a domain. If you have more than two or three, they probably aren't cross-cutting.

A decision file has a fixed shape:

```markdown
# Bulk storage tier

**Status:** ACTIVE since 2026-07-15 (reaffirmed 2026-07-16)
**Decision:** All bulk data on Hetzner Object Storage, presented as POSIX via JuiceFS. DBs stay on local NVMe.

## Why (current reasoning)
- Immich requires POSIX (hardlinks + atomic rename); it has no native S3 support.
- Object Storage is flat €7.85/mo incl VAT to 1TB — a Cloud Volume for the same bulk is €35–56/mo, over the €27.5/mo cap.

## Rejected
- **Storage Box as live tier** — 10-concurrent-connection cap breaks under live app load.
- **Cloud Volume for all bulk** — cost.

## Deliberation
- `audit-2026-07-storage-architecture.md` — original costing + options
- `audit-2026-07-storagebox-live-tier-reverified.md` — 2026-07-16 re-examination
```

Rules for decision files:

- **State the reasoning that is *currently* load-bearing**, not the history of how you got there. When a price changes or an assumption dies, edit the line. The dated audits keep the archaeology.
- **Values that the decision turns on** (a price, a limit, a version) are stated here in their current form. If a later investigation corrects one, edit it here — do not leave the live value readable only inside a dated correction file.
- **`Status:`** is one of:
  - `OPEN — <what's blocking it>` — the choice is identified but not made. This is where an undecided question lives, so it never has to sit in a model as "TBD".
  - `ACTIVE since <date>` — in force. Add `(reaffirmed <date>)` when a re-examination upheld it; that record is what stops the same question being re-litigated from scratch.
  - `SUPERSEDED by <link>` — a later decision replaced it. The file stays; the link chain is the value.
  - `REVERSED <date> — <one line why>` — undone, not replaced.
- **Every decision file is listed in its domain's `_basic.md`**, same as any other file. A decision nobody can find is a decision that gets made twice.

### Where the *why* lives — one home, everything else points

Adding the Decision kind only helps if the other places rationale used to accumulate stop holding it. Rationale has exactly **one** home: the decision file. Everything else names the choice in one line and links.

| File | Holds | Does **not** hold |
|---|---|---|
| `decision-<topic>.md` | The choice, the current why, rejected alternatives | Design detail; operating steps |
| `stack.md` | *What* we use, one line each + link | The why, the alternatives weighed |
| `_basic.md` "key decisions" | A pointer list: choice → link | Any reasoning at all |
| model / per-X | What is true now, how it's built | Why this over that |
| dated audit | What was found/argued on that date | The live answer |

So `stack.md` reads **"Notes: AFFiNE — `decision-notes-app.md`"**, not "AFFiNE (MIT, better mobile than AppFlowy, OIDC on self-hosted CE)". The moment a comparison against an alternative appears in `stack.md` or an index, it has drifted — that sentence is the decision file's opening line, and now there are two of it.

**A ground rule in `stack.md` is a decision too.** "Everything is a container" with a named list of allowed exceptions is a project-wide choice with reasoning and rejected alternatives — it belongs in a top-level `decision-<topic>.md`, with `stack.md` stating the rule and linking. Otherwise the next question that tests the rule ("should this backup job be a container or bare-host?") has nowhere to record its answer, and it gets argued in a dated audit that nobody will find the next time it comes up. **A decision that *applies* an existing ground rule to a specific case is its own decision file** in the governing domain, linking up to the ground rule — not an amendment to `stack.md` and not a paragraph buried in an audit.
- **Rejected alternatives belong here**, not only in the audit — "why not X?" is the single most re-asked question, and re-deriving the answer from primary sources because it wasn't written down currently is pure waste.
- A decision file is **not** a design doc. It records the choice and the why. *How the thing is built* is the model; *how to operate it* is a pattern.

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
│   ├── decision-*.md      # living decisions governing this domain
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
- `phases.md` — a cross-domain ordered plan (optional; created only when one exists — see "Open entries are pointers, not plans")
- `stack.md` — the chosen tools, one line each, linking to the decision file for the reasoning (optional — see "Where the *why* lives" below)

If you find yourself adding a new top-level file, ask: **which domain does it belong to?** If the answer is "none, it's its own thing", the project probably needs a new domain, not a new top-level file.

### Cross-cutting knowledge that has no domain

Some knowledge is genuinely cross-domain — it touches every domain. Two examples:

- A **roadmap** of the project (phases, milestones, status of each).
- A **glossary** of domain terms.

These belong at the top level as their own files. They are not part of any single domain because every domain is involved.

## The per-X convention

When a project has many instances of a thing — services, components, integrations, environments, vendors — give each its own file under a per-X domain. One file per instance, always.

Examples of the per-X convention:

- `services/<name>.md` — one file per running service (or `libraries/<name>.md` — one file per published package, for a project with no running services)
- `integrations/<name>.md` — one file per third-party integration
- `infrastructure/<env>.md` — one file per environment
- `components/<name>.md` — one file per internal component

### Why per-X matters

A per-X domain **structurally prevents** the "one mega-file that grows by appending" failure mode. The temptation to "just add a section to the existing file" disappears when the convention is "create a new file in the per-X domain". The act of writing forces you to commit to a topic.

### Per-X file checklist

A per-X file is a **model** of one instance. It has a documented structure so the reader knows where to look. Every per-X file should cover:

1. **Identity** — name, version, location, owner
2. **Purpose** — one paragraph: what this thing does and why it exists
3. **Configuration** — how it is set up (auth, network, data, environment, dependencies — or, for a pure code component, its props/API surface and build config)
4. **Operations** — the instance's operational *facts*: which commands are safe, what is monitored, what alerts exist, known gotchas. **Links to recipes, does not contain them** (see below).
5. **History** — pointers to the dated records and decisions that affect it

A per-X file does not duplicate its domain's model — it references the model and adds the per-X details.

### Per-X files link to recipes; they do not contain them

The per-X checklist and the "models contain no recipes" rule meet here, and getting the boundary wrong is what produces 700-line per-service files. The split:

- **In the per-X file:** one-off commands and operational facts — "health check: `curl localhost:9567/metrics`", "restarting requires `stop_grace_period: 30s` or the FUSE mount wedges". Things a reader needs *while looking at this instance*.
- **In a pattern file:** any **multi-step procedure with an order** — first deploy, bootstrap, migration, recovery, rotation. If it has numbered steps and a definition of done, it is a pattern, no matter how instance-specific it is.

Where the pattern goes: **if the procedure is a per-instance variation of a generic one, it belongs with the generic one**, not in a file of its own. `operations/add-service.md` covers deploying a service; the AFFiNE-specific bootstrap quirks are a section in it, or — once instance variations genuinely outgrow one file — `operations/add-service-affine.md`, still recognizable as an extension of the same recipe.

**What this rules out:** a `<service>-setup.md` per service, growing to 700 lines and shadowing `services/<service>.md`. That is a second per-X domain, split from the first by kind, and it forces every reader to check two files per service and every writer to guess which one a fact goes in. If a `-setup.md` file exists, its *steps* are a pattern and its *facts* belong in the per-X file — and a deploy that already happened and cannot be re-run is neither: it is a `deploy-YYYY-MM-*.md` audit.

## Content rules

### No duplication

If the same fact appears in two files, one of them is wrong. The fix is one of:

- The fact is *current state* → it lives in `status.md`. Other files reference it; they do not restate it.
- The fact is *a choice still in force* → it lives in exactly one `decision-<topic>.md`. The model and the audits link to it.
- The fact is *historical* → it lives in a dated audit file. The model and the decision reference the audit.
- The fact is *reference* → it lives in exactly one model file. Other files link to it; they do not restate it.

### Model files contain no dynamic state

A model file describes the system *as designed*. Current state — "is X deployed? does Y pass the check?" — belongs in `status.md`. A model file that says "X is deployed on 2026-06-08" will be wrong within weeks. State goes in `status.md`; the model references the design.

### Model files contain no historical record, and no rationale

A model file is the current understanding of *how the system is built*. Two things it is not:

- **Not history.** "On 2026-06-08 we migrated from X" belongs in a dated audit. The model describes what stands today; the audit records the day it changed.
- **Not rationale.** "We chose X over Y because Z" belongs in `decision-<topic>.md`. The model says *the system uses X*; the decision says *why X and not Y*, and stays editable when the why changes.

The model links to both. A reader asking "how does this work?" should not have to wade through why the alternatives lost; a reader asking "why not Y?" should not have to reconstruct it from a design description.

**The open-question trap:** a model must never carry an unresolved choice ("mount delivery: host agent vs container — decided at build time"). The moment it is decided, that line is stale, and nobody goes back for it — the model now actively lies about a question that has an answer. Open choices live in the decision file (`Status: OPEN`) or in `status.md`/a plan; the model states only what is true now.

### Model files contain no recipes

"How to do X" is a pattern, not a model. Patterns live in `patterns.md` or `runbooks.md` files in the relevant domain. The model describes the design; the pattern applies it.

### One file, one topic

If a file cannot be summarized in one sentence, it is doing too much. Split it. A 500-line file titled "infrastructure" probably contains facts about the host, the network, the storage, *and* per-instance operations — those are different domains and different files.

### Link, do not restate

When a fact in one file is relevant to another, link to the canonical source. Do not copy the text across files. Restated text drifts; links do not.

### Recent-changes entries are pointers, not records

A `status.md` "recent changes" entry is **at most two lines and ends with a link**: what changed, and where the full record lives. It is not the record itself.

This is a hard budget, not a style preference, because it is the single most-violated rule in practice — the pressure to "just add the context here while I'm writing it" is present in every session, and it is exactly how `status.md` becomes a changelog nobody can read. **Two lines. Ends with a link. No exceptions for important changes** — importance is an argument for writing the record properly somewhere else, not for a bigger status entry.

What does *not* go in a status entry, ever: root cause, evidence, what was tried, verification steps, next steps, security narrative, rationale. Each of those has a home:

| Tempting to inline | Actually belongs in |
|---|---|
| Root cause, evidence, what broke | a dated `incident-`/`audit-` file |
| Why we chose this | `decision-<topic>.md` |
| How it's configured now | the per-X file |
| What to do next | `status.md` **Open** (one line) or a plan file |

If you cannot say it in two lines, the record is missing — go write it, then link to it. A status entry that has grown into a paragraph is a sign the fact was captured in the wrong place, not that `status.md` needed a bigger entry.

**Ordering:** newest first, strictly. An entry inserted out of order is invisible — readers scan until the dates stop being new and stop there.

This matters most for facts captured live, mid-task, rather than during a dedicated `reflect`/`curate` pass — see `AGENTS.md`'s "Capture as you go" for the live-capture discipline this enables.

### Open entries are pointers, not plans

The twin problem to the one above, on the forward-looking side: the Status kind's own definition includes "what is in flight," which is broad enough to also absorb a multi-step, multi-session plan if nobody stops it. `status.md`'s Open section (or a domain's own backlog) holds only atomic, independent line items — one line each, pointer-only, no sub-steps. It is not the place for an ordered, multi-step initiative.

Extract to a dedicated plan file the moment any of these is true, regardless of how few items exist so far:

- the items have an internal order or dependency (step 2 can't start before step 1 finishes) — an ordered plan, not a queue
- the work touches more than one domain or per-X instance
- the list has grown past roughly 5–7 open items with no end in sight

A queue of independent, same-shaped items scoped to one domain ("install these N apps, any order, one per session") is *not* a plan under this rule — it stays a flat checklist, one line per item, checked off and linked to the resulting per-X file once done.

Where the extracted plan goes: cross-domain → top-level `phases.md`. Single-domain → `<domain>/plan.md`. Both are still Status-kind content — same update cadence, same "every read" audience — just scoped differently from `status.md` itself, the same way a domain's `_basic.md` is still an index despite not being the top-level one.

A plan file has a fixed shape: a one-line goal, ordered phases each carrying a status marker (done / in-progress / pending), a pointer to fuller detail (a per-X file, a dated audit) where one exists, and the current phase called out explicitly enough that a resuming session can tell where things stand from a single read. On completion: write one final pointer line into `status.md`, then delete the plan file — git history keeps the record. A fully-resolved plan is no longer current state, and a kind that never drains anything is the wrong home for it.

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

If a piece of knowledge cannot be classified into the six kinds, or if no domain is the right home:

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
| `kebab-case.md`; dated `<prefix>-YYYY-MM-*.md` from a closed prefix list; no version suffixes | Inconsistency, ambiguity, false lineages |
| Six kinds: index / status / model / decision / audit / pattern | Mixed cadences, mixed audiences |
| Decisions are living and editable; audits are dated and frozen | Correction-chains where no file states the live answer |
| Decision files hold the current "why" + rejected alternatives | Re-deriving settled reasoning from scratch when it's questioned |
| One file, one topic | Mega-files that grow by appending |
| Model files contain no dates, no state, no history, no rationale, no recipes, no open questions | Models that go stale, drift, or balloon |
| Status lives only in `status.md` | State scattered across files, or worse, in the index |
| Audits are dated and append-only | History silently rewritten |
| Patterns are recipes, not design | Models that conflate "what" with "how" |
| No duplication; link, do not restate | Two files claiming to be the truth |
| Recent-changes entries: max 2 lines, ends with a link, newest first | `status.md` bloating into a de facto changelog/audit |
| Open entries are pointers, not plans | `status.md`/backlogs silently absorbing multi-step, multi-session initiatives |
| Top-level is cross-cutting only | Top-level becomes a junk drawer |
| Per-X convention for collections of instances | The mega-file-that-grows failure mode |
| Per-X files have a documented structure | Inconsistent per-instance docs |
| Per-X files link to recipes, never contain them | `<service>-setup.md` shadow files duplicating the per-X domain |
| `.local/` is owner-specific only | Portable knowledge trapped in private dir |
| Restructure, do not patch | Permanent debt from accumulated drift |
| Refine the taxonomy when something does not fit | The "misc" / "general" escape hatch |
