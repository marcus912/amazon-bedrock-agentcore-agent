# AWS Deployment Guide

Deploy your AI agent to AWS Bedrock AgentCore for production use.

## Understanding the Deployment

### Dockerfile

The auto-generated `.bedrock_agentcore/*/Dockerfile`:
- Uses `uv` for fast dependency installation
- Installs AWS OpenTelemetry for monitoring
- Runs as non-root user for security
- Exposes ports 9000, 8000, 8080
- Launches with: `opentelemetry-instrument python -m bedrock_app`

**When used:**
| Deployment Target | Uses Dockerfile? |
|-------------------|------------------|
| Local (`agentcore launch --local`) | Yes |
| AWS Lambda | No (Lambda runtime) |
| AWS Fargate | Yes |
| AWS EKS | Yes |
| AWS EC2 | Yes |

## Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured (`aws configure`)
- Bedrock AgentCore Starter Toolkit (installed via `uv sync`)
- `jq` installed (`brew install jq`) - required for IAM setup

## Project Structure

```
project/
├── .bedrock_agentcore.yaml  # Multi-agent configuration
├── .env.example             # Template for environment files
├── dev.env                  # Dev environment config (gitignored)
├── prod.env                 # Prod environment config (gitignored)
├── bin/
│   ├── deploy.sh            # Deploy script with env selection
│   └── setup-agent-permissions.sh  # IAM permissions setup
└── bedrock_app.py           # Agent code
```

## Deployment Workflow

### 1. Configure Environment

Create environment-specific config files:

```bash
# For development
cp .env.example dev.env

# For production
cp .env.example prod.env
```

Edit each file to configure:

| Variable | Description | Example |
|----------|-------------|---------|
| `AGENT_NAME` | Agent name (must match `.bedrock_agentcore.yaml`) | `my_agent_dev` |
| `AGENT_LOG_LEVEL` | Logging level | `INFO` |
| `BEDROCK_MODEL_ID` | Model ID (default: Claude Sonnet 4) | |
| `PROMPT_PROFILE` | System prompt profile | `default` |
| `GITHUB_PAT` | GitHub Personal Access Token | |
| `SES_SENDER_EMAIL` | Verified AWS SES sender email | |
| `SES_SENDER_NAME` | Friendly sender name | |
| `KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | |
| `AWS_REGION` | AWS region | `us-west-2` |
| `MIN_SCORE` | Retrieval score threshold | `0.6` |

AWS credentials via `aws configure`:
- Access Key ID & Secret Access Key
- Default region: `us-west-2`
- Output format: `json`

### 2. Test Locally (Optional)

```bash
./bin/deploy.sh dev --local

curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

### 3. Deploy to AWS

```bash
# Interactive - prompts for environment
./bin/deploy.sh

# Deploy to specific environment
./bin/deploy.sh dev
./bin/deploy.sh prod

# With additional options
./bin/deploy.sh dev --local         # Local deployment
./bin/deploy.sh prod --local-build  # Local build, cloud deploy
```

The deploy script automatically:
1. Reads environment variables from `{env}.env` file
2. Extracts `AGENT_NAME` to select the agent configuration
3. Passes all env vars to `agentcore launch` using `--env` flags
4. Sets up IAM permissions (Knowledge Base, SES) after deployment

**Manual deployment (alternative):**

```bash
agentcore launch --agent my_agent_dev \
  --env GITHUB_PAT=your-github-pat \
  --env SES_SENDER_EMAIL=noreply@yourdomain.com \
  --env KNOWLEDGE_BASE_ID=your-kb-id
```

### 4. Get Endpoint

```bash
agentcore status --agent my_agent_dev
agentcore status --agent my_agent_prod
```

Shows endpoint URL and configuration.

### 5. Test Deployment

```bash
# Via CLI
agentcore invoke '{"prompt": "Hello, agent!"}'

# Via AWS SDK (Python)
import boto3

client = boto3.client(
    'bedrock-agentcore',
    region_name='us-west-2'
)
response = client.invoke_agent_runtime(
    agentRuntimeArn='your-agent-runtime-arn',
    runtimeSessionId='session-123',
    inputText='Your prompt here'
)
```

### 6. Manage Deployment

```bash
agentcore status --agent my_agent_dev   # Check status
agentcore stop-session                   # Stop session
agentcore destroy                        # Remove all resources
```

## Multi-Environment Setup

### Agent Configuration (.bedrock_agentcore.yaml)

The AgentCore CLI supports multiple agent configurations in a single file:

```yaml
default_agent: my_agent_dev
agents:
  my_agent_dev:
    name: my_agent_dev
    entrypoint: /path/to/bedrock_app.py
    aws:
      execution_role: arn:aws:iam::123456789:role/DevExecutionRole
      ecr_repository: 123456789.dkr.ecr.us-west-2.amazonaws.com/my-agent-dev
      region: us-west-2

  my_agent_prod:
    name: my_agent_prod
    entrypoint: /path/to/bedrock_app.py
    aws:
      execution_role: arn:aws:iam::123456789:role/ProdExecutionRole
      ecr_repository: 123456789.dkr.ecr.us-west-2.amazonaws.com/my-agent-prod
      region: us-west-2
```

### Environment Files

