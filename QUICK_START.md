# Quick Start Guide

Get your Amazon Bedrock AgentCore Agent running in minutes.

## Prerequisites

**Required:**
- Python 3.10+ (project uses 3.13.5)
- AWS Account with Bedrock access
- Claude 3.7 Sonnet access in `us-west-2` region
- `uv` - Fast Python package manager

**Optional (for local testing):**
- Docker, Finch, or Podman

## Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # Provide: Access Key ID, Secret Access Key, Region (us-west-2), Output (json)
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env to set AGENT_LOG_LEVEL (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   ```

## Run the Agent

### Local Testing (Optional)

Requires Docker, Finch, or Podman:

```bash
# Build and run in container
agentcore launch --local

# Test via HTTP
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?"}'
```

### Deploy to AWS

```bash
# Deploy (no Docker required)
agentcore launch

# Check status
agentcore status

# Test
agentcore invoke --prompt "Hello!"

# Clean up
agentcore destroy
```

## Deployment Options

```bash
agentcore launch              # Remote build (no Docker needed)
agentcore launch --local      # Local container testing
agentcore launch --local-build  # Local build, cloud deploy
```

## Add Custom Tools

1. Create tool in `tools/custom_tools.py`:

```python
from strands import tool

@tool
def weather_lookup(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather data for {city}"
```

2. Add to list:

```python
def get_custom_tools() -> List:
    return [text_analyzer, format_data, weather_lookup]
```

## Common Commands

```bash
# Dependencies
uv add package-name           # Add dependency
uv sync --upgrade             # Update all

# Development
uv run pytest                 # Run tests
uv run black agent/ tools/    # Format code
uv run ruff check agent/      # Lint code

# Python version
uv python install 3.13.5      # Install Python version
```

## Troubleshooting

**uv not found:**
```bash
source $HOME/.cargo/env  # macOS/Linux
```

**AWS credentials error:**
```bash
aws configure  # Reconfigure credentials
aws sts get-caller-identity  # Verify
```

**Model access denied:**
- Enable Bedrock service access
- Request Claude 3.7 Sonnet access in us-west-2
- Check IAM permissions: [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)

**Docker not installed (for --local):**
- Install Docker Desktop, Finch (`brew install finch`), or Podman
- Or skip local testing and deploy directly: `agentcore launch`

## Next Steps

- See [README.md](README.md) for project overview
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed AWS deployment
- Check example tools in `tools/custom_tools.py`
- Explore [Strands SDK](https://github.com/strands-agents/sdk-python) documentation
