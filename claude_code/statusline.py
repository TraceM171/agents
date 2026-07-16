#!/usr/bin/env python3
import hashlib, html, json, os, re, subprocess, sys, tempfile, time

try:
    data = json.load(sys.stdin)
except Exception:
    print("claude")
    sys.exit(0)

G, Y, R, C, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[0m"
DIM = "\033[2m"
ITALIC = "\033[3m"
SEP = f"{DIM} · {RESET}"

# Marks a segment as session-scoped — italic, meaning "resets/changes on a new Claude session"
# (context %, session line-diff, knowledge read/edit counts, reflect nudge) as opposed to
# persistent environment/repo state (git branch, model choice, rate limits, curate nudge).
def italic(s):
    return ITALIC + s.replace(RESET, RESET + ITALIC) + RESET

def remaining_dot_color(remaining_pct):
    return G if remaining_pct > 50 else Y if remaining_pct > 20 else R

def used_dot_color(used_pct):
    return G if used_pct < 50 else Y if used_pct < 80 else R

# Context dot — green < 50%, yellow < 80%, red >= 80%
ctx = data.get("context_window", {})
pct = ctx.get("used_percentage") or 0
ctx_str = italic(f"{used_dot_color(pct)}●{RESET}\033[1m {pct:.0f}%{RESET}")

# Friendly model name from statusline JSON's display_name field
model_obj = data.get("model", {})
if isinstance(model_obj, dict):
    friendly = model_obj.get("display_name") or model_obj.get("id", "")
else:
    friendly = str(model_obj)

model_str = f"\033[1m{friendly}{RESET}"

max_ctx = ctx.get("context_window_size")
if max_ctx:
    size_str = f"{max_ctx // 1_000_000}M" if max_ctx >= 1_000_000 else f"{max_ctx // 1000}k"
    model_str += f"{DIM} ({size_str}){RESET}"

effort_obj = data.get("effort")
if isinstance(effort_obj, dict) and effort_obj.get("level"):
    model_str += f"{DIM} [{RESET}\033[1m{effort_obj['level']}{RESET}{DIM}]{RESET}"

def fmt_reset(rl):
    resets_at = rl.get("resets_at")
    used = rl.get("used_percentage")
    if resets_at is None or used is None:
        return None
    secs = max(0, int(resets_at - time.time()))
    d, rem = divmod(secs, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        countdown = f"{d}d {h}h"
    elif h:
        countdown = f"{h}h {m:02d}m"
    else:
        countdown = f"{m}m"
    c = used_dot_color(used)
    return f"{c}●{RESET}\033[1m {used:.0f}%{RESET} ({countdown})"

# Session cost — data["cost"]["total_cost_usd"], same object session line-diff/duration read from.
cost_usd = data.get("cost", {}).get("total_cost_usd")
cost_str = italic(f"\033[1m${cost_usd:.2f}{RESET}") if cost_usd is not None else None

rate = data.get("rate_limits", {})
rl_parts = [s for s in [fmt_reset(rate.get("five_hour", {})), fmt_reset(rate.get("seven_day", {}))] if s]

# OSC8 hyperlink — wraps text so terminals that support it (iTerm2, kitty, wezterm, VSCode)
# can click through to a generated local page. Terminals without support just show the text,
# no link. Only count segments (read / edited / branch / session stats) get wrapped — labels
# and names stay plain so it's clear what's clickable. All four link into the same combined
# page (one write_page call per render), each to its own section via #anchor.
def hyperlink(text, path):
    return f"\033]8;;file://{path}\033\\{text}\033]8;;\033\\"

PAGE_SHELL = """<!doctype html>
<html><head><meta charset="utf-8"><title>{title} — this session</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 14px/1.5 -apple-system, system-ui, sans-serif; max-width: min(1100px, 96vw);
          margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; background: #fff; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #e4e4e4; background: #1e1e1e; }}
    .path {{ background: #2a2a2a; }}
    h2 {{ border-bottom-color: #3a3a3a; }}
    .toolbar button {{ background: #2a2a2a; border-color: #3a3a3a; color: #e4e4e4; }}
  }}
  h1 {{ font-size: 1.1rem; margin-bottom: 0.25rem; }}
  .sub {{ color: #888; font-size: 0.85rem; margin-bottom: 1rem; }}
  .toolbar {{ margin-bottom: 1rem; }}
  .toolbar button {{ padding: 0.35rem 0.8rem; border-radius: 6px; border: 1px solid #ddd;
                      background: #f2f2f2; font-size: 0.85rem; cursor: pointer; }}
  h2 {{ font-size: 0.95rem; border-bottom: 1px solid #ddd; padding-bottom: 0.3rem; margin-top: 1.5rem; }}
  ul {{ list-style: none; padding: 0; margin: 0.5rem 0 1.5rem; }}
  li {{ padding: 0.2rem 0; }}
  li.plain {{ display: flex; justify-content: space-between; gap: 1rem; }}
  .path {{ background: #f2f2f2; padding: 0.1rem 0.4rem; border-radius: 4px;
           font-family: ui-monospace, monospace; font-size: 0.85rem; }}
  .stat {{ font-family: ui-monospace, monospace; font-size: 0.85rem; color: #888; white-space: nowrap; }}
  .dirty-badge {{ font-size: 0.75rem; font-weight: 600; color: #9a6700; background: #fff8c5;
                   padding: 0.05rem 0.45rem; border-radius: 4px; white-space: nowrap; }}
  .empty {{ color: #888; font-style: italic; }}
  summary {{ display: flex; justify-content: space-between; gap: 1rem; cursor: pointer; }}
  summary::marker {{ color: #888; }}
  pre.diff {{ margin: 0.4rem 0 0.6rem; padding: 0.6rem 0.8rem; overflow-x: auto;
              background: #f7f7f7; border-radius: 6px; font-family: ui-monospace, monospace;
              font-size: 0.8rem; line-height: 1.4; }}
  pre.diff span {{ display: block; white-space: pre; }}
  .d-add {{ color: #1a7f37; background: #e6ffec; }}
  .d-del {{ color: #cf222e; background: #ffebe9; }}
  .d-hunk {{ color: #8250df; }}
  .d-ctx {{ color: #57606a; }}
  @media (prefers-color-scheme: dark) {{
    pre.diff {{ background: #252525; }}
    .d-add {{ color: #7ee2a8; background: #0f3f22; }}
    .d-del {{ color: #ff9492; background: #4a1210; }}
    .d-hunk {{ color: #c297ff; }}
    .d-ctx {{ color: #9198a1; }}
    .dirty-badge {{ color: #f2cc60; background: #3d3410; }}
  }}
</style></head>
<body>
<h1>{title}</h1>
<div class="sub">session {session}</div>
{body}
<script>
function toggleAll() {{
  var btn = document.getElementById('toggle-all');
  var opening = btn.textContent === 'Expand all';
  document.querySelectorAll('details').forEach(function(d) {{ d.open = opening; }});
  btn.textContent = opening ? 'Collapse all' : 'Expand all';
}}
</script>
</body></html>
"""

def _diff_html(diff_text):
    out = []
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            cls = "d-hunk"
        elif line.startswith("+") and not line.startswith("+++"):
            cls = "d-add"
        elif line.startswith("-") and not line.startswith("---"):
            cls = "d-del"
        else:
            cls = "d-ctx"
        out.append(f'<span class="{cls}">{html.escape(line)}</span>')
    return "".join(out)

def _truncate_diff(text, max_lines=300):
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines] + [f"… truncated ({len(lines) - max_lines} more lines)"])

