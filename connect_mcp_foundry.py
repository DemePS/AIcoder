"""
PowerBI Agent using Microsoft Agent Framework + Azure AI Foundry.

Required environment variables:
  FOUNDRY_PROJECT_ENDPOINT  - https://<account>.services.ai.azure.com/api/projects/<project>
  FOUNDRY_MODEL             - Model deployment name (default: gpt-4o)
  POWERBI_MCP_URL           - HTTP URL of the PowerBI MCP server (default: http://localhost:3000/mcp)

The PowerBI MCP server must be reachable as an HTTP endpoint.
To run it locally over HTTP, check if your version supports a --port flag:
  npx -y @microsoft/powerbi-modeling-mcp@latest --start --port 3000
Or use an HTTP-stdio bridge such as mcp-proxy:
  npx -y mcp-proxy --port 3000 -- npx -y @microsoft/powerbi-modeling-mcp@latest --start

Authentication: uses DefaultAzureCredential (env vars → managed identity → Azure CLI → etc.).

Install dependencies:
  pip install agent-framework azure-identity
"""

import asyncio
import argparse
import os

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

DEFAULT_PROMPT = """
Connect to The workspace Data Readiness - Prod and the semantic model
is PIM_ASSISTANT_SIMPLIFIED 2
"""

AGENT_INSTRUCTIONS = (
    "You are a Power BI expert. Help users manage and analyze their "
    "Power BI data models and semantic models using the available tools. "
    "Always confirm which workspace and semantic model you are connected to "
    "before performing operations."
)


async def main(initial_prompt: str) -> None:
    credential = DefaultAzureCredential()

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
        credential=credential,
    )

    powerbi_mcp = MCPStreamableHTTPTool(
        name="powerbi-modeling-mcp",
        url=os.environ.get("POWERBI_MCP_URL", "http://localhost:3000/mcp"),
    )

    async with Agent(
        client=client,
        name="PowerBIAgent",
        instructions=AGENT_INSTRUCTIONS,
        tools=[powerbi_mcp],
    ) as agent:
        result = await agent.run(initial_prompt)
        print(f"\nAssistant: {result.text}")

        while True:
            try:
                user_input = input("\nYou: ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if user_input.strip().lower() in ("exit", "quit", "q"):
                break
            if not user_input.strip():
                continue
            result = await agent.run(user_input)
            print(f"\nAssistant: {result.text}")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Interactive Power BI agent via Microsoft Foundry and Agent Framework"
    )
    argparser.add_argument("--prompt", help="Initial prompt to send to the agent")
    args = argparser.parse_args()

    asyncio.run(main(args.prompt or DEFAULT_PROMPT))
