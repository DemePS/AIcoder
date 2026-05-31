import asyncio
from aio_stdout import ainput, aprint
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    AssistantMessage,
)
import argparse


DEFAULT_PROMPT = """
Connect to The workspace Data Readiness - Prod and the semantic model\
      is PIM_ASSISTANT_SIMPLIFIED 2\
{"query": "In which markets are my products open?"}\
{"query": "Show me all products which are halogen free?"}\
{"query": "Which products have material status 30 in my portfolio?"}\
{"query": "Give me all product relation & technical data for these products?"}\
{"query": "Which project do these products belong to?"}\
{"query": "What is the operating voltage / IP protection of these products?"}\
{"query": "Do all my products have a PEP document/CE declaration?"}\
{"query": "What is the predecessor product?"}\
{"query": "Do the products have mandatory / spare part relations?"}\
{"query": "Do the products have a deletion flag?"}\
{"query": "Which is the start date of e-catalogue for the products?"}\
{"query": "Which products are integrated in the wholesaler export?"}\
"""


async def main(prompt: str | None):

    options = ClaudeAgentOptions(
        tools=[],
        allowed_tools=[
            "mcp__powerbi-modeling-mcp__*",
        ],
        permission_mode="dontAsk",
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt=prompt or DEFAULT_PROMPT)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        await aprint(block.text)  # Claude's reasoning
                    elif hasattr(block, "name"):
                        await aprint(f"Tool: {block.name}")  # Tool being called
            elif isinstance(message, ResultMessage):
                await aprint(f"Done: {message.subtype}")  # Final result


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prompt", help="The prompt to send to the Claude agent")
    args = argparser.parse_args()

    asyncio.run(main(args.prompt))
