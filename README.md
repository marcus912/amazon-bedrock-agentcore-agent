# Amazon Bedrock AgentCore Agent

An AI agent built with AWS Strands SDK and deployed via AWS Bedrock AgentCore.

> **Quick Start**: See [QUICK_START.md](QUICK_START.md) for setup instructions.

## Features

- 🤖 Model-driven agent architecture using Strands SDK
- 🔧 Built-in tools: Calculator, Tavily search, and custom tools
- 🏗️ Production deployment via Bedrock AgentCore
- 📝 Logging and observability support

## Project Structure

```
amazon-bedrock-agentcore-agent/
├── agent/
│   └── strands_agent.py         # Main agent implementation
├── tools/
│   └── custom_tools.py          # Custom tool definitions
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

## Custom Tools

Add custom tools using the `@tool` decorator:

```python
from strands import tool

@tool
def your_tool(param: str) -> str:
    """Tool description for LLM to understand when to use it."""
    return result
```

Add to `tools/custom_tools.py`:

```python
def get_custom_tools() -> List:
    return [text_analyzer, format_data, aws_region_info, your_tool]
```

## Configuration

Edit `.env` to configure:

- **AGENT_LOG_LEVEL**: DEBUG, INFO, WARNING, ERROR, or CRITICAL (default: INFO)

AWS credentials are configured via `aws configure` command.

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
