# Build Scripts

## build_notellm_magic.sh

Builds the `notellm_magic/cc_jupyter/` module from the pristine archive.

### What it does

1. Copies `archive/cc_jupyter/` to `notellm_magic/cc_jupyter/`
2. Applies Patch 1: Permission error fix in `magics.py`
3. Applies Patch 2: Decorative header removal in `jupyter_integration.py`

### When to run

- After updating `archive/cc_jupyter/` with a new upstream version
- After modifying patch logic

### Usage

```bash
./build/build_notellm_magic.sh
```

## Patches

### Patch 1: Permission Error Fix

**File:** `magics.py`

The original code checks if `/root/code` exists (for Anthropic's internal remote dev setup), but this throws `PermissionError` on regular user systems.

**Fix:** Wrap the check in a try/except block.

### Patch 2: Decorative Header Removal

**File:** `jupyter_integration.py`

The original code adds decorative `═══` banner comments to every generated cell. This patch removes them for cleaner output.
