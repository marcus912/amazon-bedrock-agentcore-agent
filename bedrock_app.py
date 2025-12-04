"""Bedrock AgentCore application integration."""

from bedrock_agentcore import BedrockAgentCoreApp
from agent.strands_agent import create_agent
from config import setup_logging, config
from tools import get_custom_tools, get_subagent_tools
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# Initialize tools once at startup
logger.debug("Initializing tools...")

# Custom utility tools
CUSTOM_TOOLS = get_custom_tools()
logger.debug(f"Initialized {len(CUSTOM_TOOLS)} custom utility tools")

# Sub-agent tools (github_agent, email_agent)
SUBAGENT_TOOLS = get_subagent_tools()
logger.debug(f"Initialized {len(SUBAGENT_TOOLS)} sub-agent tools")

# Combine tools for main agent
# Note: retrieve tool is added by create_agent()
# Note: github_agent sub-agent manages its own GitHub MCP tools internally
AGENT_TOOLS = CUSTOM_TOOLS + SUBAGENT_TOOLS
logger.info(f"Total tools available: {len(AGENT_TOOLS)}")


@app.entrypoint
def production_agent(request):
    """Main entrypoint for Bedrock AgentCore application.

    Args:
        request: Incoming request from Bedrock AgentCore

    Returns:
        Dict with response or error
    """
    session_id = request.get("session_id", "unknown")

    try:
        prompt = request.get("prompt", "")
        if not prompt:
            return {"error": "No prompt provided", "session_id": session_id}

        logger.info(f"Processing request (session: {session_id})")

        # Create agent with custom tools and sub-agents
        agent = create_agent(model=config.MODEL_ID, additional_tools=AGENT_TOOLS)
        response = agent(prompt)

        logger.info(f"Request processed (session: {session_id})")
        return {"response": str(response), "session_id": session_id}

    except Exception as e:
        logger.error(f"Error (session: {session_id}): {e}", exc_info=True)
        return {"error": str(e), "session_id": session_id}


if __name__ == "__main__":
    logger.info("Starting Bedrock AgentCore application...")
    app.run()
