#!/usr/bin/env python3
import json, os

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.environ.get("CLAUDE_PROJECT_DIR")

try:
    with open(os.path.join(plugin_root, "AGENTS.md")) as f:
        agents_md = f.read()
except OSError:
    agents_md = ""

# Inject the two _basic.md index files plus status.md directly (scaffold bootstrap already
# happened in the sh wrapper) — KNOWLEDGE_ORG.md rates all three "every read"/"first read of
# session" cadence, so inlining them skips three Read calls. If status.md has grown too large
# for this to be reasonable, that's a curate problem to fix at the source, not something to
# work around here by leaving it out.
context = [agents_md]
if project_dir:
    basic_path = os.path.join(project_dir, "knowledge", "_basic.md")
    local_basic_path = os.path.join(project_dir, "knowledge", ".local", "_basic.md")
    status_path = os.path.join(project_dir, "knowledge", "status.md")

    for label, path in (
        ("knowledge/_basic.md", basic_path),
        ("knowledge/.local/_basic.md", local_basic_path),
        ("knowledge/status.md", status_path),
    ):
        try:
            with open(path) as f:
                body = f.read().strip()
        except OSError:
            body = ""
        if body:
            context.append(f"<!-- {label} -->\n{body}")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n\n---\n\n".join(context),
    }
}))
