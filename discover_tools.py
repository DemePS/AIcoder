from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import SystemMessage
import asyncio
import argparse


async def main(prompt: str):
    options = ClaudeAgentOptions()

    async for message in query(prompt="...", options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("Available MCP tools:", message.data.get("mcp_servers"))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prompt", help="The prompt to send to the Claude agent")
    args = argparser.parse_args()

    asyncio.run(main(args.prompt))
