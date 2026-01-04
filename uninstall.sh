#!/usr/bin/env bash
set -euo pipefail

#######################################
# notellm uninstallation script
#######################################

# Colors
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
NC=$'\033[0m'

USER_SITE=$(python3 -c "import site; print(site.USER_SITE)")
TARGET="$USER_SITE/notellm_magic"

if [ -d "$TARGET" ]; then
    rm -rf "$TARGET"
    echo -e "${GREEN}Removed $TARGET${NC}"
else
    echo -e "${YELLOW}Not installed (nothing to remove)${NC}"
fi
