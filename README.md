# notellm

A streamlined development environment for iterative notebook development combining:
- Jupyter notebooks for interactive data science
- Claude Code for AI-assisted development
- Work directly in notebooks with `%cc` magic for AI assistance and `%%nb_modify` for iterative code refinement
- Built-in notebook helpers for cell organization and management

**New workflow:** Develop iteratively within notebooks using magic commands—no external MCP server required.

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

### 2. Patch cc_jupyter

```bash
./patch_jupyter_magic.sh
```

This fixes permission errors and improves the notebook experience.

### 3. Open JupyterLab

The server URL will be displayed. Open it in your browser (typically `http://localhost:9999`).

### 4. Create a notebook

```bash
notellm new exploration
```

### 5. Load magic commands

In your first notebook cell:

```python
# Load Claude Code magic
%load_ext cc_jupyter

# Load notebook helpers for iterative development
import sys
sys.path.insert(0, "..")
%load_ext src.cc_notebook_helpers
```

### 6. Iterative Development Workflow

**Generate initial code with %cc:**

```python
%cc Create a function to calculate fibonacci numbers with memoization
```

Claude will create a new cell with the fibonacci function.

**Refine code iteratively with %%nb_modify:**

Copy the generated function to a new cell and modify it:

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

```python
%%nb_modify make it iterative instead of recursive
# [paste the improved function from the previous cell]
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

**Creates (on first run):**
- `pyproject.toml` — Python dependencies
- `CLAUDE.md` — Instructions for Claude Code
- `.claude/settings.json` — Claude Code permissions
- `.env.jupyter` — Port and token config
- `src/` — Notebook helper utilities
- `patch_jupyter_magic.sh` — Patch script for cc_jupyter fixes (run after first install)
- `notebooks/`, `data/`, `figures/` directories

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
- Removes: `.env.jupyter`, `.jupyter.pid`, `.jupyter.log`
- Refuses to clean if server is running (run `notellm stop` first)
- Preserves all user files and directories

**With --purge:**
- Also removes: `.venv/`, `uv.lock`, `pyproject.toml`, `CLAUDE.md`, `.jupyter_ystore.db`, and any other `.jupyter*` files
- Requires confirmation before proceeding
- Use when you want to completely reset the workspace

**Always preserved:**
- User directories: `notebooks/`, `data/`, `src/`, `figures/`
- Jupyter notebooks: All `*.ipynb` files
- Any other user-created files

### `notellm new`

Create a new notebook with boilerplate.

```bash
notellm new my_analysis              # notebooks/my_analysis.ipynb
notellm new exploration --dir .      # ./exploration.ipynb
notellm new data_viz --open          # Create and open in browser
```

Each notebook includes:
- Title (derived from filename)
- Imports: polars, pandas, numpy, altair, matplotlib, seaborn
- Configuration: display options, paths
- Claude Magic Commands placeholder

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

## Patching cc_jupyter

After running `notellm start` for the first time, run the patch script to fix known issues:

```bash
./patch_jupyter_magic.sh
```

**What it fixes:**
- **Permission errors**: Prevents `PermissionError` when checking `/root/code` on some systems
- **Clean output**: Removes decorative box headers from `%cc` magic-generated cells

**When to run:**
- After first `notellm start` in a new project
- After updating Python dependencies (`uv sync`)
- If you encounter permission errors or unwanted cell decorations

The script automatically:
- Locates your `.venv` installation
- Creates backups before patching (`.backup` files)
- Checks if patches are already applied (won't re-apply)
- Can be extended with additional patches in the future

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

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (installed automatically if missing)
- [Claude Code](https://claude.ai/code) CLI

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
