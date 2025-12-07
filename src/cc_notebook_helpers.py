"""IPython magic commands for notebook cell utilities."""
from IPython.core.magic import Magics, line_magic, cell_magic, magics_class
from IPython.display import display, Markdown
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent))
import notebook_utils as nu

@magics_class
class NotebookHelpers(Magics):
    """Magic commands for notebook cell utilities."""

    def __init__(self, shell):
        super().__init__(shell)
        self._current_nb = None

    def _get_notebook_path(self) -> Path:
        """Get current notebook path with automatic detection."""
        if self._current_nb: return Path(self._current_nb)

        # Method 1: Try JPY_SESSION_NAME environment variable (JupyterLab 3.0+)
        import os
        notebook_path = os.environ.get("JPY_SESSION_NAME")
        if notebook_path:
            return Path(notebook_path)

        # Method 2: Try Jupyter Server Sessions API
        try:
            import re
            from ipykernel.connect import get_connection_file

            # Get kernel ID from connection file
            connection_file = get_connection_file()
            kernel_match = re.search(r'kernel-(.*?)\.json', connection_file)
            if kernel_match:
                kernel_id = kernel_match.group(1)

                # Query Jupyter server (notellm uses port 9999)
                import urllib.request
                token = 'notellm-9fec938a535ba980'
                url = f'http://localhost:9999/api/sessions?token={token}'

                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=2) as response:
                    import json
                    sessions = json.loads(response.read())

                    for session in sessions:
                        if session.get('kernel', {}).get('id') == kernel_id:
                            path = session.get('notebook', {}).get('path') or session.get('path')
                            if path:
                                return Path(path)
        except:
            pass

        # Fallback: require manual setting
        raise RuntimeError(
            "Could not auto-detect notebook path.\n"
            "Tip: Ensure JupyterLab server is running on localhost:9999"
        )

    @line_magic
    def nb_list(self, line: str):
        """List all cells."""
        try:
            nb_path = self._get_notebook_path()
            show_empty = '--show-empty' in line or '-a' in line
            nu.list_cells(nb_path, show_empty=show_empty)
        except Exception as e:
            print(f"Error: {e}")

    @line_magic
    def nb_find(self, line: str):
        """Find cells by content.

        Usage:
            %nb_find <query>              # Search content
            %nb_find --content <query>    # Explicit content search
        """
        try:
            nb_path = self._get_notebook_path()
            parts = line.strip().split(maxsplit=1)

            if not parts:
                print("Error: No query provided")
                return

            if parts[0] == '--content':
                query = parts[1] if len(parts) > 1 else ''
            else:
                query = line.strip()

            matches = nu.find_cell(nb_path, query)

            if matches:
                print(f"\nFound {len(matches)} match(es) for '{query}':")
                nb = nu.read_notebook(nb_path)
                for i in matches:
                    cell = nb['cells'][i]
                    ctype = cell['cell_type']
                    first = nu.get_cell_first_line(cell)
                    print(f"[{i:>2}] {ctype:8} \"{first}\"")
            else:
                print(f"\nNo matches found for '{query}'")

        except Exception as e:
            print(f"Error: {e}")

    @line_magic
    def nb_section(self, line: str):
        """Find cells under a markdown header.

        Usage: %nb_section <header>
        Example: %nb_section ### Configuration
        """
        try:
            nb_path = self._get_notebook_path()
            header = line.strip()

            if not header:
                print("Error: No header provided")
                return

            matches = nu.get_section_cells(nb_path, header)

            if matches:
                print(f"\nFound {len(matches)} cell(s) under '{header}':")
                nb = nu.read_notebook(nb_path)
                for i in matches:
                    cell = nb['cells'][i]
                    ctype = cell['cell_type']
                    first = nu.get_cell_first_line(cell)
                    print(f"[{i:>2}] {ctype:8} \"{first}\"")
            else:
                print(f"\nNo cells found under '{header}'")

        except Exception as e:
            print(f"Error: {e}")

    @cell_magic
    def nb_modify(self, line: str, cell: str):
        """Modify code in this cell using Claude (via subprocess claude code).

        Usage:
            %%nb_modify <instruction>
            <code to modify>

        Example:
            %%nb_modify sort penguins by name length
            df = sns.load_dataset('penguins')
            species_order = sorted(df['species'].dropna().unique())
        """
        try:
            instruction = line.strip()
            current_code = cell.strip()

            if not instruction:
                print("Error: No instruction provided")
                return

            # Build prompt for Claude
            prompt = f"""Modify this Python code according to the instruction.
Return ONLY the modified code, no explanations or markdown formatting.

Instruction: {instruction}

Original code:
{current_code}

Modified code:"""

            display(Markdown("🔄 Modifying code with Claude..."))

            # Use Claude CLI via subprocess (same as cc_jupyter)
            import subprocess

            # Call claude code with --print flag and prompt via stdin
            result = subprocess.run(
                ['claude', 'code', '--print'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"Error from Claude: {result.stderr}")
                return

            modified_code = result.stdout.strip()

            # Remove markdown code fences if present
            if modified_code.startswith("```"):
                lines = modified_code.split('\n')
                # Remove first and last lines if they're fences
                if lines[0].startswith("```") and lines[-1].strip() == "```":
                    modified_code = '\n'.join(lines[1:-1])

            # Use shell.set_next_input to create next cell with modified code
            self.shell.set_next_input(modified_code)

            display(Markdown(f"✓ Modified code will appear in next cell"))

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def load_ipython_extension(ipython):
    """Load the extension."""
    ipython.register_magics(NotebookHelpers)
    display(Markdown("""
✓ **Notebook Helpers loaded!**

**Commands:**
- `%nb_list` - List all cells
- `%nb_find <query>` - Find cells by content
- `%nb_find --content <query>` - Explicit content search
- `%nb_section <header>` - Find cells under markdown header
- `%%nb_modify <instruction>` - Modify code in this cell using Claude

**Options:**
- `%nb_list --show-empty` or `%nb_list -a` - Include empty cells

**Example Iterative Editing:**
```python
%%nb_modify sort penguins by name length
df = sns.load_dataset('penguins')
species_order = sorted(df['species'].dropna().unique())
```
"""))

def unload_ipython_extension(ipython):
    """Unload the extension."""
    pass
