"""
notellm IPython Extension

Fork of claude-code-jupyter-staging (MIT License, Anthropic)
Provides %%cc magic for Claude Code integration in Jupyter notebooks.
"""

from pathlib import Path
import json

DEFAULT_PERMISSIONS = {
    "permissions": {
        "allow": [
            "Bash",
            "Glob",
            "Grep",
            "Read",
            "Edit",
            "Write",
            "WebSearch",
            "WebFetch"
        ]
    }
}


def _ensure_claude_settings():
    """Create .claude/settings.local.json if not present in cwd."""
    cwd = Path.cwd()
    claude_dir = cwd / ".claude"
    settings_file = claude_dir / "settings.local.json"

    if not settings_file.exists():
        claude_dir.mkdir(exist_ok=True)
        settings_file.write_text(json.dumps(DEFAULT_PERMISSIONS, indent=2))
        print(f"Created {settings_file.relative_to(cwd)}")
        return True
    return False


def load_ipython_extension(ipython):
    """Load the cc_jupyter extension."""
    # Show security warning first
    print("")
    print("\033[1;31m" + "=" * 80 + "\033[0m")
    print("\033[1;31mWARNING: Claude has permissions for Bash, Read, Write, Edit, WebSearch, WebFetch\033[0m")
    print("")
    print("  Claude can execute shell commands, read/write/edit files, and access the web.")
    print("  Only use in trusted environments.")
    print("")
    print("  Consider removing .claude/settings.local.json when done.")
    print("\033[1;31m" + "=" * 80 + "\033[0m")
    print("")

    created = _ensure_claude_settings()
    if created:
        print(f"Created .claude/settings.local.json")
        print("  (Permissions: Bash, Glob, Grep, Read, Edit, Write, WebSearch, WebFetch)")
        print("")

    from .cc_jupyter import load_ipython_extension as load_cc
    load_cc(ipython)


def unload_ipython_extension(ipython):
    """Unload the cc_jupyter extension."""
    try:
        from .cc_jupyter import unload_ipython_extension as unload_cc
        unload_cc(ipython)
    except (ImportError, AttributeError):
        pass
