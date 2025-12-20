output "policy_name" {
  description = "Name of the inline IAM policy"
  value       = module.agent_iam.policy_name
}

output "role_name" {
  description = "Name of the role the policy is attached to"
  value       = module.agent_iam.role_name
}
