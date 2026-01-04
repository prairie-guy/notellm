"""
IPython magic for Claude Code using SDK's in-process MCP server.

This refactored version eliminates the separate MCP and HTTP servers by using
the Claude Code SDK's @tool decorator and create_sdk_mcp_server functionality.
Instead of the complex flow: Claude → MCP Server Process → HTTP Server → Jupyter,
we now have: Claude → In-Process SDK Tool → Jupyter.
"""

from __future__ import annotations

import argparse
import contextlib
import queue
import signal
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import trio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    McpServerConfig,
    create_sdk_mcp_server,
    tool,
)
from IPython.core.magic import Magics, line_cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

from .capture_helpers import (
    extract_images_from_captured,
    format_images_summary,
)
from .claude_client import ClaudeClientManager, run_streaming_query
from .config_manager import ConfigManager
from .history_manager import HistoryManager
from .jupyter_integration import (
    adjust_cell_queue_markers,
    create_approval_cell,
    is_in_jupyter_notebook,
    process_cell_queue,
)
from .prompt_builder import PromptBuilder, get_system_prompt
from .variable_tracker import VariableTracker

if TYPE_CHECKING:
    from types import FrameType

    from IPython.core.interactiveshell import InteractiveShell

    from .cell_watcher import CellWatcher

# Global variables
_magic_instance: ClaudeCodeMagics | None = None


