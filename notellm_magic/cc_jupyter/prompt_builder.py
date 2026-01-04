"""
Prompt building functionality for Claude Code Jupyter magic.
Handles system prompts and content preparation.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .constants import EXECUTE_PYTHON_TOOL_NAME

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


def get_system_prompt(is_ipython: bool, max_cells: int) -> str:
    """Generate the system prompt for Claude based on environment.

    Args:
        is_ipython: Whether running in IPython (vs Jupyter notebook)
        max_cells: Maximum number of cells Claude can create

    Returns:
        Complete system prompt string
    """
    if is_ipython:
        env = "shared IPython session"
        tool_call_result = f"The {EXECUTE_PYTHON_TOOL_NAME} tool call will populate the next input with the Python code you provide."
        preference = f"""You can only call {EXECUTE_PYTHON_TOOL_NAME} once, since the IPython terminal does not allow for multiple pending code blocks.

The user will see the code block and can choose to execute it or not."""
    else:
        env = "Jupyter notebook"
        tool_call_result = f"Each {EXECUTE_PYTHON_TOOL_NAME} call will create a new cell in the user's Jupyter notebook interface."
        preference = f"""IMPORTANT: Prefer to call {EXECUTE_PYTHON_TOOL_NAME} only ONCE with a short code snippet.
As a last resort, you may call it multiple times to split up a large code block. You can make at most {max_cells} calls per turn (i.e., in response to each user prompt).
The user will be presented with the code blocks one by one.
If the user executes it and it succeeds, the next code block gets created in a new cell.
If the user executes it and it errors, then the error will get reported, but the chain is broken. Assume that the user does not see the subsequent code.
If the user executes a cell that is not the next code block, then the chain will pause until the proper next code block is executed.

If the user asks you to modify code in the current cell, you may do this by using the {EXECUTE_PYTHON_TOOL_NAME} tool EXACTLY ONCE.
Identifying that the current cell is the target is obvious because the code block is included directly in the user's request itself.

If the user asks you to edit/change/modify code in a DIFFERENT cell, inform them that you do not have that capability.
Instead, suggest that they use `%%cc edit this cell to <requested edits>` at the top of the cell they would like to edit.
Respond ONLY with that suggestion. DO NOT create new cells for the request and DEFINITELY DO NOT use the {EXECUTE_PYTHON_TOOL_NAME} tool."""

    system_prompt_preamble = f"""You are operating in a {env}.
You can see the current session state. You can create new code cells using the {EXECUTE_PYTHON_TOOL_NAME} tool.
{tool_call_result}
Never call {EXECUTE_PYTHON_TOOL_NAME} if you can answer the user's question directly with text.
{preference}
"""
    system_prompt_image_capture = """IMPORTANT: When generating code that displays images (matplotlib, seaborn, PIL, etc.), you MUST wrap that code with IPython's capture_output() and the variable `_claude_captured_output` to capture the images. Then, you must re-display the captured output. You can only have one _claude_captured_output context. Use this pattern:

```
from IPython.utils.capture import capture_output

# Your plotting/image code here
import matplotlib.pyplot as plt

with capture_output() as _claude_captured_output:
    plt.plot([1, 2, 3, 4])
    plt.show()
    plt.plot([3, 4, 5, 6])
    plt.show()

for output in _claude_captured_output.outputs:
    display(output)
```

This allows the system to capture any images for you for further processing."""

    system_prompt_tool_usage = f"""For any questions you can answer on your own, DO NOT use {EXECUTE_PYTHON_TOOL_NAME}.
Don't forget that you have other built-in tools like Read. Try responding using your built-in tools first without using {EXECUTE_PYTHON_TOOL_NAME}. Your response does not need to invoke {EXECUTE_PYTHON_TOOL_NAME}.
If you want to explain something to the user, do not put your explanation in {EXECUTE_PYTHON_TOOL_NAME}. Just return regular prose.

Examples:
<basic-example>
    <request>Help me understand what's in the dataframe `my_df`</request>
    This request should use {EXECUTE_PYTHON_TOOL_NAME} to generate the code for inspecting the dataframe.
</basic-example>

<no-python-example>
    <request>Explain how cc_jupyter/magics.py works</request>
    This request should not use {EXECUTE_PYTHON_TOOL_NAME} at all, since it can be fulfilled by reading the file.
</no-python-example>

<plot-example>
    <request>Plot the data in `my_df` and save the images to files</request>
    The generated code should use `with capture_output() as _claude_captured_output` to capture the displayed image.
</plot-example>

IMPORTANT: Do not invoke {EXECUTE_PYTHON_TOOL_NAME} in parallel.
IMPORTANT: Always include a return value or expression at the end of your {EXECUTE_PYTHON_TOOL_NAME} output. Only return values are captured in output cells - print statements are NOT captured.
For example, instead of print(df.head()), use df.head() as the last line.

If <request> is empty, it is because the user wants you to continue from where you left off in the previous messages."""

    return "\n".join(
        [system_prompt_preamble, system_prompt_image_capture, system_prompt_tool_usage]
    )


class PromptBuilder:
    """Builds and prepares prompts for Claude interactions."""

    def __init__(self, shell: InteractiveShell | None) -> None:
        """Initialize the prompt builder.

        Args:
            shell: IPython shell instance
        """
        self.shell = shell

    def prepare_imported_files_content(self, imported_files: list[str]) -> str:
        """Prepare content from imported files to include in initial conversation.

        Args:
            imported_files: List of file paths to import

        Returns:
            Formatted string with file contents
        """
        if not imported_files:
            return ""

        files_content = []

        for file_path_str in imported_files:
            file_path = Path(file_path_str)
            if file_path.exists():
                try:
                    with file_path.open() as f:
                        content = f.read()
                    files_content.append(f"{file_path.name}:\n```\n{content}\n```")
                except Exception:
                    # Skip files that can't be read
                    pass

        if files_content:
            return (
                "Files imported by the user for your reference. Use this content directly. Don't read them again:\n\n"
                + "\n\n".join(files_content)
            )
        return ""

    def build_enhanced_prompt(
        self,
        prompt: str,
        variables_info: str,
        previous_execution: str = "",
        shell_output: str = "",
        is_new_conversation: bool = False,
        imported_files_content: str = "",
        last_cells_content: str = "",
        captured_images: list[dict[str, Any]] | None = None,
    ) -> str | list[dict[str, Any]]:
        """Build the enhanced prompt with all context.

        Args:
            prompt: User's prompt text
            variables_info: Current variables information
            previous_execution: Previous execution results
            shell_output: Recent shell output
            is_new_conversation: Whether this is a new conversation
            imported_files_content: Content from imported files
            last_cells_content: Content from last executed cells
            captured_images: List of captured images

        Returns:
            Either a string prompt or structured content with images
        """
        if captured_images is None:
            captured_images = []

        # Build base enhanced prompt
        enhanced_prompt_text = f"""
Your client's request is <request>{prompt}</request>

{variables_info}
{previous_execution}
"""

        # Add shell output if present
        if shell_output:
            enhanced_prompt_text += shell_output

        # Prepend context for new conversations
        if is_new_conversation:
            context_parts = []

            # Add imported files content
            if imported_files_content:
                context_parts.append(imported_files_content)

            # Add last executed cells if requested
            if last_cells_content:
                context_parts.append(last_cells_content)

            if context_parts:
                enhanced_prompt_text = (
                    "\n\n".join(context_parts) + "\n\n" + enhanced_prompt_text
                )

        # Build structured content if we have images
        if captured_images:
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

            return content_blocks
        else:
            return enhanced_prompt_text
