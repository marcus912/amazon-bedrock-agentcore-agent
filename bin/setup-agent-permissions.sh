#!/usr/bin/env bash
# Setup IAM permissions for agent execution role
#
# This script attaches the following permissions to the agent's execution role:
# - Bedrock Knowledge Base: Retrieve, RetrieveAndGenerate
# - AWS SES: SendEmail, SendRawEmail
#
# Usage:
#   ./bin/setup-agent-permissions.sh [ENV]
#
# Examples:
#   ./bin/setup-agent-permissions.sh dev   # Setup for dev environment
#   ./bin/setup-agent-permissions.sh prod  # Setup for prod environment
#   ./bin/setup-agent-permissions.sh       # Interactive: prompts for environment

set -e

# Check for jq dependency
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install with: brew install jq"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Valid environments
VALID_ENVS=("dev" "prod")

select_environment() {
    echo -e "${CYAN}Select environment:${NC}" >&2
    echo "" >&2
    echo "  1) dev" >&2
    echo "  2) prod" >&2
    echo "" >&2
    read -p "Enter choice [1-2]: " choice
    case $choice in
        1) echo "dev" ;;
        2) echo "prod" ;;
        *) echo -e "${RED}Invalid choice${NC}" >&2; exit 1 ;;
    esac
}

validate_env() {
    local env=$1
    for valid in "${VALID_ENVS[@]}"; do
        [[ "$env" == "$valid" ]] && return 0
    done
    return 1
}

