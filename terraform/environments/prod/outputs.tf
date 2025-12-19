output "policy_arn" {
  description = "ARN of the agent permissions policy"
  value       = module.agent_iam.policy_arn
}

output "policy_name" {
  description = "Name of the agent permissions policy"
  value       = module.agent_iam.policy_name
}
