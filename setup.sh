#!/usr/bin/env bash
set -euo pipefail

#######################################
# notellm setup - Install notellm
# https://github.com/prairie-guy/notellm
#######################################

INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/notellm"
BIN_DIR="${HOME}/.local/bin"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_step() {
    echo -e "${BLUE}▶${NC} $1"
}

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════╗"
echo "║           notellm installer                    ║"
echo "║   Jupyter + Claude Code Workspace Manager      ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Clean up previous installation
if [ -d "$INSTALL_DIR" ]; then
    log_step "Removing previous installation..."
    rm -rf "$INSTALL_DIR"
    log_info "Previous installation removed"
fi

if [ -L "$BIN_DIR/notellm" ]; then
    rm -f "$BIN_DIR/notellm"
fi

# Create directories
log_step "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Copy files
log_step "Installing files..."
cp -r "$REPO_DIR/notellm" "$INSTALL_DIR/"
cp -r "$REPO_DIR/templates" "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/notellm"

log_info "Files installed to $INSTALL_DIR"

# Create symlink
log_step "Creating symlink..."
ln -sf "$INSTALL_DIR/notellm" "$BIN_DIR/notellm"
log_info "Symlink created at $BIN_DIR/notellm"

# Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    log_warn "$BIN_DIR is not in your PATH"
    echo ""
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "Then restart your shell or run:"
    echo ""
    echo -e "  ${CYAN}source ~/.bashrc${NC}  # or ~/.zshrc"
    echo ""
fi

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Installation Complete!               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Installed:${NC}"
echo "  Files:   $INSTALL_DIR/"
echo "  Command: $BIN_DIR/notellm"
echo ""
echo -e "${YELLOW}Usage:${NC}"
echo "  cd ~/your-project"
echo -e "  ${CYAN}notellm start${NC}          # Initialize and start JupyterLab"
echo -e "  ${CYAN}notellm new analysis${NC}   # Create notebook"
echo -e "  ${CYAN}notellm stop${NC}           # Stop server"
echo ""
echo -e "${YELLOW}More info:${NC}"
echo -e "  ${CYAN}notellm help${NC}"
echo ""
