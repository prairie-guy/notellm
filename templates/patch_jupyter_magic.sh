#!/usr/bin/env bash
set -euo pipefail

#######################################
# Modular cc_jupyter Patcher
# Add new patches by creating new patch_xxx() functions
#######################################

VERSION="3.1.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "cc_jupyter Modular Patcher v${VERSION}"
echo "======================================="
echo ""

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

    echo -e "${BLUE}[PATCH 1]${NC} Permission Error Fix"

    if [ ! -f "$magics_file" ]; then
        echo -e "${RED}  ✗ SKIP${NC} - magics.py not found"
        return 1
    fi

    # Check if already patched
    if grep -q "except (PermissionError, OSError):" "$magics_file"; then
        echo -e "${GREEN}  ✓ SKIP${NC} - Already applied"
        return 0
    fi

    echo -e "${YELLOW}  → Applying...${NC}"

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
        echo -e "${GREEN}  ✓ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}  ✗ FAILED${NC} - Could not find target code"
        return 1
    fi
}

#######################################
# PATCH 2: Remove Decorative Headers
#######################################
patch_decorative_headers() {
    local cc_jupyter_path="$1"
    local jupyter_integration_file="$cc_jupyter_path/jupyter_integration.py"

    echo -e "${BLUE}[PATCH 2]${NC} Remove Decorative Headers"

    if [ ! -f "$jupyter_integration_file" ]; then
        echo -e "${RED}  ✗ SKIP${NC} - jupyter_integration.py not found"
        return 1
    fi

    # Check if already patched
    if grep -q "# No decorative header - use original code as-is" "$jupyter_integration_file"; then
        echo -e "${GREEN}  ✓ SKIP${NC} - Already applied"
        return 0
    fi

    echo -e "${YELLOW}  → Applying...${NC}"

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
        echo -e "${GREEN}  ✓ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}  ✗ FAILED${NC} - Could not find target code"
        return 1
    fi
}

#######################################
# PATCH 4: Set Working Directory from MCP Config Location
#######################################
patch_cwd_from_mcp_config() {
    local cc_jupyter_path="$1"
    local magics_file="$cc_jupyter_path/magics.py"

    echo -e "${BLUE}[PATCH 4]${NC} Set Working Directory from MCP Config Location"

    if [ ! -f "$magics_file" ]; then
        echo -e "${RED}  ✗ SKIP${NC} - magics.py not found"
        return 1
    fi

    # Check if already patched (look for the explicit settings path code)
    if grep -q "settings_local_path = project_root" "$magics_file"; then
        echo -e "${GREEN}  ✓ SKIP${NC} - Already applied"
        return 0
    fi

    echo -e "${YELLOW}  → Applying...${NC}"

    # Create backup
    cp "$magics_file" "${magics_file}.backup.$(date +%Y%m%d_%H%M%S)"

    # Apply patch using Python
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

    # Find where we need to add the import (after other imports, before class definition)
    if 'from .prompt_builder import PromptBuilder, get_system_prompt' in line:
        new_lines.append(line)
        # Check if Path is already imported
        if i + 1 < len(lines) and 'from pathlib import Path' not in ''.join(lines[:i+1]):
            # Add Path import if not already there
            new_lines.append('from pathlib import Path\n')
        i += 1
        continue

    # Find the section where remote_dev cwd setting happens
    if 'remote_dev_monorepo_root = Path("/root/code")' in line:
        # Get the indentation
        indent = len(line) - len(line.lstrip())
        base_indent = ' ' * indent

        # Add the patch before the remote dev logic
        new_lines.append(f"{base_indent}# PATCH: Set cwd from MCP config file location\n")
        new_lines.append(f"{base_indent}# This ensures Claude SDK can find .claude/settings.local.json\n")
        new_lines.append(f"{base_indent}if self._config_manager.mcp_config_file:\n")
        new_lines.append(f"{base_indent}    project_root = Path(self._config_manager.mcp_config_file).parent\n")
        new_lines.append(f"{base_indent}    options.cwd = str(project_root)\n")
        new_lines.append(f"{base_indent}    \n")
        new_lines.append(f"{base_indent}    # Always pass settings file path (overrides any JSON)\n")
        new_lines.append(f"{base_indent}    settings_local_path = project_root / \".claude\" / \"settings.local.json\"\n")
        new_lines.append(f"{base_indent}    if settings_local_path.exists():\n")
        new_lines.append(f"{base_indent}        options.settings = str(settings_local_path)\n")
        new_lines.append(f"{base_indent}\n")
        new_lines.append(f"{base_indent}# Original remote dev logic (kept for compatibility)\n")
        new_lines.append(line)

        patched = True
        i += 1
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
        echo -e "${GREEN}  ✓ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}  ✗ FAILED${NC} - Could not find target code"
        return 1
    fi
}

