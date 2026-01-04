"""
Cell watcher for detecting queued cell executions in Jupyter notebooks.

If someone does "Run All" on a notebook with %%cc blocks,
we don't want Claude to run again. Unfortunately, queued
cells are a client-side construct (they aren't preemptively
sent to the kernel), so we use hooks to watch for the execution
time in between cells.
"""

from __future__ import annotations

from collections import deque
from time import monotonic
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell

QUEUED_EXECUTION_THRESHOLD_SECONDS = 0.1


class CellWatcher:
    """Watches cell execution timing to detect queued executions."""

    def __init__(self, shell: InteractiveShell) -> None:
        """Initialize the cell watcher.

        Args:
            shell: IPython shell instance
        """
        self.shell = shell
        self.last_cell_finish_time = monotonic()
        self.time_between_cell_executions: deque[float] = deque(maxlen=2)

    def pre_run_cell(self, info: Any) -> None:
        """Hook called before a cell runs.

        Args:
            info: Cell execution info from IPython
        """
        self.time_between_cell_executions.append(
            monotonic() - self.last_cell_finish_time
        )

    def post_run_cell(self, result: Any) -> None:
        """Hook called after a cell runs.

        Args:
            result: Cell execution result from IPython
        """
        # Clients may fire off a bunch of executions after
        # restarting a kernel, such as loading this extension!
        # We want to ignore those.
        if result.execution_count:
            self.last_cell_finish_time = monotonic()

    def was_execution_probably_queued(self) -> bool:
        """Check if the current execution was probably part of a queue.

        Returns:
            True if execution appears to be queued (e.g., from Run All)
        """
        if len(self.time_between_cell_executions) < 2:
            return False

        previous_gap, current_gap = self.time_between_cell_executions
        return (
            previous_gap < QUEUED_EXECUTION_THRESHOLD_SECONDS
            and current_gap < QUEUED_EXECUTION_THRESHOLD_SECONDS
        )
