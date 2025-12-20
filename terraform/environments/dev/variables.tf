variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "agent_name" {
  description = "Name of the agent"
  type        = string
  default     = "my_agent_dev"
}

variable "execution_role_name" {
  description = "Name of the AgentCore execution role (without ARN prefix)"
  type        = string
  # Get this from .bedrock_agentcore.yaml after first deployment
}

variable "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  type        = string
  default     = ""
}

variable "ses_sender_email" {
  description = "SES verified sender email"
  type        = string
  default     = ""
}

variable "ses_domain" {
  description = "SES verified domain"
  type        = string
  default     = ""
}