def _list_html(rows):
    if not rows:
        return '<p class="empty">none</p>'
    lis = []
    for path, stat, diff_text in rows:
        if stat == "dirty":  # sentinel: edited-since-last-reflect indicator, not a +/- diffstat
            stat_html = '<span class="dirty-badge">dirty</span>'
        else:
            stat_html = f'<span class="stat">{stat}</span>' if stat else ""
        if diff_text:
            lis.append(
                f'<li><details><summary><span class="path">{path}</span>{stat_html}</summary>'
                f'<pre class="diff">{_diff_html(diff_text)}</pre></details></li>'
            )
        else:
            lis.append(f'<li class="plain"><span class="path">{path}</span>{stat_html}</li>')
    return "<ul>" + "".join(lis) + "</ul>"

# One page per category (knowledge / branch / session) — each clickable count links to its own
# file. "Expand all" toolbar only appears when the page actually has foldable diffs (branch,
# session); the knowledge page has none, so it's omitted there automatically.
def write_page(name, session_key, title, sections):
    if not sections:
        return None
    path = os.path.join(tempfile.gettempdir(), f"claude-statusline-{name}-{session_key}.html")
    has_diffs = any(diff_text for _, _, rows in sections for _, _, diff_text in rows)
    toolbar = '<div class="toolbar"><button id="toggle-all" onclick="toggleAll()">Expand all</button></div>' if has_diffs else ""
    body = toolbar + "".join(
        f'<h2 id="{sec_id}">{heading} ({len(rows)})</h2>\n{_list_html(rows)}\n'
        for heading, sec_id, rows in sections
    )
    page_html = PAGE_SHELL.format(title=title, session=session_key, body=body)
    try:
        with open(path, "w") as f:
            f.write(page_html)
    except OSError:
        return None
    return path

