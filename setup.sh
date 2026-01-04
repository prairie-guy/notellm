#!/usr/bin/env bash
set -euo pipefail

#######################################
# notellm installation script
#######################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
NC=$'\033[0m'

echo ""
echo "Installing notellm_magic..."
echo ""

# Check dependencies (warn but don't block)
missing=""
python3 -c "import trio" 2>/dev/null || missing="$missing trio"
python3 -c "import claude_agent_sdk" 2>/dev/null || missing="$missing claude-code-sdk"

if [ -n "$missing" ]; then
    echo -e "${YELLOW}Missing dependencies:$missing${NC}"
    echo "  Install with: pip install$missing"
    echo "  (tested with trio==0.24.0, claude-code-sdk==0.1.0)"
    echo ""
fi

# Install to user site-packages
USER_SITE=$(python3 -c "import site; print(site.USER_SITE)")
mkdir -p "$USER_SITE"

# Remove existing installation
if [ -d "$USER_SITE/notellm_magic" ]; then
    rm -rf "$USER_SITE/notellm_magic"
fi

# Copy module
cp -r "$SCRIPT_DIR/notellm_magic" "$USER_SITE/"

echo -e "${GREEN}Installed notellm_magic to $USER_SITE/${NC}"
echo ""
echo "Usage in Jupyter notebook:"
echo "  %load_ext notellm_magic"
echo "  %%cc"
echo "  Your prompt here"
echo ""
