"""Centralized configuration for the AWS AI Agent."""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Logging configuration
    LOG_LEVEL: str = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()

    # You can add more configuration variables here as needed
    # Example:
    # AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")
    # MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-4-sonnet-v2:0")

    @classmethod
    def get_log_level(cls) -> int:
        """
        Get the logging level as a logging constant.

        Returns:
            Logging level constant (defaults to INFO if not set or invalid)
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(cls.LOG_LEVEL, logging.INFO)


def setup_logging():
    """
    Configure logging for the entire application.

    Reads AGENT_LOG_LEVEL from environment and sets up basicConfig.
    """
    log_level = Config.get_log_level()

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )

    # Log the configured level for debugging
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured with level: {logging.getLevelName(log_level)}")


# Convenience reference
config = Config()
