"""
Main MCP server that integrates all tools
"""
import logging
from fastmcp import FastMCP

# Import tool modules
from tools.time_tools import register_time_tools
from tools.weather_tools import register_weather_tools
from tools.search_tools import register_search_tools
from tools.memory_tools import register_memory_tools
from tools.planning_tools import register_planning_tools
from tools.calculation_tools import register_calculation_tools
from tools.crm_tools import register_crm_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_server")

def create_mcp_server():
    """Create and configure the MCP server with all tools"""
    
    # Initialize the MCP server
    mcp = FastMCP("Agentic AI Tools Server")
    
    # Register all tool groups
    logger.info("Registering time tools...")
    register_time_tools(mcp)
    
    logger.info("Registering weather tools...")
    register_weather_tools(mcp)
    
    logger.info("Registering search tools...")
    register_search_tools(mcp)
    
    logger.info("Registering memory tools...")
    register_memory_tools(mcp)
    
    logger.info("Registering planning tools...")
    register_planning_tools(mcp)
    
    logger.info("Registering calculation tools...")
    register_calculation_tools(mcp)
    
    logger.info("Registering CRM tools...")
    register_crm_tools(mcp)
    
    logger.info("MCP server initialized with all tools")
    
    return mcp

# Create server instance
mcp = create_mcp_server()

# Run the server
# RUN THIS COMMAND: fastmcp run main.py:mcp --transport sse --port 8001 --host 0.0.0.0
if __name__ == "__main__":
    logger.info("Starting MCP server with agentic capabilities")
    # Specify port 8001 to match the client configuration
    # Set host to 0.0.0.0 to accept connections from any IP
    # uvicorn main:app --host 0.0.0.0 --port 8001, suck
    mcp.run()
