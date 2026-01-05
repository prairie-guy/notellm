#!/usr/bin/env bash
set -euo pipefail

#######################################
# notellm installation script
#######################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
RED=$'\033[0;31m'
BLUE=$'\033[0;34m'
BOLD=$'\033[1m'
NC=$'\033[0m'

echo ""
echo "${BOLD}notellm_magic Installation${NC}"
echo "=============================="
echo ""

#######################################
# Step 1: Check Python
#######################################
echo "${BLUE}[1/5]${NC} Checking Python..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}  ERROR: python3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "  Found: $PYTHON_VERSION"

#######################################
# Step 2: Check dependencies
#######################################
echo ""
echo "${BLUE}[2/5]${NC} Checking dependencies..."

missing=""

if python3 -c "import trio" 2>/dev/null; then
    TRIO_VERSION=$(python3 -c "import trio; print(trio.__version__)" 2>/dev/null || echo "unknown")
    echo "  trio: ${GREEN}installed${NC} (v$TRIO_VERSION)"
else
    echo "  trio: ${YELLOW}not found${NC}"
    missing="$missing trio"
fi

if python3 -c "import claude_agent_sdk" 2>/dev/null; then
    SDK_VERSION=$(python3 -c "import claude_agent_sdk; print(getattr(claude_agent_sdk, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "  claude-agent-sdk: ${GREEN}installed${NC} (v$SDK_VERSION)"
else
    echo "  claude-agent-sdk: ${YELLOW}not found${NC}"
    missing="$missing claude-agent-sdk"
fi

if [ -n "$missing" ]; then
    echo ""
    echo "=============================="
    echo -e "${RED}Installation aborted!${NC}"
    echo "=============================="
    echo ""
    echo -e "${RED}Missing dependencies:$missing${NC}"
    echo ""
    echo "To fix, run:"
    echo "  pip install trio claude-agent-sdk"
    echo ""
    echo "(tested with trio==0.24.0, claude-agent-sdk==0.1.18)"
    echo ""
    echo "Then re-run:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

#######################################
# Step 3: Determine install location
#######################################
echo ""
echo "${BLUE}[3/5]${NC} Determining install location..."

USER_SITE=$(python3 -c "import site; print(site.USER_SITE)")
echo "  Target: $USER_SITE/notellm_magic/"

#######################################
# Step 4: Remove existing installation
#######################################
echo ""
echo "${BLUE}[4/5]${NC} Checking for existing installation..."

if [ -d "$USER_SITE/notellm_magic" ]; then
    echo "  Found existing installation, removing..."
    rm -rf "$USER_SITE/notellm_magic"
    echo "  Removed: $USER_SITE/notellm_magic/"
else
    echo "  No existing installation found"
fi

#######################################
# Step 5: Install
#######################################
echo ""
echo "${BLUE}[5/5]${NC} Installing notellm_magic..."

# Ensure target directory exists
if [ ! -d "$USER_SITE" ]; then
    echo "  Creating: $USER_SITE/"
    mkdir -p "$USER_SITE"
fi

# Copy module
cp -r "$SCRIPT_DIR/notellm_magic" "$USER_SITE/"

# Verify installation
if [ -d "$USER_SITE/notellm_magic" ]; then
    FILE_COUNT=$(find "$USER_SITE/notellm_magic" -type f -name "*.py" | wc -l)
    echo "  Copied: $FILE_COUNT Python files"
    echo -e "  ${GREEN}Installed to: $USER_SITE/notellm_magic/${NC}"
else
    echo -e "${RED}  ERROR: Installation failed${NC}"
    exit 1
fi

#######################################
# Summary
#######################################
echo ""
echo "=============================="
echo -e "${GREEN}Installation complete!${NC}"
echo "=============================="
echo ""
echo "Usage in Jupyter notebook:"
echo ""
echo "  %load_ext notellm_magic"
echo ""
echo "  %cc Create a hello world script"
echo ""
echo "  %%cc"
echo "  Your multi-line"
echo "  prompt here"
echo ""
echo "On first load, notellm creates .claude/settings.local.json"
echo "with permissions for Bash, Read, Write, Edit, WebSearch, etc."
echo ""
