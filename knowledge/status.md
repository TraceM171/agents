# Status — Current State

**As of 2026-07-16.**

## Current version

`0.1.13` (`claude_code/.claude-plugin/plugin.json`), pushed to `origin/main` (`b586a1f`). Marketplace: `arwyl-lite-marketplace` → GitHub `TraceM171/arwyl-lite`.

(The push to get `0.1.7` out briefly failed — SSH agent couldn't sign with the hardware key, "agent refused operation" — retried clean once the key was touched; every version since has pushed normally.)

This machine's marketplace checkout and plugin cache were last refreshed to `0.1.10` (`fd0c381`) via `/plugin marketplace update` + `/reload-plugins` on 2026-07-11 — now three versions stale against the `0.1.13` push above; needs another refresh cycle before this machine (or sanctum, which shares the cache) picks it up. Manual semver bump is still what actually invalidates a stale cached copy, even with the per-marketplace auto-update toggle on (cache is keyed by the `version` string).

## Known consumers

- **sanctum** — installed via the GitHub marketplace route, project-scope enabled (`.claude/settings.json`). Shares this machine's plugin cache (not a separate install) — still on the cached `0.1.10`; owner plans to run `/plugin marketplace update` there to pick up `0.1.13`. Last confirmed running the plugin during a 2026-07-15 `curate` pass (the one whose bare-date marker exposed the drift-counting bug fixed in `0.1.13` — see Recent changes).

## Recent changes

- **(uncommitted)** — `_curated.md` marker switched from a bare date (`YYYY-MM-DD`) to a full UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`); `curate_signal()` and the curate skill updated to match. Root cause: bare-date markers are midnight-inclusive under `git log --since`, so a curate pass run anywhere but first-thing-in-the-morning had that whole day's pre-pass commits double-counted as post-pass drift — confirmed against sanctum's 2026-07-15 session logs (curate ran last that day, at 19:49 UTC, after a 26-file storage/backup rewrite it had already reviewed; the bare-date marker still made the next day's nudge count all 26 files as new drift). Old bare-date markers (this tree's own `knowledge/_curated.md` says `2026-07-11`; sanctum's says `2026-07-15`) no longer match the new regex and fall back to the never-curated `total_files >= 15` gate until their next curate pass rewrites them in the new format — expected, not a bug. Also reordered curate's steps 6/7 (commit-then-stamp, not stamp-then-commit) and split the marker into its own trailing commit: verified against sanctum's real commits that a timestamp alone still didn't fully close the gap — the pass's own closing commit (`238d692`, landing 39s after the marker would've been written mid-session) still counted as fresh drift on its own, since any commit landing at or after the marker instant counts. Stamping strictly after that commit lands closes it. Bumped to 0.1.13.
- **`3df49f2`** — statusline: curate's own knowledge edits no longer count toward the dirtiness/dup-risk trigger (mirrors the existing reflect-boundary exclusion). Bumped to 0.1.12.
- **`b0471bd`** — statusline: dropped always-on dirty/changed baseline stats (nudge-only now), fixed read/edit % exceeding 100% after mid-session file renames/deletes. Bumped to 0.1.11.
- **`efd5ed9`** — added "Open entries are pointers, not plans" (status/plan split, `phases.md`/`plan.md`) and de-biased infra-only examples across the rule docs. Bumped to 0.1.10.
- **`85fe55a`** — merged statusline's dirtiness stat into the reflect segment (`reflect: N dirty (Y%)`), made the count clickable. Bumped to 0.1.9.
- **`0e783e3`** — fixed the reflect-boundary detector: tool-result and `isMeta` transcript entries were closing the boundary before reflect's own edits ran, so its own writes always counted as dirty. Bumped to 0.1.8.
- **`e0219f6`** — fixed reflect-boundary detection missing user-typed `/reflect` invocations (no assistant `tool_use` emitted for those) — partial fix, see `0e783e3` for the rest. Bumped to 0.1.7.
- **`2146543`** — fixed reflect-boundary detection not matching marketplace-namespaced skill names (`arwyl-lite:reflect`), so the nudge never cleared for sanctum. Bumped to 0.1.6.
- **`d089882`** — made statusline's read/edited/branch/session counts clickable (OSC8 hyperlink) — each opens a generated local HTML page with details/diffs.
- **`655e47f`** — statusline's `reflect?` nudge gained a second trigger: fires again after >2 knowledge files edited since the last reflect pass, not just once per session. Bumped to 0.1.5.
- **`59a6207`** — closed the live-capture duplication gap: status.md recent-changes entries must be pointers not records (this rule), append-to-existing-file added as a mandatory `KNOWLEDGE_ORG.md` reread trigger, reflect gained a session-scoped dedup-audit step.
- **`09556ec`** — `SessionStart` hook stopped inlining large knowledge files (`_basic.md`/`status.md`) — see `stack.md`'s "AGENTS.md is inlined; knowledge files are not".
- **`cda2226`** — renamed from `agents-knowledge` to `arwyl-lite` (plugin + marketplace name).

## Open

- Refresh this machine's marketplace cache to `0.1.13` (`/plugin marketplace update` + `/reload-plugins`) — owner doing this after the push; confirm sanctum picks it up next session (shared cache), and that its next `curate` pass rewrites `_curated.md` from the old bare date into the new timestamp format.
- This `knowledge/` tree itself is brand new (scaffolded 2026-07-10) — expect a `reflect`/`curate` pass to reshape it as real work accumulates. No domains yet, by design.
