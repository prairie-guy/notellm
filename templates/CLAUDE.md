# Project Configuration

## Environment

- Python 3.12 managed via `uv`
- JupyterLab running on port {{PORT}}
- Token: {{TOKEN}}

## Directory Structure

```
├── notebooks/          # Jupyter notebooks
├── data/              # Data files
├── src/               # Python modules (including notebook helpers)
├── figures/           # Saved visualizations
└── .claude/           # Claude Code settings
```

## Jupyter Notebook Workflow

### Setup Note

cc_jupyter patches are automatically applied when running `notellm start`.
These patches fix permission errors and remove decorative headers.

### In-Notebook Magic Commands

**cc_jupyter** - `%cc` and `%%cc` magic commands for Claude interactions

Load in notebook:
```python
%load_ext cc_jupyter
```

Usage:
- `%cc <prompt>` - Single-line prompt, creates new code cell with result
- `%%cc <prompt>` - Multi-line prompt with code context in cell body

Example:
```python
%%cc Create a function to calculate fibonacci numbers
Use recursion with memoization
```

### Available Tools

When using `%cc` commands, Claude Code has access to:

**Built-in Tools:**
- `Bash` - Run shell commands
- `Read` - Read files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Grep` - Search file contents
- `WebSearch` - Search the web
- `WebFetch` - Fetch web content

**Cell Creation:**
- `mcp__jupyter__create_python_cell` - Create and insert Python code cells

**Note:** This setup does NOT use the external Jupyter MCP server. All operations are streamlined through cc_jupyter and built-in tools.

## Notebook Helper Tools

### Loading Helpers

Add to notebook (usually in first cell):
```python
sys.path.append("..")
%load_ext src.cc_notebook_helpers
```

### Cell Organization Commands

These commands help navigate and organize notebook cells:

- `%nb_list` - List all cells
- `%nb_list --show-empty` - Include empty cells
- `%nb_find <query>` - Search cells by content
- `%nb_find --content <query>` - Explicit content search
- `%nb_section <header>` - Find cells under markdown header

Example workflow:
```python
# List all cells
%nb_list

# Find cells containing specific text
%nb_find load_dataset

# Find cells under a section
%nb_section ## Data Loading
```

### Iterative Code Editing

**`%%nb_modify <instruction>`** - Modify code in current cell using Claude

This is the primary tool for incremental code development within Jupyter.

Usage:
```python
%%nb_modify sort penguins by name length
df = sns.load_dataset('penguins')
species_order = sorted(df['species'].dropna().unique())
```

How it works:
1. Put `%%nb_modify` with instruction at top of cell
2. Include current code below the magic command
3. Run cell → Claude modifies the code
4. New cell appears below with modified code only (no magic command)
5. Iterate: copy magic command to new cell, run again to further refine

Benefits:
- Fast iterative development
- Stays within notebook context
- No separate terminal sessions needed
- Uses same authentication as cc_jupyter

## Commands

```bash
# Start JupyterLab
notellm start

# Create new notebook
notellm new <name>

# Stop server
notellm stop

# Clean and reinstall
notellm clean --purge
```

-----

# Coding Style Guide

## General Principles

### Layout

- Maximum line width: 160 characters
- One line of code should implement one complete idea
- If a 1-line function body fits comfortably on the same line as `def`/`function`, put them together
- No blank line between signature and first line of code
- No blank line between docstring and code
- Minimal blank lines within function bodies—use sparingly to indicate logical sections

Example:

```python
def double(x: int) -> int: return x * 2
```

### Alignment

Align conceptually similar statement parts so differences are immediately visible:

```python
if self.store.stretch_dir==0: x = stretch_cv(x, self.store.stretch, 0)
else:                         x = stretch_cv(x, 0, self.store.stretch)
```

### Naming

Follow the Huffman Coding principle: commonly used and generic concepts get shorter names.

Follow the life-cycle principle: shorter-lived symbols get shorter names.

- **Aggressive abbreviations**: list comprehensions, lambdas, temporary variables
- **Common abbreviations**: function arguments, function names, variables
- **Light/no abbreviations**: module names, class names, constructors

Common short names: `i` (index), `k`/`v` (key/value), `o` (object in comprehension), `x` (input), `n` (count), `fn` (function), `df` (dataframe), `sz` (size)

Use domain-appropriate abbreviations consistently.

### Comments

Avoid comments unless necessary to explain *why*. Use clear symbol names and expository code to show *how*.

### Code Generation Scope

Generate only what was requested. **Do not include test code, example usage, or demonstration calls unless explicitly asked.**

Let the user decide when and how to test or use the code.

### Formatting

- Do not use automatic linters or formatters
- Align conceptually similar statement parts so differences are immediately visible

-----

## Python

### Signatures

- Keep signatures on one line when under 160 characters
- Use type hints—they serve as documentation (not enforcement)

### Docstrings

- One-line docstrings for simple functions: `"""Return the sum of x and y."""`
- Parameters should be evident from type hints; don’t repeat them in docstrings

### Casing

- `CamelCase` for classes
- `snake_case` for functions, variables, modules

-----

## Julia

### Type Annotations

Omit type annotations unless needed for multiple dispatch. When annotations are required, prefer abstract types (`AbstractArray`, `Real`, `Number`) to preserve flexibility.

### Docstrings

Standard Julia docstrings (Markdown above the function with triple quotes). Use short one-line docstrings for simple functions.

-----

## Library Preferences

### Polars

Use method chaining. Surround with parentheses, one method per line, each line starting with `.`:

```python
(df.filter(pl.col("a") > 1)
    .select("a", "b")
    .sort("a"))
```

### Altair

Use method chaining, same pattern as Polars:

```python
(alt.Chart(df)
    .mark_bar()
    .encode(
        x="category",
        y="value"))
```
