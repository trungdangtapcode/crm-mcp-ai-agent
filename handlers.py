import json
import logging
from datetime import datetime
import chainlit as cl
from typing import Dict, List, Any
from openai import AsyncOpenAI
from config import API_KEY, MCP_SERVER_URL, BASE_URL
from mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("handlers")

# Store conversation history
conversation_history = {}

@cl.on_chat_start
async def setup_mcp():
    # Initialize MCP client
    mcp_client = MCPClient(MCP_SERVER_URL)
    await mcp_client.initialize()
    
    # Store client in user session
    cl.user_session.set("mcp_client", mcp_client)
    
    # Create a new conversation ID
    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cl.user_session.set("conversation_id", conversation_id)
    conversation_history[conversation_id] = []
    
    logger.info(f"New conversation started: {conversation_id}")

async def handle_message(message: cl.Message):
    # Get the MCP client and conversation history
    mcp_client = cl.user_session.get("mcp_client")
    if not mcp_client:
        # Create and initialize if not exists
        mcp_client = MCPClient(base_url=MCP_SERVER_URL)
        await mcp_client.initialize()
        cl.user_session.set("mcp_client", mcp_client)
    
    conversation_id = cl.user_session.get("conversation_id")
    if not conversation_id:
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cl.user_session.set("conversation_id", conversation_id)
        conversation_history[conversation_id] = []
    
    # Add user message to history
    conversation_history[conversation_id].append({"role": "user", "content": message.content})
    
    # Get tools from MCP client
    tools = mcp_client.get_tools_for_llm()
    
    # Create OpenAI client
    client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    # Prepare messages with conversation history
    messages = conversation_history[conversation_id][-10:]  # Use last 10 messages for context
    
    # Create a thinking indicator
    thinking_msg = cl.Message(content="")
    await thinking_msg.send()
    
    try:
        # Call the LLM
        response = await client.chat.completions.create(
            model="mistralai/devstral-small:free",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Add assistant response to history
        conversation_history[conversation_id].append({
            "role": "assistant", 
            "content": assistant_message.content or "",
            "tool_calls": assistant_message.tool_calls
        })
        
        # Handle tool calls if any
        if assistant_message.tool_calls:
            await thinking_msg.stream_token("Executing tools... 🛠️\n\n")
            
            # Execute all tool calls
            tool_results = await mcp_client.execute_tool_calls(assistant_message.tool_calls)
            
            # Create a message showing executed tools
            tools_msg = "**Tools executed:**\n\n"
            for result in tool_results:
                tool_name = result.get("name", "unknown")
                tool_content = json.dumps(result.get("result"), indent=2)
                tools_msg += f"📌 **{tool_name}**\n```json\n{tool_content}\n```\n\n"
                
                # Add tool results to conversation history
                conversation_history[conversation_id].append({
                    "role": "tool", 
                    "tool_call_id": result.get("tool_call_id"),
                    "name": tool_name,
                    "content": json.dumps(result.get("result"))
                })
            
            await thinking_msg.stream_token(tools_msg)
            
            # Call the model again to process tool results
            second_response = await client.chat.completions.create(
                model="mistralai/devstral-small:free",
                messages=conversation_history[conversation_id]
            )
            
            # Add final response to history
            final_response = second_response.choices[0].message
            conversation_history[conversation_id].append({
                "role": "assistant", 
                "content": final_response.content
            })
            
            # Update the thinking message with the final result
            await thinking_msg.stream_token("\n\n**Final response:**\n\n")
            await thinking_msg.stream_token(final_response.content or "I've processed the results but have nothing more to add.")
            await thinking_msg.update()
        else:
            # Just show the assistant's response
            await thinking_msg.stream_token(assistant_message.content)
            await thinking_msg.update()
            
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(error_message)
        await thinking_msg.stream_token(error_message)
        await thinking_msg.update()