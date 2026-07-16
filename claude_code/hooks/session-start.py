#!/usr/bin/env python3
import json, os

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.environ.get("CLAUDE_PROJECT_DIR")

try:
    with open(os.path.join(plugin_root, "AGENTS.md")) as f:
        agents_md = f.read()
except OSError:
    agents_md = ""

# AGENTS.md is a fixed-size governance doc that doesn't grow with project history — safe to
# inline directly. The three knowledge files are NOT inlined the same way: Claude Code silently
# truncates a large hook additionalContext payload down to a small preview (the same "output too
# large" treatment big tool results get) with no error surfaced anywhere — a growing status.md
# blows past that unnoticed, and the model never sees it while believing context was complete.
# A Read tool call isn't subject to this, so we point the model at the files and let it read them
# itself, rather than gambling on their combined size staying under an undocumented limit.
#
# AGENTS.md itself stays inlined, so it must stay well under the documented 10,000-character hard
# cap on hook additionalContext (code.claude.com/docs/en/hooks.md). Budget below leaves headroom
# for the read-instruction line appended below and for any other context. This check runs every
# session, so drift can't go unnoticed the way the knowledge-file truncation did.
#
# Raised 8000 -> 8500 in 0.1.14, deliberately: the Decision kind is a permanent sixth entry in the
# taxonomy and its quick-reminder line has to live here. 8000 was set with no measurement behind it;
# the only other thing in the payload is the ~150-char read-instruction line below, so the real
# worst case is ~8660 against the 10,000 cap — still ~1.3k of margin. Keep this in sync with
# AGENTS_MD_BUDGET in .githooks/pre-commit.
AGENTS_MD_BUDGET = 8500
context = [agents_md]
if len(agents_md) > AGENTS_MD_BUDGET:
    context.append(
        f"WARNING: AGENTS.md is {len(agents_md)} characters, over its {AGENTS_MD_BUDGET}-character "
        "safety budget. Hook additionalContext is hard-capped at 10,000 characters (undocumented "
        "past that: silent truncation, no error) — trim AGENTS.md before it gets cut off mid-file. "
        "Tell the user this needs attention."
    )
if project_dir:
    basic_path = os.path.join(project_dir, "knowledge", "_basic.md")
    local_basic_path = os.path.join(project_dir, "knowledge", ".local", "_basic.md")
    status_path = os.path.join(project_dir, "knowledge", "status.md")

    to_read = [
        os.path.relpath(path, project_dir)
        for path in (basic_path, local_basic_path, status_path)
        if os.path.isfile(path) and os.path.getsize(path) > 0
    ]
    if to_read:
        context.append(
            "Before doing anything else this session, read these files in full, in order: "
            + ", ".join(to_read) + "."
        )

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n\n---\n\n".join(context),
    }
}))
