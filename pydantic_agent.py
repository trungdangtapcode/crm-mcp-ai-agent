from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
import asyncio
import os
import logging
import chainlit as cl
from datetime import datetime
from config import API_KEY, MCP_SERVER_URL, BASE_URL, MODEL_NAME
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pydantic_agent")

# Store conversation history
conversation_history = {}

def get_model():
    """Get the OpenAI model configured with custom base URL and API key"""
    ollama = OpenAIModel(model_name=MODEL_NAME, provider=OpenAIProvider(base_url=BASE_URL, api_key=API_KEY))
    return ollama

# Set up MCP Server
server = MCPServerSSE(url=MCP_SERVER_URL)

# Create the Agent with the custom OpenAI client
agent = Agent(model=get_model(), mcp_servers=[server])

async def setup_mcp():
    """Initialize the PydanticAI agent and MCP server connection"""
    try:
        logger.info(f"Setting up PydanticAI agent with MCP server: {MCP_SERVER_URL}")
        
        # Create a new conversation ID
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cl.user_session.set("conversation_id", conversation_id)
        conversation_history[conversation_id] = []
        
        # Store the agent in user session
        cl.user_session.set("agent", agent)
        
        logger.info(f"New conversation started with PydanticAI: {conversation_id}")
        
    except Exception as e:
        logger.error(f"Failed to setup MCP with PydanticAI: {str(e)}")
        raise

async def handle_message(message: cl.Message):
    """Handle incoming messages using PydanticAI agent"""
    try:
        # Get the agent and conversation history
        agent_instance = cl.user_session.get("agent", agent)
        conversation_id = cl.user_session.get("conversation_id")
        
        if not conversation_id:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cl.user_session.set("conversation_id", conversation_id)
            conversation_history[conversation_id] = []
        
        # Add user message to history
        conversation_history[conversation_id].append({"role": "user", "content": message.content})
        
        # Create a thinking indicator
        thinking_msg = cl.Message(content="")
        await thinking_msg.send()
        
        # Use PydanticAI to process the message with MCP tools
        async with agent_instance.run_mcp_servers():
            # Build context from conversation history
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[conversation_id][-5:]  # Last 5 messages for context
            ])
            
            await thinking_msg.stream_token("Processing with PydanticAI agent... 🤖\n\n")
            
            # Run the agent with the user's message
            result = await agent_instance.run(message.content)
            
            # Add assistant response to history
            conversation_history[conversation_id].append({
                "role": "assistant", 
                "content": result.output
            })
            
            # Stream the response
            await thinking_msg.stream_token("**PydanticAI Response:**\n\n")
            await thinking_msg.stream_token(result.output)
            await thinking_msg.update()
            
            logger.info(f"Successfully processed message with PydanticAI: {message.content[:50]}...")
            
    except Exception as e:
        error_message = f"An error occurred with PydanticAI: {str(e)}"
        logger.error(error_message)
        await thinking_msg.stream_token(error_message)
        await thinking_msg.update()

# Async function to run the query (for testing)
async def main():
    """Test function for standalone execution"""
    async with agent.run_mcp_servers():
        result = await agent.run('What time is it?')
    print(result.output)

# Run the main loop
if __name__ == "__main__":
    asyncio.run(main())
