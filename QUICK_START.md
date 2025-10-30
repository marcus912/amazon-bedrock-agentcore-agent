# Quick Start Guide

Get your AWS AI Agent up and running in minutes with `uv`.

## Prerequisites

### Required
- **Python 3.10+** (this project uses 3.13.5)
- **AWS Account** with Bedrock access
- **Claude 3.7 Sonnet** access in `us-west-2` region (default model)
- **uv** - Fast Python package manager

### Optional (for local containerized testing)
- **Docker**, **Finch**, or **Podman** - Only needed if you want to test with `agentcore launch --local`

Install `uv` if not already installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew (macOS)
brew install uv

# Or via pip
pip install uv
```

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

   This will:
   - Create a virtual environment in `.venv`
   - Install all project dependencies
   - Lock dependencies in `uv.lock`

2. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

   You'll need:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region: `us-west-2`
   - Default output format: `json`

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Key settings in `.env`:
   ```bash
   # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
   AGENT_LOG_LEVEL=INFO
   ```

   Note: AWS credentials and region are configured via `aws configure` command, not in `.env`

## Running the Agent

### Option 1: Simple Local Testing (Recommended for Quick Start)

Run commands directly with uv (no need to activate virtual environment):

```bash
# Interactive CLI testing
uv run python main.py

# Test bedrock_app.py entrypoint (simulates AgentCore requests)
uv run python test_bedrock_app.py
```

This is the fastest way to test your agent logic without Docker or AWS.

### Option 2: Local Testing with Docker (Full Production Simulation)

Test your agent in a containerized environment (requires Docker, Finch, or Podman):

```bash
# Build and run locally in a container
uv run python agentcore launch --local

# The agent will be available at http://localhost:8080
# Test it with:
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, agent!"}'
```

**Requirements**: Docker, Finch, or Podman installed
**Note**: Make sure port 8080 is free before starting
**Architecture**: Containers are built for ARM64 (AWS Graviton)

### Option 3: AWS Deployment

Deploy your agent to AWS Bedrock AgentCore:

```bash
# Remote build and deploy (no Docker required)
uv run python agentcore launch

# Local build, cloud deploy (requires Docker/Finch/Podman)
uv run python agentcore launch --local-build

# Check deployment status
uv run python agentcore status

# Test deployed agent
uv run python agentcore invoke --prompt "Hello, agent!"
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Option 4: Activate Virtual Environment

If you prefer working with an activated environment:


## Common Commands

### Dependency Management

All dependencies are managed in `pyproject.toml`. Use these commands to manage them:

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name

# Update all dependencies
uv sync --upgrade

# Install dev dependencies (pytest, black, ruff, mypy)
uv sync --extra dev

# Export to requirements.txt (if needed for legacy systems)
uv pip compile pyproject.toml -o requirements.txt
```

### Development Tools

```bash
# Run tests
uv run pytest

# Format code
uv run black agent/ tools/ *.py

# Lint code
uv run ruff check agent/ tools/ *.py

# Type check
uv run mypy agent/ tools/ *.py
```

### Python Version Management

The project uses Python 3.13.5 as specified in `.python-version`. uv will automatically use this version if available, or you can install it:

```bash
# uv can install Python versions for you
uv python install 3.13.5

# List installed Python versions
uv python list

# List all available Python versions
uv python list --all-versions
```

## Project Structure

```
aws-ai-agent/
├── agent/
│   └── strands_agent.py         # Main agent logic with Strands SDK
├── tools/
│   └── custom_tools.py          # Custom tools (@tool decorated functions)
├── bedrock_app.py               # Bedrock AgentCore entrypoint
├── main.py                      # Local testing script (interactive CLI)
├── test_bedrock_app.py          # Test bedrock app locally
├── config.py                    # Centralized configuration (loads .env)
├── agentcore                    # CLI for AWS deployment
├── pyproject.toml               # Dependencies & project config (managed by uv)
├── uv.lock                      # Locked dependencies (auto-generated)
├── .python-version              # Python version (3.13.5)
└── .env                         # Your configuration (copy from .env.example)
```

## Key Dependencies

- **strands-agents**: Open-source framework for building AI agents
- **strands-agents-tools**: Pre-built tools (calculator, tavily_search, etc.)
- **bedrock-agentcore**: Deploy to AWS managed infrastructure
- **boto3**: AWS SDK for additional AWS service integrations
- **python-dotenv**: Load environment variables from .env

## Testing the Agent

Once running `main.py`, you can interact with the agent:

```
You: What is the square root of 144?
Agent: The square root of 144 is 12.

You: Analyze this text: "Hello world, this is a test."
Agent: [Returns statistics about the text]

You: What AWS region is us-west-2?
Agent: [Returns information about the Oregon region]
```

Type `exit`, `quit`, or `q` to stop the agent.

## Creating Custom Tools

Add custom tools using the `@tool` decorator with clear docstrings:

```python
from strands import tool

