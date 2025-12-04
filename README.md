# notellm
 
A command-line tool for creating Jupyter + Claude Code workspaces optimized for AI-assisted data science.

**notellm** sets up everything you need to work with JupyterLab and Claude Code side-by-side:
- JupyterLab with MCP server integration (Claude can read/write notebooks)
- Claude magic commands (`%cc`) for in-notebook prompts
- Notebook templates with sensible defaults (polars, altair, etc.)
- Simple commands to start, stop, and manage your workspace

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

```bash
# 1. Create a new project
mkdir ~/my-analysis && cd ~/my-analysis

# 2. Start JupyterLab (auto-initializes workspace)
notellm start

# 3. Patch cc_jupyter (fixes permission errors and removes decorative headers)
./patch_jupyter_magic.sh

# 4. Create a notebook
notellm new exploration

# 5. Start Claude Code (in another terminal)
claude

# 6. When done
notellm stop
```

## Workflow

Split your screen:
- **Left half:** JupyterLab in browser
- **Right half:** Claude Code in terminal

### From Claude Code

Claude can read and manipulate your notebooks via MCP:

```
> use the notebook notebooks/exploration.ipynb
> read all cells with outputs
> add a code cell that creates a scatter plot of price vs quantity
> read cell 5 with outputs and suggest improvements
```

### From Notebook Cells

Use the Claude magic for quick prompts:

```python
%load_ext cc_jupyter

# Single line
%cc Create a histogram of the 'price' column

# Multi-line
%%cc
Group by category
Calculate mean and median
Create a comparison bar chart
```

## Claude Magic Commands

The `cc_jupyter` extension provides full Claude Code integration within Jupyter notebooks:

**Features:**
- Full agentic Claude Code execution
- Cell-based code approval workflow
- Real-time message streaming
- Session state preservation
- Conversation continuity across cells

**Basic Usage:**
```python
%cc <instructions>       # Continue with additional instructions (one-line)
%%cc <instructions>      # Continue with additional instructions (multi-line)
%cc_new (or %ccn)        # Start fresh conversation
%cc --help               # Show available options and usage information
```

**Context Management:**
```python
%cc --import <file>       # Add a file to be included in initial conversation messages
%cc --add-dir <dir>       # Add a directory to Claude's accessible directories
%cc --mcp-config <file>   # Set path to a .mcp.json file containing MCP server configurations
%cc --cells-to-load <num> # The number of cells to load into a new conversation (default: all for first %cc, none for %cc_new)
```

**Output:**
```python
%cc --model <name>       # Model to use for Claude Code (default: sonnet)
%cc --max-cells <num>    # Set the maximum number of cells CC can create per turn (default: 3)
```

**Display:**
```python
%cc --clean              # Replace prompt cells with Claude's code cells (tell us if you like this feature, maybe it should be the default)
%cc --no-clean           # Turn off the above setting (default)
```

**When to use each form:**
- Use `%cc` (single %) for short, one-line instructions
- Use `%%cc` (double %) for multi-line instructions or detailed prompts

**Notes:**
- Restart the kernel to stop the Claude session
- Documentation: go/claude-code-jupyter

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
- Always keeps `.mcp.json` in sync with running server

**Creates (on first run):**
- `pyproject.toml` — Python dependencies
- `CLAUDE.md` — Instructions for Claude Code
- `.mcp.json` — MCP server configuration
- `.env.jupyter` — Port and token config
- `patch_jupyter_magic.sh` — Patch script for cc_jupyter fixes (run after first install)
- `notebooks/`, `data/`, `src/`, `figures/` directories

### `notellm stop`

Stop the JupyterLab server.

```bash
notellm stop              # Stop all processes on configured port
notellm stop --port 8888  # Stop all processes on port 8888
```

**Behavior:**
- Finds all processes using the specified port (or configured port from `.env.jupyter`)
- Sends SIGTERM for graceful shutdown (waits up to 30 seconds)
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
- Removes: `.env.jupyter`, `.mcp.json`, `.jupyter.pid`, `.jupyter.log`
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
- Claude magic placeholder

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
| jupyter-collaboration | Real-time collaboration (MCP) |
| claude-code-jupyter-staging | Claude magic commands |

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
