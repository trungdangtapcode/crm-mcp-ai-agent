"""
Web search tools for MCP server
"""
import time
from typing import Dict, List, Any

from duckduckgo_search import DDGS
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any
import re

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


def func_fetch_url(url: str) -> Dict[str, Any]:
    """
    Fetch content from a webpage and format it for LLM processing.

    Args:
        url: URL of the webpage to fetch

    Returns:
        Dictionary containing the URL, title, cleaned content, and status
    """
    try:
        # Send HTTP GET request with a timeout
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()  # Raise exception for bad status codes

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.title.string.strip() if soup.title else "No title found"

        # Extract main content (remove scripts, styles, and navigation)
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Get text content and clean it
        content = soup.get_text(separator=' ', strip=True)
        # Remove excessive whitespace and newlines
        content = re.sub(r'\s+', ' ', content).strip()

        # Limit content length to avoid overwhelming LLMs (e.g., 10,000 chars)
        if len(content) > 10000:
            content = content[:10000] + "... [Content truncated]"

        return {
            "url": url,
            "title": title,
            "content": content,
            "status": "success"
        }

    except httpx.HTTPStatusError as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Failed to fetch webpage: HTTP {e.response.status_code}",
            "status": "error"
        }
    except httpx.RequestError as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Network error while fetching webpage: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Unexpected error while fetching webpage: {str(e)}",
            "status": "error"
        }

def func_fetch_webpage(url: str) -> Dict[str, Any]:
    """
    Fetch content from a webpage and return it in a structured format. This format is easy for LLM processing.
    
    Args:
        url: URL of the webpage to fetch
    Returns:
        A string containing the title and content of the webpage, formatted for LLMs.
    """
    webpage = func_fetch_url(url)
    title = webpage.get("title", "No title found")
    content = webpage.get("content", "No content found")
    return f"""# Webpage Title:\n{title}\n\n# Content:\n{content}"""

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
        Fetch content from a webpage and return it in a structured format. This format is easy for LLM processing.
        
        Args:
            url: URL of the webpage to fetch
        Returns:
            A string containing the title and content of the webpage, formatted for LLMs.
        """
        # In a real application, you would use requests or httpx to fetch the page
        # This is a mock response
        return func_fetch_webpage(url)


if __name__ == "__main__":
    # print(func_search_web("MCP protocol", 2))
    print(func_fetch_webpage("https://github.com/trungdangtapcode"))
    