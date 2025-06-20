"""
MCP Client for Agentic AI
This module provides a client for interacting with the Model Context Protocol server,
enabling agentic capabilities for AI applications.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
try:
    from fastmcp import Client
    from fastmcp.client.transports import SSETransport
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_client")

class Tool(BaseModel):
    """Representation of a tool that can be called via MCP"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)
    category: str = "general"  # Added tool category

class MCPClient:
    """Client for interacting with an MCP server using SSE transport"""
    
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
        
        # Initialize FastMCP client with SSE transport if available
        if FASTMCP_AVAILABLE:
            # Create SSE transport for FastMCP server
            # FastMCP SSE servers typically use /sse/ in the path or can be explicitly configured
            sse_url = base_url
            if not "/sse" in sse_url:
                # Add /sse to the URL if not present for SSE transport
                sse_url = base_url.rstrip('/') + '/sse'
            
            self.transport = SSETransport(url=sse_url)
            self.fastmcp_client = Client(self.transport)
            logger.info(f"Initialized FastMCP client with SSE transport for {sse_url}")
        else:
            logger.warning("FastMCP not available, falling back to basic HTTP client")
            self.fastmcp_client = None
        
    def _infer_tool_category(self, tool_name: str) -> str:
        """
        Infer the category of a tool based on its name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Category name
        """
        name_lower = tool_name.lower()
        
        # Time related tools
        if any(keyword in name_lower for keyword in ["time", "date", "clock", "calendar"]):
            return "time"
            
        # Weather related tools
        if any(keyword in name_lower for keyword in ["weather", "forecast", "temperature", "climate"]):
            return "weather"
            
        # Search related tools
        if any(keyword in name_lower for keyword in ["search", "web", "find", "lookup", "query", "fetch"]):
            return "search"
            
        # Memory related tools
        if any(keyword in name_lower for keyword in ["memory", "remember", "recall", "store"]):
            return "memory"
            
        # Planning related tools
        if any(keyword in name_lower for keyword in ["plan", "task", "schedule", "goal"]):
            return "planning"
            
        # Calculation related tools
        if any(keyword in name_lower for keyword in ["calculate", "math", "compute", "convert"]):
            return "calculation"
            
        # CRM related tools
        if any(keyword in name_lower for keyword in ["customer", "crm", "client"]):
            return "crm"
            
        # Default category
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
        if FASTMCP_AVAILABLE and self.fastmcp_client:
            # Use FastMCP client with SSE transport
            for attempt in range(retry_count):
                try:
                    logger.info(f"Connecting to MCP server via SSE at {self.base_url} (attempt {attempt+1}/{retry_count})")
                    
                    # Connect to the FastMCP server
                    async with self.fastmcp_client as client:
                        # List available tools
                        tools_response = await client.list_tools()
                        
                        # Convert FastMCP tools to our Tool format
                        self.available_tools = []
                        if hasattr(tools_response, 'tools') and tools_response.tools:
                            for tool in tools_response.tools:
                                # Extract tool information from FastMCP tool object
                                tool_name = tool.name if hasattr(tool, 'name') else str(tool.get('name', ''))
                                tool_desc = tool.description if hasattr(tool, 'description') else str(tool.get('description', ''))
                                
                                # Handle input schema
                                parameters = {}
                                required_params = []
                                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                                    schema = tool.inputSchema
                                    if hasattr(schema, 'properties'):
                                        parameters = schema.properties or {}
                                    elif isinstance(schema, dict):
                                        parameters = schema.get('properties', {})
                                    
                                    if hasattr(schema, 'required'):
                                        required_params = schema.required or []
                                    elif isinstance(schema, dict):
                                        required_params = schema.get('required', [])
                                
                                self.available_tools.append(Tool(
                                    name=tool_name,
                                    description=tool_desc,
                                    parameters=parameters,
                                    category=self._infer_tool_category(tool_name),
                                    required_parameters=required_params
                                ))
                        
                        logger.info(f"Loaded {len(self.available_tools)} tools from FastMCP server via SSE")
                        self.connection_status = "connected"
                        return self.available_tools
                        
                except Exception as e:
                    logger.error(f"FastMCP SSE connection failed (attempt {attempt+1}/{retry_count}): {str(e)}")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(1)
                    
            # If all FastMCP attempts failed, fall back to HTTP
            logger.warning("FastMCP SSE connection failed, trying HTTP fallback")
        
        # Fallback to HTTP for backwards compatibility
        for attempt in range(retry_count):
            try:
                logger.info(f"Connecting to MCP server via HTTP at {self.base_url} (attempt {attempt+1}/{retry_count})")
                if not FASTMCP_AVAILABLE:
                    import httpx
                    
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # Try to list available tools from the common endpoint
                    response = await client.get(f"{self.base_url}/")
                    response.raise_for_status()
                    
                    # Try to parse the server response and extract tools
                    try:
                        data = response.json()
                        # Check if we have a tools list directly
                        if isinstance(data, list):
                            tools_data = data
                        # Check if tools are in a nested structure
                        elif isinstance(data, dict) and "tools" in data:
                            tools_data = data["tools"]
                        else:
                            # Manually create a basic list based on registered tool modules
                            logger.warning("Could not find tools in server response, creating basic tool list")
                            tools_data = [
                                {"name": "get_current_time", "description": "Get current time"},
                                {"name": "get_date_info", "description": "Get detailed date information"},
                                {"name": "weather_info", "description": "Get weather information"},
                                {"name": "search_web", "description": "Search the web"},
                                {"name": "remember", "description": "Store information in memory"},
                                {"name": "recall", "description": "Recall information from memory"},
                                {"name": "calculate_expression", "description": "Calculate a mathematical expression"},
                                {"name": "list_customers", "description": "List customers from CRM"}
                            ]
                    except Exception as e:
                        logger.error(f"Error parsing tools: {str(e)}")
                        tools_data = []
                    
                    self.available_tools = [
                        Tool(
                            name=tool["name"],
                            description=tool.get("description", ""),
                            parameters=tool.get("parameters", {}),
                            category=self._infer_tool_category(tool["name"]),
                            required_parameters=tool.get("required", [])
                        )
                        for tool in tools_data
                    ]
                    logger.info(f"Loaded {len(self.available_tools)} tools from MCP server via HTTP")
                    self.connection_status = "connected"
                    return self.available_tools
            except Exception as e:
                logger.error(f"HTTP connection failed (attempt {attempt+1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1)
        
        # If we got here, all attempts failed
        if use_fallback:
            logger.warning("Using fallback tools since MCP server is unavailable")
            self._setup_fallback_tools()
            return self.available_tools
        else:
            raise ConnectionError(f"Could not connect to MCP server at {self.base_url} after {retry_count} attempts")
            
    def _setup_fallback_tools(self):
        """
        Set up fallback tools when the MCP server is unavailable
        This provides a minimal set of tools that can be used without a server connection
        """
        logger.info("Setting up fallback tools")
        
        # Clear any existing tools
        self.available_tools = []
        
        # Add a simple echo tool
        self.available_tools.append(Tool(
            name="echo",
            description="Echo a message back to the user",
            parameters={"message": {"type": "string", "description": "The message to echo"}},
            required_parameters=["message"],
            category="utility"
        ))
        
        # Add a current time tool
        self.available_tools.append(Tool(
            name="current_time",
            description="Get the current time",
            parameters={},
            required_parameters=[],
            category="time"
        ))
        
        # Add a simple calculator tool
        self.available_tools.append(Tool(
            name="calculate",
            description="Perform a simple calculation",
            parameters={
                "expression": {"type": "string", "description": "The mathematical expression to evaluate"}
            },
            required_parameters=["expression"],
            category="calculation"
        ))
        
        logger.info(f"Created {len(self.available_tools)} fallback tools")
            
    def get_tools_for_llm(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get tools in a format suitable for LLM API calls
        
        Args:
            categories: Optional list of categories to filter tools by
            
        Returns:
            List of tool definitions formatted for OpenAI-compatible APIs
        """
        tools = []
        for tool in self.available_tools:
            # Filter by category if specified
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
        """
        Get tools organized by category
        
        Returns:
            Dictionary mapping categories to lists of tools
        """
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
        print("In call_tool()")
        print(f"Calling tool: {tool_name} with params: {params}")

        # Try FastMCP client first if available
        if FASTMCP_AVAILABLE and self.fastmcp_client:
            try:
                async with self.fastmcp_client as client:
                    result = await client.call_tool(tool_name, **params)
                    return result
            except Exception as e:
                logger.error(f"FastMCP SSE call failed for tool {tool_name}: {str(e)}")
                # Fall through to HTTP fallback

        # Check if tool exists in fallback tools
        is_fallback_available = False
        for tool in self.available_tools:
            if tool.name == tool_name:
                is_fallback_available = True
                break
                
        # Try HTTP fallback if FastMCP failed
        try:
            if not FASTMCP_AVAILABLE:
                import httpx
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use direct tool endpoint without 'tools/' prefix to match FastMCP's routing
                response = await client.post(
                    f"{self.base_url}/{tool_name}", 
                    json=params
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result")
        except Exception as e:
            logger.error(f"HTTP connection error calling tool {tool_name}: {str(e)}")
            
            # If we have a fallback tool implementation, use it
            if is_fallback_available and hasattr(self, f"_fallback_{tool_name}"):
                logger.info(f"Using fallback implementation for {tool_name}")
                fallback_method = getattr(self, f"_fallback_{tool_name}")
                return await fallback_method(**params)
            else:
                raise ConnectionError(f"Could not connect to MCP server for tool {tool_name} and no fallback is available")

    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a batch of tool calls and return their results
        
        Args:
            tool_calls: List of tool calls from an LLM response
            
        Returns:
            List of tool results with their IDs
        """
        print("In execute_tool_calls()")
        results = []
        for call in tool_calls:
            try:
                print("Processing tool call:", call)
                tool_id = call.get("id")
                function = call.get("function", {})
                name = function.get("name")
                arguments = function.get("arguments", "{}")
                # Parse arguments - handle both JSON string and dict
                if isinstance(arguments, str):
                    import json
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                
                # Ensure arguments is a dictionary, not None
                if arguments is None:
                    arguments = {}
                
                result = await self.call_tool(name, **arguments)
                results.append({
                    "tool_call_id": tool_id,
                    "name": name,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed to execute tool call: {str(e)}")
                results.append({
                    "tool_call_id": call.get("id"),
                    "name": call.get("function", {}).get("name"),
                    "error": str(e)
                })
        
        return results

    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """
        Get the description of a specific tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool description or None if tool not found
        """
        for tool in self.available_tools:
            if tool.name == tool_name:
                return tool.description
        return None
    
    def get_available_categories(self) -> List[str]:
        """
        Get a list of all available tool categories
        
        Returns:
            List of category names
        """
        return sorted(list(set(tool.category for tool in self.available_tools)))
    
    def get_tools_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all available tools
        
        Returns:
            Dictionary with tool statistics and categorized listings
        """
        categorized = self.get_tools_by_category()
        
        summary = {
            "total_tools": len(self.available_tools),
            "categories": {
                category: {
                    "count": len(tools),
                    "tools": [{"name": tool.name, "description": tool.description} for tool in tools]
                }
                for category, tools in categorized.items()
            }
        }
        
        return summary

# Backwards compatibility with FastMCPClient
FastMCPClient = MCPClient
