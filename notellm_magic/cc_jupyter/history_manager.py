"""
IPython history management for Claude Code Jupyter magic.
Handles cell history tracking and formatting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


class HistoryManager:
    """Manages IPython history tracking and formatting."""

    def __init__(self, shell: InteractiveShell | None) -> None:
        """Initialize the history manager.

        Args:
            shell: IPython shell instance
        """
        self.shell = shell
        self.last_output_line = 0

    def reset_output_tracking(self) -> None:
        """Reset output tracking to start of history."""
        self.last_output_line = 0

    def update_last_output_line(self) -> None:
        """Update last_output_line to current position after conversation completes."""
        if self.shell is not None:
            self.last_output_line = len(self.shell.user_ns.get("In", [])) - 1

    def get_history_range(
        self, start: int | None = None, stop: int | None = None
    ) -> list[tuple[int, int, Any]]:
        """Get history range from the shell's history manager.

        Args:
            start: Starting line number (negative for last N entries, or positive for specific line)
            stop: Ending line number (None for current)

        Returns:
            List of (session_id, line_num, item) tuples where item is either
            input_code string or (input_code, output_result) tuple
        """
        if self.shell is None or self.shell.history_manager is None:
            return []

        try:
            session_id = self.shell.history_manager.get_last_session_id()
            return list(
                self.shell.history_manager.get_range(
                    session=session_id,
                    start=start,
                    stop=stop,
                    raw=False,
                    output=True,  # Include outputs when available
                )
            )
        except Exception:
            return []

    def format_cell(
        self, line_num: int, input_code: str, output_result: Any = None
    ) -> str:
        """Format a cell's input and output as XML tags.

        Args:
            line_num: Line number for the cell
            input_code: The input code
            output_result: Optional output result

        Returns:
            Formatted string with XML tags
        """
        cell_parts = []

        # Add input with its own tags
        cell_parts.append(f"<cell-in-{line_num}>")
        cell_parts.append(f"{input_code.strip()}")
        cell_parts.append(f"</cell-in-{line_num}>")

        # Add output with its own tags if it exists
        if output_result is not None:
            cell_parts.append(f"<cell-out-{line_num}>")
            if isinstance(output_result, str):
                cell_parts.append(f"{output_result}")
            else:
                cell_parts.append(f"{output_result!r}")
            cell_parts.append(f"</cell-out-{line_num}>")

        return "\n".join(cell_parts)

    def get_shell_output_since_last(self) -> str:
        """Get any shell commands and output since the last claude_local call.

        Returns:
            Formatted string with recent shell interactions
        """
        try:
            shell_interactions = []

            # Get history from last_output_line+1 to current
            history = self.get_history_range(start=self.last_output_line + 1, stop=None)

            if history:
                for _, line_num, item in history:
                    # Extract input and output from item
                    if isinstance(item, tuple):
                        input_code, output_result = item
                    else:
                        input_code = item
                        output_result = None

                    # Skip claude magic commands
                    if input_code and not input_code.strip().startswith(
                        "get_ipython().run_cell_magic"
                    ):
                        formatted_cell = self.format_cell(
                            line_num, input_code, output_result
                        )

                        # If no output from history but it exists in Out dict, add it
                        if output_result is None and self.shell:
                            out_dict = self.shell.user_ns.get("Out", {})
                            if line_num in out_dict:
                                formatted_cell = self.format_cell(
                                    line_num, input_code, out_dict[line_num]
                                )

                        shell_interactions.append(formatted_cell)
            else:
                # Fallback to the old method if history manager fails
                if self.shell:
                    in_list = self.shell.user_ns.get("In", [])
                    out_dict = self.shell.user_ns.get("Out", {})

                    for i in range(self.last_output_line + 1, len(in_list)):
                        cmd = in_list[i] if i < len(in_list) else None
                        if cmd and not cmd.strip().startswith(
                            "get_ipython().run_cell_magic"
                        ):
                            output = out_dict.get(i)
                            formatted_cell = self.format_cell(i, cmd, output)
                            shell_interactions.append(formatted_cell)

            if shell_interactions:
                shell_output = "\n".join(shell_interactions)
                return f"\nRecent IPython cell executions (Note: Only return values are captured, print statements are not shown):\n{shell_output}\n"

            return ""

        except Exception:
            return ""

    def get_last_executed_cells(self, n: int) -> str:
        """Get the last N executed cells from IPython history for initial conversation context.

        If n is -1, loads all available history.

        Args:
            n: Number of cells to load (-1 for all, 0 for none)

        Returns:
            Formatted string with cell history
        """
        if n == 0:
            return ""

        if n == -1:
            # Load all available history
            history = self.get_history_range(start=1, stop=None)
        elif n > 0:
            # Load last N entries
            history = self.get_history_range(start=-n, stop=None)
        else:
            return ""

        try:
            if not history:
                return ""

            cells_content = []
            cells_content.append("Last executed cells from this session:")

            for _session_id, line_num, item in history:
                # Extract input and output from item
                if isinstance(item, tuple):
                    input_code, output_result = item
                else:
                    input_code = item
                    output_result = None

                # Skip magic commands
                if input_code and not input_code.strip().startswith(
                    "get_ipython().run_cell_magic"
                ):
                    formatted_cell = self.format_cell(
                        line_num, input_code, output_result
                    )
                    cells_content.append(formatted_cell)

            if len(cells_content) > 1:  # More than just the header
                return "\n\n".join(cells_content)
            return ""

        except Exception:
            return ""
