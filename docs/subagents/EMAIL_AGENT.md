# Email Agent Sub Agent

## Overview
The Email Agent is a specialized sub-agent that sends emails via AWS SES (Simple Email Service). The orchestrator agent prepares the email content and provides all necessary details. This sub-agent parses the information, validates it, and sends the email.

**Important**: AWS SES operates in sandbox mode by default. In sandbox mode, you can only send emails to verified email addresses. Both the sender email and recipient emails must be verified in the AWS SES console until you request production access.

## Architecture

### Orchestrator → Sub-Agent Pattern
1. **Orchestrator** prepares email content (subject, body, recipients)
2. **Email Agent** receives structured data
3. **Email Agent** parses and validates
4. **Email Agent** calls AWS SES via boto3
5. **Email Agent** returns status and message ID

## Capabilities

- Parse email details from structured context
- Validate email addresses and required fields
- Send emails via AWS SES using boto3
- Support both plain text and HTML email bodies
- Handle TO, CC, BCC recipients
- Support Reply-To addresses
- Custom sender display name (friendly "From" format)
- Return AWS SES message IDs for tracking

## Validation

The Email Agent validates all data **before** calling the send_email_ses tool:

1. **Required Fields**:
   - Subject must not be empty
   - Body must not be empty
   - At least one recipient (TO, CC, or BCC) must be provided

2. **Email Format Validation**:
   - All email addresses (TO, CC, BCC, ReplyTo) are validated
   - Must contain exactly one @ symbol
   - Must have characters before and after @
   - Must follow basic email format (user@domain.com)

3. **Error Handling**:
   - If validation fails, returns `Status: Failed` immediately
   - Does NOT call send_email_ses if validation fails
   - Provides specific error message (e.g., "Invalid email address: user@")

This validation prevents unnecessary AWS SES API calls and provides faster feedback on invalid data.

## Usage

The Email Agent is invoked as a tool from the main agent:

```python
email_agent(
    task="Send email",
    recipients="user@company.com; cc:manager@company.com",
    context="""
    Subject: Project Update
    Body: The milestone has been completed successfully.
    ReplyTo: pm@company.com
    """
)
```

## Parameters

- **task** (str, required): Email action (usually "Send email")

- **recipients** (str, required): Email addresses in format:
  - Single: `"user@example.com"`
  - Multiple TO: `"user1@example.com, user2@example.com"`
  - With CC: `"to@example.com; cc:cc@example.com"`
  - With BCC: `"to@example.com; cc:cc@example.com; bcc:bcc@example.com"`

- **context** (str, required): Email details in key-value format:
  ```
  Subject: <subject line>
  Body: <email body content>
  ReplyTo: <optional reply-to address>
  ```

## Return Value

Success:
```
Status: Success
MessageID: <AWS SES message ID>
Recipients: <count of TO + CC + BCC>
Subject: <subject line>
```

Failure:
```
Status: Failed
Error: <error description>
```

## Configuration

### Environment Variables

```bash
# AWS SES Configuration
SES_SENDER_EMAIL=noreply@yourdomain.com  # Must be verified in SES
SES_SENDER_NAME=Your App Name            # Displayed in "From" field

# AWS Region
AWS_REGION=us-west-2

# Optional: Model ID for Email sub-agent (defaults to Claude Sonnet 4)
EMAIL_AGENT_MODEL_ID=
```

**SES_SENDER_EMAIL**: (required) Sender email address - must be verified in AWS SES

**SES_SENDER_NAME**: (optional) Friendly name shown to recipients (e.g., "Your App Name <noreply@yourdomain.com>")

**EMAIL_AGENT_MODEL_ID**: (optional) Leave empty to use Strands default (Claude Sonnet 4), or specify a Bedrock model ID

### AWS SES Setup

1. **Verify Sender Email:**
   ```bash
   aws ses verify-email-identity --email-address noreply@yourdomain.com
   ```
   Or verify via AWS Console: SES → Verified identities → Create identity

2. **Verify Recipient Emails (Sandbox Mode Only):**
   When in sandbox mode, all recipient email addresses must also be verified:
   ```bash
   aws ses verify-email-identity --email-address recipient@example.com
   ```
   Recipients will receive a verification email with a link to click.

3. **Move Out of Sandbox** (for production):
   - Request production access in AWS SES console (Identity Management → Account dashboard)
   - Production mode: Can send to any email address without verification
   - Includes higher sending limits and reputation monitoring

4. **IAM Permissions:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": [
         "ses:SendEmail",
         "ses:SendRawEmail"
       ],
       "Resource": "*"
     }]
   }
   ```

## Example

### Simple Email
```python
result = email_agent(
    task="Send email",
    recipients="user@company.com",
    context="""
    Subject: Welcome
    Body: Welcome to our platform!
    """
)
# Returns: "Status: Success\nMessageID: 01234...\nRecipients: 1\nSubject: Welcome"
```

### Email with CC/BCC
```python
result = email_agent(
    task="Send email",
    recipients="team@company.com; cc:manager@company.com; bcc:archive@company.com",
    context="""
    Subject: Weekly Update
    Body: This week's accomplishments...
    ReplyTo: pm@company.com
    """
)
# Returns: "Status: Success\nMessageID: 01234...\nRecipients: 3\nSubject: Weekly Update"
```

## Error Handling

Common errors:
- `Subject is required` - Missing Subject field
- `Body is required` - Missing Body field
- `At least one recipient is required` - No recipients provided
- `Invalid email address: <address>` - Malformed email address
- `SES sender email not configured` - Missing SES_SENDER_EMAIL
- `AWS SES Error: <code>` - AWS SES API error

## Tools Used Internally

The Email Agent sub-agent uses:
- **send_email_ses**: Boto3-based AWS SES sending tool

## Design Principles

1. **Simple Delegation**: Orchestrator handles composition, sub-agent handles delivery
2. **Structured Input**: Key-value format for reliable parsing
3. **Validation First**: Sub-agent validates all data before calling send_email_ses tool
4. **No Composition**: Sub-agent doesn't write email content
5. **Trust Orchestrator**: No authorization checks (orchestrator verified intent)
6. **Concise Output**: Structured status response for easy parsing

## Limitations

- **AWS SES Sandbox Mode**: Can only send to verified email addresses until production access is granted
- **Rate Limits**: 200 messages per 24 hours (sandbox mode), higher limits in production
- **Recipients**: Maximum 50 recipients per email (TO + CC + BCC combined)
- **Email Size**: Maximum 10 MB per email
- **Attachments**: Not currently supported (planned feature)
- **Email Format**: Supports both plain text and HTML email bodies

## Future Enhancements

- Attachment handling
- Email templates
- Retry logic for transient failures
- Bounce/complaint handling via SNS
- Advanced HTML email templates with inline CSS

## Testing

For testing without sending real emails, use AWS SES mailbox simulator:
```python
# These addresses trigger specific SES behaviors
recipients = "success@simulator.amazonses.com"  # Always succeeds
recipients = "bounce@simulator.amazonses.com"   # Simulates bounce
recipients = "complaint@simulator.amazonses.com" # Simulates complaint
```

## Security

- Never log email body content (may contain sensitive data)
- SES sender email must be verified to prevent spoofing
- Use IAM roles with minimal SES permissions
- Monitor bounce and complaint rates
- Implement rate limiting to prevent abuse
