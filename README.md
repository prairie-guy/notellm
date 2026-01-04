# notellm

Lightweight Jupyter magic extension for Claude Code integration.

Fork of [claude-code-jupyter-staging](https://pypi.org/project/claude-code-jupyter-staging/) (MIT License, Anthropic).

## Installation

### Prerequisites

Install dependencies in your Python environment:

```bash
pip install trio claude-code-sdk
```

(tested with trio==0.24.0, claude-code-sdk==0.1.0)

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

%%cc
Create a hello world script
```

### Magic Commands

- `%cc <prompt>` - Single-line prompt
- `%%cc` - Multi-line prompt (cell magic)
- `%cc_new <prompt>` - Start fresh conversation (no history)
- `%ccn <prompt>` - Alias for `%cc_new`

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
