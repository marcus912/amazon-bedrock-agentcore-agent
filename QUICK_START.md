# Quick Start Guide

Get your AWS AI Agent up and running in minutes with `uv`.

## Prerequisites

Make sure you have `uv` installed. If not, install it:

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

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS region and other settings
   ```

## Running the Agent

### Option 1: Using `uv run` (Recommended)

Run commands directly with uv (no need to activate virtual environment):

```bash
# Local testing
uv run python main.py

# Deploy to Bedrock AgentCore
uv run python src/bedrock_app.py
```

### Option 2: Activate Virtual Environment

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the agent
python main.py

# Deploy to Bedrock AgentCore
python src/bedrock_app.py

# Deactivate when done
deactivate
```

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
uv run black src/

# Lint code
uv run ruff check src/

# Type check
uv run mypy src/
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
├── src/
│   ├── agent/
│   │   └── strands_agent.py     # Main agent logic with Strands SDK
│   ├── tools/
│   │   └── custom_tools.py      # Custom tools (@tool decorated functions)
│   ├── bedrock_app.py           # Bedrock AgentCore entrypoint
│   └── config.py                # Configuration from .env
├── main.py                      # Local testing script (interactive CLI)
├── pyproject.toml               # Dependencies & project config (managed by uv)
├── uv.lock                      # Locked dependencies (auto-generated)
├── .python-version              # Python version (3.13.5)
└── .env                         # Your configuration (copy from .env.example)
```

## Key Dependencies

- **strands-agents**: Open-source framework for building AI agents
- **strands-agents-tools**: Pre-built tools (calculator, web_search, etc.)
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
- Default region name (e.g., us-west-2)
- Default output format (json)

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

## Why uv?

- **Fast**: 10-100x faster than pip for dependency resolution
- **Simple**: Single tool for Python versions, packages, and environments
- **Reliable**: Deterministic dependency resolution with `uv.lock`
- **Modern**: Native support for `pyproject.toml` (PEP 621)
- **All-in-one**: Replaces pip, pip-tools, virtualenv, pyenv, and more

## Next Steps

1. **Explore custom tools**: Check `src/tools/custom_tools.py` for examples
2. **Add your own tools**: Use the `@tool` decorator from Strands
3. **Customize prompts**: Edit system prompt in `src/agent/strands_agent.py`
4. **Deploy to production**: Use `src/bedrock_app.py` for Bedrock AgentCore
5. **Write tests**: Create a `tests/` directory and run `uv run pytest`
6. **Set up CI/CD**: Use GitHub Actions or AWS CodePipeline

## Additional Resources

- **Full Documentation**: See [README.md](README.md)
- **Strands SDK**: https://github.com/strands-agents/sdk-python
- **Bedrock AgentCore**: https://github.com/aws/bedrock-agentcore-sdk-python
- **uv Documentation**: https://docs.astral.sh/uv/