@tool(
    "create_python_cell",
    "Create a cell with Python code in the IPython environment",
    {"code": str},
)
async def execute_python_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Handle create_python_cell tool calls - create cells and return immediately."""
    if _magic_instance is None:
        # Ensure async checkpoint before returning
        await trio.lowlevel.checkpoint()
        return {
            "content": [{"type": "text", "text": "❌ Magic instance not initialized"}],
            "is_error": True,
        }

    code = args.get("code", "")
    if not code:
        # Ensure async checkpoint before returning
        await trio.lowlevel.checkpoint()
        return {
            "content": [{"type": "text", "text": "❌ No code provided"}],
            "is_error": True,
        }

    # Check if max_cells limit has been reached
    if (
        _magic_instance._config_manager.create_python_cell_count
        >= _magic_instance._config_manager.max_cells
    ):
        # Ensure async checkpoint before returning
        await trio.lowlevel.checkpoint()
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ Maximum number of cells ({_magic_instance._config_manager.max_cells}) reached for this turn. Please wait for the user to provide additional input before creating more cells.",
                }
            ],
            "is_error": True,
        }

    # Generate tool_use_id for tracking
    tool_use_id = str(uuid.uuid4())

    try:
        # Get or create request ID
        request_id = _magic_instance.current_request_id
        if not request_id:
            request_id = str(uuid.uuid4())
            _magic_instance.current_request_id = request_id

        # Initialize the request if it doesn't exist
        if request_id not in _magic_instance.pending_requests:
            _magic_instance.pending_requests[request_id] = {
                "timestamp": time.time(),
            }

        # Create cell in IPython
        _magic_instance._create_approval_cell(code, request_id, tool_use_id)

        # Increment the counter after successful cell creation
        _magic_instance._config_manager.create_python_cell_count += 1

        # Ensure async checkpoint before returning
        await trio.lowlevel.checkpoint()
        # Return immediately - don't wait for user
        return {
            "content": [
                {
                    "type": "text",
                    "text": "✅ Code cell created. Waiting for user to review and execute. The user will run %cc when ready to proceed.",
                }
            ]
        }

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        # Ensure async checkpoint before returning
        await trio.lowlevel.checkpoint()
        return {
            "content": [{"type": "text", "text": f"❌ Error creating cells: {e!s}"}],
            "is_error": True,
        }


@magics_class
class ClaudeCodeMagics(Magics):
    """IPython magic for Claude Code with direct SDK integration."""

    def __init__(self, shell: InteractiveShell, cell_watcher: CellWatcher) -> None:
        super().__init__(shell)
        global _magic_instance  # noqa: PLW0603
        _magic_instance = self

        self.cell_watcher = cell_watcher
        # Initialize delegated components
        self._variable_tracker = VariableTracker(shell)
        self._history_manager = HistoryManager(shell)
        self._prompt_builder = PromptBuilder(shell)
        self._config_manager = ConfigManager()

        # Request tracking for cell-based flow
        # request_id -> request data
        self.pending_requests: dict[str, dict[str, Any]] = {}

        # Track the current request ID for the batch of tool calls
        self.current_request_id: str | None = None

        # Track last line number we've seen for shell output
        # Now handled by history_manager

        # Claude client manager for persistent connections
        # Will be initialized on first use
        self._client_manager: ClaudeClientManager | None = None

        # Register post-execution hook to process cell queue
        if shell is not None:
            shell.events.register("post_run_cell", self._post_run_cell_hook)

        # Don't let ipython intercept question marks at the end of line magic
        from IPython.core.inputtransformer2 import EscapedCommand, HelpEnd

        HelpEnd.priority = EscapedCommand.priority + 1

    def _create_approval_cell(
        self, code: str, request_id: str, tool_use_id: str | None = None
    ) -> None:
        """Create a cell for user approval of code execution."""
        should_cleanup_prompts = (
            self._config_manager.should_cleanup_prompts
            or self._config_manager.editing_current_cell
        )
        create_approval_cell(
            self, code, request_id, should_cleanup_prompts, tool_use_id
        )

    def _post_run_cell_hook(self, result: Any) -> None:
        """Hook that runs after each cell execution to process the queue."""
        if self.shell is None:
            return

        # Check if we have a cell queue
        cell_queue: list[dict[str, Any]] = self.shell.user_ns.get(
            "_claude_cell_queue", []
        )
        if not cell_queue:
            return

        # Get the last executed code
        last_input = (
            self.shell.user_ns.get("In", [""])[-1] if "In" in self.shell.user_ns else ""
        )

        # Find the next unexecuted cell in the queue
        next_expected_index: int | None = None
        next_expected_marker: str | None = None
        next_expected_marker_id: str | None = None
        for i, cell_info in enumerate(cell_queue):
            if not cell_info["executed"]:
                next_expected_index = i
                next_expected_marker = cell_info.get("marker", "")
                next_expected_marker_id = cell_info["marker_id"]
                break

        # Check if the executed code contains the expected marker
        executed_expected = False
        if next_expected_marker and last_input.startswith(next_expected_marker):
            executed_expected = True
            # Mark this cell as executed
            if next_expected_index is not None:
                cell_queue[next_expected_index]["executed"] = True
                cell_queue[next_expected_index]["had_exception"] = (
                    not result.success if result else False
                )
                if result and not result.success and result.error_in_exec:
                    # Store the exception information
                    cell_queue[next_expected_index]["error"] = {
                        "type": type(result.error_in_exec).__name__,
                        "message": str(result.error_in_exec),
                    }

        # Only process the queue if the expected cell was executed successfully
        if executed_expected and result and result.success:
            # Set up the next cell
            process_cell_queue(self)
        elif executed_expected and result and not result.success:
            # Expected cell was executed but failed - notify user but don't set up next cell
            remaining = sum(1 for cell in cell_queue if not cell.get("executed", False))
            if remaining > 0:
                print(
                    f"\n⚠️ Execution failed. {remaining} cell(s) remaining in queue.",
                    flush=True,
                )
                print(
                    "Run %cc to continue with the error in context, or %cc_new to start fresh.",
                    flush=True,
                )
        elif not executed_expected and next_expected_marker:
            # User executed something else - check if it's a different queued cell
            for cell_info in cell_queue:
                marker = cell_info.get("marker", "")
                if marker and last_input.startswith(marker):
                    marker_id = cell_info["marker_id"]
                    print(
                        f"\n⚠️ Claude cell [{marker_id}] executed out of order. Expected Claude cell [{next_expected_marker_id}] to run next.",
                        flush=True,
                    )
                    print(
                        "Run the expected cell to continue the automatic queue, or use %cc to report results.",
                        flush=True,
                    )
                    break

    def __del__(self) -> None:
        """Clean up resources when magic is destroyed."""
        global _magic_instance  # noqa: PLW0603
        _magic_instance = None

        # Unregister post-execution hook
        if self.shell is not None:
            with contextlib.suppress(Exception):
                self.shell.events.unregister("post_run_cell", self._post_run_cell_hook)

        # Clear Claude client manager
        if self._client_manager is not None:
            with contextlib.suppress(Exception):
                # Just clear the reference - no need to disconnect since
                # we're creating fresh clients for each query now
                self._client_manager = None

    def _execute_prompt(
        self,
        prompt: str,
        previous_execution: str = "",
        captured_images: list[dict[str, Any]] | None = None,
        verbose: bool = False,
    ) -> None:
        """
        Implementation of claude_local functionality with support for captured images.

        Args:
            prompt: User prompt
            previous_execution: Previous execution context
            captured_images: Optional list of captured images from previous execution
            verbose: Whether to show verbose output
        """
        if captured_images is None:
            captured_images = []

        # Generate a new request ID for this batch of tool calls
        self.current_request_id = str(uuid.uuid4())

        # Reset create_python_cell_count for this turn
        self._config_manager.create_python_cell_count = 0

        # Check for captured output with images
        if self.shell is not None and "_claude_captured_output" in self.shell.user_ns:
            captured_output = self.shell.user_ns["_claude_captured_output"]
            captured_images = extract_images_from_captured(captured_output)

            # Clean up the captured output variable
            del self.shell.user_ns["_claude_captured_output"]

        # Get current variables for context
        variables_info = self._variable_tracker.get_variables_info()

        # Capture any shell output since last call
        # Skip this if we're loading cells for a new conversation to avoid duplication
        shell_output = ""
        if not self._config_manager.is_new_conversation:
            shell_output = self._history_manager.get_shell_output_since_last()

        # Build enhanced prompt with conversation history
        enhanced_prompt_text = f"""