# Parse environment argument
DEPLOY_ENV=""
if [[ $# -gt 0 ]] && validate_env "$1"; then
    DEPLOY_ENV="$1"
else
    DEPLOY_ENV=$(select_environment)
fi

# Load environment file
ENV_FILE="$PROJECT_DIR/${DEPLOY_ENV}.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: $ENV_FILE not found${NC}"
    exit 1
fi

# Helper function to extract value from env file
get_env_value() {
    local key=$1
    # Use cut -f2- to get everything after the first '=' (handles values containing '=')
    local value=$(grep -E "^${key}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    echo "$value"
}

# Extract configuration from env file
AGENT_NAME=$(get_env_value "AGENT_NAME")
KNOWLEDGE_BASE_ID=$(get_env_value "KNOWLEDGE_BASE_ID")
AWS_REGION=$(get_env_value "AWS_REGION")
SES_SENDER_EMAIL=$(get_env_value "SES_SENDER_EMAIL")

# Set defaults
AWS_REGION=${AWS_REGION:-us-west-2}

# Validate required values
if [[ -z "$AGENT_NAME" ]]; then
    echo -e "${RED}Error: AGENT_NAME not set in $ENV_FILE${NC}"
    exit 1
fi

# Get execution role from .bedrock_agentcore.yaml
CONFIG_FILE="$PROJECT_DIR/.bedrock_agentcore.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: .bedrock_agentcore.yaml not found${NC}"
    exit 1
fi

# Extract execution role ARN
EXECUTION_ROLE=$(grep -A 50 "^  ${AGENT_NAME}:" "$CONFIG_FILE" | grep "execution_role:" | head -1 | sed 's/.*execution_role: //' | tr -d ' ')

if [[ -z "$EXECUTION_ROLE" || "$EXECUTION_ROLE" == "null" ]]; then
    echo -e "${RED}Error: Could not find execution_role for agent ${AGENT_NAME}${NC}"
    echo -e "${YELLOW}Make sure the agent has been deployed at least once.${NC}"
    exit 1
fi

# Extract role name from ARN
ROLE_NAME=$(echo "$EXECUTION_ROLE" | sed 's/.*role\///')

# Get AWS account ID
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [[ -z "$AWS_ACCOUNT" ]]; then
    echo -e "${RED}Error: Could not get AWS account ID. Check AWS credentials.${NC}"
    exit 1
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Environment:      ${GREEN}${DEPLOY_ENV}${NC}"
echo -e "${CYAN}  Agent:            ${GREEN}${AGENT_NAME}${NC}"
echo -e "${CYAN}  Role:             ${GREEN}${ROLE_NAME}${NC}"
echo -e "${CYAN}  Region:           ${GREEN}${AWS_REGION}${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Build policy statements array
POLICY_STATEMENTS="[]"

# Add Knowledge Base permissions if configured
if [[ -n "$KNOWLEDGE_BASE_ID" && "$KNOWLEDGE_BASE_ID" != "your-"* ]]; then
    echo -e "${GREEN}Adding Knowledge Base permissions...${NC}"
    echo -e "  Knowledge Base: ${CYAN}${KNOWLEDGE_BASE_ID}${NC}"

    KB_STATEMENT=$(cat <<EOF
{
    "Sid": "BedrockKnowledgeBaseAccess",
    "Effect": "Allow",
    "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
    ],
    "Resource": [
        "arn:aws:bedrock:${AWS_REGION}:${AWS_ACCOUNT}:knowledge-base/${KNOWLEDGE_BASE_ID}"
    ]
}
EOF
)
    POLICY_STATEMENTS=$(echo "$POLICY_STATEMENTS" | jq --argjson stmt "$KB_STATEMENT" '. + [$stmt]')
else
    echo -e "${YELLOW}Skipping Knowledge Base permissions (not configured)${NC}"
fi

# Add SES permissions if configured
if [[ -n "$SES_SENDER_EMAIL" && "$SES_SENDER_EMAIL" != *"@yourdomain"* ]]; then
    # Extract domain from email
    SES_DOMAIN=$(echo "$SES_SENDER_EMAIL" | cut -d'@' -f2)

    echo -e "${GREEN}Adding SES permissions...${NC}"
    echo -e "  Sender Email: ${CYAN}${SES_SENDER_EMAIL}${NC}"
    echo -e "  Domain:       ${CYAN}${SES_DOMAIN}${NC}"

    SES_STATEMENT=$(cat <<EOF
{
    "Sid": "SESSendEmail",
    "Effect": "Allow",
    "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
    ],
    "Resource": [
        "arn:aws:ses:${AWS_REGION}:${AWS_ACCOUNT}:identity/${SES_DOMAIN}",
        "arn:aws:ses:${AWS_REGION}:${AWS_ACCOUNT}:identity/${SES_SENDER_EMAIL}"
    ]
}
EOF
)
    POLICY_STATEMENTS=$(echo "$POLICY_STATEMENTS" | jq --argjson stmt "$SES_STATEMENT" '. + [$stmt]')
else
    echo -e "${YELLOW}Skipping SES permissions (not configured)${NC}"
fi

# Check if we have any statements to add
STATEMENT_COUNT=$(echo "$POLICY_STATEMENTS" | jq 'length')
if [[ "$STATEMENT_COUNT" -eq 0 ]]; then
    echo -e "${YELLOW}No permissions to add. Check your environment configuration.${NC}"
    exit 0
fi

# Build the complete policy document
POLICY_NAME="AgentServicePermissions"
POLICY_DOCUMENT=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": ${POLICY_STATEMENTS}
}
EOF
)

echo ""
echo -e "${GREEN}Attaching policy to role...${NC}"

# Check if policy already exists
EXISTING_POLICY=$(aws iam get-role-policy --role-name "$ROLE_NAME" --policy-name "$POLICY_NAME" 2>/dev/null || echo "")
if [[ -n "$EXISTING_POLICY" ]]; then
    echo -e "${YELLOW}Policy '${POLICY_NAME}' already exists. Updating...${NC}"
fi

# Put the inline policy
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --policy-document "$POLICY_DOCUMENT"

echo ""
echo -e "${GREEN}Successfully attached permissions!${NC}"
echo ""
echo -e "Policy: ${CYAN}${POLICY_NAME}${NC}"
echo -e "Role:   ${CYAN}${ROLE_NAME}${NC}"
echo ""
echo -e "Permissions granted:"
if [[ -n "$KNOWLEDGE_BASE_ID" && "$KNOWLEDGE_BASE_ID" != "your-"* ]]; then
    echo -e "  ${GREEN}+${NC} bedrock:Retrieve"
    echo -e "  ${GREEN}+${NC} bedrock:RetrieveAndGenerate"
fi
if [[ -n "$SES_SENDER_EMAIL" && "$SES_SENDER_EMAIL" != *"@yourdomain"* ]]; then
    echo -e "  ${GREEN}+${NC} ses:SendEmail"
    echo -e "  ${GREEN}+${NC} ses:SendRawEmail"
fi
