# Stack & Design Mechanics

Chosen approach for distributing and versioning Arwyl Lite, and how the moving parts work. This is design as it stands — current dynamic state (which version is live, who's on what) lives in `status.md`; the reasoning behind a settled choice, and the alternatives rejected, live in the `decision-*.md` files, not here.

## Taxonomy

- **Six kinds of knowledge**: index / status / model / decision / audit / pattern (`claude_code/KNOWLEDGE_ORG.md`) — the core taxonomy the whole system is built around. Why six, and what was rejected: `decision-taxonomy-kinds.md`.
- **Per-X convention**: one file per instance (service, integration, consumer, etc.) for any collection that would otherwise become a mega-file.
- **`phases.md` / `<domain>/plan.md`**: reserved Status-kind files for a multi-step, multi-session plan that has outgrown `status.md`'s Open section — see `KNOWLEDGE_ORG.md`'s "Open entries are pointers, not plans".

## Distribution

- **Channel**: GitHub marketplace `TraceM171/arwyl-lite`, plugin name `arwyl-lite`, marketplace name `arwyl-lite-marketplace`. Previously named `agents-knowledge` (renamed `cda2226`).
- **Multi-tool intent, not multi-tool sharing**: `claude_code/` today; other tools (e.g. OpenCode) get their own top-level folder with real, adapted copies — not one abstraction shared across tools.

## Version-bump-for-cache

Claude Code caches an installed plugin keyed by `plugin.json`'s `version` string, not by commit SHA. Pushing new commits alone does not reach existing installs — `version` must bump too, or the cached copy stays stale even after `/plugin marketplace update` refreshes the marketplace's own git checkout. Learned the hard way twice (`2d491a9`, `3e93d02`) before this became an explicit rule.

Alternative exists: omit `version` entirely → Claude Code falls back to commit-SHA versioning, fully automatic once the per-marketplace auto-update toggle is on. Considered, not adopted — chose to keep explicit semver plus the auto-update toggle instead.

**`installed_plugins.json` is not a reliable record of what a project runs.** `~/.claude/plugins/installed_plugins.json` pins a per-project `installPath`/`version`, but it goes stale: during the 2026-07-16 field review it listed `0.1.11` for sanctum while sanctum was demonstrably running `0.1.13`. It is a red herring — do not use it to determine a consumer's version. Trust, in order: the `/plugin` UI, or **behavioural evidence** in the consumer's own output (the `_curated.md` marker format proved `0.1.13` outright: bare date = ≤`0.1.11`, ISO timestamp + separate trailing commit = `0.1.13`). Version-discriminating behaviour beats metadata.

**Skills load from the cache at session start.** A push (even after `/plugin marketplace update`) does not affect the session that made it — it keeps running the previously-cached skill text. Expect to write a rule and then have the *old* rule govern the same session's `reflect`/`curate`.

## AGENTS.md is inlined; knowledge files are not

`claude_code/AGENTS.md` is pasted verbatim into the `SessionStart` hook's context (Claude Code hard-caps hook `additionalContext` at 10,000 characters — silent truncation past that, no error). A pre-commit hook (`.githooks`, opt in via `git config core.hooksPath .githooks`) blocks any commit that pushes it over an **8,500-character** budget. The constant lives in two places that must stay in sync: `.githooks/pre-commit` and `hooks/session-start.py`.

Raised 8,000 → 8,500 in `0.1.14` — the original had no measurement behind it, and the sixth kind's reminder line had to fit. The payload's only other content is the ~150-char read-instruction line, so the worst case is ~8,660 against the 10,000 cap. Measured live at the raise: 8,092 total, 1,908 margin.

`_basic.md` / `status.md` files are deliberately *not* inlined the same way — a growing `status.md` would blow the cap unnoticed — so the hook points the agent at them and lets it `Read` them instead (`09556ec`).

## Rules reach the agent via the skill, not a file

On a **plugin install** there is no `KNOWLEDGE_ORG.md` anywhere in the consuming project — it exists only inside the version-pinned plugin cache. So the rule docs must tell agents to **invoke the `knowledge-org` skill**, never to "read the file".

Wording matters more than it looks: until `0.1.14` both `AGENTS.md` and `curate.md` said *"invoke the skill if available, otherwise read the file directly."* Sanctum's transcripts show **16 direct-read attempts, none of which could have succeeded** — 10 at the project root, 5 under `knowledge/`, 1 at a guessed cache path missing the `claude_code/` segment. Agents burned failed tool calls before falling back to the skill. The sanctioned-sounding fallback caused it.

Reading the cache path directly is also wrong even when it resolves: it is version-pinned, so it silently serves a stale copy after an upgrade. The direct-read fallback now applies only to manual installs, where the repo has its own symlinked copy at a known path.

## Memory discipline

Never use Claude Code's own memory tool for project knowledge — the `knowledge/` tree is the single source of truth (`AGENTS.md` "Memory discipline"). Applies to every project that installs this plugin, including this one.

## Commit style

Conventional Commits prefix (`feat` / `fix` / `docs` / `chore` / `refine` / `rename`), short subject, body explaining why when it's non-obvious. No feature branches so far — history is linear on `main`.
