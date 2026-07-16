# Taxonomy — the kinds of knowledge

**Status:** ACTIVE since 2026-07-16 (Decision added as a sixth kind; the original five date to the project's start)
**Decision:** Six kinds — **index / status / model / decision / audit / pattern** (`claude_code/KNOWLEDGE_ORG.md`). Every file in a knowledge tree is exactly one of them. A seventh is not added to dodge a rule.

## Why (current reasoning)

The kinds exist to separate **update cadences**: a model changes when the design changes, a status when the system changes, an audit essentially never. A file mixing two forces every reader to re-verify which half is still true.

**Decision earns its own kind because it is the only kind whose cadence is "rarely, but it must be possible."** The other five are each either frozen (audit) or continuously live (status/model/index/pattern). A choice-in-force is neither: it is stable for months, then revisited — and revisiting it must be able to *edit something*, not just append.

Filing decisions under Audit (the original design) made that impossible, because audits are append-only. The consequence, observed in sanctum and not predicted:

- Every re-examination of a settled choice had to open a **new dated file**. Storage architecture accumulated a four-file correction chain (`storage-architecture` → `pricing-correction` → `storagebox-live-tier-reverified` → `backup-retention-decision`) in two days.
- Answering "what did we decide?" cost four reads plus a mental patch-merge, with **nothing marking which answer was live**.
- A corrected price ended up stated in **no current file at all** — readable only inside a dated file whose own title said it was a correction.
- A decision questioned **one day** after it was made was re-derived from primary sources rather than read, because the reasoning existed only as frozen history.

This also explains a complaint that looked separate: "dated audit files are used for things that aren't audits" (investigations, app comparisons, decisions). Agents were **following the rule correctly** — the rule said decisions were audits. The kind was missing, not the discipline.

**Rule of thumb that falls out of this:** if a reader would ask *"is this still true?"*, it is not an audit.

## Rejected

- **Relax "models contain no rationale" instead** — let a model state the current decision + link the audit for deliberation. Rejected: no new kind, but it re-mixes cadences inside the model (the exact thing the taxonomy exists to prevent) and models balloon. The rationale would ride along with design edits forever.
- **Give audits a `SUPERSEDED-BY` / `STILL-ACTIVE` header, keep five kinds** — smallest rule change, append-only preserved, curate could verify headers mechanically. Rejected: still N files to read for one answer, and maintaining a header *is* editing a file the rules call closed — the append-only guarantee becomes a fiction.
- **A `decisions/` subdirectory per domain** — rejected mechanically: it is a second level of nesting, which the structure rules forbid. Decisions are flat in their governing domain as `decision-<topic>.md`.
- **One shared `decisions.md` per domain** — rejected: the mega-file-that-grows-by-appending failure mode the per-X convention exists to prevent.

## Consequences accepted

- `KNOWLEDGE_ORG.md`'s "do not create a sixth kind to dodge the rule" became "do not create a **seventh**". The line's intent (refine the taxonomy, don't add escape hatches) is intact — this refined it rather than dodging it.
- **Rationale now has exactly one home.** `stack.md` and an index's "key decisions" block become pointers; they may name a choice but not argue it. Without this, the new kind would have been a *fourth* home for "why" rather than the only one — the multiplicity, not the location, was the bug.
- Existing trees need decisions extracted from their audit chains. Not automatic; a `curate` pass surfaces them.

## Deliberation

- Commit `5b28d68` — the change itself; body carries the full field-review reasoning.
- Field review of **sanctum** (2026-07-16), the heaviest consumer: three owner complaints — audits used for non-audits, decisions scattering across status/audit/service/security files, and "where does bare-vs-container go?" — all traced to this one root cause.
