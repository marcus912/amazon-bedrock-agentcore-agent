# Agent IAM Permissions Module
# Attaches service permissions to an existing AgentCore execution role

data "aws_caller_identity" "current" {}

# Policy document for agent service permissions
data "aws_iam_policy_document" "agent_permissions" {
  # Bedrock Knowledge Base permissions
  dynamic "statement" {
    for_each = var.knowledge_base_id != "" ? [1] : []
    content {
      sid    = "BedrockKnowledgeBaseAccess"
      effect = "Allow"
      actions = [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ]
      resources = [
        "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:knowledge-base/${var.knowledge_base_id}"
      ]
    }
  }

  # SES permissions
  dynamic "statement" {
    for_each = var.ses_sender_email != "" ? [1] : []
    content {
      sid    = "SESSendEmail"
      effect = "Allow"
      actions = [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ]
      resources = [
        "arn:aws:ses:${var.aws_region}:${data.aws_caller_identity.current.account_id}:identity/${var.ses_domain}",
        "arn:aws:ses:${var.aws_region}:${data.aws_caller_identity.current.account_id}:identity/${var.ses_sender_email}"
      ]
    }
  }
}

# Create inline policy on the execution role
resource "aws_iam_role_policy" "agent_permissions" {
  name   = "${var.agent_name}-permissions"
  role   = var.execution_role_name
  policy = data.aws_iam_policy_document.agent_permissions.json
}
