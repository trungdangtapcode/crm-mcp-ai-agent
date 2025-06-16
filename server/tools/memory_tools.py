"""
Memory storage tools for MCP server
"""
from typing import Dict, Any

# Memory storage (in a production system, this would be a database)
memory_store = {}

def register_memory_tools(mcp):
    """Register memory-related tools with the MCP server"""
    
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
    def list_memory_keys() -> Dict[str, Any]:
        """
        List all keys stored in memory
        
        Returns:
            List of keys in memory
        """
        return {
            "keys": list(memory_store.keys()),
            "count": len(memory_store),
            "status": "success"
        }
    
    @mcp.tool
    def clear_memory(key: str = None) -> Dict[str, Any]:
        """
        Clear memory storage
        
        Args:
            key: Specific key to clear (if None, clears all memory)
            
        Returns:
            Confirmation of memory clearing
        """
        if key is None:
            # Clear all memory
            count = len(memory_store)
            memory_store.clear()
            return {"status": "success", "message": f"Cleared all memory ({count} items)"}
        else:
            # Clear specific key
            if key in memory_store:
                del memory_store[key]
                return {"status": "success", "message": f"Cleared memory for key '{key}'"}
            else:
                return {"status": "error", "message": f"Key '{key}' not found in memory"}
