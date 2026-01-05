#!/usr/bin/env bash
set -euo pipefail

#######################################
# notellm uninstallation script
#######################################

# Colors
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
RED=$'\033[0;31m'
BLUE=$'\033[0;34m'
BOLD=$'\033[1m'
NC=$'\033[0m'

echo ""
echo "${BOLD}notellm_magic Uninstallation${NC}"
echo "=============================="
echo ""

#######################################
# Step 1: Check Python
#######################################
echo "${BLUE}[1/4]${NC} Checking Python..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}  ERROR: python3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "  Found: $PYTHON_VERSION"

#######################################
# Step 2: Determine install location
#######################################
echo ""
echo "${BLUE}[2/4]${NC} Determining install location..."

USER_SITE=$(python3 -c "import site; print(site.USER_SITE)")
TARGET="$USER_SITE/notellm_magic"
echo "  Target: $TARGET/"

#######################################
# Step 3: Remove installation
#######################################
echo ""
echo "${BLUE}[3/4]${NC} Removing notellm_magic..."

if [ -d "$TARGET" ]; then
    # Count files before removal
    FILE_COUNT=$(find "$TARGET" -type f -name "*.py" | wc -l)

    rm -rf "$TARGET"

    # Verify removal
    if [ ! -d "$TARGET" ]; then
        echo "  Removed: $FILE_COUNT Python files"
        echo -e "  ${GREEN}Removed: $TARGET/${NC}"
    else
        echo -e "${RED}  ERROR: Failed to remove $TARGET${NC}"
        exit 1
    fi
else
    echo -e "  ${YELLOW}Not installed (nothing to remove)${NC}"
fi

#######################################
# Step 4: Verify cleanup
#######################################
echo ""
echo "${BLUE}[4/4]${NC} Verifying cleanup..."

FAILED=0

# Check directory is gone
if [ -d "$TARGET" ]; then
    echo -e "  ${RED}FAIL: Directory still exists: $TARGET${NC}"
    FAILED=1
else
    echo -e "  ${GREEN}OK${NC}: Directory removed"
fi

# Check module cannot be imported from site-packages
if python3 -c "import notellm_magic" 2>/dev/null; then
    FOUND_AT=$(python3 -c "import notellm_magic; print(notellm_magic.__file__)" 2>/dev/null || echo "unknown location")
    # Check if it's the local source (not installed copy)
    if [[ "$FOUND_AT" == *"site-packages"* ]]; then
        echo -e "  ${RED}FAIL: Module still importable from: $FOUND_AT${NC}"
        FAILED=1
    else
        echo -e "  ${GREEN}OK${NC}: Module not in site-packages (local source at: $FOUND_AT)"
    fi
else
    echo -e "  ${GREEN}OK${NC}: Module not importable"
fi

#######################################
# Summary
#######################################
echo ""
echo "=============================="

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}Uninstallation failed!${NC}"
    echo "=============================="
    echo ""
    echo "Some files could not be removed. Try manually removing:"
    echo "  rm -rf $TARGET"
    echo ""
    exit 1
else
    echo -e "${GREEN}Uninstallation complete!${NC}"
    echo "=============================="
    echo ""
    echo "Note: .claude/settings.local.json files created by notellm"
    echo "in your project directories are not removed."
    echo ""
    echo "To reinstall:"
    echo "  ./setup.sh"
    echo ""
fi
