#!/usr/bin/env python3
import json, os, re, subprocess, sys, time

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
    model_str += f"\033[1m [{effort_obj['level']}]{RESET}"

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

rate = data.get("rate_limits", {})
rl_parts = [s for s in [fmt_reset(rate.get("five_hour", {})), fmt_reset(rate.get("seven_day", {}))] if s]

# Git branch — dot color reflects real state: clean (green), uncommitted (yellow), unpushed (cyan)
# Branch stats = uncommitted diff vs HEAD (staged + unstaged)
def git_status():
    cwd = data.get("cwd") or data.get("workspace", {}).get("current_dir")
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
        ahead = subprocess.run(
            ["git", "-C", cwd, "rev-list", "--count", "@{u}.."],
            capture_output=True, text=True, timeout=2,
        )
        unpushed = int(ahead.stdout.strip()) if ahead.returncode == 0 and ahead.stdout.strip().isdigit() else 0
        return name, ins, dele, unpushed
    except Exception:
        return None

git_info = git_status()
git_str = None
if git_info:
    branch, b_added, b_removed, unpushed = git_info
    dirty = bool(b_added or b_removed)
    dot = Y if dirty else C if unpushed else G
    branch_stats = f"{DIM}branch {RESET}\033[1m+{b_added} -{b_removed}{RESET}"
    git_str = f"{dot}●{RESET} \033[1m{branch}{RESET}{SEP}{branch_stats}"

# Lines added/removed this session (whole session, not knowledge-scoped). Computed from the
# transcript's per-edit patches rather than data["cost"] — the latter only tracks the current
# process and resets to 0 on session resume, even though the transcript (and its line diffs)
# carries over since resume appends to the same transcript file rather than starting a new one.
def session_line_diff():
    transcript_path = data.get("transcript_path")
    if not transcript_path:
        return None
    added = removed = 0
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
                for hunk in tur.get("structuredPatch") or []:
                    for l in hunk.get("lines") or []:
                        if l.startswith("+") and not l.startswith("+++"):
                            added += 1
                        elif l.startswith("-") and not l.startswith("---"):
                            removed += 1
    except OSError:
        return None
    return added, removed

diff = session_line_diff()
if diff is not None:
    added, removed = diff
else:
    cost = data.get("cost", {})
    added, removed = cost.get("total_lines_added"), cost.get("total_lines_removed")
