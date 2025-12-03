# notellm

A command-line tool for creating Jupyter + Claude Code workspaces optimized for AI-assisted data science.

**notellm** sets up everything you need to work with JupyterLab and Claude Code side-by-side:
- JupyterLab with MCP server integration (Claude can read/write notebooks)
- Claude magic commands (`%🎷`) for in-notebook prompts
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

# 2. Initialize workspace
notellm init

# 3. Start JupyterLab
notellm start

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
%🎷 Create a histogram of the 'price' column

# Multi-line
%%🎷
Group by category
Calculate mean and median
Create a comparison bar chart
```

## Commands

### `notellm init`

Initialize a new workspace in the current directory.

```bash
notellm init                    # Use defaults (port 9999, auto token)
notellm init --port 8888        # Custom port
notellm init --token mysecret   # Custom token
```

Creates:
- `pyproject.toml` — Python dependencies
- `CLAUDE.md` — Instructions for Claude Code
- `.mcp.json` — MCP server configuration
- `.env.jupyter` — Port and token config
- `notebooks/`, `data/`, `src/`, `figures/` directories

### `notellm start`

Start the JupyterLab server.

```bash
notellm start              # Run in background
notellm start --foreground # Run in foreground (Ctrl+C to stop)
```

### `notellm stop`

Stop the JupyterLab server.

```bash
notellm stop           # Graceful shutdown
notellm stop --force   # Force kill if needed
notellm stop --clean   # Also remove log files
```

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
notellm init --help
notellm new --help
```

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
