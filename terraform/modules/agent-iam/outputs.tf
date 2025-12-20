output "policy_name" {
  description = "Name of the inline IAM policy"
  value       = aws_iam_role_policy.agent_permissions.name
}

output "role_name" {
  description = "Name of the role the policy is attached to"
  value       = aws_iam_role_policy.agent_permissions.role
}
