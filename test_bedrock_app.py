"""Local test script for bedrock_app.py"""

import sys
from bedrock_app import production_agent


def test_local():
    """Test the bedrock app locally by simulating requests."""
    print("=" * 60)
    print("Testing Bedrock AgentCore App Locally")
    print("=" * 60)
    print()
    print("This simulates requests that would come from Bedrock AgentCore.")
    print("Enter your queries (type 'exit' or 'quit' to stop):")
    print("-" * 60)

    session_id = "test-session-123"

    while True:
        try:
            # Get user input
            prompt = input("\nYou: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            # Create a mock request like Bedrock AgentCore would send
            mock_request = {
                "prompt": prompt,
                "session_id": session_id,
            }

            # Call the production agent entrypoint
            print("\nAgent: ", end="", flush=True)
            response = production_agent(mock_request)

            # Display the response
            if "error" in response:
                print(f"ERROR: {response['error']}")
            else:
                print(response.get("response", "No response"))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    test_local()
