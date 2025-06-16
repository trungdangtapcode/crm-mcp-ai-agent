"""
Time and date tools for MCP server
"""
from datetime import datetime
from typing import Dict, Any

def register_time_tools(mcp):
    """Register time-related tools with the MCP server"""
    
    @mcp.tool
    def get_current_time() -> str:
        """Get the current time in ISO format"""
        return datetime.now().isoformat()
    
    @mcp.tool
    def get_date_info() -> Dict[str, Any]:
        """Get detailed information about the current date"""
        now = datetime.now()
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "day_of_month": now.day,
            "month": now.strftime("%B"),
            "year": now.year,
            "timestamp": now.timestamp(),
            "iso_format": now.isoformat()
        }
