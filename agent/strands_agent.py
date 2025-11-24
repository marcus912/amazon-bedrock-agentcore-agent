"""Main agent implementation using Strands SDK."""

from strands import Agent
from typing import Optional, List
import logging

from strands_tools import retrieve
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from config import config

logger = logging.getLogger(__name__)

# GitHub MCP client (requires GITHUB_PAT environment variable)
github_mcp_client = MCPClient(
    lambda: streamablehttp_client(
        url="https://api.githubcopilot.com/mcp/",
        headers={"Authorization": f"Bearer {config.GITHUB_PAT}"}
    )
)


def create_agent(
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    additional_tools: Optional[List] = None,
    session_manager=None,
) -> Agent:
    """Create a Strands agent with specified configuration.

    Args:
        model: Model identifier (defaults to Claude Sonnet 4.5)
        system_prompt: Custom system prompt
        additional_tools: Additional tools beyond default retrieve tool
        session_manager: Session manager for conversation persistence

    Returns:
        Configured Agent instance
    """
    default_prompt = """You are LAILA. Convert ONE email into ONE GitHub issue, then STOP.

Workflow:
1. Retrieve github bug issue guide from knowledge base
2. Validate email has required fields (steps to reproduce, error details, environment)
3. Create ONE issue using issue_write MCP tool
4. Return result and STOP

Hard Stop Conditions (return error and STOP immediately):
- Guide not found in knowledge base
- Email missing required fields
- ANY MCP tool error (authentication, 404, 403, API failures)

MCP Tool Failure Protocol:
- Return: "ERROR: GitHub MCP tool failed - [exact error]"
- STOP immediately - DO NOT retry or attempt workarounds

Response Format:
- Success: "✓ Issue created: [URL]\\n\\nSummary: [brief]"
- Error: "ERROR: [what failed]"

One issue per request. No exceptions."""

    tools = [retrieve]
    if additional_tools:
        tools.extend(additional_tools)

    logger.info(f"Creating agent with {len(tools)} tools")

    return Agent(
        tools=tools,
        system_prompt=system_prompt or default_prompt,
        model=model,
        session_manager=session_manager,
    )


def run_agent(query: str, agent: Optional[Agent] = None) -> str:
    """Run the agent with a given query.

    Args:
        query: User query to process
        agent: Pre-configured agent (creates default if None)

    Returns:
        Agent response as string
    """
    if agent is None:
        agent = create_agent()

    logger.info(f"Processing query: {query[:100]}...")
    try:
        response = agent(query)
        logger.info("Query processed successfully")
        return str(response)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise
