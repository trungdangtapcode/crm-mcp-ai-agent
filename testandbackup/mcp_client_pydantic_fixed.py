"""
MCP Client for Agentic AI using PydanticAI
This module provides a client for interacting with the Model Context Protocol server,
using PydanticAI's SSE transport for improved performance and reliability.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from pydantic_ai.mcp import SSEClientContext
    PYDANTIC_AI_AVAILABLE = True
    logger = logging.getLogger("mcp_client_pydantic")
    logger.info("PydanticAI library available - SSE transport enabled")
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    logger = logging.getLogger("mcp_client_pydantic")
    logger.warning("PydanticAI library not available - install with: pip install 'pydantic-ai-slim[mcp]'")

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class Tool(BaseModel):
    """Representation of a tool that can be called via MCP"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)
    category: str = "general"

class MCPClient:
    """Client for interacting with an MCP server using PydanticAI SSE transport"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the MCP client.
        
        Args:
            base_url: The base URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.available_tools: List[Tool] = []
        self.connection_status = "disconnected"
        self.sse_client = None
        
        # Initialize PydanticAI SSE client if available
        if PYDANTIC_AI_AVAILABLE:
            try:
                # Create SSE client context for the MCP server
                self.sse_client = SSEClientContext(url=base_url, timeout=timeout)
                logger.info(f"Initialized PydanticAI SSE client for {base_url}")
            except Exception as e:
                logger.error(f"Failed to initialize PydanticAI SSE client: {e}")
                self.sse_client = None
        else:
            logger.error("PydanticAI not available - please install with: pip install 'pydantic-ai-slim[mcp]'")
        
    def _infer_tool_category(self, tool_name: str) -> str:
        """Infer the category of a tool based on its name"""
        name_lower = tool_name.lower()
        
        if any(keyword in name_lower for keyword in ["time", "date", "clock", "calendar"]):
            return "time"
        elif any(keyword in name_lower for keyword in ["weather", "forecast", "temperature", "climate"]):
            return "weather"
        elif any(keyword in name_lower for keyword in ["search", "web", "find", "lookup", "query", "fetch"]):
            return "search"
        elif any(keyword in name_lower for keyword in ["memory", "remember", "recall", "store"]):
            return "memory"
        elif any(keyword in name_lower for keyword in ["plan", "task", "schedule", "goal"]):
            return "planning"
        elif any(keyword in name_lower for keyword in ["calculate", "math", "compute", "convert"]):
            return "calculation"
        elif any(keyword in name_lower for keyword in ["customer", "crm", "client"]):
            return "crm"
        else:
            return "general"
        
    async def initialize(self, retry_count=3, use_fallback=True):
        """
        Initialize the client by fetching available tools from the server
        
        Args:
            retry_count: Number of connection attempts before giving up
            use_fallback: Whether to use fallback tools if server is unavailable
            
        Returns:
            List of available tools
        """
        if not PYDANTIC_AI_AVAILABLE:
            if use_fallback:
                logger.warning("PydanticAI not available, using fallback tools")
                self._setup_fallback_tools()
                return self.available_tools
            else:
                raise ImportError("PydanticAI not available - install with: pip install 'pydantic-ai-slim[mcp]'")
        
        if not self.sse_client:
            if use_fallback:
                logger.warning("SSE client not initialized, using fallback tools")
                self._setup_fallback_tools()
                return self.available_tools
            else:
                raise ConnectionError("SSE client not initialized")
        
        # Try to connect and get tools using PydanticAI SSE client
        for attempt in range(retry_count):
            try:
                logger.info(f"Connecting to MCP server via PydanticAI SSE (attempt {attempt+1}/{retry_count})")
                
                async with self.sse_client as client:
                    # List available tools from the MCP server
                    tools_response = await client.list_tools()
                    
                    # Convert MCP tools to our Tool format
                    self.available_tools = []
                    if hasattr(tools_response, 'tools') and tools_response.tools:
                        for tool in tools_response.tools:
                            tool_name = getattr(tool, 'name', '')
                            tool_desc = getattr(tool, 'description', '')
                            
                            # Handle input schema
                            parameters = {}
                            required_params = []
                            
                            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                                schema = tool.inputSchema
                                if hasattr(schema, 'properties') and schema.properties:
                                    parameters = dict(schema.properties)
                                if hasattr(schema, 'required') and schema.required:
                                    required_params = list(schema.required)
                            
                            self.available_tools.append(Tool(
                                name=tool_name,
                                description=tool_desc,
                                parameters=parameters,
                                category=self._infer_tool_category(tool_name),
                                required_parameters=required_params
                            ))
                    
                    logger.info(f"Successfully loaded {len(self.available_tools)} tools via PydanticAI SSE")
                    self.connection_status = "connected"
                    return self.available_tools
                        
            except Exception as e:
                logger.error(f"PydanticAI SSE connection failed (attempt {attempt+1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2)
        
        # If all attempts failed, use fallback if requested
        if use_fallback:
            logger.warning("Using fallback tools since PydanticAI SSE connection failed")
            self._setup_fallback_tools()
            return self.available_tools
        else:
            raise ConnectionError(f"Could not connect to MCP server at {self.base_url}")
            
    def _setup_fallback_tools(self):
        """Set up fallback tools when the MCP server is unavailable"""
        logger.info("Setting up fallback tools")
        
        self.available_tools = [
            Tool(
                name="echo",
                description="Echo a message back to the user",
                parameters={"message": {"type": "string", "description": "The message to echo"}},
                required_parameters=["message"],
                category="utility"
            ),
            Tool(
                name="get_current_time",
                description="Get the current time",
                parameters={},
                required_parameters=[],
                category="time"
            ),
            Tool(
                name="calculate_expression",
                description="Calculate a mathematical expression",
                parameters={
                    "expression": {"type": "string", "description": "The mathematical expression to evaluate"}
                },
                required_parameters=["expression"],
                category="calculation"
            )
        ]
        
        self.connection_status = "fallback"
        logger.info(f"Created {len(self.available_tools)} fallback tools")
            
    def get_tools_for_llm(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """Get tools in a format suitable for LLM API calls"""
        tools = []
        for tool in self.available_tools:
            if categories and tool.category not in categories:
                continue
                
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                        "required": tool.required_parameters
                    }
                }
            })
        return tools
        
    def get_tools_by_category(self) -> Dict[str, List[Tool]]:
        """Get tools organized by category"""
        categorized_tools = {}
        
        for tool in self.available_tools:
            category = tool.category
            if category not in categorized_tools:
                categorized_tools[category] = []
            categorized_tools[category].append(tool)
            
        return categorized_tools
        
    async def call_tool(self, tool_name: str, **params) -> Any:
        """
        Call a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to call
            **params: Parameters to pass to the tool
            
        Returns:
            The result of the tool execution
        """
        logger.info(f"Calling tool: {tool_name} with params: {params}")

        # Try PydanticAI SSE client first
        if PYDANTIC_AI_AVAILABLE and self.sse_client:
            try:
                async with self.sse_client as client:
                    # Call the tool using the SSE client
                    result = await client.call_tool(tool_name, params)
                    
                    # Extract the actual result from the MCP response
                    if hasattr(result, 'content') and result.content:
                        # Get the first content item if it's a list
                        content = result.content[0] if isinstance(result.content, list) else result.content
                        if hasattr(content, 'text'):
                            return content.text
                        elif hasattr(content, 'data'):
                            return content.data
                        else:
                            return str(content)
                    
                    logger.info(f"Tool {tool_name} executed successfully via PydanticAI SSE")
                    return result
            except Exception as e:
                logger.error(f"PydanticAI SSE tool call failed for {tool_name}: {str(e)}")
                
        # Fallback implementations for basic tools
        if tool_name == "echo" and "message" in params:
            return params["message"]
        elif tool_name == "get_current_time":
            return datetime.now().isoformat()
        elif tool_name == "calculate_expression" and "expression" in params:
            try:
                # Simple calculator - be careful with eval in production
                result = eval(params["expression"])
                return str(result)
            except Exception as e:
                return f"Calculation error: {str(e)}"
                
        raise ConnectionError(f"Could not execute tool {tool_name} - server unavailable and no fallback")

    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a batch of tool calls and return their results"""
        logger.info(f"Executing {len(tool_calls)} tool calls")
        results = []
        
        for call in tool_calls:
            try:
                tool_id = call.get("id")
                function = call.get("function", {})
                name = function.get("name")
                arguments = function.get("arguments", "{}")
                
                # Parse arguments if they're a JSON string
                if isinstance(arguments, str):
                    import json
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                
                if not isinstance(arguments, dict):
                    arguments = {}
                
                result = await self.call_tool(name, **arguments)
                results.append({
                    "tool_call_id": tool_id,
                    "name": name,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed to execute tool call {call}: {str(e)}")
                results.append({
                    "tool_call_id": call.get("id"),
                    "name": call.get("function", {}).get("name"),
                    "error": str(e)
                })
        
        return results

    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """Get the description of a specific tool"""
        for tool in self.available_tools:
            if tool.name == tool_name:
                return tool.description
        return None
    
    def get_available_categories(self) -> List[str]:
        """Get a list of all available tool categories"""
        return sorted(list(set(tool.category for tool in self.available_tools)))
    
    def get_tools_summary(self) -> Dict[str, Any]:
        """Get a summary of all available tools"""
        categorized = self.get_tools_by_category()
        
        return {
            "total_tools": len(self.available_tools),
            "connection_status": self.connection_status,
            "transport_type": "PydanticAI SSE" if (PYDANTIC_AI_AVAILABLE and self.sse_client) else "Fallback",
            "categories": {
                category: {
                    "count": len(tools),
                    "tools": [{"name": tool.name, "description": tool.description} for tool in tools]
                }
                for category, tools in categorized.items()
            }
        }

# Backwards compatibility
FastMCPClient = MCPClient
