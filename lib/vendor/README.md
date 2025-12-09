# Vendored Dependencies

This directory contains archived copies of dependencies that are under active development and may break in future releases.

## claude-code-jupyter-staging-0.0.1

**Archived:** 2024-12-08
**Reason:** Package is in active development (staging release), future versions may introduce breaking changes
**Original source:** https://pypi.org/project/claude-code-jupyter-staging/

### To Install from Wheel

If the package is no longer available on PyPI or a newer version breaks compatibility:

```bash
# Using uv (preferred)
uv pip install lib/vendor/claude_code_jupyter_staging-0.0.1-py3-none-any.whl

# Using pip
pip install lib/vendor/claude_code_jupyter_staging-0.0.1-py3-none-any.whl
```

### Wheel Details

- **File:** `claude_code_jupyter_staging-0.0.1-py3-none-any.whl`
- **Size:** 32 KB
- **Python:** 3.x (any version)
- **Platform:** Any (pure Python, no compiled extensions)
- **ABI:** None (no binary interface dependencies)

### Current Usage

The version is pinned in `templates/pyproject.toml`:

```toml
dependencies = [
    "claude-code-jupyter-staging==0.0.1",
    # ...
]
```

This ensures consistent behavior across installations while the wheel serves as a backup if the package is removed from PyPI.
