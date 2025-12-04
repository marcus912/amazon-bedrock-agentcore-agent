"""Sub-agent implementations for specialized tasks."""

from strands import tool, Agent
from typing import List
import logging

logger = logging.getLogger(__name__)


@tool
def github_agent(task: str, context: str) -> str:
    """
    Execute GitHub operations (issues, PRs, code search, repository management).

    Args:
        task: Action to perform (e.g., "Create an issue", "List open pull requests")
        context: All information needed for the task:
            - Repository: owner/repo
            - Issue/PR details: title, description, labels
            - Search queries and filters

    Returns:
        Structured response: "Status: Success/Failed" with operation details (URLs, IDs) or error message
    """
    try:
        from config import load_system_prompt_by_name, config
        from mcp.client.streamable_http import streamablehttp_client
        from strands.tools.mcp import MCPClient

        logger.info(f"[github_agent] Starting - task: {task[:100]}...")
        logger.debug(f"[github_agent] Config GITHUB_AGENT_MODEL_ID: {repr(config.GITHUB_AGENT_MODEL_ID)}")

        # Load GitHub agent system prompt
        system_prompt = load_system_prompt_by_name("github_agent")
        logger.debug(f"[github_agent] System prompt loaded, length: {len(system_prompt) if system_prompt else 0}")

        # Create GitHub MCP client (only when github_agent is called)
        github_mcp_client = MCPClient(
            lambda: streamablehttp_client(
                url="https://api.githubcopilot.com/mcp/",
                headers={"Authorization": f"Bearer {config.GITHUB_PAT}"}
            )
        )
        logger.debug("[github_agent] MCP client created")

        # Create sub-agent with GitHub MCP tools
        with github_mcp_client:
            github_tools = github_mcp_client.list_tools_sync()
            logger.debug(f"[github_agent] MCP tools loaded: {len(github_tools)} tools")

            # Use configured model or None for Strands default (Sonnet 4)
            model_id = config.GITHUB_AGENT_MODEL_ID or None
            logger.debug(f"[github_agent] Creating Agent with model_id: {repr(model_id)}")

            github_sub_agent = Agent(
                tools=github_tools,
                system_prompt=system_prompt,
                model=model_id
            )
            logger.debug("[github_agent] Agent created successfully")

            # Construct the query for the sub-agent
            query = f"Task: {task}\n\nContext:\n{context}"

            # Execute the sub-agent
            logger.debug("[github_agent] Invoking sub-agent...")
            response = github_sub_agent(query)
            logger.info(f"[github_agent] Completed successfully, response length: {len(str(response))}")
            return str(response)

    except Exception as e:
        logger.error(f"[github_agent] Failed - {type(e).__name__}: {e}", exc_info=True)
        return f"Status: Failed\n\nError: {str(e)}\n\nDetails: An error occurred while executing the GitHub operation."


@tool
def email_agent(task: str, recipients: str, context: str) -> str:
    """
    Send emails via AWS SES.

    Args:
        task: Email action (usually "Send email")
        recipients: "to@example.com" or "to@example.com; cc:cc@example.com; bcc:bcc@example.com"
        context: Email details in key-value format:
            Subject: <subject line>
            Body: <email body content>
            ReplyTo: <optional reply-to address>

    Returns:
        Success: "Status: Success\\nMessageID: <id>\\nRecipients: <count>\\nSubject: <subject>"
        Failure: "Status: Failed\\nError: <description>"
    """
    try:
        from config import load_system_prompt_by_name, config
        from tools.ses_email import send_email_ses

        logger.info(f"[email_agent] Starting - task: {task}, recipients: {recipients}")
        logger.debug(f"[email_agent] Config EMAIL_AGENT_MODEL_ID: {repr(config.EMAIL_AGENT_MODEL_ID)}")

        # Load Email agent system prompt
        system_prompt = load_system_prompt_by_name("email_agent")
        logger.debug(f"[email_agent] System prompt loaded, length: {len(system_prompt) if system_prompt else 0}")

        # Use configured model or None for Strands default (Sonnet 4)
        model_id = config.EMAIL_AGENT_MODEL_ID or None
        logger.debug(f"[email_agent] Creating Agent with model_id: {repr(model_id)}")

        # Create sub-agent with AWS SES tool
        email_sub_agent = Agent(
            tools=[send_email_ses],
            system_prompt=system_prompt,
            model=model_id
        )
        logger.debug("[email_agent] Agent created successfully")

        # Construct the query for the sub-agent
        query = f"Task: {task}\n\nRecipients: {recipients}\n\nContext:\n{context}"

        # Execute the sub-agent (will parse details and call send_email_ses)
        logger.debug("[email_agent] Invoking sub-agent...")
        response = email_sub_agent(query)
        logger.info(f"[email_agent] Completed successfully, response length: {len(str(response))}")

        return str(response)

    except Exception as e:
        logger.error(f"[email_agent] Failed - {type(e).__name__}: {e}", exc_info=True)
        return f"Status: Failed\n\nError: {str(e)}\n\nDetails: An error occurred while processing the email."


def get_subagent_tools() -> List:
    """
    Get all sub-agent tools.

    Returns:
        List of sub-agent tool functions
    """
    return [github_agent, email_agent]
