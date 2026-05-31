import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage
import argparse


DEFAULT_PROMPT = (
    "Review utils.py for bugs that would cause crashes. Fix any issues you find."
)


async def main(args):
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt=args.prompt if args.prompt else DEFAULT_PROMPT,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob", "Bash"],  # Auto-approve these tools
            permission_mode="acceptEdits",  # Auto-approve file edits
            system_prompt="You are a senior Python developer. Always follow PEP 8 style guidelines.",
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)  # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # Final result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt to send to the Claude agent")
    args = parser.parse_args()

    asyncio.run(main(args))
