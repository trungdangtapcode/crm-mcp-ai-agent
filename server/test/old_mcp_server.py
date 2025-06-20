from fastmcp import FastMCP
from datetime import datetime
import json
import os
import httpx
import logging
from typing import Dict, List, Any, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_server")

# Initialize the MCP server
mcp = FastMCP("Agentic AI Tools Server")

# Memory storage (in a production system, this would be a database)
memory_store = {}

# Define the tool to get the current time
@mcp.tool
def get_current_time() -> str:
    """Get the current time in ISO format"""
    return datetime.now().isoformat()

@mcp.tool
def weather_info(location: str) -> Dict[str, Any]:
    """
    Get current weather information for a location
    
    Args:
        location: City name or location to get weather for
    
    Returns:
        Weather information including temperature and conditions
    """
    # In a real application, you would call a weather API here
    # This is a mock response
    mock_weather = {
        "location": location,
        "temperature": 22,
        "temperature_unit": "celsius",
        "conditions": "partly cloudy",
        "humidity": 65,
        "wind_speed": 10,
        "wind_direction": "NE",
        "timestamp": datetime.now().isoformat()
    }
    return mock_weather

@mcp.tool
def search_web(query: str, num_results: int = 3) -> List[Dict[str, str]]:
    """
    Search the web for information
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 3)
    
    Returns:
        List of search results with title, snippet and url
    """
    # In a real application, you would call a search API here
    # This is a mock response
    time.sleep(1)  # Simulate network delay
    mock_results = [
        {
            "title": f"Result 1 for {query}",
            "snippet": f"This is a snippet of information about {query}...",
            "url": f"https://example.com/result1?q={query}"
        },
        {
            "title": f"Result 2 for {query}",
            "snippet": f"More information about {query} and related topics...",
            "url": f"https://example.com/result2?q={query}"
        },
        {
            "title": f"Result 3 for {query}",
            "snippet": f"Everything you need to know about {query}...",
            "url": f"https://example.com/result3?q={query}"
        }
    ]
    return mock_results[:num_results]

@mcp.tool
def remember(key: str, value: str) -> Dict[str, str]:
    """
    Store information in memory
    
    Args:
        key: Key to store the information under
        value: Value to store
    
    Returns:
        Confirmation of storage
    """
    memory_store[key] = value
    return {"status": "success", "message": f"Stored '{value}' under key '{key}'"}

@mcp.tool
def recall(key: str) -> Dict[str, Any]:
    """
    Recall information from memory
    
    Args:
        key: Key to retrieve information for
    
    Returns:
        The stored information or error message
    """
    if key in memory_store:
        return {"status": "success", "value": memory_store[key]}
    else:
        return {"status": "error", "message": f"No information stored for key '{key}'"}

@mcp.tool
def generate_task_plan(goal: str, constraints: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a task plan to achieve a goal
    
    Args:
        goal: The goal to achieve
        constraints: Any constraints to consider (optional)
    
    Returns:
        A structured task plan
    """
    constraints_text = f" considering these constraints: {constraints}" if constraints else ""
    
    # In a real implementation, this might call another AI model
    mock_plan = {
        "goal": goal,
        "constraints": constraints,
        "steps": [
            {"step": 1, "task": f"Research {goal}", "estimated_time": "30 minutes"},
            {"step": 2, "task": f"Analyze information related to {goal}", "estimated_time": "1 hour"},
            {"step": 3, "task": f"Create initial implementation for {goal}", "estimated_time": "2 hours"},
            {"step": 4, "task": f"Test and validate the solution for {goal}", "estimated_time": "1 hour"},
            {"step": 5, "task": f"Finalize and document the solution for {goal}", "estimated_time": "45 minutes"}
        ],
        "estimated_total_time": "5 hours 15 minutes",
        "generated_at": datetime.now().isoformat()
    }
    return mock_plan

@mcp.tool
def calculate_expression(expression: str) -> Dict[str, Any]:
    """
    Calculate the result of a mathematical expression
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        The result of the calculation
    """
    try:
        # Use safer eval with restricted globals
        # Warning: In production, you should use a proper math parser
        import math
        allowed_names = {
            "abs": abs,
            "max": max,
            "min": min,
            "pow": pow,
            "round": round,
            "sum": sum,
            "math": math
        }
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {
            "expression": expression,
            "result": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "status": "error"
        }

# Run the server
if __name__ == "__main__":
    logger.info("Starting MCP server with agentic capabilities")
    mcp.run(host="0.0.0.0", port=8000)