# notellm

Lightweight Jupyter magic extension for Claude Code integration.

Fork of [claude-code-jupyter-staging](https://pypi.org/project/claude-code-jupyter-staging/) (MIT License, Anthropic).

## Demo

[View demo notebook](https://nbviewer.org/github/prairie-guy/notellm/blob/main/docs/demo.ipynb)

## Installation

### Prerequisites

1. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code):
```bash
npm install -g @anthropic-ai/claude-code
```

2. Install Python dependencies (pip only):
```bash
pip install trio claude-agent-sdk
```
(tested with trio==0.24.0, claude-agent-sdk==0.1.18)

**Note:** Use pip for these dependencies. The `claude-agent-sdk` package is only available on PyPI, not conda-forge.

### Install notellm_magic

```bash
./setup.sh
```

This copies `notellm_magic/` to your user site-packages.

### Uninstall

```bash
./uninstall.sh
```

## Usage

In a Jupyter notebook:

```python
%load_ext notellm_magic
```

On first load in a directory, notellm creates `.claude/settings.local.json` with default permissions:

```
Created .claude/settings.local.json
  (Permissions: Bash, Glob, Grep, Read, Edit, Write, WebSearch, WebFetch)
```

Then you'll see:

```
Claude Code Magic loaded!
Features:
  • Full agentic Claude Code execution
  • Cell-based code approval workflow
  • Real-time message streaming
  • Session state preservation
  • Conversation continuity across cells
```

### Permissions

The auto-created `.claude/settings.local.json` grants Claude access to:
- **Bash** - Run shell commands
- **Glob** - Find files by pattern
- **Grep** - Search file contents
- **Read** - Read files
- **Edit** - Modify files
- **Write** - Create files
- **WebSearch** - Search the web
- **WebFetch** - Fetch web content

To customize, edit `.claude/settings.local.json` in your project directory.

### Basic Usage

```python
%cc Create a hello world script
```

Or multi-line:

```python
%%cc
Create a function that calculates fibonacci numbers
Use memoization for efficiency
```

### Magic Commands

**Basic:**
- `%cc <instructions>` - Continue conversation (one-line)
- `%%cc <instructions>` - Continue conversation (multi-line)
- `%cc_new` (or `%ccn`) - Start fresh conversation
- `%cc --help` - Show all options

**Context management:**
- `%cc --import <file>` - Add file to conversation context
- `%cc --add-dir <dir>` - Add directory to Claude's accessible directories
- `%cc --mcp-config <file>` - Set path to MCP server config
- `%cc --cells-to-load <num>` - Number of cells to load into new conversation

**Output:**
- `%cc --model <name>` - Model to use (default: sonnet)
- `%cc --max-cells <num>` - Max cells Claude can create per turn (default: 3)

**Display:**
- `%cc --clean` - Replace prompt cells with Claude's code cells
- `%cc --no-clean` - Keep prompt cells (default)

### When to use each form

- **`%cc`** (single %) - Short, one-line instructions
- **`%%cc`** (double %) - Multi-line instructions or detailed prompts

### Notes

- Restart the kernel to stop the Claude session

## Project Structure

```
notellm/
├── archive/
│   └── cc_jupyter/           # Pristine copy from PyPI
├── notellm_magic/
│   ├── __init__.py           # Thin wrapper
│   └── cc_jupyter/           # Patched fork
├── build/
│   └── build_notellm_magic.sh
├── setup.sh
├── uninstall.sh
├── LICENSE
└── README.md
```

## Development

### Rebuilding from archive

If you update `archive/cc_jupyter/` with a new upstream version:

```bash
./build/build_notellm_magic.sh
```

This copies the archive to `notellm_magic/cc_jupyter/` and applies patches.

### Patches Applied

1. **Permission error fix** (`magics.py`) - Wraps `/root/code` check in try/except
2. **Decorative header removal** (`jupyter_integration.py`) - Removes banner comments from generated cells

## Attribution

This project is a fork of `claude-code-jupyter-staging` by Anthropic, released under the MIT License.

See [LICENSE](LICENSE) for details.
