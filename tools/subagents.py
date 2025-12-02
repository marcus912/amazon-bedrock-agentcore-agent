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

        # Load GitHub agent system prompt
        system_prompt = load_system_prompt_by_name("github_agent")

        # Create GitHub MCP client (only when github_agent is called)
        github_mcp_client = MCPClient(
            lambda: streamablehttp_client(
                url="https://api.githubcopilot.com/mcp/",
                headers={"Authorization": f"Bearer {config.GITHUB_PAT}"}
            )
        )

        # Create sub-agent with GitHub MCP tools
        with github_mcp_client:
            github_tools = github_mcp_client.list_tools_sync()

            # Use configured model or None for Strands default (Sonnet 4)
            model_id = config.GITHUB_AGENT_MODEL_ID or None

            github_sub_agent = Agent(
                tools=github_tools,
                system_prompt=system_prompt,
                model=model_id
            )

            # Construct the query for the sub-agent
            query = f"Task: {task}\n\nContext:\n{context}"

            # Execute the sub-agent
            response = github_sub_agent(query)
            return str(response)

    except Exception as e:
        logger.error(f"Error in github_agent: {e}", exc_info=True)
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

        # Load Email agent system prompt
        system_prompt = load_system_prompt_by_name("email_agent")

        # Use configured model or None for Strands default (Sonnet 4)
        model_id = config.EMAIL_AGENT_MODEL_ID or None

        # Create sub-agent with AWS SES tool
        email_sub_agent = Agent(
            tools=[send_email_ses],
            system_prompt=system_prompt,
            model=model_id
        )

        # Construct the query for the sub-agent
        query = f"Task: {task}\n\nRecipients: {recipients}\n\nContext:\n{context}"

        # Execute the sub-agent (will parse details and call send_email_ses)
        response = email_sub_agent(query)

        return str(response)

    except Exception as e:
        logger.error(f"Error in email_agent: {e}", exc_info=True)
        return f"Status: Failed\n\nError: {str(e)}\n\nDetails: An error occurred while processing the email."


def get_subagent_tools() -> List:
    """
    Get all sub-agent tools.

    Returns:
        List of sub-agent tool functions
    """
    return [github_agent, email_agent]
