#!/usr/bin/env bash
set -euo pipefail

#######################################
# notellm uninstall - Remove notellm
# https://github.com/prairie-guy/notellm
#######################################

INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/notellm"
BIN_DIR="${HOME}/.local/bin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_step() {
    echo -e "${BLUE}▶${NC} $1"
}

QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -h|--help)
            cat << EOF
${CYAN}notellm uninstall${NC} - Remove notellm

${YELLOW}USAGE:${NC}
    ./uninstall.sh [options]

${YELLOW}OPTIONS:${NC}
    -q, --quiet     Suppress output
    -h, --help      Show this help

${YELLOW}REMOVES:${NC}
    $INSTALL_DIR/
    $BIN_DIR/notellm

${YELLOW}NOTE:${NC}
    This does not remove project files created by 'notellm init'.
    Those remain in their respective project directories.

EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ "$QUIET" = false ]; then
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════╗"
    echo "║           notellm uninstaller                  ║"
    echo "╚════════════════════════════════════════════════╝"
    echo -e "${NC}"
fi

# Remove symlink
if [ -L "$BIN_DIR/notellm" ]; then
    [ "$QUIET" = false ] && log_step "Removing symlink..."
    rm -f "$BIN_DIR/notellm"
    [ "$QUIET" = false ] && log_info "Removed $BIN_DIR/notellm"
elif [ "$QUIET" = false ]; then
    log_warn "No symlink found at $BIN_DIR/notellm"
fi

# Remove install directory
if [ -d "$INSTALL_DIR" ]; then
    [ "$QUIET" = false ] && log_step "Removing installation directory..."
    rm -rf "$INSTALL_DIR"
    [ "$QUIET" = false ] && log_info "Removed $INSTALL_DIR"
elif [ "$QUIET" = false ]; then
    log_warn "No installation found at $INSTALL_DIR"
fi

if [ "$QUIET" = false ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           Uninstall Complete                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "notellm has been removed."
    echo ""
    echo "Project files created with 'notellm init' were not removed."
    echo "You can delete those manually if desired."
    echo ""
fi
