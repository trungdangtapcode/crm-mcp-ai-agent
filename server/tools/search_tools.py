"""
Web search tools for MCP server
"""
import time
from typing import Dict, List, Any

def register_search_tools(mcp):
    """Register search-related tools with the MCP server"""
    
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
    def fetch_webpage(url: str) -> Dict[str, Any]:
        """
        Fetch content from a webpage
        
        Args:
            url: URL of the webpage to fetch
            
        Returns:
            Content of the webpage
        """
        # In a real application, you would use requests or httpx to fetch the page
        # This is a mock response
        time.sleep(1.5)  # Simulate network delay
        
        return {
            "url": url,
            "title": f"Mock page title for {url}",
            "content": f"This is mock content for the webpage at {url}. In a real implementation, this would contain the actual text content of the page.",
            "status": "success"
        }