#######################################
# Main Execution
#######################################

#######################################
# PATCH 5: Rename SDK Server to Avoid Conflict
#######################################
patch_rename_sdk_server() {
    local cc_jupyter_path="$1"
    local magics_file="$cc_jupyter_path/magics.py"
    local constants_file="$cc_jupyter_path/constants.py"

    echo -e "${BLUE}[PATCH 5]${NC} Rename SDK Server to Avoid Conflict"

    if [ ! -f "$magics_file" ] || [ ! -f "$constants_file" ]; then
        echo -e "${RED}  ✗ SKIP${NC} - Required files not found"
        return 1
    fi

    # Check if already patched
    if grep -q 'mcp__jupyter_executor__create_python_cell' "$constants_file"; then
        echo -e "${GREEN}  ✓ SKIP${NC} - Already applied"
        return 0
    fi

    echo -e "${YELLOW}  → Applying...${NC}"

    # Create backups
    cp "$magics_file" "${magics_file}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$constants_file" "${constants_file}.backup.$(date +%Y%m%d_%H%M%S)"

    # Patch constants.py - change tool name constant
    sed -i 's/EXECUTE_PYTHON_TOOL_NAME = "mcp__jupyter__create_python_cell"/EXECUTE_PYTHON_TOOL_NAME = "mcp__jupyter_executor__create_python_cell"/' "$constants_file"

    # Patch magics.py - change server name in mcp_servers dict
    sed -i 's/"jupyter": sdk_server/"jupyter_executor": sdk_server/' "$magics_file"

    # Patch magics.py - change tool name in allowed_tools list
    sed -i 's/"mcp__jupyter__create_python_cell"/"mcp__jupyter_executor__create_python_cell"/' "$magics_file"

    # Verify patches
    if grep -q 'mcp__jupyter_executor__create_python_cell' "$constants_file" && \
       grep -q '"jupyter_executor": sdk_server' "$magics_file" && \
       grep -q '"mcp__jupyter_executor__create_python_cell"' "$magics_file"; then
        echo -e "${GREEN}  ✓ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}  ✗ FAILED${NC} - Verification failed"
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

echo -e "${GREEN}Found cc_jupyter:${NC} $CC_JUPYTER_PATH"
echo ""

# Array of patch functions to run
PATCH_FUNCTIONS=(
    "patch_permission_error"
    "patch_decorative_headers"
    "patch_cwd_from_mcp_config"
    "patch_rename_sdk_server"
    # Add new patches here:
    # "patch_another_fix"
)

# Run all patches
PATCHES_APPLIED=0
PATCHES_SKIPPED=0
PATCHES_FAILED=0

for patch_func in "${PATCH_FUNCTIONS[@]}"; do
    if $patch_func "$CC_JUPYTER_PATH"; then
        # Check if it was skipped (already applied) or newly applied
        if grep -q "SKIP" <<< "$($patch_func "$CC_JUPYTER_PATH" 2>&1 | head -1)"; then
            ((PATCHES_SKIPPED++)) || true
        else
            ((PATCHES_APPLIED++)) || true
        fi
    else
        ((PATCHES_FAILED++)) || true
    fi
    echo ""
done

# Summary
echo "======================================="
if [ $PATCHES_APPLIED -gt 0 ]; then
    echo -e "${GREEN}✓ $PATCHES_APPLIED patch(es) applied${NC}"
fi
if [ $PATCHES_SKIPPED -gt 0 ]; then
    echo -e "${YELLOW}→ $PATCHES_SKIPPED patch(es) skipped (already applied)${NC}"
fi
if [ $PATCHES_FAILED -gt 0 ]; then
    echo -e "${RED}✗ $PATCHES_FAILED patch(es) failed${NC}"
fi
echo ""

if [ $PATCHES_FAILED -eq 0 ]; then
    echo "Ready to test! Run in Jupyter:"
    echo "  %cc write factorial function"
    exit 0
else
    echo -e "${RED}Some patches failed. Check output above.${NC}"
    exit 1
fi
