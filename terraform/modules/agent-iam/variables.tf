variable "agent_name" {
  description = "Name of the agent (used for resource naming)"
  type        = string
}

variable "execution_role_name" {
  description = "Name of the existing AgentCore execution role to attach permissions to"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID (leave empty to skip KB permissions)"
  type        = string
  default     = ""
}

variable "ses_sender_email" {
  description = "SES sender email address (leave empty to skip SES permissions)"
  type        = string
  default     = ""
}

variable "ses_domain" {
  description = "SES domain (extracted from sender email if not provided)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
