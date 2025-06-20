
from handlers import handle_message, setup_mcp
import chainlit as cl
from config import API_KEY, MCP_SERVER_URL, BASE_URL
import asyncio

from mcp_client import MCPClient

class MockMessage(cl.Message):
    def __init__(self, content):
        super().__init__(content=content)

    async def send(self):
        print(f"[Mock Send] {self.content}")


async def test_weather():
	# Simulate a weather query
	await setup_mcp()
	message = MockMessage(content="What's the weather like?")
	await handle_message(message)

async def client():
    print("Setting up MCP client...", MCP_SERVER_URL)
    mcp_client = MCPClient(MCP_SERVER_URL)
    await mcp_client.initialize()
    print("MCP client initialized.")
    print("Available tools:", mcp_client.get_tools_summary())

if __name__ == "__main__":
	# import asyncio
	# asyncio.run(test_weather())
	asyncio.run(client())