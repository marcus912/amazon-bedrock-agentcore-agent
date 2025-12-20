# Terraform IAM Configuration

Manages IAM permissions for Bedrock AgentCore agents using Terraform.

## Structure

```
terraform/
├── modules/
│   └── agent-iam/           # Reusable IAM module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/                 # Dev environment
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── outputs.tf
│   └── prod/                # Prod environment
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── outputs.tf
└── README.md
```

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured
- Agent deployed at least once (to create execution role)

## Usage

### 1. Update Configuration

Edit `terraform/environments/{env}/terraform.tfvars` with your values:

```hcl
agent_name          = "my_agent_dev"
execution_role_name = "AmazonBedrockAgentCoreSDKRuntime-us-west-2-xxxxx"
knowledge_base_id   = "YOUR_KB_ID"
ses_sender_email    = "sender@yourdomain.com"
ses_domain          = "yourdomain.com"
```

### 2. Initialize and Apply

```bash
# Dev environment
cd terraform/environments/dev
terraform init
terraform plan
terraform apply

# Prod environment
cd terraform/environments/prod
terraform init
terraform plan
terraform apply
```

### 3. Verify

```bash
# Check the policy was created
aws iam get-role-policy --role-name YOUR_ROLE_NAME --policy-name my_agent_dev-permissions
```

## Permissions Created

The module creates an IAM policy with:

| Service | Actions | Resource |
|---------|---------|----------|
| Bedrock KB | `bedrock:Retrieve`, `bedrock:RetrieveAndGenerate` | Knowledge Base ARN |
| SES | `ses:SendEmail`, `ses:SendRawEmail` | Domain and email identity ARNs |

## Getting Execution Role Name

After first deployment with `agentcore launch`, find the role in `.bedrock_agentcore.yaml`:

```yaml
agents:
  my_agent_dev:
    aws:
      execution_role: arn:aws:iam::123456789:role/AmazonBedrockAgentCoreSDKRuntime-us-west-2-xxxxx
```

Extract the role name (part after `role/`).

## Remote State (Optional)

Uncomment the backend block in `main.tf` to use S3 remote state:

```hcl
backend "s3" {
  bucket = "your-terraform-state-bucket"
  key    = "agent/dev/terraform.tfstate"
  region = "us-west-2"
}
```

## Terraform vs Bash Script

| Approach | Use When |
|----------|----------|
| Terraform | Want IaC, version control, drift detection |
| `bin/setup-agent-permissions.sh` | Quick setup, no Terraform experience |

Both approaches are valid. Use `--skip-iam` with deploy.sh if using Terraform.