transcript_path = data.get("transcript_path")
session_key = hashlib.sha1(transcript_path.encode()).hexdigest()[:12] if transcript_path else None
project_dir = data.get("workspace", {}).get("project_dir") or data.get("cwd")
cwd = data.get("cwd") or data.get("workspace", {}).get("current_dir")

# Git branch — dot color reflects real state: clean (green), uncommitted (yellow), unpushed (cyan)
# Branch stats = uncommitted diff vs HEAD (staged + unstaged); file_stats is the same diff broken
# down per file (git diff --numstat), used for the branch stats' clickthrough section.
def git_status():
    if not cwd:
        return None
    try:
        branch = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=2,
        )
        name = branch.stdout.strip()
        if branch.returncode != 0 or not name:
            return None
        diff = subprocess.run(
            ["git", "-C", cwd, "diff", "--shortstat", "HEAD"],
            capture_output=True, text=True, timeout=2,
        )
        out = diff.stdout.strip()
        ins = int(m.group(1)) if (m := re.search(r"(\d+) insertion", out)) else 0
        dele = int(m.group(1)) if (m := re.search(r"(\d+) deletion", out)) else 0
        numstat = subprocess.run(
            ["git", "-C", cwd, "diff", "--numstat", "HEAD"],
            capture_output=True, text=True, timeout=2,
        )
        file_stats = []
        for line in numstat.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            a, d, path = parts
            if a == "-" or d == "-":  # binary file, numstat can't count lines
                continue
            file_stats.append((path, int(a), int(d)))
        ahead = subprocess.run(
            ["git", "-C", cwd, "rev-list", "--count", "@{u}.."],
            capture_output=True, text=True, timeout=2,
        )
        unpushed = int(ahead.stdout.strip()) if ahead.returncode == 0 and ahead.stdout.strip().isdigit() else 0
        return name, ins, dele, unpushed, file_stats
    except Exception:
        return None

# Full unified diff (git diff HEAD), split per file — feeds the branch stats' foldable diff view.
# Only hunk lines are kept (index/---/+++ header lines dropped); binary files are absent from
# `paths` already (filtered out by git_status's numstat pass).
def git_diff_patches(paths):
    if not paths or not cwd:
        return {}
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "diff", "HEAD", "--"] + paths,
            capture_output=True, text=True, timeout=3,
        )
    except Exception:
        return {}
    if out.returncode != 0:
        return {}
    patches, current_path, current_lines, in_hunk = {}, None, [], False
    for line in out.stdout.splitlines():
        m = re.match(r"^diff --git a/(?:.*) b/(.*)$", line)
        if m:
            if current_path is not None:
                patches[current_path] = "\n".join(current_lines)
            current_path, current_lines, in_hunk = m.group(1), [], False
            continue
        if line.startswith("@@"):
            in_hunk = True
        if in_hunk:
            current_lines.append(line)
    if current_path is not None:
        patches[current_path] = "\n".join(current_lines)
    return patches

