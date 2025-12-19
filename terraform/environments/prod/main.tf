terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use remote state
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "agent/prod/terraform.tfstate"
  #   region = "us-west-2"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "prod"
      ManagedBy   = "terraform"
      Project     = "bedrock-agent"
    }
  }
}

module "agent_iam" {
  source = "../../modules/agent-iam"

  agent_name          = var.agent_name
  execution_role_name = var.execution_role_name
  aws_region          = var.aws_region
  knowledge_base_id   = var.knowledge_base_id
  ses_sender_email    = var.ses_sender_email
  ses_domain          = var.ses_domain

  tags = {
    Environment = "prod"
    Agent       = var.agent_name
  }
}
