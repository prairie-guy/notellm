# Project Configuration

## Environment

- Python 3.12 managed via `uv`
- JupyterLab running on port {{PORT}}
- Jupyter MCP server enabled for real-time notebook access

## Jupyter Notebook Workflow

### CRITICAL: Always Read Context First

Before generating any new cell content:

1. Use `read_cells` or `read_notebook` to understand existing notebook state
2. Use `read_cell` with `include_outputs=true` to see execution results including images/plots
3. Reference prior cells explicitly when generating dependent code

### Available Tools

**Jupyter MCP Server Tools:**
- `use_notebook` - Connect to a notebook
- `read_cells` - Read all cells with full content
- `read_cell` - Read single cell with outputs (including images)
- `insert_cell` - Add new cell at position
- `execute_cell` - Run a cell and get outputs
- `insert_execute_code_cell` - Insert and run in one step

**In-Notebook Magic:**
- User may use `%🎷` or `%%🎷` magic commands in cells
- These share state bidirectionally with the notebook kernel
- Load with: `%load_ext cc_jupyter`

### Workflow Pattern

When user asks for notebook help:

1. First: `use_notebook` to connect to the active notebook
2. Then: `read_cells` with `response_format="detailed"` to see full context
3. For specific cells with outputs: `read_cell` with `include_outputs=true`
4. Generate code that builds on existing variables and imports
5. Prefer `insert_cell` over `insert_execute_code_cell` to let user review first

### Code Style

- Use polars for dataframes (prefer over pandas unless user specifies)
- Use altair for visualizations (prefer over matplotlib unless user specifies)
- Include type hints
- Keep cells focused—one logical step per cell
- Add markdown cells to explain analysis steps

## Commands

```bash
# Start JupyterLab
notellm start

# Create new notebook
notellm new <name>

# Stop server
notellm stop
```

## Directory Structure

```
├── notebooks/          # Jupyter notebooks
├── data/              # Data files
├── src/               # Python modules
└── figures/           # Saved visualizations
```

## MCP Connection

- URL: http://localhost:{{PORT}}
- Token: {{TOKEN}}
- Image output: enabled