Each environment has its own config file:

**dev.env:**
```bash
AGENT_NAME=my_agent_dev
AGENT_LOG_LEVEL=DEBUG
GITHUB_PAT=dev-github-pat
KNOWLEDGE_BASE_ID=dev-kb-id
SES_SENDER_EMAIL=dev@yourdomain.com
```

**prod.env:**
```bash
AGENT_NAME=my_agent_prod
AGENT_LOG_LEVEL=INFO
GITHUB_PAT=prod-github-pat
KNOWLEDGE_BASE_ID=prod-kb-id
SES_SENDER_EMAIL=noreply@yourdomain.com
```

### Configuration Differences by Environment

| Setting | Dev | Prod |
|---------|-----|------|
| `AGENT_NAME` | `my_agent_dev` | `my_agent_prod` |
| `execution_role` | Dev IAM role | Prod IAM role |
| `ecr_repository` | `...-dev` | `...-prod` |
| `AGENT_LOG_LEVEL` | `DEBUG` | `INFO` |
| API keys/secrets | Dev keys | Prod keys |

### Adding a New Environment

1. **Add agent configuration:**
   ```bash
   agentcore configure \
     --name my_agent_staging \
     --entrypoint bedrock_app.py \
     --execution-role arn:aws:iam::123456789:role/StagingRole
   ```

2. **Create environment file:**
   ```bash
   cp .env.example staging.env
   # Edit staging.env and set AGENT_NAME=my_agent_staging
   ```

3. **Update deploy script** (add "staging" to `VALID_ENVS` array in `bin/deploy.sh`)

### Direct CLI Commands

```bash
# Deploy specific agent
agentcore launch --agent my_agent_dev
agentcore launch --agent my_agent_prod

# Set default agent
agentcore configure set-default my_agent_prod

# List all configured agents
agentcore configure list
```

## IAM Permissions Setup

The deploy script automatically sets up IAM permissions after deployment. To run manually:

```bash
./bin/setup-agent-permissions.sh dev
./bin/setup-agent-permissions.sh prod
```

This attaches the following permissions to the agent's execution role:
- **Bedrock Knowledge Base**: `bedrock:Retrieve`, `bedrock:RetrieveAndGenerate`
- **AWS SES**: `ses:SendEmail`, `ses:SendRawEmail`

## Deployment Modes

### Remote Build (Recommended)
```bash
./bin/deploy.sh dev
```
- Builds containers in AWS CodeBuild
- No local Docker required
- Automatically passes env variables to deployment

### Local Container Testing
```bash
./bin/deploy.sh dev --local
```
- Requires Docker/Finch/Podman
- Runs entirely locally
- Fast iteration and debugging

### Hybrid: Local Build + Cloud Deploy
```bash
./bin/deploy.sh dev --local-build
```
- Requires Docker/Finch/Podman
- Builds locally, deploys to cloud
- Useful for build customization

## Advanced Commands

```bash
# Gateway management
agentcore gateway --help
agentcore create_mcp_gateway

# Configuration
agentcore configure

# Import existing agent
agentcore import-agent
```

## Deployment Checklist

- [ ] AWS credentials configured
- [ ] Environment file created (`dev.env` or `prod.env`):
  - [ ] AGENT_NAME (required)
  - [ ] GITHUB_PAT (for github_agent)
  - [ ] SES_SENDER_EMAIL (for email_agent)
  - [ ] KNOWLEDGE_BASE_ID (for retrieve tool)
  - [ ] PROMPT_PROFILE (optional)
- [ ] AWS SES sender email verified
- [ ] (Optional) Tested locally with `--local`
- [ ] Deployment mode selected
- [ ] Agent deployed successfully
- [ ] IAM permissions configured
- [ ] Endpoint tested

## Troubleshooting

**AWS credentials error:**
```bash
aws sts get-caller-identity  # Verify
aws configure  # Reconfigure
```

**Region not supported:**
Try `us-west-2` or `us-east-1`.

**Deployment failed:**
```bash
aws cloudformation describe-stacks --stack-name your-agent-stack
```

**Can't invoke agent:**
```bash
agentcore status --agent my_agent_dev  # Verify endpoint and config
```

**IAM permissions error:**
```bash
./bin/setup-agent-permissions.sh dev  # Re-run permissions setup
```

## Monitoring

View logs in CloudWatch:
```bash
agentcore status # Copy log group/stream info
aws logs tail /aws/bedrock-agentcore/runtimes/your-log-group --log-stream-name-prefix "yyyy/MM/dd/[runtime-logs]" --follow
aws logs tail /aws/bedrock-agentcore/runtimes/your-log-group --log-stream-name-prefix "yyyy/MM/dd/[runtime-logs]" --since 1h
```

## Cost Considerations

AgentCore charges for:
- **Compute**: Lambda invocations or Fargate vCPU/memory
- **Model Usage**: Bedrock API calls (Claude Sonnet 4)
- **Storage**: Agent memory and state
- **Data Transfer**: Inbound/outbound traffic

Estimate: [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

## Resources

- [Bedrock AgentCore Docs](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [Starter Toolkit GitHub](https://github.com/aws/bedrock-agentcore-starter-toolkit)
- [Strands on Bedrock](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/)
