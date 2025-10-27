#!/bin/bash

# AI Agent Sandbox - Assistant Setup Script
# This script helps set up and manage AI coding assistants

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup environment variables
setup_env_vars() {
    local env_file="$PROJECT_DIR/.env"

    if [ ! -f "$env_file" ]; then
        print_info "Creating .env file for API keys..."
        cat > "$env_file" << 'EOF'
# AI Agent Sandbox Environment Variables
# Add your API keys here

# Google Gemini
# GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI (for Codex)
# OPENAI_API_KEY=your_openai_api_key_here

# Kilo Code
# KILO_CODE_API_KEY=your_kilo_code_api_key_here

# Qwen
# QWEN_API_KEY=your_qwen_api_key_here

# Anthropic (for Claude Code)
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub (for Copilot)
# GITHUB_TOKEN=your_github_token_here

# Open Code
# OPEN_CODE_API_KEY=your_open_code_api_key_here
EOF
        print_success "Created .env file at $env_file"
        print_warning "Please edit the .env file and add your API keys"
    else
        print_info ".env file already exists at $env_file"
    fi
}

# Function to check CLI installations
check_cli_installations() {
    print_info "Checking AI assistant CLI installations..."

    local assistants=(
        "gemini:Google Gemini CLI:@google/gemini-cli"
        "codex:GitHub Codex CLI:codex-cli"
        "kilo-code:Kilo Code CLI:kilo-code"
        "qwen-cli:Qwen CLI:qwen-cli"
        "claude-code:Claude Code CLI:@anthropic/claude-code"
        "github-copilot-cli:GitHub Copilot CLI:@github/copilot-cli"
        "open-code:Open Code CLI:open-code"
    )

    for assistant in "${assistants[@]}"; do
        local cmd=$(echo "$assistant" | cut -d: -f1)
        local name=$(echo "$assistant" | cut -d: -f2)
        local package=$(echo "$assistant" | cut -d: -f3)

        if command_exists "$cmd"; then
            print_success "$name is installed"
            # Check if it's globally installed
            if [[ "$package" == @* ]]; then
                # npm package
                if npm list -g "$package" >/dev/null 2>&1; then
                    echo "  📦 Globally installed via npm"
                fi
            else
                # pip package
                if pip show "$package" >/dev/null 2>&1; then
                    echo "  🐍 Installed via pip"
                fi
            fi
        else
            print_warning "$name is not installed"
            echo "  To install $name, run:"
            if [[ "$package" == @* ]]; then
                echo "    npm install -g $package"
            else
                echo "    pip install $package"
            fi
            echo "  Or visit the official documentation for manual installation"
        fi
    done
}

# Function to test assistant connectivity
test_assistant() {
    local assistant=$1
    local test_prompt="Hello, please respond with 'Assistant working' if you can read this."

    print_info "Testing $assistant assistant..."

    case "$assistant" in
        "gemini")
            if command_exists "gemini" && [ -n "$GEMINI_API_KEY" ]; then
                if gemini -p "$test_prompt" >/dev/null 2>&1; then
                    print_success "Gemini CLI is working"
                else
                    print_error "Gemini CLI test failed"
                fi
            else
                print_warning "Gemini CLI or API key not available"
            fi
            ;;
        "codex")
            if command_exists "codex" && [ -n "$OPENAI_API_KEY" ]; then
                if codex --prompt "$test_prompt" >/dev/null 2>&1; then
                    print_success "Codex CLI is working"
                else
                    print_error "Codex CLI test failed"
                fi
            else
                print_warning "Codex CLI or API key not available"
            fi
            ;;
        "kilo_code")
            if command_exists "kilo-code" && [ -n "$KILO_CODE_API_KEY" ]; then
                if kilo-code -p "$test_prompt" >/dev/null 2>&1; then
                    print_success "Kilo Code CLI is working"
                else
                    print_error "Kilo Code CLI test failed"
                fi
            else
                print_warning "Kilo Code CLI or API key not available"
            fi
            ;;
        "qwen")
            if command_exists "qwen-cli" && [ -n "$QWEN_API_KEY" ]; then
                if qwen-cli --prompt "$test_prompt" >/dev/null 2>&1; then
                    print_success "Qwen CLI is working"
                else
                    print_error "Qwen CLI test failed"
                fi
            else
                print_warning "Qwen CLI or API key not available"
            fi
            ;;
        "claude_code")
            if command_exists "claude-code" && [ -n "$ANTHROPIC_API_KEY" ]; then
                if claude-code -p "$test_prompt" >/dev/null 2>&1; then
                    print_success "Claude Code CLI is working"
                else
                    print_error "Claude Code CLI test failed"
                fi
            else
                print_warning "Claude Code CLI or API key not available"
            fi
            ;;
        "github_copilot")
            if command_exists "github-copilot-cli" && [ -n "$GITHUB_TOKEN" ]; then
                if github-copilot-cli --prompt "$test_prompt" >/dev/null 2>&1; then
                    print_success "GitHub Copilot CLI is working"
                else
                    print_error "GitHub Copilot CLI test failed"
                fi
            else
                print_warning "GitHub Copilot CLI or token not available"
            fi
            ;;
        "open_code")
            if command_exists "open-code" && [ -n "$OPEN_CODE_API_KEY" ]; then
                if open-code -p "$test_prompt" >/dev/null 2>&1; then
                    print_success "Open Code CLI is working"
                else
                    print_error "Open Code CLI test failed"
                fi
            else
                print_warning "Open Code CLI or API key not available"
            fi
            ;;
    esac
}

# Function to test all assistants
test_all_assistants() {
    print_info "Testing all AI assistants..."

    # Load environment variables
    if [ -f "$PROJECT_DIR/.env" ]; then
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    fi

    test_assistant "gemini"
    test_assistant "codex"
    test_assistant "kilo_code"
    test_assistant "qwen"
    test_assistant "claude_code"
    test_assistant "github_copilot"
    test_assistant "open_code"
}

# Function to show usage
show_usage() {
    cat << EOF
AI Agent Sandbox - Assistant Setup Script

Usage: $0 [COMMAND]

Commands:
    setup       Setup environment variables and check installations
    check       Check which AI assistant CLIs are installed
    test        Test all AI assistant connections
    test <name> Test specific assistant (gemini, codex, kilo_code, qwen, claude_code, github_copilot, open_code)
    help        Show this help message

Examples:
    $0 setup                    # Initial setup
    $0 check                    # Check installations
    $0 test                     # Test all assistants
    $0 test gemini              # Test only Gemini

Environment Variables:
    GEMINI_API_KEY              # Google Gemini API key
    OPENAI_API_KEY              # OpenAI API key (for Codex)
    KILO_CODE_API_KEY           # Kilo Code API key
    QWEN_API_KEY                # Qwen API key
    ANTHROPIC_API_KEY           # Anthropic API key (for Claude)
    GITHUB_TOKEN                # GitHub token (for Copilot)
    OPEN_CODE_API_KEY           # Open Code API key

EOF
}

# Main script logic
case "${1:-help}" in
    "setup")
        print_info "Setting up AI assistants..."
        setup_env_vars
        check_cli_installations
        print_success "Setup complete!"
        ;;
    "check")
        check_cli_installations
        ;;
    "test")
        if [ -n "$2" ]; then
            test_assistant "$2"
        else
            test_all_assistants
        fi
        ;;
    "help"|*)
        show_usage
        ;;
esac