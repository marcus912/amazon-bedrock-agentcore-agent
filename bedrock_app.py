"""Bedrock AgentCore application integration."""

from bedrock_agentcore import BedrockAgentCoreApp
from agent.strands_agent import create_agent, run_agent
from config import setup_logging
import logging

# Configure logging from environment variable
setup_logging()
logger = logging.getLogger(__name__)

# Create the Bedrock AgentCore app
app = BedrockAgentCoreApp()

# Create the Strands agent (will be initialized once and reused)
agent = None


def get_or_create_agent():
    """Get or create the Strands agent instance."""
    global agent
    if agent is None:
        logger.info("Initializing Strands agent...")
        agent = create_agent()
        logger.info("Agent initialized successfully")
    return agent


@app.entrypoint
def production_agent(request):
    """
    Main entrypoint for the Bedrock AgentCore application.

    This function is called for each request to the agent.
    It processes the request through the Strands agent and returns the response.

    Args:
        request: The incoming request from Bedrock AgentCore

    Returns:
        The agent's response
    """
    try:
        # Get the prompt from the request
        prompt = request.get("prompt", "")
        session_id = request.get("session_id", "unknown")

        logger.info(f"Processing request for session {session_id}")

        if not prompt:
            return {"error": "No prompt provided in request"}

        # Get the agent instance
        current_agent = get_or_create_agent()

        # Process the request through the Strands agent
        response = run_agent(prompt, current_agent)

        logger.info(f"Request processed successfully for session {session_id}")

        return {
            "response": response,
            "session_id": session_id,
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {
            "error": str(e),
            "session_id": request.get("session_id", "unknown"),
        }


if __name__ == "__main__":
    # Run the Bedrock AgentCore app
    logger.info("Starting Bedrock AgentCore application...")
    app.run()
