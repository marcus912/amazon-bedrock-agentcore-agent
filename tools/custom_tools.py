"""Custom tools for the Strands agent."""

from strands import tool
from typing import List
import logging

logger = logging.getLogger(__name__)


@tool
def text_analyzer(text: str) -> dict:
    """
    Analyze text and return basic statistics.

    Args:
        text: The text to analyze

    Returns:
        Dictionary containing word count, character count, and sentence count
    """
    words = text.split()
    sentences = text.split('.')

    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
    }


@tool
def format_data(data: str, output_format: str = "json") -> str:
    """
    Format data into specified output format.

    Args:
        data: Input data as string
        output_format: Desired format (json, yaml, xml)

    Returns:
        Formatted data string
    """
    import json

    if output_format.lower() == "json":
        try:
            # Try to parse and pretty-print if it's already JSON
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # If not JSON, wrap it
            return json.dumps({"data": data}, indent=2)
    elif output_format.lower() == "yaml":
        # Note: Would need PyYAML installed for full YAML support
        return f"data: {data}"
    else:
        return data


@tool
def aws_region_info(region: str = "us-west-2") -> dict:
    """
    Get information about an AWS region.

    Args:
        region: AWS region code (e.g., us-west-2, us-east-1)

    Returns:
        Dictionary with region information
    """
    # Common AWS regions and their details
    regions = {
        "us-east-1": {"name": "US East (N. Virginia)", "location": "North Virginia"},
        "us-east-2": {"name": "US East (Ohio)", "location": "Ohio"},
        "us-west-1": {"name": "US West (N. California)", "location": "Northern California"},
        "us-west-2": {"name": "US West (Oregon)", "location": "Oregon"},
        "eu-west-1": {"name": "Europe (Ireland)", "location": "Ireland"},
        "eu-central-1": {"name": "Europe (Frankfurt)", "location": "Frankfurt"},
        "ap-northeast-1": {"name": "Asia Pacific (Tokyo)", "location": "Tokyo"},
        "ap-southeast-1": {"name": "Asia Pacific (Singapore)", "location": "Singapore"},
    }

    return regions.get(
        region,
        {"name": f"Unknown region: {region}", "location": "Unknown"}
    )


def get_custom_tools() -> List:
    """
    Get all custom tools for the agent.

    Returns:
        List of custom tool functions
    """
    return [text_analyzer, format_data, aws_region_info]