@tool
def weather_lookup(city: str) -> str:
    """
    Get current weather for a city.

    The docstring is important - the LLM uses it to understand
    when and how to use this tool.

    Args:
        city: Name of the city

    Returns:
        Weather description
    """
    # Your implementation here
    return f"Weather data for {city}"
```

**Key principles:**
- ✅ Use descriptive docstrings (LLM reads these!)
- ✅ Type hints for parameters and return values
- ✅ Keep tools focused on one task
- ✅ Handle errors gracefully

Add your tool to `tools/custom_tools.py`:

```python
def get_custom_tools() -> List:
    return [text_analyzer, format_data, aws_region_info, weather_lookup]
```

## Understanding Your Agent

### Agent Architecture

```python
# In agent/strands_agent.py
from strands import Agent
from strands_tools.calculator import calculator
from strands_tools.tavily import tavily_search
from tools.custom_tools import get_custom_tools

# Agent combines built-in and custom tools
agent = Agent(
    tools=[calculator, tavily_search] + get_custom_tools(),
    system="Your custom prompt here",
    model=None  # Defaults to Bedrock Claude 3.7 Sonnet
)
```

**Available Built-in Tools:**
- `calculator` - Math calculations
- `tavily_search` - Web search
- Many more in `strands-agents-tools` package

**Model Providers:**
The agent defaults to Amazon Bedrock (Claude 3.7 Sonnet) but supports:
- Anthropic
- Google Gemini
- OpenAI
- Ollama (local)
- LiteLLM (proxy)
- Custom providers

## Common Patterns

### Pattern 1: Simple Query Agent
```python
from agent.strands_agent import create_agent

agent = create_agent()
response = agent("What is 2 + 2?")
print(response)
```

### Pattern 2: Custom System Prompt
```python
agent = create_agent(
    system_prompt="You are a helpful math tutor. Explain step-by-step."
)
response = agent("What is the quadratic formula?")
```

### Pattern 3: Additional Tools
```python
from strands_tools.http_request import http_request

agent = create_agent(additional_tools=[http_request])
response = agent("Fetch data from https://api.example.com")
```

### Pattern 4: Different Model
```python
# Use a different Bedrock model
agent = create_agent(model="anthropic.claude-3-5-sonnet-20241022-v2:0")

# Or use OpenAI
agent = create_agent(model="gpt-4o")  # Requires OpenAI API key
```

## Troubleshooting

### uv command not found
Make sure uv is in your PATH. After installation, restart your terminal or run:
```bash
source $HOME/.cargo/env  # macOS/Linux
```

### AWS credentials not configured
Run `aws configure` and provide:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., `us-west-2`)
- Default output format (`json`)

**Important**: Bedrock requires `us-west-2` for Claude 3.7 Sonnet.

### Module not found errors
Make sure dependencies are installed:
```bash
uv sync
```

### Python version mismatch
Install the correct Python version:
```bash
uv python install 3.13.5
```

### "Access denied" or model errors
Ensure you have:
1. ✅ AWS Bedrock service access enabled
2. ✅ Claude 3.7 Sonnet model access in `us-west-2`
3. ✅ Correct IAM permissions for Bedrock API calls

Request model access: [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/) → Model access

### Docker/Podman/Finch not installed (for --local testing)
For local containerized testing, install one of:
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
- **Finch** (AWS, macOS/Linux): `brew install finch`
- **Podman**: https://podman.io/getting-started/installation

If you don't need containerized testing, use Option 1 (Simple Local Testing) instead.

## Quick Reference

### Testing Commands
```bash
# Simple local testing (no Docker required)
uv run python main.py                      # Interactive CLI
uv run python test_bedrock_app.py          # Test bedrock_app entrypoint

# Local containerized testing (requires Docker/Finch/Podman)
uv run python agentcore launch --local     # Build and run in container
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

### Deployment Commands
```bash
# Deploy to AWS
uv run python agentcore launch             # Remote build (no Docker needed)
uv run python agentcore launch --local-build  # Local build, cloud deploy

# Manage deployment
uv run python agentcore status             # Check status
uv run python agentcore invoke --prompt "Hi"  # Test deployed agent
uv run python agentcore destroy            # Remove all resources
```

### Development Commands
```bash
# Dependencies
uv sync                                    # Install dependencies
uv add package-name                        # Add dependency

# Code quality
uv run pytest                              # Run tests
uv run black agent/ tools/ *.py           # Format code
uv run ruff check agent/ tools/ *.py      # Lint code
```

## Next Steps

1. **Explore custom tools**: Check `tools/custom_tools.py` for examples
2. **Add your own tools**: Use the `@tool` decorator from Strands
3. **Customize prompts**: Edit system prompt in `agent/strands_agent.py`
4. **Deploy to AWS**: See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment guide
5. **Write tests**: Create a `tests/` directory and run `uv run pytest`

## Additional Resources

- **Full Documentation**: See [README.md](README.md)
- **Strands SDK**: https://github.com/strands-agents/sdk-python
- **Bedrock AgentCore**: https://github.com/aws/bedrock-agentcore-sdk-python
- **uv Documentation**: https://docs.astral.sh/uv/
