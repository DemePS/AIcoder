import asyncio
from aio_stdout import ainput, aprint
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    AssistantMessage,
)
import argparse


async def _print_message(message: AssistantMessage | ResultMessage) -> None:
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if hasattr(block, "text"):
                await aprint(block.text)
            elif hasattr(block, "name"):
                await aprint(f"Tool: {block.name}")
    elif isinstance(message, ResultMessage):
        await aprint(f"Done: {message.subtype}")


async def main(initial_prompt: str) -> None:

    options = ClaudeAgentOptions(
        tools=[],
        allowed_tools=[
            "mcp__powerbi-modeling-mcp__*",
        ],
        permission_mode="dontAsk",
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt=initial_prompt)
        async for message in client.receive_response():
            await _print_message(message)

        while True:
            user_input = await ainput("\nYou: ")
            if user_input.strip().lower() in ("exit", "quit", "q"):
                break
            if not user_input.strip():
                continue
            await client.query(prompt=user_input)
            async for message in client.receive_response():
                await _print_message(message)


if __name__ == "__main__":
    DEFAULT_PROMPT = """
Connect to The workspace Data Readiness - Prod and the semantic model\
      is PIM_ASSISTANT_SIMPLIFIED 2
"""
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prompt", help="The prompt to send to the Claude agent")
    args = argparser.parse_args()

    asyncio.run(main(args.prompt or DEFAULT_PROMPT))
