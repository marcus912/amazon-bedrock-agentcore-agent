"""Bedrock AgentCore application integration."""

from bedrock_agentcore import BedrockAgentCoreApp
from agent.strands_agent import create_agent, github_mcp_client
from config import setup_logging, config
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# Initialize GitHub MCP tools once at startup (tools are static)
logger.info("Initializing GitHub MCP tools...")
with github_mcp_client:
    GITHUB_TOOLS = github_mcp_client.list_tools_sync()
logger.info(f"Initialized {len(GITHUB_TOOLS)} GitHub MCP tools")


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

        # MCP client context needed for tool execution
        with github_mcp_client:
            agent = create_agent(model=config.MODEL_ID, additional_tools=GITHUB_TOOLS)
            response = agent(prompt)

        logger.info(f"Request processed (session: {session_id})")
        return {"response": str(response), "session_id": session_id}

    except Exception as e:
        logger.error(f"Error (session: {session_id}): {e}", exc_info=True)
        return {"error": str(e), "session_id": session_id}


if __name__ == "__main__":
    logger.info("Starting Bedrock AgentCore application...")
    app.run()
