# Stack & Design Decisions

Chosen approach for distributing and versioning Arwyl Lite, and why. This is design as it stands — current dynamic state (which version is live, who's on what) lives in `status.md`, not here.

## Taxonomy

- **Five kinds of knowledge**: index / status / model / audit / pattern (`claude_code/KNOWLEDGE_ORG.md`) — the core taxonomy the whole system is built around.
- **Per-X convention**: one file per instance (service, integration, consumer, etc.) for any collection that would otherwise become a mega-file.

## Distribution

- **Channel**: GitHub marketplace `TraceM171/arwyl-lite`, plugin name `arwyl-lite`, marketplace name `arwyl-lite-marketplace`. Previously named `agents-knowledge` (renamed `cda2226`).
- **Multi-tool intent, not multi-tool sharing**: `claude_code/` today; other tools (e.g. OpenCode) get their own top-level folder with real, adapted copies — not one abstraction shared across tools.

## Version-bump-for-cache

Claude Code caches an installed plugin keyed by `plugin.json`'s `version` string, not by commit SHA. Pushing new commits alone does not reach existing installs — `version` must bump too, or the cached copy stays stale even after `/plugin marketplace update` refreshes the marketplace's own git checkout. Learned the hard way twice (`2d491a9`, `3e93d02`) before this became an explicit rule.

Alternative exists: omit `version` entirely → Claude Code falls back to commit-SHA versioning, fully automatic once the per-marketplace auto-update toggle is on. Considered, not adopted — chose to keep explicit semver plus the auto-update toggle instead.

## AGENTS.md is inlined; knowledge files are not

`claude_code/AGENTS.md` is pasted verbatim into the `SessionStart` hook's context (Claude Code hard-caps hook `additionalContext` at 10,000 characters — silent truncation past that, no error). A pre-commit hook (`.githooks`, opt in via `git config core.hooksPath .githooks`) blocks any commit that pushes it over an 8,000-character budget.

`_basic.md` / `status.md` files are deliberately *not* inlined the same way — a growing `status.md` would blow the cap unnoticed — so the hook points the agent at them and lets it `Read` them instead (`09556ec`).

## Memory discipline

Never use Claude Code's own memory tool for project knowledge — the `knowledge/` tree is the single source of truth (`AGENTS.md` "Memory discipline"). Applies to every project that installs this plugin, including this one.

## Commit style

Conventional Commits prefix (`feat` / `fix` / `docs` / `chore` / `refine` / `rename`), short subject, body explaining why when it's non-obvious. No feature branches so far — history is linear on `main`.
