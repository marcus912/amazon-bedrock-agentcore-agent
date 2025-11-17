#!/usr/bin/env bash
# Deploy agent to Bedrock AgentCore with environment variables from .env file
#
# Usage:
#   ./bin/deploy.sh [OPTIONS]
#
# Examples:
#   ./bin/deploy.sh                    # Deploy with .env variables
#   ./bin/deploy.sh --local            # Local deployment with .env variables
#   ./bin/deploy.sh --local-build      # Local build, cloud deploy with .env variables
#   ./bin/deploy.sh -a my-agent        # Deploy specific agent with .env variables
#
# This script:
# 1. Loads environment variables from .env file
# 2. Passes them to agentcore launch using --env flags
# 3. Supports all agentcore launch options

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Path to .env file
ENV_FILE="$PROJECT_DIR/.env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found at $ENV_FILE${NC}"
    echo -e "${YELLOW}Copy .env.example to .env and configure your environment variables:${NC}"
    echo "  cp .env.example .env"
    exit 1
fi

echo -e "${GREEN}Loading environment variables from .env${NC}"

# Read .env file and build --env arguments
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

        # Skip placeholder values
        if [[ "$value" == "your-"* || "$value" == *"-here" ]]; then
            echo -e "${YELLOW}Warning: Skipping placeholder value for $key${NC}"
            continue
        fi

        # Add to env args
        ENV_ARGS+=("--env" "$key=$value")
        echo -e "  ${GREEN}✓${NC} $key"
    fi
done < "$ENV_FILE"

# Check if any valid environment variables were found
if [ ${#ENV_ARGS[@]} -eq 0 ]; then
    echo -e "${YELLOW}Warning: No valid environment variables found in .env${NC}"
    echo -e "${YELLOW}Make sure to replace placeholder values like 'your-github-pat-here'${NC}"
fi

# Build the final command with all arguments
echo ""
echo -e "${GREEN}Deploying to Bedrock AgentCore...${NC}"
echo "Command: agentcore launch ${ENV_ARGS[@]} $@"
echo ""

# Execute agentcore launch with env variables and pass through all script arguments
agentcore launch "${ENV_ARGS[@]}" "$@"
