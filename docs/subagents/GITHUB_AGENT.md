# GitHub Agent Sub Agent

## Overview
The GitHub Agent is a specialized sub-agent designed to handle GitHub-related operations using the GitHub MCP (Model Context Protocol) tools. It provides intelligent automation for repository management, issue tracking, pull request operations, and code analysis.

## Capabilities

### Repository Operations
- List repositories for a user or organization
- Get repository details and metadata
- Search across repositories
- Manage repository settings

### Issue Management
- Create new issues with detailed descriptions
- Update existing issues
- Search and filter issues
- Add labels, milestones, and assignees
- Comment on issues

### Pull Request Operations
- Create pull requests
- Review and comment on PRs
- Merge pull requests
- Check PR status and CI/CD results

### Code Operations
- Search code across repositories
- Get file contents
- Create and update files
- Analyze code structure

## Usage

The GitHub Agent is invoked as a tool from the main agent:

```python
github_agent(
    task="Create an issue for bug report",
    context="User reported login failure on mobile app"
)
```

## Parameters

- **task** (str, required): The specific GitHub task to perform
  - Examples: "Create an issue", "Review pull request #123", "Search for TODO comments"

- **context** (str, required): Additional context, details, or data needed to complete the task
  - Can include: issue descriptions, code snippets, repository names, search criteria

## Return Value

Returns a structured string response:

**Success:**
```
Status: Success

Operation: [What was done]
Repository: [owner/repo]
URL: [Link to resource]

Details: [Additional information]
```

**Failure:**
```
Status: Failed

Error: [What went wrong]
Solution: [How to fix it]
```

## Examples

### Example 1: Create an Issue
```python
result = github_agent(
    task="Create a bug report issue",
    context="""
    Repository: myorg/myapp
    Title: Login fails on iOS Safari
    Description: Users on iOS Safari can't login after the latest update.
    Steps to reproduce: Open app in iOS Safari, click login, observe error.
    Labels: bug, mobile
    """
)
```

### Example 2: Search Code
```python
result = github_agent(
    task="Search for deprecated API usage",
    context="""
    Repository: myorg/myapp
    Search for: deprecated_function calls
    File types: .py
    """
)
```

### Example 3: Review Pull Request
```python
result = github_agent(
    task="Review pull request and check for security issues",
    context="""
    Repository: myorg/myapp
    PR Number: 456
    Focus: Check for SQL injection vulnerabilities and hardcoded secrets
    """
)
```

## Configuration

### Environment Variables

```bash
# GitHub Personal Access Token (required)
GITHUB_PAT=ghp_your_token_here

# Optional: Model ID for GitHub sub-agent (defaults to Claude Sonnet 4)
GITHUB_AGENT_MODEL_ID=

# AWS Region for Bedrock
AWS_REGION=us-west-2
```

**GITHUB_PAT**: GitHub Personal Access Token (required)
- Must have appropriate scopes for the operations needed
- Recommended scopes: `repo`, `write:discussion`, `read:org`
- Get token from: GitHub Settings → Developer settings → Personal access tokens

**GITHUB_AGENT_MODEL_ID**: (optional)
- Leave empty to use Strands default (Claude Sonnet 4)
- Override to use specific Bedrock model for github_agent

### GitHub MCP Client
The agent creates a GitHub MCP client when invoked:
```python
# Created inside github_agent function when called
github_mcp_client = MCPClient(
    lambda: streamablehttp_client(
        url="https://api.githubcopilot.com/mcp/",
        headers={"Authorization": f"Bearer {config.GITHUB_PAT}"}
    )
)
```

This lazy initialization ensures the GitHub MCP client is only created when the github_agent is actually used, keeping the orchestrator agent lightweight.

## System Prompt

The GitHub Agent uses a specialized system prompt (`config/prompts/github_agent.txt`) that:
- Focuses on GitHub operations
- Understands GitHub conventions and best practices
- Formats responses appropriately for GitHub (markdown, labels, etc.)
- Handles errors gracefully
- Validates inputs before making API calls

## Error Handling

The agent handles common errors:
- Invalid repository names
- Permission issues
- API rate limits
- Network failures
- Invalid GitHub PAT

Errors are returned in the response with clear descriptions and suggested fixes.

## Best Practices

1. **Be Specific**: Provide clear, specific tasks and detailed context
2. **Include Repository**: Always specify the target repository
3. **Use Proper Formatting**: Use markdown for issue/PR descriptions
4. **Handle Sensitive Data**: Never include secrets or credentials in issue descriptions
5. **Check Permissions**: Ensure the GitHub PAT has necessary permissions

## Limitations

- Cannot perform destructive operations without explicit confirmation
- Rate limited by GitHub API (typically 5000 requests/hour for authenticated users)
- Cannot access private repositories without appropriate PAT permissions
- Cannot perform GitHub Actions workflow operations (by design)

## Integration with Main Agent

The main agent can delegate GitHub-specific tasks to this sub-agent when:
- User explicitly mentions GitHub operations
- Task involves repository, issue, or PR management
- Code search or analysis is needed
- GitHub automation is requested

The main agent's system prompt should guide it to use the github_agent tool for these scenarios.
