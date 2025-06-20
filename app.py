import chainlit as cl
import logging
from pydantic_agent import handle_message, setup_mcp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")

@cl.on_chat_start
async def start():
    logger.info("New chat session started with PydanticAI")
    await setup_mcp()
    await cl.Message(content="👋 Hello! I'm your Agentic AI assistant powered by PydanticAI and MCP. I can help you with various tasks like checking the weather, searching the web, planning tasks, and more. How can I assist you today?").send()

@cl.on_message
async def main(message: cl.Message):
    logger.info(f"Received message: {message.content[:50]}...")
    await handle_message(message)