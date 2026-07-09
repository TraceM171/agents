#!/bin/sh
# Opt-in gate: only act in projects that already have a knowledge/ directory. This keeps the
# plugin fully inert everywhere else, regardless of whether it's installed at user (global) or
# project scope — an unrelated repo never gets AGENTS.md injected or a knowledge/ tree created
# just because the plugin happens to be installed. Adopting the template is one `mkdir knowledge`.
if [ -z "$CLAUDE_PROJECT_DIR" ] || [ ! -d "$CLAUDE_PROJECT_DIR/knowledge" ]; then
    exit 0
fi

# Bootstrap the rest of the scaffold — no dependencies, so a plugin-only install never needs
# the manual mkdir/touch steps beyond that first knowledge/ directory.
mkdir -p "$CLAUDE_PROJECT_DIR/knowledge/.local"
[ -f "$CLAUDE_PROJECT_DIR/knowledge/_basic.md" ] || : > "$CLAUDE_PROJECT_DIR/knowledge/_basic.md"
[ -f "$CLAUDE_PROJECT_DIR/knowledge/.local/_basic.md" ] || : > "$CLAUDE_PROJECT_DIR/knowledge/.local/_basic.md"

# Prefer python3: it can safely inline AGENTS.md + the two _basic.md files as context
# (correct JSON string escaping for arbitrary markdown content is not worth hand-rolling in sh).
if command -v python3 >/dev/null 2>&1; then
    if python3 "$CLAUDE_PLUGIN_ROOT/hooks/session-start.py"; then
        exit 0
    fi
fi

# Fallback — no python3, or it errored: don't attempt to inline file content in shell.
# Point the model at the real files instead; it reads them itself with its own tools.
echo "Read $CLAUDE_PLUGIN_ROOT/AGENTS.md in full, then read knowledge/_basic.md and knowledge/.local/_basic.md (relative to the project root, if they exist) before doing anything else this session."
