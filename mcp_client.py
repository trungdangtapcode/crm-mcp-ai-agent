"""
MCP Client for Agentic AI
This module provides a client for interacting with the Model Context Protocol server,
enabling agentic capabilities for AI applications.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
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
    """Client for interacting with an MCP server"""
    
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
        
    async def initialize(self):
        """Initialize the client by fetching available tools from the server"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/tools")
                response.raise_for_status()
                tools_data = response.json()
                
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
                logger.info(f"Loaded {len(self.available_tools)} tools from MCP server")
                return self.available_tools
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {str(e)}")
            raise
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
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/tools/{tool_name}", 
                    json=params
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            raise

    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a batch of tool calls and return their results
        
        Args:
            tool_calls: List of tool calls from an LLM response
            
        Returns:
            List of tool results with their IDs
        """
        results = []
        for call in tool_calls:
            try:
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
