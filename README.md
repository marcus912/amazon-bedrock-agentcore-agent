# Amazon Bedrock AgentCore Agent

An AI agent built with AWS Strands SDK and deployed via AWS Bedrock AgentCore.

> **Quick Start**: See [QUICK_START.md](QUICK_START.md) for setup instructions.

## Features

- 🤖 Model-driven agent architecture using Strands SDK
- 📚 Bedrock Knowledge Base integration for RAG (retrieve tool)
- 🔧 GitHub MCP tools for issue management
- 🎯 Configurable system prompts via profiles
- 🏗️ Production deployment via Bedrock AgentCore
- 📝 Logging and observability support

## Project Structure

```
amazon-bedrock-agentcore-agent/
├── agent/
│   └── strands_agent.py         # Main agent implementation
├── config/
│   └── prompts/                 # System prompt templates
│       ├── default.txt          # General assistant prompt
│       └── *.txt                # Custom prompt profiles
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

- **AGENT_LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL - default: INFO)
- **BEDROCK_MODEL_ID**: Model identifier (leave empty for default: Claude Sonnet 4)
- **PROMPT_PROFILE**: System prompt profile name from `config/prompts/` (default: default)
- **GITHUB_PAT**: GitHub Personal Access Token for MCP tools
- **KNOWLEDGE_BASE_ID**: Bedrock Knowledge Base ID for retrieval
- **AWS_REGION**: AWS region for knowledge base (default: us-west-2)
- **MIN_SCORE**: Minimum relevance score for retrieval (0.0-1.0, default: 0.7)

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

- **[QUICK_START.md](QUICK_START.md)** - Fast setup guide with `uv`
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - AWS deployment guide

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
