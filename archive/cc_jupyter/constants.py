import importlib.util

EXECUTE_PYTHON_TOOL_NAME = "mcp__jupyter__create_python_cell"
PYGMENTS_AVAILABLE = importlib.util.find_spec("pygments") is not None

HELP_TEXT = """
🚀 Claude Code Magic loaded!
Features:
  • Full agentic Claude Code execution
  • Cell-based code approval workflow
  • Real-time message streaming
  • Session state preservation
  • Conversation continuity across cells

Usage:
  %cc <instructions>       # Continue with additional instructions (one-line)
  %%cc <instructions>      # Continue with additional instructions (multi-line)
  %cc_new (or %ccn)        # Start fresh conversation
  %cc --help               # Show available options and usage information

Context management:
  %cc --import <file>       # Add a file to be included in initial conversation messages
  %cc --add-dir <dir>       # Add a directory to Claude's accessible directories
  %cc --mcp-config <file>   # Set path to a .mcp.json file containing MCP server configurations
  %cc --cells-to-load <num> # The number of cells to load into a new conversation (default: all for first %cc, none for %cc_new)

Output:
  %cc --model <name>       # Model to use for Claude Code (default: sonnet)
  %cc --max-cells <num>    # Set the maximum number of cells CC can create per turn (default: 3)

Display:
  %cc --clean              # Replace prompt cells with Claude's code cells (tell us if you like this feature, maybe it should be the default)
  %cc --no-clean           # Turn off the above setting (default)

When to use each form:
  • Use %cc (single %) for:
    - Short, one-line instructions

  • Use %%cc (double %) for:
    - Multi-line instructions or detailed prompts

Notes:
- Restart the kernel to stop the Claude session
- Documentation: go/claude-code-jupyter
"""

QUEUED_EXECUTION_TEXT = """
⚠️ Not executing this prompt because you've queued multiple cell executions (e.g. Run All),
so re-running Claude might be unintentional. If you did mean to do this, please add the
flag `--allow-run-all` and try again.
"""

CLEANUP_PROMPTS_TEXT = """
🧹 Persistent preference set. For the rest of this session, cells with prompts will {maybe_not}
be cleaned up after executing.
"""