lines_str = None
if added is not None or removed is not None:
    lines_str = italic(f"{DIM}session {RESET}\033[1m+{added or 0} -{removed or 0}{RESET}")

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
def knowledge_activity():
    transcript_path = data.get("transcript_path")
    project_dir = data.get("workspace", {}).get("project_dir") or data.get("cwd")
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
    # reflect's own writes (Skill call -> its Edits -> next user turn) all land *before* the
    # boundary is knowable. Find it first: the line of the first "user" entry after the LAST
    # Skill("reflect") call. Edits at or before it are reflect's own; edits after are "since
    # last reflect". No reflect this session leaves it at -1, so everything counts from the top.
    reflect_boundary = -1
    reflected = False
    awaiting_boundary = False
    for line_no, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        etype = entry.get("type")
        if etype == "user":
            if awaiting_boundary:
                reflect_boundary = line_no
                awaiting_boundary = False
            continue
        if etype != "assistant":
            continue
        for block in entry.get("message", {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                if (block.get("input") or {}).get("skill") == "reflect":
                    reflected = True
                    awaiting_boundary = True

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
                    if line_no > reflect_boundary:
                        edited_since_reflect.add(fp)
            elif name in ("Edit", "Write", "NotebookEdit"):
                non_kn_edited_files.add(fp)

    return (knowledge_dir, len(read_files), len(edited_files), total_files, len(non_kn_edited_files),
            tool_calls, reflected, len(edited_since_reflect))

# Curate nudge — how much of the knowledge tree has changed since the last curate pass.
# `knowledge/_curated.md` (reserved marker, see KNOWLEDGE_ORG.md) holds the date curate last
# ran; count distinct knowledge files touched by commits since then. No marker yet (never
# curated) falls back to total tree size, gated so a small fresh tree doesn't nag.
def curate_signal(cwd, knowledge_dir, total_files):
    marker_path = os.path.join(knowledge_dir, "_curated.md")
    since_date = None
    if os.path.isfile(marker_path):
        try:
            content = open(marker_path).read().strip()
        except OSError:
            content = ""
        if re.match(r"^\d{4}-\d{2}-\d{2}$", content):
            since_date = content
    if not since_date:
        return total_files, total_files >= 15
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "log", f"--since={since_date}", "--name-only", "--pretty=format:", "--", knowledge_dir],
            capture_output=True, text=True, timeout=2,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    changed = len({l for l in out.stdout.splitlines() if l.strip()})
    return changed, changed >= 10

kn = knowledge_activity()
kn_str = None
if kn is not None:
    knowledge_dir, n_read, n_edit, total_files, n_non_kn_edit, tool_calls, reflected, n_edit_since_reflect = kn
    read_pct = (n_read / total_files * 100) if total_files else 0
    edit_pct = (n_edit / total_files * 100) if total_files else 0
    read_part = italic(f"\033[1m{n_read}{RESET}{DIM} read ({RESET}\033[1m{read_pct:.0f}%{RESET}{DIM}){RESET}")
    edit_part = italic(f"\033[1m{n_edit}{RESET}{DIM} edited ({RESET}\033[1m{edit_pct:.0f}%{RESET}{DIM}){RESET}")
    kn_str = f"{DIM}knowledge:{RESET} " + SEP.join([read_part, edit_part])

    # Reflect nudge, two independent triggers:
    # 1. Nothing captured live at all — code changed (>=8 non-knowledge files) or a long
    #    investigation (>=45 tool calls over >=30min) happened, no knowledge file touched
    #    (n_edit == 0), and reflect hasn't run yet this session. Fires once per session — if
    #    reflect already ran, this scenario no longer applies.
    # 2. Live-capture pileup — more than 2 knowledge files edited since the last reflect pass
    #    (or since session start, if reflect hasn't run yet), excluding reflect's own edits.
    #    This is the duplication/kind-mixing risk zone (see KNOWLEDGE_ORG.md's "no duplication"
    #    and "recent-changes entries are pointers, not records") — it re-fires after reflect runs
    #    once enough new edits pile up again, unlike trigger 1.
    duration_min = (data.get("cost", {}).get("total_duration_ms") or 0) / 60000
    edits_trigger = n_non_kn_edit >= 8 and n_edit == 0
    activity_trigger = tool_calls >= 45 and duration_min >= 30 and n_edit == 0
    no_capture_trigger = not reflected and (edits_trigger or activity_trigger)
    dup_risk_trigger = n_edit_since_reflect > 2
    if no_capture_trigger or dup_risk_trigger:
        reasons = "+".join(r for r, on in (
            ("edits", edits_trigger and not reflected),
            ("activity", activity_trigger and not reflected),
            ("dup-risk", dup_risk_trigger),
        ) if on)
        kn_str += SEP + italic(f"{Y}●{RESET} \033[1mreflect?{RESET} {DIM}({reasons}){RESET}")

    cwd = data.get("cwd") or data.get("workspace", {}).get("current_dir")
    cur = curate_signal(cwd, knowledge_dir, total_files) if cwd else None
    if cur is not None:
        changed_count, curate_trigger = cur
        if curate_trigger:
            kn_str += f"{SEP}{Y}●{RESET} \033[1mcurate?{RESET} {DIM}({changed_count} files){RESET}"

git_line_parts = [p for p in [git_str, lines_str] if p]
status_parts = [ctx_str, model_str] + rl_parts

lines = []
if kn_str:
    lines.append(kn_str)
if git_line_parts:
    lines.append(SEP.join(git_line_parts))
lines.append(SEP.join(status_parts))
print("\n".join(lines))
