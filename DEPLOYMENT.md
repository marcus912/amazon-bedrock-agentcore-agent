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
| Local (`agentcore launch --local`) | ✅ Yes |
| AWS Lambda | ❌ No (Lambda runtime) |
| AWS Fargate | ✅ Yes |
| AWS EKS | ✅ Yes |
| AWS EC2 | ✅ Yes |

## Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured (`aws configure`)
- Bedrock AgentCore Starter Toolkit (installed via `uv sync`)

## Deployment Workflow

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env: Set AGENT_LOG_LEVEL
```

AWS credentials via `aws configure`:
- Access Key ID & Secret Access Key
- Default region: `us-west-2`
- Output format: `json`

### 2. Test Locally (Optional)

```bash
agentcore launch --local

curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

### 3. Deploy to AWS

```bash
agentcore launch
```

Follow prompts to select:
- Deployment mode (Lambda or Fargate)
- Resource configuration (memory, timeout)
- Network settings

### 4. Get Endpoint

```bash
agentcore status
```

Shows endpoint URL and configuration.

### 5. Test Deployment

```bash
# Via CLI
agentcore invoke '{"prompt": "Hello, agent!"}'

# Via AWS SDK (Python)
import boto3

client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
response = client.invoke_agent(
    agentId='your-agent-id',
    sessionId='session-123',
    inputText='Your prompt here'
)
```

### 6. Manage Deployment

```bash
agentcore status          # Check status
agentcore stop-session    # Stop session
agentcore destroy         # Remove all resources
```

## Deployment Modes

### Remote Build (Recommended)
```bash
agentcore launch
```
- Builds containers in AWS CodeBuild
- No local Docker required
- Best for teams without containerization tools

### Local Container Testing
```bash
agentcore launch --local
```
- Requires Docker/Finch/Podman
- Runs entirely locally
- Fast iteration and debugging

### Hybrid: Local Build + Cloud Deploy
```bash
agentcore launch --local-build
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
- [ ] Environment variables set (`.env`)
- [ ] (Optional) Tested locally with `--local`
- [ ] Deployment mode selected
- [ ] Resource limits configured
- [ ] IAM permissions verified
- [ ] Agent deployed successfully
- [ ] Endpoint tested
- [ ] Monitoring configured

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
agentcore status  # Verify endpoint and config
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
