"""Main agent implementation using Strands SDK."""

from strands import Agent
from typing import Optional, List
import logging

# Import tools
from strands_tools.calculator import calculator
from strands_tools.tavily import tavily_search
from src.tools.custom_tools import get_custom_tools

logger = logging.getLogger(__name__)


def create_agent(
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    additional_tools: Optional[List] = None,
) -> Agent:
    """
    Create a Strands agent with specified configuration.

    Args:
        model: Model identifier (defaults to Bedrock Claude 3.7 Sonnet)
        system_prompt: Custom system prompt for the agent
        additional_tools: Additional tools to include beyond default tools

    Returns:
        Configured Strands Agent instance
    """
    # Default system prompt
    default_prompt = """You are a helpful AI assistant powered by AWS Bedrock.
You have access to various tools to help answer questions and perform tasks.
Always be concise, accurate, and helpful in your responses."""

    # Combine default tools with custom tools
    tools = [calculator, tavily_search] + get_custom_tools()

    # Add any additional tools passed by the user
    if additional_tools:
        tools.extend(additional_tools)

    logger.info(f"Creating agent with {len(tools)} tools")

    # Create the agent
    agent = Agent(
        tools=tools,
        system=system_prompt or default_prompt,
        model=model,  # Will default to Bedrock Claude 4 Sonnet if None
    )

    return agent


def run_agent(query: str, agent: Optional[Agent] = None) -> str:
    """
    Run the agent with a given query.

    Args:
        query: User query to process
        agent: Pre-configured agent (will create default if None)

    Returns:
        Agent response as string
    """
    if agent is None:
        agent = create_agent()

    logger.info(f"Processing query: {query[:100]}...")

    try:
        response = agent(query)
        return str(response)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise
