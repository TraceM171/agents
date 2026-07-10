# Status — Current State

**As of 2026-07-10.**

## Current version

`0.1.7` (`claude_code/.claude-plugin/plugin.json`), committed locally (`e0219f6`) — **not yet pushed**: `git push origin main` failed, SSH agent couldn't sign with the hardware key (`cardno:14_330_696`, "agent refused operation"). Needs a retry once the key is touched/unlocked. Marketplace: `arwyl-lite-marketplace` → GitHub `TraceM171/arwyl-lite`.

This machine's marketplace checkout (`~/.claude/plugins/marketplaces/arwyl-lite-marketplace`) was last confirmed at `a52fd67` (0.1.4) — now several commits behind `main`. Cached versions on disk (`~/.claude/plugins/cache/arwyl-lite-marketplace/arwyl-lite/`): `0.1.0`–`0.1.4`; `0.1.5`–`0.1.7` not yet fetched. Needs a `/plugin marketplace update` to catch up — this is what sanctum needs before it sees the reflect-boundary fix below.

Manual semver bump is still required for any consumer's cached copy to refresh — an auto-update toggle exists per-marketplace (`/plugin` → Marketplaces → enable) but even with it on, the cache is keyed by the `version` string, so a bump is still what actually invalidates the old cached copy.

## Known consumers

- **sanctum** — installed via the GitHub marketplace route, project-scope enabled (`.claude/settings.json`). Shares this machine's plugin cache (not a separate install) — whatever version is cached here is what sanctum sees next session. Last confirmed running the plugin during a 2026-07-09 `curate` pass, when the marketplace had just been migrated to this GitHub route.

## Recent changes

- **`e0219f6`** — 0.1.6's namespacing fix wasn't the whole story: when a user directly types `/reflect` (or `/arwyl-lite:reflect`), Claude Code never emits an assistant `Skill` tool_use at all — it's a `"user"`-type transcript entry whose content is a literal string containing `<command-name>/arwyl-lite:reflect</command-name>`. The boundary logic only recognized the tool_use form, so a user-typed `/reflect` was completely invisible to it. Verified by replaying sanctum's actual transcript (`f954ac2a...` — the session behind the "why still suggested, I just ran it" report, screenshot-matched: `8 edited (12%) · 8 dirty (12%)` before, `8 edited (12%) · 4 dirty (6%)` after): edited-since-reflect went from 8/8 (boundary never moved) to the true 4/8 (real post-reflect edits — nudge still fires, now for a legitimate reason). Bumped to 0.1.7.
- **`2146543`** — found and fixed the real cause of sanctum's "reflect nudge fires right after I just reflected": boundary detection matched only the bare skill name `"reflect"`, but marketplace-installed consumers invoke it namespaced (`"arwyl-lite:reflect"`), so `reflected` never went true and the boundary never got set for sanctum specifically — every knowledge edit all session counted as "since last reflect" regardless of whether reflect had actually just run. Now matches on the name after the last `:`. Also relabeled the nudge reason `dup-risk` → `dirtiness`, made that count always-visible on the knowledge line (not just inside the nudge), un-bolded the effort-level brackets, and added a session cost segment (`$X.XX`) between model and rate limits. Bumped to 0.1.6.
- **`d089882`** — statusline `read`/`edited`/`branch`/`session` counts are now clickable (OSC8 hyperlink, needs a terminal that supports it — iTerm2/kitty/wezterm/VSCode). Each opens its own generated local HTML page in `$TMPDIR`: knowledge page lists read/edited file paths; branch/session pages list changed files with foldable per-file diffs (colored +/-, "Expand all" toggle, 300-line cap per file, wide layout).
- **`655e47f`** — statusline `reflect?` nudge gained a second, independent trigger: more than 2 knowledge files edited since the last `reflect` pass (excluding reflect's own edits) re-fires the nudge, unlike the old "nothing captured at all" triggers, which fire at most once per session. Needed a two-pass transcript scan — the reflect boundary isn't knowable while still walking reflect's own edits in a single forward pass. Bumped to 0.1.5.
- **`59a6207`** — closed the gap that let sanctum duplicate facts across `status.md` and per-X files despite having read `KNOWLEDGE_ORG.md` shortly before writing: added "recent-changes entries are pointers, not records", extended the mandatory-reread trigger list to cover appending to an *existing* file (not just new/move/restructure — the actual failure mode observed), and gave `reflect` a session-scoped dedup-audit step instead of only checking for gaps.
- **`09556ec`** — `SessionStart` hook stopped inlining `knowledge/_basic.md` / `.local/_basic.md` / `status.md` content directly into hook context; large files were silently truncated past Claude Code's undocumented size cap, with no error surfaced. The hook now tells the agent to `Read` them itself.
- **`cda2226`** — renamed from `agents-knowledge` to `arwyl-lite` (plugin + marketplace name).

## Open

- **Push blocked** — `e0219f6` (0.1.7) is local-only, `git push origin main` failed on SSH key signing. Retry once resolved.
- Confirm sanctum's plugin actually picks up `0.1.7` next session there (needs the marketplace checkout refreshed past `a52fd67` first) — this is the release that actually carries the fix sanctum's session needed (0.1.6's namespacing fix alone didn't cover slash-command invocations).
- This `knowledge/` tree itself is brand new (scaffolded 2026-07-10) — expect a `reflect`/`curate` pass to reshape it as real work accumulates. No domains yet, by design.
