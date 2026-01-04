"""
Variable tracking functionality for Claude Code Jupyter magic.
Tracks changes in IPython session variables between interactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


class VariableTracker:
    """Tracks and reports changes in IPython session variables."""

    def __init__(self, shell: InteractiveShell | None) -> None:
        """Initialize the variable tracker.

        Args:
            shell: IPython shell instance
        """
        self.shell = shell
        self._previous_variables: dict[str, Any] = {}

    def reset(self) -> None:
        """Reset the variable tracking state."""
        self._previous_variables = {}

    def get_truncated_repr(self, value: Any, max_length: int = 100) -> str:
        """Get truncated repr of a value.

        Args:
            value: Value to represent
            max_length: Maximum length of the representation

        Returns:
            Truncated string representation
        """
        try:
            value_repr = repr(value)
            if len(value_repr) > max_length:
                value_repr = value_repr[: max_length - 3] + "..."
            return value_repr
        except Exception:
            return f"<{type(value).__name__} object>"

    def get_variables_info(self) -> str:
        """Get formatted information about current IPython variables, showing only changes.

        Returns:
            Formatted string describing variable changes
        """
        try:
            if self.shell is None:
                return "The IPython session has no user-defined variables."
            user_ns = self.shell.user_ns
            filtered_vars = {
                k: v
                for k, v in user_ns.items()
                if not k.startswith("_") and k not in ["In", "Out", "exit", "quit"]
            }

            if not filtered_vars and not self._previous_variables:
                return "The IPython session has no user-defined variables."

            # Detect changes
            added_vars = []
            modified_vars = []
            removed_vars = []

            # Check for added or modified variables
            for name, value in filtered_vars.items():
                if name not in self._previous_variables:
                    added_vars.append(name)
                else:
                    # Check if value changed by comparing repr
                    current_repr = self.get_truncated_repr(value)
                    previous_repr = self._previous_variables[name]
                    if current_repr != previous_repr:
                        modified_vars.append(name)

            # Check for removed variables
            for name in self._previous_variables:
                if name not in filtered_vars:
                    removed_vars.append(name)

            # Update previous state with truncated repr strings
            self._previous_variables = {}
            for name, value in filtered_vars.items():
                self._previous_variables[name] = self.get_truncated_repr(value)

            # Build output showing only changes
            var_lines = []

            if added_vars:
                var_lines.append("New variables:")
                for name in sorted(added_vars):
                    value = filtered_vars[name]
                    type_name = type(value).__name__
                    value_repr = self.get_truncated_repr(value)
                    var_lines.append(f"  + {name}: {type_name} = {value_repr}")

            if modified_vars:
                if var_lines:
                    var_lines.append("")
                var_lines.append("Modified variables:")
                for name in sorted(modified_vars):
                    value = filtered_vars[name]
                    type_name = type(value).__name__
                    value_repr = self.get_truncated_repr(value)
                    var_lines.append(f"  ~ {name}: {type_name} = {value_repr}")

            if removed_vars:
                if var_lines:
                    var_lines.append("")
                var_lines.append("Removed variables:")
                for name in sorted(removed_vars):
                    var_lines.append(f"  - {name}")

            if not var_lines:
                # No changes detected
                return "No variable changes detected since last interaction."

            return "Variable changes in IPython session:\n" + "\n".join(var_lines)

        except Exception:
            return "Could not retrieve session variables."
