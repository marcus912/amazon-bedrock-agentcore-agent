"""Centralized configuration for the AWS AI Agent.

NOTE: For deployment, use ./bin/deploy.sh or pass environment variables via --env flags.
Local development automatically loads from .env file.
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration from environment variables."""

    # Logging
    LOG_LEVEL: str = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()

    # Model
    MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "")

    # GitHub MCP
    GITHUB_PAT: Optional[str] = os.getenv("GITHUB_PAT")

    # Prompt Configuration
    PROMPT_PROFILE: str = os.getenv("PROMPT_PROFILE", "default") or "default"

    # Note: Other env vars (KNOWLEDGE_BASE_ID, AWS_REGION, MIN_SCORE, etc.)
    # are used directly by strands_tools.retrieve, not via this config object

    @classmethod
    def get_log_level(cls) -> int:
        """Get logging level constant (defaults to INFO)."""
        return {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }.get(cls.LOG_LEVEL, logging.INFO)


def setup_logging():
    """Configure application logging from AGENT_LOG_LEVEL environment variable."""
    log_level = Config.get_log_level()
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )


def load_system_prompt() -> str:
    """Load system prompt from configuration.

    Loads prompt from config/prompts/{PROMPT_PROFILE}.txt
    Defaults to 'default' profile if PROMPT_PROFILE not set.

    Returns:
        System prompt string

    Raises:
        FileNotFoundError: If specified prompt file doesn't exist
    """
    prompts_dir = os.path.join(os.path.dirname(__file__), 'config', 'prompts')
    profile_path = os.path.join(prompts_dir, f"{config.PROMPT_PROFILE}.txt")

    if not os.path.exists(profile_path):
        raise FileNotFoundError(
            f"Prompt profile '{config.PROMPT_PROFILE}' not found at {profile_path}"
        )

    with open(profile_path, 'r') as f:
        return f.read().strip()


config = Config()
