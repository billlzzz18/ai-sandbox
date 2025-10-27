#!/bin/bash

# AI Agent Sandbox Environment Setup Script
# This script helps users set up their environment variables

set -e

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

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local response

    read -p "$prompt [$default]: " response
    echo "${response:-$default}"
}

# Function to setup environment file
setup_env_file() {
    local env_file=".env"

    if [[ -f "$env_file" ]]; then
        print_warning "Environment file $env_file already exists."
        local overwrite=$(prompt_with_default "Do you want to overwrite it? (y/N)" "n")
        if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
            print_info "Skipping environment file creation."
            return 0
        fi
    fi

    print_info "Creating environment file..."

    # Copy from template
    cp .env.example "$env_file"

    print_success "Environment file created: $env_file"
    print_warning "Please edit $env_file and fill in your API keys before running the application."
}

# Function to validate API keys
validate_api_keys() {
    print_info "Validating API keys..."

    local env_file=".env"
    local missing_keys=()

    if [[ ! -f "$env_file" ]]; then
        print_error "Environment file $env_file not found. Run setup first."
        return 1
    fi

    # Load environment variables
    set -a
    source "$env_file"
    set +a

    # Check required keys (at least one AI assistant should be configured)
    local ai_keys=("GEMINI_API_KEY" "OPENAI_API_KEY" "ANTHROPIC_API_KEY" "GITHUB_TOKEN" "QWEN_API_KEY" "KILO_CODE_API_KEY" "OPEN_CODE_API_KEY")
    local configured_count=0

    for key in "${ai_keys[@]}"; do
        if [[ -n "${!key}" && "${!key}" != "your_"*"_here" ]]; then
            ((configured_count++))
            print_success "$key is configured"
        else
            missing_keys+=("$key")
        fi
    done

    if [[ $configured_count -eq 0 ]]; then
        print_error "No AI assistant API keys are configured!"
        print_info "Please configure at least one of the following in $env_file:"
        printf '  - %s\n' "${ai_keys[@]}"
        return 1
    else
        print_success "$configured_count AI assistant(s) configured"
    fi

    if [[ ${#missing_keys[@]} -gt 0 ]]; then
        print_warning "The following API keys are not configured (optional):"
        printf '  - %s\n' "${missing_keys[@]}"
    fi

    return 0
}

# Function to test AI assistant connections
test_assistant_connections() {
    print_info "Testing AI assistant connections..."

    local env_file=".env"

    if [[ ! -f "$env_file" ]]; then
        print_error "Environment file $env_file not found."
        return 1
    fi

    # Load environment variables
    set -a
    source "$env_file"
    set +a

    # Test Gemini (if configured)
    if [[ -n "$GEMINI_API_KEY" && "$GEMINI_API_KEY" != "your_"*"_here" ]]; then
        print_info "Testing Gemini CLI..."
        if command_exists "gemini"; then
            # Try a simple test (this might require actual API call)
            print_success "Gemini CLI is available"
        else
            print_warning "Gemini CLI not installed. Install with: npm install -g @google/gemini-cli"
        fi
    fi

    # Test other assistants similarly...
    print_info "Connection testing completed. Run the application to verify full functionality."
}

# Function to show usage
show_usage() {
    cat << EOF
AI Agent Sandbox Environment Setup

Usage: $0 [COMMAND]

Commands:
    setup       Create .env file from template
    validate    Validate API keys configuration
    test        Test AI assistant connections
    all         Run setup, validate, and test
    help        Show this help message

Examples:
    $0 setup          # Create environment file
    $0 validate       # Check API key configuration
    $0 test           # Test assistant connections
    $0 all            # Complete setup process

Environment Variables:
    Copy .env.example to .env and configure the following:
    - GEMINI_API_KEY          (Google Gemini)
    - OPENAI_API_KEY          (GitHub Codex)
    - ANTHROPIC_API_KEY       (Claude Code)
    - GITHUB_TOKEN            (GitHub Copilot)
    - QWEN_API_KEY            (Alibaba Qwen)
    - KILO_CODE_API_KEY       (Kilo Code)
    - OPEN_CODE_API_KEY       (Open Code)

EOF
}

# Main script logic
main() {
    local command="${1:-help}"

    case "$command" in
        "setup")
            setup_env_file
            ;;
        "validate")
            validate_api_keys
            ;;
        "test")
            test_assistant_connections
            ;;
        "all")
            print_info "Running complete setup process..."
            setup_env_file
            echo
            if validate_api_keys; then
                echo
                test_assistant_connections
            fi
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"