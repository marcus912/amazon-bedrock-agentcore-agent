"""Local testing script for the AWS AI Agent."""

import logging
from agent.strands_agent import create_agent, run_agent
from config import setup_logging

# Configure logging from environment variable
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Run the agent locally for testing."""
    print("=" * 60)
    print("AWS AI Agent - Local Testing")
    print("=" * 60)
    print()

    # Create the agent
    print("Initializing agent...")
    agent = create_agent()
    print("Agent initialized successfully!")
    print()

    # Interactive loop
    print("Enter your queries (type 'exit' or 'quit' to stop):")
    print("-" * 60)

    while True:
        try:
            # Get user input
            query = input("\nYou: ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            # Process the query
            print("\nAgent: ", end="", flush=True)
            response = run_agent(query, agent)
            print(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
