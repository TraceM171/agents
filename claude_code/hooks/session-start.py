#!/usr/bin/env python3
import json, os

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.environ.get("CLAUDE_PROJECT_DIR")

try:
    with open(os.path.join(plugin_root, "AGENTS.md")) as f:
        agents_md = f.read()
except OSError:
    agents_md = ""

# Inject the two _basic.md index files directly (scaffold bootstrap already happened in the
# sh wrapper) — AGENTS.md mandates reading them every session, and they're meant to stay small
# (index kind, not content), so inlining them skips two Read calls.
context = [agents_md]
if project_dir:
    basic_path = os.path.join(project_dir, "knowledge", "_basic.md")
    local_basic_path = os.path.join(project_dir, "knowledge", ".local", "_basic.md")

    for label, path in (("knowledge/_basic.md", basic_path), ("knowledge/.local/_basic.md", local_basic_path)):
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
