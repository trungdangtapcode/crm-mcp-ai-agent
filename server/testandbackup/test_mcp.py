"""
Test script for MCP server and tools
This script tests the functionality of the MCP server and all registered tools.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_mcp")

MCP_SERVER_URL = "http://localhost:8001"

async def test_all_tools():
    """Test all available tools on the MCP server"""
    
    logger.info(f"Connecting to MCP server at {MCP_SERVER_URL}")
    
    # Initialize client
    client = MCPClient(MCP_SERVER_URL)
    await client.initialize()
    
    # Get all available tools
    tools_summary = client.get_tools_summary()
    
    logger.info(f"Found {tools_summary['total_tools']} tools in {len(tools_summary['categories'])} categories")
    
    # Print categories and tools
    for category, details in tools_summary["categories"].items():
        logger.info(f"Category: {category.upper()} ({details['count']} tools)")
        for tool in details["tools"]:
            logger.info(f"  - {tool['name']}: {tool['description']}")
    
    # Test key tools (one from each category)
    test_cases = [
        # Time tools
        {
            "tool": "get_current_time",
            "params": {}
        },
        # Weather tools
        {
            "tool": "weather_info",
            "params": {"location": "New York"}
        },
        # Search tools
        {
            "tool": "search_web",
            "params": {"query": "Agentic AI", "num_results": 2}
        },
        # Memory tools
        {
            "tool": "remember",
            "params": {"key": "test_key", "value": "This is a test value"}
        },
        # Recall what we just stored
        {
            "tool": "recall",
            "params": {"key": "test_key"}
        },
        # Planning tools
        {
            "tool": "generate_task_plan",
            "params": {"goal": "Test the MCP server"}
        },
        # Calculation tools
        {
            "tool": "calculate_expression",
            "params": {"expression": "2 + 2 * 3"}
        },
        # CRM tools - may fail if MongoDB is not set up
        {
            "tool": "list_customers",
            "params": {"limit": 5}
        }
    ]
    
    # Run test cases
    logger.info("\nRunning test cases:")
    for i, test_case in enumerate(test_cases):
        tool_name = test_case["tool"]
        params = test_case["params"]
        
        try:
            logger.info(f"\nTest {i+1}: {tool_name} with params {params}")
            result = await client.call_tool(tool_name, **params)
            logger.info(f"Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            logger.error(f"Error testing {tool_name}: {str(e)}")
    
    logger.info("\nTesting complete!")

if __name__ == "__main__":
    asyncio.run(test_all_tools())
