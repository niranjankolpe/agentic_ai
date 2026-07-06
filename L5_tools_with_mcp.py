import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import nest_asyncio

nest_asyncio.apply()

mcp_client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone", "Asia/Kolkata"],
        }
    },
)


async def main():
    mcp_tools = await mcp_client.get_tools()
    print(f"Loaded {len(mcp_tools)} MCP tools: {[t.name for t in mcp_tools]}")

    # model = init_chat_model("ollama:llama3.2:3b", temperature=0)

    agent_with_mcp = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt="You are a helpful assistant",
    )

    result = await agent_with_mcp.ainvoke(
        {"messages": [{"role": "user", "content": "What's the time in America/Los_Angeles right now?"}]}
    )
    for msg in result["messages"]:
        msg.pretty_print()

asyncio.run(main())