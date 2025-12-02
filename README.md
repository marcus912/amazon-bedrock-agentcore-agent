# Amazon Bedrock AgentCore Agent

An AI agent built with AWS Strands SDK and deployed via AWS Bedrock AgentCore.

> **Quick Start**: See [QUICK_START.md](docs/QUICK_START.md) for setup instructions.

## Features

- 🤖 Model-driven agent architecture using Strands SDK
- 📚 Bedrock Knowledge Base integration for RAG (retrieve tool)
- 🔧 Specialized sub-agents (agent-as-tool pattern)
  - **GitHub Agent**: Repository management, issues, PRs via GitHub MCP
  - **Email Agent**: AWS SES email sending with validation
- 🎯 Configurable system prompts via profiles
- 🏗️ Production deployment via Bedrock AgentCore
- 📝 Logging and observability support

## Project Structure

```
amazon-bedrock-agentcore-agent/
├── agent/
│   └── strands_agent.py         # Orchestrator agent
├── tools/
│   ├── subagents.py             # Sub-agents (github_agent, email_agent)
│   ├── ses_email.py             # AWS SES email tool
│   └── custom_tools.py          # Custom utility tools
├── config/
│   └── prompts/                 # System prompt templates
│       ├── default.txt          # Orchestrator prompt
│       ├── github_agent.txt     # GitHub sub-agent prompt
│       └── email_agent.txt      # Email sub-agent prompt
├── docs/
│   └── subagents/               # Sub-agent documentation
│       ├── GITHUB_AGENT.md      # GitHub agent setup guide
│       └── EMAIL_AGENT.md       # Email agent setup guide
├── bin/
│   └── deploy.sh                # Deployment script (auto-loads .env)
├── bedrock_app.py               # Production entrypoint
├── config.py                    # Configuration (loads .env)
├── pyproject.toml               # Dependencies (managed by uv)
└── .env.example                 # Environment template
```

## Quick Commands

```bash
# Setup
uv sync                    # Install dependencies
cp .env.example .env       # Configure environment

# Local testing (requires Docker)
agentcore launch --local

# Deploy to AWS with environment variables
./bin/deploy.sh                      # Recommended: auto-loads .env
# Or manually:
agentcore launch --env GITHUB_PAT=your-pat

# Test and cleanup
agentcore invoke '{"prompt": "Hi"}'
agentcore destroy
```

**Important:** When deploying to AWS, the `.env` file is NOT automatically uploaded. Use `./bin/deploy.sh` to automatically pass environment variables, or use `--env` flags manually.

## Configuration

Edit `.env` to configure:

**Core Settings:**
- **AGENT_LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL - default: INFO)
- **BEDROCK_MODEL_ID**: Model identifier (leave empty for default: Claude Sonnet 4)
- **PROMPT_PROFILE**: System prompt profile name from `config/prompts/` (default: default)
- **KNOWLEDGE_BASE_ID**: Bedrock Knowledge Base ID for retrieval
- **MIN_SCORE**: Minimum relevance score for retrieval (0.0-1.0, default: 0.7)

**Sub-Agent Configuration:**
- **GITHUB_AGENT_MODEL_ID**: Model for github_agent (leave empty for default: Claude Sonnet 4)
- **EMAIL_AGENT_MODEL_ID**: Model for email_agent (leave empty for default: Claude Sonnet 4)

**GitHub MCP:**
- **GITHUB_PAT**: GitHub Personal Access Token for github_agent

**AWS SES Email:**
- **SES_SENDER_EMAIL**: Verified sender email address (required for email_agent)
- **SES_SENDER_NAME**: Friendly sender name (optional)
- **AWS_REGION**: AWS region for SES and knowledge base (default: us-west-2)

AWS credentials are configured via `aws configure` command.

### System Prompt Configuration

System prompts are stored as text files in `config/prompts/`. To use a different prompt:

```bash
# In .env file
PROMPT_PROFILE=default

# Or via deployment
./bin/deploy.sh --env PROMPT_PROFILE=custom
```

To create a custom prompt, add a new `.txt` file in `config/prompts/` and reference it via `PROMPT_PROFILE`.

## Documentation

- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Fast setup guide with `uv`
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - AWS deployment guide
- **[docs/subagents/GITHUB_AGENT.md](docs/subagents/GITHUB_AGENT.md)** - GitHub agent setup and usage
- **[docs/subagents/EMAIL_AGENT.md](docs/subagents/EMAIL_AGENT.md)** - Email agent and AWS SES setup

## Key Dependencies

- **strands-agents** (1.13.0) - Core agent framework
- **strands-agents-tools** (0.2.12) - Pre-built tools
- **bedrock-agentcore** (1.0.4+) - AWS deployment runtime
- **boto3** - AWS SDK

Dependencies are locked in `uv.lock` for reproducible builds.

## References

- [Strands Agents SDK](https://github.com/strands-agents/sdk-python)
- [Bedrock AgentCore SDK](https://github.com/aws/bedrock-agentcore-sdk-python)
- [Strands 1.0 Announcement](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-1-0-production-ready-multi-agent-orchestration-made-simple/)
- [uv Documentation](https://docs.astral.sh/uv/)

## License

Apache License 2.0
