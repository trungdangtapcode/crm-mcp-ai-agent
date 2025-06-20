"""
Web search tools for MCP server
"""
import time
from typing import Dict, List, Any

from duckduckgo_search import DDGS

def func_search_web(query: str, num_results: int = 3) -> List[Dict[str, str]]:
    try:
        # Initialize DuckDuckGo search client
        with DDGS() as ddgs:
            # Perform search
            results = list(ddgs.text(query, max_results=num_results))
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", "No title"),
                "snippet": result.get("body", "No snippet available"),
                "url": result.get("href", "No URL")
            })
        
        # Pad with empty results if fewer than requested
        while len(formatted_results) < num_results:
            formatted_results.append({
                "title": "No result",
                "snippet": "No additional information available",
                "url": ""
            })
        
        time.sleep(1)  # Respectful delay to avoid overwhelming the service
        return formatted_results

    except Exception as e:
        print(f"Error fetching search results: {e}")
        return [
            {
                "title": "Error",
                "snippet": f"Failed to fetch results: {str(e)}",
                "url": ""
            }
        ] * num_results

def register_search_tools(mcp):
    """Register search-related tools with the MCP server"""
    
    @mcp.tool
    def search_web(query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search the web for information using DuckDuckGo.
        
        Args:
            query: Search query
            num_results: Number of results to return (default: 3)
        
        Returns:
            List of search results with title, snippet, and url
        """
        # In a real application, you would call a search API here
        # This is a mock response
        return func_search_web(query, num_results)

    
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


if __name__ == "__main__":
    print(func_search_web("MCP protocol", 2))
    