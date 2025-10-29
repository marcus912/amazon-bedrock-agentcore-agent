"""Configuration management for the AWS AI Agent."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the agent."""

    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")
    AWS_PROFILE: str = os.getenv("AWS_PROFILE", "default")

    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "anthropic.claude-4-sonnet-v2:0"
    )

    # Agent Configuration
    AGENT_LOG_LEVEL: str = os.getenv("AGENT_LOG_LEVEL", "INFO")

    @classmethod
    def get_aws_region(cls) -> str:
        """Get the configured AWS region."""
        return cls.AWS_REGION

    @classmethod
    def get_bedrock_model_id(cls) -> str:
        """Get the configured Bedrock model ID."""
        return cls.BEDROCK_MODEL_ID

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        required_vars = ["AWS_REGION"]

        missing = []
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}"
            )

        return True


# Validate configuration on import
Config.validate()
