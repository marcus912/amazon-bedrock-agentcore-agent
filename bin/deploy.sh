#!/usr/bin/env bash
# Deploy agent to Bedrock AgentCore with environment selection
#
# Usage:
#   ./bin/deploy.sh [ENV] [OPTIONS]
#
# Arguments:
#   ENV         Environment to deploy: dev, prod (optional - will prompt if not provided)
#
# Examples:
#   ./bin/deploy.sh                     # Interactive: prompts for environment
#   ./bin/deploy.sh dev                 # Deploy to dev
#   ./bin/deploy.sh prod                # Deploy to prod
#   ./bin/deploy.sh dev --local         # Local deployment for dev
#   ./bin/deploy.sh prod --local-build  # Local build, cloud deploy for prod
#
# This script:
# 1. Selects the target environment (dev/prod)
# 2. Loads environment variables from {env}.env file
# 3. Reads AGENT_NAME from the env file
# 4. Passes all env vars to agentcore launch using --env flags
# 5. Sets up IAM permissions (Knowledge Base, SES) after deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Valid environments
VALID_ENVS=("dev" "prod")

# Function to show environment selection menu
select_environment() {
    echo -e "${CYAN}Select deployment environment:${NC}" >&2
    echo "" >&2
    echo "  1) dev  - Development environment" >&2
    echo "  2) prod - Production environment" >&2
    echo "" >&2
    read -p "Enter choice [1-2]: " choice

    case $choice in
        1) echo "dev" ;;
        2) echo "prod" ;;
        *)
            echo -e "${RED}Invalid choice${NC}" >&2
            exit 1
            ;;
    esac
}

# Function to validate environment
validate_env() {
    local env=$1
    for valid in "${VALID_ENVS[@]}"; do
        if [[ "$env" == "$valid" ]]; then
            return 0
        fi
    done
    return 1
}

# Parse arguments
DEPLOY_ENV=""
EXTRA_ARGS=()

# Check if first argument is an environment
if [[ $# -gt 0 ]]; then
    if validate_env "$1"; then
        DEPLOY_ENV="$1"
        shift  # Remove env from arguments
    fi
fi

# Collect remaining arguments
EXTRA_ARGS=("$@")

# If no environment specified, prompt user
if [[ -z "$DEPLOY_ENV" ]]; then
    DEPLOY_ENV=$(select_environment)
fi

# Path to environment-specific .env file
ENV_FILE="$PROJECT_DIR/${DEPLOY_ENV}.env"

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: Environment file not found at $ENV_FILE${NC}"
    echo -e "${YELLOW}Create ${DEPLOY_ENV}.env from .env.example:${NC}"
    echo "  cp .env.example ${DEPLOY_ENV}.env"
    echo "  # Then set AGENT_NAME and other environment-specific values"
    exit 1
fi

echo -e "${GREEN}Loading environment variables from ${DEPLOY_ENV}.env${NC}"

# Read env file and build --env arguments
# Also extract AGENT_NAME for the --agent flag
AGENT_NAME=""
ENV_ARGS=()
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # Extract KEY=VALUE pairs
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"

        # Remove leading/trailing whitespace and quotes from value
        value=$(echo "$value" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

        # Skip empty values
        if [[ -z "$value" ]]; then
            continue
        fi

        # Skip placeholder values
        if [[ "$value" == "your-"* || "$value" == *"-here" ]]; then
            echo -e "${YELLOW}Warning: Skipping placeholder value for $key${NC}"
            continue
        fi

        # Extract AGENT_NAME separately (don't pass as --env)
        if [[ "$key" == "AGENT_NAME" ]]; then
            AGENT_NAME="$value"
            continue
        fi

        # Add to env args
        ENV_ARGS+=("--env" "$key=$value")
        echo -e "  ${GREEN}+${NC} $key"
    fi
done < "$ENV_FILE"

# Validate AGENT_NAME is set
if [[ -z "$AGENT_NAME" ]]; then
    echo -e "${RED}Error: AGENT_NAME not set in ${DEPLOY_ENV}.env${NC}"
    echo -e "${YELLOW}Add AGENT_NAME to your env file:${NC}"
    echo "  AGENT_NAME=your_agent_name"
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Environment: ${CYAN}${DEPLOY_ENV}${NC}"
echo -e "${BLUE}  Agent:       ${CYAN}${AGENT_NAME}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if any valid environment variables were found
if [ ${#ENV_ARGS[@]} -eq 0 ]; then
    echo -e "${YELLOW}Warning: No environment variables found in ${DEPLOY_ENV}.env (other than AGENT_NAME)${NC}"
fi

# Build the final command
echo -e "${GREEN}Deploying to Bedrock AgentCore...${NC}"
echo -e "${YELLOW}Command: agentcore launch --agent $AGENT_NAME ${ENV_ARGS[*]} ${EXTRA_ARGS[*]}${NC}"
echo ""

# Execute agentcore launch with agent name, env variables, and extra arguments
agentcore launch --agent "$AGENT_NAME" "${ENV_ARGS[@]}" "${EXTRA_ARGS[@]}"

# Setup IAM permissions after successful deployment
echo ""
echo -e "${GREEN}Setting up IAM permissions...${NC}"
"$SCRIPT_DIR/setup-agent-permissions.sh" "$DEPLOY_ENV"
