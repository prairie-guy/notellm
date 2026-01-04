"""
Jupyter notebook integration for Claude Code.
Handles cell creation, code display, and notebook-specific functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from IPython import get_ipython  # type: ignore[attr-defined]

from .constants import PYGMENTS_AVAILABLE

if TYPE_CHECKING:
    from .magics import ClaudeCodeMagics


def create_approval_cell(
    parent: ClaudeCodeMagics,
    code: str,
    request_id: str,
    should_cleanup_prompts: bool,
    tool_use_id: str | None = None,
) -> None:
    """Create a cell for user approval of code execution."""
    marker_id = tool_use_id if tool_use_id else request_id
    # Add a marker comment at the beginning of the code if tool_use_id is provided
    marker = f"# Claude cell [{marker_id}]"
    marked_code = f"{marker}\n{code}"

    # Store code and request ID in IPython namespace for access
    if parent.shell is not None:
        # Store the main request ID
        parent.shell.user_ns["_claude_request_id"] = request_id

        # Initialize cell queue if it doesn't exist
        if "_claude_cell_queue" not in parent.shell.user_ns:
            parent.shell.user_ns["_claude_cell_queue"] = []

        # Add to queue with metadata
        cell_info: dict[str, Any] = {
            "code": marked_code,  # Store the marked version
            "original_code": code,  # Store original for reporting
            "tool_use_id": tool_use_id,
            "request_id": request_id,
            "marker_id": marker_id,
            "marker": marker,
            "executed": False,
        }
        parent.shell.user_ns["_claude_cell_queue"].append(cell_info)

    queue_position = (
        len(parent.shell.user_ns["_claude_cell_queue"]) if parent.shell else 0
    )

    # Display formatted output
    print("\n" + "=" * 60, flush=True)
    print(
        "🤖 Claude wants to execute code",
        flush=True,
    )
    print("-" * 60, flush=True)

    if parent._config_manager.is_current_execution_verbose:
        if PYGMENTS_AVAILABLE:
            # Syntax highlighted code
            from pygments import highlight
            from pygments.formatters import TerminalFormatter
            from pygments.lexers import PythonLexer

            print(
                highlight(marked_code, PythonLexer(), TerminalFormatter()), flush=True
            )
        else:
            print(marked_code, flush=True)

        print("-" * 60, flush=True)

    if queue_position == 1:
        # Store the code to be prepopulated after the async operation completes
        if parent.shell is not None:
            parent.shell.user_ns["_claude_pending_input"] = marked_code

        if is_in_jupyter_notebook():
            cell_location = "above" if should_cleanup_prompts else "below"
            print(f"📋 To approve: Run the cell {cell_location}", flush=True)
        else:
            print("📋 Press Enter to execute the code (or edit it first)", flush=True)
    else:
        print(
            "⏳ Queued: Cell will appear automatically after previous cell is executed",
            flush=True,
        )

    print("➡️ To continue Claude agentically afterward: Run %cc", flush=True)
    print("=" * 60 + "\n", flush=True)


def adjust_cell_queue_markers(parent: ClaudeCodeMagics) -> None:
    """Supplement markers for cells in queue now that we have more complete information."""
    if parent.shell is None:
        return

    cell_queue = parent.shell.user_ns.get("_claude_cell_queue", [])
    if not cell_queue:
        return

    queue_length = len(cell_queue)
    for i, cell_info in enumerate(cell_queue):
        original_code = cell_info["original_code"]
        marker_id = cell_info["marker_id"]

        generated_cell_message = (
            f"# ║                        CLAUDE GENERATED CELL [id: {marker_id}]"
        )
        if len(generated_cell_message) < 80:
            generated_cell_message += " " * (79 - len(generated_cell_message)) + "║"
        queue_position_message = ""
        if queue_length > 1:
            queue_position_message = (
                f"# ║                                 CELL {i + 1} OF {queue_length}"
            )
            if len(queue_position_message) < 80:
                queue_position_message = (
                    f"\n{queue_position_message}"
                    + " " * (79 - len(queue_position_message))
                    + "║"
                )

        marker = f"""\
# ╔════════════════════════════════════════════════════════════════════════════╗
{generated_cell_message}{queue_position_message}
# ╚════════════════════════════════════════════════════════════════════════════╝
"""
        marked_code = f"{marker}\n{original_code}"
        cell_info["code"] = marked_code
        cell_info["marker"] = marker

        if i == 0:
            parent.shell.user_ns["_claude_pending_input"] = marked_code


def process_cell_queue(parent: ClaudeCodeMagics) -> None:
    """Process the cell queue after a successful cell execution."""
    if parent.shell is None:
        return

    cell_queue = parent.shell.user_ns.get("_claude_cell_queue", [])
    if not cell_queue:
        return

    # Find the next unexecuted cell
    next_cell_index = None
    for i, cell_info in enumerate(cell_queue):
        if not cell_info["executed"]:
            next_cell_index = i
            # Set this as the next input (use marked code)
            parent.shell.set_next_input(cell_info.get("code", ""))
            break

    if next_cell_index is not None:
        # Only show "Next cell ready" if there are more cells after this one
        remaining = sum(
            1 for cell in cell_queue[next_cell_index:] if not cell.get("executed", False)
        )
        if remaining > 0:
            next_cell_marker_id = cell_queue[next_cell_index]["marker_id"]
            print(
                f"📋 Next cell ready (Claude cell [{next_cell_marker_id}])",
                flush=True,
            )
    elif len(cell_queue) > 1:
        # All cells have been executed
        if all(cell["executed"] for cell in cell_queue):
            # Check if any had exceptions
            had_exceptions = any(cell.get("had_exception", False) for cell in cell_queue)
            if had_exceptions:
                print(
                    "⚠️ All of Claude's generated cells processed (some with errors)",
                    flush=True,
                )
            else:
                print(
                    "✅ All of Claude's generated cells have been processed successfully",
                    flush=True,
                )


def is_in_jupyter_notebook() -> bool:
    """Check if we're running in a Jupyter notebook (vs IPython terminal)."""
    ipython = get_ipython()
    return ipython is not None and hasattr(ipython, "kernel")
