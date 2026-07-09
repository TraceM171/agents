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
    branch_stats = f"{DIM}branch {RESET}{DIM}+{b_added} -{b_removed}{RESET}"
    git_str = f"{dot}●{RESET} {branch}{SEP}{branch_stats}"

# Lines added/removed this session (whole session, not knowledge-scoped)
cost = data.get("cost", {})
added, removed = cost.get("total_lines_added"), cost.get("total_lines_removed")
lines_str = None
if added is not None or removed is not None:
    lines_str = italic(f"{DIM}session {RESET}\033[1m+{added or 0} -{removed or 0}{RESET}")

# Knowledge-tree activity this session — knowledge/**.md files read vs edited, as % of the tree.
# Also scans for reflect-nudge signals: non-knowledge edits (code changed, not captured) and
# overall tool-call volume/session duration (investigation happened, e.g. an SSH debugging session
# with no file edits at all) — either is a proxy for "there's probably something worth reflecting".
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
    read_files, edited_files, non_kn_edited_files = set(), set(), set()
    tool_calls = 0
    reflected = False
    try:
        with open(transcript_path) as f:
            for line in f:
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
                    if name == "Skill" and inp.get("skill") == "reflect":
                        reflected = True
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if not fp:
                        continue
                    if fp.startswith(knowledge_root):
                        if name == "Read":
                            read_files.add(fp)
                        elif name in ("Edit", "Write", "NotebookEdit"):
                            edited_files.add(fp)
                    elif name in ("Edit", "Write", "NotebookEdit"):
                        non_kn_edited_files.add(fp)
    except OSError:
        return None
    return knowledge_dir, len(read_files), len(edited_files), total_files, len(non_kn_edited_files), tool_calls, reflected

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
    knowledge_dir, n_read, n_edit, total_files, n_non_kn_edit, tool_calls, reflected = kn
    read_pct = (n_read / total_files * 100) if total_files else 0
    edit_pct = (n_edit / total_files * 100) if total_files else 0
    read_part = italic(f"\033[1m{n_read}{RESET}{DIM} read ({RESET}\033[1m{read_pct:.0f}%{RESET}{DIM}){RESET}")
    edit_part = italic(f"\033[1m{n_edit}{RESET}{DIM} edited ({RESET}\033[1m{edit_pct:.0f}%{RESET}{DIM}){RESET}")
    kn_str = f"{DIM}knowledge:{RESET} " + SEP.join([read_part, edit_part])

    # Reflect nudge — code changed (>=3 non-knowledge files) or a long investigation
    # (>=25 tool calls over >=15min) happened, and reflect hasn't run yet this session.
    duration_min = (data.get("cost", {}).get("total_duration_ms") or 0) / 60000
    edits_trigger = n_non_kn_edit >= 3
    activity_trigger = tool_calls >= 25 and duration_min >= 15
    if not reflected and (edits_trigger or activity_trigger):
        reasons = "+".join(r for r, on in (("edits", edits_trigger), ("activity", activity_trigger)) if on)
        kn_str += SEP + italic(f"{Y}●{RESET} {DIM}reflect? ({reasons}){RESET}")

    cwd = data.get("cwd") or data.get("workspace", {}).get("current_dir")
    cur = curate_signal(cwd, knowledge_dir, total_files) if cwd else None
    if cur is not None:
        changed_count, curate_trigger = cur
        if curate_trigger:
            kn_str += f"{SEP}{Y}●{RESET} {DIM}curate? ({changed_count} files){RESET}"

git_line_parts = [p for p in [git_str, lines_str] if p]
status_parts = [ctx_str, model_str] + rl_parts

lines = []
if kn_str:
    lines.append(kn_str)
if git_line_parts:
    lines.append(SEP.join(git_line_parts))
lines.append(SEP.join(status_parts))
print("\n".join(lines))
