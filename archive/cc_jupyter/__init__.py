"""
Claude Code Jupyter Integration

This package provides comprehensive IPython and Jupyter integration for Claude Code
with multiple execution modes including local execution, MCP server integration,
and SDK-based usage.
"""

from __future__ import annotations

from .cell_watcher import CellWatcher
from .constants import HELP_TEXT, PYGMENTS_AVAILABLE
from .magics import ClaudeCodeMagics

__version__ = "0.1.0"

# Global configuration
DEFAULT_PORT = 0  # Use 0 to let OS assign an available port

__all__ = [
    "ClaudeCodeMagics",
    "DEFAULT_PORT",
    "PYGMENTS_AVAILABLE",
    "load_ipython_extension",
]


# IPython extension loading function
def load_ipython_extension(ipython: object) -> None:
    """Load the extension in IPython."""
    from IPython.core.interactiveshell import InteractiveShell

    if not isinstance(ipython, InteractiveShell):
        return

    cell_watcher = CellWatcher(ipython)
    magics = ClaudeCodeMagics(ipython, cell_watcher)
    # Register magic functions - line_cell_magic decorators handle both modes
    ipython.register_magics(magics)
    ipython.events.register("pre_run_cell", cell_watcher.pre_run_cell)
    ipython.events.register("post_run_cell", cell_watcher.post_run_cell)

    print(HELP_TEXT)
