"""
Simple diagnostic script to test FastMCP server endpoints
"""

import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_diagnostic")

# Base URL and endpoints to test
BASE_URL = "http://localhost:8001"
TOOL_NAME = "get_current_time"  # A simple tool to test

def test_endpoints():
    """Test different endpoint variations to find the working one"""
    
    # List of possible endpoint patterns
    endpoints = [
        f"{BASE_URL}/{TOOL_NAME}",                # Direct tool name
        f"{BASE_URL}/tools/{TOOL_NAME}",          # With tools/ prefix
        f"{BASE_URL}/api/v1/{TOOL_NAME}"          # With api/v1/ prefix
    ]
    
    # Also test discovery endpoints
    discovery_endpoints = [
        f"{BASE_URL}/",                    # Root  
        f"{BASE_URL}/tools",               # Tools list
        f"{BASE_URL}/docs"                 # Swagger docs
    ]
    
    # Test tool endpoints with POST
    logger.info("\n--- Testing tool invocation endpoints ---")
    for endpoint in endpoints:
        try:
            logger.info(f"Testing POST {endpoint}")
            response = requests.post(endpoint, json={})
            logger.info(f"Response: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"SUCCESS! Working endpoint: {endpoint}")
                logger.info(f"Response content: {response.text[:100]}...")
        except Exception as e:
            logger.info(f"Error: {str(e)}")
            
    # Test discovery endpoints with GET
    logger.info("\n--- Testing discovery endpoints ---")
    for endpoint in discovery_endpoints:
        try:
            logger.info(f"Testing GET {endpoint}")
            response = requests.get(endpoint)
            logger.info(f"Response: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"SUCCESS! Working endpoint: {endpoint}")
                logger.info(f"Response content: {response.text[:100]}...")
        except Exception as e:
            logger.info(f"Error: {str(e)}")
            
    logger.info("\nDiagnostic tests completed!")

if __name__ == "__main__":
    logger.info("Starting FastMCP server diagnostics...")
    asyncio.run(test_endpoints())