# Lines added/removed this session (whole session, not knowledge-scoped). Computed from the
# transcript's per-edit patches rather than data["cost"] — the latter only tracks the current
# process and resets to 0 on session resume, even though the transcript (and its line diffs)
# carries over since resume appends to the same transcript file rather than starting a new one.
# Also tallies a per-file breakdown (toolUseResult.filePath), and the actual hunk text (per file,
# in edit order — multiple edits to the same file just append, since it's showing what happened
# rather than a single net diff), for the session stats' clickthrough section.
def session_line_diff():
    if not transcript_path:
        return None
    added = removed = 0
    per_file, per_file_diff = {}, {}
    try:
        with open(transcript_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                tur = entry.get("toolUseResult")
                if not isinstance(tur, dict):
                    continue
                fp = tur.get("filePath")
                a = d = 0
                chunks = []
                for hunk in tur.get("structuredPatch") or []:
                    hlines = hunk.get("lines") or []
                    for l in hlines:
                        if l.startswith("+") and not l.startswith("+++"):
                            a += 1
                        elif l.startswith("-") and not l.startswith("---"):
                            d += 1
                    header = f"@@ -{hunk.get('oldStart')},{hunk.get('oldLines')} +{hunk.get('newStart')},{hunk.get('newLines')} @@"
                    chunks.append("\n".join([header] + hlines))
                added += a
                removed += d
                if fp and (a or d):
                    pa, pd = per_file.get(fp, (0, 0))
                    per_file[fp] = (pa + a, pd + d)
                    existing = per_file_diff.get(fp, "")
                    per_file_diff[fp] = (existing + "\n" if existing else "") + "\n".join(chunks)
    except OSError:
        return None
    return added, removed, per_file, per_file_diff

# Knowledge-tree activity this session — knowledge/**.md files read vs edited, as % of the tree.
# Also scans for reflect-nudge signals: non-knowledge edits (code changed, not captured), overall
# tool-call volume/session duration (investigation happened, e.g. an SSH debugging session with no
# file edits at all), and live-capture edits piling up since the last reflect pass — each is a proxy
# for "there's probably something worth reflecting".
#
# `reflect_boundary` marks the line where the last reflect pass handed control back to the user (the
# first "user" transcript entry after a Skill("reflect") call) — edits after that line are "since last
# reflect"; edits at or before it are reflect's own writes and don't count. No reflect this session
# leaves the boundary at -1, so everything since session start counts (matches AGENTS.md's "capture
# as you go" framing: first reflect, or session start, whichever is the relevant zero point).
#
# `curate_windows` is the same idea applied to curate: a list of (start, end) line ranges, one per
# curate invocation this session, using identical open/close detection. A curate pass makes deliberate,
# already-reviewed cleanup edits — not live capture at risk of duplication — so edits falling inside
# any window are excluded from `edited_since_reflect` the same way reflect's own edits are, regardless
# of where the window falls relative to `reflect_boundary`.
def knowledge_activity():
    if not transcript_path or not project_dir:
        return None
    knowledge_dir = os.path.join(project_dir, "knowledge")
    if not os.path.isdir(knowledge_dir):
        return None
    knowledge_root = knowledge_dir + os.sep
    total_files = sum(len(files) for _, _, files in os.walk(knowledge_dir))
    try:
        with open(transcript_path) as f:
            lines = f.readlines()
    except OSError:
        return None

    # Pass 1: locate reflect_boundary — a forward scan can't know it while walking edits, since
    # reflect's own writes (invocation -> its Edits -> next real user turn) all land *before* the
    # boundary is knowable. Find it first: the line of the first real user turn after the LAST
    # reflect invocation. Edits at or before it are reflect's own; edits after are "since last
    # reflect". No reflect this session leaves it at -1, so everything counts from the top.
    #
    # Reflect gets invoked two different ways, and both have to be caught:
    #  - the assistant calls the Skill tool (input.skill may be namespaced, e.g.
    #    "arwyl-lite:reflect" for marketplace installs — match on the tail after the last ":").
    #  - the user directly types the slash command (`/reflect` or `/arwyl-lite:reflect`). This
    #    does NOT show up as an assistant Skill tool_use at all — Claude Code records it as a
    #    "user"-type entry whose content is a literal string containing
    #    "<command-name>/arwyl-lite:reflect</command-name>".
    #
    # "First user entry after the invocation" is NOT "first real chat turn", though — tool_result
    # blocks come back as type:"user" too (every tool call reflect itself makes, e.g. its own
    # Edit/Write calls, gets an immediate type:"user" tool_result entry), and slash-command
    # invocation is actually TWO synthetic entries: the "<command-name>" marker (real, matched
    # above) immediately followed by a second type:"user" entry containing the expanded skill
    # prompt text, flagged `isMeta: true`. Treating either of those as "the next user turn" closed
    # the boundary one line after the invocation — before reflect had done any of its actual work
    # — so its own edits counted as "since last reflect" (confirmed against sanctum's real
    # transcript: 8/8 edited-since-reflect immediately after a reflect run). Skip both: only a
    # user entry that's neither tool-result-only nor isMeta really closes the boundary. If nothing
    # like that appears before EOF (reflect was the literal last thing that ran), the boundary
    # closes at end-of-file — none of reflect's edits should count as "since reflect" either way.
    reflect_cmd_re = re.compile(r"<command-name>/(?:[^<:]+:)?reflect</command-name>")
    curate_cmd_re = re.compile(r"<command-name>/(?:[^<:]+:)?curate</command-name>")
    reflect_boundary = -1
    reflected = False
    awaiting_boundary = False
    curate_windows = []
    awaiting_curate_boundary = False
    curate_window_start = None
    for line_no, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        etype = entry.get("type")
        if etype == "user":
            content = entry.get("message", {}).get("content")
            is_meta = bool(entry.get("isMeta"))
            is_tool_result_only = isinstance(content, list) and content and all(
                isinstance(b, dict) and b.get("type") == "tool_result" for b in content
            )
            is_reflect_command = isinstance(content, str) and bool(reflect_cmd_re.search(content))
            is_curate_command = isinstance(content, str) and bool(curate_cmd_re.search(content))
            if awaiting_boundary and not is_tool_result_only and not is_meta and not is_reflect_command:
                reflect_boundary = line_no
                awaiting_boundary = False
            if awaiting_curate_boundary and not is_tool_result_only and not is_meta and not is_curate_command:
                curate_windows.append((curate_window_start, line_no))
                awaiting_curate_boundary = False
            if is_reflect_command:
                reflected = True
                awaiting_boundary = True
            if is_curate_command:
                curate_window_start = line_no
                awaiting_curate_boundary = True
            continue
        if etype != "assistant":
            continue
        for block in entry.get("message", {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                skill_name = (block.get("input") or {}).get("skill") or ""
                tail = skill_name.rsplit(":", 1)[-1]
                if tail == "reflect":
                    reflected = True
                    awaiting_boundary = True
                elif tail == "curate":
                    curate_window_start = line_no
                    awaiting_curate_boundary = True
    if awaiting_boundary:
        reflect_boundary = len(lines)
    if awaiting_curate_boundary:
        curate_windows.append((curate_window_start, len(lines)))

    # Pass 2: tally reads/edits against the now-known boundary.
    read_files, edited_files, non_kn_edited_files = set(), set(), set()
    edited_since_reflect = set()
    tool_calls = 0
    for line_no, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if entry.get("type") != "assistant":
            continue
        for block in entry.get("message", {}).get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            tool_calls += 1
            name = block.get("name")
            inp = block.get("input") or {}
            fp = inp.get("file_path") or inp.get("notebook_path")
            if not fp:
                continue
            if fp.startswith(knowledge_root):
                if name == "Read":
                    read_files.add(fp)
                elif name in ("Edit", "Write", "NotebookEdit"):
                    edited_files.add(fp)
                    in_curate_window = any(s <= line_no <= e for s, e in curate_windows)
                    if line_no > reflect_boundary and not in_curate_window:
                        edited_since_reflect.add(fp)
            elif name in ("Edit", "Write", "NotebookEdit"):
                non_kn_edited_files.add(fp)

    # A file touched mid-session can be renamed/merged/deleted later in the same session (e.g.
    # a curate restructuring pass) — its path stays in these sets but drops out of total_files
    # (a fresh disk count at render time), which pushed read/edit % over 100. Drop paths that no
    # longer exist so the numerator and denominator describe the same tree snapshot.
    read_files = {p for p in read_files if os.path.isfile(p)}
    edited_files = {p for p in edited_files if os.path.isfile(p)}
    edited_since_reflect &= edited_files

    return (knowledge_dir, len(read_files), len(edited_files), total_files, len(non_kn_edited_files),
            tool_calls, reflected, len(edited_since_reflect), sorted(read_files), sorted(edited_files),
            edited_since_reflect)

# Curate nudge — how much of the knowledge tree has changed since the last curate pass.
# `knowledge/_curated.md` (reserved marker, see KNOWLEDGE_ORG.md) holds the UTC timestamp curate
# last ran; count distinct knowledge files touched by commits since then. No marker yet (never
# curated) falls back to total tree size, gated so a small fresh tree doesn't nag.
#
# A bare date (`YYYY-MM-DD`) marker is day-granular: `git log --since=<date>` is midnight-inclusive,
# so it sweeps in every commit from that whole calendar day — including ones made *before* curate
# ran that day, and curate's own reviewed-but-not-yet-committed work landing moments after. That
# double-counted a day's ordinary work as post-curate drift whenever curate ran anywhere but first
# thing in the morning (confirmed against sanctum's 2026-07-15 session logs: curate ran last, at
# 19:49 UTC, after reviewing that day's 26-file storage/backup rewrite and finding nothing to fix —
# but the bare-date marker still made the next session's --since=2026-07-15 catch all 26 files,
# including ones committed hours before curate even started). A full timestamp fixes the common
# case; it can't fully close a several-second race if a commit lands after curate's marker write
# but before the process that authored it exits — not worth chasing further.
def curate_signal(knowledge_dir, total_files):
    marker_path = os.path.join(knowledge_dir, "_curated.md")
    since_ts = None
    if os.path.isfile(marker_path):
        try:
            content = open(marker_path).read().strip()
        except OSError:
            content = ""
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", content):
            since_ts = content
    if not since_ts:
        return total_files, total_files >= 15
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "log", f"--since={since_ts}", "--name-only", "--pretty=format:", "--", knowledge_dir],
            capture_output=True, text=True, timeout=2,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    changed = len({l for l in out.stdout.splitlines() if l.strip()})
    return changed, changed >= 10

git_info = git_status()
diff = session_line_diff()
kn = knowledge_activity()

# Git branch line
git_str = None
if git_info:
    branch, b_added, b_removed, unpushed, branch_file_stats = git_info
    dirty = bool(b_added or b_removed)
    dot = Y if dirty else C if unpushed else G
    stat_text = f"\033[1m+{b_added} -{b_removed}{RESET}"
    if dirty and session_key and branch_file_stats:
        patches = git_diff_patches([p for p, _, _ in branch_file_stats])
        branch_rows = [
            (path, f"+{a} -{d}", _truncate_diff(patches[path]) if patches.get(path) else None)
            for path, a, d in branch_file_stats
        ]
        page_path = write_page("branch", session_key, "Branch changes", [("Changed files", "branch", branch_rows)])
        if page_path:
            stat_text = hyperlink(stat_text, page_path + "#branch")
    branch_stats = f"{DIM}branch {RESET}{stat_text}"
    git_str = f"{dot}●{RESET} \033[1m{branch}{RESET}{SEP}{branch_stats}"

# Session line-diff line
per_file, per_file_diff = {}, {}
if diff is not None:
    added, removed, per_file, per_file_diff = diff
else:
    cost = data.get("cost", {})
    added, removed = cost.get("total_lines_added"), cost.get("total_lines_removed")
lines_str = None
if added is not None or removed is not None:
    session_stat_text = f"\033[1m+{added or 0} -{removed or 0}{RESET}"
    if (added or removed) and session_key and per_file and project_dir:
        session_rows = [
            (os.path.relpath(p, project_dir), f"+{a} -{d}", _truncate_diff(per_file_diff[p]) if per_file_diff.get(p) else None)
            for p, (a, d) in sorted(per_file.items())
        ]
        page_path = write_page("session", session_key, "Session changes", [("Changed files", "session", session_rows)])
        if page_path:
            session_stat_text = hyperlink(session_stat_text, page_path + "#session")
    lines_str = italic(f"{DIM}session {RESET}{session_stat_text}")

# Knowledge line — always rendered when a knowledge/ dir exists, even at 0/0/0 (that's a
# legitimate reading: nothing touched yet this session).
kn_str = None
if kn is not None:
    knowledge_dir, n_read, n_edit, total_files, n_non_kn_edit, tool_calls, reflected, n_edit_since_reflect, read_files_list, edited_files_list, edited_since_reflect = kn

    # Reflect nudge triggers — see git history / KNOWLEDGE_ORG.md for the rationale:
    # 1. no_capture_trigger — code changed (>=8 non-knowledge files) or a long investigation
    #    (>=45 tool calls over >=30min) happened, no knowledge file touched (n_edit == 0), and
    #    reflect hasn't run yet this session.
    # 2. dup_risk_trigger — more than 2 knowledge files edited since the last reflect pass (or
    #    since session start, if reflect hasn't run yet), excluding reflect's and curate's own edits.
    duration_min = (data.get("cost", {}).get("total_duration_ms") or 0) / 60000
    edits_trigger = n_non_kn_edit >= 8 and n_edit == 0
    activity_trigger = tool_calls >= 45 and duration_min >= 30 and n_edit == 0
    no_capture_trigger = not reflected and (edits_trigger or activity_trigger)
    dup_risk_trigger = n_edit_since_reflect > 2
    cur = curate_signal(knowledge_dir, total_files) if cwd else None
    curate_trigger = bool(cur and cur[1])

    read_pct = (n_read / total_files * 100) if total_files else 0
    edit_pct = (n_edit / total_files * 100) if total_files else 0
    read_num = f"\033[1m{n_read}{RESET}"
    edit_num = f"\033[1m{n_edit}{RESET}"
    if session_key:
        rows_read = [(os.path.relpath(p, knowledge_dir), None, None) for p in read_files_list]
        rows_edit = [
            (os.path.relpath(p, knowledge_dir), "dirty" if p in edited_since_reflect else None, None)
            for p in edited_files_list
        ]
        page_path = write_page(
            "knowledge", session_key, "Knowledge activity",
            [("Read", "read", rows_read), ("Edited", "edited", rows_edit)],
        )
        if page_path:
            # a zero count has nothing to click through to — leave those plain, not linked
            if n_read:
                read_num = hyperlink(read_num, page_path + "#read")
            if n_edit:
                edit_num = hyperlink(edit_num, page_path + "#edited")
    read_text = f"{read_num}{DIM} read ({RESET}\033[1m{read_pct:.0f}%{RESET}{DIM}){RESET}"
    edit_text = f"{edit_num}{DIM} edited ({RESET}\033[1m{edit_pct:.0f}%{RESET}{DIM}){RESET}"
    read_part = italic(read_text)
    edit_part = italic(edit_text)
    kn_str = f"{DIM}knowledge:{RESET} " + SEP.join([read_part, edit_part])

    # Reflect nudge — no baseline stat, shown only when a trigger actually fires.
    if no_capture_trigger or dup_risk_trigger:
        reasons = "+".join(r for r, on in (
            ("edits", edits_trigger and not reflected),
            ("activity", activity_trigger and not reflected),
            ("dirtiness", dup_risk_trigger),
        ) if on)
        reflect_text = f"{Y}●{RESET} \033[1mreflect?{RESET} {DIM}({reasons}){RESET}"
        kn_str += SEP + italic(reflect_text)

    # Curate nudge — same shape, no baseline stat. Not wrapped in italic() — curate is persistent
    # repo state (survives across sessions), not session-scoped, per italic()'s docstring.
    if curate_trigger:
        kn_str += f"{SEP}{Y}●{RESET} \033[1mcurate?{RESET} {DIM}(dirtiness){RESET}"

git_line_parts = [p for p in [git_str, lines_str] if p]
status_parts = [ctx_str, model_str] + ([cost_str] if cost_str else []) + rl_parts

lines = []
if kn_str:
    lines.append(kn_str)
if git_line_parts:
    lines.append(SEP.join(git_line_parts))
lines.append(SEP.join(status_parts))
print("\n".join(lines))
