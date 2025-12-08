#!/usr/bin/env bash
set -euo pipefail

#######################################
# Modular cc_jupyter Patcher
# Add new patches by creating new patch_xxx() functions
#######################################

VERSION="4.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Silent mode - only show output on first run or errors

# Find cc_jupyter installation
find_cc_jupyter() {
    if [ -d ".venv/lib" ]; then
        find .venv/lib -type d -name "cc_jupyter" 2>/dev/null | head -n 1
    fi
}

#######################################
# PATCH 1: Fix Permission Error
#######################################
patch_permission_error() {
    local cc_jupyter_path="$1"
    local magics_file="$cc_jupyter_path/magics.py"

    if [ ! -f "$magics_file" ]; then
        echo -e "${RED}[PATCH 1] SKIP - magics.py not found${NC}"
        return 1
    fi

    # Check if already patched
    if grep -q "except (PermissionError, OSError):" "$magics_file"; then
        return 0  # Already applied, silent
    fi

    echo "[PATCH 1] Applying Permission Error Fix..."

    # Create backup
    cp "$magics_file" "${magics_file}.backup.$(date +%Y%m%d_%H%M%S)"

    # Apply patch
    export MAGICS_FILE="$magics_file"
    python3 << 'PYTHON_SCRIPT'
import os

magics_file = os.environ['MAGICS_FILE']

with open(magics_file, 'r') as f:
    lines = f.readlines()

patched = False
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Find the target line that causes permission error
    if 'if remote_dev_monorepo_root.exists():' in line and i + 1 < len(lines):
        indent = len(line) - len(line.lstrip())
        base_indent = ' ' * indent
        inner_indent = ' ' * (indent + 4)

        # Replace 2-line block with try-except wrapper
        new_lines.append(f"{base_indent}try:\n")
        new_lines.append(f"{inner_indent}if remote_dev_monorepo_root.exists():\n")
        new_lines.append(f"{inner_indent}    options.cwd = str(remote_dev_monorepo_root)\n")
        new_lines.append(f"{base_indent}except (PermissionError, OSError):\n")
        new_lines.append(f"{inner_indent}pass\n")

        i += 2  # Skip the next line (options.cwd = ...)
        patched = True
        continue

    new_lines.append(line)
    i += 1

if patched:
    with open(magics_file, 'w') as f:
        f.writelines(new_lines)
    exit(0)
else:
    exit(1)
PYTHON_SCRIPT

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Applied${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED - Could not find target code${NC}"
        return 1
    fi
}

#######################################
# PATCH 2: Remove Decorative Headers
#######################################
patch_decorative_headers() {
    local cc_jupyter_path="$1"
    local jupyter_integration_file="$cc_jupyter_path/jupyter_integration.py"

    if [ ! -f "$jupyter_integration_file" ]; then
        echo -e "${RED}[PATCH 2] SKIP - jupyter_integration.py not found${NC}"
        return 1
    fi

    # Check if already patched
    if grep -q "# No decorative header - use original code as-is" "$jupyter_integration_file"; then
        return 0  # Already applied, silent
    fi

    echo "[PATCH 2] Removing Decorative Headers..."

    # Create backup
    cp "$jupyter_integration_file" "${jupyter_integration_file}.backup.$(date +%Y%m%d_%H%M%S)"

    # Apply patch
    export JUPYTER_INTEGRATION_FILE="$jupyter_integration_file"
    python3 << 'PYTHON_SCRIPT'
import os

jupyter_file = os.environ['JUPYTER_INTEGRATION_FILE']

with open(jupyter_file, 'r') as f:
    lines = f.readlines()

patched = False
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Find the start of the decorative header block
    if 'generated_cell_message = (' in line:
        # Get the indentation
        indent = len(line) - len(line.lstrip())
        base_indent = ' ' * indent

        # Find the end of the block (cell_info["marker"] = marker)
        j = i
        while j < len(lines):
            if 'cell_info["marker"] = marker' in lines[j]:
                # Found the end - replace entire block with simple version
                new_lines.append(f"{base_indent}# No decorative header - use original code as-is\n")
                new_lines.append(f"{base_indent}marked_code = original_code\n")
                new_lines.append(f"{base_indent}cell_info[\"code\"] = marked_code\n")
                new_lines.append(f"{base_indent}cell_info[\"marker\"] = \"\"\n")

                i = j + 1  # Skip past the end line
                patched = True
                break
            j += 1

        if patched:
            continue

    new_lines.append(line)
    i += 1

if patched:
    with open(jupyter_file, 'w') as f:
        f.writelines(new_lines)
    exit(0)
else:
    exit(1)
PYTHON_SCRIPT

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Applied${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED - Could not find target code${NC}"
        return 1
    fi
}


#######################################
# Main Script
#######################################

# Find cc_jupyter
CC_JUPYTER_PATH=$(find_cc_jupyter)

if [ -z "$CC_JUPYTER_PATH" ]; then
    echo -e "${RED}ERROR:${NC} cc_jupyter not found in .venv/lib"
    echo ""
    echo "Make sure you have cc_jupyter installed:"
    echo "  uv venv"
    echo "  uv pip install claude-code-jupyter-staging"
    exit 1
fi

# Found cc_jupyter (silent unless error)

# Array of patch functions to run
PATCH_FUNCTIONS=(
    "patch_permission_error"
    "patch_decorative_headers"
    # Removed PATCH 4 (MCP config) and PATCH 5 (server renaming) - no longer needed
    # Add new patches here:
    # "patch_another_fix"
)

# Run all patches
PATCHES_APPLIED=0
PATCHES_SKIPPED=0
PATCHES_FAILED=0

for patch_func in "${PATCH_FUNCTIONS[@]}"; do
    $patch_func "$CC_JUPYTER_PATH"
    result=$?
    if [ $result -eq 0 ]; then
        ((PATCHES_APPLIED++)) || true
    else
        ((PATCHES_FAILED++)) || true
    fi
done

# Only show summary if patches were applied or failed
if [ $PATCHES_APPLIED -gt 0 ]; then
    echo -e "${GREEN}✓ cc_jupyter patches applied${NC}"
elif [ $PATCHES_FAILED -gt 0 ]; then
    echo -e "${RED}✗ Patch application failed${NC}"
    exit 1
fi

exit 0