Your client's request is <request>{prompt}</request>

{variables_info}
{previous_execution}
"""

        # Add shell output if present
        if shell_output:
            enhanced_prompt_text += shell_output

        # Prepend context for new conversations
        if self._config_manager.is_new_conversation:
            context_parts = []

            # Add imported files content
            if self._config_manager.imported_files:
                imported_content = self._prompt_builder.prepare_imported_files_content(
                    self._config_manager.imported_files
                )
                if imported_content:
                    context_parts.append(imported_content)

            # Add last executed cells if requested
            if (
                self._config_manager.cells_to_load != 0
            ):  # Load cells if not explicitly disabled (0)
                last_cells_content = self._history_manager.get_last_executed_cells(
                    self._config_manager.cells_to_load
                )
                if last_cells_content:
                    context_parts.append(last_cells_content)

            if context_parts:
                enhanced_prompt_text = (
                    "\n\n".join(context_parts) + "\n\n" + enhanced_prompt_text
                )

        # Build the prompt content - either as string or structured with images
        enhanced_prompt: str | list[dict[str, Any]]
        if captured_images:
            print(format_images_summary(captured_images), flush=True)

            # Build structured content with images
            content_blocks: list[dict[str, Any]] = []

            # Add images first
            for img in captured_images:
                content_blocks.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img["format"],
                            "data": img["data"],
                        },
                    }
                )

            # Add text content
            content_blocks.append({"type": "text", "text": enhanced_prompt_text})

            enhanced_prompt = content_blocks
        else:
            enhanced_prompt = enhanced_prompt_text

        # Create SDK MCP server with the execute_python tool
        sdk_server = create_sdk_mcp_server(
            name="jupyter_executor",
            version="1.0.0",
            tools=[execute_python_tool],  # This is the SdkMcpTool instance
        )

        # Build MCP servers dictionary - explicitly type as McpServerConfig to handle union type
        mcp_servers: dict[str, McpServerConfig] = {
            "jupyter": sdk_server
        }  # Start with our SDK server

        # Configure any additional MCP servers from config
        additional_mcp_servers = self._config_manager.get_mcp_servers(
            ""
        )  # Pass empty string instead of None

        if additional_mcp_servers:
            # Merge with our SDK server
            mcp_servers.update(additional_mcp_servers)

        options = ClaudeAgentOptions(
            allowed_tools=[
                "Bash",
                "LS",
                "Grep",
                "Read",
                "Edit",
                "MultiEdit",
                "Write",
                "WebSearch",
                "WebFetch",
                "mcp__jupyter__create_python_cell",
            ],
            model=self._config_manager.model,
            mcp_servers=mcp_servers,  # Use the combined dictionary
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": get_system_prompt(
                    is_ipython=not is_in_jupyter_notebook(),
                    max_cells=self._config_manager.max_cells,
                ),
            },
            setting_sources=["user", "project", "local"],
        )

        # If we have added directories, construct the permissions JSON
        settings_json = self._config_manager.get_claude_code_options_settings()
        if settings_json:
            options.settings = settings_json

        # Determine the appropriate working directory
        # For remote dev, we will set Claude Code's cwd to the monorepo root so
        # that Claude Code can access it. (Temporary solution until Claude Code
        # SDK supports --add-dir in the monorepo.)
        remote_dev_monorepo_root = Path("/root/code")
        try:
            if remote_dev_monorepo_root.exists():
                options.cwd = str(remote_dev_monorepo_root)
        except (PermissionError, OSError):
            pass

        # If we have an existing session ID from the client manager, use it to resume the conversation
        if self._client_manager is not None and self._client_manager.session_id:
            options.resume = self._client_manager.session_id

        # Run the query with streaming
        # Simple approach: always use a thread to avoid trio.run() nesting issues
        exception_queue: queue.Queue[Exception] = queue.Queue()

        def run_in_thread() -> None:
            try:
                # This always works because the thread has its own context
                trio.run(
                    self._run_streaming_query,
                    enhanced_prompt,
                    options,
                    verbose,
                )
            except Exception as e:
                exception_queue.put(e)

        # Run in a separate thread to avoid any trio context issues
        thread = threading.Thread(target=run_in_thread)
        thread.start()

        # Set up interrupt handler that sends interrupt signal to Claude
        original_handler = None

        def interrupt_handler(signum: int, frame: FrameType | None) -> None:
            # Send interrupt signal to Claude client if one exists
            if self._client_manager is not None:
                print("Interrupting Claude Code")

                # Handle interrupt in a separate thread to avoid nesting trio.run()
                def handle_interrupt() -> None:
                    if self._client_manager is not None:
                        with contextlib.suppress(Exception):
                            trio.run(self._client_manager.handle_interrupt)

                interrupt_thread = threading.Thread(target=handle_interrupt)
                interrupt_thread.start()

        # Install our handler temporarily
        try:
            original_handler = signal.signal(signal.SIGINT, interrupt_handler)
            thread.join()
        finally:
            # Restore original handler
            if original_handler is not None:
                signal.signal(signal.SIGINT, original_handler)

        # Check for exceptions
        if not exception_queue.empty():
            raise exception_queue.get()

        # Update last_output_line to current position after conversation completes
        # This ensures the next call will capture any cells executed after set_next_input
        self._history_manager.update_last_output_line()

        adjust_cell_queue_markers(self)

        # After the async operation completes, set any pending input for terminal
        if self.shell is not None and "_claude_pending_input" in self.shell.user_ns:
            pending_input = self.shell.user_ns["_claude_pending_input"]
            del self.shell.user_ns["_claude_pending_input"]
            with contextlib.suppress(Exception):
                # Now we can safely set the next input
                self.shell.set_next_input(
                    pending_input,
                    replace=self._config_manager.should_cleanup_prompts
                    or self._config_manager.editing_current_cell,
                )

        self._config_manager.is_new_conversation = False

    async def _run_streaming_query(
        self,
        prompt: str | list[dict[str, Any]],
        options: ClaudeAgentOptions,
        verbose: bool,
    ) -> None:
        """Run Claude query with real-time message streaming."""
        self._config_manager.is_current_execution_verbose = verbose
        await run_streaming_query(self, prompt, options, verbose)
        self._config_manager.is_current_execution_verbose = False

    def _claude_continue_impl(
        self, request_id: str, additional_prompt: str = "", verbose: bool = False
    ) -> str:
        cell_queue: list[dict[str, Any]] = (
            self.shell.user_ns.get("_claude_cell_queue", []) if self.shell else []
        )

        if verbose:
            executed_count = sum(1 for cell in cell_queue if cell.get("executed", False))
            total_count = len(cell_queue)

            print(
                f"📊 Cell execution summary: {executed_count} of {total_count} cells executed",
                flush=True,
            )

        execution_results = []
        for i, cell in enumerate(cell_queue):
            tool_use_id = cell.get("tool_use_id", "")
            code = cell.get("original_code", cell.get("code", ""))
            executed = cell.get("executed", False)
            had_exception = cell.get("had_exception", False)
            error_info = cell.get("error", None)
            output = None

            # If executed, try to get output from history
            if executed:
                try:
                    if self.shell is not None:
                        history = self._history_manager.get_history_range(
                            start=-10,  # Look at last 10 entries to find all cells
                            stop=None,
                        )

                        for _session_id, _line_num, (
                            input_code,
                            output_result,
                        ) in history:
                            if input_code.strip() == code.strip():
                                if output_result is not None:
                                    output = str(output_result)
                                break
                except Exception:
                    pass

            # Build result summary
            if tool_use_id:
                result_entry = f"Tool use {tool_use_id}: "
            else:
                result_entry = f"Code cell {i + 1}: "

            if executed:
                if had_exception:
                    if error_info:
                        result_entry += f"Executed but encountered {error_info['type']}: {error_info['message']}"
                    else:
                        result_entry += "Executed but encountered an error"
                elif output:
                    result_entry += f"Executed successfully with output:\n{output}"
                else:
                    result_entry += "Executed successfully (no output)"
            else:
                result_entry += "Not executed by user"

            execution_results.append(result_entry)

        continue_prompt = (
            "Previous code execution results for requested code cells:\n"
            + "\n\n".join(execution_results)
        )

        additional_prompt = additional_prompt.strip()
        if not additional_prompt:
            additional_prompt = "Please continue with the task."

        print("✅ Continuing Claude session with execution results...", flush=True)

        # Clean up namespace
        if self.shell is not None:
            if "_claude_request_id" in self.shell.user_ns:
                del self.shell.user_ns["_claude_request_id"]

            # Clear the cell queue
            if "_claude_cell_queue" in self.shell.user_ns:
                del self.shell.user_ns["_claude_cell_queue"]

        # Clean up the pending request
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]

        # Run a new Claude query with the execution results
        self._execute_prompt(additional_prompt, continue_prompt)

        return request_id  # Return for cell deletion logic

    def _handle_cc_options(self, args: Any) -> bool:
        """
        Handle all command-line options for the cc magic command.
        Returns True if any option was handled (meaning the command should return early).
        """
        return self._config_manager.handle_cc_options(args, self.cell_watcher)

    @line_cell_magic
    @magic_arguments()
    @argument("--verbose", "-v", action="store_true", help="Show verbose output")
    @argument(
        "--allow-run-all",
        "-a",
        action="store_true",
        help="Allow this cell to call Claude when Run All is used",
    )
    @argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Persistent setting for this session to automatically clean up prompt cells with Claude's code cells",
    )
    @argument(
        "--max-cells",
        type=int,
        default=None,
        help="Maximum number of code cells Claude can create (default: 3)",
    )
    @argument(
        "--help",
        "-h",
        action="store_true",
        help="Show available options and usage information",
    )
    @argument(
        "--import",
        type=str,
        dest="import_file",
        help="Add a file to be included in initial conversation messages",
    )
    @argument(
        "--add-dir",
        type=str,
        dest="add_dir",
        help="Add a directory to Claude's accessible directories",
    )
    @argument(
        "--mcp-config",
        type=str,
        dest="mcp_config",
        help="Path to a .mcp.json file containing MCP server configurations",
    )
    @argument(
        "--cells-to-load",
        type=int,
        dest="cells_to_load",
        help="Maximum number of recent cells to load when starting a new conversation (default: 0)",
    )
    @argument(
        "--model",
        type=str,
        dest="model",
        help="Model to use for Claude Code (default: sonnet)",
    )
    def cc(self, line: str, cell: str | None = None) -> None:
        """
        Run Claude Code with full agentic loop.

        This combines the functionality of claude_local and claude_continue:
        - If there's a pending code execution, it continues with the results
        - Otherwise, it starts/continues a conversation with Claude

        Usage as line magic:
            %cc
            %cc additional instructions here
            %cc --verbose
            %cc --help

        Usage as cell magic:
            %%cc
            Create a pandas DataFrame and plot it

            %%cc --verbose
            Show detailed tool call information

        Note: If your prompt ends with '?', use cell magic (%%cc) instead of line magic (%cc)
        to avoid IPython's help system interference.
        """
        if cell is not None:
            line = line + "\n" + cell

        # Parse arguments and prompt
        args, prompt = self._parse_args_and_prompt(line, self.cc)

        # Handle all command-line options (returns True if we should exit early)
        if self._handle_cc_options(args):
            return

        # If no prompt provided after handling options, return
        if not prompt:
            return

        # Check if there's a pending request
        request_id = (
            self.shell.user_ns.get("_claude_request_id")
            if self.shell is not None
            else None
        )

        if request_id:
            # There's a pending code execution - continue with it
            self._claude_continue_impl(request_id, prompt, args.verbose)
        else:
            # Clear any remaining cell queue when starting a new prompt
            if self.shell is not None and "_claude_cell_queue" in self.shell.user_ns:
                cell_queue = self.shell.user_ns["_claude_cell_queue"]
                if cell_queue:
                    unexecuted = sum(
                        1 for cell in cell_queue if not cell.get("executed", False)
                    )
                    if unexecuted > 0:
                        print(
                            f"⚠️ Clearing {unexecuted} unexecuted cells from previous request",
                            flush=True,
                        )
                del self.shell.user_ns["_claude_cell_queue"]

            if not prompt:
                raise ValueError("A prompt must be provided to start the conversation.")
            self._execute_prompt(prompt, verbose=args.verbose)

    @line_cell_magic
    def ccn(self, line: str, cell: str | None = None) -> None:
        """
        An alias for %cc_new
        """
        self.cc_new(line, cell)

    @line_cell_magic
    def cc_new(self, line: str, cell: str | None = None) -> None:
        """
        Run Claude Code with a fresh conversation (no history).

        Usage as line magic:
            %cc_new
            %cc_new Analyze this data from scratch
            %cc_new --verbose Start a new analysis

        Usage as cell magic:
            %%cc_new
            Analyze this data from scratch

            %%cc_new --verbose
            Start a new analysis with detailed output
        """
        if cell is not None:
            line = line + "\n" + cell

        # Parse arguments and prompt
        args, prompt = self._parse_args_and_prompt(line, self.cc)

        # Handle all command-line options (returns True if we should exit early)
        if self._handle_cc_options(args):
            return

        if not prompt:
            raise ValueError("A prompt must be provided to start the conversation.")

        # Reset shell output tracking to 0 so new conversation sees all shell history
        self._history_manager.reset_output_tracking()

        # Reset variable tracking for new conversation
        self._variable_tracker.reset()

        # Reset configuration for new conversation
        self._config_manager.reset_for_new_conversation()

        # Clear any remaining cell queue since we're starting fresh
        if self.shell is not None and "_claude_cell_queue" in self.shell.user_ns:
            del self.shell.user_ns["_claude_cell_queue"]

        # Reset session in the client manager to force new conversation
        if self._client_manager is not None:
            self._client_manager.reset_session()
        else:
            # Create a new client manager if needed
            self._client_manager = ClaudeClientManager()

        # Now run as normal
        self._config_manager.is_new_conversation = True
        self._execute_prompt(prompt, verbose=args.verbose)

    def _parse_args_and_prompt(
        self, line: str, magic_func: Any
    ) -> tuple[Any, str]:
        """Parse arguments and prompt from magic command line.

        Returns tuple of (args, prompt).
        """
        self._config_manager.editing_current_cell = False

        parts = line.split(None, 1) if line else []  # Split into at most 2 parts

        if not parts:
            # Empty line
            return parse_argstring(magic_func, ""), ""

        # Check if first part looks like an argument
        if parts[0].startswith("-"):
            # First part is an argument
            first_part = parts[0]
            remaining = parts[1] if len(parts) > 1 else ""

            # Get all value-taking args
            value_taking_args = []
            for action in magic_func.parser._actions:
                # Skip help action and positional arguments
                if action.option_strings and action.nargs != 0:
                    # Store both short and long forms
                    value_taking_args.extend(action.option_strings)

            # Special handling for arguments that take values
            if first_part in value_taking_args:
                # These arguments need a value, check if we have more parts
                value_and_prompt = remaining.split(None, 1) if remaining else []
                if value_and_prompt:
                    # We have a value
                    args_str = f"{first_part} {value_and_prompt[0]}"
                    prompt = value_and_prompt[1] if len(value_and_prompt) > 1 else ""
                else:
                    # No value provided, let argparse handle the error
                    args_str = first_part
                    prompt = ""
            else:
                # Boolean flag or other argument type
                args_str = first_part
                prompt = remaining

            return parse_argstring(magic_func, args_str), prompt
        else:
            lines = line.splitlines()
            if any("=" in code_line or "(" in code_line for code_line in lines[1:]):
                self._config_manager.editing_current_cell = True

            # First part is not an argument, entire line is the prompt
            return parse_argstring(magic_func, ""), line
