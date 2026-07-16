# Status — Current State

**As of 2026-07-16.**

## Current version

`0.1.14` (`claude_code/.claude-plugin/plugin.json`), pushed to `origin/main` (`5b28d68`). Marketplace: `arwyl-lite-marketplace` → GitHub `TraceM171/arwyl-lite`.

(The push to get `0.1.7` out briefly failed — SSH agent couldn't sign with the hardware key, "agent refused operation" — retried clean once the key was touched; every version since has pushed normally.)

This machine's marketplace checkout and plugin cache were last refreshed to `0.1.13` (2026-07-16, `/plugin marketplace update` + `/reload-plugins`). **`0.1.14` is pushed but not yet pulled into the cache** — see Open.

## Known consumers

- **sanctum** — installed via the GitHub marketplace route, project-scope enabled (`.claude/settings.json`). Shares this machine's plugin cache (not a separate install), so a refresh here serves both. **Confirmed running `0.1.13`** on 2026-07-16 by behavioural evidence: its `_curated.md` holds an ISO timestamp stamped in a separate trailing commit, which only `0.1.13`'s curate does. Note `installed_plugins.json` claimed `0.1.11` for sanctum at the same time — it is unreliable, see `stack.md`.

## Recent changes

- **`5b28d68`** — **Decision** added as a sixth kind, plus five rule fixes, all traced to one root cause in a sanctum field review. Bumped to 0.1.14. Why + rejected alternatives: `decision-taxonomy-kinds.md`.
- **`6aca49d`** — curate: `_curated.md` marker changed from a bare date to a full UTC timestamp, and marker-stamping moved to after the pass's own commit (not before) — bare-date `git log --since` is midnight-inclusive and double-counted same-day pre-pass commits as drift; even a timestamp alone still let the pass's own closing commit count itself as drift the next time. Bumped to 0.1.13.
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

- Refresh this machine's marketplace checkout + plugin cache to `0.1.14` (`/plugin marketplace update` + `/reload-plugins`), then run a `curate` in sanctum in a **fresh** session to exercise the new rules — owner will do this by hand.
- This `knowledge/` tree itself is brand new (scaffolded 2026-07-10) — expect a `reflect`/`curate` pass to reshape it as real work accumulates. No domains yet, by design.
- Sanctum has pre-`0.1.14` drift the new rules now name: decisions to extract from its infrastructure audit chain, `.local/collab.md` sections failing the portability test, and `operations/*-setup.md` shadow files. Owner's call, not this project's work — recorded so the next `curate` there isn't a surprise.
