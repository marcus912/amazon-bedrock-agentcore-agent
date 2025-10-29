# Deployment Guide - AWS Bedrock AgentCore

This guide explains how to deploy your AWS AI Agent to AWS Bedrock AgentCore using the starter toolkit.

## Understanding Deployment Files

### `.bedrock_agentcore.yaml`
Configuration file for Bedrock AgentCore deployments. Contains:
- Agent settings (name, entrypoint, platform)
- AWS configuration (region, account, IAM roles)
- Network settings (public/private, ports)
- Memory and observability settings

### `.bedrock_agentcore/aws_ai_agent/Dockerfile`
Auto-generated Dockerfile for **containerized deployments** (Fargate, EKS, EC2).

**What it does:**
- Uses `uv` for fast dependency installation
- Sets up AWS environment variables
- Installs your agent with all dependencies
- Adds AWS OpenTelemetry for monitoring
- Runs as non-root user for security
- Exposes ports 9000, 8000, 8080
- Launches with: `opentelemetry-instrument python -m bedrock_app`

**When it's used:**
| Deployment Target | Uses Dockerfile? |
|-------------------|------------------|
| Local testing (`main.py`) | ❌ No |
| AWS Lambda | ❌ No (uses Lambda runtime) |
| AWS Fargate | ✅ **Yes** (serverless containers) |
| AWS EKS | ✅ **Yes** (Kubernetes) |
| AWS EC2 | ✅ **Yes** (container instances) |

## Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured with credentials (`aws configure`)
- Bedrock AgentCore Starter Toolkit installed (✅ Already installed)

## Quick Start

### 1. Configure AWS Credentials

Ensure your AWS credentials are configured:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-west-2`)
- Default output format (`json`)

### 2. Launch Your Agent

Use the convenient wrapper script:

```bash
# View all available commands
uv run python agentcore --help

# Check current status
uv run python agentcore status

# Launch agent (will prompt for deployment options)
uv run python agentcore launch
```

## Available Commands

### Core Commands

#### `launch` - Deploy Your Agent
```bash
uv run python agentcore launch
```

Three deployment modes:
- **Local**: Test locally before deploying
- **AWS Lambda**: Serverless deployment
- **AWS Fargate**: Container-based deployment

#### `status` - Check Agent Status
```bash
uv run python agentcore status
```

Shows:
- Configuration details
- Runtime status
- Endpoint URLs
- Resource information

#### `invoke` - Test Your Agent
```bash
uv run python agentcore invoke --prompt "What is 2+2?"
```

Send test requests to your deployed agent.

#### `destroy` - Remove Deployment
```bash
uv run python agentcore destroy
```

Removes all AWS resources created for your agent.

#### `stop-session` - Stop Active Session
```bash
uv run python agentcore stop-session
```

Stops the current runtime session.

### Gateway Commands

#### `create_mcp_gateway` - Create MCP Gateway
```bash
uv run python agentcore create_mcp_gateway
```

Creates a Model Context Protocol gateway for tool integration.

#### `gateway` - Manage Gateways
```bash
uv run python agentcore gateway --help
```

Manage Bedrock AgentCore gateways.

### Configuration

#### `configure` - Manage Configuration
```bash
uv run python agentcore configure
```

Manage agent configuration settings.

### Import Agents

#### `import-agent` - Import Existing Agent
```bash
uv run python agentcore import-agent
```

Import a Bedrock Agent and convert it to LangChain or Strands format with AgentCore primitives.

## Deployment Workflow

### Step 1: Configure Your Agent

Edit `.env` with your AWS settings:
```bash
AWS_REGION=us-west-2
AWS_PROFILE=default
BEDROCK_MODEL_ID=anthropic.claude-4-sonnet-v2:0
```

### Step 2: Test Locally First

Before deploying to AWS, test locally:
```bash
# Option 1: Interactive CLI
uv run python main.py

# Option 2: Test bedrock_app entrypoint
uv run python test_bedrock_app.py
```

### Step 3: Launch to AWS

```bash
uv run python agentcore launch
```

Follow the prompts to:
1. Select deployment mode (Lambda or Fargate)
2. Configure resources (memory, timeout, etc.)
3. Deploy to AWS

### Step 4: Get Endpoint Information

```bash
uv run python agentcore status
```

This shows your agent's endpoint URL and configuration.

### Step 5: Invoke Your Agent

```bash
# Via CLI
uv run python agentcore invoke --prompt "Hello, agent!"

# Via AWS SDK (Python)
import boto3

client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
response = client.invoke_agent(
    agentId='your-agent-id',
    sessionId='session-123',
    inputText='Your prompt here'
)
```

### Step 6: Monitor and Manage

```bash
# Check status
uv run python agentcore status

# View logs (CloudWatch)
aws logs tail /aws/lambda/your-agent-name --follow

# Stop session if needed
uv run python agentcore stop-session

# Destroy when done (removes all resources)
uv run python agentcore destroy
```

## Alternative: Direct Python Module

You can also use the Python module directly:

```bash
# Full module path
uv run python -m bedrock_agentcore_starter_toolkit.cli.cli --help

# Launch
uv run python -m bedrock_agentcore_starter_toolkit.cli.cli launch

# Status
uv run python -m bedrock_agentcore_starter_toolkit.cli.cli status
```

## Production Deployment Checklist

- [ ] AWS credentials configured
- [ ] Agent tested locally (`main.py` or `test_bedrock_app.py`)
- [ ] Environment variables configured (`.env`)
- [ ] AWS region selected
- [ ] Deployment mode chosen (Lambda vs Fargate)
- [ ] Resource limits configured (memory, timeout)
- [ ] IAM roles and permissions verified
- [ ] CloudWatch logging enabled
- [ ] Agent launched successfully
- [ ] Endpoint tested with sample requests
- [ ] Monitoring and alerts configured

## Troubleshooting

### AWS Credentials Error
```bash
# Verify credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

### Region Not Supported
Some regions may not have Bedrock AgentCore. Try:
- `us-west-2` (Oregon)
- `us-east-1` (N. Virginia)

### Deployment Failed
Check CloudFormation stack status:
```bash
aws cloudformation describe-stacks --stack-name your-agent-stack
```

### Can't Invoke Agent
Verify endpoint and credentials:
```bash
uv run python agentcore status
```

## Cost Considerations

AWS Bedrock AgentCore charges for:
- **Compute**: Lambda invocations or Fargate vCPU/memory
- **Model Usage**: Bedrock model API calls (Claude 4 Sonnet)
- **Storage**: Agent memory and state
- **Data Transfer**: Inbound/outbound traffic

Estimate costs at: https://aws.amazon.com/bedrock/pricing/

## Resources

- [Bedrock AgentCore Documentation](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [Starter Toolkit GitHub](https://github.com/aws/bedrock-agentcore-starter-toolkit)
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Strands Agents on Bedrock](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/)

## Quick Reference

```bash
# Essential commands
uv run python agentcore launch        # Deploy to AWS
uv run python agentcore status        # Check status
uv run python agentcore invoke        # Test agent
uv run python agentcore destroy       # Clean up

# Local testing
uv run python main.py                 # Interactive CLI
uv run python test_bedrock_app.py     # Test bedrock_app
```
