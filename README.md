# notellm

A streamlined development environment for iterative notebook development combining:
- Jupyter notebooks for interactive data science
- Claude Code for AI-assisted development
- Work directly in notebooks with `%cc` magic for AI assistance and `%%nb_modify` for iterative code refinement
- Built-in notebook helpers for cell organization and management

**New workflow:** Develop iteratively within notebooks using magic commands—no external MCP server required.

## Prerequisites

Before installing notellm, ensure you have **Claude Code CLI** installed and working.

### Installing Claude Code

Follow the [Official Claude Code Setup Guide](https://code.claude.com/docs/en/setup) to install and configure the CLI.

**Authentication:**

After installation, authenticate with your Anthropic account. You'll need:
- Active billing at [console.anthropic.com](https://console.anthropic.com)
- A "Claude Code" workspace will be created automatically for usage tracking

### Other Requirements

- **Python 3.12+** - Required for JupyterLab and data science packages
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager (installed automatically if missing)

## Installation

```bash
git clone https://github.com/prairie-guy/notellm.git
cd notellm
./setup.sh
```

This installs:
- `~/.local/share/notellm/` — templates and scripts
- `~/.local/bin/notellm` — the command

> **Note:** If `~/.local/bin` is not in your PATH, add this to your `~/.bashrc` or `~/.zshrc`:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

## Quick Start

### 1. Create a new project

```bash
cd ~/projects
mkdir my_analysis
cd my_analysis
notellm start
```

This creates a workspace with JupyterLab, Claude Code integration, and notebook helpers.

### 2. Start the server

Patches are applied automatically:

```bash
notellm start
```

The first start will apply cc_jupyter patches automatically (see Technical Details below).

### 3. Open JupyterLab

The server URL will be displayed. Open it in your browser (typically `http://localhost:9999`).

### 4. Create a notebook

```bash
notellm new exploration
```

### 5. Load magic commands

In your first notebook cell:

```python
%load_ext notellm_magic
```

### 6. Iterative Development Workflow

**Generate initial code with %cc:**

```python
%cc Create a function to calculate fibonacci numbers with memoization
```

Claude will create a new cell with the fibonacci function.

**Refine code iteratively with %%nb_modify:**

Add `%%nb_modify` to the cell with your code:

```python
%%nb_modify add type hints and a docstring
def fibonacci(n):
    cache = {}
    def fib(n):
        if n in cache: return cache[n]
        if n <= 1: return n
        cache[n] = fib(n-1) + fib(n-2)
        return cache[n]
    return fib(n)
```

Run the cell—Claude will modify your code and create a new cell below with the improvements.

**Continue iterating:**

Add `%%nb_modify` to the new cell to refine further:

```python
%%nb_modify make it iterative instead of recursive
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number with memoization."""
    cache = {}
    def fib(n):
        if n in cache: return cache[n]
        if n <= 1: return n
        cache[n] = fib(n-1) + fib(n-2)
        return cache[n]
    return fib(n)
```

This workflow enables rapid, incremental code development entirely within the notebook.

### 7. Use %cc for other tasks

```python
# Get help understanding code
%cc Explain how this fibonacci function works

# Generate visualizations
%cc Create a plot showing fibonacci growth rate for n=1 to 20

# Analyze data
%cc Load the penguins dataset and show summary statistics
```

### 8. When done

```bash
notellm stop
```

**Key difference from traditional workflows:** Instead of switching between terminal and notebook, or using external servers, you develop iteratively within the notebook itself using `%%nb_modify` for refinements and `%cc` for new code generation.

## Magic Commands for In-Notebook Development

notellm provides two types of magic commands for different purposes:

### %cc - Claude Code Magic

Use Claude Code directly in notebook cells for AI-assisted development.

**Basic usage:**

```python
%cc <instruction>          # Single-line prompt
%%cc <instruction>         # Multi-line prompt
Code context here...
```

**Examples:**

```python
# Generate new code
%cc Create a function to load CSV files with polars

# Analyze existing code
%cc Explain what this function does and suggest improvements

# Generate visualizations
%cc Create a scatter plot of price vs. size with altair
```

**Available options:**

```python
# Conversation management
%cc_new                    # Start fresh conversation (alias: %ccn)

# Context management
%cc --import <file>        # Include file in conversation
%cc --add-dir <dir>        # Add directory to accessible paths
%cc --cells-to-load <num>  # Number of cells to load (default: all)

# Output control
%cc --model <name>         # Model: sonnet (default), opus, haiku
%cc --max-cells <num>      # Max cells created per turn (default: 3)

# Display options
%cc --clean                # Replace prompt cells with code cells
%cc --no-clean             # Keep prompt cells (default)
```

**Built-in tools available to %cc:**
- `Bash` - Run shell commands
- `Read` - Read files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Grep` - Search file contents
- `WebSearch` - Search the web
- `WebFetch` - Fetch web content

---

### %%nb_modify - Iterative Code Refinement

**The primary tool for iterative notebook development.**

Modify code in the current cell using Claude. The modified code appears in a new cell below, enabling rapid iteration.

**Usage pattern:**

```python
%%nb_modify <instruction>
<code to modify>
```

**Example workflow:**

```python
# Initial code
def process_data(df):
    return df.filter(pl.col("age") > 18)
```

```python
# Refine it
%%nb_modify add parameter for minimum age, add type hints, add docstring
def process_data(df):
    return df.filter(pl.col("age") > 18)
```

Result: New cell created with improved code.

```python
# Continue refining
%%nb_modify also filter out null values in the age column
def process_data(df: pl.DataFrame, min_age: int = 18) -> pl.DataFrame:
    """Filter dataframe to include only records above minimum age."""
    return df.filter(pl.col("age") > min_age)
```

Result: Another new cell with further improvements.

**Why %%nb_modify?**
- Fast iteration without leaving the notebook
- Preserves your code history in cells
- No need to describe location—operates on "this cell"
- Clean output—only the modified code, no magic command in result

---

### %nb - Notebook Organization (Optional)

Helper commands for organizing and navigating notebooks. **These are optional**—use them only if they add value to your workflow.

**Available commands:**

```python
%nb_list                        # List all cells
%nb_list --show-empty           # Include empty cells

%nb_find <query>                # Search cells by content
%nb_find --content <query>      # Explicit content search

%nb_section <header>            # Find cells under markdown header
```

**Example use case:**

```python
# List all cells
%nb_list

# Find specific functionality
%nb_find load_dataset

# Find cells under a section
%nb_section ## Data Loading
```

**Note:** For iterative development, use `%%nb_modify` which operates on the current cell.

## Commands

### `notellm start`

Initialize workspace (if needed) and start JupyterLab server.

```bash
notellm start                      # Use defaults or existing config
notellm start --port 9998          # Reinitialize with custom port
notellm start --host myserver      # Reinitialize with hostname
notellm start --token mysecret     # Reinitialize with custom token
notellm start --foreground         # Run in foreground (Ctrl+C to stop)
```

**Behavior:**
- If no config exists OR options provided: initializes workspace first
- Otherwise: uses existing configuration
- **Never overwrites existing `pyproject.toml`** — your customizations are preserved

**Creates (on first run):**
- `pyproject.toml` — Python dependencies (only if doesn't exist)
- `CLAUDE.md` — Instructions for Claude Code
- `.claude/settings.json` — Claude Code permissions
- `.env.jupyter` — Port and token config
- `.notellm_template.ipynb` — Customizable notebook template

**Note:** All notellm utilities are installed globally in `~/.local/share/notellm/lib/` (shared across all projects).

### `notellm stop`

Stop the JupyterLab server.

```bash
notellm stop              # Stop all processes on configured port
notellm stop --port 8888  # Stop all processes on port 8888
```

**Behavior:**
- Finds all processes using the specified port (or configured port from `.env.jupyter`)
- Sends SIGTERM for graceful shutdown (waits up to 8 seconds)
- Automatically sends SIGKILL if process doesn't exit
- Cleans up `.jupyter.pid` file
- Default port: Uses `.env.jupyter` if exists, otherwise 9999

### `notellm status`

Show the status of the configured server and all running Jupyter Lab instances.

```bash
notellm status
```

**Displays:**
- Current directory's configured server (if exists) with URLs and running status
- All Jupyter Lab processes running system-wide with their PIDs and ports
- Helpful for troubleshooting when multiple servers are running

### `notellm clean`

Remove configuration files from the workspace.

```bash
notellm clean             # Remove config files only
notellm clean --purge     # Remove everything including dependencies
```

**Default behavior:**
- Removes: `.env.jupyter`, `.jupyter.pid`, `.jupyter.log`, `.mcp.json`, `.ipynb_checkpoints/`
- Refuses to clean if server is running (run `notellm stop` first)
- Preserves: `pyproject.toml`, `.notellm_template.ipynb`, all user notebooks

**With --purge:**
- Removes everything: `.venv/`, `uv.lock`, `CLAUDE.md`, `.claude/`, `.jupyter*` files,
  `pyproject.toml`, `.notellm_template.ipynb`
- Removes `.gitignore` **only if** it contains the `### NOTELLM_GITIGNORE ###` marker
- Cleans uv cache for patched packages
- Requires confirmation before proceeding
- Use when you want to completely remove notellm from a project

**Always preserved (even with --purge):**
- All user notebooks: `*.ipynb` files (except `.notellm_template.ipynb`)
- `.gitignore` without the notellm marker (user-created or customized)
- Any other user-created files and directories

**About `.gitignore`:**
- Created on first `notellm start` if doesn't exist
- Contains `### NOTELLM_GITIGNORE ###` marker at top
- Remove marker to prevent deletion by `--purge`
- Never overwritten (safe to customize)
- Template located at `~/.local/share/notellm/templates/.gitignore`

#### What Remains After Clean

**After `notellm clean`:**

Your workspace retains its notellm configuration and is ready to restart:

```
my_project/
├── pyproject.toml              # Python dependencies (preserved)
├── .notellm_template.ipynb     # Notebook template (preserved)
├── CLAUDE.md                   # Claude instructions (preserved)
├── .claude/                    # Claude settings (preserved)
├── .venv/                      # Virtual environment (preserved)
├── uv.lock                     # Dependency lock (preserved)
├── .gitignore                  # Git ignore rules (preserved)
└── *.ipynb                     # All user notebooks (preserved)
```

**Result:** Run `notellm start` to resume work. All dependencies and configuration remain intact.

---

**After `notellm clean --purge`:**

Your workspace is returned to a clean state with only your notebooks:

```
my_project/
├── analysis.ipynb              # User notebooks (preserved)
├── exploration.ipynb           # User notebooks (preserved)
├── notebooks/                  # User directories (preserved)
│   └── data_viz.ipynb
└── .gitignore*                 # Preserved if marker removed

* .gitignore remains only if you removed the ### NOTELLM_GITIGNORE ### marker
```

**Result:** A fresh directory with notebooks only. Run `notellm start` to recreate the notellm environment from scratch.

---

**Key Differences:**

| Command | Use Case | What Stays |
|---------|----------|------------|
| `notellm clean` | Temporary cleanup, server restart issues | Everything except runtime files (.jupyter.pid, .jupyter.log, etc.) |
| `notellm clean --purge` | Complete removal, start fresh | User notebooks only |

**Common workflows:**

```bash
# Restart with clean slate (keeps all config)
notellm stop
notellm clean
notellm start

# Complete reset (rebuild everything)
notellm stop
notellm clean --purge
notellm start                   # Rebuilds .venv, reinstalls dependencies
```

### `notellm new`

Create a new notebook with boilerplate.

```bash
notellm new analysis                    # ./analysis.ipynb (current directory)
notellm new notebooks/my_analysis       # notebooks/my_analysis.ipynb (creates dir if needed)
notellm new data/exploration --open     # data/exploration.ipynb and open in browser
```

**Path handling:**
- Simple filename: Creates in current directory
- `path/filename`: Creates in path (creates directory if doesn't exist)
- Must be relative paths within current directory (no `..` or absolute paths)
- Can overwrite existing files
- Never deletes directories

**Why the restriction?** JupyterLab server runs with `--notebook-dir=.` and only has access to the current directory and subdirectories.

**Template customization:**

Notebooks are created from `.notellm_template.ipynb` (hidden file in project root). Customize this template to change the default notebook structure.

**Default template includes:**
- Title (derived from filename) and date
- Imports: polars, pandas, numpy, altair, matplotlib, seaborn
- Configuration: pandas, polars, matplotlib settings
- Magic commands: `%load_ext notellm_magic`

### `notellm update`

Update to the latest version.

```bash
notellm update
```

### `notellm help`

Show help for any command.

```bash
notellm help
notellm start --help
notellm stop --help
notellm new --help
```

## Technical Details

### Automatic cc_jupyter Patches

Patches are applied automatically when running `notellm start`. The patcher (`src/patch_jupyter_magic.sh`) fixes known issues with the `claude-code-jupyter-staging` library:

#### PATCH 1: Permission Error Fix

**Issue:** `PermissionError` when cc_jupyter checks if `/root/code` directory exists on some systems.

**Target file:** `.venv/lib/python*/site-packages/cc_jupyter/magics.py`

**Fix:** Wraps `remote_dev_monorepo_root.exists()` in a try-except block to catch `PermissionError` and `OSError`.

**Original code:**
```python
if remote_dev_monorepo_root.exists():
    options.cwd = str(remote_dev_monorepo_root)
```

**Patched code:**
```python
try:
    if remote_dev_monorepo_root.exists():
        options.cwd = str(remote_dev_monorepo_root)
except (PermissionError, OSError):
    pass
```

#### PATCH 2: Remove Decorative Headers

**Issue:** `%cc` magic command generates cells with decorative ASCII box headers that clutter the notebook.

**Target file:** `.venv/lib/python*/site-packages/cc_jupyter/jupyter_integration.py`

**Fix:** Removes decorative header generation logic and uses original code as-is.

**Original behavior:**
```python
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        CLAUDE GENERATED CELL [id: abc123]                  ║
# ╚════════════════════════════════════════════════════════════════════════════╝

# Your generated code here
```

**Patched behavior:**
```python
# Your generated code here (no decorative header)
```

#### Manual Patch Execution

If needed, you can manually run patches:

```bash
src/patch_jupyter_magic.sh
```

The patcher:
- Creates timestamped backups before modifying files
- Checks if patches are already applied (idempotent)
- Reports success/failure for each patch
- Can be safely re-run

### Cell Duplication Bug Fix

**Issue:** JupyterLab's Real-Time Collaboration (RTC) feature can cause excessive cell duplication when using Claude magic commands.

**Bug report:** [jupyterlab/jupyterlab#15544](https://github.com/jupyterlab/jupyterlab/issues/15544)

**Fix:** notellm disables RTC by default when starting JupyterLab:

```bash
jupyter lab --YDocExtension.disable_rtc=True
```

This prevents the cell duplication issue while maintaining all other JupyterLab functionality.

**Impact:** Real-time collaboration between multiple users editing the same notebook is disabled, but single-user workflows (the primary use case for notellm) are unaffected.

### JupyterLab Version Pinning

**Version Pinned:** `jupyterlab==4.0.9`

**Issue:** iPad Pro users experience an extra line bug when entering text within a cell. After pressing Shift-Return to execute a cell, JupyterLab 4.2+ adds an unwanted newline into the cell before execution, whereas version 4.0.9 executes the cell without adding the extra line.

**Related Issues:**
- [Configure Shift-Return to only Execute a Code Cell and Not Enter a new line](https://discourse.jupyter.org/t/configure-shift-return-to-only-execute-a-code-cell-and-not-enter-a-new-line-into-the-cell/25608) - Jupyter Discourse (May 2024)
- iPad keyboard input handling has general compatibility issues in JupyterLab 4.2+

**For non-iPad users:** If you don't experience this issue, you can change the version constraint in `pyproject.toml`:

```toml
"jupyterlab>=4.2",  # Instead of jupyterlab==4.0.9
```

Then run `uv sync` to upgrade to the latest version.

## Dependencies

Workspaces include these Python packages:

| Package | Purpose |
|---------|---------|
| polars | Fast DataFrames |
| pandas | DataFrames (compatibility) |
| numpy | Numerical computing |
| altair | Declarative visualization |
| matplotlib | Plotting |
| seaborn | Statistical visualization |
| jupyterlab | Notebook interface |
| jupyter-collaboration | Real-time collaboration support |
| claude-code-jupyter-staging | Claude Magic Commands |

## Uninstall

```bash
# From the cloned repo
./uninstall.sh

# Or manually
rm -rf ~/.local/share/notellm
rm -f ~/.local/bin/notellm
```

This removes the tool itself. Project files created with `notellm init` remain in their directories.

## License

MIT License — see [LICENSE](LICENSE)

## Author

C. Bryan Daniels

---

*Built for AI-assisted data science with Claude*
